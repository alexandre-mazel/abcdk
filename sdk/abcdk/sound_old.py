# -*- coding: utf-8 -*-
###########################################################
# Aldebaran Behavior Complementary Development Kit
# Sound tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

import logging
"Audio tools"
logging.debug( "importing abcdk.sound" );

import ctypes
import math

import numpy as np # for windows user: pip install numpy
try:
    import numpy as np
except BaseException, err:
    print "WRN: can't load numpy, and it is required for some functionnalities... detailed error: %s" % err;	
import os
import struct
import sys
import time

# sys.path.append( "../" ); # pour pouvoir adder les modules suivant, si on est dans un subfolder "audio"

import config
import debug
import filetools
import pathtools
import naoqitools
import system
import test
try:
    import leds
except:
    pass

import math
try:
    import pylab
    from scipy.io import wavfile
except:
    pass
import os
global_memcpy_address = None;

def stringReplaceQuickAndDirty( strOriginal, strToReplace, nOffset = 0 ):
    """
    Replace a character in a string, quick and dirty, but usefull for big buffers
    """
    pOrigin = id(strOriginal) + 20
    pReplace = id(strToReplace) + 20

    global global_memcpy_address;
    if( global_memcpy_address == None ):
        global_memcpy_address =  ctypes.cdll.msvcrt.memcpy
    # For Linux, use the following. Change the 6 to whatever it is on your computer.
    # memset =  ctypes.CDLL("libc.so.6").memset
    
    #~ for idx, ch in enumerate( strToReplace ):
        #~ global_memset_address(pOrigin+nOffset+idx, ord(ch), 1);
        
    global_memcpy_address(pOrigin+nOffset, pReplace, len(strToReplace));
# stringReplaceQuickAndDirty - end

#~ s = "Bonjour";
#~ stringReplaceQuickAndDirty( s, "AB" );
#~ print s;

def findFirstValueHigher( data, limit ):
    """
    find the first value higher than a limit (in absolute value). 
    return -1 if no value higher in the array
    """
    # NB: argmax could return 0 if all remaining sample are equal to zero (the index of equal value are the one of the first element)
    # min( np.argmax( self.data>nLimit ), np.argmax( self.data<-nLimit ) ); => pb if no neg or no positive value => 0 => min => 0 and so we think there's no value, even if other sign has some # eg: [15,15,-1,-1] and limit = 2    
    # for long sound with a lot of silence and noise, it's faster to recode it having a return well placed.
    idx = np.argmax( np.abs(data)>limit );
    if( abs(data[idx])<= limit ):
        return -1;
    return idx;    
# findFirstValueHigher - end

def findFirstTrueValue( data ):
    """
    find the first value true.
    return -1 if no value true in the array
    """
    #~ idx = np.argmax( data );
    #~ if( not data[idx] ):
        #~ return -1;
    #~ return idx;
    
    # for long sound with a lot of silence and noise, it's faster to recode it having a return well placed. (8sec => 0.052sec)
    n = len(data);
    i = 0;    
    while( i < n ):
        if( data[i] ):
            return i;
        i += 1;
    return -1;    
# findFirstTrueValue - end

def findFirstFalseValue( data ):
    """
    find the first value true.
    return -1 if no value true in the array
    """
    #~ idx = np.argmin( data ); 
    #~ if( data[idx] ):
        #~ return -1;
    #~ return idx;
    
    # argmin seems far less efficient than argmax...   (and seems to compute all the list)
    n = len(data);
    i = 0;    
    while( i < n ):
        if( not data[i] ):
            return i;
        i += 1;
    return -1;
# findFirstFalseValue - end 

