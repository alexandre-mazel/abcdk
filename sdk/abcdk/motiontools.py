# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Motion tools
# Author: A.Mazel, L.George, ...
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Motion tools"

# this module should be called motion, but risk of masking with the official motion.py from Naoqi, since 1.816

print( "importing abcdk.motiontools" );

import math
import mutex
import time


import arraytools
import debug
import filetools
import os
import pathtools
import poselibrary
import naoqitools
import system
import test
import typetools


def getMotionBodyJointName():
    "return a list of all joint name used by Motion"
    motion = naoqitools.myGetProxy( "ALMotion" );
    return motion.getJointNames('Body');
# getMotionBodyJointName - end

def getDcmBodyJointName():
    "return a list of all joint name used by the DCM"
    listJoint = getMotionBodyJointName();
    if( "RHipYawPitch" in listJoint ):
        listJoint.remove( "RHipYawPitch" ); # when using dcm: remove this joint
        
    for strJoint in ["LEyeYaw", "LEyePitch", "REyeYaw", "REyePitch" ]:
        if strJoint in listJoint:
            listJoint.remove( strJoint );
    
    return listJoint;
# getMotionBodyJointName - end
    
def getStringTemplateActuator():
    return "Device/SubDeviceList/%s/Position/Actuator/Value";

def getStringTemplateSensor():
    return "Device/SubDeviceList/%s/Position/Sensor/Value";

def getListJoints( listGroup, bRemoveHipYawPitch = False ):
    """
    get list of joints from a group name or a list of group:
    eg: ["Head", "LHand", "RArm"] => ['HeadYaw', 'HeadPitch', 'LHand', 'RShoulderPitch', 'RShoulderRoll', 'RElbowRoll', 'RElbowYaw']
          "Head;LHand;  RArm" => idem (alternate form)
    bRemoveHipYawPitch: remove all HipYawPitch from the list
    """    
    return poselibrary.PoseLibrary.getListJoints( listGroup, bRemoveHipYawPitch );
# getListJoints - end
#print getListJoints(["Head", "LHand", "RArm"]);
#~ print getListJoints("Head;LHand;  RArm");

def getAngles( strJointOrGroups, proxyMem = None ):
    """
    get angles value from ALMemory
    - listJoints: a joint or a group of joint
    - proxyMem: alternate proxy to avoid recreation
    """
    listJoints = getListJoints( strJointOrGroups );
    if( proxyMem == None ):
        proxyMem = naoqitools.myGetProxy( "ALMemory" );
    aListSensorNameMem = [];
    for strJointName in listJoints:
        aListSensorNameMem.append( "Device/SubDeviceList/%s/Position/Sensor/Value" % strJointName );
    arActualPos = proxyMem.getListData( aListSensorNameMem );
    # put 0 instead of None
    #~ for i, val in enumerate( arActualPos ):
        #~ if( val == None ):
            #~ arActualPos[i] = 0.;
    return arActualPos;
# getAngles - end    
    

def ensureMinimalStiffness( strJointOrGroups, rNewValue ):
    """
    Ensure that the stiffness is at least of rNewValue
    strJointOrGroups: a joint or a group of joint
    """
    listJoints = getListJoints( strJointOrGroups );
    motion = naoqitools.myGetProxy( "ALMotion" );
    for joint in listJoints:
        if( motion.getStiffnesses( joint )[0] < rNewValue ):
            print( "INF: ensureMinimalStiffness: setting joint %s to %f" % ( joint, rNewValue ) );
            motion.post.setStiffnesses( joint, rNewValue );
# ensureMinimalStiffness - end


# global variable = beurk, should be in a class !

global_getNbrMoveOrder_listKeyOrder = [];
global_getNbrMoveOrder_listKeyValue = [];
global_getNbrMoveOrder_listKeyStiffness = [];
global_getNbrMoveOrder_listOrder_prev = [];

def getNbrMoveOrder( nThreshold = 0.06 ):
    "compute current joint moving by order"
    mem = naoqitools.myGetProxy( "ALMemory" );
    global global_getNbrMoveOrder_listKeyOrder;
    global global_getNbrMoveOrder_listKeyValue;
    global global_getNbrMoveOrder_listKeyStiffness;
    global global_getNbrMoveOrder_listOrder_prev;

    # first time: generate key list
    if( len( global_getNbrMoveOrder_listKeyOrder ) < 1 ):
        listJointName = getDcmBodyJointName();
        for strJointName in listJointName:
            global_getNbrMoveOrder_listKeyOrder.append( "Device/SubDeviceList/%s/Position/Actuator/Value" % strJointName );
            global_getNbrMoveOrder_listKeyValue.append( "Device/SubDeviceList/%s/Position/Sensor/Value" % strJointName );
            global_getNbrMoveOrder_listKeyStiffness.append( "Device/SubDeviceList/%s/Hardness/Actuator/Value" % strJointName );
            global_getNbrMoveOrder_listOrder_prev = mem.getListData( global_getNbrMoveOrder_listKeyOrder ); # init first time

    # get all values
    arOrder = mem.getListData( global_getNbrMoveOrder_listKeyOrder );
    arValue = mem.getListData( global_getNbrMoveOrder_listKeyValue );
    arStiffness= mem.getListData( global_getNbrMoveOrder_listKeyStiffness );

    nNbr = 0;
    for i in range( len( arOrder ) ):
        # a joint is moving if: pos is different from order, if order changed and if stiffness
        # we can have a big difference between order and value when no stiffness (position is out of range)
        if( ( abs( arOrder[i] - arValue[i] ) > nThreshold or abs( global_getNbrMoveOrder_listOrder_prev[i] - arOrder[i] ) > 0.01 ) and arStiffness[i] > 0.01 ):
            nNbr += 1;
#            debug.debug( "getNbrMoveOrder: difference on %s: order: %f; sensor: %f; stiffness: %f" % ( global_getNbrMoveOrder_listKeyValue[i], arOrder[i], arValue[i], arStiffness[i] ) );
    global_getNbrMoveOrder_listOrder_prev = arOrder;
    return nNbr;
# getNbrMoveOrder - end

# record the activity of a joint and knows if it's moving or not and the side of the move
# classe qui enregistre l'activité d'une articulation et permet de savoir si elle est en train de bouger et dans quelle sens
# elle ne va sortir un info de bougé uniquement quand c'est l'utilisateur qui la bouge, et pas si c'est Nao qui decide de bouger
# compter a peu pres 1-2% de cpu pour un update toutes les 0.3sec (a verifier, c'est pas plus, mais peut etre moins...)
class JointMove:

  def __init__( self, strJointName ):
    print( "INF: JointMove: created for '%s'" % strJointName );
    self.strJointName = strJointName;
    self.stm = naoqitools.myGetProxy( "ALMemory" );
    self.strStmJointNameSensor = "Device/SubDeviceList/" + strJointName + "/Position/Sensor/Value";
    self.strStmJointNameActuator = "Device/SubDeviceList/" + strJointName + "/Position/Actuator/Value";
    self.strStmJointNameStiffness    = "Device/SubDeviceList/" + strJointName + "/Hardness/Actuator/Value";
    self.rDiffThreshold = 0.05;
    self.reset();
  # __init__ - end

  def getJointName( self ):
    return self.strJointName;
  # getJointName - end

  # assume that joint has no stiffness or that joint is not too much stiff
  def ensureJointIsSoft( self, bTotalSoft = False ):
    rCurrentValueHardness = self.stm.getData( self.strStmJointNameStiffness, 0 );
    rMin = 0.30; # below this value, arms couldn't move to the up side.
    if( "Elbow" in self.strJointName ):
        rMin = 0.15;
    if( "Wrist" in self.strJointName ):
        rMin = 0.15;
    if( "Head" in self.strJointName ):
        rMin = 0.14;
    if( bTotalSoft ):
        rMin = 0.;
    if( system.isOnRomeo() ):
        if( "Shoulder" in self.strJointName ):
            rMin = 0.15;
        
    if( rCurrentValueHardness > rMin ):
        # this method doesn't work anymore ?
        #~ dcm = naoqitools.myGetProxy( "DCM" );
        #~ dcm.set( ["%s/Hardness/Actuator/Value" % self.strJointName, "Merge",  [[rMin, dcm.getTime( 20 ) ]] ] );
        motion = naoqitools.myGetProxy( "ALMotion" );
        motion.setStiffnesses( self.strJointName, rMin );
        
  # ensureJointIsSoft - end
  
  def setDiffThreshold( self, rNewVal ):
        "Change the diff threshold"
        self.rDiffThreshold = rNewVal;

  # start the event catching
  def start( self, bTotalSoft = False ):
    self.reset();
    self.ensureJointIsSoft( bTotalSoft = bTotalSoft );
  # start - end

  # return 0 si l'articulation n'as presque pas bougé, 1 si elle a bougé dans le sens positif, et -1 si dans le sens negatif
  # return 100 if there's a move command
  # don't call it too often, because sensor take some time to reach actuator value
  def update( self ):
    rNewValueSensor = self.stm.getData( self.strStmJointNameSensor, 0 ); # todo: en une passe avec un getListData ?
    rNewValueActuator = self.stm.getData( self.strStmJointNameActuator, 0 );
    rNewValueHardness = self.stm.getData( self.strStmJointNameStiffness, 0 );
    #~ print( "rNewValueSensor: %s" % rNewValueSensor );
    # check if there was a new user command
    if( abs( rNewValueActuator - self.rLastActuatorValue ) < 0.005 or rNewValueHardness < 0.001 ):  # actuator is by nature very precise - actuator is copied from position when stifnness is 0
#      debug( "JointMove debug('" + self.strJointName + "'): rActu-old: %8.5f; new: %8.5f; rSensor-old: %8.5f; new: %8.5f" % ( self.rLastActuatorValue, rNewValueActuator, self.rLastSensorValue, rNewValueSensor ) );
      rDiff = rNewValueSensor - self.rLastSensorValue;
      self.rLastSensorValue = rNewValueSensor;
      if( abs( rDiff ) > self.rDiffThreshold ):
        #~ print( "JointMove debug('" + self.strJointName + "'): rSensor-old: %8.5f; rDiff: %5.3f >>>" % ( self.rLastSensorValue, rDiff ) );
        if( rDiff > 0 ): return 1;
        return -1;
    else:
      # the joint has received a move order: update value
#      debug( "JointMove debug('" + self.strJointName + "'): rActu-old: %8.5f; new: %8.5f stiff: %5.3f" % ( self.rLastActuatorValue, rNewValueActuator, rNewValueHardness ) );
      # to skip the (rebond) rebound, we add small latency after having move, we put the actuator small by small to the new value
#      self.rLastActuatorValue = rNewValueActuator;
      self.rLastActuatorValue = self.rLastActuatorValue *0.2 + rNewValueActuator * 0.8; # slowly update value (but not too slowly)      
      # update sensor, so it won't trigger next frame
      self.rLastSensorValue = rNewValueSensor;
      return 100;
    return 0;
  # update - end
  
  def updateEffort( self ):
        "Transform the JointMove in JointEffort object"
        "update information to know if something produce an effort on a joint"
        "return a signed direction: a direction and the amount of the effort"
        "WARNING: this is a specific use of this class: you shouldn't use both update and updateEffort method of the same object at the same time"
        rNewValueSensor = self.stm.getData( self.strStmJointNameSensor, 0 ); # todo: en une passe avec un getListData ?
        rNewValueActuator = self.stm.getData( self.strStmJointNameActuator, 0 );
        if( abs( rNewValueActuator - self.rLastActuatorValue ) > 0.005 ):
            # joint is moving
            self.rLastActuatorValue = rNewValueActuator;
            return 0;
        if( abs( rNewValueSensor - rNewValueActuator ) < 0.040 ):
            # no effort
            return 0;
        return rNewValueSensor - rNewValueActuator;
  # updateEffort - end
  
  def updatePush( self ):
        """Transform the JointMove in JointPush object
        update information to know if something produce an effort on a joint
        return a signed direction: a direction and the amount of the effort
        WARNING: this is a specific use of this class: you shouldn't use both update and updateEffort method of the same object at the same time
        return:
            - 0: not pushed
            - +1: push in a direction
            - -1: push in the other side
            - 2: moving
        """
        rNewValueSensor = self.stm.getData( self.strStmJointNameSensor, 0 ); # todo: en une passe avec un getListData ?
        rNewValueActuator = self.stm.getData( self.strStmJointNameActuator, 0 );
        if( abs( rNewValueActuator - self.rLastActuatorValue ) > 0.005 ):
            # joint is moving
            self.rLastActuatorValue = rNewValueActuator;
            return 2;
        if( abs( rNewValueSensor - rNewValueActuator ) > self.rDiffThreshold ):
            # pushed!
            if( rNewValueSensor > rNewValueActuator ):
                return 1;
            return -1;                
        return 0;
  # updatePush - end  

  # remet les valeurs a zero pour un nouveau catch d'evenement
  def reset( self ):
    self.rLastSensorValue = self.stm.getData( self.strStmJointNameSensor, 0 );
    self.rLastActuatorValue = self.stm.getData( self.strStmJointNameActuator, 0 );
  # reset - end
# class JointMove - end

