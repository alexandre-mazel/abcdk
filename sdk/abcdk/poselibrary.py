# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Pose Library
# Author A. Mazel
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Pose Library: handle position, compare between them, fusion them..."

print( "importing abcdk.poselibrary" );

import math

import arraytools
import debug
import naoqitools
import numeric
import stringtools
import system
import test
import typetools

global_dicoGroupDefinition = None; # bit precalc
class PoseLibrary():
  "A module to store Nao position, compare position between them and help user use them"

  @staticmethod
  def getCurrentPosition():
    "get a list of joint name and their current position value in radians ['HeadYaw'=1.0; 'HeadPitch'=1.0;... work even if no stiffness"
    motion = naoqitools.myGetProxy( "ALMotion" );
    listJointName = motion.getJointNames('Body');
    listJointName.remove( "RHipYawPitch" ); # when using dcm: remove this joint
    listJointsDCMValue = []; # la liste des clés de chaque joint dans la stm
    for strJointName in listJointName:
      listJointsDCMValue.append( "Device/SubDeviceList/%s/Position/Sensor/Value" % strJointName );
    # add TorsoX and Y and AccZ
    listJointsDCMValue.append( "Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value" );
    listJointsDCMValue.append( "Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value" );
    listJointsDCMValue.append( "Device/SubDeviceList/InertialSensor/AccZ/Sensor/Value" );
    stm = naoqitools.myGetProxy( "ALMemory" );
    listJointValue = stm.getListData( listJointsDCMValue );
    dicoConstructed = dict([]);
    for i in range( len( listJointName ) ):
      dicoConstructed[listJointName[i]] = listJointValue[i];
    dicoConstructed['TorsoX'] = listJointValue[len( listJointName )];
    dicoConstructed['TorsoY'] = listJointValue[len( listJointName ) + 1];
    dicoConstructed['TorsoAccZ'] = listJointValue[len( listJointName ) + 2] * math.pi / 180;
#    debug.debug( "poselibrary::PoseLibrary::getCurrentPosition: " + stringtools.dictionnaryToString( dicoConstructed ) );
    return dicoConstructed;
  # getJointPos - end

  @staticmethod
  def getGroupDefinition():
    "get list of group, group can contains some subgroups"
    global global_dicoGroupDefinition;
    if( global_dicoGroupDefinition != None ):
        return global_dicoGroupDefinition;
    dicoGroup = {
        'All':           ['Torsos', 'Body'],
        'Torsos':      ['TorsoX','TorsoY', 'TorsoAccZ'],
        'Body':         ['UpperBody', 'BottomBody'],
        'UpperBody': ['Head', 'Arms', 'ForeArms'],
        'BottomBody': ['Legs'],
        'Head':         ['HeadYaw', 'HeadPitch'],
        'Arms':         ['LArm', 'RArm'],
        'Legs':         ['LLeg', 'RLeg'],
        'ForeArms':   ['LForeArm', 'RForeArm'],
        'LArm':         ['LShoulderPitch','LShoulderRoll','LElbowRoll', 'LElbowYaw'],
        'RArm':         ['RShoulderPitch','RShoulderRoll','RElbowRoll', 'RElbowYaw'],
        'LLeg':         ['LHipYawPitch','LHipPitch','LHipRoll', 'LKneePitch', 'LAnkleRoll', 'LAnklePitch' ],
        'RLeg':         ['LHipYawPitch','RHipPitch','RHipRoll', 'RKneePitch', 'RAnkleRoll', 'RAnklePitch' ], # LHipYawPitch because it's better to send order to this one
        'LForeArm': ['LWristYaw','LHand' ],
        'RForeArm': ['RWristYaw','RHand' ],
        'LFullArm': ['LForeArm','LArm' ],
        'RFullArm': ['RForeArm','RArm' ],        
        'FullArm': ['LFullArm','RFullArm' ], # argh typo ! leave it for backward compat
        'FullArms': ['LFullArm','RFullArm' ],
        'Hands': ['LHand','RHand' ],
    };
    # patch on the fly!
    if( system.isOnRomeo() ):
        dicoGroup["Body"].append( "TrunkYaw" );
        dicoGroup["LLeg"].append( "LHipYaw" );
        dicoGroup["RLeg"].append( "RHipYaw" );
        dicoGroup["Head"] = ["NeckPitch", "NeckYaw", "HeadPitch", "HeadRoll"];
        if( True ):
            # add eyes groups
            dicoGroup["Eyes"] = ["LeftEye", "RightEye"];
            dicoGroup["LeftEye"] = ["LEyePitch", "LEyeYaw"];
            dicoGroup["RightEye"] = ["REyePitch", "REyeYaw"];
            dicoGroup["All"].append( "Eyes" );
        for strSide in ['L', 'R']:
            strGroupName = strSide + "ForeArm";
            dicoGroup[strGroupName].append( strSide + "Wrist" + "Roll" );
            dicoGroup[strGroupName].append( strSide + "Wrist" + "Pitch" );
        for k,v in dicoGroup.iteritems():
            for i, strJoint in enumerate( v ):
                if( "ShoulderRoll" in strJoint ):
                    dicoGroup[k][i] = strJoint.replace( "Roll", "Yaw" );
        
        # remove all non present final joint
        motion = naoqitools.myGetProxy( "ALMotion" );
        listCurrentJoint = motion.getJointNames('Body');
        for k,v in dicoGroup.iteritems():
            i = 0;
            while( i < len(v) ):
                if( not v[i] in dicoGroup.keys() and not v[i] in listCurrentJoint and not "Torso" in v[i] ):
                    print( "abcdk.poselibrary.getGroupDefinition: removing '%s' from list because not present seen by motion" % v[i] );
                    del v[i];
                else:
                    i += 1;
    
    global_dicoGroupDefinition = dicoGroup;
    #~ print( dicoGroup );
    return dicoGroup;
    # getGroupDefinition - end
    
  @staticmethod
  def getListJoints( listGroup, bRemoveHipYawPitch = False ):
    """
    get list of joints from a group name or a list of group:
    eg: ["Head", "LHand", "RArm"] => ['HeadYaw', 'HeadPitch', 'LHand', 'RShoulderPitch', 'RShoulderRoll', 'RElbowRoll', 'RElbowYaw']
          "Head;LHand;RArm" => idem (alternate form)
    bRemoveHipYawPitch: remove all HipYawPitch from the list
    """
    if( not isinstance( listGroup, list ) ):
        #~ print( "interpreting joint from string %s =>" % str( listGroup ) );
        listGroup = listGroup.split( ";" );
        for i in range( len( listGroup ) ):
            listGroup[i] = listGroup[i].strip(); # remove surrounding space(s)
        #~ print( "%s" % str( listGroup ) );
    dicoGroup = PoseLibrary.getGroupDefinition();
    bGroupExploded = True;
    while( bGroupExploded ):
        listGroupExploded = [];
        bGroupExploded = False;
        for group in listGroup:
