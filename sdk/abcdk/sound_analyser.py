# -*- coding: utf-8 -*-
###########################################################
# Aldebaran Behavior Complementary Development Kit
# Sound Analyser
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

import logging
"Sound Analyser: receive sound buffer, and handle them"
logging.debug( "importing abcdk.sound_analyser" );

import config
import filetools
import leds
import naoqitools
import sound
import stringtools
import system

import naoqi

import numpy as np
import os
import sys
import time
from abcdk import log_formatter
import shutil

import python_speech_features

global_strALMemoryKeyName__stop_process = "sound_receiver_must_stop"
global_bSampleReceived = False

class VAD:
    """
    receive mfcc ad compute a vad (keep current state from previous buffer)
    """
    def __init__(self, rPreTime = 0.150, rPostTime = 0.40 ):
        self.rPreTime = rPreTime
        self.rPostTime = rPostTime
        self.bPrevFrameHasPotentialVoice = False
        self.bCurrentStatus = False
        self.nCptNoVoiceSinceDetected = 1000
        
    def computeFromMfcc( self, computedMfcc, rWindowStepInSec ):
        """
        Detect Voice Activity from buffer slices
        return an array of state change in second, relative to the origin of the first window
        [sc1, sc2, sc3, ...]
        with sc: [True, -0.15]: voice start 150ms from now or [False, 0.3]: voice stop in 0.3 sec...
        """
        aSc = []
        rCurrentTime = 0.
        nNbrWindowRelativeToPostTime = int(self.rPostTime / rWindowStepInSec)
        
        for band_results in computedMfcc:
            res = 0
            # band index should be relative to the samplerate
            nLimit = 10 # 10: ok pour voix, si on veut enlever tout les claquements de doigs et ... il faut 13 voire 16
            # todo: have a prePotentialVoice tunable with more than just the previous (for hands_noise)
            bPotentialVoice = band_results[1] > nLimit  or band_results[2] > nLimit or band_results[3] > nLimit+6 # or band_results[2] < -30
            if bPotentialVoice and self.bPrevFrameHasPotentialVoice:
                res = 1
                self.nCptNoVoiceSinceDetected = 0
            else:
                self.nCptNoVoiceSinceDetected += 1
                if self.nCptNoVoiceSinceDetected < nNbrWindowRelativeToPostTime:
                    res = 1
            self.bPrevFrameHasPotentialVoice = bPotentialVoice
            
            if res != self.bCurrentStatus:
                self.bCurrentStatus = res
                scTime = rCurrentTime
                if res == 1:
                    scTime -= self.rPreTime # add pretime
                aSc.append( [res, scTime] )
            
            rCurrentTime += rWindowStepInSec

        return aSc
    
# class VAD - end
        


