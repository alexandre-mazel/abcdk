# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Romeo tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Romeo tools"

import datetime
import filetools
import motiontools
import naoqitools
import system

import math
import numpy
import os
import time

#~ global_romeo_ip
#~ def setRomeoIP( strIP ):
    #~ """
    #~ """

    

def getCameraGroup( bUseFuse = True ):
    """
    get the current active camera group    
      0: forehead
      1: eyes
    """
    try:
        if( bUseFuse ):
            strCommand = "cat /tmp/fuse/BusUSBRomeo/FaceBoard/FaceBoard.CameraSwitch";
            strCommand = "ssh nao@198.18.0.3 \"%s\"" % strCommand;
            buf = system.executeAndGrabOutput( strCommand )
            if( buf[0] == '1' ):
                return 1;
            return 0;
        else:
            mem = naoqitools.myGetProxy( "ALMemory" );
            return int( mem.getData( "Device/SubDeviceList/FaceBoard/CameraSwitch/Value" ) );
    except Exception, err:
        print( "ERR: abcdk.romeo.getCameraGroup: error: %s" % err );
    return -1;
# getCameraGroup - end

def setCameraGroup( nGroupNumber, bUseFuse = True ):
    """
    set the current active camera group    
    - nGroupNumber:     
      0: forehead
      1: eyes
    """
    if( nGroupNumber < 0 or nGroupNumber > 1 ):
        print( "ERR: abcdk.romeo.setCameraGroup: bad group number: %s" % nGroupNumber );
        return False;
    rGroupNumber = float( nGroupNumber );
    try:
        if( not bUseFuse ):
            # this part of code isn't currently working
            dcm = naoqitools.myGetProxy( "DCM_video" );
            dcm.set( ["FaceBoard/CameraSwitch/Value", "Merge",  [[rGroupNumber, dcm.getTime( 0 ) ]] ] );
        else:
            strCommand = "echo %s > /tmp/fuse/BusUSBRomeo/FaceBoard/FaceBoard.CameraSwitch" % rGroupNumber;
            strCommand = "ssh nao@198.18.0.3 \"%s\"" % strCommand;
            print( "WRN: abcdk.romeo.setCameraGroup: Launching this command: '%s'" % strCommand );
            os.system( strCommand );
            
            # auto flipping
            #~ if( nGroupNumber == 0 ):
                #~ aFlipConfig = 
            #~ else:
            #~ # flip all camera:
            #~ for i in range(2):
                
    except Exception, err:
        print( "ERR: abcdk.romeo.setCameraGroup: error: %s" % err );    
    return True;
# setCameraGroup - end


def switchCamera( nGroupNumber = -1 ):
    """
    switch between forehead and eyes
    """
    nCurrent = getCameraGroup();
    nCurrent = ( nCurrent + 1 ) % 2;
    setCameraGroup( nCurrent );
# switchCamera - end

def moveTrunkYawWithSpeed( rPos, rSpeedAmount = 0.2, bRelative = False ):
    """
    Dedicated method to avoid the vibration of the joint while he's not moving
    """
    print( "%s: INF: abcdk.romeo.moveTrunkYawWithSpeed: moving trunk yaw to %5.3f at speed %s" % ( time.time(), rPos, rSpeedAmount ) );
    strJoint = "TrunkYaw";
    motion = naoqitools.myGetProxy( "ALMotion" );
    rCurPos = motion.getAngles( strJoint, True )[0];
    if( bRelative ):
        rPos += rCurPos;
    if( abs(rPos) > 0.6 ):
        return; # at the maximum, do nothing!
    if( abs(rPos - rCurPos) < 0.1 ):
        return; # same pos => nothing

    print( "%s: INF: abcdk.romeo.moveTrunkYawWithSpeed: sending movement to positiong: %5.3f" % ( time.time(), rPos ) );
    motion.setStiffnesses( strJoint, 0.5 );
    motion.angleInterpolationWithSpeed( strJoint, rPos, rSpeedAmount );
    time.sleep( 0.1 ); # wait for a real end
    motion.post.setStiffnesses( strJoint, 0.0 ); # suppress vibration    
# moveTrunkYawWithSpeed - end
    