#            debug.debug( "group: " + str( group ) );
            if( group in dicoGroup ):
                listGroupExploded.extend( dicoGroup[group] );
#                debug.debug( "listGroupExploded: " + str( listGroup ) );
                bGroupExploded = True; # begin another time, because there's some new group
            else:
                listGroupExploded.append( group ); # here group is just a joint name
        listGroup = listGroupExploded;
        
    if( bRemoveHipYawPitch ):        
        for i in range( len( listGroup ) ):
            if( i >= len( listGroup ) ):
                break; # la liste diminue en direct
            if( listGroup[i] in [ "RHipYawPitch", "LHipYawPitch" ] ):
                del listGroup[i];
                i -=1;

    return listGroup;
    # getListJoints - end
    
  @staticmethod
  def getGroupLimits( listGroup, rCoef = 1., bOrderedByMinMax = False ):
    "get list of limits from a group name or a list of group"
    "rCoef: you can reduce the list by a ratio (0.5, will get halt the limits)"    
    "order default: list of min,max,acc for each joint"
    "order bOrderedByMinMax: list of min of each joint, then list of max of each joint..."
    listJoints = PoseLibrary.getListJoints( listGroup );
    listLimits = [];
    if( bOrderedByMinMax ):
        listLimits = [[],[],[]];
    motion = naoqitools.myGetProxy( 'ALMotion' );
    for strJointName in listJoints:
        limitForThisJoint = motion.getLimits( strJointName );
        # gestion 1.7.25 et rétrocompatibilité
        if( len( limitForThisJoint ) > 1 ):
            limitForThisJoint = limitForThisJoint[1];
        limitForThisJoint = limitForThisJoint[0];
        print( "getGroupLimits: %s => %s" % ( strJointName, str( limitForThisJoint ) ) );
        if( not bOrderedByMinMax ):
            limitForThisJoint[0] *= rCoef;
            limitForThisJoint[1] *= rCoef;
            limitForThisJoint[2] *= rCoef;            
            listLimits.append( limitForThisJoint );
        else:
            listLimits[0].append( limitForThisJoint[0]*rCoef );
            listLimits[1].append( limitForThisJoint[1]*rCoef );
            listLimits[2].append( limitForThisJoint[2]*rCoef );
    return listLimits;
    # getGroupLimits - end    

  @staticmethod
  def filterPosition( aPos, listGroupToRemove, bKeepInsteadOfRemove = False ):
    """
    remove a group of joint from a position
    return the filtered list
    listGroupToRemove: list of joint to remove can contains a joint or a torso/gyro, or one of the groups in the dicoGroup: (ask for getGroupDefinition to see complete list of group)
    bKeepInsteadOfRemove: when set, the list of joint is the one to keep !
    """
    #~ print( "DBG: filterPosition:\npos: %s\nlistGroupToRemove: %s\nbKeepInsteadOfRemove: %s" % (aPos, listGroupToRemove, bKeepInsteadOfRemove) );
    # construct the list of joint with group transformed in a list of joint name
    dicoGroup = PoseLibrary.getGroupDefinition();
#    debug.debug( "dicoGroup:" + str( dicoGroup ) );
    bGroupExploded = True;
    while( bGroupExploded ):
      listGroupExploded = [];
      bGroupExploded = False;
      for group in listGroupToRemove:
#        debug.debug( "group: " + str( group ) );
        if( group in dicoGroup ):
            listGroupExploded.extend( dicoGroup[group] );
#            debug.debug( "listGroupExploded: " + str( listGroupExploded ) );
            bGroupExploded = True; # begin another time, because there's some new group
        else:
            listGroupExploded.append( group ); # here group is just a joint name
      listGroupToRemove = listGroupExploded;
#    debug.debug( "poselibrary::PoseLibrary::filterPosition: final joint list to remove: %s" % str( listGroupToRemove ) );
    aKeeped = dict();
    for strJointName in listGroupToRemove:
        if( strJointName in aPos ):
            if( not bKeepInsteadOfRemove ):
                del aPos[strJointName];
            else:
                aKeeped[strJointName] = aPos[strJointName];

    if( bKeepInsteadOfRemove ):
        return aKeeped;
    return aPos;
  # filterPosition - end

  @staticmethod
  def setPosition( aPosToSet, rTimeSec = 1.4, bWaitEnd = True, bDontUseLegs = False ):
    """
    set a position on Nao (with optionnal time in sec to go to the position)
    bWaitEnd: thread command and return the motion id
    """