class Wav:
    # load and extract properties from a wav
    """
    Wave file format specification

    Field name	                            Size and format	    Meaning
    File description header	            4 bytes (DWord)	    The ASCII text string "RIFF" (0x5249 0x4646) The procedure converiting 4-symbol string into dword is included in unit Wave
    Size of file	                            4 bytes (DWord)	    The file size not including the "RIFF" description (4 bytes) and file description (4 bytes). This is file size - 8.
    
    WAV description header	        4 bytes (DWord)	    The ASCII text string "WAVE"
    Format description header	        4 bytes (DWord)	    The ASCII text string "fmt "(The space is also included)
    Size of WAVE section chunck	    4 bytes (DWord)	    The size of the WAVE type format (2 bytes) + mono/stereo flag (2 bytes) + sample rate (4 bytes) + bytes per sec (4 bytes) + block alignment (2 bytes) + bits per sample (2 bytes). This is usually 16.
    WAVE type format	                2 bytes (Word)	    Type of WAVE format. This is a PCM header = $01 (linear quntization). Other values indicates some forms of compression.
    Number of channels	                2 bytes (Word)	    mono ($01) or stereo ($02). You may try more channels...
    Samples per second	                4 bytes (DWord)	    The frequency of quantization (usually 44100 Hz, 22050 Hz, ...)
    Bytes per second	                    4 bytes (DWord)	    Speed of data stream = Number_of_channels*Samples_per_second*Bits_per_Sample/8
    Block alignment	                    2 bytes (Word)	    Number of bytes in elementary quantization = Number_of_channels*Bits_per_Sample/8
    Bits per sample	                    2 bytes (Word)	    Digits of quantization (usually 32, 24, 16, 8). I wonder if this is, for example, 5 ..?
    
    Data description header	        4 bytes (DWord)	    The ASCII text string "data" (0x6461 7461).
    Size of data	                        4 bytes (DWord)	    Number of bytes of data is included in the data section.
    Data	                                    -?-	                    Wave stream data itself. Be careful with format of stereo (see below)

    Notes.

    Note the order of samples in stereo wave file.
    Sample 1 - Left	Sample 1 - Right	Sample 2 - Left	Sample 2 - Right	Sample 3 - Left	 ...

    In case of 8 - bit quantization the sample is unsigned byte (0..255),
    in case of 16 - bit - signed integer (-32767..32767)
    
    Vocabulary:
    - sample: all data for a slice of time, so for a multichannel sound, it's an array.
    - element or value: an elementary value, so for a multichannel sound a sample is an array of element
    so:    
      - nbrSample: number of sample, a 44100Hz Stereo file has 44100 sample per sec
      - nbrElement: number of element, a 44100Hz Stereo file has 88200 element per sec
      - data size: the size in byte, a 44100Hz Stereo file has 176400 byte per sec
      - offset: often exprimed in element offset or in byte (depending of the context)
    
    WARNING: 
    WARNING: TESTED ONLY ON some Channels and depth bits ! (not tested for 24/32 bits)
    WARNING: 
    
    """
    def __init__( self, strLoadFromFile = None, bQuiet = True ):
        self.reset();
        if( strLoadFromFile != None ):
            self.load( strLoadFromFile, bQuiet = bQuiet );
    # __init__ - end
        
    def reset( self ):
        self.strFormatTag = "WAVEfmt ";
        self.nNbrChannel = 0;
        self.nSamplingRate = 0;
        self.nAvgBytesPerSec = 0;
        self.nSizeBlockAlign = 0;
        self.nNbrBitsPerSample = 0;
        self.nDataSize = 0; # the data size (in byte)
        self.nNbrSample = 0; # number of sample (1 sample in stereo 16 bits => 4 bytes)
        self.dataType = -1;
        self.rDuration = 0.; # duration in seconds
        self.info = {}; # extra info (name, date, title, ...)
        self.data = []; # temp array. Will be filled by interlaced sound datas
        self.bHeaderCorrected = False; # when loading header wasn't good...
        #~ self.dataUnpacked = []; # an array of samples stereo unpacked (eg in string python format): [L0, R0, L1, R1, ...] multi chan: [chan0-s0, chan1-s0, chan2-s0,chan3-s0,chan0-s1, chan1-s1, ...]
        
    def isOpen( self ):
        return self.nNbrChannel > 0
        
    def new( self, nSamplingRate = 44100, nNbrChannel = 1, nNbrBitsPerSample = 16 ):
        """
        generate a new empty sound
        """
        self.reset();
        self.nNbrChannel = nNbrChannel;
        self.nSamplingRate = nSamplingRate;
        self.nNbrBitsPerSample = nNbrBitsPerSample;        
        self.updateHeaderComputedValues();
    # new - end
    
    def updateHeaderSize( self, nNewDataSize ):
        """
        Update header information relative to the data size to match new data size
        - nNewDataSize: total size of data in bytes
        
        NB: updateHeaderComputedValues() needs to be called before that if you've changed your header properties
        """
        #~ print( "INF: sound.Wav.updateHeaderSize: updating header to match new data size: %s" % nNewDataSize );
        self.nDataSize = int( nNewDataSize );
        self.nNbrSample = int( self.nDataSize * 8 / self.nNbrChannel / self.nNbrBitsPerSample );
        self.rDuration = self.nDataSize / float( self.nAvgBytesPerSec );        
        #~ print( "INF: sound.Wav.updateHeaderSize: updating header to match new data size: new duration: %f" % self.rDuration );
    # updateHeaderSize - end
    
    def updateHeaderSizeFromDataLength( self ):
        """
        Update header information relative to the data in current self.data
        NB: updateHeaderComputedValues() needs to be called before that if you've changed your header properties
        """
        self.updateHeaderSize( int( len( self.data ) * self.nNbrBitsPerSample / 8 ) );
    # updateHeaderSizeFromDataLength - end
    
    def updateHeaderComputedValues( self ):
        """
        Update variable that are computed from properties
        """
        self.nAvgBytesPerSec = int( self.nNbrChannel*self.nSamplingRate*self.nNbrBitsPerSample/8 );
        self.nSizeBlockAlign = int( self.nNbrChannel*self.nNbrBitsPerSample/8 );
        self.dataType = Wav.getDataType( self.nNbrBitsPerSample );
    # updateHeaderComputedValue - end
    
    @staticmethod
    def getDataType( nNbrBitsPerSample ):
        if( nNbrBitsPerSample == 8 ):
            return np.int8;
        if( nNbrBitsPerSample == 16 ):
            return np.int16;
        if( nNbrBitsPerSample == 32 ):
            return np.int32; # NOT TESTED: float ? TODO
            
        raise( BaseException("TODO: handle this NDEV case of unhandled bits per samples" ));
    # getDataType - end
    
    def getNumpyDataType( self ):
        return Wav.getDataType( self.nNbrBitsPerSample )
        
    def getSampleMaxValue( self ):
        if( self.nNbrBitsPerSample == 8 ):
            return 0x7F;
        if( self.nNbrBitsPerSample == 16 ):
            return 0x7FFF;
        if( self.nNbrBitsPerSample == 32 ):
            return 0x7FFFFF; # NOT TESTED: float ? TODO

        raise( BaseException("TODO: handle this NDEV case of unhandled bits per samples" ) );
    # getSampleMaxValue - end
    
    #~ def durationToNbrSample( self, rDuration ):
        #~ return 
        
    #~ def nbrSampleToDuration( self, nNbrSample ):
        #~ return int( nNbrSample / self.nSamplingRate );
    
    def readListData( self, file, bQuiet = True ):
        """
        Takes an open file already located on data just after "LIST" and extract list data.
        Leave the file pointer to the first field after the list data
        Return the length of the field or 0 if it's not a list data field 
        """
        nSizeOfSectionChunck = struct.unpack_from( "i", file.read( 4 ) )[0];
        #print( "nSizeOfSectionChunck: %d"  % nSizeOfSectionChunck );
        data = file.read( 4 );
        #print debug.dumpHexa( data );
        if( data[0] == 'I' and data[3] == 'O' ):
            self.readInfoData( file, nSizeOfSectionChunck - 4, bQuiet = bQuiet );
            return nSizeOfSectionChunck;
        return 0;
    # readListData - end
    
    def readInfoData( self, file, nChunckSize, bQuiet = True ):
        """
        Takes an open file already located on List-INFO just after INFO and extract INFO data.
        Leave the file pointer to the first field after that chunck
        - nChunckSize: length of data to analyse
        """
        
        aDictConvNameField = {
            "INAM": "Name",
            "IART": "Artist",
            "ICMT": "Comments",
            "ICRD": "Date",
            "ISFT": "Software",
        };
        
        nCpt = 0;
        
        while( nCpt < nChunckSize ):
            strFieldName = file.read( 4 ); nCpt += 4;
            if( not bQuiet ):
                print( "DBG: abcdk.sound.wav.readInfoData: strFieldName: '%s'" % strFieldName );
            nFieldDataSize = struct.unpack_from( "i", file.read( 4 ) )[0]; nCpt += 4;
            if( ( nFieldDataSize % 2 ) == 1 ):
                nFieldDataSize += 1; # some software doesn't output the padded size => padding
            if( not bQuiet ):
                print( "DBG: abcdk.sound.wav.readInfoData: nFieldDataSize: %s" % nFieldDataSize );
            strFieldContents = file.read( nFieldDataSize ); nCpt += nFieldDataSize;
            
            while( strFieldContents[len(strFieldContents)-1] == '\0' ):
                strFieldContents = strFieldContents[:-1];
            if( not bQuiet ):
                print( "DBG: abcdk.sound.wav.readInfoData: strFieldContents: '%s'" % strFieldContents );
            self.info[aDictConvNameField[strFieldName]] = strFieldContents;
            
    # readInfoData - end

    def load( self, strFilename, bLoadData = True, bUnpackData = False, bQuiet = True ):
        """
        load a wav file in the Wav object
        return true if ok
        - bLoadData: when set: raw data are loaded in self.data
        - bUnpackData: DEPRECATED
        """
        if not bQuiet: print( "INF: sound.Wav.load: loading '%s'" % strFilename );
        
        timeBegin = time.time();
        try:
            file = open( strFilename, "rb" );
        except BaseException, err:
            print( "ERR: sound.Wav.load: can't load '%s', err: %s" % (strFilename, err) );
            return False;
        # look for the header part
        file.seek( 8L, 0 );
        self.strFormatTag = file.read( 8 );
        if( self.strFormatTag != "WAVEfmt " ):
            file.close();
            print( "ERR: sound.Wav.load: unknown format: '%s'" % self.strFormatTag );
            return False;
            
        nSizeOfWaveSectionChunck = struct.unpack_from( "i", file.read( 4 ) )[0];
        #print( "nSizeOfWaveSectionChunck: %d" % nSizeOfWaveSectionChunck );
        
        nWaveTypeFormat = struct.unpack_from( "h", file.read( 2 ) )[0]; # Type of WAVE format. This is a PCM header = $01 (linear quntization). Other values indicates some forms of compression.
        #print( "nWaveTypeFormat: %d" % nWaveTypeFormat );
        
        self.nNbrChannel  = struct.unpack_from( "h", file.read( 2 ) )[0]; # mono ($01) or stereo ($02). You may try more channels...
        #print( "self.nNbrChannel: %d" % self.nNbrChannel  );

        self.nSamplingRate  = struct.unpack_from( "i", file.read( 4 ) )[0]; # The frequency of quantization (usually 44100 Hz, 22050 Hz, ...)
        #print( "self.nSamplingRate: %d" % self.nSamplingRate  );

        self.nAvgBytesPerSec  = struct.unpack_from( "i", file.read( 4 ) )[0]; # Speed of data stream = Number_of_channels*Samples_per_second*Bits_per_Sample/8
        #print( "self.nAvgBytesPerSec: %d" % self.nAvgBytesPerSec  );
        
        self.nSizeBlockAlign  = struct.unpack_from( "h", file.read( 2 ) )[0]; # Number of bytes in elementary quantization = Number_of_channels*Bits_per_Sample/8
        #print( "self.nSizeBlockAlign: %d" % self.nSizeBlockAlign  );

        self.nNbrBitsPerSample  = struct.unpack_from( "h", file.read( 2 ) )[0]; # Digits of quantization (usually 32, 24, 16, 8). I wonder if this is, for example, 5 ..?
        #print( "self.nNbrBitsPerSample: %d" % self.nNbrBitsPerSample  );
        
        strDataTag = file.read( 4 );
        #print( "strDataTag: '%s'" % strDataTag );
        if( strDataTag != "data" ):
            if( strDataTag == "LIST" ):
                self.readListData( file, bQuiet = bQuiet );
                strDataTag = file.read( 4 );

        if( strDataTag != "data" ):
            if( ord(strDataTag[0]) == 0x16 and ord(strDataTag[1]) == 0x0 and ord(strDataTag[2]) == 0x10 and ord(strDataTag[3]) == 0x0 ):
                print( "WRN: sound.Wav.load: exotic header found, trying to patch it..." );
                # parecord generate another flavoured head, weird...
                file.seek( 20, 1 );
                strDataTag = file.read( 4 );
        if( strDataTag != "data" ):
            nCurrentPos = file.tell();
            print( "ERR: sound.Wav.load: unknown data chunk name: '%s' (0x%x 0x%x 0x%x 0x%x) (at: %d) - opening failed" % (strDataTag, ord(strDataTag[0]), ord(strDataTag[1]), ord(strDataTag[2]), ord(strDataTag[3]), nCurrentPos - 4 ) );
            if( 1 ):
                print( "ERR: sound.Wav.load: contents of file from begin to 64 after:" );
                file.seek( 0 );
                print debug.dumpHexa( file.read(nCurrentPos+64) );
            file.close();
            return False;
            
        self.nDataSize  = struct.unpack_from( "i", file.read( 4 ) )[0];
        # print( "self.nDataSize: %d" % self.nDataSize  );
        
        self.dataType = Wav.getDataType( self.nNbrBitsPerSample );
        
        self.updateHeaderSize( self.nDataSize );
        
        if( bLoadData ):
            try:
                self.data=np.fromfile( file, dtype=self.dataType );
            except BaseException, err:
                print( "ERR: sound.Wav.load: while loading data: err: %s (file:'%s')" % ( err, strFilename ) )
                file.close();
                return False;
            
            nNbrBytesPerSample = int( self.nNbrBitsPerSample / 8 );
            nRealDataSize = len( self.data ) * nNbrBytesPerSample;
            
            if( nRealDataSize != self.nDataSize ):
                # try to decode info field at the end of the file
                if( nRealDataSize > self.nDataSize ):
                    nLenExtraData = int( (nRealDataSize-self.nDataSize) / nNbrBytesPerSample );
                    #~ for i in range(nLenExtraData):
                        #~ print( "DBG: after data %d: %d 0x%x (%c%c)" % (i, self.data[self.nDataSize/nNbrBytesPerSample+i], self.data[self.nDataSize/nNbrBytesPerSample+i],self.data[self.nDataSize/nNbrBytesPerSample+i]&0xFF,(self.data[self.nDataSize/nNbrBytesPerSample+i]>>8)&0xFF) );                    
                    if( self.data[self.nDataSize/nNbrBytesPerSample] == 0x494c and self.data[self.nDataSize/nNbrBytesPerSample+1] == 0x5453  ):
                        # "LIST"
                        nOffsetFromEnd = nLenExtraData*nNbrBytesPerSample - 4;
                        if not bQuiet: print( "WRN: At the end of the file: raw info field is present (at offset from end: %d (0x%x))" % (nOffsetFromEnd,nOffsetFromEnd) );
                        file.seek( -nOffsetFromEnd, os.SEEK_END );
                        nReadSize = self.readListData(file);
                        nReadSize += 8;
                        nRealDataSize -= nReadSize;
                        self.data = self.data[:-int((nReadSize)/nNbrBytesPerSample)];
            
            if( nRealDataSize != self.nDataSize ):
                if not bQuiet: print( "WRN: sound.Wav.load: in '%s', effective data is different than information from header... changing header... (real: %d, header: %d)" % (strFilename,nRealDataSize,self.nDataSize) );
                self.bHeaderCorrected = True;
                self.updateHeaderSizeFromDataLength();
                
        #~ print( "DBG: last data: raw: %s" % self.data[-32:] );
        #~ print( "DBG: last data: %s" % debug.dumpHexaArray( self.data[-32:], 2 ) );

        file.close();

        if not bQuiet: print( "INF: sound.Wav.load: loading '%s' - success (loading takes %5.3fs)" % ( strFilename, time.time() - timeBegin ) );
        return True;
    # load - end
    
    def loadFromRaw( self, strFilename, nNbrChannel = 2, nSamplingRate = 44100, nNbrBitsPerSample = 16 ):
        """
        load from a raw file, default settings are for CD quality
        """
        self.reset();
                
        print( "INF: sound.Wav.loadFromRaw: loading '%s'" % strFilename );
        timeBegin = time.time();
        try:
            file = open( strFilename, "rb" );
        except BaseException, err:
            print( "ERR: sound.Wav.loadFromRaw: can't load '%s'" % strFilename );
            return False;
            
        self.nNbrChannel = nNbrChannel;
        self.nSamplingRate = nSamplingRate;
        self.nNbrBitsPerSample = nNbrBitsPerSample;
        
        self.updateHeaderComputedValues();
        
        self.data = np.fromfile( file, dtype=self.dataType );
        
        self.nDataSize = int( len(self.data) * nNbrBitsPerSample/8 );
        
        self.updateHeaderSize( self.nDataSize );
        
        file.close();
        
        return True;
    # loadFromRaw - end
    
    
    def write( self, strFilename, bAsRawFile = False, bQuiet = False ):
        """
        write current object to a file
        bAsRawFile: just output sound data
        return False on error (empty wav or ...)
        """
        if( len( self.data ) < 1 ):
            print( "WRN: sound.Wav.write: wav is empty, NOT saving it (to '%s')." % (strFilename) );            
            return False;
        timeBegin = time.time();
        file = open( strFilename, "wb" );
        if( not bAsRawFile ):
            self.writeHeader( file );
        self.writeData( file, bAddBeginOfDataChunk = not bAsRawFile );
        file.close();
        rDuration = time.time() - timeBegin;
        if not bQuiet: logging.info( "sound.Wav: successfully saved wav to '%s', duration: %5.3fs, datasize: %d (saving takes %5.3fs)" % (strFilename, self.rDuration, self.nDataSize, rDuration) );
    # write - end
    
    def writeHeader( self, file, bAddBeginOfDataChunk = False, nDataSize = -1 ):
        """
        Write header to the open file
            - bAddBeginOfDataChunk: should be write data chunk in this method ?
            - nDataSize: specific data to write in headers (instead of object current one)
        """
        file.write( "RIFF" );
        if( nDataSize == -1 ):
            nDataSize = self.nDataSize; # default use data size from object
        file.write( struct.pack( "I", 4 + nDataSize + 44 + 4 - 16 ) );
        
        file.write( "WAVE" );
        file.write( "fmt " );
        file.write( struct.pack( "I", 16 ) );
        file.write( struct.pack( "h", 1) ); # self.nWaveTypeFormat
        file.write( struct.pack( "h", self.nNbrChannel) );
        file.write( struct.pack( "i", self.nSamplingRate) );
        file.write( struct.pack( "i", self.nAvgBytesPerSec) );
        file.write( struct.pack( "h", self.nSizeBlockAlign) );
        file.write( struct.pack( "h", self.nNbrBitsPerSample) );        
        
        if( bAddBeginOfDataChunk ):
            file.write( "data" );
            file.write( struct.pack( "I", nDataSize ) );
    # writeHeader - end
    
    def writeData( self, file, bAddBeginOfDataChunk = True ):
        """
        Write current sound data to file
        """
        self.writeSpecificData( file, self.data, bAddBeginOfDataChunk = bAddBeginOfDataChunk );
    # writeData - end
    
    def writeSpecificData( self, file, data, bAddBeginOfDataChunk = True ):
        """
        Write random data to file
        """
        if( not isinstance( data, np.ndarray ) ):
            #~ print( "CEST PAS UNE NP.ARRAY !!!" );
            data = np.array( data, dtype = self.dataType );
        if( bAddBeginOfDataChunk ):
            file.write( "data" );
            file.write( struct.pack( "I", len(data)*self.nNbrBitsPerSample/8 ) );
        #~ print( "DATA: %s" % data[:16] );
        #~ print( "DATA: len: %s" % len( data ) );
        #~ print( "DATA type: %s" % data.dtype );
        data.tofile( file );
    # writeSpecificData - end

    #~ def writeSpecificUnpackedData( self, file, dataUnpacked, bAddBeginOfDataChunk = True ):
        #~ newData = "";
        #~ for i in range( self.nNbrSample ):
            #~ for nNumChannel in range( self.nNbrChannel ):
                #~ if( self.nNbrBitsPerSample == 8 ):
                    #~ newData += struct.pack( "B", dataUnpacked[(i*self.nNbrChannel)+nNumChannel] ); # NOT TESTED !
                #~ elif( self.nNbrBitsPerSample == 16 ):
                    #~ newData += struct.pack( "h", dataUnpacked[(i*self.nNbrChannel)+nNumChannel] );
        
        #~ self.writeSpecificData( file, newData, bAddBeginOfDataChunk = bAddBeginOfDataChunk );
    #~ # writeSpecificUnpackedData - end
    
    def copyHeader( self, rhs ):
        """
        Copy header from a Wav object to another one
        """
        self.reset();
        self.strFormatTag = rhs.strFormatTag;
        self.nNbrChannel = rhs.nNbrChannel;
        self.nSamplingRate = rhs.nSamplingRate;
        self.nAvgBytesPerSec = rhs.nAvgBytesPerSec;
        self.nSizeBlockAlign = rhs.nSizeBlockAlign;
        self.nNbrBitsPerSample = rhs.nNbrBitsPerSample;
        self.nDataSize = rhs.nDataSize;
        self.nNbrSample = rhs.nNbrSample;
        self.dataType = rhs.dataType;        
        self.rDuration = rhs.rDuration;
    # copyHeader - end
    
    def extractOneChannel( self, nNumChannel = 0 ):
        """
        get one channel from some multiband sound
        """
        if( nNumChannel >= self.nNbrChannel ):
            print( "ERR: sound.Wav.extractOneChannel: you ask for a non existing channel, returning empty data list (nbr channel: %d, asked: %d)" %(self.nNbrChannel,nNumChannel) );
            return [];
        return self.data[nNumChannel::self.nNbrChannel];
    # extractOneChannel - end

    def extractOneChannelAndSaveToFile( self, strOutputFilename, nNumChannel = 0 ):
        """
        Extracting one channel from a wav and saving to some file
        - strOutputFilename: output file
        - nNumChannel: channel to extract
        """
        print( "INF: sound.Wav.extractOneChannelAndSaveToFile: extracting channel %d to file '%s'" % (nNumChannel, strOutputFilename ) );
        if( self.nDataSize < 1 or len( self.data ) < 2 ):
            print( "INF: sound.Wav.extractOneChannelAndSaveToFile: original wav has no data (use bLoadData option at loading)" );
            return False;
        timeBegin = time.time();
        
        newWav = Wav();
        newWav.copyHeader( self );
        newWav.nNbrChannel = 1;
        newWav.updateHeaderComputedValues();        
        newWav.updateHeaderSize( self.nDataSize * newWav.nNbrChannel / self.nNbrChannel );
        
        newData = [];
        idx = nNumChannel; # positionnate on good channel
        nIncIdx = int( (self.nNbrChannel) / newWav.nNbrChannel );
        #print( "self.nNbrSample: %s" % self.nNbrSample );
        #print( "self.nIncIdx: %s" % nIncIdx );
        
        #~ for i in range( self.nNbrSample ):
            #~ newData.append( self.data[idx] );
            #~ idx += nIncIdx;
        # equivalent to:
        newData = self.data[nNumChannel::nIncIdx];

        file = open( strOutputFilename, "wb" );
        newWav.writeHeader( file );
        newWav.writeSpecificData( file, newData );
        file.close();
        print( "INF: sound.Wav.extractOneChannelAndSaveToFile: done (datasize: %d, nbrsample: %d) (duration: %5.3fs)" % (newWav.nDataSize, newWav.nNbrSample, time.time() - timeBegin) );
        return True;
    # extractOneChannelAndSaveToFile - end
    
    def addData( self, anValue ):
        """
        Add data at the end of the current sound.
        - anValue: unpacked value  (python value), could be just a value, or a bunch of value eg for a stereo: [val1_chan1, val1_chan2, val2_chan1, val2, chan2 ...]
        return False on error
        """
        nNbrData = len(anValue); 
        nNbrSample = nNbrData/self.nNbrChannel;
        if( self.nNbrChannel*nNbrSample != nNbrData ):
            print( "ERR: sound.Wav.addData: you should provide a number of data multiple of you channel number ! (data:%d, nbrChannel: %d)" % ( nNbrData, self.nNbrChannel ) );
            return False;

        if( not isinstance( anValue, np.ndarray ) ):
            anValue = np.array( anValue, dtype = self.dataType );
        
        #~ print( "DBG: sound.Wav.addData: before concatenate, datalen: %d, other: %d (type:%s)" % (len(self.data), len(anValue), anValue.dtype ) );
        if( len( self.data ) == 0 ):
            self.data = np.copy( anValue ); # so we copy the type !!!
        else:
            self.data = np.concatenate( ( self.data, anValue) );
        #~ print( "DBG: sound.Wav.addData: after concatenate, datalen: %d (type:%s)" % ( len(self.data), self.data.dtype) );
        self.updateHeaderSizeFromDataLength();        
        return True;
    # addData - end
    
    def insertData( self, nOffset, anValue ):
        """
        Insert data at a random point
        - nOffset: offset, in number of sample.
        - anValue: unpacked value  (python value), could be just a value, or a bunch of value eg for a stereo: [val1_chan1, val1_chan2, val2_chan1, val2, chan2 ...]
        return False on error
        """
        nNbrDataSize = len(anValue); 
        nNbrSample = nNbrDataSize/self.nNbrChannel;
        if( self.nNbrChannel*nNbrSample != nNbrDataSize ):
            print( "ERR: sound.Wav.insertData: you should provide a number of data multiple of your channel number ! (data size:%d, nbrChannel: %d)" % ( nNbrDataSize, self.nNbrChannel ) );
            return False;
        # update header:
        self.rDuration += float(nNbrSample)/self.nSamplingRate;        
        self.nDataSize += int( nNbrDataSize*self.nNbrBitsPerSample/8 );
        self.nNbrSample += nNbrSample;
        # update data:
        #~ self.dataUnpacked.append( anValue );
        strFormat = "B";
        if( self.nNbrBitsPerSample == 16 ):
            strFormat = "h";
        
        newData = "";
        for i in range( nNbrDataSize ):
            newData += struct.pack( strFormat, anValue[i] );
        
        nInsertPoint = nOffset*self.nNbrChannel*self.nNbrBitsPerSample/8;
        self.data = self.data[:nInsertPoint] + newData + self.data[nInsertPoint:];

        return True;
    # insertData - end
    
    def replaceData( self, nOffset, anValue, nOperation = 0 ):
        """
        Change data at a random point
        - nOffset: offset, in number of sample.
        - anValue: unpacked value  (python value), could be just a value, or a bunch of value eg for a stereo: [val1_chan1, val1_chan2, val2_chan1, val2, chan2 ...]
        - nOperation: 0: replace, 1: add to data, -1: substract from data
        return False on error
        """
        nNbrElementNew = len(anValue); 
        nNbrSampleNew = int(nNbrElementNew/self.nNbrChannel);
        
        print( "INF: sound.Wav.replaceData: replacing %d samples (nbr element:%d)" % (nNbrSampleNew,nNbrElementNew) );
        if( self.nNbrChannel*nNbrSampleNew != nNbrElementNew ):
            print( "ERR: sound.Wav.replaceData: you should provide a number of element multiple of you channel number ! (data size:%d, nbrChannel: %d)" % ( nNbrElementNew, self.nNbrChannel ) );
            return False;

        if( nNbrSampleNew + nOffset > self.nNbrSample ):
            print( "ERR: sound.Wav.replaceData: too much data to replace sound (nbrSampleToReplace: %d, offset: %d, total sample in sound: %d) (nbrChannel: %d)" % ( nNbrSampleNew, nOffset, self.nNbrSample, self.nNbrChannel ) );
            return False;
                            
        #~ strFormat = "B";
        #~ nMax = 0x7F;
        #~ if( self.nNbrBitsPerSample == 16 ):
            #~ strFormat = "h";
            #~ nMax = 0x7FFF;

        #~ newData = "";
        #~ if( nOperation == 0 ):
            #~ # replace
            #~ for i in range( nNbrDataSize ):
                #~ newData += struct.pack( strFormat, anValue[i] );
        #~ else:
            #~ dataUnpacked = [];
            #~ for i in range( nNbrSample ):
                #~ for nNumChannel in range( self.nNbrChannel ):
                    #~ if( self.nNbrBitsPerSample == 8 ):
                        #~ oneData = struct.unpack_from( "B", self.data, ((i+nOffset)*self.nNbrChannel)+nNumChannel )[0];
                    #~ elif( self.nNbrBitsPerSample == 16 ):
                        #~ oneData = struct.unpack_from( "h", self.data, (((i+nOffset)*self.nNbrChannel)+nNumChannel)*2 )[0];
                    #~ oneData = oneData + nOperation * anValue[i*self.nNbrChannel+nNumChannel];
                    #~ if( oneData > nMax ):
                        #~ oneData = nMax;
                    #~ elif( oneData < -nMax ):
                        #~ oneData = -nMax;
                    #~ dataUnpacked.append( oneData );
            
            #~ newData = "";
            #~ for i in range( nNbrDataSize ):
                #~ newData += struct.pack( strFormat, dataUnpacked[i] );            
                
        #~ # replace newdata
        #~ self.data = self.data[:nOffset*self.nNbrChannel*self.nNbrBitsPerSample/8] + newData + self.data[((nOffset+nNbrSample)*self.nNbrChannel*self.nNbrBitsPerSample/8):];
        
        nInPoint = nOffset*self.nNbrChannel;
        if( nOperation == 0 ):
            self.data[nInPoint:nInPoint+nNbrElementNew] = anValue;
        elif( nOperation == 1 ):
            self.data[nInPoint:nInPoint+nNbrElementNew] += anValue;
        else:
            self.data[nInPoint:nInPoint+nNbrElementNew] -= anValue;
            
        return True;
    # insertData - end    
    
    def delData( self, nOffset, nNbrSample = 1 ):
        """
        Remove data at a random point
        - nOffset: offset, in number of sample.    
        - nNbrSample: number of sample to remove
        """
        nNbrDataSize = nNbrSample * self.nNbrChannel;
        # update header:
        self.nDataSize -= int( nNbrDataSize*self.nNbrBitsPerSample/8 );
        self.rDuration -= float(nNbrSample)/self.nSamplingRate;        
        self.nNbrSample -= nNbrSample;
        self.data = self.data[:nOffset*self.nNbrChannel*self.nNbrBitsPerSample/8] + self.data[((nOffset+nNbrSample)*self.nNbrChannel*self.nNbrBitsPerSample/8):];
        return True;
    # delData - end
    
    def trim( self, rSilenceTresholdPercent = 0. ):
        """
        Remove silence at begin or end
        - rSilenceTresholdPercent: threshold to detect a silence [0..100]
        """

        #~ nLimit = int( 0x7F * rSilenceTresholdPercent / 100 );
        #~ if( self.nNbrBitsPerSample == 16 ):
            #~ nLimit = int( 0x7FFF * rSilenceTresholdPercent / 100 );
        #~ # detect begin
        #~ nNumSample = 0;
        #~ while( True ):
            #~ for nNumChannel in range( self.nNbrChannel ):
                #~ if( self.nNbrBitsPerSample == 8 ):
                    #~ oneData = struct.unpack_from( "B", self.data, ((nNumSample)*self.nNbrChannel)+nNumChannel )[0];
                #~ elif( self.nNbrBitsPerSample == 16 ):
                    #~ oneData = struct.unpack_from( "h", self.data, (((nNumSample)*self.nNbrChannel)+nNumChannel)*2 )[0];
                #~ if( abs(oneData) > nLimit ):
                    #~ break;
            #~ if( abs(oneData) > nLimit ):
                #~ break;
            #~ nNumSample += 1;
            #~ if( nNumSample >= self.nNbrSample ):
                #~ break;
            #~ # while - end
        #~ if( nNumSample > 0 ):
            #~ print( "INF: sound.Wav.trim: at begin: removing %s sample(s) (~%5.3fs)" % (nNumSample, nNumSample/float(self.nSamplingRate) ) );
            #~ self.delData( 0, nNumSample );

        #~ nNumSample = 0;
        #~ while( True ):
            #~ for nNumChannel in range( self.nNbrChannel ):
                #~ if( self.nNbrBitsPerSample == 8 ):
                    #~ oneData = struct.unpack_from( "B", self.data, ((self.nNbrSample-nNumSample-1)*self.nNbrChannel)+nNumChannel )[0];
                #~ elif( self.nNbrBitsPerSample == 16 ):
                    #~ oneData = struct.unpack_from( "h", self.data, (((self.nNbrSample-nNumSample-1)*self.nNbrChannel)+nNumChannel)*2 )[0];
                #~ if( abs(oneData) > nLimit ):
                    #~ break;
            #~ if( abs(oneData) > nLimit ):
                #~ break;
            #~ nNumSample += 1;
            #~ if( nNumSample >= self.nNbrSample ):
                #~ break;            
        #~ # while - end
        #~ if( nNumSample > 0 ):
            #~ print( "INF: sound.Wav.trim: at end: removing %s sample(s) (~%5.3fs)" %  (nNumSample, nNumSample/float(self.nSamplingRate) ) );
            #~ self.delData( self.nNbrSample-nNumSample, nNumSample );
            
        return self.ensureSilence( rTimeAtBegin = 0., rTimeAtEnd = 0., bRemoveIfTooMuch = True, rSilenceTresholdPercent = rSilenceTresholdPercent );
    # trim - end
    
    def addSilence( self, rSilenceDuration = 1., nOffsetNDEV = -1 ):
        nNbrSample = int( self.nSamplingRate * self.nNbrChannel * rSilenceDuration );
        aRawSilence = [0] * nNbrSample; # TODO: np.zeros
        self.addData( aRawSilence );
    # addSilence - end
    
    #
    # Processing
    #
    
    def ensureSilenceAtBegin( self, rTimeAtBegin = 1., bRemoveIfTooMuch = False, rSilenceTresholdPercent = 0. ):
        
        nLimit = int( self.getSampleMaxValue() * rSilenceTresholdPercent / 100 );
        #~ print( "data: %s" % self.data[:32] );
        #~ print( "nLimit: %s" % nLimit );
        
        # beginning        
        nFirstNonSilenceIndex = findFirstValueHigher( self.data, nLimit );
        if( nFirstNonSilenceIndex == -1 ):
            print( "WRN: abcdk.sound.ensureSilenceAtBegin: this sound seems to have only silence!!!" );
            nFirstNonSilenceIndex = len(self.data) - 1;
        #~ print( "nFirstNonSilenceIndex = %d" % nFirstNonSilenceIndex );
        nNumFirstSample = (nFirstNonSilenceIndex/self.nNbrChannel)*self.nNbrChannel;
        #~ print( "nNumFirstSample = %d" % nNumFirstSample );
        nNbrWantedSilenceSample = rTimeAtBegin * self.nSamplingRate;
        if( nNbrWantedSilenceSample > nNumFirstSample ):
            # add silence:
            print( "INF: abcdk.sound.ensureSilenceAtBegin: adding %d sample at beginning (or end)" % nMissingSample );
            nMissingSample = nNbrWantedSilenceSample-nNumFirstSample;
            self.data = np.concatenate( (np.zeros( nMissingSample*self.nNbrChannel, dtype=self.dataType ), self.data ) );
        elif( bRemoveIfTooMuch and nNbrWantedSilenceSample < nNumFirstSample ):
            # remove some
            nRemovingSample = nNumFirstSample-nNbrWantedSilenceSample;
            print( "INF: abcdk.sound.ensureSilenceAtBegin: removing %d sample at beginning (or end)" % nRemovingSample );
            self.data = self.data[nRemovingSample*self.nNbrChannel:];
            
        # end (reverse order ? lazy ?)
        #~ nLastNonSilenceIndex = min( np.argmax( self.data>nLimit ), np.argmax( self.data<-nLimit ) );
        
        self.updateHeaderSizeFromDataLength();
    # ensureSilenceAtBegin - end
    
    def ensureSilence( self, rTimeAtBegin = 1., rTimeAtEnd = 1., bRemoveIfTooMuch = False, rSilenceTresholdPercent = 0. ):
        """
        Ensure there's enough silence at begin or end of a sound
        - timeAtBegin: time in sec at begin of the sound
        - timeAtEnd: ...
        - bRemoveIfTooMuch: if there's more silence than required, did we remove some ?
        - rSilenceTresholdPercent: how to qualify silence ?
        """
        self.ensureSilenceAtBegin( rTimeAtBegin = rTimeAtBegin, bRemoveIfTooMuch = bRemoveIfTooMuch, rSilenceTresholdPercent = rSilenceTresholdPercent );
        self.data = self.data[::-1]; # reverse data (WRN: left and right are swapped too, but our computation is doing the same on each channels)
        self.ensureSilenceAtBegin( rTimeAtBegin = rTimeAtEnd, bRemoveIfTooMuch = bRemoveIfTooMuch, rSilenceTresholdPercent = rSilenceTresholdPercent );
        self.data = self.data[::-1]; # revert it back
    # def ensureSilence - end
    
    def removeGlitch( self, rGlitchMaxTresholdPercent = 5., rGlitchMaxDurationSec = 0.01, rSilenceTresholdPercent = 1., rSilenceMinDurationSec = 0.020 ):
        """
        Remove glitch, by replacing them with samples at 0.
        A glitch is defined to be a small noise in peak and duration, surrounded by blank
        
        - rGlitchMaxTresholdPercent: the absolute peak of the glitch has to be lower than this value
        - rGlitchMaxDurationSec: the peak duration must be shorter or equal to that duration (for reference a 's' short is about 0.084 sec, and a small lingual glitch is 0.003s, a 'p' as in handicap is a 0.058s length (but hard part is only 0,025 long) with a very small peak: 812)
        - rSilenceTresholdPercent: the maximum volume to detect silence
        - rSilenceMinDurationSec: the minimal duration of no sound surrounding the peak
        
        NB: This method will also remove all constant lower sound (bruit de fond) < rMaxGlitchTresholdPercent
        """
        timeBegin = time.time();
        nGlitchLimit =  int( self.getSampleMaxValue() * rGlitchMaxTresholdPercent / 100 );
        nSilenceLimit = int( self.getSampleMaxValue() * rSilenceTresholdPercent / 100 );
        
        nGlitchNumSampleMaxDuration = int( rGlitchMaxDurationSec * self.nSamplingRate );
        nSilenceNumSampleMinDuration = int( rSilenceMinDurationSec * self.nSamplingRate );
                    
        rMarginAroundSilenceBlanking = 0.1; # in sec
        nSilenceAroundSilenceBlanking = int( rMarginAroundSilenceBlanking * self.nSamplingRate );
        
        
        print( "nSilenceLimit: %d, nGlitchLimit: %d, nGlitchNumSampleMaxDuration: %d, nSilenceNumSampleMinDuration: %d" % ( nSilenceLimit, nGlitchLimit, nGlitchNumSampleMaxDuration, nSilenceNumSampleMinDuration ) );
                    
        aPosGlitchBegin = [0]*self.nNbrChannel; # for each channel, the position of beginning glitch
        aPosSilenceBegin = [0]*self.nNbrChannel; # for each channel, the position of beginning silence
        aPosLastSoundEnd = [0]*self.nNbrChannel; # for each channel, the last time with sound
        anState = [0]*self.nNbrChannel; # for each channel: the nature of current sound: 0: real silence, 1: glitch, 2: sound, 3: short silence after glitch, 4: short silence after sound

        nNbrGlitch = 0;
        nNumSample = 0;
        nNbrSampleReplace = 0;
        while( True ):
            for nNumChannel in range( self.nNbrChannel ):
                val = self.data[(nNumSample*self.nNbrChannel)+nNumChannel];
                val = abs(val);
                nCurrentState = anState[nNumChannel];
                newState = nCurrentState;
                    
                if( nCurrentState == 0 ):
                    if( val > nGlitchLimit ):
                        newState = 2;
                    elif( val > nSilenceLimit ):
                        newState = 1;
                        aPosGlitchBegin[nNumChannel] = nNumSample;
                elif( nCurrentState == 1 ):
                    if( val > nGlitchLimit ):
                        newState = 2;
                    elif( val < nSilenceLimit ):
                        newState = 3;
                        aPosSilenceBegin[nNumChannel] = nNumSample;
                    elif( nNumSample - aPosGlitchBegin[nNumChannel] >= nGlitchNumSampleMaxDuration ):
                        # too long => sound
                        newState = 2;
                elif( nCurrentState == 2 ):
                    if( val < nSilenceLimit ):
                        newState = 4;
                        aPosSilenceBegin[nNumChannel] = nNumSample;
                        aPosLastSoundEnd[nNumChannel] = nNumSample;
                elif( nCurrentState == 3 ):
                    if( val > nGlitchLimit ):
                        newState = 2;
                    elif( val > nSilenceLimit ):
                        newState = 1;
                    elif( nNumSample - aPosSilenceBegin[nNumChannel] >= nSilenceNumSampleMinDuration ):
                        newState = 0;
                        # erase this glitch
                        print( "Channel%d: Erasing glitch between %s (%5.3fs) and %s (%5.3fs)" % (nNumChannel, aPosGlitchBegin[nNumChannel],aPosGlitchBegin[nNumChannel]/float(self.nSamplingRate), nNumSample, nNumSample/float(self.nSamplingRate) ) );
                        nNbrGlitch += 1;
                        self.data[ (aPosGlitchBegin[nNumChannel]*self.nNbrChannel)+nNumChannel:(nNumSample*self.nNbrChannel)+nNumChannel:self.nNbrChannel]=[0]*(nNumSample-aPosGlitchBegin[nNumChannel]);
                elif( nCurrentState == 4 ):
                    if( val > nSilenceLimit ):
                        newState = 2;
                    elif( nNumSample - aPosSilenceBegin[nNumChannel] >= nSilenceNumSampleMinDuration ):
                        newState = 0;
                        # nothing to do!
                        
                if( newState != nCurrentState ):
                    if( nNumSample < 300000 ):
                        print( "Channel%d: sample: %d (%5.3fs), new state: %d, data: %d" % (nNumChannel,nNumSample,nNumSample/float(self.nSamplingRate), newState,val) );
                    anState[nNumChannel] = newState;
                    if( newState == 2 ):
                        # we add a small respiration to leave sound trail and attacks
                        if( aPosLastSoundEnd[nNumChannel] == 0 ):
                            nBegin = 0;
                        else:
                            nBegin = aPosLastSoundEnd[nNumChannel] + nSilenceAroundSilenceBlanking;
                        nEnd = nNumSample - nSilenceAroundSilenceBlanking;
                        if( nBegin < nEnd ):
                            print( "Channel%d: Blanking silence between %s (%5.3fs) and %s (%5.3fs)" % ( nNumChannel, nBegin, nBegin/float(self.nSamplingRate), nEnd, nEnd/float(self.nSamplingRate) ) );
                            self.data[ (nBegin*self.nNbrChannel)+nNumChannel:(nEnd*self.nNbrChannel)+nNumChannel:self.nNbrChannel]=[0]*(nEnd-nBegin);
                        
            # for each chan - end
            nNumSample += 1;
            if( nNumSample % 10000 == 0 ):
                print( "nNumSample: %d (state[0]: %d)" % (nNumSample, anState[0]) );  # TODO: depacké pour pouvoir modifier juste un bout de chaine OU regarder comment remplacer un bout de chaine sans toute la recopier!!! => tres long !!!
            
            if( nNumSample >= self.nNbrSample ):
                break;

            # quick output for testing
            #~ if( nNumSample >= 20000 ):
                #~ break;
                
        # while - end
        
        rDuration = time.time()-timeBegin;
        
        print( "INF: sound.Wav.removeGlitch: nNbrGlitch: %d, (time taken: %5.3fs)" % (nNbrGlitch, rDuration ) );
        
        return True;
    # removeGlitch - end
    
    def getPeakValue( self ):
        """
        Return the peak value [0..1] of the sound (represent the fact that the sound is loud or not) (cheaper than rms power)
        """
        nCurrentMax = max( self.data.max(), -self.data.min() );
        return float(nCurrentMax) / self.getSampleMaxValue()
    # getPeakValue - end
    
    def normalise( self, rWantedMax = 100. ):
        """
        Normalise sound to achieve maximum power (just a scale)
        - rWantedMax: value of peak to achieve (in %)
        Return True if modification has been made, False if no modification was apply
        """
        nWantedMax = int( self.getSampleMaxValue() * rWantedMax / 100);
        nCurrentMax = max( self.data.max(), -self.data.min() );
        rRatio = nWantedMax / float(nCurrentMax);
        if( nCurrentMax == nWantedMax ):
            return False;
        print( "INF: sound.Wav.normalise: nCurrentMax: %s" % nCurrentMax );
        print( "INF: sound.Wav.normalise: nWantedMax: %s" % nWantedMax );            
        print( "INF: sound.Wav.normalise: applying a %f ratio to the whole sound" % rRatio );
        self.data *= rRatio;  # another option is to make a np.round(self.data*rRatio), but it's perhaps less linear (on a linear elevation for example)
        return True;
    # normalise - end
    
    def isEqual( self, rhs ):
        if( not self.hasSameProperties( rhs ) ):
            return False;
        bRet = np.all( self.data == rhs.data );
        if( not bRet ):
            if( len( self.data ) != len( rhs.data ) ):
                print( "INF: sound.Wav.isEqual: length of data is different: %d != %d" % ( len( self.data ), len( rhs.data ) ) );
            bLookForDifference = True;
            if( bLookForDifference ):
                # automatic method:
                #~ listdiff = self.data - rhs.data;
                #~ u, inv = np.unique(listdiff, return_inverse=True)
                #~ print u;
                #~ print inv; # we should the one pointing remove zero ! TODO !!!
                # manual method:
                nNbrDiff = 0;
                for i in range( len( self.data ) ):
                    if( self.data[i] != rhs.data[i] ):
                        if( nNbrDiff < 20 ):
                            print( "INF: sound.Wav.isEqual: DIFFERENCE at offset %d: data: %d (0x%02x) and %d (0x%02x)"  % ( i, self.data[i],self.data[i],rhs.data[i],rhs.data[i] ) );
                        nNbrDiff += 1;
                print( "INF: sound.Wav.isEqual: %d DIFFERENCE(s) found..." % nNbrDiff );
            
        return bRet;
    # isEqual - end

    def hasSameProperties( self, rhs ):
        if( self.nNbrChannel != rhs.nNbrChannel ):
            print( "INF: sound.Wav.hasSameProperties: different nbr channel: %s != %s" % ( self.nNbrChannel,  rhs.nNbrChannel) );
            return False;
        if( self.nSamplingRate != rhs.nSamplingRate ):
            print( "INF: sound.Wav.hasSameProperties: different sampling rate: %s != %s" % ( self.nSamplingRate,  rhs.nSamplingRate) );
            return False;
        if( self.nAvgBytesPerSec != rhs.nAvgBytesPerSec ):
            print( "INF: sound.Wav.hasSameProperties: different nAvgBytesPerSec: %s != %s" % ( self.nAvgBytesPerSec,  rhs.nAvgBytesPerSec) );
            return False;
        if( self.nSizeBlockAlign != rhs.nSizeBlockAlign ):
            print( "INF: sound.Wav.hasSameProperties: different nSizeBlockAlign: %s != %s" % ( self.nSizeBlockAlign,  rhs.nSizeBlockAlign) );
            return False;
        if( self.nNbrBitsPerSample != rhs.nNbrBitsPerSample ):
            print( "INF: sound.Wav.hasSameProperties: different nNbrBitsPerSample: %s != %s" % ( self.nNbrBitsPerSample,  rhs.nNbrBitsPerSample) );
            return False;
        #~ if( self.nDataSize != rhs.nDataSize ):
            #~ print( "INF: sound.Wav.hasSameProperties: different nNbrBitsPerSample: %s != %s" % ( self.nDataSize,  rhs.nDataSize) );
            #~ return False;
        return True;
    # hasSameProperties - end
    
    def split( self, rSilenceTresholdPercent = 0.1, rSilenceMinDuration = 0.3, nExtractJustFirsts = -1 ):
        """
        split a wav into a bunch of wav
        - rSilenceTresholdPercent: how to qualify silence ?
        - rSilenceMinDuration: how to qualify silence ? (in second)
        - nExtractJustFirsts: limit extraction to the n'th first
        return a list of new created wav
        """
        nLimit = int( self.getSampleMaxValue() * rSilenceTresholdPercent / 100 );        
        print( "INF: sound.Wav.split: splitting a sound of %5.3fs, using silence limits at %d for %5.3fs" % (self.rDuration, nLimit, rSilenceMinDuration) ); 
        aSplitted = [];
        
        precalcWavIsNotSilence = np.abs(self.data)>nLimit;

        #~ print self;
        
        nCurrentPos = 0; # in data index (not sample)
        nSilenceMinLenData = rSilenceMinDuration * self.nAvgBytesPerSec * 8 / self.nNbrBitsPerSample;
        while( nCurrentPos < len(self.data) ):
            
            # first find the beginning of a sound            
            nFirstNonSilenceIndex = findFirstTrueValue( precalcWavIsNotSilence[nCurrentPos:] );
            #~ print( "nFirstNonSilenceIndex (brut): %d" % nFirstNonSilenceIndex );
            if( nFirstNonSilenceIndex == -1 ):
                # all remaining sound are silence!
                break;
            nFirstNonSilenceIndex += nCurrentPos;
            nNumFirstSample = nFirstNonSilenceIndex/self.nNbrChannel;
            print( "INF: sound.Wav.split: found a sound at sample %d" % nNumFirstSample );
            nCurrentPos = nFirstNonSilenceIndex; # so at the end, we're stopping
            
            # then find end
            nEndOfSilence = nNumFirstSample*self.nNbrChannel; # init of the loop
            while( nEndOfSilence < len(self.data) ):
                #nFirstSilenceIndex = np.argmax( np.abs(self.data[nEndOfSilence:])<=nLimit );
                nFirstSilenceIndex = findFirstFalseValue( precalcWavIsNotSilence[nEndOfSilence:] );                
                #~ print( "nFirstSilenceIndex (brut): %d (from %d)" % (nFirstSilenceIndex, nEndOfSilence) );
                if( nFirstSilenceIndex == -1 ):
                    break;
                nFirstSilenceIndex += nEndOfSilence;
                # ensure there's enough silence
                nEndOfSilence = findFirstTrueValue( precalcWavIsNotSilence[nFirstSilenceIndex:] );
                #~ print( "nEndOfSilence (brut): %d (data: %d) (offset: %d)" % (nEndOfSilence, self.data[nFirstSilenceIndex+nEndOfSilence],nEndOfSilence + nFirstSilenceIndex) );
                # positionnate onto the end of the silence for next time
                if( nEndOfSilence == -1 ):
                    nCurrentPos = len(self.data);
                else:
                    nCurrentPos = nEndOfSilence + nFirstSilenceIndex;
                    
                if( nEndOfSilence > nSilenceMinLenData or nEndOfSilence == -1 ):
                    break;
                nEndOfSilence += nFirstSilenceIndex;
            # while - end
            
            # each time we're out, we've got a silence or we're at the end => new split
            if( nFirstSilenceIndex == -1 ):
                break;
            nNumLastSample = nFirstSilenceIndex/self.nNbrChannel;
            print( "INF: sound.Wav.split: found the end of that sound at sample %d" % nNumLastSample );
            if( nNumLastSample - nNumFirstSample > 4000 ):
                w = Wav();
                w.copyHeader( self );
                w.data = np.copy(self.data[nNumFirstSample*self.nNbrChannel:nNumLastSample*self.nNbrChannel]);
                nPeakMax = max( max( w.data ), -min( w.data ) );
                if( nPeakMax > self.getSampleMaxValue() / 8 ): # remove glitch sound
                    w.updateHeaderSizeFromDataLength();
                    print( "INF: sound.Wav.split: new split of %5.2fs" % w.rDuration );
                    aSplitted.append( w );
            #~ print( "nCurLocalVs: %s" % nCurLocalVs );
            if( nExtractJustFirsts != -1 and nExtractJustFirsts == len(aSplitted) ):
                print( "WRN: sound.Wav.split: got enough split (%d), leaving..." % len(aSplitted) );
                break;
        # while - end
        print( "INF: sound.Wav.split: created %d wav(s)" % len( aSplitted ) );
        return aSplitted;
    # split - end
    
    def __str__( self ):
        strOut = "";
        strOut += "- strFormatTag: '%s'\n" % self.strFormatTag;
        strOut += "- nNbrChannel: %s\n" % str( self.nNbrChannel );
        strOut += "- nSamplingRate: %s\n" % self.nSamplingRate; # print with "%s" so we detect floating stuffs
        strOut += "- nAvgBytesPerSec: %s\n" % self.nAvgBytesPerSec;
        strOut += "- nSizeBlockAlign: %s\n" % self.nSizeBlockAlign;        
        strOut += "- nNbrBitsPerSample: %s\n" % self.nNbrBitsPerSample;
        strOut += "- nDataSize: %s\n" % self.nDataSize;
        strOut += "- nNbrSample: %s\n" % self.nNbrSample;
        strOut += "- rDuration: %f\n" % self.rDuration;
        strOut += "- info: %s\n" % self.info;
        strOut += "- data (size)(in type): %d\n" % len( self.data );
        strOut += "- dataType: %s\n" % self.dataType;
        if( len( self.data ) > 0 ):
            for i in range( min(16, len(self.data) ) ):
                strOut += "- data[%d]: 0x%x (%d)\n" % ( i, self.data[i], self.data[i] );
            strOut += "- ...";
        #~ strOut += "- dataUnpacked (size): %d\n" % len( self.dataUnpacked );            
        #~ if( len( self.dataUnpacked ) > 0 ):
            #~ for i in range( min(4,len(self.dataUnpacked) ) ):
                #~ strOut += "- dataUnpacked[%d]: 0x%x (%d)\n" % ( i, self.dataUnpacked[i], self.dataUnpacked[i] );
        return strOut;