class SoundAnalyzer:  
    def __init__( self, nSampleRate = 16000, datatype=np.int16, nNbrChannel = 4, nEnergyThreshold = 300, bActivateSpeechRecognition = True , bActivateSoundRecognition = False, strUseLang = "" ):
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
        self.bActivateSoundRecognition = bActivateSoundRecognition
        self.rEnergyThreshold = nEnergyThreshold; # 60 # 10
        self.strUseLang = strUseLang

        self.rTimePrePeak = 0.150 # time to keep before a peak is detected
        self.rTimePostPeak = 0.400 # time to keep after a peak is detected

        self.rTimePreVAD = 0.150 # for VAD/ASR
        self.rTimePostVAD = 0.500
        
        self.rMfccWindowStepInSec = 0.01
        
        self.rTimePreBuffer = max(self.rTimePreVAD, self.rTimePrePeak) # time to buffer for have start of sound (in sec)
        self.nSizePreBuffer = int(self.rTimePreBuffer*nSampleRate) # in nbrSamples
        
        

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
        
        self.vad = VAD(self.rTimePreVAD, self.rTimePostVAD )
        
        self.strLastRecognized = "";
        
        self.strDstPath = "/tmp/"
        
        self.simulatedTime = time.time() # never use real computer time, but simulated one, so we could make automatic test faster
        
        self.debug_fileAllSpeech = None
        
        self.bKeepAudioFiles = True
        
        self.bIsOnRobot = system.isOnRobot()
        
    def __del__( self ):
        if self.debug_fileAllSpeech != None:
            self.debug_fileAllSpeech.write( self.strDstPath + "concatenated_speechs.wav" )

    def setKeepAudioFiles( self, bNewState ):
        self.bKeepAudioFiles = bNewState
        
    def _writeBufferToFile( self, datas, strFilename ):
        wavFile = sound.Wav()
        wavFile.new( nSamplingRate = self.nSampleRate, nNbrChannel = 1, nNbrBitsPerSample = 16 )
        wavFile.addData( datas )
        wavFile.write( strFilename )
        
        if not self.bIsOnRobot:
            if self.debug_fileAllSpeech == None:
                self.debug_fileAllSpeech = sound.Wav()
                self.debug_fileAllSpeech.new( nSamplingRate = self.nSampleRate, nNbrChannel = 1, nNbrBitsPerSample = 16 )
            self.debug_fileAllSpeech.addData( datas )
            self.debug_fileAllSpeech.addData( np.zeros( self.nSampleRate/2, self.datatype) )
            
        
    def _sendToSpeechReco( self, strFilename ):
        """
        Send a file to the speech recognition engine.
        Return: the string of recognized text, + confidence or None if nothing recognized
        """
        import freespeech
        
        logging.info("_sendToSpeechReco: sending to speech reco '%s'" % strFilename )
        retVal = None
        
        timeBegin = time.time()
        
        retVal = freespeech.freeSpeech.analyse( strFilename, strUseLang=self.strUseLang )
                
        rProcessDuration = time.time() - timeBegin
        
        if self.bVerbose: logging.info( "SoundAnalyser._sendToSpeechReco: freeSpeech analysis processing takes: %5.2fs" % rProcessDuration )
        
        if( 0 ): # disabled
            self.rSkipBufferTime = rProcessDuration  # if we're here, it's already to zero
        
        if retVal != None:
            retVal = [ retVal[0][0], retVal[0][1] ]
            txtForRenameFile = retVal[0]
        else:
            txtForRenameFile = "Not_Recognized"
            
        if self.bKeepAudioFiles:
            newfilename = strFilename.replace( ".wav", "__%s.wav" % stringtools.convertForFilename(txtForRenameFile) )
            baseFilename = os.path.basename(strFilename)
            newBaseFilename = os.path.basename(newfilename)
            newfilename = "/home/nao/Hopias/prevWavs/" + newBaseFilename
            shutil.move(  strFilename, newfilename )
            print( "INF: SoundAnalyser._sendToSpeechReco: saved wav file in " + newfilename)
        
        return retVal

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
        
                
    def analyse(self, aInterlacedSoundData, bVerbose = False ):
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
        
        if bVerbose: logging.info( "SoundAnalyser.analyse: receiving a buffer of len: %s (equivalent to %5.3fs) (shape:%s)" % (len(aInterlacedSoundData), rSoundDataDuration, str(aInterlacedSoundData.shape)) )
        
        if time.time() > self.timeLastBufferReceived + 0.7:
            # our buffer is now to old (for instance the robot was speaking and we were inhibited)
            logging.info( "SoundAnalyser.analyse: clearing buffer after gap of %5.2fs (after inhibition...)" % (time.time()-self.timeLastBufferReceived) )
            self.bStoringSpeech = False
            self.aStoredDataSpeech = np.array( [], dtype=self.datatype ) # reset
            
        self.timeLastBufferReceived = time.time()
        
        aSoundData = np.reshape( aInterlacedSoundData, (self.nNbrChannel, nNbrOfSamplesByChannel), 'F' );
        #~ logging.debug( "aSoundData len: %s, shape: %s" % (len(aSoundData), str(aSoundData.shape)) )

        aRecognizedNoise = None
        aRecognizedSpeech = None
        aRecognizedUser = None
        
        try:
        	nEnergy = sound.computeEnergyBestNumpy(aSoundData[0]);
        except BaseException, err:
            logging.error( "analyse: while computing energy, err: %s" % str(err) )
            nEnergy = 0
        if bVerbose: logging.info( "SoundAnalyser.analyse: Energy %d" % nEnergy )
        
        # sum of two mics
        mixedSoundData = aSoundData[0]+aSoundData[1]
        #~ logging.debug( "mixedSoundData len: %s, shape: %s" % (len(mixedSoundData), str(mixedSoundData.shape)) )

        computedMfcc = python_speech_features.base.mfcc( mixedSoundData, samplerate=self.nSampleRate, winstep=self.rMfccWindowStepInSec )
        
        aVadStateChange = self.vad.computeFromMfcc( computedMfcc, self.rMfccWindowStepInSec )
        #~ if bVerbose: logging.debug( "aVadStateChange: %s" % aVadStateChange )
        
        # analyse VAD analyse results
        bStoringSpeechDone = False
        for i in range(len(aVadStateChange)):            
            b, t = aVadStateChange[i]
            if b: 
                if t < 0.:
                    # take datas from preBuffer
                    nNbrSamples = int(-t*self.nSampleRate)
                    self.aStoredDataSpeech = self.aStoredSoundPreBuffer[-nNbrSamples:]
                    #~ logging.debug( "pre: %s" % len( self.aStoredDataSpeech ) )
                    #~ logging.debug( "pre: %s" % str(self.aStoredDataSpeech.shape ) )
                    
                    t = 0.
                # add data to next changes:
                if i+1 < len(aVadStateChange):
                    rDuration = aVadStateChange[i+1][1]-t
                else:
                    rDuration = rSoundDataDuration-t
                nStart = int(t*self.nSampleRate)
                nDuration = int(rDuration*self.nSampleRate)
                #~ logging.debug( "%s" % len( self.aStoredDataSpeech ) )
                #~ logging.debug( "%s" % len( mixedSoundData ) )
                #~ logging.debug( "%s" % str(self.aStoredDataSpeech.shape) )
                #~ logging.debug( "%s" % str(mixedSoundData.shape) )
                
                self.aStoredDataSpeech = np.concatenate( (self.aStoredDataSpeech, mixedSoundData[nStart:nStart+nDuration]) );
                
                self.bStoringSpeech = True
                bStoringSpeechDone = True
            else:
                self.bStoringSpeech = False
                strFilename = self.strDstPath + filetools.getFilenameFromTime() + "_speech.wav";
                if bVerbose: logging.info( "SoundAnalyser.analyse: outputting speech to file: '%s'" % strFilename );

                rDuration = len(self.aStoredDataSpeech) / float(self.nSampleRate)
                self._writeBufferToFile( self.aStoredDataSpeech, strFilename  )
                self.aStoredDataSpeech = np.array( [], dtype=self.datatype ) # reset
                
                if self.bActivateSpeechRecognition: 
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
            self.aStoredDataSpeech = np.concatenate( (self.aStoredDataSpeech, mixedSoundData) );
            
            
        if self.bStoringSpeech:
            if len(self.aStoredDataSpeech) > self.nSampleRate*14:
                # if more than 14 sec, keep only 10 last sec
                logging.warning( "SoundAnalyser.analyse: buffer too long, keeping only 10 last seconds..." )
                self.aStoredDataSpeech = self.aStoredDataSpeech[self.nSampleRate*4:] # removing by chunk of 4 sec
                
        
        # prebuffer store and offseting
        self.aStoredSoundPreBuffer = np.concatenate( (self.aStoredSoundPreBuffer, mixedSoundData) );
        self.aStoredSoundPreBuffer = self.aStoredSoundPreBuffer[-self.nSizePreBuffer:]
        
        
        self.simulatedTime += rSoundDataDuration
        return [self.bStoringNoise, self.bStoringSpeech, aRecognizedNoise, aRecognizedSpeech,aRecognizedUser]
        
    # Analyse - end
    
