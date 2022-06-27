# -*- coding: utf-8 -*-
###########################################################
# Aldebaran Behavior Complementary Development Kit
# Sound Generator
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

print("importing abcdk.sound_generation")

import math

try:
    import numpy as np
except ImportError, err:
    print "WRN: can't load numpy, and it is required for some functionalities... detailed error: %s" % err;



class SoundGenerator:
    """
    Generate sound intended to be streamed to some sound card
    classic use:
        sg = SoundGenerator( 22000 )
        rDt = 0.2
        while( True ):
            timeBeginLoop = time.time()
            aAudioBuf = getNewSoundPortion( 440, rDt )
            send_to_you_audio_card( aAudioBuf )
            timeElapsed = time.time() - timeBeginLoop
            time.sleep( rDt - timeElapsed )
    """
    
    def __init__(self, rSamplingRate = 44100 ):
        self.rSamplingRate = rSamplingRate
        self.rPhase = 0.
        self.nCptCall = 0
        
    def getNewSoundPortion( self, rFreq, rDuration = 0.1 ):
        """
        generate a buffer with sound
        """
        nNbrSample = int(rDuration*self.rSamplingRate)
        
        t = np.arange(nNbrSample)
        amplitudeVector = np.linspace(0, 100, nNbrSample)  # ?
        #~ print amplitudeVector
        audiobuf = np.sin(t * 2 * math.pi*rFreq/self.rSamplingRate + self.rPhase)
        
        rOffset = ((nNbrSample * rFreq / self.rSamplingRate ) % 1) #/ nSamplingRate   # decalage temporel
        self.rPhase = self.rPhase + (2*math.pi * rOffset) # * (1/ nSamplingRate)
        
        self.nCptCall += 1
        
        if( 1 ):
            nNbrSample = 8192
            if( self.nCptCall & 1 ):
                return [32000]*nNbrSample
            return [0]*nNbrSample
        
        return audiobuf
        
# class SoundGenerator - end

def autoTest():
    import time
    sg = SoundGenerator( 22000 )
    rDt = 0.2
    for i in range(5):
        timeBeginLoop = time.time()
        aAudioBuf = sg.getNewSoundPortion( 440, rDt )
        print( "aAudioBuf: %s" % aAudioBuf )
        #~ send_to_you_audio_card( aAudioBuf )
        timeElapsed = time.time() - timeBeginLoop
        time.sleep( rDt - timeElapsed )
    
    
if( __name__ == "__main__" ):
    autoTest();