# class Wav - end



def isEqual( strFilename1, strFilename2 ):
    wav1 = Wav();
    if( not wav1.load( strFilename1 ) ):
        return False;
    wav2 = Wav();
    if( not wav2.load( strFilename2 ) ):
        return False;
    return wav1.isEqual( wav2 );    
# isEqual - end    

    

def getInfoFromWav( strFilename, bReadData = False ):
    """
    Return a string describing wav info
    """
    wav = Wav();
    wav.load( strFilename, bLoadData = bReadData, bUnpackData = False );
    return str( wav );
# getInfoFromWav - end

def substract( strFilename1, strFilename2, strFilenameOut ):
    """
    substract 2 from 1
    """
    
    wav1 = Wav();
    wav1.load( strFilename1, bLoadData = True, bUnpackData = False );
    wav2 = Wav();
    wav2.load( strFilename2, bLoadData = True, bUnpackData = True );
    
    if( wav1.nNbrChannel != wav2.nNbrChannel ):
        print( "ERR: sound.Wav.substract: the two sources must have same channel numbers" );
        return False;    
    if( wav1.nSamplingRate != wav2.nSamplingRate ):
        print( "ERR: sound.Wav.substract: the two sources must have same sampling rate" );
        return False;
    if( wav1.nNbrBitsPerSample != wav2.nNbrBitsPerSample ):
        print( "ERR: sound.Wav.substract: the two sources must have same bits per sample" );
        return False;                
    wav1.replaceData( 0, wav2.data, -1 );    
    return wav1.write( strFilenameOut );