class JointMinimalStiffness:
    """
    Ensure the position of a joint is keeped, using the very minimal stiffness.
    The position to keep is the one at creation or when storePosition is called.
    """

    def __init__( self, strJointName ):
        self.strJointName = strJointName;
        self.stm = naoqitools.myGetProxy( "ALMemory" );
        self.motion = naoqitools.myGetProxy( "ALMotion" );
        self.strStmJointNameSensor = "Device/SubDeviceList/" + strJointName + "/Position/Sensor/Value";
        self.strStmJointNameActuator = "Device/SubDeviceList/" + strJointName + "/Position/Actuator/Value";
        self.strStmJointNameStiffness    = "Device/SubDeviceList/" + strJointName + "/Hardness/Actuator/Value";
        self.rDiffThreshold = 0.1;
        self.timeLastDecrease = time.time();
        self.timeLastResendConsign = time.time();
        self.reset();
    # __init__ - end

    def getJointName( self ):
        return self.strJointName;
    # getJointName - end

    def setDiffThreshold( self, rNewVal ):
        "Change the diff threshold"
        self.rDiffThreshold = rNewVal;
    # setDiffThreshold - end

    def storeCurrentPosition( self ):
        reset();
    # storeCurrentPosition - end

    # update the stiffness and the position
    def update( self, bVerbose = False ):
        """
        return a value relative to action made:
          -2: we've got too much order differnce, so we restoring a new consign
          -1: new order has been received: someone ask that joint to move, what to do ?
            0: if nothing has been made.
            1: stiffness decreased
            2: stiffness increased
            3: stiffness increased and consign send again
        """
        rIncreaseStiffness = 0.2;
        rDecreaseStiffness = 0.04;
        nReturnValue = 0;
        rNewValueSensor = self.stm.getData( self.strStmJointNameSensor );        
        rDiff = abs( rNewValueSensor - self.rConsign );
        if( rDiff > self.rDiffThreshold ):
            # update a bit the stiffness, and copy the value to actuator
            rCurrentStiffness = self.stm.getData( self.strStmJointNameStiffness );
            if( rCurrentStiffness < 1. ):
                rCurrentStiffness += rIncreaseStiffness;
                if( rCurrentStiffness + rIncreaseStiffness >= 1. ):
                    rCurrentStiffness = 1.;                
                self.motion.setStiffnesses( self.strJointName, rCurrentStiffness );
                nReturnValue = 2;
                if( bVerbose ):
                    print( "INF: %s: motiontools.JointMinimalStiffness %s: increasing stiffness to %.3f (sensor/consign: %.3f, %.3f)" % ( time.time(), self.strJointName, rCurrentStiffness, rNewValueSensor, self.rConsign) );
                self.timeLastDecrease = time.time(); # avoid decreasing too fast...
            rCurrentConsign = self.stm.getData( self.strStmJointNameActuator );
            if( rCurrentConsign != self.rConsign ):
                rPrevStiffness = rCurrentStiffness-rIncreaseStiffness;
                if( rPrevStiffness <= 0.0001 ): # the only case when we agree to resend, is when stiffness touch zero, so actuator has been copied. else, it's for sure an order received from another behavior
                    if( bVerbose ):
                        print( "INF: %s: motiontools.JointMinimalStiffness %s: resending consign to %.3f (current is %.3f) (prev stiffness is %f)" % ( time.time(), self.strJointName, self.rConsign, rCurrentConsign, rPrevStiffness ) );
                    self.motion.post.setAngles( self.strJointName, self.rConsign, 1. ); # send at max speed
                    self.timeLastResendConsign = time.time();
                    nReturnValue = 3;
                else:
                    if( time.time() - self.timeLastResendConsign > 2. ): # when we resend a consign, motion takes time to handle it, so for some times, the consign is moving, and so we should think it's from outer world
                        if( bVerbose ):
                            print( "INF: %s: motiontools.JointMinimalStiffness %s: consign has moved, doesn't resend consign because someone seems to need to send order ! wanted: %.3f (current is %.3f) (prev stiffness is %f)" % ( time.time(), self.strJointName, self.rConsign, rCurrentConsign, rPrevStiffness ) );
                        nReturnValue = -1;
                        if( rCurrentStiffness > 0.9 ):
                            if( bVerbose ):
                                print( "INF: %s: motiontools.JointMinimalStiffness %s: storing a new consign current: %f, new: %f" % ( time.time(), self.strJointName, self.rConsign, rCurrentConsign ) );
                            self.rConsign = rCurrentConsign;                            
                            nReturnValue = -2;
                                            
        else:
            if( time.time() - self.timeLastDecrease > 2. ):
                self.timeLastDecrease = time.time();
                rCurrentStiffness = self.stm.getData( self.strStmJointNameStiffness );
                if( rCurrentStiffness > 0.0001 ):
                    rCurrentStiffness -= rDecreaseStiffness;
                    if( rCurrentStiffness < 0. ):
                        rCurrentStiffness = 0.;
                    self.motion.setStiffnesses( self.strJointName, rCurrentStiffness );
                    nReturnValue = 1;
                    if( bVerbose ):
                        print( "INF: %s: motiontools.JointMinimalStiffness %s: decreasing stiffness to %.3f" % ( time.time(), self.strJointName, rCurrentStiffness) );
        return nReturnValue;
    # update - end


    # remet les valeurs a zero pour un nouveau catch d'evenement
    def reset( self ):
        self.rLastSensorValue = self.stm.getData( self.strStmJointNameSensor, 0 );
        self.rConsign = self.stm.getData( self.strStmJointNameActuator, 0 );
    # reset - end
    
# class JointMinimalStiffness - end

class Hand:
    "a class handling hand, closing, detection and ..."
    def __init__( self, cSide = 'L' ):
        
        """You can init both with 'L'/'R' or "LHand"/"RHand" """
        
        self.cSide = cSide[0];
        if( self.cSide == 'L' ):
            self.strHandName = "LHand";
        else:
            self.strHandName = "RHand";
        self.rlastActuatorValue = -1000.; # a dummy value
        self.mem = naoqitools.myGetProxy( "ALMemory" );
        self.motion = naoqitools.myGetProxy( "ALMotion" );
        self.listKeyName = [ "Device/SubDeviceList/%s/Position/Actuator/Value" % self.strHandName,
                                    "Device/SubDeviceList/%s/Position/Sensor/Value" % self.strHandName,
                                    "Device/SubDeviceList/%s/ElectricCurrent/Sensor/Value" % self.strHandName,
                                ];
        self.rErrorMargin = 0.002;
        if( system.isOnRomeo() ):
            self.rErrorMargin *= 15
        self.calibrate();
    # __init__ - end
    
    def loadCalibration( self ):
        """
        load previous calibration (once in a boot)
        """        
        try:
            file = open( pathtools.getVolatilePath() + "abcdk_calibration_%s.txt" % self.getSide(), "rt" );
            buf = file.read();
            file.close();
            self.rFullClosed = eval( buf );
            print( "INF: abcdk.motiontools.hand.loadCalibration: %s: rFullClosed: %f" % (self.getName(), self.rFullClosed ) );
            return True;            
        except BaseException, err:
            print( "INF: abcdk.motiontools.hand.loadCalibration: %s: %s" % (self.getName(), str(err) ) );
        return False;
    # loadCalibration - end

    def saveCalibration( self ):
        """
        """        
        try:
            file = open( pathtools.getVolatilePath() + "abcdk_calibration_%s.txt" % self.getSide(), "wt" );
            file.write(str(self.rFullClosed) );
            file.close();
            return True;            
        except BaseException, err:
            print( "ERR: abcdk.motiontools.hand.saveCalibration: %s: %s" % (self.getName(), str(err) ) );
        return False;
    # loadCalibration - end

    def calibrate( self, bForceRecalibration = False ):
        """
        at every reboot, we recalibrate hand
        - bForceRecalibration: even if calibrated, recalibrate
        """
        if( not bForceRecalibration ):
            if( self.loadCalibration()  ):
                return;
        rMaxFullClosed = 0.;
        self.motion.setStiffnesses( self.getName(), 1. );
        for i in range( 5 ):
            self.motion.angleInterpolation( self.getName(), 1., 0.5, True );
            time.sleep( 0.4 ); # wait for end of movement
            self.motion.angleInterpolationWithSpeed( self.getName(), 0., 0.2*(i+1) );
            time.sleep( 1. ); # wait for "stuffs"
            if( system.isOnRomeo() ):
                time.sleep( 0.6 );
            rFullClosed = self.mem.getData( self.listKeyName[1] );
            print( "INF: abcdk.motiontools.hand.calibrate: %s: full closed=%f" % (self.getName(), rFullClosed ) );
            if( rFullClosed > rMaxFullClosed ):
                rMaxFullClosed = rFullClosed;
        self.rFullClosed = rMaxFullClosed;
        #~ self.rFullClosed += self.rErrorMargin;
        print( "INF: abcdk.motiontools.hand.calibrate: %s: storing full closed=%f" % (self.getName(), self.rFullClosed ) );
        self.saveCalibration();        
    # calibrate - end
    
    def getSide( self ):
        return self.cSide;
        
    def getName( self ):
        return self.strHandName;
        
    def open( self, rTime = 1.5 ):        
        "a simple open"
        if( self.motion.getAngles( self.getName(), True)[0] >= 0.9 ):
            # seems already open, do nothing!
            return;
        self.motion.setStiffnesses( self.getName(), 1. );
        self.motion.post.angleInterpolation( self.strHandName, 0.9, rTime, True );
        time.sleep( rTime ); # on some robot, the moving of hand leave without the moves to be really finished, so we make our own wait
    # open - end
    
    def close( self ):
        "close the hand, but not totally to prevent hitting the physical limits"
        "so we could know if there's 'something' in the hand"
        
        self.motion.setStiffnesses( self.getName(), 1. );
        strNaoVer = system.getBodyVersion();
        bV32 = ( strNaoVer == '3.2' or strNaoVer == '3Plus' );
        print( "robot version is v3.2 => %s (sys: '%s')" % ( str( bV32 ), system.getBodyVersion() ) );
        rValue = self.rFullClosed;
        if( bV32 ):
            rValue = 0.15;
        rTime = 1.5;
        self.motion.post.angleInterpolation( self.strHandName, rValue, rTime, True );
        time.sleep( rTime ); # on some robot, the moving of hand leave without the moves to be really finished, so we make our own wait
    # close - end
    
    def grab( self, bLoose = False ):
        """
        Grab stuffs: close hand, then reopen it a bit to not broke or heat too much
        - bLoose: grab it but open a bit so it's loose, so the object can sleep a bit (for charger, fork, ...)
        Return true if something has been grabed
        """
        self.motion.setStiffnesses( self.getName(), 1. );
        self.motion.angleInterpolation( self.strHandName, 0., 0.8, True );
        time.sleep( 0.5 );
        rCurrentPosition = self.mem.getData( self.listKeyName[1] );
        bStuffsInIt = rCurrentPosition > self.rFullClosed + self.rErrorMargin;
        print( "INF: abcdk.motiontools.hand.grab: %s: current position=%f; rFullClosed:%f; bStuffsInIt: %s" % (self.getName(), rCurrentPosition, self.rFullClosed, bStuffsInIt ) );
        if( bStuffsInIt ):
            # something in the hand !!!
            rNewPosition = rCurrentPosition - 0.001;
            if( system.isOnRomeo() ):
                rNewPosition = 0.01; # Romeo is not very abile with it's hand, continue to close it a lot!
            if( bLoose ):
                rNewPosition += 0.12; # 0.09 was fine too...
            print( "INF: abcdk.motiontools.hand.grab: %s: new position=%f; " % ( self.getName(), rNewPosition ) );
            self.motion.post.angleInterpolation( self.strHandName, rNewPosition, 0.4, True ); # open a bit
            return True;
        return False;        
    # grab - end
    
    def isSomethingInIt( self ):
        rCurrentPosition = self.mem.getData( self.listKeyName[1] );
        rCurrentOrder = self.mem.getData( self.listKeyName[0] );
        bStuffsInIt = rCurrentPosition > self.rFullClosed + self.rErrorMargin and rCurrentOrder <= rCurrentPosition;
        print( "INF: abcdk.motiontools.hand.getSomethingInIt: %s: rFullClosed: %f, current position: %f; rCurrentOrder: %f, bStuffsInIt: %s" % (self.getName(), self.rFullClosed, rCurrentPosition, rCurrentOrder, bStuffsInIt ) );
        return bStuffsInIt;
    # getSomethingInIt - end
    
    def getStatus( self ):
        """
        return 2 if something is in the hand, 0 if nothing is in the hand, 1 if the hand is moving
        WARNING: seems outdated: doesn't use the rFullClosed position...
        """
        
        rActuatorValue, rSensorValue, rConsumpValue = self.mem.getListData( self.listKeyName );
        if( abs( self.rlastActuatorValue - rActuatorValue ) > 0.01 ):
            # moving
            self.rlastActuatorValue = rActuatorValue;
            return 1;
            
        rDiff = rSensorValue - rActuatorValue + rConsumpValue/70; # the consumption is a bit interesting just to add a slight bonus
        if( rDiff > 0.009 ):
            return 2;
        return 0;
    # getStatus - end

# class Hand - end


# handy method to memorize wich hand to use to grab object
global_cHandToGrab = "R"; # default is righty
def setHandToGrabSide( cSide ):
    """
    define wich hand you want to use to grab thing
    """
    global global_cHandToGrab;
    cNewSide = cSide[0].upper();
    print( "INF: abcdk.motiontools.setHandToGrabSide: changing from '%s' to '%s'=>'%s'" % (global_cHandToGrab, cSide, cNewSide ) );
    global_cHandToGrab = cNewSide;

def getHandToGrabSide():
    global global_cHandToGrab;
    return global_cHandToGrab;
    
def getHandNotToGrabSide():
    global global_cHandToGrab
    if( global_cHandToGrab == "R" ):
        return "L";
    return "R";
    
def getHandToGrab():
    return Hand(getHandToGrabSide());

def getHandNotToGrab():
    return Hand(getHandNotToGrabSide());

    
def getFreeHandSide():
    """
    Return a free hand letter or "" if none
    """
    if( not getHandToGrab().isSomethingInIt() ):
        return getHandToGrabSide();
        
    if( not getHandToGrab().isSomethingInIt() ):
        return getHandNotToGrab();    
    return "";
# getFreeHandLetter - end


def autoTest_Hand():
    h = Hand( 'L' );
    h.open();
    h.close();
    print( "hand: name: %s, status: %d" % ( h.getName(), h.getStatus() ) );
# autoTest_Hand - end

def convertPostureName( strNameFromSomeVersion ):
    """
    Convert old and new posture to standard one 
    (cf getCurrentPosture for further information)
    """
    aTableCompat = {
        "Stand": "Standing",
        "Sit": "Sitting",
        "Crouch": "Crouching",
        "Kneel": "Unknown",
        "Frog": "Unknown",
        "Back": "LyingBack",
        "Belly": "LyingBelly",
        "Left" : "LyingLeft",
        "Right": "LyingRight", 
        "HeadBack":  "Unknown",
    };        
    try:
        return aTableCompat[strNameFromSomeVersion];
    except KeyError, err:
        return strNameFromSomeVersion;
# convertPostureName - end

def getCurrentPosture():
    """
    Return current NAO position, using the 1.14 namming, even if the NAO is using 1.12.
    Could be: ["Back", "Belly", "Kneeling", "Left", "Lifted", "LyingBack", "LyingBelly", "LyingLeft", "LyingRight", "Right", "Sitting", "Standing", "UpsideDown"] or "Unknown" or "Crouching" (added to 1.14 standard)
    We ensure that it would remains the same, even in the futur !
    """
    try:
        rp = naoqitools.myGetProxy( "ALRobotPosture" );
        memory = naoqitools.myGetProxy( "ALMemory" );
        strPos = rp.getPostureFamily();
        nNumPos = rp._getPosture();
        #~ print( "DBG: motiontools.getCurrentPosture: nNumPos: %s" % nNumPos );
        kPosCrouching1_14 = 10162;
        strSensorTemplate = "Device/SubDeviceList/%s/Position/Sensor/Value";
        arKneeAngle = memory.getListData( [ strSensorTemplate % "RKneePitch", strSensorTemplate % "LKneePitch" ] );
        #~ print( "DBG: motiontools.getCurrentPosture: arKneeAngle: %s" % arKneeAngle );
        bKneeFlexed = (reduce(lambda x, y: abs(x) + y, arKneeAngle) / len(arKneeAngle)) >1.3; # is average > 1.3 ?
        #~ print( "DBG: motiontools.getCurrentPosture: bKneeFlexed: %s" % bKneeFlexed );
        if( nNumPos == kPosCrouching1_14 or kPosCrouching1_14 in nNumPos or (strPos == "Standing" and bKneeFlexed) ): # What a surprise, now in 1.22 _getPosture return an array of posture !!!
            strPos = "Crouching";
    except BaseException, err:
        print( "DBG: normal error: " + str( err ) );
        rp = None;
    if( rp == None ):
        try:
            rp = naoqitools.myGetProxy( "ALRobotPose" );
            strPos = rp.getActualPoseAndTime()[0];    
        except BaseException, err:
            print( "ERR: abnormal error: " + str( err ) + " (or we are on romeo? => TODO: add in poselibrary the romeo case) => returning Standing" );
            return "Standing";
    return convertPostureName( strPos );