class BodyFromEyesMover:
    """
    Move the upper body relatively to the eyes movement
    """
    def __init__( self ):    
        self.motion = None;
        self.bUsePitch = False;
        self.taskIDY = -1;
        self.taskIDP = -1;


    def start( self ):    
        self.motion = naoqitools.myGetProxy( "ALMotion" );
        self.bUsePitch = False;
        
        self.listJoint = ["NeckYaw", "NeckPitch"];
        for strJoint in self.listJoint:
            self.motion.setStiffnesses( strJoint, 1. );
            self.motion.angleInterpolationWithSpeed( strJoint, 0., 0.1 );

        self.eyesMover = motiontools.eyesMover;
        print( "INF: abcdk.romeo.BodyFromEyesMover.start: using eyesmover: %s!" % self.eyesMover );
        self.reset();
    # start - end
        
    def reset( self ):
        self.eyesMover.moveLeft( [0., 0.] );
        self.taskIDY = self.motion.post.angleInterpolationWithSpeed( self.listJoint[0], 0., 0.02 );
        self.taskIDP = self.motion.post.angleInterpolationWithSpeed( self.listJoint[1], 0., 0.02 );
        moveTrunkYawWithSpeed( 0, 0.05, bRelative = False );
        self.aEyePosPrev = [-1.,-1.]
        self.rTimeEyeLastMove = time.time();
    # reset - end
        
    def update( self ):
        #aEyePos = eyesMover.getPos(); # $$$$ a trouver un jour !
        aEyePos = motiontools.getEyesPosition();
        #print( "eyes pos: %s" % aEyePos );
        
        if( abs(self.aEyePosPrev[0] - aEyePos[0] ) < 0.1 and abs(self.aEyePosPrev[1] - aEyePos[1] ) < 0.1 ):
            # eyes are at the same position, 
            if(  time.time() - self.rTimeEyeLastMove < 1. ):
                print( "%s: INF: abcdk.romeo.BodyFromEyesMover.update: eyes are not moving, time last move: %s" % (time.time(), self.rTimeEyeLastMove ) );
                return;
        else:
            print( "%s: INF: abcdk.romeo.BodyFromEyesMover.update: eyes are moving..." % time.time() );
            self.rTimeEyeLastMove = time.time();
            self.aEyePosPrev = aEyePos;
            return;
            
        self.aEyePosPrev = aEyePos;
        # self.rTimeEyeLastMove = time.time();


        print( "%s: INF: abcdk.romeo.BodyFromEyesMover.update: thinking for a head moves..." % time.time() );
        #self.rTimeEyeLastMove = time.time();
        
        # in two passes, as our Neck Pitch isn't enough precise for small moves (loop of get/set screw everything)
        aCurrPos = self.motion.getAngles( self.listJoint, True );        
        if( abs(aEyePos[0]) > 0.08 ):
            print( "%s: INF: abcdk.romeo.BodyFromEyesMover.update: moving yaw..." % time.time() );
            if( self.taskIDY != -1 ):
                try:
                    self.motion.stop( self.taskIDY );
                except Exception, err:
                    print( "ERR: normal error: %s" % err );
            rNewPos = aCurrPos[0]+aEyePos[0]*0.2;
            if( abs( rNewPos ) > 0.7 ):
                rAngleMoveTrunk = rNewPos*0.4;
                moveTrunkYawWithSpeed( -rAngleMoveTrunk, 0.05, bRelative = True );
                self.taskIDY = self.motion.post.angleInterpolationWithSpeed( self.listJoint[0], rNewPos, 0.02 ); # put the head back a bit (in fact not, because sometimes we're at the yaw limits, so we need to continue to turn the head
            else:
                self.taskIDY = self.motion.post.angleInterpolationWithSpeed( self.listJoint[0], rNewPos, 0.1 );                
            #eyesMover.moveLeft( [0.,0.], rTime = 0.2 ); # not good
            
        if( self.bUsePitch ):
            if( abs(aEyePos[1]) > 0.4 ): # big movement only!
                print( "%s: INF: abcdk.romeo.BodyFromEyesMover.update: moving pitch..." % time.time() );
                if( self.taskIDP != -1 ):
                    try:
                        self.motion.stop( self.taskIDP );
                    except Exception, err:
                        print( "ERR: normal error: %s" % err );
                rNewPos = aCurrPos[1]-aEyePos[1]*0.2;
                self.taskIDP = self.motion.post.angleInterpolationWithSpeed( self.listJoint[1], rNewPos, 0.01 );
        
    # update - end
    
# class BodyFromEyesMover - end