# substract - end    
        
def cleanAllWavInOneDirectory( strPath, nCleanMode = 1, bOverwriteSourceFile = False ):
    """
    - nCleanMode:
      1: for speech
      2: for sample (tracker)
    """
    if( False ):
        w = Wav( "c:\\temp\\01_Patients_annonce.wav" );
        #~ w = Wav( "c:\\temp\\08_Patients_ma_chambre.wav" );
        timeBegin = time.time();
        w.removeGlitch();
        #~ w.ensureSilence( rTimeAtBegin = 0.2, rTimeAtEnd = 2., bRemoveIfTooMuch=True, rSilenceTresholdPercent=0.8 );
        #~ w.normalise();
        #~ w.normalise();
        print( "time taken: %5.3fs" % (time.time() - timeBegin ) );
        #w.data=w.data[::-1];
        w.write( "c:\\temp\\output.wav" );
        substract( "c:\\temp\\01_Patients_annonce.wav", "c:\\temp\\output.wav", "c:\\temp\\output2.wav" );
        
    for strFilename in sorted( os.listdir( strPath ) ):
        if( not ".wav" in strFilename ):
            continue;
        if( "_clean.wav" in strFilename ):
            continue;            
        w = Wav( strPath + strFilename );
        timeBegin = time.time();
        if( nCleanMode == 1 ):
            w.removeGlitch();
            w.ensureSilence( rTimeAtBegin = 0.2, rTimeAtEnd = 2., bRemoveIfTooMuch=True, rSilenceTresholdPercent=0.8 );
            w.normalise();
        if( nCleanMode == 2 ):
            w.normalise();            
            # we normalise before so the threshold is higher !
            w.ensureSilence( rTimeAtBegin = 0.0, rTimeAtEnd = 0., bRemoveIfTooMuch=True, rSilenceTresholdPercent=1.7 ); 
        
        print( "time taken: %5.3fs" % (time.time() - timeBegin ) );
        if( bOverwriteSourceFile ):
            strFilenameOut = strFilename;
        else:
            strFilenameOut = strFilename.replace( ".wav", "_clean.wav" );
        w.write( strPath + strFilenameOut );
