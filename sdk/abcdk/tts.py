# -*- coding: utf-8 -*-
###########################################################
# Aldebaran Behavior Complementary Development Kit
# TTS tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

import filetools
import sound

import math
import numpy as np

#~ def __init__( self ):
    #~ print "init du module";
    #~ self.bTest = True;


class TTS:
    
    def __init__( self, strSamplePath ):
        self.strSamplePath = strSamplePath;
        self.mapLoaded = dict(); # a dict word => wav sample or None if this sample doesn't exists
        
    def wordToFilename( self, strTxt ):
        """
        find the filename related to a word or a small sentence
        """
        strTxt = strTxt.replace( ' ', '_' );
        strTxt = strTxt.lower();
        return strTxt;
        
    
    def sayToFile( self, strTxtToSay, strFilename ):
        """
        Generate a sentence and output the results in strFilename.
        - strTxtToSay: a sentence or a group of sentences to say
        - strFilename: path and destination filename
        """
        wavOut = sound.Wav();
        wavOut.new( nSamplingRate = 44100, nNbrChannel = 1, nNbrBitsPerSample = 16 );
        aSentences = strTxtToSay.split( "!?." );
        rTimeBetweenWords = 0.01;
        for sentence in aSentences:
            print( "sentence: '%s'" % sentence );
            # find the biggest word part
            part = sentence;
            # find a part
            while( len(part)>0 ):
                try:
                    sample = self.mapLoaded[part];
                except BaseException, err:
                    # this part hasn't been loaded/tested
                    name = self.strSamplePath + self.wordToFilename( part ) + ".wav";
                    if( filetools.isFileExists( name ) ):
                        self.mapLoaded[part] = sound.Wav( name );
                        if( len(self.mapLoaded[part].data) < 1 ):
                            self.mapLoaded[part] = None;
                        else:
                            self.mapLoaded[part].trim( 1 );
                            
                    else:
                        self.mapLoaded[part] = None;
                    sample = self.mapLoaded[part];
                if( sample == None ):
                    # no sample for that part, trying with a smaller one
                    part = part[:-1];
                    if( len(part) == 0 ):
                        # can't find this, reducing the word
                        print( "WRN: abcdk.tts: can't say the word '%s': missing sample, skipping the first letter..." % sentence );                        
                        sentence = sentence[1:];
                        part = sentence;
                else:
                    # we've found one
                    
                    #generating
                    rLenCrossFade = 0.025;
                    nNbrSampleCrossFade = int(rLenCrossFade*wavOut.nSamplingRate);
                    if( wavOut.rDuration < rLenCrossFade ):
                        print( "INF: => adding sample '%s' (%5.3fs) at position: %ss" % (part, sample.rDuration, wavOut.rDuration ) );
                        wavOut.addData( sample.data );
                    else:
                        print( "INF: => inserting sample '%s' (%5.3fs) at position: %ss" % (part, sample.rDuration, wavOut.rDuration ) );                        
                        nInsertionPoint = wavOut.nNbrSample-nNbrSampleCrossFade;
                        wavOut.addSilence( sample.rDuration-rLenCrossFade+0.01 );
                        wavOut.replaceData( nInsertionPoint, sample.data, nOperation = 1 );                    
                    # go to next
                    sentence = sentence[len(part):];
                    if( sentence[0] == ' ' ):
                        sentence = sentence[1:];
                        wavOut.addSilence( rTimeBetweenWords );
                    part = sentence;
                    
        wavOut.write( strFilename );
    # sayToFile - end
    
    def getStatus(self):
        """
        Return a state of the tts object
        """
        strOut = "tts object:\n";
        nNbrTotal = len(self.mapLoaded);
        nNbrLoaded = 0;
        for k,v in self.mapLoaded.iteritems():
            if( v != None ):
                nNbrLoaded += 1;
                strOut += "'%s': duration: %5.2fs\n" % (k,v.rDuration);
                if( False ): # output all info for sample
                    strOut += str(v) + "\n";
        strOut += "sample tested: %d\n" % nNbrTotal;
        strOut += "really loaded: %d\n" % nNbrLoaded;
        return strOut;
    # getStatus - end
    