# class SoundAnalyzer - end

def analyseFile( strFilename, rPacketSliceTime = 0.170, bSimulateRealTime = True, strUseLang = "", bVerbose = False ):
    """
    take a file and simulated it's heard from the microphone.
    realtime is keeped
    - strUseLang: lang to use for speech recognition, eg: "fr-FR", if leaved to "": use language currently in the tts
    """
    strFilename = os.path.expanduser( strFilename )
    s = sound.Wav( strFilename )

    if not s.isOpen():
        return False
        
    sa = SoundAnalyzer( nSampleRate=s.nSamplingRate, datatype=s.getNumpyDataType(), nNbrChannel=s.nNbrChannel, strUseLang=strUseLang )
    
    timeBegin = time.time()
    audiodata = s.data
    idx = 0
    nSizeSlice = int(rPacketSliceTime * s.nAvgBytesPerSec/2) # /2 => 16 to 8 bits
    #~ logging.debug( s.data )
    while( idx < len(s.data) ):
        sa.analyse( s.data[idx:idx+nSizeSlice], bVerbose = bVerbose )
        idx += nSizeSlice
        
        if bSimulateRealTime: time.sleep( rPacketSliceTime )        
# analyseFile - end


class AbcdkSoundReceiverModule(naoqi.ALModule):
    """
    Use this object to get call back from the ALMemory of the naoqi world.
    Your callback needs to be a method with two parameter (variable name, value).
    """

    def __init__( self, strModuleName, strNaoIp ):
        self.mem = None
        self.leds = None
        
        self.strNaoIp = strNaoIp
        self.bStarted = False
        
        try:
            naoqi.ALModule.__init__(self, strModuleName )
            self.BIND_PYTHON( self.getName(),"callback" )
            self.BIND_PYTHON( self.getName(),"pause" );
            self.BIND_PYTHON( self.getName(),"resume" );            
            self.mem = naoqitools.myGetProxy( "ALMemory", strNaoIp, 9559 )
            self.leds = naoqitools.myGetProxy( "ALLeds", strNaoIp, 9559 )

        except BaseException, err:
            logging.error( "abcdk.naoqitools.AbcdkSoundReceiverModule: loading error: %s" % str(err) );            
    # __init__ - end
    
    def __del__( self ):
        logging.info( "abcdk.AbcdkSoundReceiverModule.__del__: cleaning everything" );
        self.stop();
    
    def start( self, bActivateSpeechRecognition = True ):
        if self.mem: self.mem.raiseMicroEvent( global_strALMemoryKeyName__stop_process, 0 )
        
        audio = naoqi.ALProxy( "ALAudioDevice", self.strNaoIp, 9559 );
        nNbrChannelFlag = 0; # ALL_Channels: 0,  AL::LEFTCHANNEL: 1, AL::RIGHTCHANNEL: 2; AL::FRONTCHANNEL: 3  or AL::REARCHANNEL: 4.
        nDeinterleave = 0;
        self.nSampleRate = 48000;
        #~ self.nSampleRate = 16000;
        audio.setClientPreferences( self.getName(),  self.nSampleRate, nNbrChannelFlag, nDeinterleave ); # setting same as default generate a bug !?!
        audio.subscribe( self.getName() );
        self.bStarted = True
        logging.info( "SoundReceiver: started!" );
        # self.processRemote( 4, 128, [18,0], "A"*128*4*2 ); # for local test
        
        # on romeo, here's the current order:
        # 0: right;  1: rear;   2: left;   3: front,  
        
        if( nNbrChannelFlag == 0 ):
            self.nNbrChannel = 4
        else:
            self.nNbrChannel = 1
            
        nEnergyThreshold = 300 # ears mic
        nEnergyThreshold = 140 # pepper mic
        self.sa = SoundAnalyzer( nSampleRate = self.nSampleRate, datatype=np.int16, nEnergyThreshold = nEnergyThreshold, bActivateSpeechRecognition = bActivateSpeechRecognition, bActivateSoundRecognition = False )
        
        self.bNoiseDetectedPrev = False
        self.bSpeechDetectedPrev = False
        

        self.inhibit_timeNextUsableAudioForSpeech = time.time() - 1000
        self.inhibit_delayAfterEgoSoundGeneration = 0.050 # time to empty soundcard buffer
        
    
    def stop( self ):
        if( self.bStarted ):
            logging.info( "SoundReceiver: stopping..." );
            audio = naoqi.ALProxy( "ALAudioDevice", self.strNaoIp, 9559 );
            logging.info( "SoundReceiver: stopping: proxy created..." );
            audio.unsubscribe( self.getName() );        
            logging.info( "SoundReceiver: stopped." );
            self.bStarted = False
            
    def isRunning( self ):
        return self.bStarted
            
    def doVisualFeedback( self, bNoiseDetected, bSpeechDetected, aRecognizedNoise, aRecognizedSpeech, aRecognizedUser ):
        if self.leds == None:
            return
            
