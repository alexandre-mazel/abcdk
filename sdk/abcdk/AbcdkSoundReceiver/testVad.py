#!/usr/bin/python

import sys
import time

from abcdk.sound import wav
from abcdk import python_speech_features
from abcdk.AbcdkSoundReceiver import vad

if __name__ == "__main__":
    
    rMfccWindowStepInSec = 0.01

    s = wav.Wav( sys.argv[1] )
    if not s.isOpen():
        raise OSError("File not found: " + strFilename)

    vad = vad.VAD(0.150,0.500)

    aMixedSoundData = s.data
    if s.nNbrChannel > 1:
        aMixedSoundData = aMixedSoundData[0::s.nNbrChannel]+aMixedSoundData[1::s.nNbrChannel] 

    nSampleRate = s.nSamplingRate

    nNbrOfSamplesByChannel = len(s.data) / s.nNbrChannel        
    rSoundDataDuration = nNbrOfSamplesByChannel / float(nSampleRate)

    timeBegin = time.time()

    computedMfcc = python_speech_features.base.mfcc( aMixedSoundData, samplerate=nSampleRate, winstep=rMfccWindowStepInSec )
    aVadStateChange = vad.computeFromMfcc( computedMfcc, rMfccWindowStepInSec )

    timeEnd = time.time()

    print("Length of the file: " + str(s.rDuration) + " seconds")
    print("Time needed to do vad: " + str(timeEnd - timeBegin) + " seconds" )
    print("Result: " + str(aVadStateChange))