# cleanAllWavInOneDirectory - end

#cleanAllWavInOneDirectory( "C:\\perso\\sound\\new\\" );
#~ for strType in ["laaa", "naaa", "mmm", "ouu", "piano", "laaa_pitched"]:
    #~ cleanAllWavInOneDirectory( "C:\\work\\Dev\\git\\appu_shared\\sdk\\abcdk\\data\\wav\\tracker\\%s\\" % strType, nCleanMode = 2, bOverwriteSourceFile = True );
#~ exit()

        
########################################################
## Test Zone
########################################################
strStereoSoundName = "c:\\work\\pythonscript\\data\\test2_stereo.wav";
strLongTextFile = "c:\\work\\pythonscript\\data\\long_text.wav";
strSentences = "c:\\work\\pythonscript\\data\\a_sentences.wav";
strOutTemp = "c:\\temp\\out.wav";

#wav = Wav();
#wav.load( strLongTextFile, bLoadData = True, bUnpackData = False );
#~ wav.load( "C:\\montagevideo2\\1328113989.wav" );
#~ wav.load( "D:\\dev\\data\\nao_sound_4_channels.wav", bLoadData = True, bUnpackData = False );
#~ print( "wav: %s" % str( wav ) );
#~ for i in range( 4 ):
    #~ wav.extractOneChannelAndSaveToFile( "d:\\mononew3_%d.wav" % i, i );
    
#~ with open('D:\\dev\\data\\nao_sound_4_channels.wav', 'rb') as f:
    #~ read_data = f.read()
    #~ print( "read_data: %d" % ord(read_data[0]) );
#~ f.closed
#~ wav.insertData( 0, [10000,20000,30000,-30000] ); # works !
#~ wav.insertData( 256*16, [0]*10000 );  # works !
#~ wav2 = Wav();
#~ wav2.load( "c:\\work\\pythonscript\\data\\test2_stereo.wav" );
#~ wav.replaceData( 256*16, wav2.dataUnpacked[256*16*2:256*16*2+6000], -1 );  # works !
#~ wav.trim( 1. );
#~ wav.removeGlitch();
#~ wav.write( strOutTemp );

#~ substract( strStereoSoundName, strStereoSoundName, strOutTemp );

def generateFatBass( rSoundDuration = 1., rFrequency = 440. ):
    ##### TODO: rewrite with np !!!
    timeBegin = time.time();
    wav = Wav();
    wav.new();
    #~ wav.addData( [0,30000, -30000] );
    rT = 0.;
    nSampling = 44100;
    nMax = 0x7FFF;
    rBaseFrequencyCounter = -nMax;
    rResonanceFrequencyCounter = -nMax;
    rSlightDelta = 50; # 50 is like in the wikipedia
    dataBuf = "";
    strFormat = "h";
    while( rT < rSoundDuration ):
        
        #~ nVal = nMax * math.sin( rT*2*math.pi*rFrequency ); # simple sinus
        
        if( 0 ):
            # Simulating a resonant filter, as seen in http://en.wikipedia.org/wiki/Phase_distortion_synthesis
            
            rBaseFrequencyCounter += rFrequency*nMax/nSampling;
            if( rBaseFrequencyCounter > nMax ):
                rBaseFrequencyCounter = -nMax;
                rResonanceFrequencyCounter = -nMax; # resetted by base

            rResonanceFrequencyCounter += (rFrequency+rSlightDelta)*nMax/nSampling;
            if( rResonanceFrequencyCounter > nMax ):
                rResonanceFrequencyCounter = -nMax;
            
            #~ nVal = rBaseFrequencyCounter;            
            #~ nVal = rResonanceFrequencyCounter;
            #~ nVal =  nMax * math.sin( rResonanceFrequencyCounter*2*math.pi/nMax );
            nVal =  nMax * math.sin( rResonanceFrequencyCounter*2*math.pi/nMax ) * (-rBaseFrequencyCounter/nMax);
            
        if( 0 ):
            # a variation about a square signal from the sinus formulae:
            # x(t) = (pi/4) * sum[0,+inf][ ( sin((2k+1)2*pi*f*t) / (2k+1) ];
            #~ nDegrees = int( 6 * math.sin( rT / 10. ) ) + 1;
            nDegrees = 6;
            rVal = 0.;            
            for k in range( nDegrees ):
                rVal += math.sin((2*k+1)*2*math.pi*rFrequency*rT) / (2*k+1);
            nVal = int( rVal * (nMax * math.pi/4) );
        
        if( 0 ):
            nVal = nMax * math.sin( rT*2*math.pi*rFrequency );
            nVal += nMax * math.sin( rT*2*math.pi*(rFrequency+0.5));
            
        if( 1 ):
            # a sum of sinus
            rVal = 0.;
            nNbrSinus = 2;
            for k in range( nNbrSinus ):
                rVal += math.sin(rT*2*math.pi*(rFrequency+(10.8*math.sin(k*0.5*rT)) ));
            nVal = int( rVal * nMax/nNbrSinus );

        # hard clipping
        if( nVal > nMax ):
            nVal = nMax;
        if( nVal < -nMax ):
            nVal = -nMax;

        
        rT += 1./nSampling;
        # wav.addData( [nVal] ); # not optimal
        
        dataBuf += struct.pack( strFormat, nVal );
    # while - end
    wav.data = dataBuf;
    self.updateHeaderSizeFromDataLength();
    
    wav.write( "/tmp/generated.wav" );
    rDuration = time.time()-timeBegin;
    print( "INF: sound.generateFatBass: generating a sound of %5.3fs in %5.3fs (%5.2fx RT)" % (rSoundDuration,rDuration,rSoundDuration/rDuration) );
# generateFatBass - end
#~ generateFatBass( rSoundDuration = 48, rFrequency = 200. ); # metttre une durée de 1 ou 2 periode pour débugger!

def testPlayWav():
    import wave
    import sys
    import alsaaudio
    strFilename = "/tmp/generated.wav";
    wavfile = wave.open(strFilename, 'r')
    output = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK)
    output.setchannels(wavfile.getnchannels())
    output.setrate(wavfile.getframerate())
    output.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    output.setperiodsize(320)
    counter = wavfile.getnframes() /320
    while counter != 0:
        counter -= 1
        output.write(wavfile.readframes(320))
    wavfile.close()
# testPlayWav - end
#~ testPlayWav();

def convertWavFile( strSrc, strDst, nNewSamplingFrequency = -1, nNewNbrChannel = -1, bAsRawFile = False ):
    """
    convert a file to another sampling/channel or to raw
    - nNewSamplingFrequency: new frequency, -1 if same
    - nNewNbrChannel: new channel number, -1 if same    
    - bAsRawFile: if True: save it as a raw file, (else it's a standard raw)
    return True if ok
    """
    timeBegin = time.time();
    wavSrc = Wav();
    bRet = wavSrc.load( strSrc, bUnpackData = True );
    #~ print( "DBG: abcdk.sound.convertWavFile: src:" + str(wavSrc) );
    if( not bRet ):
        print( "ERR: abcdk.sound.convertWavFile: source file '%s' not found" % ( strSrc ) );
        return False;
    if( nNewSamplingFrequency == -1 ):
        nNewSamplingFrequency = wavSrc.nSamplingRate;
    if( nNewNbrChannel == -1 ):
        nNewNbrChannel = wavSrc.nNbrChannel;
    nNewBitPerSample = wavSrc.nNbrBitsPerSample;
    print( "INF: abcdk.sound.convertWavFile: '%s' [%dHz, %d channel(s), %d bits] => '%s' [%dHz, %d channel(s), %d bits]" % (strSrc, wavSrc.nSamplingRate, wavSrc.nNbrChannel, wavSrc.nNbrBitsPerSample, strDst, nNewSamplingFrequency, nNewNbrChannel, nNewBitPerSample) );
    wavDst = Wav();
    wavDst.new( nSamplingRate = nNewSamplingFrequency, nNbrChannel = nNewNbrChannel, nNbrBitsPerSample =  nNewBitPerSample );
    nNumSample = 0;
    rNumSamplePrecise = 0; # point the real avancing for inflating
    nNumPrevSample = 0;
    
    dataBuf = []; # np.zeros( 0, dtype = wavSrc.dataType ); TODO: initiate an np array with a good final size !
    while( nNumSample < wavSrc.nNbrSample ):
        #~ if( nNumSample < 1000 ):
            #~ print( "nNumSample: %s" % nNumSample );
        aSample = wavSrc.data[nNumSample*wavSrc.nNbrChannel:(nNumSample+1)*wavSrc.nNbrChannel].tolist();
        # resampling
        if( nNewSamplingFrequency == wavSrc.nSamplingRate ):
            nNumSample += 1;
        else:
            if( nNewSamplingFrequency < wavSrc.nSamplingRate ):
                if( nNumSample - nNumPrevSample > 1 ):
                    # antialiasing:
                    # add a part of the previous missed sample values, to this one
                    for n in range( nNumPrevSample, nNumSample ):
                        for i in range( wavSrc.nNbrChannel ):
                            aSample[i] += wavSrc.data[n*wavSrc.nNbrChannel+i];
                    for i in range( wavSrc.nNbrChannel ):
                        aSample[i] /= (nNumSample - nNumPrevSample)+1;
                # prepare next sample
                nNumPrevSample = nNumSample;
                #~ nNumSample += int(round(wavSrc.nSamplingRate/float(nNewSamplingFrequency))); # this works only when division is integer (22050=>11025...)
                rNumSamplePrecise += wavSrc.nSamplingRate/float(nNewSamplingFrequency); # for non integer div: (22050=>14000...) in that case we should interpolate
                nNumSample = int( rNumSamplePrecise ); # don't round it ! (or?)
            else:
                # inflate
                # here we should interpolate value between original sample (currently the same value is pasted a number of time)
                if( nNumSample+1 < wavSrc.nNbrSample ):
                    aNextSample = wavSrc.data[(nNumSample+1)*wavSrc.nNbrChannel:(nNumSample+2)*wavSrc.nNbrChannel];
                    temp = [0]*wavSrc.nNbrChannel;
                    rRatioNextData = rNumSamplePrecise - nNumSample;
                    for i in range( wavSrc.nNbrChannel ):
                        temp[i] = aSample[i] * (1.-rRatioNextData) + aNextSample[i] *rRatioNextData;
                    aSample = temp;
                nNumPrevSample = nNumSample;
                rNumSamplePrecise += wavSrc.nSamplingRate/float(nNewSamplingFrequency);
                nNumSample = int( rNumSamplePrecise ); # don't round it !
                
                
        # convert channels
        if( nNewNbrChannel != wavSrc.nNbrChannel ):
            if( nNewNbrChannel > wavSrc.nNbrChannel ):
                # expand
                for i in range( wavSrc.nNbrChannel, nNewNbrChannel ):
                    aSample.append( aSample[i%wavSrc.nNbrChannel] ); # L,R => L,R,L,R
            else:
                # reduce: 
                if( nNewNbrChannel == 1 ):
                    # L, R => S: (L+R)/2
                    # 2,3,4 channels  => S: 1 avg (channel)                           
                    aSample = [sum( aSample ) / len( aSample )];
                elif( nNewNbrChannel == 2 ):
                    # C1, C2, C3 => L:(C1+C3)/2, R:(C2+C3)/2
                    # C1,C2,C3,C4 => L:(C1+C3)/2, R:(C2+C4)/2                                    
                    temp = [0]*nNewNbrChannel;
                    temp[0]  = ( aSample[0]+aSample[2] ) / 2;
                    temp[1]  = ( aSample[2]+aSample[-1] ) / 2; # [-1] => C3 or C4 depending on the channel number
                    aSample = temp;
                else:
                    print( "ERR: abcdk.sound.convertWavFile: while converting file '%s': unhandled channel conversion (%d=>%d)" % ( strSrc,  nNewNbrChannel, nNewNbrChannel) );
                    return False;
                    
        #~ wavDst.addData( aSample ); # not optimal: a lot of jumps to addData there... # for a 19sec long sound, gain was from 10s to 2.8s by removing this call !
        for val in aSample:
            dataBuf.append( val );
    # while - end
    #print( "len( dataBuf ): %d" % len( dataBuf ) );
    wavDst.data = np.array( dataBuf, dtype = wavDst.dataType );
    #print( "len( wavDst.data ): %d" % len( wavDst.data ) );
    wavDst.updateHeaderSizeFromDataLength();
    
    wavDst.write( strDst, bAsRawFile = bAsRawFile );
    #~ print( "DBG: abcdk.sound.convertWavFile: dst:" + str(wavDst) );
    print( "INF: abcdk.sound.convertWavFile: done in %.2fs" % ( time.time() - timeBegin ) );
    return True;