#    print( "poselibrary::PoseLibrary::setPosition( %d angles, time: %f, bWaitEnd: %d )" % ( len( aPosToSet ), rTimeSec, bWaitEnd ) );
    motion = naoqitools.myGetProxy( "ALMotion" );
    aJointName = [];
    aPos = [];
    listJointToExclude = [];
    if( bDontUseLegs ):
        listJointToExclude = PoseLibrary.getListJoints( ['Legs'] );
    for k, v in aPosToSet.iteritems():
        if( k.find( "Torso" ) == -1 and ( not k in listJointToExclude ) ):
            aJointName.append( k );
            aPos.append( v );
    if( bWaitEnd ):
        motion.angleInterpolation( aJointName, aPos, rTimeSec, True );
        return -1;
    nId = motion.post.angleInterpolation( aJointName, aPos, rTimeSec, True );
    return nId;

  # setPosition - end
  
  @staticmethod
  def setPositionWithSpeed( aPosToSet, nSpeed = 30, bWaitEnd = True, bDontUseLegs = False ):
    "set a position on Nao (with optionnal speed in % to go to the position)"
    "if not bWaitEnd return a post call threaded method id"
    "return the naoqi id if bWaitEnd is false"
    print( "poselibrary.setPositionWithSpeed( nSpeed: %d )" % nSpeed );
    motion = naoqitools.myGetProxy( "ALMotion" );
    aJointName = [];
    aPos = [];
    listJointToExclude = [];
    if( bDontUseLegs ):
        listJointToExclude = PoseLibrary.getListJoints( ['Legs'] );
    for k, v in aPosToSet.iteritems():
        if( k.find( "Torso" ) == -1 and ( not k in listJointToExclude ) ):
            aJointName.append( k );
            aPos.append( v );
    if( bWaitEnd ):
        motion.angleInterpolationWithSpeed( aJointName, aPos, nSpeed/100. );
        return -1;
    nId = motion.post.angleInterpolationWithSpeed( aJointName, aPos, nSpeed/100. );
    return nId;
  # setPositionWithSpeed - end
  
  @staticmethod  
  def interpolatePosition( aPos1, aPos2, rRatio = 0.5 ):
    "create a position intermediary between two positions if rRatio is 0. => pos1, if at 1. => pos2"
    "rRatio in [0.,1.]"
    listPosResult = {};
    rRatio = numeric.limitRange( rRatio, 0., 1. );
    for k, v in aPos1.iteritems():
        if( k in aPos2 ):
            listPosResult[k] = v * ( 1. - rRatio ) + aPos2[k] * rRatio;
    return listPosResult;
  # interpolatePosition - end
  
  @staticmethod  
  def interpolatePositionXY( aPosTR, aPosTL, aPosBR, aPosBL, rX = 0.0, rY = 0.0 ):
    "create a position intermediary at the center of four positions"
    "rX et rY in [-1.,1.]"
    "TR: Top Right( -1,-1), aPosTL: Top Left TR: Top Right, BL: Bottom Left, BR: Bottom Right(1,1)"
    rX_Normalised = (rX+1.) /2.;
    rY_Normalised = (rY+1.) /2.;
    listPosResultTRL = PoseLibrary.interpolatePosition( aPosTR, aPosTL, rX_Normalised );
    listPosResultBRL = PoseLibrary.interpolatePosition( aPosBR, aPosBL, rX_Normalised);
    listPosResult = PoseLibrary.interpolatePosition( listPosResultBRL, listPosResultTRL, rY_Normalised );
    return listPosResult;
  # interpolatePositionXY - end    

  @staticmethod  
  def interpolatePositionXY6( aPosTR, aPosTC, aPosTL, aPosBR, aPosBC, aPosBL, rX = 0.0, rY = 0.0 ):
    "create a position intermediary at the center of 6 positions (4 corner and two center)"
    "rX et rY in [-1.,1.]"
    "TR: Top Right( -1,-1), aPosTL: Top Left TR: Top Right, BL: Bottom Left, BR: Bottom Right(1,1)"
    "aPosTC: Top Center, aPosBC: Bottom Center"
    rX_Normalised = (rX+1.) /2.;
    rY_Normalised = (rY+1.) /2.;
    if( rX_Normalised < 0.5 ):        
        rX_Normalised *= 2; # ramene sur 0..1
        listPosResultTRL = PoseLibrary.interpolatePosition( aPosTR, aPosTC, rX_Normalised );
        listPosResultBRL = PoseLibrary.interpolatePosition( aPosBR, aPosBC, rX_Normalised);
    else:
        rX_Normalised = ( rX_Normalised - 0.5 ) * 2; # ramene sur 0..1
        listPosResultTRL = PoseLibrary.interpolatePosition( aPosTC, aPosTL, rX_Normalised );
        listPosResultBRL = PoseLibrary.interpolatePosition( aPosBC, aPosBL, rX_Normalised);        
    listPosResult = PoseLibrary.interpolatePosition( listPosResultTRL, listPosResultBRL, rY_Normalised );
    return listPosResult;
  # interpolatePositionXY - end
  
  @staticmethod  
  def interpolatePositionXY_Mirror( aPosCT, aPosCB, aPosLB, aPosLT, rX = 0., rY = 0. ):
    "create a position intermediary at the center of 6 positions using mirror: "
    "we just give Center and left, and the right is mirrored"
    "rX et rY in [-1.,1.]"
    "CT: Center-Top( 0,-1), aPosLB: Left-Bottom (1,1)"
    bDoMirror = False;

    if( rX < 0. ):
        rX = -rX;
        bDoMirror = True;

    rY_Normalised = (rY+1.) /2.;
    
#    print( "interpolatePositionXY_Mirror: %5.2f, %5.2f, %5.2f, %5.2f, " % ( aPosCT['LShoulderPitch'], aPosCB['LShoulderPitch'], aPosLB['LShoulderPitch'], aPosLT['LShoulderPitch'] ) );    
#    print( "interpolatePositionXY_Mirror: using x,y: %f,%f (mirror:%s)" % ( rX, rY_Normalised, str(bDoMirror) ) );
    listPosResultTCL = PoseLibrary.interpolatePosition( aPosCT, aPosLT, rX );
    listPosResultBCL = PoseLibrary.interpolatePosition( aPosCB, aPosLB, rX);
    listPosResult = PoseLibrary.interpolatePosition( listPosResultTCL, listPosResultBCL, rY_Normalised );
    if( bDoMirror ):
        listPosResult = PoseLibrary.mirror( listPosResult ); 
    return listPosResult;
  # interpolatePositionXY_Mirror - end  

  @staticmethod
  def getEmotionName( bAddNeutral = False ):
    "return a list of 6 dictionnary of pose"
    "if bAddNeutral: add a seven neutral pose"
    listName = [ 'Proud', 'Happy', 'Excitement', 'Fear', 'Sadness', 'Anger'] ;
    if( bAddNeutral ):
        listName.append( 'Neutral' );
    return listName;
  # getEmotionName - end

  @staticmethod
  def getEmotionPose( bAddNeutral = False ):
    "return a list of 6 dictionnary of pose"
    "if bAddNeutral: add a seven neutral pose"
    import emotion_list_poses;
    listPose = [];
    listPose.extend( emotion_list_poses.listPoses ); # listPose = list_emotion_poses.listPoses ne ferait qu'un pointeur sur l'objet, et donc quand on append la neutralpose, ca ajoute a la liste du module, beurk.
    if( bAddNeutral ):
        listPose.append( emotion_list_poses.poseNeutral );
    return listPose;
  # getEmotionPose - end
  
  @staticmethod
  def interpolateEmotion( arListRatioParams, rNeutral = 0. ):
    "create a position intermediary mixed from 6 emotions and a neutral"
    "arListRatio: the ratio of each emotions: [Proud, Happy, Excitement, Fear, Sadness, Anger]"
    "             if sum is greater than 1, it would be normalised"
    "             if sum is lower than 1, a neutral position would be added"
    "rNeutral:    to force an addition of a proportion of the neutral pose"
    
    # preparation of the ratio
    
    arListRatio = arraytools.dup( arListRatioParams );
    
    if( len( arListRatio ) > 6 ):
        arListRatio = arListRatio[:6];
        
    rSum = arraytools.arraySum( arListRatio );
    
