# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Tracking Tools
# Author A. Mazel
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Tracking Tools: tracking and prepare to interaction functions"

print( "importing abcdk.tracking" );

import mutex
import os
import random
import time

import extractortools
import facerecognition
import image
import leds
import motiontools
import naoqitools
import numeric
import pathtools
import system
import test

def loadFaceDetectorModule():
    """
    Find and launch the face detection extractor module
    return the proxy on him or None
    """
    if( system.isOnRomeo() ):
        strLauncherName = "ALLauncher_video";
    else:
        strLauncherName = "ALLauncher";
    
    extractor = naoqitools.myGetProxy( "HaarExtractor" );
    if( extractor == None ):
        naoqitools.launch( "HaarExtractor", "/home/nao/.local/lib/libhaar_extractor.so", bHandleMultiVersion = True, strLauncherName = strLauncherName );
        extractor = naoqitools.myGetProxy( "HaarExtractor" );
    extractor.setCascadeFile( pathtools.getABCDK_Path() + os.sep + "data" + os.sep + "haarcascades" + os.sep + "haarcascade_frontalface_alt.xml" );                        
    return extractor;
# loadFaceDetectorModule - end

# lancer l'extracteur a la main depuis romeo.video
"""
import naoqi
launcher = naoqi.ALProxy( "ALLauncher_video", "198.18.0.1", 9559 )
# or
launcher = naoqi.ALProxy( "ALLauncher", "localhost", 9559 )
launcher.launchLocal( "/home/nao/.local/lib/libhaar_extractor_1_22_2.so" );
ha = naoqi.ALProxy( "HaarExtractor", "localhost", 9559 )
ha.setCascadeFile( "/home/nao/.local/lib/python2.7/site-packages/abcdk/data/haarcascades/haarcascade_frontalface_alt.xml" );
ha.setDebugMode( True );
ha.subscribe( "toto" );

ha.unsubscribe( "toto" );
"""
    