# convertWavFile - end


def autoTest_Wav( strDataTestPath ):
    assert( isEqual( strDataTestPath + "test_11_1_16_ref.wav", strDataTestPath + "test_11_1_16_ref.wav" ) );
    assert( not isEqual( strDataTestPath + "test_11_1_16_ref.wav", strDataTestPath + "test_11_2_16_ref.wav" ) );
    
    w1 = Wav( strDataTestPath + "test_11_2_16_ref.wav" );
    w2 = Wav( strDataTestPath + "test_11_2_16_ref.wav" );
    assert( w1.replaceData( 50, w2.data[100:] ) );
    assert( w1.isEqual( w2 ) );
    
    wp = Wav( strDataTestPath + "test_sound_properties_soundforge.wav" );
    print( "wp:\n%s" % wp );    
    assert( wp.info["Software"] == "Sound Forge 4.5" );
    assert( wp.data[-1] == 4 );
    assert( wp.data[-2] == 5 );
    
    wp = Wav( strDataTestPath + "test_sound_properties_soundforge_stereo.wav" );
    print( "wp:\n%s" % wp );    
    assert( wp.info["Software"] == "Sound Forge 4.5" );
    assert( wp.data[-1] == 4 );
    assert( wp.data[-2] == 4 );
    assert( wp.data[-3] == 5 );    
    assert( wp.data[-4] == 5 );
    
    wp = Wav( strDataTestPath + "test_sound_properties_audacity.wav" );
    print( "wp:\n%s" % wp );
    assert( wp.info["Software"] == "Audacity (libsndfile-1.0.24)" );
    assert( wp.info["Name"] == "SuperTitre" );
    
# autoTest_Wav - end    

def autoTest_convertWavFile(strDataTestPath):
    bTestJustSpeed = False;
    if( not bTestJustSpeed ):
        convertWavFile( strDataTestPath + "test_22_mono_16.wav", strDataTestPath + "converted_test.wav", 48000, 4 );
        assert( Wav( strDataTestPath+"converted_test.wav" ) ); # test opening
        assert( 0 == filetools.compareFile( strDataTestPath+"test_48_4_16_ref.wav", strDataTestPath+"converted_test.wav", bVerbose = True ) );
        w = Wav( strDataTestPath+"test_48_4_16_ref.wav" );
        print( "w:\n%s" % w );
        assert( w.extractOneChannel(4) == [] );
        assert( w.extractOneChannel(0) != [] );
        assert( w.extractOneChannel(1) != [] );
        assert( w.extractOneChannel(2) != [] );
        assert( w.extractOneChannel(3) != [] );
        w.extractOneChannelAndSaveToFile( strDataTestPath + "converted_test.wav" );
        assert( isEqual( strDataTestPath+"test_48_1_16_ref.wav", strDataTestPath + "converted_test.wav" ) );

        w = Wav( strDataTestPath+"test_22_stereo_16.wav" );
        w.extractOneChannelAndSaveToFile( strDataTestPath + "converted_test.wav" );
        assert( isEqual( strDataTestPath+"test_22_1_16_ref.wav", strDataTestPath + "converted_test.wav" ) );

        assert( np.all( w.extractOneChannel( 0 ) == Wav( strDataTestPath + "converted_test.wav" ).data ) );
        
        convertWavFile( strDataTestPath + "test_22_mono_16.wav", strDataTestPath + "converted_test.wav", 14000, 2 );
        assert( 0 == filetools.compareFile( strDataTestPath+"test_14_2_16_ref.wav", strDataTestPath+"converted_test.wav", bVerbose = True ) );

        convertWavFile( strDataTestPath + "test_22_stereo_16.wav", strDataTestPath + "converted_test.wav", 11025, 1 );
        assert( 0 == filetools.compareFile( strDataTestPath+"test_11_1_16_ref.wav", strDataTestPath+"converted_test.wav", bVerbose = True ) );
        
        convertWavFile( strDataTestPath + "test_ttsfile.wav", strDataTestPath + "converted_test.wav", 11025, 1 );
        assert( 0 == filetools.compareFile( strDataTestPath+"test_ttsfile_11_1_16_ref.wav", strDataTestPath+"converted_test.wav", bVerbose = True ) );    
        
        w = Wav( strDataTestPath+"test_48_2_16_different_channel_contents.wav" );
        assert( w.extractOneChannel(0)[162] == 7947 );
        assert( w.extractOneChannel(1)[162] == 0 );        
        assert( np.any( w.extractOneChannel(0) != w.extractOneChannel(1) ) );
    
    timeBegin = time.time();
    convertWavFile( strDataTestPath + "test_44_mono_16_long.wav", strDataTestPath + "converted_test.wav", 11025, 1 );
    rDuration = time.time() - timeBegin;
    print( "time taken: %fs" % rDuration );    
    assert( isEqual( strDataTestPath+"test_11_1_16_long_ref.wav", strDataTestPath+"converted_test.wav" ) );
    assert( 0 == filetools.compareFile( strDataTestPath+"test_11_1_16_long_ref.wav", strDataTestPath+"converted_test.wav", bVerbose = True ) );
    assert( rDuration < 4 ); # on my PC, it takes 2.4-2.8s (the sound is 19sec long), with np: 2.8-2.9
# autoTest_convertWavFile - end
#~ autoTest_convertWavFile();

def autoTest_processWavFile(strDataTestPath):
    w = Wav( strDataTestPath+"test_split.wav" );
    splitted = w.split();
    w0 = Wav( strDataTestPath+"test_split_result_0.wav" );
    w1 = Wav( strDataTestPath+"test_split_result_1.wav" );
    assert( len(splitted) == 2 );
    assert( w0.isEqual( splitted[0] ) );
    assert( w1.isEqual( splitted[1] ) );
    return True;
# autoTest_processWavFile - end

def autoTest_loadRaw( strDataTestPath ):
    wav1 = Wav();
    bRet = wav1.load( strDataTestPath + "test_44_stereo_16.wav" );
    assert( bRet );
    wav2 = Wav();
    bRet = wav2.loadFromRaw( strDataTestPath + "test_44_stereo_16.raw" );
    assert( bRet );
    assert( wav1.isEqual( wav2 ) );
    

def correctHeader( strWavFile ):
    """
    Open a wav, and write it with a corrected header (if header was bad)
    """
    timeBegin = time.time();
    wav = Wav();
    bRet = wav.load( strWavFile, bUnpackData = True );
    #~ print( "DBG: abcdk.sound.convertWavFile: src:" + str(wavSrc) );
    if( not bRet ):
        print( "ERR: abcdk.sound.correctHeader: source file '%s' not found" % ( strWavFile ) );
        return False;
    wav.write(strWavFile);
    rDuration = time.time() - timeBegin;
    print( "INF: correctHeader: rewriting wav '%s' (in %5.2fs) [OK]" % (strWavFile, rDuration) );
# correctHeader - end

def correctHeaderInFolder( strPath ):
    """
    Open all wav in a folder, and write them with a corrected header (if header was bad)
    """
    for strFilename in sorted( os.listdir( strPath ) ):
        if( not ".wav" in strFilename ): # don't analyse this one!
            continue;
        correctHeader( strPath + os.sep + strFilename );    
# correctHeaderInFolder - end

global_nAudioOutUser = 0; # count the number of people currently using audio out
def setUsingAudioOut( bUsingIt = True ):
    """
    Inform the system that sounds are outputted from the audio speakers
    (so that you could stop analysing sound, speech, ...
    """
    global global_nAudioOutUser;
    if( bUsingIt ):
        global_nAudioOutUser += 1;
    else:
        global_nAudioOutUser -= 1;
    if( global_nAudioOutUser <= 0 or global_nAudioOutUser == 1 ):
        mem = naoqitools.myGetProxy( "ALMemory" );
        mem.raiseMicroEvent( "AudioOutUsed", global_nAudioOutUser >= 1 );
# setUsingAudio - end

def isSomeoneUsingAudioOut( ):
    """
    Is someone using the audio out (speech or sound or ...) ?
    """
    try:
        mem = naoqitools.myGetProxy( "ALMemory" );
        return mem.getData( "AudioOutUsed" ) > 0.5 or mem.getData( "ALTextToSpeech/TextStarted" ) > 0.5 ;
    except BaseException, err:
        print( "DBG: abcdk.sound.isSomeoneUsingAudioOut: err: %s" % str( err ) );
        return False; # in case of error (data not found or ...)
# isSomeoneUsingAudioOut - end

global_bUsageNoiseExtractorIsNotPresent = False; # cpu optim: if no analyseSound present at first call, then disable test
def analyseSound_pause( bWaitForResume ):
    "pause some running sound analyse"
    "bWaitForResume: True => pause until resume call, False => pause a little times (5sec?)"
    global global_bUsageNoiseExtractorIsNotPresent;
    if( global_bUsageNoiseExtractorIsNotPresent ):
        return;    
    try:
        analyser = naoqitools.myGetProxy( "UsageNoiseExtractor" );
        nTime = 5;
        if( bWaitForResume ):
            nTime = -1;
        analyser.inhibitSoundAnalyse( nTime );
    except BaseException, err:
        debug.debug( "analyseSound_pause: ERR: " + str( err ) );
        global_bUsageNoiseExtractorIsNotPresent = True;
# analyseSound_pause - end

def analyseSound_resume( bWaitForResume ):
    "resume a previously infinite paused sound analyse"
    global global_bUsageNoiseExtractorIsNotPresent;
    if( global_bUsageNoiseExtractorIsNotPresent ):
        return;
    if( bWaitForResume ):
        try:
            analyser = naoqitools.myGetProxy( "UsageNoiseExtractor" );
            analyser.inhibitSoundAnalyse( 0 );
        except BaseException, err:
            debug.debug( "analyseSound_resume: ERR: " + str( err ) );
            global_bUsageNoiseExtractorIsNotPresent = True;
# analyseSound_resume - end

def playSound( strFilename, bWait = True, bDirectPlay = False, nSoundVolume = 100 , bUseLedEars=True):
    "Play a sound, return True if ok"
    "bDirectPlay: play it Now! (could fragilise system and video drivers"
    "nSoundVolume: [0..100] will play the sound with a specific volume (ndev on some version, and if using bDirectPlay )"
    "bUseLedEars: do a a circleLedEars"
    
    print( "playSound( '%s', bWait = %s, bDirectPlay = %s, nSoundVolume = %d )" % ( strFilename, str( bWait ), str( bDirectPlay ), nSoundVolume ) );
    
    if( config.bRemoveDirectPlay ):
        print( "WRN: DISABLING_DIRECTPLAY SETTINGS for testing/temporary purpose" );
        bDirectPlay = False;
    
    try:
        if bUseLedEars:
            if( system.isOnRomeo() ):
                #leds.dcmMethod.setEyesColor();
                leds.dcmMethod.setBrainLedsIntensity( 1., 100, bDontWait = True );
            else:
                leds.dcmMethod.setEarsLedsIntensity( 1., 100, bDontWait = True );
        # If strFilename has an absolute path, go ahead with this path !
        if strFilename.startswith( pathtools.getDirectorySeparator() ):
            strSoundFile = strFilename
        else:
            strSoundFile = pathtools.getApplicationSharedPath() + "wav/0_work_free/" + strFilename;
            if( not filetools.isFileExists( strSoundFile ) ):
                # then try another path
                strSoundFile = pathtools.getApplicationSharedPath() + "wav/1_validated/" + strFilename;
            if( not filetools.isFileExists( strSoundFile ) ):
                # and another path
                strSoundFile = pathtools.getApplicationSharedPath() + "wav/0_work_copyright/" + strFilename;
            if( not filetools.isFileExists( strSoundFile ) ):
                # and another path
                strSoundFile = pathtools.getApplicationSharedPath() + "wav/" + strFilename;
            if( not filetools.isFileExists( strSoundFile ) ):
                # and another path
                strSoundFile = pathtools.getNaoqiPath() + "/share/naoqi/wav/" + strFilename;
            if( not filetools.isFileExists( strSoundFile ) ):
                # and another path
                strSoundFile = pathtools.getABCDK_Path() + "data/wav/" + strFilename;
            if( not filetools.isFileExists( strSoundFile ) ):
                print( "ERR: appu.playSound: can't find file '%s'" % strFilename );
                return False;

        setUsingAudioOut( True );
        analyseSound_pause( bWait );
        if( bDirectPlay ):
            system.mySystemCall( "aplay -q " + strSoundFile, bWait );
        else:
            global_proxyAudioPlayer = naoqitools.myGetProxy( "ALAudioPlayer" );            
            if( global_proxyAudioPlayer == None ):
                print( "ERR: sound.playSound: can't find module 'ALAudioPlayer'" );
            else:
                try:
                    # try with specific volume
                    if( bWait ):
                        global_proxyAudioPlayer.playFile( strSoundFile, nSoundVolume / 100., 0. );
                    else:
                        global_proxyAudioPlayer.post.playFile( strSoundFile, nSoundVolume / 100., 0. );
                except BaseException, err:
                    print( "DBG: sound.playSound: this version can't handle volume? (err:%s)" % str(err) );    
                    if( bWait ):
                        global_proxyAudioPlayer.playFile( strSoundFile );
                    else:
                        global_proxyAudioPlayer.post.playFile( strSoundFile );
                    
        analyseSound_resume( bWait );
        setUsingAudioOut( False );
    except BaseException, err:
        debug.debug( "playSound: ERR: " + str( err ) );
        print( "errr: " + str( err ) );
        
    if bUseLedEars:
        if( system.isOnRomeo() ):
            #~ leds.dcmMethod.setEyesColor( nColor = 0 );
            leds.setBrainLedsIntensity( 0., 100, bDontWait = True );
        else:
            leds.setEarsLedsIntensity( 0., 100, bDontWait = True );
        
    return True;
