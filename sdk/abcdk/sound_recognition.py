# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Sound Recognition Extractor
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

print( "importing abcdk.sound_recognition" );

import naoqi
import qi
import numpy as np
import os
import time
import sys
import datetime


import json
import abcdk.sound


class SoundRecognizer:
    """
    Receive buffer directly from a sound buffer and analyse it
    """

    def __init__( self, strModuleName, strNaoIp = "localhost" ):
        self.strNaoIp = strNaoIp;
        self.strCurrentFilename = None;
        self.rMaxDurationPerSend = 4.; # in second
        self.rSegmentDurationForANewIncompleteCall = 0.5; # the length of each diff for a new send in second: default: 1, put a big number and you'll save some cpu but lose reactivity in long/noisy ambiance
        self.rTimeDurationLastSend = 0.;  # the time (expressed in duration) of the last send
        
        mem = naoqi.ALProxy( "ALMemory", self.strNaoIp, 9559 );
        try:
            self.soundRecognition_proxy = naoqi.ALProxy( "ProtolabSoundRecognitionService", self.strNaoIp, 9559 );
        except BaseException, err:
            print( "WRN: ProtolabSoundRecognitionService not found !!! (err:%s)" % err );
        self.strRobotName = mem.getData( "HAL/Robot/Type" );
        self.rEnergyThreshold = 60;
        if( "nao" in self.strRobotName.lower() ):
            self.rEnergyThreshold = 200;
            
        self.aStoredSoundData = np.array( [], dtype=np.int16 ); # a numpy int16 array storing current sound
        self.bStoring = False; # are we currently storing ?
        self.timeLastEnergy = time.time() - 100
        
        self.strDstPath = "/tmp/";
        try:
            os.makedirs( self.strDstPath );
        except: pass
        
    # __init__ - end
    
    def __del__( self ):
        print( "INF: abcdk.SoundRecognizer.__del__: cleaning everything" );
        self.stop();
    
    def start( self ):
        nNbrChannelFlag = 2; # ALL_Channels: 0,  AL::LEFTCHANNEL: 1, AL::RIGHTCHANNEL: 2; AL::FRONTCHANNEL: 3  or AL::REARCHANNEL: 4.
        if( nNbrChannelFlag == 0 ):
            self.nNbrChannels = 4;
        else:
            self.nNbrChannels = 1;
        nDeinterleave = 0;
        self.nSampleRate = 48000;
        #~ self.nSampleRate = 16000;
        audio.setClientPreferences( self.getName(),  self.nSampleRate, nNbrChannelFlag, nDeinterleave ); # setting same as default generate a bug !?!
        audio.subscribe( self.getName() );
        print( "INF: SoundReceiver: started!" );
        # self.processRemote( 4, 128, [18,0], "A"*128*4*2 ); # for local test
        
        # on romeo, here's the current order:
        # 0: right;  1: rear;   2: left;   3: front,  
        
    
    def stop( self ):
        print( "INF: abcdk.SoundRecognizer.: stopping..." );
        print( "INF: abcdk.SoundRecognizer.: stopped!" );
            
    
    def processRemote( self, nbOfChannels, nbrOfSamplesByChannel, aTimeStamp, buffer ):
        """
        This is THE method that receives all the sound buffers from the "ALAudioDevice" module
        """

        
        global global_bSampleReceived;
        global_bSampleReceived = True;
        
        aSoundData = np.fromstring( str(buffer), dtype=np.int16 );
        nEnergy = abcdk.sound.computeEnergyBestNumpy(aSoundData);
        print( "nEnergy: %s" % nEnergy );
        
        bSendFile = False;
        bEndOfSound = False;
        if( nEnergy > self.rEnergyThreshold ):
            print( "DBG: High nEnergy: %s" % nEnergy );
            self.timeLastEnergy = time.time();
            self.bStoring = True;
        else:
            if( self.bStoring and time.time() - self.timeLastEnergy > 0.2 ):
                # end of the sound
                bEndOfSound = True;
                
                
        if( self.bStoring ):
            print( "bStoring: %s" % self.bStoring );
            self.aStoredSoundData = np.concatenate( (self.aStoredSoundData, aSoundData) );
            #~ rSampleDuration = float(nbrOfSamplesByChannel) / self.nSampleRate;
            rCurrentDuration = len(self.aStoredSoundData) / self.nSampleRate; # ASSUME MONO CHANNEL !
            if( rCurrentDuration > self.rMaxDurationPerSend ):
                # remove 1 sec from beginning
                rTimeToRemove = 1.;
                self.aStoredSoundData = self.aStoredSoundData[int(self.nSampleRate*rTimeToRemove):]; # ASSUME MONO CHANNEL !
                rCurrentDuration -= rTimeToRemove;
                self.rTimeDurationLastSend -= rTimeToRemove;
            if( rCurrentDuration > self.rTimeDurationLastSend + self.rSegmentDurationForANewIncompleteCall or (bEndOfSound and self.rTimeDurationLastSend == 0. ) ):
                bSendFile = True;
            
            
        if( bSendFile ):
            print( "bSendFile: %s" % bSendFile );
            self.rTimeDurationLastSend = rCurrentDuration;
            strFilename = self.strDstPath + getFilenameFromTime() + "_" + self.strRobotName + ".wav";
            self.strCurrentFilename = strFilename;
            print( "INF: outputting to a new file: %s" % strFilename );
            wavTemp = abcdk.sound.Wav();
            wavTemp.new( nSamplingRate = self.nSampleRate, nNbrChannel = self.nNbrChannels, nNbrBitsPerSample = 16 );
            wavTemp.addData( self.aStoredSoundData );
            wavTemp.write( strFilename );

            print( "bEndOfSound: %s" % bEndOfSound );
            
            if( 0 ):
                ## CALLING REMOTE Service
                print("Calling remote rest service")
                ## attention le proxy vers le service est sur le robot le fichier doit aussi etre sur le robot..

                fut = qi.async(self.soundRecognition_proxy.analyzeSoundFile, self.strCurrentFilename)
                fut.addCallback(self.callback_sound_detected)

        if( bEndOfSound ):
            print( "bEndOfSound: new buffer" );
            self.aStoredSoundData = np.array( [], dtype=np.int16 );
            self.bStoring = False;
            self.rTimeDurationLastSend = 0;
                
    # processRemote - end

    def callback_sound_detected(self, fut):
        print('calling calback sound detected')
        res = json.loads(fut.value())
        print("RES IS %s" % str(res))
        for aClassifResult in res['classif']:
            strTextToSay = aClassifResult[2]
            if strTextToSay == "fingerclap":
                continue
            print("saying %s" % strTextToSay)
            self.tts.say(str(strTextToSay))

    def version( self ):
        return "0.6";
        
# SoundReceiverAndDetectorModule - end