#    rEpsilon = 0.1;
    if( rSum + rNeutral < 1. ):
        rNeutral = 1. - rSum;
    rSumTotal = rSum + rNeutral;
    if( rSumTotal > 1. ):
        # normalisation
        for i in range( len( arListRatio ) ):
            arListRatio[i] /= rSumTotal;
        rNeutral /= rSumTotal;
    
    # push zeroes for others emotions:
    for i in range( len( arListRatio ), 6 ):
        arListRatio.append( 0. );
    
    print( "interpolateEmotion: using emotions ratio: %s and neutral ratio: %5.2f" % ( str( arListRatio ), rNeutral ) );

    arListRatio.append( rNeutral );
    listPosEmotion = PoseLibrary.getEmotionPose( True ); # True => ajoute la neutre !
    # print( "listPosEmotion has %d poses" % len( listPosEmotion ) );
    listPosResult = {};
    for k, v in listPosEmotion[0].iteritems():
        rVal = v * arListRatio[0];
        bKeyInAllPos = True;
        for i in range( 1, len( listPosEmotion ) ):
            if( k in listPosEmotion[i] ):                
                rVal += listPosEmotion[i][k] * arListRatio[i];                
            else:
                bKeyInAllPos = False;
        if( bKeyInAllPos ):
            listPosResult[k] = rVal;
    # for - end
    
    return listPosResult;
    
  # interpolateEmotion - end

  @staticmethod
  def getTrackingEmotionPose( bAddNeutral = False ):
    "return a list of 6 dictionnary of pose"
    "if bAddNeutral: add a seven neutral pose"
    import emotion_list_tracking_poses;
    listPose = [];
    listPose.extend( emotion_list_tracking_poses.listAllEmotions ); # listPose = list_emotion_poses.listPoses ne ferait qu'un pointeur sur l'objet, et donc quand on append la neutralpose, ca ajoute a la liste du module, beurk.
    if( bAddNeutral ):
        listPose.append( emotion_list_tracking_poses.listNeutral );
    return listPose;
  # getTrackingEmotionPose - end
  
  @staticmethod
  def interpolateTrackingEmotion( arListRatio, arPosHead, rNeutral = 0. ):
    "create a position intermediary mixed from 6 emotions and a neutral, related to some specific angle of the head"
    "arListRatio: the ratio of each emotions: [Proud, Happy, Excitement, Fear, Sadness, Anger]"
    "             if sum is greater than 1, it would be normalised"
    "             if sum is lower than 1, a neutral position would be added"
    "rNeutral:    to force an addition of a proportion of the neutral pose"
    
    # preparation of the ratio
    
    if( len( arListRatio ) > 6 ):
        arListRatio = arListRatio[:6];
        
    rSum = arraytools.arraySum( arListRatio );
#    rEpsilon = 0.1;
    if( rSum + rNeutral < 1. ):
        rNeutral = 1. - rSum;
    rSumTotal = rSum + rNeutral;
    if( rSumTotal > 1. ):
        # normalisation
        for i in range( len( arListRatio ) ):
            arListRatio[i] /= rSumTotal;
        rNeutral /= rSumTotal;
    
    # push zeroes for others emotions:
    for i in range( len( arListRatio ), 6 ):
        arListRatio.append( 0. );
    
    print( "interpolateTrackingEmotion(head:%5.2f,%5.2f): using emotions ratio: %s and neutral ratio: %f" % ( arPosHead[0], arPosHead[1], str( arListRatio ), rNeutral ) );

    arListRatio.append( rNeutral );
    
    listPosTrackingEmotion = PoseLibrary.getTrackingEmotionPose( True ); # True => ajoute la neutre !
    
    # in fact we will allways generate from a square from center to left side, and we mirror it if we are in the right area
    
    # first we compute the 4 poses from emotion mixes:
    
#    print( "arListRatio final: %s, len: %d" % ( str( arListRatio ), len( arListRatio ) ) );
    
    listPosResult = [{},{},{},{}];
    # for each corner to generate
    for indexSquare in range( 4 ):
        # for each joint
        for k, v in listPosTrackingEmotion[0][indexSquare].iteritems():
            rVal = v * arListRatio[0];
            bKeyInAllPos = True;
            # for each emotion, sum the ratio concerning this joint
            for i in range( 1, len( listPosTrackingEmotion ) ):
#                print( "i: %d / %d" % (i,len( listPosTrackingEmotion) ) );
#                print( "ratio: %f" % arListRatio[i] );
                if( k in listPosTrackingEmotion[i][indexSquare] ):
                    rVal += listPosTrackingEmotion[i][indexSquare][k] * arListRatio[i];
                else:
                    bKeyInAllPos = False;
            if( bKeyInAllPos ):