# playSound - end

def stopSound( strFilename = None, bDirectPlay = False ):
    """
    Stop a sound or every sound !
    strFilename: when at None: stop all playing sound
    """
    if( not bDirectPlay ):
        ap = naoqitools.myGetProxy( "ALAudioPlayer" );
        if( ap != None ):
            ap.stopAll(); # TODO: kill the right sound !
            analyseSound_resume( True );
            return;
    os.system( "killall aplay" );
    analyseSound_resume( True ); # TODO: kill the right sound !
# stopSound - end

def playMusic( strFilename, bWait ):
  print( "appuPlaySound: avant cnx sur audioplayer (ca lagge?)" );
  #myAP = naoqitools.myGetProxy( "ALAudioPlayer" );
  print( "appuPlaySound: apres cnx sur audioplayer (ca lagge?)" );
  ap = naoqitools.myGetProxy( "ALAudioPlayer" );
  if( bWait ):
    ap.playFile( getApplicationSharedPath() + "/mp3/" + strFilename );
  else:
    ap.post.playFile( getApplicationSharedPath() + "/mp3/" + strFilename );

  #if( not bNaoqiSound ):
  #  strSoundFile = getApplicationSharedPath() + "/mp3/" + strFilename;
  #else:
  #  strSoundFile = getNaoqiPath() + "/data/mp3/" + strFilename;
  #system.mySystemCall( getSystemMusicPlayerName() + " " +  strSoundFile, bWait );

# playMusic - end

def playSoundHearing():
  "play the standard appu sound before earing user command"
#  time.sleep( 0.4 ); # time to empty all sound buffers
  playSound( "jingle_earing.wav", bDirectPlay = True );
  time.sleep( 0.05 ); # time to empty all sound buffers ?
# playSoundHearing - end

def playSoundSpeaking():
  "play the standard appu sound before speaking to user"
  playSound( "jingle_speaking.wav", bDirectPlay = True );
# playSoundSpeaking - end

def playSoundUnderstanding():
  "play the standard appu sound to show a command is understood"
  playSound( "jingle_understanded.wav", bDirectPlay = True );
# playSoundUnderstanding - end

# sound volume (premisse of the robot's class)

def getCurrentMasterVolume():
    "get nao master sound system volume (in %)"
    "return 0 on error or problem (not on nao or ...)"
    "deprecated: you should use getMasterVolume()"
    return getMasterVolume();
# getCurrentMasterVolume - end

def volumeFadeOut( rApproxTime = 1. ):
    "Fade out master sound system"
    nVol = getCurrentMasterVolume();
    print( "volumeFadeOut: %d -----> 0" % nVol );
    nCpt = 0;
    nApproximateCall = 20;
    while( nVol > 0 and nCpt < 30 ): # when concurrent calls are made with other fade type, it could go to a dead lock. because getCurrentMasterVolume take some time, we prefere to add some counter
        ++nCpt;
        # ramping
        if( nVol > 55 ):
            nVol -= 3;
        else:
            nVol -= 9;
        (nVol);
#        print( "volout: %d" % nVol );
        setMasterVolume(nVol);
        time.sleep( float( rApproxTime ) / nApproximateCall ); # approximation of the time to make it

def volumeFadeIn( nFinalVolume, rApproxTime = 1. ):
    "Fade in master sound system"
    nVol = getCurrentMasterVolume();
    print( "volumeFadeIn: %d -----> %d" % ( nVol, nFinalVolume ) );
    nCpt = 0;
    nApproximateCall = 20;
    while( nVol < nFinalVolume and nCpt < 30 ): # when concurrent calls are made with other fade type, it could go to a dead lock. because getCurrentMasterVolume take some time, we prefere to add some counter
        ++nCpt;
        if( nVol > 55 ):
            nVol += 3;
        else:
            nVol += 9;
#        print( "volin: %d" % nVol );
        setMasterVolume(nVol);
        time.sleep( float( rApproxTime ) / nApproximateCall ); # approximation of the time to make it

def setMasterMute( bMute ):
  "mute nao sound volume"
  if( bMute ):
    strVal = "off";
  else:
    strVal = "on";
  debug.debug( "setMasterMute: %s" % strVal );
  system.mySystemCall( "amixer -q sset Master " + strVal );
  if( not bMute ):
    system.mySystemCall( "amixer -q sset PCM " + strVal );  # to be sure   
# setMasterMute - end

def isMasterMute():
  "is nao sound volume muted?"
  strOutput = system.executeAndGrabOutput( "amixer sget Master | grep 'Front Right: Playback' | cut -d[ -f4 | cut -d] -f1", True );
  strOutput = strOutput.strip();
  bMute = ( strOutput == "off" );
  debug.debug( "isMasterMute: %d (strOutput='%s')" % ( bMute, strOutput ) );
  return bMute;
# isMasterMute - end

def setMasterPanning( nPanning = 0 ):
    "change the sound master panning: 0: center -100: left +100: right"
    "current bug: currently volume is louder when at border, than at center, sorry"
    try:
        debug.debug( "setMasterPanning to %d" % nPanning );
        nVol = getCurrentMasterVolume();
        nCoefR = nVol + nVol*nPanning/100;
        nCoefL = nVol - nVol*nPanning/100;
        nCoefR = nCoefR * 32 / 100;
        nCoefL = nCoefL * 32 / 100;
        system.mySystemCall( "amixer -q sset Master %d,%d" % ( nCoefL, nCoefR ) );
        system.mySystemCall( "amixer -q sset PCM 25" );
        system.mySystemCall( "amixer -q sset \"Master Mono\" 32" );
    except BaseException, err:
        print( "setMasterPanning: error '%s'" % str( err ) );
# setMasterPanning - end

 # pause music
def pauseMusic():
  "pause the music player"
  debug.debug( "pauseMusic" );
  system.mySystemCall( "killall -STOP mpg321b" );

# restart music
def unPauseMusic():
  debug.debug( "unPauseMusic" );
  system.mySystemCall( "killall -CONT mpg321b" );

def ensureVolumeRange( nMinValue = 58, nMaxValue = 84 ):
    "analyse current volume settings, and change it to be in a specific range"
    "default range is the 'confort' range"
    nCurrentVolume = getCurrentMasterVolume();
    if( nCurrentVolume >= nMinValue and nCurrentVolume <= nMaxValue ):
        return;
    # set the volume sound nearest the min or max range
    nNewVolume = 0;
    if( nCurrentVolume < nMinValue ):
        nNewVolume = nMinValue;
    else:
        nNewVolume = nMaxValue;
    setMasterVolume( nNewVolume );
# ensureVolumeAbove - end

def removeBlankFromFile( strFilename, b16Bits = True, bStereo = False ):
  "remove blank at begin and end of a raw sound file, a blank is a 0 byte."
  "bStereo: if set, it remove only by packet of 4 bytes (usefull for raw in stereo 16 bits recording)"
  try:
    file = open( strFilename, "rb" );
  except BaseException, err:
    print( "WRN: removeBlankFromFile: ??? (err:%s)" % ( str( err ) ) );

    return False;
    
  try:
    aBuf = file.read();
  finally:
    file.close();
    
  try:  
    nNumTrimAtBegin = 0;
    nNumTrimAtEnd = 0;
    nFileSize = len( aBuf );
    for i in range( nFileSize ):
  #    print( "aBuf[%d]: %d" % (i, ord( aBuf[i] )  ) );
      if( ord( aBuf[i] ) != 0 ):
  #      print( "i1:%d" % i );
        if( bStereo and b16Bits ):
          i = (i/4)*4; # don't cut between channels
        elif( bStereo or b16Bits ):
          i = (i/2)*2;
        break;
    nNumTrimAtBegin = i;

    for i in range( nFileSize - 1, 0, -1 ):
  #    print( "aBuf[%d]: %d" % (i, ord( aBuf[i] )  ) );
      if( ord( aBuf[i] ) != 0 ):
  #      print( "i2:%d" % i );
        if( bStereo ):
          i = ((i/4)*4)+4;
        elif( bStereo or b16Bits ):
          i = ((i/2)*2)+2;
        break;
    nNumTrimAtEnd = i;

  #  debug( "sound::removeBlankFromFile: nNumTrimAtBegin: %d, nNumTrimAtEnd: %d, nFileSize: %d" % (nNumTrimAtBegin, nNumTrimAtEnd, nFileSize ) );
    if( nNumTrimAtBegin > 0 or nNumTrimAtEnd < nFileSize - 1 ):
        print( "sound::removeBlankFromFile: trim at begin: %d; pos trim at end: %d (data trimmed:%d)" % ( nNumTrimAtBegin, nNumTrimAtEnd, nNumTrimAtBegin + ( nFileSize - nNumTrimAtEnd ) ) );
        aBuf = aBuf[nNumTrimAtBegin:nNumTrimAtEnd];
        try:
            file = open( strFilename, "wb" );
        except BaseException, err:
            print( "WRN: sound::removeBlankFromFile: dest file open error (2) (err:%s)" % ( str( err ) ) );
            return False;
        try:
            file.write( aBuf );
        finally:            
            file.close();
  except BaseException, err:
    print( "sound::removeBlankFromFile: ERR: something wrong occurs (file not found or ...) err: " + str( err ) );
    return False;
  return True;
# removeBlankFromFile - end

def loadSound16( strFileIn, nNbrChannel = 1 ):
    "load a sound file and return an array of samples (16 bits) (in mono)"
    "return [] on error"
    aSamplesMono = [];    
    try:
        file = open( strFileIn, "rb" );
    except BaseException, err:
        print( "sound::loadSound16: ERR: something wrong occurs: %s" % str( err ) );
        return [];
    try:
        aBuf = file.read();  
        file.close();
        nOffset = 0;
        lenFile = len( aBuf );
        strHeaderTag = struct.unpack_from( "4s", aBuf, 0 )[0];
        if( strHeaderTag == "RIFF" ):
            print( "sound::loadSound16: skipping wav header found in %s" % strFileIn );
            nOffset += 44; # c'est en fait un wav, on saute l'entete (bourrin)
        
        print( "sound::loadSound16: reading file '%s' of size %d interpreted as %d channel(s)" % ( strFileIn, lenFile, nNbrChannel ) );
        while( nOffset < lenFile ):
            nValSample = struct.unpack_from( "h", aBuf, nOffset )[0];
            aSamplesMono.append( nValSample ); # ici c'est lourd car on alloue un par un (pas de reserve) (des essais en initialisant le tableau  avec des [0]*n, font gagner un petit peu (5.0 sec au lieu de 5.4)
            nOffset += 2;
            if( nNbrChannel > 1 ):
                nOffset += 2; # skip right channel
        # while - end
    except BaseException, err:
        print( "sound::loadSound16: ERR: something wrong occurs: %s" % str( err ) );
        pass
        
    print( "=> %d samples" %  len( aSamplesMono ) );    
    return aSamplesMono;
# loadSound16 - end

def computePeak16( strFilename ):
    """
    analyse a sound to found the peak of a 16 bits wav (quick and dirty)
    return a max as a float [0..1]
    """
    aMonoSound = loadSound16( strFilename, 1 );
    if( len( aMonoSound ) < 1 ):
        return 0.;

    nMax = 0;
    nOffset = 0;
    nNbrSample = len( aMonoSound );
    print( "computeMax16: analysing %d sample(s)" % nNbrSample );
    while( nOffset < nNbrSample ):
        nVal = aMonoSound[nOffset];
        if( nVal < 0 ):
            nVal =-nVal;
        if( nVal > nMax ):
            nMax = nVal;
        nOffset += 1;
    # while - end
    
    return nMax / float(32767);
# computePeak16 - end

def computeEnergyBest( aSample ):
	"Compute sound energy on a mono channel sample, aSample contents signed int from -32000 to 32000 (in fact any signed value)"

	# Energy(x_centered) = Energy(x) - Nsamples * (Mean(x))^2
	# Energy = Energy(x_centered)/ ( 65535.0f * sqrtf((float)nNbrSamples ) # en fait c'est mieux sans le sqrtf

	nEnergy = 0;
#	nMean = 0;
	nNumSample = len( aSample );

	for i in xrange( 1, nNumSample ):
#		nMean += aSample[i];
		nDiff = aSample[i] - aSample[i-1];
		nEnergy += nDiff*nDiff;

#	rMean = nMean / float( nNumSample );

#	print( "computeEnergyBest: nNumSample: %s, sum: %s, mean: %s, energy: %s" % ( str( nNumSample ),  str( nMean ), str( rMean ), str( nEnergy )) );
#	print( "computeEnergyBest: nNumSample: %d, sum: %d, mean: %f, energy: %d" % ( nNumSample,  nMean, rMean, nEnergy ) );
#	nEnergy -= int( rMean * rMean * nNumSample ); # on n'enleve pas la moyenne: ca n'a aucun interet (vu que c'est deja des diff)
	nEnergyFinal = int( float( nEnergy ) / (nNumSample-1) );
#	nEnergyFinal /= 32768;
	nEnergyFinal = int( math.sqrt( nEnergyFinal ) );
#	print( "computeEnergyBest: nEnergy: %f - nEnergyFinal: %s " % ( nEnergy,  str( nEnergyFinal ) ) );
	return nEnergyFinal;
# computeEnergyBest - end

def computeEnergyBestNumpy( aSample ):
    "Compute sound energy on a mono channel sample, aSample contents signed int from -32000 to 32000 (in fact any signed value)"
    if( len(aSample) < 1 ):
        return 0;
    diff = np.diff( aSample );
    diff = np.array(diff, dtype=np.int32)
    diff *= diff;
    rEnergy = np.mean(diff)
    nEnergyFinal = int( math.sqrt( rEnergy ) );
    return nEnergyFinal;
# computeEnergyBestNumpy - end

if( 0 ):
    a = [1,2,3,4,45,87,100,10,12]*3840
    a = np.array(a)
    timeBegin = time.time()
    for i in range(100):
        computeEnergyBestNumpy(a)
    print( "time: %s" % (time.time() - timeBegin ) );
    exit(0)


def convertEnergyToEyeColor_Intensity( nValue, nMax ):
    "convert energy[0,nMax] in eye color intensity"
    return ( nValue / float( nMax ) ) * 1.0 + 0.00; # add 0.2 pour la possibilité de ne pas etre tout noir
# convertEnergyToEyeColor_Intensity - end