class HeadStabilizer:
    """
    Stabilize the head, relatively to the Head Imu
    """
    def __init__( self, strUsePitchJoint = "HeadPitch", bUseFaceInertial = False, bVerbose = False ):
        """
        The stabilizer could use the HeadPitch or the NeckPitch (for calibration purpose)
        """
        self.mem = None;
        self.motion = None;
        self.bUseFaceInertial = bUseFaceInertial;
        if( self.bUseFaceInertial ):
            self.listValue = [ "Device/SubDeviceList/FaceBoard/AngleX/Value", "Device/SubDeviceList/FaceBoard/AngleY/Value" ];
        else:
            # the IMU hasn't the same orientation !
            self.listValue = [ "Device/SubDeviceList/InertialSensorHead/AngleY/Sensor/Value", "Device/SubDeviceList/InertialSensorHead/AngleX/Sensor/Value" ];
            
        self.taskID = -1;
        self.chain = [ "HeadRoll", strUsePitchJoint ];
        self.rOldX = 0.;
        self.rOldY = 0.;
        self.bVerbose = bVerbose;
    
    def start( self, bUsePitch = True ):
        if( self.mem == None ):
            if( self.bUseFaceInertial ):
                self.mem = naoqitools.myGetProxy( "ALMemory_video" );
            else:
                self.mem = naoqitools.myGetProxy( "ALMemory_motion" );
            self.motion = naoqitools.myGetProxy( "ALMotion" );
            self.bUsePitch = bUsePitch;

    def update( self, rRatioSpeed = 0.3 ):
        """
        return True when the position is updated. False when nothing to do
        """
        rX, rY = self.mem.getListData( self.listValue );
        
        if( self.bVerbose ):
            print( "DBG: abcdk.romeo.HeadStabilizer: rX: %s, rY: %s, rOldX: %s, rOldY: %s" % (rX, rY,self.rOldX, self.rOldY) );
        rX = self.rOldX * 0.5 + rX * 0.5;
        rY = self.rOldY * 0.5 + rY * 0.5;
        self.rOldX = rX;
        self.rOldY = rY;
        
        if( rX == None or rY == None ):
            raise( BaseException( "romeo.HeadStabilizer: can't get value from the Inertial..." ) );
        
        rThreshold = 0.05;
        bUpdated = False;
        if( abs(rX) > rThreshold or (abs(rY) > rThreshold and self.bUsePitch ) ):
            if( self.bVerbose ):
                print( "DBG: abcdk.HeadStabilizer.update: updating, rX=%5.2f, rY=%5.2f" % (rX, rY ) );
            if( self.taskID != -1 ):
                try:
                    self.motion.stop( self.taskID );
                except BaseException, err:
                    print( "DBG: abcdk.HeadStabilizer.update: normal error: %s" % str( err ) );
                    pass
            arPos = self.motion.getAngles( self.chain, True );
            if( self.bUseFaceInertial ):
                arPos[0] += -rX * 0.9;
                arPos[1] += -rY * 0.9;
            else:
                arPos[0] += +rX * 0.9;
                arPos[1] += -rY * 0.9;                # TO TEST!
            if( self.bUsePitch ):
                self.taskID = self.motion.post.angleInterpolationWithSpeed( self.chain, arPos, rRatioSpeed );
            else:
                self.taskID = self.motion.post.angleInterpolationWithSpeed( self.chain[0], arPos[0], rRatioSpeed );
            bUpdated = True;
        return bUpdated;
# class HeadStabilizer - end