#                print( "k: %s, rVal: %f" % ( k, rVal ) );
                listPosResult[indexSquare][k] = rVal;
        # for - each point of square end
    # for - end square
    
    # then we compute the center position relative of the 4 pose
    listPosResult = PoseLibrary.interpolatePositionXY_Mirror( listPosResult[0], listPosResult[1], listPosResult[2], listPosResult[3], arPosHead[0], arPosHead[1] );
    
    return listPosResult;
    
  # interpolateTrackingEmotion - end
  
  @staticmethod
  def getAnimationPoseName():
    "return a list of 6 dictionnary of pose"
    "if bAddNeutral: add a seven neutral pose"
    listName = [ 'Confidence_lo', 'Confidence_hi', 'Engagement_lo', 'Engagement_hi', 'Neutral'] ;
    return listName;
  # getEmotionName - end

  @staticmethod
  def getAnimationPose():
    "return a list of 6 dictionnary of pose"
    "if bAddNeutral: add a seven neutral pose"
    import animation_list_poses;
    import emotion_list_poses;    
    listPose = [];
    listPose.extend( animation_list_poses.listPoses );
    listPose.append( emotion_list_poses.poseNeutral );
    return listPose;
  # getAnimationPose - end
  
  @staticmethod
  def interpolateAnimationPose( arListRatio ):
    "create a position intermediary mixed from animation parameters"
    "arListRatio: the ratio of each animation parameters: [Confidence, Engagement]"
    
    nRequiredParameters = 2;
    
    if( len( arListRatio ) > nRequiredParameters ):
        arListRatio = arListRatio[:nRequiredParameters];
        
  
    # push zeroes for missing parameters:
    for i in range( len( arListRatio ), nRequiredParameters ):
        arListRatio.append( 0. );
        
    # now we would generate the resulting pose for each parameters, then mix them
    listPose = PoseLibrary.getAnimationPose();
    listPoseToMix = [];
    newPose = PoseLibrary.interpolatePosition( listPose[0], listPose[1], arListRatio[0] ); # confidence
    listPoseToMix.append( newPose );
    newPose = PoseLibrary.interpolatePosition( listPose[2], listPose[3], arListRatio[1] ); # engagement
    listPoseToMix.append( newPose );
    
    # mix them
    listPosResult = PoseLibrary.interpolatePosition( listPoseToMix[0], listPoseToMix[1] );
    
    return listPosResult;
    
  # interpolateAnimationPose - end
  
  

  @staticmethod
  def positionToString( aPos ):
    "format a position to print it"
    return stringtools.dictionnaryToString( aPos );
  # positionToString - end

  @staticmethod
  def getDifferentJoints( aPosToCompare, rThreshold = 0.12 ):
    "return the list of joint that has a difference between a specific position and nao current position"
    listDiff = [];
    dicoCurrentPos = PoseLibrary.getCurrentPosition();
    for k, v in dicoCurrentPos.iteritems(): # not optimal: should iterate on aPosToCompare !
      if( k in aPosToCompare ):
        rDiff = abs( v - aPosToCompare[k] );
        if( rDiff > rThreshold ):
          debug.debug( "difference on key %s (%f -> %f (diff:%f))" %( k, aPosToCompare[k], v, rDiff ) );
          listDiff.append( k );
    return listDiff;
  # getDifferentJoints - end
  
  
  @staticmethod
  def comparePosition( aPosToCompare, aListGroupToIgnore = [] ):
    "compare a specific position of nao with current position"
    "aPosToCompare is a dictionnary of some angles; eg: dict(  [ ('LArm', 1.32), ('HeadYaw', 0.5), ('TorsoX', 0.5) ] );"
    "aListGroupToIgnore is a mixed type list of joint or group to ignore for comparison"
    "It will return the median of absolute difference of joints in radians"
#    debug.debug( "len( aPosToCompare ): " + str( len( aPosToCompare ) ) );
    if( len( aPosToCompare ) < 1 ):
      return 421.0; # surely some sort of error => return a big value
    dicoCurrentPos = PoseLibrary.getCurrentPosition();
    if( len( aListGroupToIgnore ) > 0 ):
        dicoCurrentPos = PoseLibrary.filterPosition( dicoCurrentPos, aListGroupToIgnore );
    rDiffSum = 0.0;
    nNbrComp = 0;
    for k, v in dicoCurrentPos.iteritems(): # not optimal: should iterate on aPosToCompare !
      if( k in aPosToCompare ):
        rDiff = abs( v - aPosToCompare[k] );