# class Tts - end

tts = TTS("c:/work/worksound/tts/alexandre/" );

def autoTest_tts():
    tts.sayToFile( "Bonjour tout le monde!", "c:/tempo/tts_generated.wav" );
    print tts.getStatus();
    
class OneGenerator:
    """
    a simple nammed tuple
    """
    def __init__( self ):
        self.rFrequency = 0.;
        self.rAmp = 0.;
        self.nOffset = 0; # last generator end offset
        self.bUsed = False;
        
    def __str__( self ):
        strOut = "";
        strOut += "rFrequency: %5.1fHz, " % self.rFrequency;
        strOut += "rAmp: %5.1f, " % self.rAmp;
        strOut += "nOffset: %s, " % self.nOffset;
        strOut += "bUsed: %s;" % self.bUsed;
        return strOut;
# class OneGenerator - end

class SinusGenerator:
    """
    An object to generate a family of sinus, keeping track of previouses one, so there's no glitch.
    The nearest frequency is reused
    """
    def __init__( self, nNbrGenerator ):
        self.aCurrentGenerator = [OneGenerator() for i in range(nNbrGenerator)];
        
    def startFrame( self ):
        """
        Inform we've finished with previous frame, and so we could begin to reuse previous band
        """
        for gen in self.aCurrentGenerator:
            gen.bUsed = False;
        print( "INF: SinusGenerator.startFrame: at the end:\n%s" % ('\n'.join(map(str, self.aCurrentGenerator)) ) );
            
    def generate( self, nNbrSamples = 8192, rFreq = 440.,  rAmplitude = 1., nSamplingRate = 48000 ):
        """
        Generate some sound data.
        -rAmplitude: the max amplitude you want to achieve (0..+inf).
        """
        print( "INF: SinusGenerator.generate(rFreq: %5.1f, amp: %5.1f)" % (rFreq,rAmplitude) );
        
        # look for a free generator
        rDistMin = 10000;
        iMin = -1;
        for i in range(len(self.aCurrentGenerator)):
            if( not self.aCurrentGenerator[i].bUsed ):
                rDist = abs(self.aCurrentGenerator[i].rFrequency - rFreq);
                if( rDist < rDistMin ):
                    rDistMin = rDist;
                    iMin = i;
        #~ print( "generate: iMin: a la fin: %s" % iMin );
        assert( iMin != -1 ); # raise if not enough nNbrGenerator !
        
        # we should generate a new sinus, using amp iMin.rAmp to rAmplitude and reusing offset
        
        nNbrSamples = int(nNbrSamples);
        t = np.arange(nNbrSamples);
        data = np.sin((t * 2 * math.pi*rFreq/nSamplingRate)+self.aCurrentGenerator[iMin].nOffset)
        aAmplitude = np.linspace( self.aCurrentGenerator[iMin].rAmp, rAmplitude, nNbrSamples );
        #~ print( "amplitude first, last: %s, %s" % (aAmplitude[0], aAmplitude[-1]) );
        #~ print( "max amp: %s" % max( data ) );
        #~ print( "min amp: %s" % min( data ) );
        data *= aAmplitude;
        #~ print( "max amp with amp: %s" % max( data ) );
        #~ print( "min amp with amp: %s" % min( data ) );
        
        # update this generator
        self.aCurrentGenerator[iMin].rFrequency = rFreq;
        self.aCurrentGenerator[iMin].rAmp = rAmplitude;
        self.aCurrentGenerator[iMin].nOffset = (nNbrSamples * 2 * math.pi*rFreq/nSamplingRate)+self.aCurrentGenerator[iMin].nOffset
        self.aCurrentGenerator[iMin].bUsed = True;
        
        return data;
    # generate - end
        
# class SinusGenerator - end
    
