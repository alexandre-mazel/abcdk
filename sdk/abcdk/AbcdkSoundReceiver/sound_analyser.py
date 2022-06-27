import numpy as np
import time
import logging
import datetime
import os
import shutil
import math

from vad import VAD
from stk import runner

from abcdk.sound import wav
from abcdk.sound import freespeech
from abcdk import python_speech_features
from abcdk.files import moveFiles

class SoundAnalyser:  
    def __init__( self, qiapp, 
                        nSampleRate = 16000, 
                        datatype=np.int16, 
                        nNbrChannel = 4, 
                        nEnergyThreshold = 300, 
                        bActivateSpeechRecognition = True, 
                        strUseLang = "", 
                        bKeepAudioFiles = False,
                        rTimePreVAD = 0.150,
                        rTimePostVAD = 0.500):
        """
        analyse chunk of data (must have no specific to robot nor naoqi method)
        - nSampleRate: the sample rate of your sound
        - datatype: the way your sound is stored
        - nNbrChannel: ...
        - nEnergyThreshold: threshold for the sound to be analysed for sound reco
        - rVadThreshold: threshold for confidence of the VAD: Currently not used
        - bActivateSpeechRecognition: do we send the interesting sound to the speech recognition ?
        - bActivateSoundRecognition: 
        - strUseLang: lang to use for speech recognition, eg: "fr-FR", if leaved to "": use language currently in the tts
        """

        self.nSampleRate = nSampleRate
        self.datatype = datatype
        self.nNbrChannel = nNbrChannel
        self.bActivateSpeechRecognition = bActivateSpeechRecognition
        self.rEnergyThreshold = nEnergyThreshold; # 60 # 10
        self.strUseLang = strUseLang

        self.rTimePreVAD = rTimePreVAD
        self.rTimePostVAD = rTimePostVAD
        
        self.rMfccWindowStepInSec = 0.01
        
        self.nSizePreBuffer = int(self.rTimePreVAD*nSampleRate) # conversion from time to samples
        
        

        self.bStoringSpeech = False; # are we currently storing for speech reco ?
        self.bStoringNoise = False; # are we currently storing for sound reco ?
        
            
        # all sounds buffer will be stored in monochannel
        self.aStoredDataSpeech = np.array( [], dtype=self.datatype ) # a numpy int16 array storing current sound
        self.aStoredDataNoise = np.array( [], dtype=self.datatype )
        self.aStoredMfccSound = np.array( [], dtype=np.float64 )
        
        self.aStoredSoundPreBuffer = np.array( [], dtype=self.datatype )
        
        self.timeLastBufferReceived = time.time()

        self.timeLastPeak = time.time() - 1000
        self.timeLastVAD = self.timeLastPeak
        
        self.strLastRecognized = "";
        self.strDstPath = "/tmp/"
        self.simulatedTime = time.time() # never use real computer time, but simulated one, so we could make automatic test faster
        self.debug_fileAllSpeech = None
        self.bIsOnRobot = runner.is_on_robot()

        self.vad = VAD(self.rTimePreVAD, self.rTimePostVAD )
        self.fs = freespeech.FreeSpeech(qiapp)
        self.strPathToKeepAudioFiles = "prevWavs/" # 18-01-25 Alma: questionnable location
        self.setKeepAudioFiles( bKeepAudioFiles ) 

        if self.bKeepAudioFiles == True:
            self.mover = moveFiles.MoveFiles(strPath = self.strPathToKeepAudioFiles,
                                             strDstHost = "robotdata@protolab.aldebaran.com",
                                             rBandwithMax = 10.0)
            self.mover.start()
        
    def __del__( self ):
        self.stop()
        if self.debug_fileAllSpeech != None:
            self.debug_fileAllSpeech.write( self.strDstPath + "concatenated_speechs.wav" )

    def stop(self):
        if self.bKeepAudioFiles == True:
            self.mover.stop()

    def setKeepAudioFiles( self, bNewState ):
        self.bKeepAudioFiles = bNewState
        if self.bKeepAudioFiles:
            try:
                os.makedirs( self.strPathToKeepAudioFiles )
            except BaseException, err:
                pass # quiet!  
        
    def _writeBufferToFile( self, datas, strFilename ):
        wavFile = wav.Wav()
        wavFile.new( nSamplingRate = self.nSampleRate, nNbrChannel = 1, nNbrBitsPerSample = 16 )
        wavFile.addData( datas )
        bRetWrite = wavFile.write( strFilename )
        
        if not self.bIsOnRobot:
            if self.debug_fileAllSpeech == None:
                self.debug_fileAllSpeech = wav.Wav()
                self.debug_fileAllSpeech.new( nSamplingRate = self.nSampleRate, nNbrChannel = 1, nNbrBitsPerSample = 16 )
            self.debug_fileAllSpeech.addData( datas )
            self.debug_fileAllSpeech.addData( np.zeros( self.nSampleRate/2, self.datatype) )

        return bRetWrite
            
        
    def _sendToSpeechReco( self, strFilename ):
        """
        Send a file to the speech recognition engine.
        Return: the string of recognized text, + confidence or None if nothing recognized
        """
        
        logging.info("_sendToSpeechReco: sending to speech reco '%s'" % strFilename )
        retVal = None
        
        timeBegin = time.time()
        
        retVal = self.fs.analyse( strFilename, strUseLang=self.strUseLang )
                
        rProcessDuration = time.time() - timeBegin
        
        logging.debug( "SoundAnalyser._sendToSpeechReco: freeSpeech analysis processing takes: %5.2fs" % rProcessDuration )
        
        if( 0 ): # disabled
            self.rSkipBufferTime = rProcessDuration  # if we're here, it's already to zero
        
        if retVal != None:
            retVal = [ retVal[0][0], retVal[0][1] ]
            txtForRenameFile = retVal[0]
        else:
            txtForRenameFile = "Not_Recognized"
            
        if self.bKeepAudioFiles:
            newfilename = strFilename.replace( ".wav", "__%s.wav" % self.convertForFilename(txtForRenameFile) )
            baseFilename = os.path.basename(strFilename)
            newBaseFilename = os.path.basename(newfilename)
            newfilename = self.strPathToKeepAudioFiles + newBaseFilename
            shutil.move(  strFilename, newfilename )
            logging.info( "Saved wav file in: " + newfilename)
        
        return retVal

    def convertForFilename(self, strTxt ):
        """
        convert a text to be usable as filename
        "toto is happy" => "toto_is_happy"
        """
        s = strTxt
        s = s.replace( " ", "_" )
        s = s.replace( "'", "_" )
        s = s.replace( "\"", "_" )
        s = s.replace( ",", "_" )
        s = s.replace( ":", "_" )
        s = s.replace( "/", "_" )
        s = s.replace( "\\", "_" )
        s = s.replace( "-", "_" )
        return s
    # convertForFilename - end

    def _sendFileToRemoteSoundRecognition( self, strFilename ):
        """
        ugly send to the sound recognition in background from a remote computer (just for ears project)
        """        
        #~ os.system( "scp -q %s nao@%s:%s" % (strFilename, self.strNaoIP, strFilename) ) # assume folder exists at destination
        #~ if( self.mem == None ):
            #~ import naoqi
            #~ self.mem = naoqi.ALProxy( "ALMemory", self.strNaoIP, 9559 )
        #~ if( self.mem != None ):
            #~ self.mem.raiseMicroEvent( "SoundRecoAnalyseFilename", strFilename )
        pass
        
    def _sendFileToSoundRecognition( self, buffer ):
        pass
        
    def asrFile( self, strFilename ):
        """
        analyse a file, return all voice segment
        """
        s = wav.Wav( strFilename )

        if not s.isOpen():
            raise OSError("File not found: " + strFilename)

        timeBegin = time.time()
        aMixedSoundData = s.data
        if s.nNbrChannel > 1:
            aMixedSoundData = aMixedSoundData[0::s.nNbrChannel]+aMixedSoundData[1::s.nNbrChannel] 

        self.nSampleRate = s.nSamplingRate

        nNbrOfSamplesByChannel = len(s.data) / s.nNbrChannel        
        rSoundDataDuration = nNbrOfSamplesByChannel / float(self.nSampleRate)

        return self.analyseBuffer(aMixedSoundData,rSoundDataDuration)
                
    def asrBuffer(self, aInterlacedSoundData, bVerbose = False ):
        """
        This is THE method that receives all the sound buffers from the "ALAudioDevice" module or the sound card or a file
        - aSoundData: it's an interlaced chunks of wav of a various length
        Return [bNoiseDetected, bSpeechDetected, aRecognizedNoise, aRecognizedSpeech, aRecognizedUser]
            - aRecognizedXxx: a pair [strText, rConfidence, rDuration]
                - strText: the recognized text, or name of the recognized sound
                - rConfidence: [0..1]
                - rDuration: duration of the recognized sound                 
                or [] if nothing recognized
                or None if nothing analized
            - aRecognizedUser: to be defined later
            
        """
        self.bVerbose = bVerbose
        
        nNbrOfSamplesByChannel = len(aInterlacedSoundData) / self.nNbrChannel        
        rSoundDataDuration = nNbrOfSamplesByChannel / float(self.nSampleRate)
        
        logging.debug( "Receiving a buffer of len: %s (equivalent to %5.3fs) (shape:%s)" % (len(aInterlacedSoundData), rSoundDataDuration, str(aInterlacedSoundData.shape)) )
        
        if time.time() > self.timeLastBufferReceived + 0.7:
            # our buffer is now to old (for instance the robot was speaking and we were inhibited)
            logging.info( "Clearing buffer after gap of %5.2fs (after inhibition...)" % (time.time()-self.timeLastBufferReceived) )
            self.bStoringSpeech = False
            self.aStoredDataSpeech = np.array( [], dtype=self.datatype ) # reset
            
        self.timeLastBufferReceived = time.time()
        
        aSoundData = np.reshape( aInterlacedSoundData, (self.nNbrChannel, nNbrOfSamplesByChannel), 'F' );
        
        # sum of two mics
        aMixedSoundData = aSoundData[0]+aSoundData[1]
        logging.debug( "aMixedSoundData len: %s, shape: %s" % (len(aMixedSoundData), str(aMixedSoundData.shape)) )

        return self.analyseBuffer(aMixedSoundData,rSoundDataDuration)


    def analyseBuffer(self,aMixedSoundData,rSoundDataDuration):
        aRecognizedNoise = None
        aRecognizedSpeech = None
        aRecognizedUser = None

        computedMfcc = python_speech_features.base.mfcc( aMixedSoundData, samplerate=self.nSampleRate, winstep=self.rMfccWindowStepInSec )
        
        aVadStateChange = self.vad.computeFromMfcc( computedMfcc, self.rMfccWindowStepInSec )
        logging.debug( "aVadStateChange: %s" % aVadStateChange )
        
        # analyse VAD analyse results
        bStoringSpeechDone = False
        for i in range(len(aVadStateChange)):            
            b, t = aVadStateChange[i]
            if b: 
                if t < 0.:
                    # take datas from preBuffer
                    nNbrSamples = int(-t*self.nSampleRate)
                    self.aStoredDataSpeech = self.aStoredSoundPreBuffer[-nNbrSamples:]
                    logging.debug( "pre: %s" % len( self.aStoredDataSpeech ) )
                    logging.debug( "pre: %s" % str(self.aStoredDataSpeech.shape ) )
                    
                    t = 0.

                # add data to next changes:
                if i+1 < len(aVadStateChange):
                    rDuration = aVadStateChange[i+1][1]-t
                else:
                    rDuration = rSoundDataDuration-t
                nStart = int(t*self.nSampleRate)
                nDuration = int(rDuration*self.nSampleRate)
                logging.debug( "%s" % len( self.aStoredDataSpeech ) )
                logging.debug( "%s" % len( aMixedSoundData ) )
                logging.debug( "%s" % str(self.aStoredDataSpeech.shape) )
                logging.debug( "%s" % str(aMixedSoundData.shape) )
                
                self.aStoredDataSpeech = np.concatenate( (self.aStoredDataSpeech, aMixedSoundData[nStart:nStart+nDuration]) );
                
                self.bStoringSpeech = True
                bStoringSpeechDone = True
            else:
                self.bStoringSpeech = False
                strFilename = self.strDstPath + datetime.datetime.now().strftime("%Y_%m_%d-%Hh%Mm%Ss%fms") + "_speech.wav";
                logging.debug( "Outputting speech to file: '%s'" % strFilename );

                rDuration = len(self.aStoredDataSpeech) / float(self.nSampleRate)
                bRetWrite = self._writeBufferToFile( self.aStoredDataSpeech, strFilename  )
                logging.debug("write buffer to file done")
                self.aStoredDataSpeech = np.array( [], dtype=self.datatype ) # reset
                
                if self.bActivateSpeechRecognition and bRetWrite: 
                    ret = self._sendToSpeechReco( strFilename )
                    if ret != None:
                        aRecognizedSpeech = [ret[0], ret[1], rDuration]
                    else:
                        aRecognizedSpeech = []
                        
                if not self.bKeepAudioFiles:
                    try:
                        os.unlink( strFilename )
                    except: pass
                
        
        if self.bStoringSpeech and not bStoringSpeechDone:
            self.aStoredDataSpeech = np.concatenate( (self.aStoredDataSpeech, aMixedSoundData) );
            
            
        if self.bStoringSpeech:
            if len(self.aStoredDataSpeech) > self.nSampleRate*14:
                # if more than 14 sec, keep only 10 last sec
                logging.warning( "SoundAnalyser.analyse: buffer too long, keeping only 10 last seconds..." )
                self.aStoredDataSpeech = self.aStoredDataSpeech[self.nSampleRate*4:] # removing by chunk of 4 sec
                
        
        # prebuffer store and offseting
        self.aStoredSoundPreBuffer = np.concatenate( (self.aStoredSoundPreBuffer, aMixedSoundData) );
        self.aStoredSoundPreBuffer = self.aStoredSoundPreBuffer[-self.nSizePreBuffer:]
        
        
        self.simulatedTime += rSoundDataDuration
        return [self.bStoringNoise, self.bStoringSpeech, aRecognizedNoise, aRecognizedSpeech,aRecognizedUser]
    # Analyse - end

    def computeEnergyBestNumpy(self, aSample ):
        """
        Compute sound energy on a mono channel sample, aSample contents signed int from -32000 to 32000 (in fact any signed value)
        """
        if( len(aSample) < 1 ):
            return 0
        diff = np.diff( aSample )
        diff = np.array(diff, dtype=np.int32)
        diff *= diff
        rEnergy = np.mean(diff)
        nEnergyFinal = int( math.sqrt( rEnergy ) )
        return nEnergyFinal
    # computeEnergyBestNumpy - end
        
    