#        if( k == 'TorsoAccZ' ):
#          rDiff *= 8; # This value is important and very small compared to others
        rDiffSum += rDiff;
        nNbrComp += 1;
    # debug.debug( "poselibrary::PoseLibrary::comparePosition:\ncurrent: %s\ncomp: %s\n=> %f/%d = %f" % ( str(dicoCurrentPos), str(aPosToCompare), rDiffSum, nNbrComp, rDiffSum / nNbrComp ) );
    return rDiffSum / nNbrComp;
  # comparePosition - end

  @staticmethod
  def getPosition_Standing():
    "get the standard standing position"
    return {
      'TorsoX': 0.0,
      'TorsoY': 0.0,
      'LAnklePitch': 0.010696,
      'LAnkleRoll': 0.058334,
      'LHipPitch': 0.010780,
      'LHipRoll': -0.050580,
      'LHipYawPitch': 0.007712,
      'LKneePitch': 0.009162,
      'RAnklePitch': 0.007712,
      'RAnkleRoll': -0.055182,
      'RHipPitch': 0.010696,
      'RHipRoll': 0.053732,
      'RKneePitch': 0.004644,
    };
  # getPosition_Standing - end
  @staticmethod
  def getPosition_Sitting():
    "get the official sitting position - without anklepitch due to ankle limitation far distant from real range"
    "now it's the new one WITH the ankle pitch"
    return {
    'HeadPitch': -0.0215179622173,
    'HeadYaw': 0.0260360389948,
    'LAnklePitch': 0.888144075871,
    'LAnkleRoll': 0.0123139619827,
    'LElbowRoll': -0.977116048336,
    'LElbowYaw': -0.733294010162,
    'LHand': 0.238207533956,
    'LHipPitch': -1.59992003441,
    'LHipRoll': 0.233209967613,
    'LHipYawPitch': -0.717870056629,
    'LKneePitch': 1.37442207336,
    'LShoulderPitch': 0.969446063042,
    'LShoulderRoll': 0.20551404357,
    'LWristYaw': -0.593699991703,
    'RAnklePitch': 0.879023969173,
    'RAnkleRoll': -0.0383080393076,
    'RElbowRoll': 0.882091999054,
    'RElbowYaw': 0.562936067581,
    'RHand': 0.314207285643,
    'RHipPitch': -1.59846997261,
    'RHipRoll': -0.162562042475,
    'RKneePitch': 1.41592395306,
    'RShoulderPitch': 0.874421954155,
    'RShoulderRoll': -0.196393966675,
    'RWristYaw': 0.860532045364,
    'TorsoAccZ': -0.994837673637,
    'TorsoX': -0.0542904734612,
    'TorsoY': -0.181328982115,
    };
  # getPosition_Sitting - end
  @staticmethod
  def getPosition_Crouching():
    "get the standard crouching position"
    return {
        'TorsoX': 0.010472,
        'TorsoY': -0.066323,
        'LAnklePitch': -1.193494,
        'LAnkleRoll': 0.093616,
        'LHipPitch': -0.774628,
        'LHipRoll': -0.091998,
        'LHipYawPitch': -0.237728,
        'LKneePitch': 2.181306,
        'RAnklePitch': -1.233294,
        'RAnkleRoll': -0.102736,
        'RHipPitch': -0.747100,
        'RHipRoll': 0.096684,
        'RKneePitch': 2.187526,
    };
  # getPosition_Crouching - end
  @staticmethod
  def getPosition_LyingBack():
    "get torsos from lying on his back"
    return {
      'TorsoX': 0.015708,
      'TorsoY': -1.548107,
    };
  # getPosition_LyingBack - end
  @staticmethod
  def getPosition_LyingFront():
    "get torsos from lying on his front"
    return {
      'TorsoX': -0.048869,
      'TorsoY': 1.338667,
    };
  # getPosition_LyingFront - end
  @staticmethod
  def getPosition_LyingLeft():
    "get Torsos from lying on his left"
    return {
    'TorsoX': -1.361357,
    'TorsoY': -0.034907,
  };
  # getPosition_LyingLeft - end
  @staticmethod
  def getPosition_LyingRight():
    "get Torsos from lying on his right"
    return {
      'TorsoX': 1.307252,
      'TorsoY': -0.050615,
    };
  # getPosition_LyingRight - end
  @staticmethod
  def getPosition_HeadDown():
    "get Torsos head down"
    return {
      'TorsoAccZ': 0.890118,
      'TorsoX': 0.0,
      'TorsoY': 0.0,
    };
  # getPosition_HeadDown - end

  # Various position - funny position
  @staticmethod
  def getPosition_Victory():
    "Nao's has win, and he is very happy !"
    return {
        'TorsoX': 0.001746,
        'TorsoY': -1.024508,
        'HeadPitch': -0.786984,
        'HeadYaw': 0.021434,
        'LAnklePitch': 0.526120,
        'LAnkleRoll': 0.325250,
        'LElbowRoll': -0.338972,
        'LElbowYaw': -0.348260,
        'LHipPitch': 0.500126,
        'LHipRoll': 0.777780,
        'LHipYawPitch': 0.779314,
        'LKneePitch': 1.998760,
        'LShoulderPitch': -0.069072,
        'LShoulderRoll': 0.635034,
        'RAnklePitch': 0.823800,
        'RAnkleRoll': -0.134950,
        'RElbowRoll': 0.572224,
        'RElbowYaw': -0.024586,
        'RHipPitch': 0.503110,
        'RHipRoll': -0.776162,
        'RKneePitch': 1.879192,
        'RShoulderPitch': -0.044444,
        'RShoulderRoll': -0.767042,
    };
  # getPosition_Victory - end
  @staticmethod
  def getPosition_ExtendedKickRight():
    "Nao's kick / sun !"
    return {
        'HeadPitch': -0.050664,
        'HeadYaw': -0.079810,
        'LAnklePitch': -0.102820,
        'LAnkleRoll': 0.168782,
        'LElbowRoll': -0.142620,
        'LElbowYaw': -0.645856,
        'LHipPitch': 0.104354,
        'LHipRoll': 0.434164,
        'LHipYawPitch': -0.170232,
        'LKneePitch': 0.009162,
        'LShoulderPitch': 1.052282,
        'LShoulderRoll': 1.570774,
        'RAnklePitch': 0.323716,
        'RAnkleRoll': -0.165630,
        'RElbowRoll': 0.010780,
        'RElbowYaw': 0.940300,
        'RHipPitch': -0.302240,
        'RHipRoll': -0.740880,
        'RKneePitch': 0.003110,
        'RShoulderPitch': 0.833004,
        'RShoulderRoll': -1.586198,
        'TorsoAccZ': -0.890118,
        'TorsoX': -0.523599,
        'TorsoY': 0.022689,
    };
  # getPosition_ExtendedKickRight - end
  @staticmethod
  def getPosition_SittingFeetUp():
    "Nao's sit with feet up !"
    return {
      'LAnklePitch': -0.661196,
      'LAnkleRoll': 0.046062,
      'LElbowRoll': -0.233126,
      'LElbowYaw': -0.748634,
      'LHipPitch': -1.464928,
      'LHipRoll': 0.245482,
      'LHipYawPitch': -0.498508,
      'LKneePitch': 0.477032,
      'LShoulderPitch': 1.576910,
      'LShoulderRoll': 0.291418,
      'RAnklePitch': -0.817580,
      'RAnkleRoll': -0.187106,
      'RElbowRoll': 0.052198,
      'RElbowYaw': 0.944902,
      'RHipPitch': -1.541712,
      'RHipRoll': -0.064386,
      'RKneePitch': 0.624380,
      'RShoulderPitch': 1.580062,
      'RShoulderRoll': -0.294570,
      'TorsoX': 0.038397,
      'TorsoY': -0.041888,
    };
  # getPosition_SittingFeetUp - end

  @staticmethod
  def getPosition_SittingFeetUpLegsJoint():
    "Nao's sit with feet up and legs joint (sage)!"
    return {
        'HeadPitch': -0.1,  # the head raise a little
        'HeadYaw': 0.0,
        'LAnklePitch': -0.251618,
        'LAnkleRoll': 0.001576,
        'LElbowRoll': -1.460326,
        'LElbowYaw': -0.710284,
        'LHipPitch': -1.463394,
        'LHipRoll': 0.012314,
        'LHipYawPitch': 0.032256,
        'LKneePitch': -0.072140,
        'LShoulderPitch': 1.533958,
        'LShoulderRoll': 0.165630,
        'RAnklePitch': -0.211650,
        'RAnkleRoll': -0.012230,
        'RElbowRoll': 1.518702,
        'RElbowYaw': 0.964844,
        'RHipPitch': -1.472682,
        'RHipRoll': -0.030638,
        'RKneePitch': -0.073590,
        'RShoulderPitch': 1.596936,
        'RShoulderRoll': -0.016916,
        'TorsoAccZ': -1.029744,
        'TorsoX': 0.043633,
        'TorsoY': -0.062832,
    };
  # getPosition_SittingFeetUpLegsJoint - end

  @staticmethod
  def getPosition_StandingPackShot():
    "Nao's nice standing (packshot)!"
    return {
      'HeadPitch': -0.108956,
      'HeadYaw': 0.240796,
      'LAnklePitch': -0.069072,
      'LAnkleRoll': -0.052114,
      'LElbowRoll': -0.915756,
      'LElbowYaw': -1.083046,
      'LHand': 0.731297,
      'LHipPitch': 0.493368,
      'LHipRoll': 0.069072,
      'LHipYawPitch': -0.213184,
      'LKneePitch': 0.009162,
      'LShoulderPitch': 1.472598,
      'LShoulderRoll': 0.214718,
      'LWristYaw': -1.578528,
      'RAnklePitch': -0.245398,
      'RAnkleRoll': 0.033790,
      'RElbowRoll': 1.073842,
      'RElbowYaw': 0.747016,
      'RHand': 0.044026,
      'RHipPitch': 0.490954,
      'RHipRoll': -0.091998,
      'RKneePitch': 0.136568,
      'RShoulderPitch': 1.630684,
      'RShoulderRoll': -0.434164,
      'RWristYaw': 0.141086,
      'TorsoAccZ': -1.064651,
      'TorsoX': 0.001746,
      'TorsoY': -0.146608,
    };
  # getPosition_StandingPackShot - end

  @staticmethod
  def getPosition_StandingWalk():
    "Nao's standing like before or after walking!"
    return {
      'LAnklePitch': -0.458708,
      'LAnkleRoll': 0.024586,
      'LElbowRoll': -0.518450,
      'LElbowYaw': -1.474216,
      'LHipPitch': -0.472430,
      'LHipRoll': 0.0,
      'LHipYawPitch': 0.001576,
      'LKneePitch': 0.885076,
      'LShoulderPitch': 1.734912,
      'LShoulderRoll': 0.256136,
      'RAnklePitch': -0.490838,
      'RAnkleRoll': -0.088930,
      'RElbowRoll': 0.518534,
      'RElbowYaw': 1.472598,
      'RHipPitch': -0.490922,
      'RHipRoll': 0.0,
      'RKneePitch': 0.908170,
      'RShoulderPitch': 1.753404,
      'RShoulderRoll': -0.250084,
      'TorsoAccZ': -0.977384,
      'TorsoX': 0.008727,
      'TorsoY': 0.155334,
    };
  # getPosition_StandingWalk - end


  @staticmethod
  def getPosition( strPosition ):
    "get a standard position"
    "eg: getPosition( 'Standing' )"
    methodName = "getPosition_" + strPosition;
    try:
      func = getattr( PoseLibrary, methodName );
    except AttributeError:
      print( "poselibrary::PoseLibrary::isPosition(): ERR: unknown position '%s'" % strPosition );
      return {};
    return func();
  # getPosition - end

  @staticmethod
  def getListPosition():
    "get the list of position name currently in the library"
    return [
                  'Standing',
                  'Sitting',
                  'Crouching',
                  'LyingBack',
                  'LyingFront',
                  'LyingLeft',
                  'LyingRight',
                  'HeadDown',
                  'Victory',
                  'ExtendedKickRight',
                  'SittingFeetUp',
                  'SittingFeetUpLegsJoint',
                  'StandingPackShot',
                  'StandingWalk'
              ];
  # getPosition - end

  @staticmethod
  def isPosition( strPosition ):
    "are we in a specific position?"
    "eg:  isPosition( 'Standing' )"
    return PoseLibrary.comparePosition( PoseLibrary.getPosition( strPosition ) ) < 0.1;
  # isPosition - end
  
  @staticmethod
  def mirror( aListPosition ):
    "compute a mirror of a specific position (flip)"
    "return the flipped position"
    listRet = {};
    for k, v in aListPosition.iteritems():        
        if( k[0] == 'L' ):
            k = 'R' + k[1:];
        elif( k[0] == 'R' ):
            k = 'L' + k[1:];
        else:
            if( 'Yaw' in k ):
                v = -v;
        if( 'ElbowRoll' in k or 'ElbowYaw' in k or 'WristYaw' in k or 'AnkleRoll' in k or  'ShoulderRoll' in k or 'HipRoll' in k ):
            v = -v;
        listRet[k] = v;
    return listRet;
  # mirror - end

  @staticmethod
  def findNearestPosition( aListPosition = None, aListGroupToIgnore = [] ):
    "find nearest position between some known or specific position"
    "aListPosition is a mixed type list: eg: [ 'Sitting', 'Standing', {'TorsoX': 0.005236, 'TorsoY': 0.001745 } ]"
    "aListGroupToIgnore is a mixed type list of joint or group to ignore for comparison"
    "return an array [position, distance to this position, name of position (if this position has a name)]"
    if( aListPosition == None ):
      aListPosition = PoseLibrary.getListPosition();
    rDistMin = 1000.0;
    strNameMin = "";
    posMin = dict();
    for pos in aListPosition:
      strName = "";
      if( typetools.isString( pos ) ):
        strName = pos;
        pos = PoseLibrary.getPosition( strName );
      rDist = PoseLibrary.comparePosition( pos, aListGroupToIgnore ); # here it's not optimal, at every call we will compute the current position