def generateSinusoid( nNbrSamples = 8192, rFreq = 440.,  rAmplitude = 1., nSamplingRate = 48000, nOffset = 0 ):
    """ 
    generate some simple sinus data
    return an array containting the sinusoid 
    """
    nNbrSamples = int(nNbrSamples);
    t = np.arange(nNbrSamples);
    res = np.sin((t+nOffset) * 2 * math.pi*rFreq/nSamplingRate)
    return res*rAmplitude;
# generateSinusoid - end

def analyseSample( strFile ):
    w = sound.Wav( strFile );
    assert( w.nNbrChannel == 1 );
    nWindowSize=1024*8;
    #~ nWindowSize=256; # reducing drastically it give some interesting results
    nOffset = 0;
    nLengthAdvancing = 8192 / 4; # if smaller than nWindowSize => overlap
    #~ nLengthAdvancing = 256;
    if( nLengthAdvancing > nWindowSize ):
        nLengthAdvancing = nWindowSize;
    rMaxAmp = 30e6;
    print( "rMaxAmp: %s" % rMaxAmp );

    print( "nWindowSize: %s => %5.3fs" % (nWindowSize, nWindowSize/float(w.nSamplingRate)) );
    print( "nLengthAdvancing: %s => %5.3fs" % (nLengthAdvancing, nLengthAdvancing/float(w.nSamplingRate)) );

    wavOut = sound.Wav();
    wavOut.new( nSamplingRate = 44100, nNbrChannel = 1, nNbrBitsPerSample = 16 );

    nNbrFreqToKeep = 2; # 12
    
    sg = SinusGenerator( nNbrFreqToKeep );
    
    print( "nbr float to store: %d" % (len(w.data)*2*nNbrFreqToKeep/nLengthAdvancing) );    
    
    while( nOffset < len(w.data) ):
        print( "offset: %d" % nOffset );        
        aFFT = np.fft.fft( w.data[nOffset:], nWindowSize );
        # we only first half
        aFFT = aFFT[:nWindowSize/2];
        aFreqs = np.fft.fftfreq( nWindowSize,  1. / w.nSamplingRate );
        #print( "len fft: %s" % len(aFFT) ); # the same than the sample size!
        #print( "max : nIdxMax: %s, nFreqMax: %sHz, rValMax: %5.3f" % (nIdxMax,nFreqMax,rValMax) );
        data=np.zeros( nLengthAdvancing, dtype=w.dataType );
        # find the nth more present frequency:
        sg.startFrame();
        for i in xrange( nNbrFreqToKeep ):
            nIdxMax = np.argmax( aFFT );    
            nFreqMax = aFreqs[nIdxMax];
            #~ nFreqMax = 220;
            rValMax = aFFT[nIdxMax].real;
            #~ print( "%d: max : nIdxMax: %s, nFreqMax: %sHz, rValMax: %5.3f" % (i, nIdxMax,nFreqMax,rValMax) );            
            aFFT[nIdxMax] = 0;
            
            if( rValMax < rMaxAmp / 1000 ):
                break;
            
            if( rMaxAmp < rValMax ):
                raise Exception( "trop grosse valeur: %s <= %s" % (rMaxAmp,rValMax) );
            assert( rMaxAmp > rValMax );
            if( nFreqMax < 2000 or 0 ):
                newdata = sg.generate( nLengthAdvancing, nFreqMax, wavOut.getSampleMaxValue()*rValMax/(rMaxAmp*nNbrFreqToKeep), w.nSamplingRate );
                data+= newdata;                            
            else:
                print( "TOO HIGH: %s" % nFreqMax );
        nOffset += nLengthAdvancing;        
        
        wavOut.addData( data );
        
    # while - end
    wavOut.normalise();
    wavOut.write( "c:/tempo/analysedandgenerated.wav" );
    
# analyseSample - end
  


def autoTest():
    #~ autoTest_tts();
    #analyseSample( "c:/work/worksound/tts/alexandre/bonjour.wav" );
    analyseSample( "C:/work/Dev/git/appu_data/sounds/test/la440_1sec_faded.wav" );

if __name__ == "__main__":    
    autoTest();