class Calibrator:
    """
    Calibrate the body joints in various position
    """
    def __init__( self, strUsePitchJoint = "HeadPitch" ):
        """
        """
        self.dcm = None;
        self.aArmNameL = ["LShoulderPitch" ,"LShoulderYaw" ,"LElbowRoll" ,"LElbowYaw" ,"LWristRoll" ,"LWristYaw" ,"LWristPitch" ,"LHand"];
        self.aArmNameR = ["R" + strJoint[1:] for strJoint in self.aArmNameL];

        #  angles are in degrees
        self.aArmValue_MetallicStopL = [ -79.3, 54.95, -128.9, 0.75, -210.0, -25., 0., 1. ];
        self.aArmValue_MetallicStopR = [ -85.39, -64.94, 128.87, -0.77, +210.0, +25., 0., 1. ];
        
        self.aLegNameL = ["LHipYaw" ,"LHipRoll" ,"LHipPitch" ,"LKneePitch" ,"LAnklePitch" ,"LAnkleRoll"];
        self.aLegNameR = ["R" + strJoint[1:] for strJoint in self.aLegNameL];
        
        self.aLegValue_Calibrator = [ 0., 0., -16.02, 36.03, -20.01, 0. ];
        
        self.aDictExtraJoint = {
            "NeckYaw": 120., # a gauche
            "HeadPitch": -15.23, # en arriere # 20deg == 0.3490rad... et 15.23==0.2658rad.  Le max vers l'avant étant en 19.02° soit 0.33196rad
            "TrunkYaw": 41.85, # computed from full range on my Romeo
        };
        self.dcmEyes = None; # if set it will save the eyes calibration
        
    # __init__ - end
        
    def calibrateChain( self, listName, listRefValue ):
        """
        Return true if the joint has been calibrated
        """
        print( "INF: Calibrator.calibrateChain: calibrating chain..." );
        if( self.dcm == None ):
            self.dcm = naoqitools.myGetProxy( "DCM_motion" );
        for i in range(len(listName)):
            strJoint = listName[i];
            rPos = listRefValue[i] * math.pi / 180;
            if( "Hand" in strJoint ):
                rPos = 1.;
            print( "INF: Calibrator.calibrateChain: calibrating '%s' as value %5.2f rad" % (strJoint, rPos) );
            self.dcm.calibration(["Device/SubDeviceList/%s/Position/Actuator/Value" % strJoint,"Manual" ,"InPosition",rPos])
            time.sleep( 0.5 );
        print( "INF: Calibrator.calibrateChain: finished..." );
        return True;
    # calibrateChain - end
    
    def calibrateLeftArm_onMetallicStop( self ):
        self.calibrateChain(self.aArmNameL, self.aArmValue_MetallicStopL );
        
    def calibrateRightArm_onMetallicStop( self ):
        self.calibrateChain(self.aArmNameR, self.aArmValue_MetallicStopR );
        
    def calibrateArms_onMetallicStop( self ):
        self.calibrateLeftArm_onMetallicStop();
        self.calibrateRightArm_onMetallicStop();
        
    def calibrateJoint_onMetallicStop( self, strJointName ):
        """
        Return true if the joint has been calibrated
        """
        try:
            rPos = self.aDictExtraJoint[strJointName];            
            return self.calibrateChain( [strJointName], [rPos] );
        except BaseException, err:
            raise Exception( "calibrateJoint_onMetallicStop: Bad joint name: %s. err: %s" % (strJointName, err) );
        return False;
    # calibrateJoint_onMetallicStop - end
    
    def calibrateJoint( self, strJointName, rPos = 0. ):
        """
        Return true if the joint has been calibrated
        """
        try:
            return self.calibrateChain( [strJointName], [rPos] );
        except BaseException, err:
            raise Exception( "calibrateJoint: Unknown error while calibrating %s: %s" % (strJointName, err) );
        return False;
    # calibrateJoint - end
        
    def calibrateLegs_inCalibrator( self ):
        self.calibrateChain(self.aLegNameL, self.aLegValue_Calibrator );
        self.calibrateChain(self.aLegNameR, self.aLegValue_Calibrator );
        
    def calibrateEyes( self ):
        print( "INF: Calibrator.calibrateEyes: calibrating eyes..." );
        if( self.dcmEyes == None ):
            self.dcmEyes = naoqitools.myGetProxy( "DCM_video" );

        self.dcmEyes.calibration(["Device/SubDeviceList/FaceBoard/Position1/Actuator/Value","Manual" ,"InPosition",0])
        self.dcmEyes.calibration(["Device/SubDeviceList/FaceBoard/Position2/Actuator/Value","Manual" ,"InPosition",0])
        self.dcmEyes.calibration(["Device/SubDeviceList/FaceBoard/Position3/Actuator/Value","Manual" ,"InPosition",0])
        self.dcmEyes.calibration(["Device/SubDeviceList/FaceBoard/Position4/Actuator/Value","Manual" ,"InPosition",0])
        time.sleep( 1. );
        
    def saveCalibration( self ):
        assert( self.dcm != None or self.dcmEyes != None ); # should have calibrated some chain before !
        strPath = "/home/nao/.config/hal/";
        strPathBackup = "/media/internal/";
        strOrig = "Device_Local.xml";
        strBackupName = strOrig.replace( ".xml", "_backup.xml");
        strCopyNew = strOrig.replace( ".xml", "_" + filetools.getFilenameFromTime() + ".xml");
        # copy current to backup
        strCommand = "cp %s%s %s%s; cp %s%s %s%s" %  (strPath, strOrig, strPath, strBackupName,   strPath, strOrig, strPathBackup, strBackupName);
        if( self.dcm != None ):
            print( "INF: saving chain calibration... (a backup was made in %s)" % strBackupName );
            os.system( "ssh nao@198.18.0.4 \"%s\"" % strCommand );
            self.dcm.preferences( "Save", "Local", "", 0. );
        if( self.dcmEyes != None ):
            print( "INF: saving eyes calibration... (a backup was made in %s)" % strBackupName );
            os.system( "ssh nao@198.18.0.3 \"%s\"" % strCommand );
            self.dcmEyes.preferences( "Save", "Local", "", 0. );
        # copy new (so it will be a archived for futur use)
        strCommand = "cp %s%s %s%s; cp %s%s %s%s" %  (strPath, strOrig, strPath, strCopyNew,   strPath, strOrig, strPathBackup, strCopyNew);
        time.sleep( 20 );
