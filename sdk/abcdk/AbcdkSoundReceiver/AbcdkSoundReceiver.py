"""
A sample showing how to have a NAOqi service as a Python app.
"""

__version__ = "0.0.3"

__copyright__ = "Copyright 2015, Aldebaran Robotics"
__author__ = 'YOURNAME'
__email__ = 'YOUREMAIL@aldebaran.com'

import qi
import numpy as np
import os
import sys
import time
import shutil
import threading
import logging

from vad import VAD
from sound_analyser import SoundAnalyser

import abcdk.sound.analyse
import abcdk.leds
from abcdk.files import moveFiles

import stk.runner
import stk.events
import stk.services

class AbcdkSoundReceiver(object):
    """
    NAOqi service for sound recognition.
    """
    APP_ID = "com.aldebaran.ALMyService"
    def __init__(self, qiapp):
        # generic activity boilerplate
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(self.qiapp.session)
        self.s = stk.services.ServiceCache(self.qiapp.session)
        
        filename = "~/logs/"
        filename = os.path.expanduser(filename)
        try: os.makedirs(filename)
        except: pass
        
        filename += "AbcdkSoundReceiver.log"
        logging.basicConfig(filename=filename,
            level=logging.INFO,
            format='%(levelname)s %(relativeCreated)6d %(threadName)s %(message)s (%(module)s.%(lineno)d)',
            filemode='w')

# 18-01-25 Alma: MoveFiles should be independent to this class
#        self.mover = moveFiles.MoveFiles(strPath = "logs/",
#                                         strDstHost = "robotdata@protolab.aldebaran.com",
#                                         rBandwithMax = 10.0)


    def on_start(self):
        self.start()


    @qi.bind(returnType=qi.Void, paramsType=[])
    def start(self):
        """
        Start the module. Will not run.
        To have the module running call "subscribeAudio"
        """
        logging.info("Start module")

        nNbrChannelFlag = 0 
        nDeinterleave = 0
        self.nSampleRate = 48000
        if nNbrChannelFlag == 0:
            self.nNbrChannel = 4
        else:
            self.nNbrChannel = 1
        nEnergyThreshold = 300 # ears mic
        nEnergyThreshold = 140 # pepper mic
        self.bNoiseDetectedPrev = False
        self.bSpeechDetectedPrev = False
        self.visualFeedback = True
        self.nInhibitEndTime = time.time() - 1000
        self.nDelayAfterSoundGeneration = 0.050 # time to empty soundcard buffer

        #~ self.leds = leds.LedsDcm(self.qiapp)
        #~ self.leds.createProxy()
        #~ self.leds.createAliases()
        self.leds = abcdk.leds.ledsDcm
        self.sa = SoundAnalyser( self.qiapp, 
                                 nSampleRate = self.nSampleRate, 
                                 datatype=np.int16, 
                                 nEnergyThreshold = nEnergyThreshold, 
                                 bActivateSpeechRecognition = True,
                                 bKeepAudioFiles = True,
                                 rTimePreVAD = 0.3,
                                 rTimePostVAD = 0.7)

        self.audio = self.qiapp.session.service("ALAudioDevice")
        self.audio.setClientPreferences("AbcdkSoundReceiver", self.nSampleRate, nNbrChannelFlag, nDeinterleave)

        self.mem = self.qiapp.session.service("ALMemory")

# 18-01-25 Alma: MoveFiles should be independent to this class
        #self.mover.start()


    @qi.bind(returnType=qi.Void, paramsType=[])
    def subscribeAudio(self):
        """
        Subscribe to AudioDevice. Allows the processRemove function to be called
        when a new audio sample is available
        """
        logging.info("Subscribe to audio")
        self.audio.subscribe("AbcdkSoundReceiver")


    def processRemote( self, nbOfChannels, nbrOfSamplesByChannel, aTimeStamp, aBuffer ):
        """
        Method called automatically when a new buffer is available on AudioDevice
        """
        #try:
        return self._processRemote(nbOfChannels, nbrOfSamplesByChannel, aTimeStamp, aBuffer )
        #except BaseException, err:
        #    logging.error(str(err))

    @qi.bind(returnType=qi.Void, paramsType=[qi.Bool])
    def setVisualFeedback(self, status):
        """
        Stop the service.
        """
        logging.info("Set visual feedback to: " + str(status) )
        self.visualFeedback = status


    @qi.bind(returnType=qi.Void, paramsType=[])
    def stop(self):
        """
        Stop the service.
        """
        logging.info("AbcdkSoundReceiver stopped by user request.")
        self.qiapp.stop()


    @qi.nobind
    def on_stop(self):
        """
        Cleanup
        """
        logging.info("Cleaning")
        self.unsubscribeAudio()
        self.sa.stop()