# getCurrentPosture - end

def hasFall():
    """
    Are we in a position that is not possible while standing, unless we're fallen ?
    (the old big switch case from our demo)
    Return True if yes or False, elsewhere
    """
    strPos = getCurrentPosture();
    #~ print( "DBG: hasFall: getCurrentPosture: %s" % strPos );
    bPosSayFall = not strPos in ["Standing", "Sitting", "Unknown", "Crouching"];
    if( not bPosSayFall ):
        try:
            mem = naoqitools.myGetProxy( "ALMemory" );
            timeLastFall =  mem.getTimestamp( "ALMotion/RobotIsFalling" );
            if( len(timeLastFall) > 1 ):
                if( time.time() - timeLastFall[1] < 2 ):
                    bPosSayFall = True;
        except BaseException, err:
            print( "DBG: hasFall: this error should never be raised: %s (raising for futur compatibility check)" % err );
            pass
            
    return bPosSayFall;
# hasFall - end

def isWalkPossible( _bInternalCall =  False ):
    """
    Am I in a correst position to walk, right now ?
    Return True if yes or False, elsewhere
    """
    strPos = getCurrentPosture();
    print( "DBG: isWalkPossible: getCurrentPosture: %s" % strPos );
    bIsPossible = strPos in ["Standing"];
    if( not bIsPossible and not _bInternalCall ):
        time.sleep( 0.2 );
        bIsPossible = isWalkPossible( _bInternalCall = True );
    return bIsPossible;
# hasFall - end

global_gotoPostureMultiversion_currentMove = False;

def gotoPostureMultiversion( strPositionName, nNbrRetries = 3, rSpeed = 0.8, bForceOldVersion = False ):
    """
    Go to a position, handle old 1.12 version...
    - strPositionName: the position name, eg: Stand, Sit, ...
    - nNbrRetries: retry the full movement while not achieved
    - rSpeed: an indication of the time to try to do the move (not handled in all version)
    return True on success, False on error (behavior not present, unknown position, can't reach position, ...)
    """
    print( "INF: abcdk.motiontools.gotoPostureMultiversion: strPositionName: '%s', nNbrRetries: %d, rSpeed: %f, bForceOldVersion: %d" % ( strPositionName, nNbrRetries, rSpeed, bForceOldVersion ) );
    strVersion = system.getNaoqiVersion();
    if( "1.12" in strVersion or "1.10" in strVersion or bForceOldVersion ):
        bm = naoqitools.myGetProxy( "ALBehaviorManager" );
        global global_gotoPostureMultiversion_currentMove;
        if( not bm.isBehaviorInstalled( strPositionName ) ):
            raise( BaseException( "ERR: abcdk.motiontools.gotoPostureMultiversion: behavior '%s' not found. To have backward retrocompatibilty, you need to install extra behavior to go to each pose you need, we could provide it some, yeeah..." % strPositionName ) ); 
        global_gotoPostureMultiversion_currentMove = strPositionName;
        print( "INF: abcdk.motiontools.gotoPostureMultiversion: launching behavior '%s'..." % strPositionName );
        bm.runBehavior( strPositionName );
        print( "INF: abcdk.motiontools.gotoPostureMultiversion: launching behavior '%s' - ended" % strPositionName );
        global_gotoPostureMultiversion_currentMove = False;
        bResult = strPositionName in getCurrentPosture(); # "in" used because the result of a "Stand" order is "Standing"
    else:
        rp = naoqitools.myGetProxy( "ALRobotPosture" );
        rp.setMaxTryNumber( nNbrRetries );
        bResult = rp.goToPosture( strPositionName, rSpeed );
        rp.setMaxTryNumber( 3 ); # reset the default value... bad: there's no mean to know what the value before going there...
    return bResult;    
# gotoPostureMultiversion - end

def standup( nNbrRetries = 3, rSpeed = 0.8, bForceOldVersion = False ):
    """
    standup the robot. see gotoPostureMultiversion for more information
    """
    return gotoPostureMultiversion( "Stand", nNbrRetries = nNbrRetries, rSpeed = rSpeed, bForceOldVersion = bForceOldVersion );
# standup - end

def sitdown( nNbrRetries = 3, rSpeed = 0.8, bForceOldVersion = False ):
    """
    sitdown the robot. see gotoPostureMultiversion for more information
    """
    return gotoPostureMultiversion( "Sit", nNbrRetries = nNbrRetries, rSpeed = rSpeed, bForceOldVersion = bForceOldVersion );
# sitdown - end

def stopGotoPosture( bForceOldVersion = False ):
    """
    Stop all gotoPostureMultiversion, standup or sitdown current order.
    """
    strVersion = system.getNaoqiVersion();
    if( "1.12" in strVersion or "1.10" in strVersion or bForceOldVersion ):
        global global_gotoPostureMultiversion_currentMove;
        if( global_gotoPostureMultiversion_currentMove ):
            bm = naoqitools.myGetProxy( "ALBehaviorManager" );            
            bm.stopBehavior( global_gotoPostureMultiversion_currentMove );
            global_gotoPostureMultiversion_currentMove = "";
    else:
        rp = naoqitools.myGetProxy( "ALRobotPosture" );    
        rp.stopMove();
# stopGotoPosture - end

def gotoPositionDCM( strJointName, rPos, rTimeSec = 1. ):
    """
    send a position order to a joint. non blocking call.
    """
    dcm = naoqitools.myGetProxy( "DCM" );
    endTime = dcm.getTime(int(rTimeSec*1000));
    strDeviceName = "Device/SubDeviceList/%s/Position/Actuator/Value" % strJointName;
    dcm.set( [ strDeviceName, "ClearAll",  [[ rPos, endTime ]] ] );    
# gotoPositionDCM - end

def gotoPositionDCM_WithSpeedMax( strJointName, rPos, rTimeSec = 1., rSpeedMax = 0.2 ):
    """
    send a position order to a joint, using a speed max (en rad/sec)
    return the reduction ratio (if occurs)
    - rSpeedMax: the speed max to use in sec
    """
    #~ print( "DBG: motiontools.gotoPositionDCM_WithSpeedMax: '%s',pos: %f, time: %f, speedmax: %f "% (strJointName, rPos, rTimeSec, rSpeedMax) );
    if( strJointName == "RHipYawPitch" ):
        strJointName = "LHipYawPitch";
    dcm = naoqitools.myGetProxy( "DCM" );
    mem = naoqitools.myGetProxy( "ALMemory" );
    endTime = dcm.getTime(int(rTimeSec*1000));
    strDeviceName = "Device/SubDeviceList/%s/Position/Actuator/Value" % strJointName;
    strSensorName = "Device/SubDeviceList/%s/Position/Sensor/Value" % strJointName;
    rActualPos = mem.getData( strSensorName );
    rWantedSpeed = abs( rPos - rActualPos ) / rTimeSec;
    rRatio = 1.;
    if( rWantedSpeed > rSpeedMax ):
        rRatio = rSpeedMax / rWantedSpeed;
        print( "INF: motiontools.gotoPositionDCM_WithSpeedMax: reducing speed for joint '%s', applying a reduction ratio of %f" % (strJointName, rRatio) );        
        rPos = rPos * rRatio + rActualPos * (1.-rRatio);
    dcm.set( [ strDeviceName, "ClearAll",  [[ rPos, endTime ]] ] );    
    return rRatio;
# gotoPositionDCM_WithSpeedMax - end


class TimelinePlayer():
    def __init__( self, aKeyName, aTime, aPosition ):
        self.motion = naoqitools.myGetProxy( "ALMotion" );
        self.aKeyName = aKeyName;
        self.aTime = aTime;
        self.aPosition = aPosition;
        self.reset();        
        
    def __del__( self ):
        if( self.timeBegin != 0 ):
            # there was movement!
            self.motion._resetMotionCommandModelToSensors( "Body" );
            
    def getTimelineInfo( self ):
        strOut = "# getTimelineInfo:\n";
        for idx, timeArray in enumerate(self.aTime):
            strOut += "%14s: %3d key(s), from: %5.2fs to %5.2fs\n" % (self.aKeyName[idx], len(timeArray), timeArray[0], timeArray[-1]);
        strOut += "\n"
        return strOut;
        

    def reset( self ):
        self.timeBegin = 0; # 0 means not started
        self.rTimeError = 0.; # sum the latency lost between send and precise time where to send
        self.lastorientate = 0.;
        
    
    def update( self, rSpeed = 1., rSpeedMax = 0.8, rOrientate = 0. ):
        """
        start or update the timeline playing.
        return False when finished
        """
        
        if( self.lastorientate != rOrientate ):
            self.lastorientate = rOrientate;
            bNewOrientate = True;
        else:
            bNewOrientate = False;
        nNbrKey = len(self.aKeyName);
        bForceResend = False;
        if( self.timeBegin == 0 ):
            self.timeBegin = time.time();
            self.rTimeConstant = 0.; # constant to add to permits to change speed of animation on the fly
            self.rSpeed = rSpeed;
            self.rTimeError = 0.;
            self.nNbrMoveCall = 0;
            self.aIdxTime = [0]*nNbrKey;
            # send first position:
            bForceResend = True;

        if( rSpeed != self.rSpeed or bNewOrientate ):
            # user want a new speed, we will use current time position as a new animation time departure, so from now on, we use the new speed
            self.rTimeConstant = self.rTimeConstant + (time.time() - self.timeBegin)*self.rSpeed;
            print( "INF: motiontools.TimelinePlayer.update: changing speed. new: rTimeConstant: %f, timeBegin: was %f, new: %f, newspeed: %f" % ( self.rTimeConstant, self.timeBegin, time.time(), rSpeed ) );
            self.timeBegin = time.time();
            self.rSpeed = rSpeed;
            # resend current order, so that they will be respeeded
            bForceResend = True;

        rT = self.rTimeConstant + (time.time() - self.timeBegin)*self.rSpeed;
        #~ print( "DBG: motiontools.TimelinePlayer.update: time: %f, rT: %f, time - timeBegin: %f" % ( time.time(), rT, time.time() - self.timeBegin ) );

        if( bForceResend ):
            for nNumKey in range( nNbrKey ):
                if( not self.aIdxTime[nNumKey] is False ):                
                    rPos = self.aPosition[nNumKey][self.aIdxTime[nNumKey]];
                    if( ( "ShoulderPitch" in self.aKeyName[nNumKey] or "HeadPitch" in self.aKeyName[nNumKey]  ) and abs( self.lastorientate ) >= 0.1 ):
                        rPos += self.lastorientate;
                    rTime = (self.aTime[nNumKey][self.aIdxTime[nNumKey]]-rT)/rSpeed;
                    gotoPositionDCM_WithSpeedMax( self.aKeyName[nNumKey], rPos, rTimeSec = rTime, rSpeedMax = rSpeedMax );
                    self.nNbrMoveCall += 1;
            return True;
        
        bAtLeastOneRemaining = False;
        rAnticipationTime = 0.01;        
        bUseBatchSend = False; # reduce from 61 to 28 calls on a standard hello
        if( bUseBatchSend ):            
            # we try to send many moves at the same time... (it could be interesting, if a lot of joints are moved in the same time line)
            # but if a long moves is send, ressources of finished movement are taken !
            batchKey = [];
            batchPos = [];
            batchTime = [];
        #~ print( "avant envoi (nNbrKey:%d)" % nNbrKey );
        for nNumKey in range( nNbrKey ):
            if( not self.aIdxTime[nNumKey] is False ): # 0 == False  but 0 is not False
                if( self.aTime[nNumKey][self.aIdxTime[nNumKey]] <= rT+rAnticipationTime ):
                    rLocalTimeError = rT-self.aTime[nNumKey][self.aIdxTime[nNumKey]];
                    if( rLocalTimeError > 0. ):
                        self.rTimeError += rLocalTimeError;
                    #~ print( "DBG: motiontools.playTimelineCustom: sending order (dt error: %f)" % ( rLocalTimeError ) );
                    # send next position
                    self.aIdxTime[nNumKey] += 1;
                    if( self.aIdxTime[nNumKey] < len( self.aTime[nNumKey] ) ):
                        rPos = self.aPosition[nNumKey][self.aIdxTime[nNumKey]];
                        if( ( "ShoulderPitch" in self.aKeyName[nNumKey] or "HeadPitch" in self.aKeyName[nNumKey]  ) and abs( self.lastorientate ) >= 0.1 ):
                            rPos += self.lastorientate;
                        
                        rTime = (self.aTime[nNumKey][self.aIdxTime[nNumKey]]-rT)/rSpeed;
                        bSent = False;
                        if( bUseBatchSend ):
                            if( len(batchTime)< 1 or rTime == batchTime[0] ):
                                # same time => ok
                                bSent = True;
                                batchKey.append( self.aKeyName[nNumKey] );
                                batchPos.append( rPos );
                                batchTime.append( rTime );
                        if(not bSent):
                            #~ self.motion.post.angleInterpolation( self.aKeyName[nNumKey], rPos, rTime, True );
                            gotoPositionDCM_WithSpeedMax( self.aKeyName[nNumKey], rPos, rTimeSec = rTime, rSpeedMax = rSpeedMax );
                            self.nNbrMoveCall += 1;
                        bAtLeastOneRemaining = True;
                        #~ print( "%s: send order" % self.aKeyName[nNumKey] );
                    else:
                        print( "INF: motiontools.TimelinePlayer.update: joint '%s': animation finished current idx: %d, total idx: %d, time at idx-1: %5.2f, time at end: %5.2f"  % ( self.aKeyName[nNumKey],  self.aIdxTime[nNumKey], len(self.aTime[nNumKey]), self.aTime[nNumKey][self.aIdxTime[nNumKey]-1], self.aTime[nNumKey][-1] ) );
                        self.aIdxTime[nNumKey] = False;                
                else:
                    # nothing to do, just wait...
                    #~ print( "%s: wait" % self.aKeyName[nNumKey] );
                    bAtLeastOneRemaining = True;
            # if not finished - end
        # for - end
        if( bUseBatchSend and len( batchKey ) > 0 ):
            self.motion.post.angleInterpolation( batchKey, batchPos, batchTime, True );
            self.nNbrMoveCall += 1;
            
        if( not bAtLeastOneRemaining ):
            print( "INF: motiontools.TimelinePlayer.playStandalone: finished, rTimeError: %f, nNbrMoveCall: %d" % ( self.rTimeError, self.nNbrMoveCall ) );            
        return bAtLeastOneRemaining;
     # update - end
        
    def playStandalone( self ):
        """
        Just a small method to test stuffs
        """
        print( "INF: motiontools.TimelinePlayer.playStandalone: playing a timeline with %d joint(s)" % len(self.aKeyName) );  
        rDT = 0.01/4;        
        bUnfinished = True;
        while( bUnfinished ):
            bUnfinished = self.update();
            time.sleep( rDT );
        # while - end
        self.motion._resetMotionCommandModelToSensors( "Body" );
        print( "INF: motiontools.TimelinePlayer.playStandalone: ended (time error: %f)" % self.rTimeError );
    # playStandalone - end