# class Calibrator - end

class TactileUsingFuse:
    def __init__( self ):
        self.strKeyTemplate = "/tmp/fuse/MotherBoardI2C/TouchBoard/Head.Touch.%s.Sensor";
        self.aListArea =  ["Front", "Middle", "Rear" ];
        self.mem = None;
        self.strPathLogDirectory = "/home/nao/logs/";
        self.reset();
        
    def prepare( self ):
        filetools.makedirsQuiet( self.strPathLogDirectory )
        if( self.mem == None ):
            self.mem = naoqitools.myGetProxy( "ALMemory" );
            # create the variable in the Memory
            for i in range(3):
                self.mem.raiseMicroEvent( self.aListArea[i] + "TactilTouched", 0 );
        
        
    def reset( self ):
        self.lastState = [0]*3;
        self.bMustContinue = False;
        
    def getBrainValueFromFuse( self, bVerbose=False ):
        """
        return an array of the 3 states (0 or 1)
        """
        state = [];
        for strArea in self.aListArea:
            file = open( self.strKeyTemplate % strArea );
            bState = file.read()[0] == "1";
            if( bVerbose and bState ):
                print( "INF: TactileUsingFuse.getBrainValueFromFuse: pushed: %s" % strArea );
            state.append( bState );
            file.close();    
        return state;
        
    def update( self, bVerbose = False ):
        """
        WARNING: you should prepare before calling update!
        """
        aState = self.getBrainValueFromFuse(bVerbose=bVerbose);
        for i in range(3):
            if aState[i] != self.lastState[i]:
                self.lastState[i] = aState[i];                
                if aState[i]:
                    self.mem.raiseMicroEvent( self.aListArea[i] + "TactilTouched", 1 );
                    if( bVerbose ):
                        # log all state to some file                    
                        strTime = datetime.datetime.now().strftime("%H:%M:%S.%f")
                        strToLog = ",".join([strTime, self.aListArea[i] ]) + '\n'
                        with  open(self.strPathLogDirectory + "log_fuse_activation_tactile.txt", 'a') as fLog:
                            fLog.write(strToLog)
                            fLog.flush()
        
    def run( self, bVerbose=False ):
        """
        run loop
        """
        if( bVerbose ):
            print( "INF: TactileUsingFuse.run: starting..." );
        self.prepare();
        self.bMustContinue = True;
        while( self.bMustContinue ):
            if( bVerbose ):
                print( "INF: TactileUsingFuse: updating..." );
            self.update(bVerbose=bVerbose);
            time.sleep( 0.1 );
        # while - end
        if( bVerbose ):
            print( "INF: TactileUsingFuse.run: stopped" );
            
    def stop( self ):
        self.bMustContinue = False;
    
# class TactileUsingFuse - end