#        self.leds.post.fadeRGB( "FaceLeds", nColor, 0. )
#        self.leds.post.fadeRGB( "FaceLeds", 0xFFFFFF, 1. )

        if bSpeechDetected:
            color = 0x0000ff
        else:
            color = 0x808080
        leds.dcmMethod.setEyesOneLed( 0, 0.0, color )
        
        if aRecognizedSpeech != None:
            if aRecognizedSpeech == []:
                nColor = 0xff0000
            else:
                nColor = 0x00ff00
            leds.dcmMethod.setEyesOneLed( 1, 0.0, nColor )
            leds.dcmMethod.setChestColor( 0.0, nColor )
            
            leds.dcmMethod.setEyesOneLed( 1, 1.0, 0x404040 )
            leds.dcmMethod.setChestColor( 1.0, 0x404040 )
            
            
    def isAudioOutUsed( self ):
        bText = self.mem.getData( "ALTextToSpeech/TextStarted" )
        if not bText:
            # AudioOutputChanged is of this type:
            # [['Name', 'alsa_output.PCH.output-speakers'], ['Index', 0], ['Mode', 'output'], ['HwType', 'Internal'], ['Volume', [49, 49]], ['BaseVolume', 49], ['Mute', False], ['MonitorStream', 0], ['MonitorStreamName', 'alsa_output.PCH.output-speakers.monitor'], ['State', 'suspended'], ['SampleInfo', [['Rate', 48000], ['Channels', 2], ['Positions', ['front-left', 'front-right']]]]] 
            audioOutputState = self.mem.getData( "AudioOutputChanged" )
            #~ logging.debug( "audioOutputState: %s" % audioOutputState )
            # TODO: a dict to check field name
            strMode = audioOutputState[2][1]
            strState = audioOutputState[9][1]
            #~ logging.debug( "strMode: '%s', strState: '%s'" % (strMode,strState) )
            if strMode == "output" and strState == "running":
                return True
        return bText
    # isAudioOutUsed - end
            
    
    def _processRemote_( self, nbOfChannels, nbrOfSamplesByChannel, aTimeStamp, buffer ):
        """
        This is THE method that receives all the sound buffers from the "ALAudioDevice" module
        """
        #~ logging.debug( "process!" );
        #~ logging.debug( "processRemote: nbOfChannels: %s, nbrOfSamplesByChannel: %s, timestamp: %s, lendata: %s, data0: %s (0x%x), data1: %s (0x%x)" % (nbOfChannels, nbrOfSamplesByChannel, aTimeStamp, len(buffer), buffer[0],ord(buffer[0]),buffer[1],ord(buffer[1])) );
        
        bMustStop = self.mem.getData( global_strALMemoryKeyName__stop_process )
        if( bMustStop ):
            self.stop()
            return

        if 1:
            # handle ego noising
            try:
                # bSpeaking = self.mem.getData( "Speaking" )
                bRet = self.isAudioOutUsed()
                if bRet:
                    self.inhibit_timeNextUsableAudioForSpeech = time.time() + self.inhibit_delayAfterEgoSoundGeneration
            except:
                pass
                #~ bSpeaking = False
                
            
            if( time.time() < self.inhibit_timeNextUsableAudioForSpeech ):
                logging.debug("processRemote: inhibited => skip buffer analyse" );
                return
        

        aSoundDataInterlaced = np.fromstring( str(buffer), dtype=np.int16 );

        if( 1 ):
            retVal = self.sa.analyse( aSoundDataInterlaced)
            bNoiseDetected, bSpeechDetected, aRecognizedNoise, aRecognizedSpeech, aRecognizedUser = retVal
            
            if bNoiseDetected != self.bNoiseDetectedPrev:
                self.mem.raiseMicroEvent( "Audio/NoiseDetected", bNoiseDetected )
                
            if bSpeechDetected != self.bSpeechDetectedPrev:
                self.mem.raiseMicroEvent( "Audio/SpeechDetected", bSpeechDetected )
                
            if aRecognizedNoise != None:
                self.mem.raiseMicroEvent( "Audio/RecognizedSounds", [[aRecognizedNoise[0], aRecognizedNoise[1]]] )
            if aRecognizedSpeech != None:                
                if aRecognizedSpeech == []:
                    self.mem.raiseMicroEvent( "Audio/RecognizedWords", [] )
                else:
                    self.mem.raiseMicroEvent( "Audio/RecognizedWords", [[aRecognizedSpeech[0], aRecognizedSpeech[1]]] )

            if bNoiseDetected != self.bNoiseDetectedPrev or bSpeechDetected != self.bSpeechDetectedPrev or aRecognizedNoise !=  None or aRecognizedSpeech != None:
                self.doVisualFeedback( bNoiseDetected, bSpeechDetected, aRecognizedNoise, aRecognizedSpeech, aRecognizedUser )
                        
                        
            self.bNoiseDetectedPrev = bNoiseDetected
            self.bSpeechDetectedPrev = bSpeechDetected

    # processRemote - end
    
    def processRemote( self, nbOfChannels, nbrOfSamplesByChannel, aTimeStamp, buffer ):
        global global_bSampleReceived
        global_bSampleReceived = True
        
        try:
            return self._processRemote_( nbOfChannels, nbrOfSamplesByChannel, aTimeStamp, buffer )
        except BaseException, err:
            logging.error( "processRemote: err: %s" % str(err) )
            
        
        
    def version( self ):
        return "0.6";        