# TimelinePlayer - end

def playTimelineCustom( aKeyName, aTime, aPosition ):
    """
    play a timeline with a custom player.
    we manage time and we decide how, when, and what send relative to some desire.
    """
    timelinePlayer = TimelinePlayer( aKeyName, aTime, aPosition );
    timelinePlayer.playStandalone();
# playTimelineCustom - end

def getTimelineDuration( aTime ):
    """
    return the length of an animation, based on the big time array
    """
    # find the max of each key:
    rTimeMax = 0.;
    for keyTimes in aTime:
        if( len(keyTimes) > 0 ):
            if( keyTimes[-1] > rTimeMax ):
                rTimeMax = keyTimes[-1];
    return rTimeMax;
# getTimelineDuration - end
    

def getTimelinePosition( listPos,nIdxPos ):
    """
    get the position from a list of position, handling various possible format.
    listPos: various format: 
                    [ [pos1, spline1info...],  [pos2, spline2info...]] 
                or  [ [pos1],  [pos2]]
                or  [ pos1, pos2 ] 
    - nIdxPos
    """
    if( typetools.isArray( listPos[nIdxPos] ) ):
        return listPos[nIdxPos][0];
    return listPos[nIdxPos];
# getPositionFromTimeline - end

def setTimelinePosition( listPos, nIdxPos, rVal ):
    """
    set the position, cf getTimelinePosition...
    """
    if( typetools.isArray( listPos[nIdxPos] ) ):
        listPos[nIdxPos][0] = rVal;
    else:
        listPos[nIdxPos] = rVal;
# setTimelinePosition - end
    

def transformTimeline( aKeyNameParam, aTimeParam, aPositionParam, dictPositionModifier = {}, bFlip = False ):
    """
    Modify a timeline (speed it, slow down it, mirror it, offset it, reverse it...).
        - aKeyName: list of key (as exported by the timeline export method). eg: [ "HeadPitch", "HeadYaw", ] or ["Hand"] (so it will patch every joint with the word Hand in it.
        - aTime: list of time. eg: [ [0.48, 0.88], [0.48, 0.88], ]
        - aPosition : list of position (with or without splines). eg: [   [[0.12217, [3, -0.16, 0.0], [3, 0.13333, 0.0]], [-0.12217, [3, -0.13333, 0.0], [3, 0.0, 0.0]]], [[-0.04606, [3, -0.16, 0.0], [3, 0.13333, 0.0]], [-0.04913, [3, -0.13333, 0.0], [3, 0.0, 0.0]]], ] 
                                                           or without splines: [   [[0.12217], [-0.12217]], [[-0.04606, ], [-0.04913]]   ]
                                                           or without splines, array reduced: [   [0.12217, -0.12217], [-0.04606, -0.04913]   ]
        - dictPositionModifier: an instant modifier joint per joint. 
            eg: { "HeadYaw": 1. } will add 1 rads to every position of headyaw. 
            or { "HeadYaw": ["offset",2.,"multiplier",0.5] } => will multiply each HeadYaw position per 0.5 then add 2
            possible modifier are: 
                - "offset" or "off" or "o":      add a fix value [-inf,+inf]
                - "multiplier" or "mul" or "m": multiply by a fix value [0,+inf]
                - "amplify" or "amp" or "a":     amplify or reduce a movement (around the central position of a movement) [0..1..inf]
                - "tonus" or "ton" or "t":          idem amplify but start and stop position are keeped [0..1..inf]
        - bFlip: flip all right movement to left and left to right
    return an array [aNewKeyName, aNewTime, aNewPosition ]
    """
    aKeyName = arraytools.dup( aKeyNameParam );
    aTime = arraytools.dup( aTimeParam );
    aPosition = arraytools.dup( aPositionParam );
    retValue = [aKeyName, aTime, aPosition]; # in this case we really want a shared pointer on that array (just for convenience, we will continue to use the sub array)
    
    if( bFlip ):
        # exchange every key
        for nIdxJoint in range(len(aKeyName)):
            cFirstLetter = aKeyName[nIdxJoint][0];
            bSided = (cFirstLetter in ["L", "R"]);
            if( bSided ):
                if( cFirstLetter == "R" ):                
                    cFirstLetterFlip = "L"
                else:
                    cFirstLetterFlip = "R"
                                        
                aKeyName[nIdxJoint] = cFirstLetterFlip + aKeyName[nIdxJoint][1:];
            # invert some value
            #if( bSided and ("Yaw" in aKeyName[nIdxJoint] or "Roll" in aKeyName[nIdxJoint]) ):
            if( "Yaw" in aKeyName[nIdxJoint] or "Roll" in aKeyName[nIdxJoint] ): # we want to invert arms, but also NeckYaw or HeadRoll
                for nNumKey in range( 0, len( aPosition[nIdxJoint] ) ):
                    rVal = getTimelinePosition( aPosition[nIdxJoint], nNumKey );
                    rVal = -rVal;
                    setTimelinePosition( aPosition[nIdxJoint], nNumKey, rVal );

    
    for k,v in dictPositionModifier.iteritems():
        # for each joint to modify, we compute modifiers value, then we iterate in the timeline to find it
        rOffset = 0.;
        rMultiplier = 1.;
        rAmplify = 1.;
        rTonus = 1.;
        if( typetools.isArray(v) ):
            for i in range( 0, len( v ), 2 ):
                if( v[i][0] == 'o' ):
                    rOffset = v[i+1];
                elif( v[i][0] == 'm' ):
                    rMultiplier = v[i+1];
                elif( v[i][0] == 'a' ):
                    rAmplify = v[i+1];
                elif( v[i][0] == 't' ):
                    rTonus = v[i+1];
        else:
            rOffset = v;
        #~ print( "transformTimeline: joint(s) with '%s' are modified with: val(amp:%f, tonus:%f) * %f + %f" % (k, rAmplify, rTonus, rMultiplier, rOffset ) );
        for nIdxJoint in range( len(aKeyName) ):
            if( k in aKeyName[nIdxJoint] ):                
                if( rTonus != 1. or rAmplify != 1. ):
                    rFirstPos = getTimelinePosition( aPosition[nIdxJoint], 0 );
                    rLastPos = getTimelinePosition( aPosition[nIdxJoint], -1 );
                    rTotalTimeAnimation = aTime[nIdxJoint][-1]-aTime[nIdxJoint][0];
                    rAvgPos = 0.;
                    for i in range(len(aPosition[nIdxJoint])):
                        rAvgPos += getTimelinePosition( aPosition[nIdxJoint], i );
                    rAvgPos /= len( aPosition[nIdxJoint] );
                    #~ print( "transformTimeline: tonus and ampli modifiers: the joint '%s' has a position from %f to %f with an average of %f" % (aKeyName[nIdxJoint] , rFirstPos,rLastPos,rAvgPos) );
                    for nNumKey in range( 0, len( aPosition[nIdxJoint] ) ):
                        rVal = ( getTimelinePosition( aPosition[nIdxJoint], nNumKey ) * rMultiplier ) + rOffset;
                        if( nNumKey == 0 or nNumKey == ( len( aPosition[nIdxJoint] )-1 ) ):
                            rCurrentTonus = 1.; # extremum have full tonus
                        else:
                            rCurrentTonus = rTonus;
                        # compute full lazy position: it's a linear interpolation from begin position to median positin. It would be at median position around total time / 2
                        if( aTime[nIdxJoint][nNumKey] < rTotalTimeAnimation / 2 ):
                            rTimeRatio = aTime[nIdxJoint][nNumKey] / (rTotalTimeAnimation / 2.);
                            rFullLazyPositionAtThisTime = rFirstPos * (1.-rTimeRatio) + rAvgPos * rTimeRatio;
                        else:
                            rTimeRatio = (aTime[nIdxJoint][nNumKey]-(rTotalTimeAnimation / 2.)) / (rTotalTimeAnimation / 2.);
                            rFullLazyPositionAtThisTime = rAvgPos * (1.-rTimeRatio) + rLastPos * rTimeRatio;
                        rVal = (rVal*rCurrentTonus*rAmplify) + rFullLazyPositionAtThisTime*(1.-(rCurrentTonus*rAmplify));
                        #~ print( "'%s'.%d: %f => %f" % (aKeyName[nIdxJoint], nNumKey, getTimelinePosition( aPosition[nIdxJoint], nNumKey ), rVal) );
                        setTimelinePosition( aPosition[nIdxJoint], nNumKey, rVal );
                else:
                    for nNumKey in range( len( aPosition[nIdxJoint] ) ):
                        rVal = ( getTimelinePosition( aPosition[nIdxJoint], nNumKey ) * rMultiplier ) + rOffset;
                        setTimelinePosition( aPosition[nIdxJoint], nNumKey, rVal );
                        #~ print( "DBG: abcdk.motiontools.transformTimeline: new value of joint %s is %f" % (aKeyName[nIdxJoint], rVal) );                        

    return retValue;
# transformTimeline - end

def transformTimelineForRomeo( aKeyNameParam, aTimeParam, aPositionParam ):
    # Change joint Name
    for i in range(len(aKeyNameParam) ):
        # name conversion
        if( aKeyNameParam[i] == "HeadRoll" ):
            aKeyNameParam[i] = "NeckRoll";
        elif( aKeyNameParam[i] == "HeadPitch" ):
            aKeyNameParam[i] = "NeckPitch";            
        elif( aKeyNameParam[i] == "RShoulderRoll" ):
            aKeyNameParam[i] = "RShoulderYaw";
        elif( aKeyNameParam[i] == "RElbowRoll" ):
            aKeyNameParam[i] = "RElbowYaw";            
        elif( aKeyNameParam[i] == "RElbowYaw" ):
            aKeyNameParam[i] = "RElbowRoll";                        
            
    for i in range(len(aKeyNameParam) ):
        # range conversion
        if( aKeyNameParam[i] == "RWristRoll" ):
            for j in range( len( aPositionParam[i] ) ):
                onePos = aPositionParam[i][j];
                print( "onePos: %s" % onePos );
                #~ onePos[0] -= 0.5;
        elif( aKeyNameParam[i] == "RShoulderYaw" ):
            for j in range( len( aPositionParam[i] ) ):
                onePos = aPositionParam[i][j];
                print( "onePos: %s" % onePos );
                onePos[0] += 0.2;
        elif( aKeyNameParam[i] == "RElbowYaw" ):
            for j in range( len( aPositionParam[i] ) ):
                onePos = aPositionParam[i][j];
                print( "onePos: %s" % onePos );
                onePos[0] -= 0.15;
        elif( aKeyNameParam[i] == "RElbowRoll" ):
            for j in range( len( aPositionParam[i] ) ):
                onePos = aPositionParam[i][j];
                print( "onePos: %s" % onePos );
                onePos[0] += 0.1;
                
        # speed conversion
        # ralenti tout les temps / 2
        for j in range( len( aTimeParam[i] ) ):
            aTimeParam[i][j] *= 1.6;
        
            
    return [aKeyNameParam, aTimeParam, aPositionParam];    
# transformTimelineForRomeo - end

def filterTimeline( aTimeline, listJointToExclude ):
    """
    take a timeline and remove some joint
    - aTimeline: it's an array of [aKeyName, aTime, aPosition]
    - listJointToExclude: list of joint to exclude (without groups)
    """
    if( aTimeline == None ):
        print( "WRN: motiontools.filterTimeline: receiving a timeline set to None" );
        return;
    aKeyName, aTime, aPosition = aTimeline;
    #~ print( "aKeyName: %s" % aKeyName )
    #~ print( "aTime: %s" % aTime )
    #~ print( "aPosition: %s" % aPosition )
    i = 0;
    nNbrExcluded = 0;
    while i < len( aKeyName ):
        if( aKeyName[i] in listJointToExclude ):
            del aKeyName[i];
            del aTime[i];
            del aPosition[i];
            nNbrExcluded += 1;
        else:
            i += 1;
     #print( "INF: motiontools.filterTimeline: %d joint(s) removed" % nNbrExcluded );
# filterTimeline - end

def stretchTimelineTimes( times, rTimeRatio = 1. ):
    """
    change the way a movement is played by stretching the position in time of each keyframe
    - times: a list of list of time (one list per joint). [[t1_for_first_joint, t2_for_first_joint, ...], [t1_for_second_joint, t2_for_second_joint, ...] ]
               eg: [ [0.466667, 0.966667, 1.46667, 1.96667, 2.46667, 2.96667, 3.46667, 3.96667], [0.466667, 0.966667, 1.46667, 1.96667, 2.46667, 2.96667, 3.46667, 3.96667], [0.966667], [0.466667, 0.966667, 1.46667, 1.96667, 2.46667, 2.96667, 3.46667, 3.96667], [0.966667], [0.466667, 0.966667, 1.46667, 1.96667, 2.46667, 2.96667, 3.46667, 3.96667], [0.466667, 0.966667, 1.46667, 1.96667, 2.46667, 2.96667, 3.46667, 3.96667], [0.466667, 0.966667, 1.46667, 1.96667, 2.46667, 2.96667, 3.46667, 3.96667], [0.466667, 0.966667, 1.46667, 1.96667, 2.46667, 2.96667, 3.46667, 3.96667], [0.466667, 0.966667, 1.46667, 1.96667, 2.46667, 2.96667, 3.46667, 3.96667], [0.466667, 0.966667, 1.46667, 1.96667, 2.46667, 2.96667, 3.46667, 3.96667], [0.466667, 0.966667, 1.46667, 1.96667, 2.46667, 2.96667, 3.46667, 3.96667], [0.466667, 0.966667, 1.46667, 1.96667, 2.46667, 2.96667, 3.46667, 3.96667], [0.466667, 0.966667, 1.46667, 1.96667, 2.46667, 2.96667, 3.46667, 3.96667], [0.466667, 0.966667, 1.46667, 1.96667, 2.46667, 2.96667, 3.46667, 3.96667], [0.466667, 0.966667, 1.46667, 1.96667, 2.46667, 2.96667, 3.46667, 3.96667], [0.466667, 0.966667, 1.46667, 1.96667, 2.46667, 2.96667, 3.46667, 3.96667], ],
    - rTimeRatio: change of the time, so 2 => will be played half speed (the moves are slower)
    """
    out = []
    for time_one_joint in times:
        out.append( [] )
        for t in time_one_joint:
            out[-1].append(t*rTimeRatio)
    return out
# stretchTimelineTimes - end