class TrackHuman:
    """
    Track an human, easy to launch and stop.
    Normal use:
        prepare() - once (optionnal) (first start would be faster)
            # many times:
            start()
            stop()
        close() - once (optionnal) (some cpu will be gained)

    This is an attempt to make a naoqi-module-like, without being a naoqi module
    """

    def __init__( self ):
        self.mutex = mutex.mutex(); # we armour init, pause and destroy
        self.extractor = None;
        self.bPrepared = False;        
        self.nNbrStarted = 0; # 0: not started, 1: started, 2: started twice, ...
        self.nNbrPaused = 0;
        self.rMaxDistance = 0.;
        self.bInUpdate = False;
        self.bDebugMode = False;
        self.motion = None;
        self.mem = None;
        self.memVideo = None;
        self.fr = None;
        self.sl = None;
        self.id = -1;

        self.timeLastHeadMove = 0;
        self.timeLastMoveToFix=time.time()-1000; # start time of fix people
        self.bSoundLocalisationIsRunning = False;
        
        self.nSharpnessMethod = 2;
        self.nSharpnessValue = 0;
        self.rSharpnessMultiplier = 1.1;
        self.rSharpnessRatioWindow = 0.6;
        if( system.isOnOtherRobotThanNao() ):
            print(" INF: abcdk.TrackHuman.__init__: We are on another robot than NAO" );
            self.nSharpnessMethod = 3;   
            self.nSharpnessValue = 2;
            self.rSharpnessMultiplier = 1.;
            self.rSharpnessRatioWindow = 0.4;
        else:
            print(" INF: abcdk.TrackHuman.__init__: We are on NAO" );
        print(" INF: abcdk.TrackHuman.__init__: rSharpnessMultiplier: %f" % self.rSharpnessMultiplier );
        
        # tracking move configuration
        self.rTrackSpeed = 0.06; # was 0.06
        if( system.isOnOtherRobotThanNao() ):
            self.rTrackSpeed *= 4;
        self.bTrackUsePitch = True;
        self.rTrackYawLimit = 1.5;
        
        self.nComplainAboutNotHavingPause = 0;
        self.bTrackWithEyes = False;
        
        self.bUseNativeExtractor = True; # else it's the HaarCascade generic from the ProtoLabs
        
        self.idX = -1;
        self.idY = -1;
        self.idTrunk = -1;
        self.bMustStop = False;
        
        
        if( system.isOnRomeo() ):
            print(" INF: abcdk.TrackHuman.__init__: We are on Romeo!" );
            self.bTrackWithEyes = True;
            self.bUseTrunk = True;
            self.rSpeedTrackX = 0.1;
            self.rSpeedTrackY = 0.2;
            self.rAmortiHeadX = 0.5;
            #self.eyesMover = motiontools.EyesMover();
            self.eyesMover = motiontools.eyesMover;
            print(" INF: abcdk.TrackHuman.__init__: using eyesmover: %s!" % self.eyesMover );
            self.eyesMover.setStiffness();
            self.strLauncherName = "ALLauncher_video";
            self.rThresholdToMove = 0.03;
            self.headChain = ["NeckYaw","HeadPitch", "NeckPitch"];
            self.strMemoryVideoName = "ALMemory_video";
            self.rPitchRatioThruJoint = [0.65, 0.35]
            import romeo
        else:
            self.rSpeedTrackX = 0.05;
            self.rSpeedTrackY = 0.1;
            self.rAmortiHeadX = 0.8
            self.bUseTrunk = False;
            self.strLauncherName = "ALLauncher";            
            self.rThresholdToMove = 0.05;
            self.headChain = ["HeadYaw","HeadPitch"];
            self.strMemoryVideoName = "ALMemory";
            self.rPitchRatioThruJoint = [1.]
            
        self.strFaceDetectMemoryName = "FaceDetection/FaceDetected";
        self.strSoundLocalisedMemoryName = "ALAudioSourceLocalization/SoundLocated";
        
    # __init__ - end
    
    def __del__( self ):
        self.close();
    # __del__ - end
    
    def debug( self, strMessage ):
        if( self.bDebugMode ):
            print strMessage;
    # debug - end
    
    def getName( self ):
        return "abcdk.tracking.TrackHuman";
        
    def tryToPauseExtractor( self, bNewState ):
        """
        Because some old extractor version doesn't have a pause mecanism... We emulate it or at least we catch the error!
        """
        if( not self.bUseNativeExtractor ):
            try:
                self.extractor.pause( bNewState );
            except BaseException, err:
                if( self.nComplainAboutNotHavingPause < 10 ):
                    self.nComplainAboutNotHavingPause += 1;
                    print( "DBG: should be a normal error: '%s'" % str( err ) );
                pass
    # tryToPauseExtractor - end
    
    def prepare( self, bState = True ):
        """
        Prepare to start, so it will start fast!
        """
        while( self.mutex.testandset() == False ):
            print( "INF: abcdk.TrackHuman.prepare: already preparing, waiting..." );
            time.sleep( 0.1 );
        
        if( self.bPrepared == bState ):
            self.mutex.unlock();
            return;
        self.debug( "DBG: INF: abcdk.TrackHuman.prepare(%s)" % str( bState ) );
        
        self.bPrepared = bState;
        if( bState ):
            try:
                if( self.bUseNativeExtractor ):
                    self.extractor = naoqitools.myGetProxy( "ALFaceDetection" );
                else:
                    if( self.extractor == None ):
                        print("INF: abcdk.TrackHuman.prepare: creating proxy to HaarExtractor..." );
                        self.extractor = loadFaceDetectorModule();
                    if( self.extractor == None ):
                        raise( BaseException( "ERR: abcdk.TrackHuman.prepare: the module HaarExtractor has to be loaded in your system to have face tracking!" ) );
                    if( self.fr == None ):
                        naoqitools.launch( "ALFaceRecognition", "/usr/lib/naoqi/libfacerecognition.so", strLauncherName = self.strLauncherName );
                        self.fr = naoqitools.myGetProxy( "ALFaceRecognition" );
                        if( self.fr == None ):
                            print( "WRN: abcdk.TrackHuman.prepare: no face recognition module 'ALFaceRecognition' found, you couldn't use that feature..." );
                            
                    self.extractor.setCascadeFile( pathtools.getABCDK_Path() + os.sep + "data" + os.sep + "haarcascades" + os.sep + "haarcascade_frontalface_alt.xml" );
                    self.extractor.setDebugMode( self.bDebugMode );
                    self.extractor.setMinNeighbors( 3 );       # was 2 !!!  
                    self.extractor.setFilter_MostCentral( True );
                    self.extractor.setFilter_Biggest( True );
                    if( self.fr != None ):
                        self.extractor.saveDetected( "/tmp/", 2, 18 );
                    self.extractor.setExtraSleepOnDetection( 0. );
                            
                if( self.motion == None ):
                    self.motion = naoqitools.myGetProxy( "ALMotion" );
                if( self.mem == None ):
                    self.mem = naoqitools.myGetProxy( "ALMemory" );
                if( self.memVideo == None ):
                    self.memVideo = naoqitools.myGetProxy( self.strMemoryVideoName );
                    
                if( self.sl == None ):
                    self.sl = naoqitools.myGetProxy( "ALAudioSourceLocalization" );
                if( system.isOnRomeo() ):
                    if( not self.bUseNativeExtractor ):
                        #~ self.extractor.setFlipImage( True ); # $$$ for our buggy romeo
                        self.extractor.setUseMotionProxy( False );
                    
                try:
                    self.extractor.subscribe( self.getName(), 300, 0.0 ); # 500 when face at everyframe, or around 300 is fine (if not often faces) setting too fast will take all cpu, leaving nothing to FaceRecognition - 200 because we changed the minsize to 50
                except BaseException, err:
                    print( "WRN: abcdk.TrackHuman.prepare: subscribe fail (possible on romeo, on second time...) $$$, err: %s" % err );
                self.tryToPauseExtractor( True );
                motiontools.ensureMinimalStiffness( "Head", 0.4 );
            except BaseException, err:
                self.mutex.unlock();
                raise( BaseException( "ERR: abcdk.TrackHuman.prepare: init error: %s" % err ) );
                return; # to emphasize we're raising just the line before
        else:
            if( self.extractor != None ):
                self.stop();
                if( system.isOnRomeo() and False ): # now it works!
                    print( "WRN: abcdk.TrackHuman.prepare: unsubscribing from extractor - generate a failure, won't unsubscribe !!! TODO WARNING $$$$" );
                else:
                    print( "INF: abcdk.TrackHuman.prepare: unsubscribing from extractor - begin" );
                    self.extractor.unsubscribe( self.getName() );
                    print( "INF: abcdk.TrackHuman.prepare: unsubscribing from extractor - end" );
                
            if( self.bSoundLocalisationIsRunning ):
                self.bSoundLocalisationIsRunning = False;            
                print( "DBG: abcdk.TrackHuman.prepare: SoundLocalization - stop" );           
                self.sl.unsubscribe( self.getName() );
                
            if( self.id != -1 ):
                try:
                    self.motion.stop( self.id );
                except BaseException, err:
                    print( "DBG: abcdk.TrackHuman.update: normal error: %s" % str( err ) );
                    pass
                self.id = -1;     

        if( self.bTrackWithEyes ):
            import romeo
            romeo.dispatchEyesCommand_stop();
            
        self.idX = -1;
        self.idY = -1;
        self.idTrunk = -1;
        self.abLastFrameFastMove = [False,False]; # [on axis X, on axisY]: if last frame has a big move, we skip the new face position (as it's very unprecise) TODO: have the camera position relative to the analysed image!
            
        self.mutex.unlock();
    # prepare - end
    
    def close( self ):
        """
        Released all used cpu, unsubscribe, ...
        """
        self.prepare( False );
    # close - end
    
    def start( self, rMaxDistance = 1.5 ):
        """
        Launch a tracking.
        If you start it twice, you need to stop it twice!
        rMaxDistance: an idea of the max distance to detect face (the farest, the more cpu consumming)
        """
        self.prepare();
        self.timeLastHeadMove = time.time(); # prevent to send a raz at the beginning of the tracker, so that perhaps we're already facing the good direction !
        nMinSize = int( 320*0.14/rMaxDistance ); # 320 is the resolution and 0.14 is a ratio computed roughly from current aperture and average size of an human. (very roughly)
        print("INF: abcdk.TrackHuman.start: dist: %f => minsize: %d" % ( rMaxDistance, nMinSize ) );
        if( self.extractor != None ):
            if( not self.bUseNativeExtractor ):
                self.extractor.setMinSize( nMinSize, nMinSize );
        try:
            self.extractor.setFrameRate( 30 );
        except BaseException, err:
            print("WRN: abcdk.TrackHuman.start: error in setFrameRate: %s" % ( err ) );    
            pass
        self.extractor.setSaveImageWithFace(1)
        self.tryToPauseExtractor( False );
        self.timeLastHumanSeen = time.time();
    # start - end
    
    def stop( self ):
        """
        Stop a tracking.
        If you start it twice, you need to stop it twice! (perhaps)
        """
        self.bMustStop = True;
        self.debug( "DBG: INF: abcdk.TrackHuman.stop()" );
        self.tryToPauseExtractor( True );
        for i in range(4):
            self.stopAllMoves();
            time.sleep( 0.05 );
    # stop - end
    
    def stopAllMoves(self):
        """
        kill all motion task for head and trunk
        used when moving randomly and seeing someone, or at stop or ...
        """
        if( self.id != -1 ):
            try:
                print( "DBG: stopAllMoves: stopping move task id: %d" % ( self.id ) );
                self.motion.stop( self.id );
            except BaseException, err:
                print( "DBG: abcdk.TrackHuman.update: normal error: %s" % str( err ) );
                pass
            self.id = -1;
        if( self.idX != -1 ):
            try:
                print( "DBG: stopAllMoves: stopping move task idX: %d" % ( self.idX ) );
                self.motion.stop( self.idX );
            except BaseException, err:
                print( "DBG: abcdk.TrackHuman.update: normal error: %s" % str( err ) );
                pass
            self.idX = -1;
        if( self.idY != -1 ):
            try:
                print( "DBG: stopAllMoves: stopping move task idY: %d" % ( self.idY ) );                
                self.motion.stop( self.idY );
            except BaseException, err:
                print( "DBG: abcdk.TrackHuman.update: normal error: %s" % str( err ) );
                pass
            self.idY = -1;
        if( self.idTrunk != -1 ):
            try:
                print( "DBG: stopAllMoves: stopping move task idTrunk: %d" % ( self.idTrunk ) );                                
                self.motion.stop( self.idTrunk );
            except BaseException, err:
                print( "DBG: abcdk.TrackHuman.update: normal error: %s" % str( err ) );
                pass
            self.idTrunk = -1;    
    # stopAllMoves - end                

    def pause( self, bState = True ):
        """
        put a tracking in a sleep state, but ready to relaunch
        If you pause it twice, you need to unpause it twice too!
        """
        while( self.mutex.testandset() == False ):
            print( "INF: abcdk.TrackHuman.pause: already pausing, waiting..." );
            time.sleep( 0.1 );        
        if( bState ):
            self.nNbrPaused += 1;
        else:
            if( self.nNbrPaused == 0 ):
                print( "WRN: abcdk.TrackHuman.pause(False): already unpaused" );
                self.mutex.unlock();
                return; # nothing to do !
            self.nNbrPaused -= 1;
        if( self.nNbrPaused == 1 ):
            self.tryToPauseExtractor( True );
        elif( self.nNbrPaused == 0 ):
            self.tryToPauseExtractor( False );
        self.mutex.unlock();
    # pause - end
    
    def resume( self ):
        """
        Resume after some pausing
        """
        self.pause( False );
    # resume - end
    
    def getFaceVariableMemoryName(self):
        return  ["Tracking/NoFace", "Tracking/FaceSeen", "Tracking/FaceAnalysed","Tracking/FaceRecognised"];
    
    def update( self, faceInfos, bTrackFace = True, bLaunchFaceRecognition = False, rFaceRecognitionThreshold = 0.82, bInhibateRecognisedWhenHeadHasMovedSinceAcquisition = True, bAnimateLed = True, bUseSoundLocalisation = False, bEnableRandomMoves = False ):
        """
        update position
        faceInfos: data get from ALFaceDetction
        - bEnableRandomMoves: when set: if not faces are found, the robot is moving randomly (so we hope we found something)
        return 
            following seems OUTDATED !!!
            - None if no face found
            - True if a face have been found.
            - if face reco is on, you can receive that too:
                - [[name, confidence, position in image, headPosition at taking]] with name that could be "unknown" if it's sure its' an unknown people
                
            raise also info in:
                - Tracking/NoFace: analyse doesn't find any face
                - Tracking/FaceSeen: when seen but without analysed
                - Tracking/FaceAnalysed: when seen and analysed
                - Tracking/FaceRecognised: when recognised
                - Tracking/FacePosition: everytime a face is locked (quite equal to: Tracking/FaceSeen, but a bit more often)
        """
        #~ print( "ENTERING UPDATE   " * 10 );
        self.debug( "\n\nDBG: INF: abcdk.TrackHuman.update: in with faceInfos: %s" % str( faceInfos ) );
        #self.debug( "DBG: INF: abcdk.TrackHuman.update: bSoundLocalisationIsRunning: %s" % str( self.bSoundLocalisationIsRunning ) );
        
        humanInfo = facerecognition.faceMemory.updateSeen( faceInfos );
        if humanInfo != None:  self.debug( "DBG: INF: abcdk.TrackHuman.update: humanInfo: %s" % str( humanInfo ) );
        if( humanInfo == None ):
            self.mem.raiseMicroEvent( "Tracking/NoFace",  [time.time(), None] );
        else:
            if( len(humanInfo) == 3 ):
                print( "INF: abcdk.tracking.update: output face pos: %s" % humanInfo );
                face_x,face_y,face_h = humanInfo;
                self.mem.raiseMicroEvent( "Tracking/FaceSeen",  [time.time(), humanInfo] );
            else:
                face_id, recognized_id, avg_age, avg_gender,face_x,face_y,face_h = humanInfo;            
                
                if( recognized_id == "" ):
                    print( "INF: abcdk.tracking.update: output age et genre: %s" % humanInfo );
                    self.mem.raiseMicroEvent( "Tracking/FaceAnalysed",  [time.time(),humanInfo ] );
                else:
                    print( "INF: abcdk.tracking.update: output recognized '%s': %s" % (recognized_id, humanInfo) );
                    self.mem.raiseMicroEvent( "Tracking/FaceRecognised",  [time.time(), humanInfo ] );
                
            self.mem.raiseMicroEvent( "Tracking/FacePosition",  [time.time(), [face_x,face_y,face_h] ] );
        
        retValue = None;
        if( self.bInUpdate ):
            print( "INF: abcdk.TrackHuman.update: Skipping faces..." );
            return retValue;
        
        if( self.bMustStop ):
            return retValue;

        self.bInUpdate  = True;

        if( humanInfo == None or humanInfo == [] ):
            # Warning Here: not again armored ! seems it is now !
            if( bUseSoundLocalisation and time.time() - self.timeLastHumanSeen > 3. and not self.bSoundLocalisationIsRunning ):
                print("DBG: abcdk.TrackHuman.update: SoundLocalization - start" );
                self.bSoundLocalisationIsRunning = True;
                self.sl.subscribe( self.getName() );
                self.sl.setParameter( "Sensibility", 0.9 ); # restore default parameter
            elif( time.time() - self.timeLastHeadMove > 5. and self.bTrackFace ):
                # (re)center head or move randomly
                self.timeLastHeadMove = time.time();
                if( self.id != -1 ):
                    try:
                        self.motion.stop( self.id );
                    except BaseException, err:
                        print( "DBG: abcdk.TrackHuman.update: normal error: %s" % str( err ) );
                        pass
                arPos = [0.,0.];
                rSpeed = 0.04;
                rDist = 3.; # regarde au loin
                if( bEnableRandomMoves and random.random() > 0.6 ): # return to zero a bit often
                    rYawMax = 1.;
                    if( system.isOnRomeo() ):
                        rYawMax *=0.7;
                    rPitchMax = 0.3;
                    rPitchOffset = -0.4;
                    rValYaw = random.uniform( -rYawMax , rYawMax );                    
                    rValPitch = rPitchOffset + random.uniform( -rPitchMax , rPitchMax  );
                    arPos = [ rValYaw, rValPitch ];
                    rSpeed = random.random()*0.04 + 0.002; # we could move slowly
                    rDist = random.random() + 0.5; # regarde a une distance aléatoire
                    print( "DBG: abcdk.TrackHuman.update: random move to %s at speed %f" % (str( arPos ), rSpeed ) );
                bMoveHead = True;
                if( self.bTrackWithEyes ):
                    print( "DBG: abcdk.TrackHuman.update: raz eyes (or random moves)..." );
                    self.eyesMover.moveLeft( arPos, rTime = 0.4, rDist = rDist, bWaitEnd = False );                    
                    bMoveHead = random.random() > 0.5;
                if( bMoveHead ):
                    print( "DBG: abcdk.TrackHuman.update: raz head or random moves" );
                    print( "**" * 50 );
                    if( self.idX != -1 ):
                        try:
                            self.motion.stop( self.idX );
                        except BaseException, err:
                            print( "DBG: abcdk.TrackHuman.update: normal error: %s" % str( err ) );
                            pass
                        self.idX = -1;
                    if( abs(arPos[1]) < 0.01 ):
                        arPos[1] += -0.2;  # we should look a bit higher TODO: it should be a parameter! (-0.45 for wien, and -0.2 for standard one)
                    if( self.bTrackUsePitch ):
                        if( len(self.headChain) > 2 ):
                            arPos.append( arPos[1]*self.rPitchRatioThruJoint[0]);
                            arPos[1] *= self.rPitchRatioThruJoint[1];
                        self.idX = self.motion.post.angleInterpolationWithSpeed( self.headChain, arPos, rSpeed ); # using setAngles is unstoppable!
                        self.idY = self.idX; # patch: even if we want to move only the X, we should stop both
                    else:
                        self.idX = self.motion.post.angleInterpolationWithSpeed( self.headChain[0], arPos[0], rSpeed );
                    print( "random moves task id: x: %d, y: %d" % ( self.idX, self.idY ) );
                    if( random.random() > 0.8 and self.bUseTrunk ):
                        print( "DBG: abcdk.TrackHuman.update: raz trunk..." );
                        if( self.idTrunk != -1 ):
                            try:
                                self.motion.stop( self.idTrunk );
                            except BaseException, err:
                                print( "DBG: abcdk.TrackHuman.update: normal error: %s" % str( err ) );
                                pass
                            self.idTrunk = -1;
                        
                        self.idTrunk = self.motion.post.angleInterpolationWithSpeed( "TrunkYaw", 0., rSpeed );
        
            self.bInUpdate  = False;
            return retValue;
            
            
        if( self.bSoundLocalisationIsRunning ):
            self.bSoundLocalisationIsRunning = False;            
            print("DBG: abcdk.TrackHuman.update: SoundLocalization - stop" );           
            self.sl.unsubscribe( self.getName() );

        retValue = True;            
        self.timeLastHumanSeen = time.time();
        self.timeLastHeadMove = time.time();        
        # if we're here, we've seen someone
        # print("someone");
        if( bTrackFace ):
            
            rMoveX = 0.5*face_x;
            rMoveY = 0.5*face_y;
            
            if( system.isOnRomeo() ):
                leds.dcmMethod.setMouthColor( color = [0xFFFFFF,0x00FFF00,0xFFFFFF], rTime = 0.05 );
                leds.dcmMethod.setMouthColor( color = [0x404040,0x404040,0x404040], rTime = 1. );
            
            aAngleToPutToHead = [rMoveX,rMoveY];
            bTooSmall = abs(aAngleToPutToHead[0]) < self.rThresholdToMove and abs(aAngleToPutToHead[1]) < self.rThresholdToMove;
            print( "aAngleToPutToHead[0]: %s, aAngleToPutToHead[1]: %s" % ( aAngleToPutToHead[0],aAngleToPutToHead[1] ) )
            if( bTooSmall ):
                print( "stop fix ? last:%s" % self.timeLastMoveToFix );
                if( time.time() - self.timeLastMoveToFix > 5. ):
                    print( "stop fix! " * 20 );
                    if( random.random() > 0.5 ):
                        nSign0 = -1;
                    else:
                        nSign0 = 1.;
                    if( random.random() > 0.5 ):
                        nSign1 = -1;
                    else:
                        nSign1 = 1.;                        
                    aAngleToPutToHead[0] = 0.08*nSign0; # will generate a small look to the ground # must be bigger than rLimitToMove # now, random direction
                    aAngleToPutToHead[1] = 0.08*nSign1; 
            
            if( self.bTrackWithEyes ):
                bTooSmall = abs(aAngleToPutToHead[0]) < self.rThresholdToMove and abs(aAngleToPutToHead[1]) < self.rThresholdToMove;        
                if( not bTooSmall ):
                    aCurPos = self.eyesMover.getPos();
                    print( "aCurPosEyes: %s" % aCurPos );
                    rCoefSmoothMore = 0.5; # the eyes are more sensitive, so we must smooth more (or less...)
                    aAngleMoves = [0.,0.];                    
                    aAngleMoves[0] = aCurPos[0]-aAngleToPutToHead[0];
                    aAngleMoves[1] = aCurPos[1]+rCoefSmoothMore*aAngleToPutToHead[1];
                    #~ print( "rect3: %f centred3: %f" % (rect[3], aCentred[3]) );
                    rDist = 0.31/face_h; # size in image to distance (approx on a medium sized face)
                    rTime = 0.2;                    

                    # inhibate some axis ?
                    for i in range(2):
                        if( self.abLastFrameFastMove[i] ):
                            # inhibate this axis
                            print( "DBG: abcdk.TrackHuman.update: axis %d was inhibitate" % i );
                            self.abLastFrameFastMove[i] = False;
                            aAngleMoves[i] = aCurPos[i];
                            aAngleToPutToHead[i] = 0.;
                        else:
                            if(abs(aAngleToPutToHead[i]) > 0.1 ):
                                print( "DBG: abcdk.TrackHuman.update: axis %d does a fast moves (inhibate next face position)" % i );
                                self.abLastFrameFastMove[i] = True;                            

                    # transfer eyes pos to head
                    if( 1 ):
                        for i in range(2):
                            if( abs( aAngleMoves[i] ) > 0.25 ):
                                # transfer moves to head instead of eyes
                                if( i == 0 ):
                                    aAngleToPutToHead[i] = -aAngleMoves[i];
                                else:
                                    aAngleToPutToHead[i] = +aAngleMoves[i];
                                aAngleMoves[i] = aCurPos[0]/2;
                            else:
                                aAngleToPutToHead[i] = 0.;

                            
                    print( "aAngleMoves: %s" % aAngleMoves );
                    self.stopAllMoves();
                    self.eyesMover.moveLeft(  aAngleMoves, rTime = rTime, rDist = rDist, bRelative = False, bWaitEnd = False );
                    self.timeLastMoveToFix = time.time();                    
                    
            bTooSmall = abs(aAngleToPutToHead[0]) < self.rThresholdToMove and abs(aAngleToPutToHead[1]) < self.rThresholdToMove;        
            if( not bTooSmall ):
                #yawTrue = self.motion.getAngles( "NeckYaw", True );
                #yawFalse = self.motion.getAngles( "NeckYaw", False );
                #print( "yawTrue: %s, yawFalse: %s" % (yawTrue, yawFalse) );
                #arHeadPose = self.motion.getAngles( self.headChain, True );
                arHeadPose = self.motion.getAngles( self.headChain, False ); # 2015-07-10 Alma: bug in NeckYaw Sensor reading: so we read the order, as it's more precise... TODO: remove this line
                
                aAngleToPutToHead[0] = -aAngleToPutToHead[0];  # 2015-05-21 Alma: invertion du -aAngleToPutToHead en +aAngleToPutToHead, because it's inverted...
                print( "***" * 42 );
                
                print( "arHeadPose: %s" % arHeadPose );
                print( "aAngleToPutToHead: %s" % aAngleToPutToHead );
                rNewPosX = arHeadPose[0]+aAngleToPutToHead[0]*self.rAmortiHeadX;
                print( "rNewPosX: %s" % rNewPosX );
                if( self.idX != -1 ):
                    #~ print( "stopping moves task id: x: %d" % ( self.idX ) );
                    try:
                        self.motion.stop( self.idX );
                    except BaseException, err:
                        print( "DBG: abcdk.TrackHuman.update: normal error: %s" % str( err ) );
                        pass
                    self.idX = -1;                
                self.idX = self.motion.post.angleInterpolationWithSpeed( self.headChain[0], rNewPosX, self.rSpeedTrackX );
                print( "rNewPosX: %s" % rNewPosX );
                
                # transfer head pos X to trunk
                if( abs(rNewPosX) > 0.3 and self.bUseTrunk ):
                    if( self.idTrunk != -1 ):
                        try: self.motion.stop( self.idTrunk );
                        except: pass
                        self.idTrunk =-1;
                    strJointName = "TrunkYaw";
                    rCurPose = self.motion.getAngles( strJointName, True )[0];
                    rNewPos = rCurPose-rNewPosX*0.7;
                    rMaxYaw = 0.5;
                    if( rNewPos > rMaxYaw ):
                        rNewPos = rMaxYaw;
                    if( rNewPos < -rMaxYaw ):
                        rNewPos = -rMaxYaw;                        
                    print( "DBG: abcdk.TrackHuman.update: transfer head pos to trunk: rNewPosX: %s, rNewPos: %s" % (rNewPosX,rNewPos) );                        
                    self.idTrunk = self.motion.post.angleInterpolationWithSpeed( strJointName, rNewPos, 0.03 );
                        
                # track on Y
                if( abs(aAngleToPutToHead[1]) > 0.05 and self.bTrackUsePitch ):
                    if( self.idY != -1 ):
                        #~ print( "stopping moves task id: y: %d" % ( self.idY ) );
                        try: 
                            self.motion.stop( self.idY );
                        except BaseException, err:
                            print( "DBG: abcdk.TrackHuman.update: normal error: %s" % str( err ) );
                            pass

                        self.idY =-1;
                    rNewPosY = arHeadPose[1]+aAngleToPutToHead[1]*0.5;
                    if( len(self.rPitchRatioThruJoint) > 1 ):
                        aPitchPosToSend = [rNewPosY*self.rPitchRatioThruJoint[0],rNewPosY*self.rPitchRatioThruJoint[1]]
                    else:
                        aPitchPosToSend = rNewPosY
                    self.idY = self.motion.post.angleInterpolationWithSpeed( self.headChain[1:], aPitchPosToSend, self.rSpeedTrackY );
                self.timeLastMoveToFix = time.time();
            else:
                if( random.random() > 0.6 and system.isOnRomeo() ):
                    # reduce extreme trunkYaw
                    arYaw = self.motion.getAngles( ["TrunkYaw",self.headChain[0]], True );
                    print( "arYaw: %s" % arYaw );
                    if( abs(arYaw[0]) > 0.2 and abs(arYaw[1]) < 0.3 or (arYaw[0]*arYaw[1])>0.): # if both are in the same sign, then they go in different direction
                        if( self.idTrunk != -1 ):
                            try: self.motion.stop( self.idTrunk );
                            except: pass
                            self.idTrunk =-1;                        
                        self.idTrunk = self.motion.post.angleInterpolationWithSpeed( "TrunkYaw", arYaw[0]/2, 0.02 );
            
        #~ self.resume();
        self.bInUpdate = False;
        return retValue;
    # update - end
    
    def updateSound( self, pValue ):
        """
        At some moment, we decide to launch sound localisation, so we're receiving info there
        """
        if( pValue[1][2] > .5 ): # confidence (should be a parameter)
            if( self.id != -1 ):
                try:
                    self.motion.stop( self.id );
                except BaseException, err:
                    print( "DBG: abcdk.TrackHuman.updateSound: normal error: %s" % str( err ) );
                    pass
            self.timeLastHeadMove = time.time();
            # triming
            rCurrentYaw, rCurrentPitch = self.motion.getAngles( "Head", True );
            if( pValue[1][0] + rCurrentYaw > + self.rTrackYawLimit ):
                print( "DBG: abcdk.TrackHuman.updateSound: limit left");
                pValue[1][0] = self.rTrackYawLimit - rCurrentYaw;
            elif( pValue[1][0] + rCurrentYaw < - self.rTrackYawLimit ):
                print( "DBG: abcdk.TrackHuman.updateSound: limit right");
                pValue[1][0] = - self.rTrackYawLimit - rCurrentYaw;
            aAngles = [ pValue[1][0],pValue[1][1] ]; # get position
            print( "INF: abcdk.TrackHuman.updateSound: moving to %s" % str( aAngles ) );
            if( self.bTrackWithEyes ):
              self.eyesMover.moveLeft(  aAngles, bRelative = True, bWaitEnd=False );
            else:
                if( self.bTrackUsePitch ):
                    self.id = self.motion.post.changeAngles( "Head", aAngles, self.rTrackSpeed );
                else:
                    self.id = self.motion.post.changeAngles( "HeadYaw", aAngles[0], self.rTrackSpeed );        
    # updateSound - end
    
    def start2( self, bTrackFace = True, bLaunchFaceRecognition = False, rFaceRecognitionThreshold = 0.82, bInhibateRecognisedWhenHeadHasMovedSinceAcquisition = True, bAnimateLed = True, bUseSoundLocalisation = False, bEnableRandomMoves = True ):
        """
        like start, but handle the callback
        """
        self.bMustStop = False;
        
        if( not naoqitools.isVariableInMemory( self.strFaceDetectMemoryName, self.strMemoryVideoName ) ):
            self.memVideo.raiseMicroEvent( self.strFaceDetectMemoryName, [] );
        if( not naoqitools.isVariableInMemory( self.strSoundLocalisedMemoryName, self.strMemoryVideoName ) ):
            self.memVideo.raiseMicroEvent( self.strSoundLocalisedMemoryName, [] );
        naoqitools.subscribe( self.strFaceDetectMemoryName, "abcdk.tracking.trackHuman.onFaceDetected" );
        naoqitools.subscribe( self.strSoundLocalisedMemoryName, "abcdk.tracking.trackHuman.onSoundLocalised" );

        self.bTrackFace = bTrackFace;        
        self.bLaunchFaceRecognition = bLaunchFaceRecognition = 0.82, 
        self.rFaceRecognitionThreshold = rFaceRecognitionThreshold
        self.bInhibateRecognisedWhenHeadHasMovedSinceAcquisition = bInhibateRecognisedWhenHeadHasMovedSinceAcquisition
        self.bAnimateLed = bAnimateLed
        self.bUseSoundLocalisation = bUseSoundLocalisation
        self.bEnableRandomMoves = bEnableRandomMoves
        
        self.start();
    # start2 - end
        
    def stop2( self ):
        """
        stop a start2
        """
        try:
            naoqitools.unsubscribe( self.strFaceDetectMemoryName, "abcdk.tracking.trackHuman.onFaceDetected" );
            naoqitools.unsubscribe( self.strSoundLocalisedMemoryName, "abcdk.tracking.trackHuman.onSoundLocalised" );        
        except: pass
        
        self.stop();
        
    def onFaceDetected( self, varname, value ):
        #print( "DBG: abcdk.tracking.onFaceDetected: %s: %s" % (varname, value) );
        import traceback
        try:
            self.update( value, bTrackFace = self.bTrackFace, bLaunchFaceRecognition = self.bLaunchFaceRecognition, rFaceRecognitionThreshold = self.rFaceRecognitionThreshold, bInhibateRecognisedWhenHeadHasMovedSinceAcquisition = self.bInhibateRecognisedWhenHeadHasMovedSinceAcquisition, bAnimateLed = self.bAnimateLed, bUseSoundLocalisation = self.bUseSoundLocalisation, bEnableRandomMoves = self.bEnableRandomMoves )
        except Exception as e:
            print(traceback.format_exc())
        
    def onSoundLocalised( self, varname, value ):        
        print( "DBG: abcdk.tracking.onSoundLocalised: %s: %s" % (varname, value) );
        self.updateSound( value );

    
    def setDebugMode( self, bNewState = True ):
        """
        Activate (or deactivate) debug mode and printing
        bNewState: True: activate them or False: deactivate them
        """
        if( not self.bUseNativeExtractor ):
            if( self.extractor == None ):
                print("INF: abcdk.TrackHuman.setDebugMode: creating proxy to HaarExtractor..." );
                try:
                    self.extractor = loadFaceDetectorModule();
                except: pass
            if( self.extractor != None ):
                self.extractor.setDebugMode( bNewState );
        self.bDebugMode = bNewState;
    # setDebugMode - end
    