# AbcdkSoundReceiverModule - end

# global objectPoint
abcdk_soundReceiverRef = None
global AbcdkSoundReceiver

def launchSoundReceiverStandalone( strRobotIp = "localhost", bActivateSpeechRecognition = True ):
    """
    launch a sound receiver.
    stop it when the events "sound_receiver_must_stop" is triggered in the ALMemory
    """
    logging.info( "launchSoundReceiverStandalone( ip= '%s', speechReco=%s ) - beginning..." % (strRobotIp,bActivateSpeechRecognition) )
    config.setDefaultIP( strRobotIp, bSetNotInChoregraphe = True );
    
    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = naoqi.ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       strRobotIp,         # parent broker IP
       9559)       # parent broker port    
       
    global AbcdkSoundReceiver
    AbcdkSoundReceiver = AbcdkSoundReceiverModule( "AbcdkSoundReceiver", strRobotIp )
    abcdk_soundReceiverRef = AbcdkSoundReceiver
    AbcdkSoundReceiver.start(bActivateSpeechRecognition=bActivateSpeechRecognition)
    
    # wait it's stopped to leave hands to user
    global global_bSampleReceived
    while AbcdkSoundReceiver.isRunning():
        global_bSampleReceived = False
        time.sleep( 10. )
        if not global_bSampleReceived:
            logging.info( "launchSoundReceiverStandalone( %s ) - no samples received, exiting..." % strRobotIp )        
            break
            
    AbcdkSoundReceiver.stop()
    
    logging.info( "launchSoundReceiverStandalone( %s ) - shutdowning" % strRobotIp )
    myBroker.shutdown()
    logging.info( "launchSoundReceiverStandalone( %s ) - ended" % strRobotIp )
        