def moveTorso( rX, rY = 0.5, rZ = 0.5, rAngleX = 0., bAbsolute = True ):
    """
    Use your legs joint to move your torso.
    - rX: front translation, [0;1], 0 is rear max
    - rY: side translation, [0;1], 0 is right max
    - rZ: elevation [0;1], 0 is bottom max # real elevation max is 13cm
    - rAngleX: tilt over X angle NDEV !
    - bAbsolute: absolute or move relative NDEV !
    WARNING: you can't have extremum X and Y, when Z is at extremum too
    """
    aJointName = [
        # movable joint:
        "LHipPitch",
        "RHipPitch",
        "LKneePitch",
        "RKneePitch",
        "LAnklePitch",
        "RAnklePitch",

        "LHipRoll",
        "RHipRoll",
        "LAnkleRoll",
        "RAnkleRoll",
        
        # joint to set to 0
        "LHipYawPitch",
    ];
    
    LHipPitch = 0;
    RHipPitch = 1;
    LKneePitch = 2;
    RKneePitch = 3;      
    LAnklePitch = 4;
    RAnklePitch = 5;
    LHipRoll = 6;
    RHipRoll = 7;
    LAnkleRoll = 8;
    RAnkleRoll = 9;
    nFirstJointToZeroes = 10;
    
    motion = naoqitools.myGetProxy( "ALMotion" );
    aValues = motion.getAngles( aJointName, True );
    aCurrentValues = aValues[:];
    #~ print( "aValues: %s" % aValues );
    
    if( not bAbsolute ):
        #~ rX = 2; # add current position ???
        pass
    
    for i in range( nFirstJointToZeroes, len(aJointName) ):
        aValues[i] = 0.;

    rRangeKnee = motion.getLimits( "LKneePitch")[0][1];
    rAngleZ = (1.-rZ)*rRangeKnee;
    
    rAngleX = (0.5-rX)*(rRangeKnee*0.3); # we can't use extreme angle for that
    
    rRangeRoll = motion.getLimits( "LHipRoll")[0][1]-motion.getLimits( "LHipRoll")[0][0];
    rAngleY = (0.5-rY)*rRangeRoll*0.65; # *0.65, because roll is not symetric
    
    rRatioHipComparedToAnkle = 0.379; # it's the way to report angle from knee to hip and ankle
    
    
    # moving X, is moving knee and pitch accordingly
    aValues[LHipPitch] = (-rAngleX*1.5)-(rAngleZ*rRatioHipComparedToAnkle);
    aValues[RHipPitch] = (-rAngleX*1.5)-(rAngleZ*rRatioHipComparedToAnkle);
    aValues[LKneePitch] = rAngleX+rAngleZ;
    aValues[RKneePitch] = rAngleX+rAngleZ;
    aValues[LAnklePitch] = (rAngleX*0.3)-(rAngleZ*(1.-rRatioHipComparedToAnkle));
    aValues[RAnklePitch] = (rAngleX*0.3)-(rAngleZ*(1.-rRatioHipComparedToAnkle));

    aValues[LHipRoll] = rAngleY;
    aValues[RHipRoll] = rAngleY;
    aValues[LAnkleRoll] = -rAngleY;
    aValues[RAnkleRoll] = -rAngleY;

    print( "rAngleX: %s" % rAngleX );    
    print( "rAngleY: %s" % rAngleY );    
    print( "rAngleZ: %s" % rAngleZ );

    #~ print( "aValues send: %s" % aValues );
    
    
    # we want to send movement not too fast, but we want to move every joint at the same speed, so we can't use "...WithSpeed"
    # so we need to compute an approximate distance of move to have a time
    rMaxDist = 0.01;
    for i in range( len( aValues ) ):
        rDist = abs( aValues[i] - aCurrentValues[i] );
        if( rDist > rMaxDist ):
            print( "for %d dist: %s maxdist was %f" % (i, rDist, rMaxDist) );
            rMaxDist = rDist;
    rTime = min( rMaxDist * 2., 1.5 );
    print( "rMaxDist: %s" % rMaxDist );
    print( "rTime: %s" % rTime );
    aValues = motion.angleInterpolation( aJointName, aValues, rTime, bAbsolute );
    
# moveTorso - end

def isDisplacing():
    """
    Is the robot walking ?
    """
    try:
        return naoqitools.myGetProxy( "ALMotion" ).moveIsActive(); # > 1.14
    except:
        return naoqitools.myGetProxy( "ALMotion" ).walkIsActive(); # < 1.14
    return False;
# isDisplacing - end

class HeadSnail:
    """
    Make a snail movement with the head from current position, increasing distance to initial position little by little
    """
    def __init__( self, rSpeed = 0.1, nAxisMask = 3 ):
        """
        - nAxisMask: 1: only Yaw, 2: only Pitch, 3: both
        """
        self.rSpeed = rSpeed;
        self.nAxisMask = nAxisMask;
        self.motion = naoqitools.myGetProxy( "ALMotion" );
        self.maxPos = self.motion.getLimits( "Head" );        
        self.reset();        
    # __init__ - end
        
    def reset( self ):
        self.initPos = self.motion.getAngles( "Head", True );
        #~ self.rDistance = 0.1;
        self.rAngle = 0.;
        self.motionTaskID = -1;
        self.bWasStopped = False;
        self.bFirstUpdate = True;
        self.nCptBodyMoves = 0; # after 3 turn, it's finished !
    # reset - end
    
    def update( self, rDistanceMax = 1.5, bEnableBodyMove = False ):
        """
        return True when finished
        """
        if( self.bFirstUpdate ):
            self.bFirstUpdate = False;
            # at launch, if head is near limits, we walk a bit, because, it will limits us !
            if( abs( self.initPos[0] ) > 2.0 and bEnableBodyMove ):
                rBias = -1.0;
                if( self.initPos[0] < 0 ):
                    rBias = -rBias;
                print( "INF: abcdk.motiontools.HeadSnail.update: too much near border, rotating body by bias: %f, initPos[0]: %f" % ( rBias, self.initPos[0] ) );
                self.motion.post.moveTo( 0, 0, -rBias );
                self.motion.angleInterpolationWithSpeed( "HeadYaw", self.initPos[0] + rBias, 0.2 );
                self.motion.waitUntilMoveIsFinished();
                self.initPos = self.motion.getAngles( "Head", True );
                time.sleep( 0.5 );
                return False;
        self.rAngle += 0.1;
        rDistance = self.rAngle*0.3/(2*math.pi);
        if( rDistance > rDistanceMax ):
            if( not bEnableBodyMove or self.nCptBodyMoves > 2 ):
                return True; # finito                
            rBodyAngleInc = 2.;
            if( self.initPos[0] < 0. ): # choose direction relative to where it could be
                rBodyAngleInc = - rBodyAngleInc;
            print( "INF: abcdk.motiontools.HeadSnail.update: not found and close to the border (2), rotating body by rBodyAngleInc: %f, initPos[0]: %f, nCptBodyMoves: %d" % ( rBodyAngleInc, self.initPos[0], self.nCptBodyMoves ) );
            self.motion.post.moveTo( 0, 0, rBodyAngleInc );
            self.motion.angleInterpolationWithSpeed( "HeadYaw", self.initPos[0], 0.1 );
            self.motion.waitUntilMoveIsFinished();
            self.nCptBodyMoves += 1;
            self.rAngle = 0.; # reset the snail
            return False;
        rPosX = self.initPos[0] + rDistance * math.cos( self.rAngle );
        rPosY = self.initPos[1] + rDistance * math.sin( self.rAngle );
        if( self.nAxisMask == 1 ):
            self.motionTaskID = self.motion.post.angleInterpolationWithSpeed( "HeadYaw", [rPosX], self.rSpeed );
        elif( self.nAxisMask == 2 ):
            self.motionTaskID = self.motion.post.angleInterpolationWithSpeed( "HeadPitch", [rPosY], self.rSpeed );
        elif( self.nAxisMask == 3 ):
            self.motionTaskID = self.motion.post.angleInterpolationWithSpeed( "Head", [rPosX, rPosY], self.rSpeed );
        self.motion.wait( self.motionTaskID, -1 );
        return self.bWasStopped;
    # update - end
    
    def stop( self ):
        """
        return True if stopped (was running) or False if already stopped
        """
        if( self.motionTaskID == -1 ):
            return False;
        self.bWasStopped = True;
        self.motion.stop( self.motionTaskID ); # TODO: kill move en cours
        return True;
# class HeadSnail - end

class HeadSeeker:
    """
    Pan head at different position to cover all range, beginning by current head position
    """
    def __init__( self, rAperture = 0.3 ):
        """
        - rAperture: efficient angle in each image, it depends of the object size and distance. It's an overlapping parameter.
        """
        self.rAperture = rAperture;
        self.bUseMotion = False;
        if( self.bUseMotion ):
            self.motion = naoqitools.myGetProxy( "ALMotion" );
        #~ self.maxPos = self.motion.getLimits( "Head" );
        self.reset();
    # __init__ - end
    
    def __del__( self ):
        self.stop();
        
    def reset( self ):
        self.motionTaskID = -1;
        self.bWasStopped = False;
        self.bFirstUpdate = True;
    # reset - end
    
    def run( self, rWaitTime = 1.5 ):
        """
        Make a full head seeking
        - rWaitTime: time to wait at each position.        
        """
        self.reset();
        bFinished = False;
        while( not bFinished ):
            bFinished = self.update();
            if( not bFinished ):
                time.sleep( rWaitTime );
        # while - end
        self.stop();
    # run - end
    
    def update( self ):
        """
        return True when finished
        """
        if( self.bFirstUpdate ):
            self.bFirstUpdate = False;
            # at launch, we compute an array of sector, and then we have to test each sector.            
            self.nHeadYawLimit = ( math.pi / 2 ) + 0.3; # limit to be not strange
            nNumSector = int(math.ceil((self.nHeadYawLimit*2) / self.rAperture));
            self.rStepAngle = (self.nHeadYawLimit*2) / nNumSector; # it's quite the same than aperture, but a bit different as we have a ceiling
            self.aSector = [False]*nNumSector;
            #~ nCurrentYaw = self.motion.getAngles( "HeadYaw", True )[0];
            nCurrentYaw = getAngles( "HeadYaw" )[0];
            self.nInitSector = (nCurrentYaw+self.nHeadYawLimit-self.rStepAngle/2)/self.rStepAngle; # previous is in this case the next to do
            # it's not a problem to have overflow <0 or >= len, as we just find for the nearest...
            self.nPreviousSector = self.nInitSector;
            self.nNbrSectorDone = 0;            
            print( "INF: abcdk.motiontools.HeadSeeker.update: nNumSector: %d, rStepAngle: %5.2f" % ( nNumSector, self.rStepAngle ) );
            
        # find next sector to test: nearest previous and init AND not used
        print( "INF: abcdk.motiontools.HeadSeeker.update: nPreviousSector = %d" % self.nPreviousSector );
        nNext = -1;
        nMinDist = 9999;
        for i in range( len( self.aSector ) ):
            if( not self.aSector[i] ): 
                nDist = abs( self.nPreviousSector - i );
                if( self.nNbrSectorDone < 4 ): # after some move, we don't care about dist to init
                    nDist+= abs( self.nInitSector - i )*4; # minimize dist to init
                if( nDist < nMinDist ):
                    nMinDist = nDist;
                    nNext = i;
        if( nNext == -1 ):
            return True; # finito
            
        rPosX = (nNext*self.rStepAngle)+(self.rStepAngle/2)-self.nHeadYawLimit;
        self.nPreviousSector = nNext;
        self.nNbrSectorDone += 1;
        print( "INF: abcdk.motiontools.HeadSeeker.update: nNext = %d => posX: %f" % (nNext,rPosX) );
        self.aSector[nNext] = True;
        
        if( self.bUseMotion ):
            self.motionTaskID = self.motion.post.angleInterpolationWithSpeed( "HeadYaw", [rPosX], 0.2 );
            self.motion.wait( self.motionTaskID, -1 );
            if( not self.bWasStopped ):
                time.sleep( 0.1 ); # wait for the robot to stabilize his movement
        else:
            mover.moveJointsWithSpeed( "HeadYaw", [rPosX], 0.2 );
        return self.bWasStopped;
    # update - end
    
    def stop( self ):
        """
        return True if stopped (was running) or False if already stopped
        """
        if( self.bWasStopped ):
            return False;
            
        if( self.bUseMotion ):
            if( self.motionTaskID == -1 ):
                return False;
        self.bWasStopped = True;
        time.sleep( 0.5 ); # be sure update() got it
        self.bWasStopped = True; 
        
        if( self.bUseMotion ):
            try:
                self.motion.stop( self.motionTaskID );
            except BaseException, err:
                print( "DBG: abcdk.motiontools.HeadSeeker.stop: if this error complain about a non existing task, it's ok: %s" % str(err) );
            self.motionTaskID = -1;
        else:
            mover.stopCurrentMovements( "Head" );
            mover.finishUse();
        return True;
# class HeadSeeker - end