class Model:
    def __init__( self ):
        """
        for each joint an array [mecanic min/max   /   motion min/max/speed max/torque max /  Max joint speed at zero load (rad*s-1) / Three times max continuous motor current (A)]
        from the Google docs: Romeo-Limits on 15/10/2014
        """
        # automatically generated (as seen in column A0)
        #=concatenate( """", A3, """: [", B3, ",", C3, ",", T3, ",", U3, ",", V3, ",", W3, ",", P3, ",", R3, "]," )
        #
        self.dictMechanicLimit = { 
            "NeckYaw": [-2.094395102393195,2.094395102393195,-2.059488517353309,2.059488517353309,4,3.66224664312,9.777735769727803,2.793],
            "NeckPitch": [-0.349065850398866,0.698131700797732,-0.31415929484331,0.663225145242176,2.2,2.9779077978,12.024710780654246,2.793],
            "HeadPitch": [-0.265813645078736,0.331961623729322,-0.257087006189848,0.297055068173766,1.9,2.572810314624,5.984304366507524,0.591],
            "HeadRoll": [-0.523598775598299,0.523598775598299,-0.488692220042743,0.488692220042743,1.5,0.89958574485,3.889790406342498,0.591],
            "LShoulderPitch": [-1.384046096831503,2.281145332356588,-1.349139541275948,2.246238776801033,2.2,19.09451314134,5.687070374415387,2.793],
            "LShoulderYaw": [-0.611737902824012,0.959058423970884,-0.576831347268457,0.924151868415329,4,9.0307236474,12.024710780654246,2.793],
            "LElbowRoll": [-2.249729405820691,1.9390607989657,-2.214822850265135,1.904154243410144,3.7,7.40402090064,9.777735769727803,2.793],
            "LElbowYaw": [-1.557706357404939,0.013089969389957,-1.522799801849383,0.004363330501069,4,6.0204824316,12.024710780654246,2.793],
            "LWristRoll": [-3.665191429188092,0.523598775598299,-3.630284873632537,0.488692220042743,1.1,2.17699317676764,3.889798135505977,0.591],
            "LWristYaw": [-0.436332312998582,0.436332312998582,-0.401425757443027,0.401425757443027,2.26,0.86233116518208,4.364429991586034,0.2667],
            "LWristPitch": [-1.022937474593877,0.931831287639772,-0.988030919038321,0.896924732084217,3.75,0.59760068544,6.297824101772838,0.2667],
            "LHand": [-4.266806422350538,0,-4.231899866794982,-0.034906555555556,47.59,0.10783112,60.09472430919237,0.495],
            "TrunkYaw": [-0.792379480405426,0.792379480405426,-0.75747292484987,0.75747292484987,1.5,80.90158905,2.402919426957782,6.24],
            "LHipYaw": [-0.296705972839036,0.296705972839036,-0.26179941728348,0.26179941728348,0.32,9.20007784166039,0.380344607972195,0.453],
            "LHipRoll": [-0.261799387799149,0.523598775598299,-0.261799387799149,0.523598775598299,2.08989897606752,46.5972417080441,2.592873153244378,9.51],
            "LHipPitch": [-1.710422666954443,0.401425727958696,-1.65806283362111,0.401425727958696,2.08989897606752,46.5972417080441,2.592873153244378,9.51],
            "LKneePitch": [-0.030543261909901,2.007128639793479,-0.021816623021012,1.972222084237923,6,38.173930452,8.39240801789681,9.51],
            "LAnklePitch": [-0.523598775598299,0.785398163397448,-0.51487213670941,0.750491607841893,2.10332818453099,25.7623743380235,2.609534357681999,9.51],
            "LAnkleRoll": [-0.349065850398866,0.349065850398866,-0.349065850398866,0.349065850398866,2.10332818453099,25.7623743380235,2.609534357681999,9.51],
            "RHipYaw": [-0.296705972839036,0.296705972839036,-0.26179941728348,0.26179941728348,0.32,9.19997060322701,0.380349041416786,0.453],
            "RHipRoll": [-0.523598775598299,0.261799387799149,-0.523598775598299,0.261799387799149,2.08989897606752,46.5972417080441,2.592873153244378,9.51],
            "RHipPitch": [-1.710422666954443,0.401425727958696,-1.65806283362111,0.401425727958696,2.08989897606752,46.5972417080441,2.592873153244378,9.51],
            "RKneePitch": [-0.030543261909901,2.007128639793479,-0.021816623021012,1.972222084237923,6,38.173930452,8.39240801789681,9.51],
            "RAnklePitch": [-0.523598775598299,0.785398163397448,-0.51487213670941,0.750491607841893,2.10332818453099,25.7623743380235,2.609534357681999,9.51],
            "RAnkleRoll": [-0.349065850398866,0.349065850398866,-0.349065850398866,0.349065850398866,2.10332818453099,25.7623743380235,2.609534357681999,9.51],
            "RShoulderPitch": [-1.490336648277958,2.174854780910134,-1.455430092722402,2.139948225354578,2.2,19.09451314134,5.687070374415387,2.793],
            "RShoulderYaw": [-1.133416816245118,0.437379510549779,-1.098510260689562,0.402472954994223,4,9.0307236474,12.024710780654246,2.793],
            "RElbowRoll": [-1.939584397741298,2.249205807045093,-1.904677842185742,2.214299251489537,3.7,7.40402090064,9.777735769727803,2.793],
            "RElbowYaw": [-0.013439035240356,1.55735729155454,-0.004712396351467,1.522450735998985,4,6.0204824316,12.024710780654246,2.793],
            "RWristRoll": [-0.523598775598299,3.665191429188092,-0.488692220042743,3.630284873632537,1.1,2.17699317676764,3.889798135505977,0.591],
            "RWristYaw": [-0.436332312998582,0.436332312998582,-0.401425757443027,0.401425757443027,2.26,0.86233116518208,4.364429991586034,0.2667],
            "RWristPitch": [-1.02171574411748,0.933053018116168,-0.986809188561925,0.898146462560613,3.75,0.59760068544,6.297824101772838,0.2667],
            "RHand": [-4.266806422350538,0,-4.26680642235054,0,47.59,0.10783112,60.09472430919237,0.495],
        };
        
        # hand patch on the fly:
        for strHand in ["LHand", "RHand"]:
            self.dictMechanicLimit[strHand][1] = -self.dictMechanicLimit[strHand][0];
            self.dictMechanicLimit[strHand][0] = 0.;
            # on fait quoi pour les limites motion ? on met 0..1
            #~ self.dictMechanicLimit[strHand][3] = -self.dictMechanicLimit[strHand][0];
            #~ self.dictMechanicLimit[strHand][0] = 0.;
    # __init__ - end
    
    def getLimits( self, strJointName ):
        """
        cf dictMecanicLimit
        """
        return self.dictMechanicLimit[strJointName];        
    # getLimits - end