# class TrackHuman - end

trackHuman = TrackHuman();

def autoTest_trackHuman():
    import config
    config.strDefaultIP="198.18.0.1";
    test.activateAutoTestOption();
    trackHuman.start( 2. );
    time.sleep( 5. );
    trackHuman.update(  [[[396, 100, 110, 110], 28, [-0.009245872497558594, -0.0031099319458007812], '/tmp/2011_12_04-14h40m33s0393ms_00.jpg']] );
    trackHuman.pause(True);
    time.sleep( 2. );
    trackHuman.pause(False);
    time.sleep( 5. );
    trackHuman.stop();
    
def autoTest_trackObject():    
    pass
    
class Tracker:
    """
    Track an object/human/stuffs on any kind of robots
    """
    def __init__(self):
        self.bEyesTrack = False;        
        if( system.isOnRomeo() ):
            self.bEyesTrack = True;
            self.eyesMover = motiontools.eyesMover;
        self.reset();
        
    def reset(self):
        self.idHeadYaw = -1;
        self.idTrunkYaw = -1;
        self.idHeadPitch = -1;
        self.idNeckPitch = -1;
        self.rLastDistance = -1;
        
        
    def update( self, arPos3D, rTime ):
        """
        update the position to look at - non blocking method
        - arPos3D: the position [x,y,d] to look at: 
            - x and y: angle in the head space,  (relative to the current head position) [-1., 1.]
            - d: distance to Robot in meter
            None when unknown
        - rTime: time to use to track
        """
        if( self.bEyesTrack ):
            rApprox = 0.01;
            if( abs(arPos3D[0]) < rApprox and abs(arPos3D[1]) < rApprox and (self.rLastDistance - arPos3D[2]) < 0.1 ):
                return;
            # send eyes command
            aEyePosition = self.eyesMover.getPosition();
            #if( eye hors limite, faire autre chose!
            self.eyesMover.moveLeft( arPos3D, rTime = rTime, rDist = arPos3D[2], bWaitEnd = False );
            
        
        # track avec la tete
        rApprox = 0.05;
        if( abs(arPos3D[0]) < rApprox and abs(arPos3D[1]) < rApprox ):
            return;
        chain = ["HeadYaw", "HeadPitch"]
        arPose = self.motion.getAngles( chain, True );
        if( self.idX != -1 ):
            self.motion.stop( self.idX );
            self.idX =-1;
        #print( "send order1" );

        self.idX = self.motion.post.angleInterpolationWithSpeed( chain[0], arPose[0]-p[0]*0.5, 0.2 );
        if( False ):
#        if( abs(p[0]) > 0.5 ):
            if( self.idTrunk != -1 ):
                self.motion.stop( self.idTrunk );
                self.idTrunk =-1;
            self.idTrunk = self.motion.post.angleInterpolationWithSpeed( chain[0], p[0]*0.5, 0.1 );
        #print( "send order2" );
        if( abs(p[1]) > 0.1 ):
            if( self.idY != -1 ):
                self.motion.stop( self.idY );
                self.idY =-1;
            self.idY = self.motion.post.angleInterpolationWithSpeed( chain[1], arPose[1]+p[1]*0.5, 0.2 );        
        
        
    # update - end

def autoTest():
    autoTest_trackHuman();
# autoTest - end

if( __name__ == "__main__" ):
    autoTest();