class Panner:
    """
    Find object somewhere in the world, by moving and rotating head
    """
    def __init__( self, rPanSpeed = 0.04, rBaseHeadPitch = -0.05, rRangeHeadPitch = 0., rMaxHeadRotation = 1.5, bCenterHeadAtLaunch = False ):
        """
         - rPanSpeed: when panning, which speed to use ? (in % of max speed)
         - rBaseHeadPitch: Y central position when looking
         - rRangeHeadPitch: put something else than 0. to have a pitch balayage too
         - rMaxHeadRotation: you can limit head rotation for various reason (eg style)
        """
        #~ print( "INF: abcdk.motiontools.Panner.init: rPanSpeed: %5.2f, rBaseHeadPitch: %5.2f, rRangeHeadPitch: %5.2f, rMaxHeadRotation: %5.2f, bCenterHeadAtLaunch: %d" % ( rPanSpeed, rBaseHeadPitch , rRangeHeadPitch, rMaxHeadRotation, bCenterHeadAtLaunch ) );
        self.rPanSpeed = rPanSpeed; # when panning, which speed to use ?
        self.rBaseHeadPitch = rBaseHeadPitch;
        self.rRangeHeadPitch = rRangeHeadPitch;
        self.rMaxHeadRotation = rMaxHeadRotation;
        self.bCenterHeadAtLaunch = bCenterHeadAtLaunch;
        self.bMustStop = False;
        self.motion = naoqitools.myGetProxy( "ALMotion" );
        self.reset();
    # __init__ - end
    
    def __del__( self ):
        self.stop();
    
    def reset( self ):
        self.currentMotionTaskId = -1;
    
    def run( self ):
        print( "INF: abcdk.motiontools.Panner.run: begin" );
        self.bMustStop = False;
        nCptCircle = 0;
        nBeginSide = 1; # default is turning head and body to the left, but if head is in the right side at launch, then we'll begin by turning to the right
        if( self.motion.getAngles( "HeadYaw", True )[0] < 0. ):
            nBeginSide = -1;
        nCptPitch = 0;
        nForwardSign = 1;
        while( not self.bMustStop ):
            # head scanning
            nNumberOfDifferentPitch = 1;
            if( self.rRangeHeadPitch < 0.01 ):
                rDeltaPitch = 10; # dumb, big value
            else:
                nNumberOfPitchLine = 1+int(0.5+((self.rRangeHeadPitch*2)/0.4)); # 0.4 is a rough idea of the camera Y range
                rDeltaPitch = (self.rRangeHeadPitch*2) / (nNumberOfPitchLine-1);
                print( "INF: abcdk.motiontools.Panner.run: nNumberOfPitchLine: %d, rDeltaPitch: %f" % ( nNumberOfPitchLine, rDeltaPitch ) );
            rPitch = self.rBaseHeadPitch - self.rRangeHeadPitch;
            bFirstScan = True;
            nCptPitch = 0;
            while( ( rPitch <= self.rBaseHeadPitch+self.rRangeHeadPitch or bFirstScan ) and not self.bMustStop ):
                print( "INF: abcdk.motiontools.Panner.run: scanning at rPitch: %5.3f" % rPitch );
                # begin a bit at front (it's dumb to miss that point !)
                if( bFirstScan ):
                    if( self.bCenterHeadAtLaunch ):
                        self.currentMotionTaskId = self.motion.post.angleInterpolationWithSpeed( "Head", [0., rPitch], 0.2 );
                        self.motion.wait( self.currentMotionTaskId, 0 );
                    if( not self.bMustStop ):
                        time.sleep( 2.5 ); # time to think a bit, in the current position
                nBeginSideForRotation = nBeginSide;
                if( nCptCircle > 0 ):
                    nBeginSideForRotation *= -1; # first time we want to minimize rotation, but then we want to begin to test the orientation at beginning
                nInvRelatedToPitch = 1;
                if( ( nCptPitch % 2 ) == 1 ):
                    nInvRelatedToPitch = -1;
                if( not self.bMustStop ):
                    self.currentMotionTaskId = self.motion.post.angleInterpolationWithSpeed( "Head", [nInvRelatedToPitch*self.rMaxHeadRotation*nBeginSideForRotation, rPitch], 0.2 );
                    self.motion.wait( self.currentMotionTaskId, 0 );
                if( not self.bMustStop ):
                    self.currentMotionTaskId = self.motion.post.angleInterpolationWithSpeed( "Head", [-nInvRelatedToPitch*self.rMaxHeadRotation*nBeginSideForRotation, rPitch], self.rPanSpeed ); # put it slowly but not too slow, so the object would be saw a bit more centred
                    self.motion.wait( self.currentMotionTaskId, 0 );                
                rPitch += rDeltaPitch;
                bFirstScan = False;
                nCptPitch += 1;
            # while pitch - end
            if( not self.bMustStop ):
                time.sleep( 0.1 ); # wait a bit, because when no stiffness, it eat all threads !
                self.currentMotionTaskId = self.motion.post.angleInterpolationWithSpeed( "Head", [0., self.rBaseHeadPitch], 0.055 );
                rWalkRotateAngle = (self.rMaxHeadRotation*2)*0.7; # *0.7: for approximation errors and overlapping
                if( nCptCircle * rWalkRotateAngle < math.pi * 2 ):
                    # move a bit, in circle
                    self.motion.moveTo( 0.1, 0., rWalkRotateAngle*nBeginSide );
                    self.motion.waitUntilMoveIsFinished();
                    nCptCircle += 1;
                else:
                    # forward a bit - in front or rear flip/flop
                    nCptCircle = 0;
                    self.motion.moveTo( 0.3*nForwardSign, 0., 0. );
                    nForwardSign*= -1;
                    self.motion.waitUntilMoveIsFinished();
                    
        print( "INF: abcdk.motiontools.Panner.run: end" );
    # run - end

    def stop( self ):
        """
        Return true if it was running.
        """
        if( not self.bMustStop ):
            print( "INF: abcdk.motiontools.Panner: stopping..." );
            self.bMustStop = True;
            if( self.currentMotionTaskId != -1 ):
                try:
                    self.motion.stop( self.currentMotionTaskId );
                    self.currentMotionTaskId = -1;                    
                except: pass
                time.sleep( 0.2 ); # wait all moves are finished
            self.motion.stopMove(); # WARNING: This will stop all moves; even other than ours !!!
            time.sleep( 0.2 ); # wait all moves are finished
            return True;
        return False;
    # stop - end

# Panner - end

class HeadUserMove:
    """
    Ask the user to move NAO's head to show him something.    
    """
    def __init__( self, rTimeout = 3. ):
        """
        - rTimeout: wait time before timeout in sec
        """
        self.rTimeout = rTimeout;
        self.motion = naoqitools.myGetProxy( "ALMotion" );
        self.mem = naoqitools.myGetProxy( "ALMemory" );
        self.aJointMove = [JointMove( "HeadYaw" ), JointMove( "HeadPitch" ) ];
        self.reset();
    # __init__ - end
        
    def reset( self ):
        self.bUserWasMovingMe = False;
    # reset - end
    
    
    def start( self ):
        self.reset();
        self.timeLastMove = time.time();
        for jm in self.aJointMove:
            jm.start( bTotalSoft = True );
            
    # this method is of no use
    #~ def run( self ):
        #~ self.reset();
        #~ self.start();
        #~ bFinished = False;
        #~ while( not bFinished ):
            #~ bFinished = self.update();
            #~ if( not bFinished ):
                #~ time.sleep( self.rTimeout / 2 );
        #~ # while - end
    #~ # run - end
    
    def update( self ):
        """
        return the interaction state:
            0: the user doesn't begin to move the head
            1: the user is moving it
            2: the user has finished to move it (sent only once!)
            3: the user doesn't want to show it another things
        simple use:
        while True:
            ret = update();
            if( ret == 3 ):
                # finished
            if( ret == 2 ):
                # do something specific
        """
        time.sleep( 0.1 ); # minimal update, preventing user to pump all cpu
        # multi sampling
        bMoving = self.aJointMove[0].update() != 0 or self.aJointMove[1].update() != 0;
        if( self.bUserWasMovingMe and not bMoving ):
            # the user seems to have stopped moving us, but we don't want to bother him if in fact it has changed is mind or is slow
            print( "INF: HeadUserMove.update: user seems to stop, resampling..." );
            time.sleep( 0.5 );
            bMoving = self.aJointMove[0].update() != 0 or self.aJointMove[1].update() != 0;
        
        if( bMoving != self.bUserWasMovingMe ):
            self.bUserWasMovingMe = bMoving;
            # the state has changed
            if( not bMoving ):
                print( "INF: HeadUserMove.update: user has finished to move me..." );
                return 2; # action finished
            
        if( bMoving ):
            print( "INF: HeadUserMove.update: user is moving me..." );
            self.timeLastMove = time.time();
            return 1;
        try:
            strStopActionKeyName = "ApplicationHelper/StopAction";
            aLastStopAction_sec, aLastStopAction_usec = self.mem.getData( strStopActionKeyName );
            if( aLastStopAction_sec > self.timeLastMove ):
                print( "INF: HeadUserMove.update: the user ask for skipping... (aLastStopAction_sec: %d, timeLastMove: %d)" % (aLastStopAction_sec, self.timeLastMove) );
                return 3;            
        except BaseException, err:
            print( "INF: HeadUserMove.update: while handling optionnal user skipping, catching this error: %s" % err );
            # just in case, we don't have this marvelous "ApplicationHelp", just add this data in memory so the error "Data not found" won't be raise
            self.mem.insertData( strStopActionKeyName, [0,0] );
            
        if( time.time() - self.timeLastMove >= self.rTimeout ):
            print( "INF: HeadUserMove.update: the user doesn't want to use me... (time: %d, timeLastMove: %d)" % (time.time(), self.timeLastMove) );
            return 3;
        return 0;
    # update - end
# class HeadUserMove - end

class MoveCalibration:
    "a class handling move calibration"
    def __init__( self ):        
        self.reset();
        self.loadCalibration();
    # __init__ - end
    
    def reset( self ):
        self.rLeftRotationBias = 0.; # angle bias on a 360° left turn (in rad) (so if you put a positive value, it means that your robot has a tendency to turn left, and we'll limit its left turnation)
    
    def loadCalibration( self ):
        """
        load previous calibration (once in a boot)
        """        
        try:
            file = open( pathtools.getCachePath() + "abcdk_move_calibration.txt", "rt" ); # TODO: it should be relative to the BODY !!!
            buf = file.read();
            file.close();
            self.rLeftRotationBias = eval( buf );
            print( "INF: abcdk.motiontools.MoveCalibration.loadCalibration: rLeftRotationBias: %5.3f" % ( self.rLeftRotationBias ) );
            return True;            
        except BaseException, err:
            #~ print( "INF: abcdk.motiontools.MoveCalibration.loadCalibration: err: %s (loading defaults)" % (str(err) ) );
            self.reset();
            self.saveCalibration(); # create an empty file
        return False;
    # loadCalibration - end

    def saveCalibration( self ):
        """
        """        
        try:
            filetools.makedirsQuiet( pathtools.getCachePath() );
            file = open( pathtools.getCachePath() + "abcdk_move_calibration.txt", "wt" );

            file.write(str(self.rLeftRotationBias) );
            file.close();
            return True;            
        except BaseException, err:
            print( "ERR: abcdk.motiontools.MoveCalibration.saveCalibration: %s" % ( str(err) ) );
        return False;
    # loadCalibration - end
    
    def getMoveCalibrated( self, rX, rY, rTheta = 0. ):
        rNewX = rX;
        rNewY = rY;
        rNewTheta = rTheta - (self.rLeftRotationBias*rTheta/(2*math.pi));
        retVal = ( rNewX, rNewY, rNewTheta );
        print( "INF: abcdk.motiontools.MoveCalibration.getMoveCalibrated: %s => %s" % ( (rX, rY, rTheta), retVal ) );
        return retVal;
    # getMoveCalibrated - end
    
# class MoveCalibration - end

moveCalibration = MoveCalibration();


def getMoveCalibrated( rX, rY, rTheta = 0. ):
    """
    get a move order and tweak it relatively to the known default/bias of this robot
    """
    return moveCalibration.getMoveCalibrated( rX, rY, rTheta );
# getMoveCalibrated - end