def analyseSpeakSound( strRawFile, nSampleLenMs = 50, bStereo = False ):
    "Analyse a raw stereo or mono sound file, and found the light curve relative to sound (for further speaking)"
    print( "analyseSpeakSound: analysing '%s' (time:%d)" % ( strRawFile, int( time.time() ) ) );
    nNbrChannel = 1;
    if( bStereo ):
        nNbrChannel = 2;
    aMonoSound = loadSound16( strRawFile, nNbrChannel );
    if( len( aMonoSound ) < 1 ):
        return [];

    #analyse every 50ms sound portion (because 50ms is the average latency of leds)
    anLedsColorSequency = []; # for every time step, an int corresponding to the RGB colors
    nSizeAnalyse = int( (22050*nSampleLenMs)/1000 ); # *50 => un sample chaque 50ms
    nMax = 0;
    nOffset = 0;
    nNbrSample = len( aMonoSound );
    print( "analyseSpeakSound: analysing %d sample(s)" % nNbrSample );
    while( nOffset < nNbrSample ):
        anBuf = aMonoSound[nOffset:nOffset+nSizeAnalyse];
        nOffset += nSizeAnalyse;
        nValue = computeEnergyBest( anBuf );
        if( nValue > nMax ):
            nMax = nValue;
        # storenValue to nColor
        anLedsColorSequency.append( nValue );
    # while - end

    # convert nValue to nColor (using max energy)
    nOffset = 0;
    nNbrComputed = len( anLedsColorSequency );
    print( "analyseSpeakSound: converting %d energy to leds light (max=%d)" % ( nNbrComputed, nMax) );
    while( nOffset < nNbrComputed ):
        anLedsColorSequency[nOffset] = convertEnergyToEyeColor_Intensity( anLedsColorSequency[nOffset], nMax );
        nOffset += 1;
    # while - end

    print( "analyseSpeakSound: analysing '%s' (time:%d) - end" % ( strRawFile, int( time.time() ) ) );
    return anLedsColorSequency;
# analyseSpeakSound - end

def getMasterVolume( bForceSystemCall = False ):
    "get nao master sound system volume (in %)"
    "bForceSystemCall: set to true to use system call instead of ALAudioDevice (some version are buggy and set the PCM to only 65%)"
    
    if( not bForceSystemCall ):
        try:
            ad = naoqitools.myGetProxy( 'ALAudioDevice' );
            nVal = ad.getOutputVolume();
            debug.debug( "getMasterVolume: %d%%" % ( nVal ) );
            return nVal;
        except BaseException, err:
            print( "getMasterVolume: error '%s'" % str( err ) );
        
    print( "WRN: => using old one using fork and shell!" );
  
    strOutput = system.executeAndGrabOutput( "amixer sget Master | grep 'Front Right: Playback' | cut -d[ -f2 | cut -d% -f1", True );
    nValR = int( strOutput );
    strOutput = system.executeAndGrabOutput( "amixer sget Master | grep 'Front Left: Playback' | cut -d[ -f2 | cut -d% -f1", True );
    nValL = int( strOutput );
    nVal = ( nValR + nValL ) / 2;
    debug.debug( "getMasterVolume: %d%% (%d,%d)" % ( nVal, nValL, nValR ) );
    return nVal;
# getMasterVolume - end

def setMasterVolume( nVolPercent, bForceSystemCall = False ):
    "change the master volume (in %)"
    "bForceSystemCall: set to true to use system call instead of ALAudioDevice (some version are buggy and set the PCM to only 65%)"
    " => in fact it's my v3.2 configurated as a v3.3, see  /media/internal/DeviceHeadInternalGeode.xml"
    
    if( nVolPercent < 0 ):
        nVolPercent = 0;
    if( nVolPercent > 100 ):
        nVolPercent = 100;
    debug.debug( "setMasterVolume to %d%%" % nVolPercent );

    if( not bForceSystemCall ):
        try:
            ad = naoqitools.myGetProxy( 'ALAudioDevice' );
            ad.setOutputVolume( nVolPercent );
            return;
        except BaseException, err:
            print( "getCurrentMasterVolume: error '%s'" % str( err ) );
        
    print( "WRN: => using old one using fork and shell!" );
        
    strCommand = "amixer -q sset Master " + str( nVolPercent * 32 / 100 );
    strCommand += "; amixer  -q sset \"Master Mono\" 32";
    strCommand += "; amixer  -q sset PCM 25";    
    system.mySystemCall( strCommand );
# setMasterVolume - end



def changeMasterVolume( nRelativeChange ):
    "change current volume, by adding a value (-100,+100)"
    nLimit = 3;
    if( nRelativeChange < 0 and nRelativeChange > -nLimit ):
        nRelativeChange = -nLimit;
    if( nRelativeChange > 0 and nRelativeChange < nLimit ):
        nRelativeChange = +nLimit;
    setMasterVolume( getMasterVolume() + nRelativeChange );
# changeMasterVolume - end

def getInputVolume():
    "get the input volume (in %)(0..100)"
    strOutput = system.executeAndGrabOutput( "amixer sget Capture | grep 'Front Left: Capture' | cut -d[ -f2 | cut -d% -f1", True );
    nValR = int( strOutput );
    strOutput = system.executeAndGrabOutput( "amixer sget Capture | grep 'Front Right: Capture' | cut -d[ -f2 | cut -d% -f1", True );
    nValL = int( strOutput );
    nVal = ( nValR + nValL ) / 2;
    debug.debug( "getInputVolume: %d%% (%d,%d)" % ( nVal, nValL, nValR ) );
    return nVal;
# getInputVolume - end

def setInputVolume( nVolPercent ):
    "set the input volume (in %)(0..100)"
    if( nVolPercent < 0 ):
        nVolPercent = 0;
    if( nVolPercent > 100 ):
        nVolPercent = 100;
    debug.debug( "setInputVolume to %d%%" % nVolPercent );    
    strCommand = "amixer -q sset Capture " + str( nVolPercent ) + "%"; # seems like it's by 1/15 value (so sending less than 7% could remain to nothing
    system.mySystemCall( strCommand );# getInputVolume - end
    # change ear led color
    leds = naoqitools.myGetProxy( "ALLeds" );
    leds.setIntensity( "EarLeds", nVolPercent / 100. );
# setInputVolume - end

def changeInputVolume( nRelativeChange ):
    "change current inmput, by adding a value (-100..-7 and 7..+100)"
    nLimit = 7;
    if( nRelativeChange < 0 and nRelativeChange > -nLimit ):
        nRelativeChange = -nLimit;
    if( nRelativeChange > 0 and nRelativeChange < nLimit ):
        nRelativeChange = +nLimit;    
    setInputVolume( getInputVolume() + nRelativeChange );
# changeMasterVolume - end

def getLength( strFilename ):
    "return the length in sec"
    wav = Wav();
    if( not wav.load( strFilename, bUnpackData = False ) ):
        print( "ERR: sound.getLength: can't load wav '%s'" % strFilename );
        return 0;
    print( "INF: sound.getLength: wav loaded: %s" % str( wav ) );
    return wav.rDuration;
# getLength - end

def getNoteSound( nNumber ):
    """
    return the name of a note sound, related to a nNumber, this method "knows" how much sound are in the system, and so return a valid one (TODO)
    """
    # current number:
    nSoundNumberMin = 1;
    nSoundNumberMax = 6; # included !
    nNbr = nSoundNumberMax - nSoundNumberMin;
    
    nFinalNum = ( nNumber % (nNbr+1) ) + nSoundNumberMin;
    return "blump%d.wav" % nFinalNum;
# getNoteSound - end

def midiNoteToFreq(nNote):
    """
    @param nNote: midiNote (from 0 to 128)
    @return: corresponding freq.
    """
    if nNote in range(0, 128):
        return 440 * 2**((nNote-69.0)/12.0)
    else:
        return 0

def freqToMidiNote(freq):
    """
    @param freq: frequence in Hz
    @return: correspond clossest midi Note
    """
    if freq == 0:
        return -1
    return round(12 * np.log2(freq/440.0) + 69.0 )  # le 0.5 c'est pour passer a la note au dessus si on est plus proche d'elle
    
def repair( wavFile, bQuiet = False ):
    """
    Correct sound found incorrect (bad header or ...)
    Return True when corrected
    """
    wav = Wav( wavFile, bQuiet  = bQuiet );
    if( not wav.bHeaderCorrected ):
        return False;
    print( "INF: rewriting '%s' with correct header" % wavFile );
    wav.write( wavFile );
    return True;
# repair - end

def convertRaw2432ToWav( strRawFileName, strDstFileName = None, nDstDepth = 16, nUseSampleRate = 16000 ):
    """
    an application (a dsp devboard has dumped a wav file, it was 32 bits int from some 24bits sample), let's create a 16bits wav from that.
    """
    if( strDstFileName == None ):
        strDstFileName = strRawFileName.replace( ".raw", ".wav" );
        
    data = np.fromfile( strRawFileName, dtype=np.int32 );
    for i in range(4):
        print( "data[%d]: %s (0x%x)" % (i, data[i], data[i]) );
        
    wav = Wav();
    wav.new( nSamplingRate = nUseSampleRate, nNbrChannel = 1, nNbrBitsPerSample = nDstDepth );
    nMax = wav.getSampleMaxValue();
    for i in range( len(data) ):
        nVal = data[i];
        if( nVal > nMax ):
            nVal = nMax;
        if( nVal < -nMax ):
            nVal = -nMax;        
        wav.data.append( nVal );

    for i in range(4):
        print( "wav.data[%d]: %s (0x%x)" % (i, wav.data[i], wav.data[i]) );

    wav.updateHeaderSizeFromDataLength();
    wav.write( strDstFileName );
    
    print( "INF: convertRaw2432ToWav: '%s' => '%s' (sample nbr:%d)" % (strRawFileName, strDstFileName, len(wav.data)) );
# convertRaw2432ToWav - end

def convertRaw2432InterlacedToWav( strRawFileName, nNbrChannel = 16, strDstFileName = None, nDstDepth = 16, nUseSampleRate = 16000 ):
    """
    an application (a dsp devboard has dumped a wav file, it was 32 bits int from some 24bits sample), let's create a 16bits wav from that.
    """
    if( strDstFileName == None ):
        strDstFileName = strRawFileName.replace( ".raw", "_%02d.wav" );
        
    data = np.fromfile( strRawFileName, dtype=np.int32 );
    for i in range(4):
        print( "data[%d]: %s (0x%x)" % (i, data[i], data[i]) );
        
    nNbrSamplePerChannel = len(data)/nNbrChannel;
    for nNumChannel in range( nNbrChannel ):
        wav = Wav();
        wav.new( nSamplingRate = nUseSampleRate, nNbrChannel = 1, nNbrBitsPerSample = nDstDepth );
        nMax = wav.getSampleMaxValue();
        for i in range( nNbrSamplePerChannel ):
            #nVal = data[i*nNbrChannel+nNumChannel];
            nVal = data[nNumChannel*nNbrSamplePerChannel+i];
            if( nVal > nMax ):
                nVal = nMax;
            if( nVal < -nMax ):
                nVal = -nMax;        
            wav.data.append( nVal );

        for i in range(4):
            print( "wav.data[%d]: %s (0x%x)" % (i, wav.data[i], wav.data[i]) );

        wav.updateHeaderSizeFromDataLength();
        wav.write( strDstFileName % nNumChannel );
        
        print( "INF: convertRaw2432ToWav: '%s' => '%s' (sample nbr:%d)" % (strRawFileName, strDstFileName, len(wav.data)) );
    # for - end
# convertRaw2432InterlacedToWav - end

def normaliseFile( strFileToModify ):
    """
    Normalise a file.
    Return 1 if normalied or 0 if already full power
    """
    wav = Wav()
    wav.load( strFileToModify )
    if not wav.normalise():
        return 0
    wav.write( strFileToModify )
    return 1
# normaliseFile - end

def ensureSampleRate( strFilename, nNewSampleRate ):
    """
    resample a file if needed
    """
    wav = Wav()
    wav.load( strFilename, bLoadData = False )
    if( wav.nSamplingRate ==  nNewSampleRate ):
        return 0
    wav.load( strFilename ) # reload data
    
    wavNew = Wav();
    wavNew.new( nSamplingRate = nNewSampleRate, nNbrChannel = wav.nNbrChannel, nNbrBitsPerSample = wav.nNbrBitsPerSample );
    
    #currently handle only multiple or division
    if( nNewSampleRate > wav.nSamplingRate ):
        rMultiple = float(nNewSampleRate) / wav.nSamplingRate
        if( rMultiple != int(rMultiple) ):
            print( "ERR: ensureSampleRate: can't change sample rate if not multiple or plain divisor file: '%s' (%s !=> %s)" % (strFilename, wav.nSamplingRate, nNewSampleRate) )
            return -1
        nMultiple = int(rMultiple)
        wavNew.data = wav.data.repeat( nMultiple)
        
    else:
        assert(0)  # TODO

    wav.updateHeaderSizeFromDataLength();
    wavNew.write( strFilename );
# ensureSampleRate - end
#~ ensureSampleRate( "/tmp2/nimoy_spock_test2.wav", 48000 )
#~ exit(0)

def convertToOneChannel( strFileIn, strFileOut, nIdxChannelToTake = 0 ):
    """
    convert a multichannel file to a mono file one
    """
    wav = Wav()
    if not wav.load( strFileIn ):
        print( "ERR: can't open '%s'" % strFileIn )
        return -1
    if not wav.extractOneChannelAndSaveToFile( strFileOut, nNumChannel = nIdxChannelToTake ):
        print( "ERR: can't write to '%s'" % strFileOut )
        return -2
    return 1
# convertToOneChannel - end
    


def autoTest():
    strDataTestPath = "c:/work/dev/git/appu_data/sounds/test/autotest/";
    if( test.isAutoTest() or True ):
        test.activateAutoTestOption();        
        if( not system.isOnNao() ):
            analyseSpeakSound( strDataTestPath + "TestSoundEnergy_16bit_mono.raw" );
        else:
            playSoundHearing();
            playSound( "warning.wav", bDirectPlay = True );
            playSound( "hello.wav" );
            playSound( "ho1.wav" );        
        autoTest_Wav(strDataTestPath);
        autoTest_loadRaw(strDataTestPath);
        autoTest_convertWavFile(strDataTestPath);
        autoTest_processWavFile(strDataTestPath);
# autoTest - end
    

if( __name__ == "__main__" ):
    #~ for ch in "RIFF":
        #~ print( "0x%x" % ord(ch) );
    #~ for ch in "data":
        #~ print( "0x%x" % ord(ch) );

    #import doctest
    #doctest.testmod()
    #~ autoTest();
    #testGenerateSin()
    #extractEachChannelFromFolder( "C:\\nao_images\\" );
    #repair( "C:\\perso\\projecubefromhouse\\2014-06-12_-_md_plus_belle\\181.wav" );
    # dsp tools
    #~ convertRaw2432InterlacedToWav( "c:\\tempo2\\interlaced16.raw", nUseSampleRate = 12000 );
    #~ for i in range(16):
        #~ convertRaw2432ToWav("c:\\tempo2\\chan%d.raw" % i);
    correctHeaderInFolder( "f:/recordedSound/" )