# 18-01-25 Alma: MoveFiles should be independent to this class
        #self.mover.stop()
        logging.info("ALMyService finished.")


    @qi.bind(returnType=qi.Void, paramsType=[])
    def unsubscribeAudio(self):
        logging.info("Unsubscribe from audio")
        self.audio.unsubscribe("AbcdkSoundReceiver")


    def _processRemote(self, nbOfChannels, nbrOfSamplesByChannel, aTimeStamp, aBuffer):
        """
        Main method receiving the audio buffer and returning the recognized words
        """
        logging.debug("Process remote")

        if abcdk.sound.analyse.isAudioOutUsed(self.mem) == True:
            logging.debug("Detected robot speaking")
            self.nInhibitEndTime = time.time() + self.nDelayAfterSoundGeneration

        if time.time() < self.nInhibitEndTime :
            logging.debug("Inhibited => skip buffer analyse" )
            return

        aSoundDataInterlaced = np.fromstring( str(aBuffer), dtype=np.int16 );

        retVal = self.sa.asrBuffer( aSoundDataInterlaced)
        bNoiseDetected, bSpeechDetected, aRecognizedNoise, aRecognizedSpeech, aRecognizedUser = retVal

        if bNoiseDetected == True:
            self.mem.raiseMicroEvent( "Audio/NoiseDetected", bNoiseDetected )
            
        if bSpeechDetected == True:
            self.mem.raiseMicroEvent( "Audio/SpeechDetected", bSpeechDetected )
            
        if aRecognizedNoise != None:
            self.mem.raiseMicroEvent( "Audio/RecognizedSounds", [[aRecognizedNoise[0], aRecognizedNoise[1]]] )
        if aRecognizedSpeech != None:                
            if aRecognizedSpeech == []:
                self.mem.raiseMicroEvent( "Audio/RecognizedWords", [] )
            else:
                self.mem.raiseMicroEvent( "Audio/RecognizedWords", [[aRecognizedSpeech[0], aRecognizedSpeech[1]]] )

        #TODO add a variable to start and stop the visual feedback
        if self.visualFeedback == True and (bNoiseDetected != self.bNoiseDetectedPrev or \
                                            bSpeechDetected != self.bSpeechDetectedPrev or \
                                            aRecognizedNoise !=  None or \
                                            aRecognizedSpeech != None):
            self.doVisualFeedback( bNoiseDetected, bSpeechDetected, aRecognizedNoise, aRecognizedSpeech, aRecognizedUser )

        self.bNoiseDetectedPrev = bNoiseDetected
        self.bSpeechDetectedPrev = bSpeechDetected


    def doVisualFeedback( self, bNoiseDetected, bSpeechDetected, aRecognizedNoise, aRecognizedSpeech, aRecognizedUser ):
        if self.leds == None:
            return

        if bSpeechDetected:
            color = 0x0000ff
        else:
            color = 0x808080
        self.leds.setEyesOneLed( 0, 0.0, color )
        
        if aRecognizedSpeech != None:
            if aRecognizedSpeech == []:
                nColor = 0xff0000
            else:
                nColor = 0x00ff00
            self.leds.setEyesOneLed( 1, 0.0, nColor )
            self.leds.setChestColor( 0.0, nColor )
            
            self.leds.setEyesOneLed( 1, 1.0, 0x404040 )
            self.leds.setChestColor( 1.0, 0x404040 )
####################
# Setup and Run
####################

if __name__ == "__main__":
    qiapp = stk.runner.init()
    activity,service_id = stk.runner.register_activity(AbcdkSoundReceiver, "AbcdkSoundReceiver", qiapp)
    try:
        time.sleep(1)
        qiapp.session.service("AbcdkSoundReceiver").subscribeAudio()
        qiapp.run()
    finally:
        stk.runner.cleanup(qiapp,activity,service_id)