# launchSoundReceiverStandalone - end        
    
def launchSoundReceiverStandalone_stop( strRobotIp = "localhost" ):
    # in case we're in the same memory space/python evaluator
    global AbcdkSoundReceiver
    if AbcdkSoundReceiver.isRunning():
        AbcdkSoundReceiver.stop()
        return # don't exit there, it doesn't cost a lot to post also in the ALMemory...
    
    logging.info( "launchSoundReceiverStandalone_stop: gentle memory demand" )
    config.setDefaultIP( strRobotIp, bSetNotInChoregraphe = True );
    mem = naoqitools.myGetProxy( "ALMemory", strRobotIp, 9559 )
    mem.raiseMicroEvent( global_strALMemoryKeyName__stop_process, 1 )
    return
    
    logging.warning( "kill program sound_analyser" )
    p = os.popen('ps -ef | pgrep sound_analyser',"r")
    pid = p.readline() 
    resultat = os.system("kill %s" %(pid))
    if resultat == 0:
        logging.debug("Kill with success sound_analyser.")
    else :
        logging.error("Error no process sound_analyser.")

def launchSoundReceiverFromShell( strRobotIp = "localhost",  bActivateSpeechRecognition = True ):
    """
    this is a usefull method to be launched directly from command line with this line:
    python -c "import abcdk.sound_analyser; abcdk.sound_analyser.launchSoundReceiverFromShell('localhost')"
    """
    logging.info( "launchSoundReceiverFromCommandLine( %s ) - beginning..." % strRobotIp )
    #~ strCommand = "python -c 'import abcdk.sound_analyser; abcdk.sound_analyser.launchSoundReceiverStandalone( \"%s\" )'" % strRobotIp # callback failed with this command
    strCommand = "python /home/nao/.local/lib/python2.7/site-packages/abcdk/sound_analyser.py %s %s" % (strRobotIp,bActivateSpeechRecognition)
    logging.debug( "launchSoundReceiverFromCommandLine: launching: '%s'" %  strCommand )
    os.system( strCommand )    
    logging.info( "launchSoundReceiverFromCommandLine( %s ) - ended" % strRobotIp )