#      print( "rDist: %f" % rDist );
      if( rDist < rDistMin ):
        rDistMin = rDist;
        strNameMin = strName;
        posMin = pos;
    debug.debug( "findNearestPosition between %s:"  % aListPosition );
    debug.debug( "posMin: %s\ndistMin: %f\nName: '%s'" % ( str( posMin), rDistMin, strNameMin ) );
    return [ posMin, rDistMin, strNameMin ];
  # findNearestPosition - end

  @staticmethod
  def exportToXar( aPos, rTime = 0.0 ):
    "Export a specifig position to a xar"
    "the name of the xar is returned"
    "eg:  exportToXar( getPosition( 'Standing' ) )"

    # On charge un sample, et on va juste poker notre liste de clés au milieu
    bError = False;
    file = False;
    try:
        file = open( getApplicationSharedPath() + "PoseLibrary_sample.xar", 'r' );
        strBufferSample = file.read();
    except:
        bError = True;
    finally:
        if( file ):
            file.close();
    if( bError ):
        print( "PoseLibrary:exportToXar: read file error" );
        return None;

    strListPose = "<!-- a pose containing %d motors -->\n" % len( aPos );
    strListPose +=  "<MotionKeyframe>\n";
    strListPose +=  "  <name>keyframe%d</name>\n" % 1;
    strListPose +=  "  <index>%d</index>\n" % ( 25 + int( rTime / 25 ) );   # we act as if running at 25 fps
    strListPose +=  "  <interpolation>1</interpolation>\n";
    strListPose +=  "  <Motors>\n";
    for k, v in aPos.iteritems():
      if( k.find( "Torso" ) == -1 ):
        strListPose +=  "  <Motor>\n";
        strListPose +=  " <name>%s</name>\n" % k;
        strListPose +=  " <value>%5.6f</value>\n" % ( v * 180 / math.pi );
        strListPose +=  "  </Motor>\n";
    strListPose +=  "  </Motors>\n";
    strListPose +=  "</MotionKeyframe>\n";

    strBufferSample = strBufferSample % strListPose;
    strFilename = "/home/nao/PoseLibrary_exported_%d.xar" % time.clock();
    print( "PoseLibrary.exportToXar: outputting position to %s" % strFilename );
    try:
        file = open( strFilename, 'w' );
        file.write( strBufferSample );
        file.close();
    except:
        print( "PoseLibrary:exportToXar: write file error" );        
        return None;
    return strFilename;
  # exportToXar - end
  
  @staticmethod
  def interpolateCrouchStand( rRatio = 0.5, rTimeSec = 1.4, bWaitEnd = True ):
    """
    (incidently it put NAO's head to a specific height)
    interpolateCrouchStand( 1. ) => NAO is fully stand (knee completely 'tense') (straight legs)
    interpolateCrouchStand( 0. ) => NAO is crouched (you could unstiffness him)
    """
    newPos = PoseLibrary.interpolatePosition( PoseLibrary.getPosition_Crouching(), PoseLibrary.getPosition_Standing(), rRatio );
    return PoseLibrary.setPosition( newPos, rTimeSec = rTimeSec, bWaitEnd = bWaitEnd );
  # interpolateCrouchStand - end  