class DCM_Mover:
    """
    an handy way to move joints:
        - with a motionlike grammar, 
        - but very efficiently:
          - without start lag
          - the method said it's finished, when it's really finished !
        - and with minimal thread (perhaps not less than motion, but not more!)        
    """
    
    def __init__( self, strDcmName = None ):
        if( strDcmName == None ):
            if( system.isOnRomeo() ):
                strDcmName = "DCM_motion";
            else:
                strDcmName = "DCM";
        try:
            motion = naoqitools.myGetProxy( "ALMotion" );
            self.aLimits = dict( zip(motion.getJointNames("Body"), motion.getLimits("Body") ) );
            self.dcm = naoqitools.myGetProxy( strDcmName );
            self.mem = naoqitools.myGetProxy( "ALMemory" );
        except BaseException, err:
            print( "WRN: abcdk.motiontools.DCM_Mover.init: initialisation error, mover won't be usable... (err:%s)" % str(err) );
        self.rCycleDCM = 0.010;
        self.bWasUsed = False;
        self.bMustStop = False;            
    # __init__ - end
    
    def __del__( self ):
        self.stopAll()
        self.finishUse();
    # __del__ - end
    
    def moveJoints( self, aName, aPos, aTime, bCheckParams = True, bWaitEnd = True, bWaitEndPosition = False, bVerbose = False ):
        """
        Move some joints at random position in some times:
        - aName: a joint or a group or a list of joint or group
        - aPos: a pos or a collection of pos (must be the same number as joints (exploded if in chain)
        - aTime: a time or a list of time
        - bCheckParams: to go faster, don't check values... !
        - bWaitEnd: wait the end of the move to leave
        - bWaitEndPosition: wait for the joint to be at the right position before leaving
        return a list of occuring clipped( eg: [0., 0.1, 0. ] => the second joint has been clipped of 0.1 or None on error or all those joint(s) are broken
        """
        if( bVerbose ):
            print( "%.02f: INF: abcdk.motiontools.DCM_Mover.moveJoints( %s, %s, %s, %s, bWaitEndPosition: %d )" % ( time.time(), aName, aPos, aTime, bCheckParams, bWaitEndPosition ) );
        self.bWasUsed = True;
        self.bMustStop = False;
        listJoints = poselibrary.PoseLibrary.getListJoints( aName );
        if( not isinstance( aPos, list ) and not isinstance( aPos, tuple ) ):
            aPos = [aPos]*len( listJoints );
            
        if( not isinstance( aTime, list ) ):
            aTime = [aTime]*len( listJoints );

        if( bCheckParams ):
            if( len( aPos ) != len( listJoints ) ):
                strError = "ERR: abcdk.motiontools.DCM_Mover.moveJoints: not the right number of position (%s) compared to joints number (%s)" % ( str(aPos),  str(listJoints) );
                raise Exception( strError );
                return None;
            if( len( aTime ) != len( listJoints ) ):
                strError = "ERR: abcdk.motiontools.DCM_Mover.moveJoints: not the right number of time (%s) compared to joints number (%s)" % ( str(aTime),  str(listJoints) );
                raise Exception( strError );
                return None;
                
        aClipRet = [0]*len(listJoints);
        rMaxTime = 0;
        if( self.bMustStop ):
            return None;
        for i, strJointName in enumerate( listJoints ):
            rTime = aTime[i];
            if( rTime > rMaxTime ):
                rMaxTime = rTime;
            nEndTime = self.dcm.getTime( int(rTime*1000) );
            strDeviceName = "Device/SubDeviceList/%s/Position/Actuator/Value" % strJointName;
            rPos = float( aPos[i] );
            if( bVerbose ):
                print( "%.02f: INF: abcdk.motiontools.DCM_Mover.moveJoints, sending to dcm: devicename: %s, rPos: %s, nEndTime: %s (curtime: %s)" % (time.time(), strDeviceName, rPos, nEndTime,self.dcm.getTime(0)) );
            self.dcm.set( [ strDeviceName, "ClearAll",  [[ rPos, nEndTime ]] ] ); # TODO: send in one only packet (faster!)
            if( False ):
                # test avec ajout d'envoi de vitesse, en plusse.
                rSign = 1.;
                motion = naoqitools.myGetProxy( "ALMotion" );
                if( rPos < motion.getAngles( strJointName, True )[0] ):
                    rSign = -1.;
                self.dcm.set( [ strDeviceName.replace("Position", "Speed" ), "ClearAll",  [[ rSign*0.5, nEndTime ]] ] );
                
            # todo: fill aClipRet
        
        if( bWaitEnd and not self.bMustStop ):
            #~ print( "%s: INF: abcdk.motiontools.DCM_Mover.moveJoints: waiting %fs for the command to finish..." % ( time.time(), rMaxTime ) );        
            rTimeForMoveAtBegin = 0.060; # each motors takes some time to begin to move
            rTimeToSlowDown = 0.060; # inertie to stop the motors # but it depends of the speed of the move !!! :(
            if( rMaxTime > 0.4 ):
                rTimeToSlowDown = 0.020; # slow down is faster when move is slower
            rTimeToTakenCommand = self.rCycleDCM; # add the max time for the command to be taken by the DCM
            time.sleep( rMaxTime + rTimeToTakenCommand + rTimeForMoveAtBegin + rTimeToSlowDown ); # WRN: here we don't exit the loop, even if the moves has been canceled by a stopMovement 
            
        bAllAreBroken = False;            
        if( bWaitEndPosition ):
            if( system.isOnRomeo() ):
                time.sleep( 0.25 ); # we've always at least half a second before moving!
            aPrevPos = [-421.]*len(listJoints);
            bAtLeastWaitingForOneThatMoves = True;
            if( bVerbose ):
                print( "%.02f: DBG: abcdk.motiontools.DCM_Mover.moveJoints: waiting for real end position of this list of joints: %s" % (time.time(), listJoints ) );
            while( not self.bMustStop and bAtLeastWaitingForOneThatMoves ):
                aCurrPos = getAngles(listJoints);
                bAtLeastWaitingForOneThatMoves = False;
                bAllAreBroken = True;                
                for i, strJointName in enumerate( listJoints ):
                    rWantedPos = float( aPos[i] );
                    rCurrPos = aCurrPos[i];
                    rPrevPos = aPrevPos[i];
                    if( rCurrPos == None ):
                        # this joint is not present at the moment ! we ask for a null movement
                        continue;                    
                    if( abs(rCurrPos - rWantedPos) > 0.05 ):
                        if( abs(rCurrPos - rPrevPos) < 0.001 ):
                            print( "%.02f: WRN: abcdk.motiontools.DCM_Mover.moveJoints: %s seems broken, skipping the wait for end position... (wanted: %5.3f, prev: %5.3f, cur: %5.3f)" % (time.time(), strJointName,rWantedPos,rPrevPos,rCurrPos) );
                        else:
                            if( bVerbose ):
                                print( "%.02f: INF: abcdk.motiontools.DCM_Mover.moveJoints: at the end, %s is not arrived at right position: wanted: %5.3f, cur: %5.3f, waiting a bit..." % ( time.time(), strJointName,rWantedPos,rCurrPos) );
                            bAtLeastWaitingForOneThatMoves = True;
                            bAllAreBroken = False;
                            break;
                    else:
                        bAllAreBroken = False;
                else:
                    # leave while
                    break;
                aPrevPos = aCurrPos;
                if( bAtLeastWaitingForOneThatMoves ):
                    time.sleep( 0.22 ); # needs at least one DCM refresh (two is better)
             # while - end
        if( bAllAreBroken ):
            return None;
        return aClipRet;
    # moveJoints - end
    
    def moveJointsWithSpeed( self, aName, aPos, aSpeedRatio, bCheckParams = True, bWaitEnd = True, bWaitEndPosition = False, bVerbose = False ):
        """
        cf moveJoints, but speed are in ratio of the max speed
        """
        if( bVerbose ):
            print( "%.02f: INF: abcdk.motiontools.DCM_Mover.moveJointsWithSpeed( %s, %s, %s, %s )" % ( time.time(), aName, aPos, aSpeedRatio, bCheckParams ) );
        
        listJoints = poselibrary.PoseLibrary.getListJoints( aName );
        if( not isinstance( aPos, list ) and not isinstance( aPos, tuple ) ):
            aPos = [aPos]*len( listJoints );
            
        if( not isinstance( aSpeedRatio, list ) ):
            aSpeedRatio = [aSpeedRatio]*len( listJoints );        
            
        #
        # convert speed ratio to time
        #
        aTime = [0.]*len(listJoints);
        
        arActualPos = getAngles(listJoints, proxyMem = self.mem );
        
        for i, strJointName in enumerate( listJoints ):
            rPos = aPos[i];            
            rActualPos = arActualPos[i];            
            if( rActualPos == None ):
                # this joint is not present at the moment ! we ask for a null movement
                rActualPos = rPos;
                aTime[i] = 0.;
            else:
                rSpeedLimit = self.aLimits[strJointName][2];                
                if( bVerbose ):
                    print( "%.02f: INF: abcdk.motiontools.DCM_Mover.moveJointsWithSpeed: computing move for '%s': required pos: %s, actual pos: %s, speed max: %s" % ( time.time(), strJointName, rPos, rActualPos, rSpeedLimit ) );
                if( bVerbose ):
                    if( abs(rActualPos) > 2*math.pi ):
                        print( "%.02f: INF: abcdk.motiontools.DCM_Mover.moveJointsWithSpeed: position for '%s' is very weird: %s, setting to 0." % (time.time(), strJointName, rActualPos ) );
                        rActualPos = 0.;
                rTimeSec = abs( rPos - rActualPos ) / (aSpeedRatio[i]*rSpeedLimit);
                aTime[i] = rTimeSec;
        return self.moveJoints( listJoints, aPos, aTime, bCheckParams = bCheckParams, bWaitEnd = bWaitEnd, bWaitEndPosition = bWaitEndPosition, bVerbose = bVerbose );
        
    # moveJointsWithSpeed - end
    
    def getAngles( self, aName, bUseSensor = True ):
        """
        Return current sensor position
        - aName: a joint or a group or a list of joint or group
        - bUseSensor: if false, send actuator command instead (a bit silly...)
        """
        listJoints = poselibrary.PoseLibrary.getListJoints( aName );
        if( bUseSensor ):
            strTemplate = getStringTemplateSensor();
        else:
            strTemplate = getStringTemplateActuator();
            
        aListSensorNameMem = [];
        for strJointName in listJoints:
            aListSensorNameMem.append( strTemplate % strJointName );
        return self.mem.getListData( aListSensorNameMem );            
    # getAngles - end
    
    def stopAll( self ):
        """
        Stop movements of all joints!
        """
        self.bMustStop = True;
        return self.stopCurrentMovements( "Body" );
    # stopAll - end
    
    def stopCurrentMovements( self, aName ):
        """
        Stop all movements on some joints (the only way to kill some moveJoints previously launched before wait to the end)
        - aName: a joint or a group or a list of joint or group
        """
        if( not self.bWasUsed ):
            return;
        listJoints = poselibrary.PoseLibrary.getListJoints( aName );
        
        # the only way is to send current pos now with a clear all (?) sounds weird
        
        arActualPos = getAngles(listJoints, proxyMem = self.mem );
        
        nEndTime = self.dcm.getTime( 0 );
        for i, strJointName in enumerate( listJoints ):
            strDeviceName = "Device/SubDeviceList/%s/Position/Actuator/Value" % strJointName;
            rPos = arActualPos[i];
            self.dcm.set( [ strDeviceName, "ClearAll",  [[ rPos, nEndTime ]] ] );
        time.sleep( self.rCycleDCM ); # wait the time for the command to be taken
    # stopCurrentMovements - end
    
    def sendCurrentSensorPositionToMotion(self):
        """
        see stopUseMovers for use
        # It takes quite not a lot of time (compared to a moves), so you could call it even if not very usefull (<2ms)
        - TODO: reset only moved joints !!! (it could be better, but...) (resetting only head seems not to be faster than the full body)
        """
        print( "%5.3fs: DBG: abcdk.motiontools.DCM_Mover.sendCurrentSensorPositionToMotion: begin" % time.time() );
        naoqitools.myGetProxy( "ALMotion" )._resetMotionCommandModelToSensors( "Body" );
        #~ print( "%5.3fs: DBG: abcdk.motiontools.DCM_Mover.sendCurrentSensorPositionToMotion: end" % time.time() );
    # sendCurrentSensorPositionToMotion - end
    
    def finishUse(self):
        """
        Tell the system we won't use the Mover for some time
        To be called before calling motion moves to avoid jerky moves on moved joints
        """
        if( self.bWasUsed ):
            self.bWasUsed = False;
            print( "%.02f: DBG: abcdk.motiontools.DCM_Mover.finishUse" % time.time() );
            return self.sendCurrentSensorPositionToMotion();
        return False;
    # finishUse - end

# class DCM_Mover - end

mover = DCM_Mover();

def getLastPositionFromAnimation( animation ):
    return getLastPositionFromAnimation3( animation[0], animation[1], animation[2] );
# getLastPositionFromAnimation - end
    
def getLastPositionFromAnimation3( names, times, keys ):
    """
    Take an animation, and compute the end position of every joint in the animation
    """
    aLastPosition = dict(); # for each joint, his last position
    
    for i, strJoint in enumerate( names ):
        lastKey = keys[i][len(times[i])-1];
        rPos, splinesInfo1,splinesInfo2 = lastKey;    
        aLastPosition[strJoint] = rPos;
    return aLastPosition;
# getLastPositionFromAnimation3 - end

#~ names = [ "RShoulderRoll",   "RWristYaw" ];
#~ times = [   [ 1.40000, 2.60000],   [ 1.40000, 2.60000] ];
#~ keys = [   [ [ -0.11663, [ 3, -0.46667, 0.00000], [ 3, 0.40000, 0.00000]], [ -0.40042, [ 3, -0.40000, 0.00000], [ 3, 0.00000, 0.00000]]]   ,         [ [ 0.08279, [ 3, -0.46667, 0.00000], [ 3, 0.40000, 0.00000]], [ -0.00004, [ 3, -0.40000, 0.00000], [ 3, 0.00000, 0.00000]]]    ]
#~ print( getLastPositionFromAnimation3( names, times, keys ) );

global_timesetFallManagerState_LastErrorOutputed = time.time();
def setFallManagerState( bEnableOrDisable = True ):
    """
    Change the state of the fall management
    """
    try:
        uah = naoqitools.myGetProxy( "UsageApplicationHelper", bQuiet = True );
        uah.setDeveloperStuffs( True );
    except BaseException, err:
        global global_timesetFallManagerState_LastErrorOutputed;
        if( time.time() - global_timesetFallManagerState_LastErrorOutputed > 60. ):
            print( "ERR: sorry no application helper found, you could feel some problems... (err: %s)" % err );
            global_timesetFallManagerState_LastErrorOutputed = time.time();
    motion = naoqitools.myGetProxy( "ALMotion" );
    motion.setMotionConfig( [["ENABLE_DISACTIVATION_OF_FALL_MANAGER", True]] );
    motion.setFallManagerEnabled( bEnableOrDisable );
# setFallManagerState - end

def getNominalCurrent( strJoint ):
    """
    get the theoric nominal current of each motor. 
    TODO: to move somewhere else ?
    """
    aNominalCurrent_Romeo = {
        "NeckYaw": 2.79,
        "NeckPitch": 2.79,
        "HeadPitch": 0.59,
        "HeadRoll": 0.59,
        "LShoulderPitch": 2.79,
        "LShoulderYaw": 2.79,
        "LElbowRoll": 2.79,
        "LElbowYaw": 2.79,
        "LWristRoll": 0.59,
        "LWristYaw": 0.27,
        "LWristPitch": 0.27,
        "LHand": 0.50,
        "TrunkYaw": 6.24,
        "LHipYaw": 0.45,
        "LHipRoll": 9.51,
        "LHipPitch": 9.51,
        "LKneePitch":9.51,
        "LAnklePitch":9.51,
        "LAnkleRoll":9.51,
        "RHipYaw": 0.45,
        "RHipRoll": 9.51,
        "RHipPitch": 9.51,
        "RKneePitch": 9.51,
        "RAnklePitch": 9.51,
        "RAnkleRoll": 9.51,
        "RShoulderPitch": 2.79,
        "RShoulderYaw": 2.79,
        "RElbowRoll": 2.79,
        "RElbowYaw": 2.79,
        "RWristRoll": 0.59,
        "RWristYaw": 0.27,
        "RWristPitch": 0.27,
        "RHand": 0.50,
    };
    
    if( system.isOnRomeo() ):
        return aNominalCurrent_Romeo[strJoint] / 3.; # because I enter 3*nominal, dumb...
        
    return aNominalCurrent_Romeo[strJoint] / 3.; # because I enter 3*nominal, dumb...
    
    
    
# getNominalCurrent - end
    

class ConsumptionWatcher:
    def __init__( self, astrListJointToWatch ):
        self.aListJoint = astrListJointToWatch;
        self.arNominal = [];
        self.aListKeyName = [];
        for joint in self.aListJoint:
            self.arNominal.append( getNominalCurrent( joint ) );
            self.aListKeyName.append( "Device/SubDeviceList/%s/ElectricCurrent/Sensor/Value" % joint );
        self.mem = naoqitools.myGetProxy( "ALMemory" );
        self.mutex = mutex.mutex();
        self.reset();        
    # __init__ - end
    
    def reset( self ):
        """
        reset all the measurement
        """
        if( self.mutex.testandset() == False ):
            print( "INF: abcdk.motiontools.ConsumptionWatcher.reset: locked, waiting..." );
            time.sleep( 0.001 );
        self.arSumCurrent = [0]*len(self.aListJoint);
        self.arCurrentPeak = [0]*len(self.aListJoint);
        self.arSumNominal = [0]*len(self.aListJoint);
        self.arTimeUsed = [0]*len(self.aListJoint);
        self.timeBegin = time.time();
        self.timeLast = time.time();
        self.nNbrSampling = 0;
        self.mutex.unlock();
    
    def update( self ):
        """
        sample the instantaneous consumption
        """
        if( self.mutex.testandset() == False ):
            print( "INF: abcdk.motiontools.ConsumptionWatcher.update: locked, waiting..." );
            time.sleep( 0.001 );        
        arCurrent = self.mem.getListData( self.aListKeyName );
        timeNow = time.time();
        rDurationSampling = timeNow - self.timeLast;
        self.timeLast = timeNow;
        #~ print( "INF: abcdk.motiontools.ConsumptionWatcher.update: rDurationSampling: %s" % rDurationSampling );
        for i, joint in enumerate( self.aListJoint ):
            rCurrent = abs( arCurrent[i] );
            #~ print( "DBG: abcdk.motiontools.ConsumptionWatcher.update: %s: conso: %s, nominal: %s" % (joint, rCurrent,self.arNominal[i]) );
            if( rCurrent != None ):
                if( False ):
                    self.arSumCurrent[i] += rCurrent ** 2; # *rDurationSampling # here we take in account the time, but in fact, there's no needs, no ? and it's wrong, as when we're called slowly it's not really the consumption on the last usage time
                    self.arSumNominal[i] += self.arNominal[i] ** 2; # *rDurationSampling
                    if( self.arSumNominal[i] > 1000 ):
                        self.arSumCurrent[i] /= 3.;
                        self.arSumNominal[i] /= 3.;
                    if( rCurrent != 0. ):
                        self.arTimeUsed[i] += rDurationSampling;                
                        if( rCurrent > self.arCurrentPeak[i] ):
                            self.arCurrentPeak[i] = rCurrent;
                if( True ):
                    rAmorti = 1/501;
                    self.arSumCurrent[i] = self.arSumCurrent[i] * (1.-rAmorti) + (rCurrent ** 2)*rAmorti;
                    self.arSumNominal[i] = self.arSumNominal[i] * (1.-rAmorti) + (self.arNominal[i] ** 2)*rAmorti;
        self.nNbrSampling += 1;
        self.mutex.unlock();
    # update - end
    
    def getConsumption( self, strJoint ):
        """
        get the total consumption of one joint        
        return:
            [sum_consumption, sum_consumption_nominal_on_same_time, used_time, nbr_sampling, total_measured_time, peak value]        
        """
        i = self.aListJoint.index(strJoint);
        if( self.mutex.testandset() == False ):
            print( "INF: abcdk.motiontools.ConsumptionWatcher.getConsumption: locked, waiting..." );
            time.sleep( 0.001 );        
        aRet = [self.arSumCurrent[i], self.arSumNominal[i], self.arTimeUsed[i], self.nNbrSampling, time.time() - self.timeBegin, self.arCurrentPeak[i]];
        self.mutex.unlock();
        return aRet;
    # getConsumption - end    
# class ConsumptionWatcher - end