def launchFromCommandLine():
    strIP = "localhost"
    if len(sys.argv) > 1:
        strIP = sys.argv[1]

    bActivateSpeechRecognition = False        
    if len(sys.argv) > 2:
        strSpeechReco = sys.argv[2]        
        if strSpeechReco == "1" or strSpeechReco[0].lower() == 't':
            bActivateSpeechRecognition = True
        
    launchSoundReceiverStandalone( strIP, bActivateSpeechRecognition=bActivateSpeechRecognition )
    
def testAnalyseFile():
    s = "~/sounds/alexandre_m__41__male__pepper__ref__1.wav"
    analyseFile( s, bVerbose = True, bSimulateRealTime = False, strUseLang="fr" )
    
if __name__ == "__main__":
    logging.basicConfig(filename='/home/nao/speech_reco.log',
            level=logging.DEBUG,
            format='%(levelname)s %(relativeCreated)6d %(threadName)s %(message)s (%(module)s.%(lineno)d)',
            filemode='w')

    logFormatter = log_formatter.LogFormatter("/home/nao/speech_reco.log", level=log_formatter.DEBUG)
    logFormatter.start()
    launchFromCommandLine()
    logFormatter.stopReadingLogs()
    #~ launchSoundReceiverStandalone( "localhost" ) # "NaoLaurentV5BT.local"
    
    #~ testAnalyseFile()