# class PoseLibrary - end

self = PoseLibrary(); # overwrite whole module by this class

def autoTest():
    # PoseLibrary Test Zone:
    test.activateAutoTestOption();
    if( False ):
        print( PoseLibrary.getCurrentPosition() );
        print( "PoseLibrary.isPosition : %d" % PoseLibrary.isPosition( "Standing" ) );
        PoseLibrary.setPosition( PoseLibrary.getPosition( "Standing" ) );
        print( "PoseLibrary.getPos: %s" % stringtools.dictionnaryToString( PoseLibrary.filterPosition( PoseLibrary.getCurrentPosition(), ["Arms"] ) ) );
        print( "PoseLibrary.getPos: %s" % stringtools.dictionnaryToString( PoseLibrary.filterPosition( PoseLibrary.getCurrentPosition(), ["UpperBody", "Torsos"] ) ) ); # remove all but legs
        print( "PoseLibrary.getPos: %s" % stringtools.dictionnaryToString( PoseLibrary.filterPosition( PoseLibrary.getCurrentPosition(), ["Body"] ) ) );
        PoseLibrary.exportToXar( PoseLibrary.getPosition( 'Standing' ) );
        print( PoseLibrary.positionToString( PoseLibrary.getPosition( 'Standing' ) ) );
        print( PoseLibrary.findNearestPosition( [ 'Sitting', 'Standing', {'TorsoX': 0.5, 'TorsoY': 0.5} ] ) );
        print( PoseLibrary.findNearestPosition( [ 'Standing', 'HeadDown' ]) );
        print( PoseLibrary.findNearestPosition() );
        print( "Current Pos: " + PoseLibrary.positionToString( PoseLibrary.getCurrentPosition() ) );
        PoseLibrary.getDifferentJoints( PoseLibrary.getPosition( 'Standing' ) );
        PoseLibrary.getDifferentJoints( PoseLibrary.getPosition( 'Sitting' ) );
        PoseLibrary.setPosition( PoseLibrary.getPosition( "Sitting" ) );
        print( "All joints name: " + str( PoseLibrary.getListJoints( ["Body"] ) ) );
        print( "All joints limits: " + str( PoseLibrary.getGroupLimits( ["Body"], 0.5, True ) ) );

        listPos = PoseLibrary.getCurrentPosition()
        listPos = PoseLibrary.mirror( listPos );
        PoseLibrary.setPosition( listPos );

        listPos = PoseLibrary.interpolateTrackingEmotion( [0,0,0,0,0,0], [-0.5,0.], 0.1 );
        print( "interpolateTrackingEmotion, ret: " + str( listPos ) );
        print( "interpolateTrackingEmotion, ret: LShoulderPitch: %5.2f" % listPos['LShoulderPitch'] );
        PoseLibrary.setPosition( listPos );
        
    
    listPos = PoseLibrary.getCurrentPosition()
    listPos = PoseLibrary.mirror( listPos );
    PoseLibrary.setPosition( listPos, bDontUseLegs = False );
# autoTest - end

#autoTest();