class EyesMover:
    def __init__(self, strIP = "", bVerbose = False ):
        if( not system.isOnRomeo() ):
            return;
        print( "INF: abcdk.motiontools.EyesMover: creating an instance at %s" % str(self) );
        
        # some constants:
        self.rDistTwoEyes = 0.065;
        self.timeBeforeMove = time.time();
        
        self.bVerbose = bVerbose;
        strDCMForEyes= "DCM_video";
        try:
            if( strIP == "" ):
                self.dcm = naoqitools.myGetProxy( strDCMForEyes );
            else:
                if( bVerbose ):
                    print( "INF: abcdk.motiontools.EyesMover: connecting to '%s'" % (strIP) );
                self.dcm = naoqitools.myGetProxy( strDCMForEyes, strHostName=strIP );
        except BaseException, err:
            print( "ERR: abcdk.motiontools.EyesMover: err: %s" % str(err) );
        if( self.dcm == None ):
            print( "WRN: abcdk.motiontools.EyesMover: No usable DCM found, you can't move the eyes." );
            return;
        self.listJoint = ["LEyeYaw", "LEyePitch", "REyeYaw", "REyePitch" ];
        listDevice = [];
        self.listDeviceSensorPos = [];        
        listDeviceHardness = [];
        for strJoint in self.listJoint:
            listDevice.append( "%s/Position/Actuator/Value" % strJoint );
            listDeviceHardness.append( "%s/Hardness/Actuator/Value" % strJoint );
            self.listDeviceSensorPos.append( "Device/SubDeviceList/%s/Position/Sensor/Value" % strJoint );            
        self.strAliasName = "EyesMotors";
        self.strAliasNameHardness = "EyesMotorsHardness";
        self.dcm.createAlias( [self.strAliasName,listDevice] );
        self.dcm.createAlias( [self.strAliasNameHardness,listDeviceHardness] );
        self.mem = naoqitools.myGetProxy( "ALMemory_video" );
        if( bVerbose ):
            print( "INF: abcdk.motiontools.EyesMover: object created, connected to '%s' (empty=localhost)" % strIP );
        self.aLastPos = [0.]*4; # store the last command, so we could read it (poor method)
        self.aOffsetCalibration = [0.] * 2; # the offset to add to the right eyes to match the left
        
    def setVerbose( self, bEnable=True):
        self.bVerbose = bEnable
                
    def setOffsetCalibration( self, aNewOffset ):
        print( "INF: abcdk.motiontools.EyesMover.setOffsetCalibration: setting to %s (instance at %s)" % (aNewOffset, str(self)) );
        self.aOffsetCalibration = aNewOffset;
        
    def setStiffnessesFuse( self, aVal, bUseOldCommand = False ):
        """
        an ugly way to change the eyes stiffness, using fuse and shell call
        """
        if( bUseOldCommand ):
            for i in range( 4):
                strCommand = "echo %s > /tmp/fuse/BusUSBRomeo/FaceBoard/FaceBoard.Hardness%d.Actuator" % (aVal[i], i+1);
                os.system( "ssh nao@198.18.0.3 \"%s\"" % strCommand );
        else:
            for name in ["REyeYaw", "REyePitch", "LEyeYaw", "LEyePitch"]:
                strCommand = "echo %s > /tmp/fuse/BusTypeNone/%s/%s.Hardness.Actuator" % (aVal[i], name, name);
                os.system( "ssh nao@198.18.0.3 \"%s\"" % strCommand );        
    
    def setStiffnesses( self, aVal, rTime = 0.2, bWaitEnd = True ):                
        commands = [];
        nTime = self.dcm.getTime(int(rTime*1000));
        for i in range( 4 ):
            commands.append( [[aVal[i],nTime]] );
        #~ print commands
        self.dcm.setAlias( [self.strAliasNameHardness, "Merge", "time-mixed", commands] );
        if( bWaitEnd ):
            time.sleep( rTime );
        if( 0 ):
            # sadly our current version handle badly the stiffness thru the dcm, so sad...
            self.setStiffnessesFuse( aVal );
        
        
    def setStiffness( self, rVal = 1., rTime = 0.2, bWaitEnd = True ):
        if( self.bVerbose ):
            print( "INF: abcdk.motiontools.EyesMover.setStiffness: setting stiffness..." );
            
        return self.setStiffnesses( [rVal,rVal,rVal,rVal], rTime = rTime, bWaitEnd = bWaitEnd );
            
    def getPos( self ):
        """
        Get the position, from DCM.
        return [left_eyes_x, left_eyes_y, right_eyes_x, right_eyes_y]
        """
        #return self.aLastPos;
        aCur = self.mem.getListData( self.listDeviceSensorPos );
        # invert top and bottom, so positive is to the bottom
        aCur[1] =-aCur[1];
        aCur[3] =-aCur[3];
        return aCur;
    # getPos - end
        
    def move( self, aPos, rTime=0.2, bRelative = False, bWaitEnd = True, bCanBeInhibate = True ):
        """
        Move eyes to a position in some time
        - aPos: [left_eyes_x, left_eyes_y, right_eyes_x, right_eyes_y]; X: to the left, Y: to the bottom
        - rTime: time to move the eyes (in sec)
        """
        if( bCanBeInhibate and time.time() < self.timeBeforeMove ):
            print( "WRN: abcdk.motiontools.EyesMover.move: move disabled until %s (now is: %s)" % (self.timeBeforeMove, time.time() ) );
            return;
        
        aPos2 = aPos[:];
        if( bRelative ):
            aCur = self.getPos();
            for i in range(4):
                aPos2[i] += aCur[i];
            
        # max ranging
        rMax = 0.3;
        for i in range( 4 ):            
            if( aPos2[i] < -rMax ):
                print( "INF: abcdk.motiontools.EyesMover.move: clipping %dth axis: %f=>%f" % (i, aPos2[i], -rMax) );
                aPos2[i] = -rMax;
            elif( aPos2[i] > rMax ):
                print( "INF: abcdk.motiontools.EyesMover.move: clipping %dth axis: %f=>%f" % (i, aPos2[i], rMax) );
                aPos2[i] = rMax;
        if( self.bVerbose ):
            print( "INF: abcdk.motiontools.EyesMover.move: moving to %s in %ss (bRelative=%s) (instance at %s)" % ( aPos2, rTime, bRelative, str(self) ) );
        commands = [];
        try:
            nTime = self.dcm.getTime(int(rTime*1000));
        except BaseException, err:
            print( "ERR: abcdk.motiontools.EyesMover.move: dcm not found ?, err: %s" % str(err) );
            return;
        for rVal in aPos2:
            commands.append( [[rVal,nTime]] );
        if( self.bVerbose ):
            print( "DBG: abcdk.motiontools.EyesMover.move: aOffsetCalibration: %s" % self.aOffsetCalibration );
        for i in range( 2 ):
            commands[i+2][0][0] += self.aOffsetCalibration[i];
            
        # invert top and bottom, so positive is to the bottom
        commands[1][0][0] =-commands[1][0][0];
        commands[3][0][0] =-commands[3][0][0];
        if( self.bVerbose ):
            print( "DBG: abcdk.motiontools.EyesMover.move: commands: %s" % commands );
        self.dcm.setAlias( [self.strAliasName, "Merge", "time-mixed", commands] );
        if( bWaitEnd ):
            time.sleep( rTime );
            if( self.bVerbose ):
                print( "INF: abcdk.motiontools.EyesMover.move: moving to %s in %ss: finished" % ( aPos2, rTime ) );        
        self.aLastPos = aPos2;
        #~ setEyesPosition( aPos2 ); # pour probleme de singleton pas unique $$$$
    # move - end
    
    def moveLeft( self, aPos, rTime = 0.2, rDist=1., bRelative = False, bWaitEnd = True ):
        """
        move the left eyes to a certain position, and move the right eyes  according to the looking stuff
        - aPos: X and Y of the left eyes; X: to the left, Y: to the bottom
        - rDist: distance of the looked stuff - center of attention (in meter)
        """
        aPos2 = aPos[:];
        print( "INF: abcdk.motiontools.EyesMover.moveLeft: moving to %s; rTime: %5.2f; rDist: %5.2f (bRelative=%s)" % ( aPos2, rTime, rDist, bRelative ) );
        if( bRelative ):
            aCur = self.getPos();
            print( "INF: abcdk.motiontools.EyesMover.moveLeft: current eyes position: %s" % aCur );            
            aPos2[0] += aCur[0];
            aPos2[1] += aCur[1];
            
        # compute the X Right eye from the left one        
        rLeftEyeAngle = math.pi/2+aPos2[0];
        rThirdAngle = math.atan2( self.rDistTwoEyes, rDist );
        rXRAngle = math.pi - rLeftEyeAngle - rThirdAngle;
        rXR = math.pi/2-rXRAngle;
        
        rYR=aPos2[1]; # simple copy
        
        aPos2.append( rXR );
        aPos2.append( rYR );
        return self.move( aPos = aPos2, rTime = rTime, bRelative = False, bWaitEnd = bWaitEnd );
    # moveLeft - end
    
    def lookAt3D( self, aPos, rTime = 0.5, rTimeStay = 3. ):
        """
        give a 3d point to look at, this method has the priority over anyone else, because it's used for animation.
        - aPos: the position to look in robot eyes space (different than the robot space): X: to the left, Y: to the bottom, Z: distance
                    if just the X and Y are provided, then the distance is set to be at 1.0m
        - rTime: time to go to the position
        - rTimeStay: time to stay there
        """
        if( len(aPos) > 2 ):
            rDist = aPos[2];
        else:
            rDist = 1.0;
            
        rY = math.atan2( aPos[1], rDist );
        
        ptX = aPos[0];
        
        # TODO: we could factorise those 4 cases but my brain is so old...
        if( ptX > self.rDistTwoEyes / 2 ):
            rXL = math.pi/2 - math.atan2( rDist, ptX - self.rDistTwoEyes / 2 );
        else:
            rXL = math.pi/2 - math.atan2( rDist, ptX - self.rDistTwoEyes / 2 );
        if( ptX < -self.rDistTwoEyes / 2 ):
            rXR = math.pi/2 - math.atan2( rDist, ptX + self.rDistTwoEyes / 2 );
        else:
            rXR = math.pi/2 - math.atan2( rDist, ptX + self.rDistTwoEyes / 2 );
            
        print( "INF: abcdk.motiontools.EyesMover.lookAt3D: looking at %s => %s" % (aPos,  [rXL, rY, rXR, rY]) );
        self.timeBeforeMove = time.time() + rTimeStay; # block other moves but from this method
        return self.move( aPos = [rXL, rY, rXR, rY], rTime = rTime, bRelative = False, bWaitEnd = False, bCanBeInhibate = False );
        
    # lookAt3D - end
    
# class EyesMover - end

eyesMover = EyesMover();

#~ global_eyesPosition = [0.]*4
#~ def getEyesPosition():
    # can't register with the singleton from some different boxes ?!? TODO: why ? reloading probleme ? $$$$
    #~ return eyesMover.getPos();
    #~ global global_eyesPosition;
    #~ return global_eyesPosition;
    
#~ def setEyesPosition(aPos):
    # can't register with the singleton from some different boxes ?!? TODO: why ? reloading probleme ? $$$$
    #~ return eyesMover._setPos(aPos);
    #~ global global_eyesPosition;
    #~ global_eyesPosition = aPos;
    
def setPositionDcm( strJointName, rPos = 0., rTime = 1., bDontWait = False ):
    "put a position using the dcm"
    if( system.isOnRomeo() ):
        strDcmName = "DCM_motion";
    else:
        strDcmName = "DCM";
    dcm = naoqitools.myGetProxy( strDcmName );
    nEndTime = dcm.getTime( int(rTime*1000) );
    strDeviceName = "Device/SubDeviceList/%s/Position/Actuator/Value" % strJointName;
    rPos = float( rPos );
    dcm.set( [ strDeviceName, "ClearAll",  [[ rPos, nEndTime ]] ] ); # TODO: send in one only packet (faster!)    
    if( not bDontWait ):
        time.sleep( rTime );
# setPositionDcm - end    

def setStiffnessDcm(strJointName, rValue, rTime = 1., bDontWait = False ):
    """
    set a hardness using the dcm
    - rValue could be set to -1 to use stiffness very limp (no feedback power into motor)
    """
    if( system.isOnRomeo() ):
        strDcmName = "DCM_motion";
    else:
        strDcmName = "DCM";
    dcm = naoqitools.myGetProxy( strDcmName );
    nEndTime = dcm.getTime( int(rTime*1000) );
    strDeviceName = "Device/SubDeviceList/%s/Hardness/Actuator/Value" % strJointName;
    rValue = float( rValue );
    dcm.set( [ strDeviceName, "ClearAll",  [[ rValue, nEndTime ]] ] ); # TODO: send in one only packet (faster!)    
    if( not bDontWait ):
        time.sleep( rTime );
        
    pass
# setStiffnessDcm - end


def openHand( strSide = "L", bRomeoTricks = True ):
    """
    Really open hand, even on romeo
    - strSide: "L", "LHand", "l", "Left", "left" ...
    """
    strHand = strSide[0].upper() + "Hand";
    motion = naoqitools.myGetProxy( "ALMotion" )
    if( motion.getAngles( strHand, True )[0] > 0.9 ):
        return; # do nothing...
    motion.setStiffnesses( strHand, 0. );
    motion.angleInterpolation( strHand, 0.1, 0.3, True );
    motion.setStiffnesses( strHand, 1. );
    motion.angleInterpolation( strHand, 1., 1., True );    
# openHand - end

def getDistanceBetweenTwoHands( nOnlyAxisNum = None):
    """
    return the distance in meters of the two hands (usefull to know if you pick something with two hands)
    - nOnlyAxisNum: specify an axis (None => 3 axis, 0 => X, 1 => Y, 2 => Z)
    """
    import numeric
    motion = naoqitools.myGetProxy( "ALMotion" )
    kSpaceTorso = 0
    aPosL = motion.getPosition( "LHand", kSpaceTorso, True )
    aPosR = motion.getPosition( "RHand", kSpaceTorso, True )
    
    if nOnlyAxisNum == None :
        rVal = numeric.dist3D( aPosL, aPosR )
    else:
        rVal = abs(aPosL[nOnlyAxisNum] - aPosR[nOnlyAxisNum])
    return rVal
# getDistanceBetweenTwoHands - end


    
def autoTest_eyesMover():
    if( not system.isOnRomeo() ):
        return;
    eyesMover.lookAt3D( [0.,0.] );
    eyesMover.lookAt3D( [eyesMover.rDistTwoEyes,0.] );
    eyesMover.lookAt3D( [1.,0.] );
    eyesMover.lookAt3D( [-1.,0.] );

def autoTest_Panner():
    navigate = Panner();
    navigate.run();


def autoTest():
    test.activateAutoTestOption();

    #~ autoTest_Hand();
    #~ autoTest_Panner();
    print "getCurrentPosture: " + getCurrentPosture();    
    autoTest_eyesMover();
# autoTest - end

if( __name__ == "__main__" ):
    autoTest();

#~ rDist = 1.;
#~ rDistTwoEyes = 0.065;
#~ aPos = [-0.0]
#~ rLeftEyeAngle = math.pi/2+aPos[0];
#~ rThirdAngle = math.atan2( rDistTwoEyes, rDist );
#~ rXRAngle = math.pi - rLeftEyeAngle - rThirdAngle;
#~ rXR = math.pi/2-rXRAngle;
#~ print rXR