# class Model - end
        
model = Model();

def setToeLock( state ):
    """
    lock or unlock the toe
    state: a value (True: locked) or an array of value [LeftToeState, RightToeState]
    """
    astrSide =  ["L", "R"];
    if( isinstance( state, int ) or isinstance( state, float ) ):
        state = [state] * 2;
    strCommandTemplate = "echo %s > /tmp/fuse/BusRS485Romeo1/%sToeBoard/%sToeBoard.MotorPosition.Actuator"; #TODO: change le romeo1 selon side
    strCommand = "";
    for i in range( 2 ):
        strCommand += strCommandTemplate % (state[i],astrSide[i],astrSide[i]);
        if( i == 0 ):
            strCommand += ";";
    strCommand = "ssh nao@198.18.0.4 \"%s\"" % strCommand;
    print( "WRN: abcdk.romeo.setToeLock: Launching this command: '%s'" % strCommand );
    os.system( strCommand );
# setToeLock - end

def setMicroAmplificationSettings():
    print( "INF: setMicroAmplificationSettings: setting 0xb039" );
    os.system( "ssh nao@198.18.0.2 /home/nao/hda-verb /dev/snd/hwC0D0 0x0C SET_AMP_GAIN_MUTE 0xb039; /home/nao/hda-verb /dev/snd/hwC0D0 0x0D SET_AMP_GAIN_MUTE 0xb039" );
# setMicroAmplificationSettings - end

dispatchEyesCommand_bMustStop = False
def dispatchEyesCommand( rUpdateTime = 0.01, bVerbose=False ):
    """
    patch to handle eyes from atom motion to video:
    - dispatch order from motion.motion to video.dcm
    - send current eyes position from video.memory to ???
    """
    # TODO: cut in two part, one running on motion board, and the other on video board
    global dispatchEyesCommand_bMustStop
    dispatchEyesCommand_bMustStop = False;
    print( "INF: dispatchEyesCommand: starting..." );
    mover = motiontools.eyesMover
    motion = naoqitools.myGetProxy( "ALMotion" )
    memory_video = naoqitools.myGetProxy( "ALMemory_video" )
    memory_motion = naoqitools.myGetProxy( "ALMemory_motion" )
    eyesJoints = ["LEyeYaw", "LEyePitch","REyeYaw", "REyePitch"];
    eyesSensorKey = [];
    eyesStiffnessKey = [];
    #~ eyesStiffnessKeySensor = [];
    for joint in eyesJoints:
        eyesSensorKey.append( "Device/SubDeviceList/%s/Position/Sensor/Value" % joint );
        eyesStiffnessKey.append( "Device/SubDeviceList/%s/Hardness/Actuator/Value" % joint );        
        #~ eyesStiffnessKeySensor.append( "Device/SubDeviceList/%s/Hardness/Sensor/Value" % joint );
    lastOrder = [];
    lastPos = [];
    nCptLoop = 10000; # a lot!
    lastStiffness = [];
    lastStiffnessSensor = [];
    while( not dispatchEyesCommand_bMustStop ):
        nCptLoop += 1;
        if( nCptLoop > 100 ):
            nCptLoop = 0;
            # read and copy stiffness
            stiffness = motion.getStiffnesses(eyesJoints);
            bEqual = numpy.allclose( stiffness, lastStiffness, atol = 0.001 )
            if( not bEqual ):
                if( bVerbose ):
                    print( "DBG: dispatchEyesCommand: update stiffness to %s" % stiffness )
                lastStiffness = stiffness;
                mover.setStiffnesses( stiffness, 0.1 );
                # TODO: test and send the invert to the motion almemory
            # stiffness value reading
            stiffnessSensor = memory_video.getListData( eyesStiffnessKey );
            #~ print( "stiffnessSensor: %s" % stiffnessSensor );
            #~ print( "lastStiffnessSensor: %s" % lastStiffnessSensor );
            bEqual = numpy.allclose( stiffnessSensor, lastStiffnessSensor, atol = 0.01 )
            if( not bEqual ):
                if( bVerbose ):
                    print( "DBG: dispatchEyesCommand: update stiffness sensor to %s" % pos )            
                #~ for i in range(len(eyesStiffnessKey)):
                    #~ memory_motion.insertData( eyesStiffnessKeySensor[i], stiffnessSensor[i] );
                motion.setStiffnesses( eyesJoints, stiffnessSensor );
                lastStiffnessSensor = stiffnessSensor;                
            
        # order
        order = motion.getAngles(eyesJoints, False);
        bEqual = numpy.allclose( order, lastOrder, atol = 0.001 )
        if( not bEqual ):
            if( bVerbose ):
                print( "DBG: dispatchEyesCommand: update order to %s" % order )
            lastOrder = order;
            mover.move( order, 0.03, bWaitEnd=False ); # should be the update time, or a slow one, or the average motion cycle: 3*10ms
            
        # pos
        pos = memory_video.getListData( eyesSensorKey );
        pos[1] = -pos[1]; # pitch invert
        pos[3] = -pos[3];
        bEqual = numpy.allclose( pos, lastPos, atol = 0.001 )
        if( not bEqual ):
            if( bVerbose ):
                print( "DBG: dispatchEyesCommand: update position to %s" % pos )            
            for i in range(len(eyesSensorKey)):
                memory_motion.insertData( eyesSensorKey[i], pos[i] );
            lastPos = pos;
        
        time.sleep( rUpdateTime );
    # end while    
    print( "INF: dispatchEyesCommand: stopped..." );
# dispatchEyesCommand - end

def dispatchEyesCommand_stop():
    global dispatchEyesCommand_bMustStop
    dispatchEyesCommand_bMustStop = True;
# dispatchEyesCommand_stop - end
    

bodyFromEyesMover = BodyFromEyesMover();
headStabilizer = HeadStabilizer();
calibrator = Calibrator();
tactile = TactileUsingFuse();

#~ # change to another flavoured version
#~ ssh root@198.18.0.1 sed -i 's~patchedNaoqi/~patchedNaoqi_2.2.xx/~g' /etc/init.d/naoqi.sh
#~ ssh root@198.18.0.2 sed -i 's~patchedNaoqi/~patchedNaoqi_2.2.xx/~g' /etc/init.d/naoqi.sh
#~ ssh root@198.18.0.3 sed -i 's~patchedNaoqi/~patchedNaoqi_2.2.xx/~g' /etc/init.d/naoqi.sh
#~ ssh root@198.18.0.4 sed -i 's~patchedNaoqi/~patchedNaoqi_2.2.xx/~g' /etc/init.d/naoqi.sh

#~ # change back
#~ ssh root@198.18.0.1 sed -i 's~patchedNaoqi_2.2.xx/~patchedNaoqi/~g' /etc/init.d/naoqi.sh
#~ ssh root@198.18.0.2 sed -i 's~patchedNaoqi_2.2.xx/~patchedNaoqi/~g' /etc/init.d/naoqi.sh
#~ ssh root@198.18.0.3 sed -i 's~patchedNaoqi_2.2.xx/~patchedNaoqi/~g' /etc/init.d/naoqi.sh
#~ ssh root@198.18.0.4 sed -i 's~patchedNaoqi_2.2.xx/~patchedNaoqi/~g' /etc/init.d/naoqi.sh
