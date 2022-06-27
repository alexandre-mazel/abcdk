# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Diagnostic tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Diagnostic tools (this is not specifically diagnostic, but I don't the real name)"
print( "importing abcdk.diagnostic" );

import debug
import filetools
import motiontools
import naoqitools
import poselibrary
import sound
import sound_analyse
import system
import translate # for getMicrophoneErrorText (questionnable)

import os
import random
import time

global_getBodyHigherTemperature_listKeyTemp = [];
def getBodyHigherTemperature():
    mem = naoqitools.myGetProxy( "ALMemory" );

    global global_getBodyHigherTemperature_listKeyTemp;

    # first time: generate key list
    if( len( global_getBodyHigherTemperature_listKeyTemp ) < 1 ):
        listJointName = motiontools.getDcmBodyJointName();
        for strJointName in listJointName:
            global_getBodyHigherTemperature_listKeyTemp.append( "Device/SubDeviceList/%s/Temperature/Sensor/Value" % strJointName );

    # get all temp value
    arVal = mem.getListData( global_getBodyHigherTemperature_listKeyTemp );

    rMax = 0;
    nHigherJoint = -1;
    for rVal in arVal:
        if( rVal > rMax ):
            rMax = rVal;
#    debug( "getBodyHigherTemperature: higher: joint '%s': %5.2f" % ( strHigherJoint, rMax ) );
    return rMax;
# getBodyListTemperature - end

def checkMotorBoard():
    """
    Wait 1 sec, then analyse elapsed ack and nack on all boards
    Return a list of board on error, using english name
    """
    listBoardInError = [];
    mem = naoqitools.myGetProxy( "ALMemory" );
    listBoard = system.getBoardList();
    memorised = {};
    listValue = ["Device/DeviceList/%s/Ack", "Device/DeviceList/%s/Nack"];
    for strBoard in listBoard:
        memorised[strBoard] = mem.getListData( [listValue[0] % strBoard, listValue[1] % strBoard] );
        
    time.sleep( 1. );
    for strBoard in listBoard:
        nAck, nNack = mem.getListData( [listValue[0] % strBoard, listValue[1] % strBoard] );
        if( nNack - memorised[strBoard][0] > 2 ): # US board is not acking a lot, so we remove that test: (nAck - memorised[strBoard][0] < 2 or)
            print( "INF: checkMotorBoard: card '%s': before: %s, after: %d,%d" % ( strBoard, str(memorised[strBoard]), nAck, nNack) );
            listBoardInError.append( strBoard );
            
    print( "WRN: checkMotorBoard: after analyse, board in error: %s" % str( listBoardInError ) );
    return listBoardInError;
# checkMotorBoard - end

global_bMoveAllJointsMustStop = False;
def moveAllJoints( rFullRatio = 1., nNbrTimePerJoint = 1, listJointToExclude = [] ):
    """
    move all joints to the max.
    - rFullRatio: reduce it to be more gentle (less faster and less limits) [0..1]
    - listJointToExclude:  a list of joint or chain to exclude from the test
    """
    print( "INF: diagnostic.moveAllJoints - begin" );
    global global_bMoveAllJointsMustStop;
    global_bMoveAllJointsMustStop = False;
    listAllJoint = motiontools.getDcmBodyJointName();
    mover = motiontools.mover;
    motion = naoqitools.myGetProxy( "ALMotion" );
    rMinSpeed = 0.12;
    rMaxSpeed = 1.*rFullRatio;
    rMedSpeed = (rMinSpeed+rMaxSpeed) / 2.;
    rShoulderYawPos = 0.;
    bWaitEndPosition = True;
    listJointToExclude = poselibrary.PoseLibrary.getListJoints( listJointToExclude );    
    if( listJointToExclude != [] ):
        print( "INF: diagnostic.moveAllJoints: excluding: %s" % listJointToExclude );    
    
    print( "INF: diagnostic.moveAllJoints: moving all the body to neutral position" );
    mover.moveJointsWithSpeed( "Body", 0.0, rMinSpeed, bVerbose = True, bWaitEndPosition = bWaitEndPosition );
    if( rShoulderYawPos != 0. ):
        mover.moveJointsWithSpeed( "LShoulderYaw", rShoulderYawPos, rMinSpeed, bWaitEndPosition = bWaitEndPosition ); # romeo patch temp
        mover.moveJointsWithSpeed( "RShoulderYaw", -rShoulderYawPos, rMinSpeed, bWaitEndPosition = bWaitEndPosition ); # romeo patch temp    
    while( not global_bMoveAllJointsMustStop ):
        for strJoint in listAllJoint:
            if( strJoint in listJointToExclude ):
                continue;            
            if( global_bMoveAllJointsMustStop ):
                break;            
            print( "INF: diagnostic.moveAllJoints: moving %s" % strJoint );
            bBroken = False;
            for nbr in range(nNbrTimePerJoint):
                for rSpeed in [rMinSpeed, rMedSpeed, rMaxSpeed]:
                    if( global_bMoveAllJointsMustStop or bBroken ):
                        break;
                    jointLimits = motion.getLimits( strJoint )[0];
                    # romeo patch temp
                    if( "Elbow" in strJoint ):
                        jointLimits[0] *= 0.8;
                        jointLimits[1] *= 0.8;
                    if( "NeckPitch" in strJoint ):
                        jointLimits[0] *= 0.4;
                        jointLimits[1] *= 0.4;                        
                    retVal = mover.moveJointsWithSpeed( strJoint, jointLimits[0]*rFullRatio, rSpeed, bVerbose = True, bWaitEndPosition = bWaitEndPosition );
                    if( retVal == None ):
                        # all broken or stopped?
                        print( "WRN: diagnostic.moveAllJoints: %s seems broken, skipping it !!! (TO CHECK)" % strJoint );
                        bBroken = True;
                    else:
                        retVal = mover.moveJointsWithSpeed( strJoint, jointLimits[1]*rFullRatio, rSpeed, bVerbose = True, bWaitEndPosition = bWaitEndPosition );
                        time.sleep( 0.4 );
            rToZero = 0.;
            if( "LShoulderYaw" == strJoint ):
                rToZero = rShoulderYawPos;
            if( "RShoulderYaw" == strJoint ):
                rToZero = -rShoulderYawPos;
            mover.moveJointsWithSpeed( strJoint, rToZero, rMinSpeed, bVerbose = True, bWaitEndPosition = bWaitEndPosition );
                
    # while - end
    print( "INF: diagnostic.moveAllJoints - end" );
# moveAllJoints - end

def moveAllJoints_stop():
    print( "INF: diagnostic.moveAllJoints_stop: sending the stop command !!!" );
    global global_bMoveAllJointsMustStop;
    global_bMoveAllJointsMustStop = True;
    motiontools.mover.stopAll();
    
def useAllJoints( listJointToExclude, rMaxRatioUsage = 0.5, rUseSpeedTime = 1., bPauseAllJointIfAtLeastIsTooBig = True, bStopOnAnyError = False ):
    """
    use all joints in the same time, watching not to make them too hot...
    - listJointToExclude:  a list of joint or chain to exclude from the test
    - rMaxRatioUsage: ratio to stop joint usage 1. means nominal consumption over time)
    - bPauseAllJointIfAtLeastIsTooBig: when a joint had too much work, stop all others
    - bStopOnAnyError # TODO: check Device/SubDeviceList/%s/Errors/Value are different than 512
    Return:
        False: on error on some joint
    """
    print( "*" * 80 );
    print( "INF: diagnostic.useAllJoints - begin at %s" % debug.getHumanTimeStamp() );
    print( "*" * 80 );
    global global_bUseAllJointsMustStop;
    global_bUseAllJointsMustStop = False;
    listAllJoint = motiontools.getDcmBodyJointName();
    mover = motiontools.mover;
    motion = naoqitools.myGetProxy( "ALMotion" );
    memory = naoqitools.myGetProxy( "ALMemory" );
    rFullRatio = 0.9;
    rMinSpeed = 0.12;
    rMaxSpeed = 1.*rFullRatio;
    rMedSpeed = (rMinSpeed+rMaxSpeed) / 2.;
    bWaitEndPosition = True;
    listJointToExclude = poselibrary.PoseLibrary.getListJoints( listJointToExclude );
    
    # get median position
    arMedian = [];
    for strJoint in listAllJoint:
        jointLimits = motion.getLimits( strJoint )[0];
        rMin = jointLimits[0];
        rMax = jointLimits[1];
        rMedian = (rMin+rMax)/2;
        arMedian.append( rMedian );
        
    # get list broken at beginning:
    listCriticalError = [512];
    listBroken = [];
    for strJoint in listAllJoint:
        if( strJoint in listJointToExclude ):
            continue;
        for i in range( 5 ):
            nErrorCode = int(memory.getData( "Device/SubDeviceList/%s/Errors/Value" % strJoint ));
            if( nErrorCode in listCriticalError ):
                print( "WRN: diagnostic.useAllJoints: at startup, broken joint: %s (error code:%d)" % (strJoint,nErrorCode ) );
                listBroken.append( strJoint );
                break;
            time.sleep( 0.011 );
            
        
    if( listJointToExclude != [] ):
        print( "INF: diagnostic.useAllJoints: excluding: %s" % listJointToExclude );
        
    rRangeMove = 0.3; # move +- this range
    
        
    watcher = motiontools.ConsumptionWatcher(listAllJoint);
    aMoveID = [-1]*len(listAllJoint);
    print( "INF: diagnostic.useAllJoints: moving all the body to neutral position" );
    abFlipFlop = [True]*len(listAllJoint);
    aPrevPosition = [-1.]*len(listAllJoint);
    bEveryOneMustRest = False;
    nCptSend = 0;
    while( not global_bUseAllJointsMustStop ):
        #~ print( "INF: diagnostic.useAllJoints: beginning a new loop..." );
        watcher.update();
        bOneJointWantToHaveRest = False;
        for idx, strJoint in enumerate(listAllJoint):
            if( strJoint in listJointToExclude ):
                continue;
            if( strJoint in listBroken ):
                continue;
            if( global_bUseAllJointsMustStop ):
                break;
                
            if( aMoveID[idx] == -1 or not motion.isRunning( aMoveID[idx] ) ):
                consumption = watcher.getConsumption(strJoint);
                rSum = consumption[0];
                rSumNominal = consumption[1];
                #~ print( "INF: diagnostic.useAllJoints: %s: (%5.3f / %5.3f)" % (strJoint,rSum,rSumNominal) );
                bTooMuchWork = rSum > rSumNominal * rMaxRatioUsage;
                if( bTooMuchWork ):
                    print( "WRN: diagnostic.useAllJoints: not moving %s because it's too used: (%5.3f / %5.3f)" % (strJoint,rSum,rSumNominal) );
                    bOneJointWantToHaveRest = True;
                    if( bPauseAllJointIfAtLeastIsTooBig ):
                        bEveryOneMustRest = True;
                    
                if( bEveryOneMustRest or bTooMuchWork ):
                    motion.setStiffnesses( strJoint, 0. );
                else:
                    if( bStopOnAnyError ):
                        # test joint has moved since last time
                        rCurPos = motion.getAngles( strJoint, True )[0];
                        if( abs( rCurPos - aPrevPosition[idx] ) < 0.001 ):
                            if( nCptSend > 50 ):
                                print( "ERR: diagnostic.useAllJoints: joint %s has stop to move! (prev:%s, current:%s)" % (strJoint, aPrevPosition[idx], rCurPos) );
                                return False;
                            print( "WRN: diagnostic.useAllJoints: at %d send, broken joint: %s (error code:%d)" % (nCptSend, strJoint, nErrorCode ) );
                            listBroken.append( strJoint );
                        aPrevPosition[idx] = rCurPos;
                        print( "storing to %s pos: %s" % ( strJoint, rCurPos ) );
                        
                        nErrorCode = int(memory.getData( "Device/SubDeviceList/%s/Errors/Value" % strJoint ));
                        if( nErrorCode != 0 ):
                            print( "DBG: diagnostic.useAllJoints: error code for joint %s: %s" % (strJoint, nErrorCode) );
                        if( nErrorCode in listCriticalError ):
                            if( nCptSend < 50 ):
                                print( "ERR: diagnostic.useAllJoints: joint %s has a critical error! (nErrorCode:%s)" % (strJoint, nErrorCode) );
                                return False;
                            print( "ERR: diagnostic.useAllJoints: at %d send, joint %s has a critical error! (nErrorCode:%s)" % (nCptSend, strJoint, nErrorCode) );
                            listBroken.append( strJoint );
                            
                    # launch a move on this joint            
                    #rPos = arMedian[idx]+rRangeMove*2.*(random.random() - 0.5);
                    if( abFlipFlop[idx] ):
                        rPos = rRangeMove;
                    else:
                        rPos = -rRangeMove;
                    rPos += arMedian[idx];
                    abFlipFlop[idx] = not abFlipFlop[idx];                    
                    print( "INF: diagnostic.useAllJoints: moving %s to %s" % (strJoint,rPos) );
                    motion.setStiffnesses( strJoint, 1. );
                    aMoveID[idx] = motion.post.angleInterpolation( strJoint, rPos, rUseSpeedTime, True );
                    time.sleep( 0.1 ); # time for stuff to init...
                    nCptSend += 1;

        #for each joint - end
        if( bPauseAllJointIfAtLeastIsTooBig ):
            bEveryOneMustRest = bOneJointWantToHaveRest;
            
        time.sleep( 0.01 );
    # while - end
    
    strOut = "at the end, consumption watcher:\n";
    for idx, strJoint in enumerate(listAllJoint):    
        consumption = watcher.getConsumption(strJoint);
        strOut += "%s: %s\n" % (strJoint, consumption);
    print strOut;
    print( "INF: diagnostic.useAllJoints - end" );
# useAllJoints - end


def useAllJoints_stop():
    print( "INF: diagnostic.useAllJoints_stop: sending the stop command !!!" );
    global global_bUseAllJointsMustStop;
    global_bUseAllJointsMustStop = True;
    # TODO: stop all motion moves!
# useAllJoints_stop - end    
    
def testAllJoints( bTestLegs = False, listJointToExclude = [] ):
    """
    try to make every joint to move.
    return list of joint with problem
    """
    global global_bTestAllJointsMustStop;
    global_bTestAllJointsMustStop = False;    
    aJointError = [];
    listAllJoint = motiontools.getDcmBodyJointName();
    motion = naoqitools.myGetProxy( "ALMotion" );
    rStepRef = 0.06;
    listJointLegs = poselibrary.PoseLibrary.getListJoints( "Legs" );
    listJointToExclude = poselibrary.PoseLibrary.getListJoints( listJointToExclude );
    if( not bTestLegs ):
        print( "INF: diagnostic.testAllJoints: excluding legs: %s" % listJointLegs );
    if( listJointToExclude != [] ):
        print( "INF: diagnostic.testAllJoints: excluding: %s" % listJointToExclude );
    for strJoint in listAllJoint:
        if( global_bTestAllJointsMustStop ):
            break;
        if( not bTestLegs ):
            if( strJoint in listJointLegs ):
                continue;
        if( strJoint in listJointToExclude ):
            continue;
        print( "INF: diagnostic.testAllJoints: testing %s" % strJoint );
        motion.setStiffnesses( strJoint, 1. );
        time.sleep( 0.5 );
        rCurrentStiffness = motion.getStiffnesses( strJoint )[0];
        if( rCurrentStiffness < 0.5 ):
            print( "WRN: diagnostic.testAllJoints: can't set stifness on '%s' (returned value: %s)" % (strJoint, rCurrentStiffness )  );
            aJointError.append( strJoint );
            continue;
           
        rStep = rStepRef;
        if( "Head" in  strJoint or "Neck" in strJoint ):
            rStep *= 2;
        rWaitTime = 0.7;
        rVal = motion.getAngles( strJoint, True )[0];        
        motion.setAngles( strJoint, rVal + rStep, 0.1 );
        time.sleep( rWaitTime );        
        rVal1 = motion.getAngles( strJoint, True )[0];                
        
        motion.setAngles( strJoint, rVal - rStep, 0.1 );
        time.sleep( rWaitTime );        
        rVal2 = motion.getAngles( strJoint, True )[0];        
        
        if( abs( rVal1 - rVal2 ) < rStep/10 ):
            # problem !
            print( "WRN: diagnostic.testAllJoints: after move, sensor doesn't return a too much difference '%s' (returned value: val: %s, val1: %s, val2: %s )" % ( strJoint,  rVal, rVal1, rVal2 )  );
            aJointError.append( strJoint );
            #~ continue;
        motion.setStiffnesses( strJoint, 0. );
    return aJointError;
# testAllJoints - end

def testAllJoints_stop():
    print( "INF: diagnostic.testAllJoints_stop: sending the stop command !!!" );
    global global_bTestAllJointsMustStop;
    global_bTestAllJointsMustStop = True;    

global_bLogAllJointsMustStop = False;
def logAllJoints( bTestLegs = True, bLogOnlyHighCurrent = False ):
    global global_bLogAllJointsMustStop;
    global_bLogAllJointsMustStop = False;
    
    listAllJoint = motiontools.getDcmBodyJointName();
    mem = naoqitools.myGetProxy( "ALMemory" );
    motion = naoqitools.myGetProxy( "ALMotion" );
    rStep = 0.06;
    listJointLegs = poselibrary.PoseLibrary.getListJoints( "Legs" );
    listAllDcmKey = [];
    listTemplates = ["Device/SubDeviceList/%s/Position/Actuator/Value", "Device/SubDeviceList/%s/Position/Sensor/Value", "Device/SubDeviceList/%s/ElectricCurrent/Actuator/Value", "Device/SubDeviceList/%s/ElectricCurrent/Sensor/Value" ];
    del listTemplates[2]; # remove electric actuator
    strPath = "/home/nao/logs/";
    try:
        os.makedirs( strPath );
    except BaseException, err:
        print( "WRN: diagnostic.logAllJoints: normal error: %s" % err );
    strFilename = strPath + filetools.getFilenameFromTime() + ".log";
    file = open( strFilename, "wt" );
    print( "INF: diagnostic.logAllJoints: logging every joints to '%s'..." % strFilename );
    aTestedJoint = [];
    for strJoint in listAllJoint:
        if( not bTestLegs ):
            if( strJoint in listJointLegs ):
                continue;
        aTestedJoint.append( strJoint );
        for name in listTemplates:
            strKey = name % strJoint;
            listAllDcmKey.append( strKey );
    timeLastSave = time.time();
    aPrevResults = [0.]*len(listAllDcmKey);
    nNbrDataPerJoint = len(listTemplates);
    # print header
    strTxt = "time stamp,";
    for strJoint in aTestedJoint:
        strTxt += "%s: Actuator, Sensor, Electric cur," % strJoint;
    file.write( strTxt + "\n" );    
    bAddedDataToFile = True;
    
    rHighVoltageThreshold = 0.3;
    
    while( not global_bLogAllJointsMustStop ):
        aResults = mem.getListData( listAllDcmKey );
        bIsDiff = False;
        for idx, rVal in enumerate( aResults ):
            if( aResults[idx] != None ):
                rDiff = abs( aPrevResults[idx] - aResults[idx] );
                if( ( rDiff > 0.01 ) or ( rDiff > 0.001 and idx == 2 ) ):
                    bIsDiff = True;
                    break;
        
        if( bIsDiff and bLogOnlyHighCurrent ):
            for idx in range(len(aTestedJoint)):
                if( aResults[idx*3+2] > rHighVoltageThreshold ): 
                    break;
            else:
                bIsDiff = False;
        
        if( bIsDiff ):            
            aPrevResults = aResults;
            strTxt = filetools.getFilenameFromTime() + ", ";
            for idx, rVal in enumerate( aResults ):
                if( rVal == None or rVal == 0. ):
                    strTxt += "0, ";
                else:
                    strTxt += "%5.4f, " % rVal;
            file.write( strTxt + "\n" );
            bAddedDataToFile = True;
            
        if( bAddedDataToFile and time.time() > timeLastSave + 5. ):
            timeLastSave = time.time();
            file.close();
            file = open( strFilename, "at" );
            bAddedDataToFile = False;
            
        time.sleep( 0.01 );
    # while - end    
    file.close(); #we never gone there :)            
# logAllJoints - end            

def logAllJoints_stop():
    print( "INF: diagnostic.testAllJoints_stop: sending the stop command !!!" );
    global global_bLogAllJointsMustStop;
    global_bLogAllJointsMustStop = True; 
    
global_bDetectHighCurrentMustStop = False
def detectHighCurrent():
    global global_bDetectHighCurrentMustStop;
    global_bDetectHighCurrentMustStop = False;     
    listAllJoint = motiontools.getDcmBodyJointName();
    mem = naoqitools.myGetProxy( "ALMemory" );
    strAlarmKeyName = "AlarmTooMuchCurrent";
    print( "INF: diagnostic.detectHighCurrent: started, alarm will goes to '%s'" % strAlarmKeyName );
    listAllDcmKey = [];
    listAllNominalCurrent = [];
    for strJoint in listAllJoint:
        listAllDcmKey.append( "Device/SubDeviceList/%s/ElectricCurrent/Sensor/Value" % strJoint );
        listAllNominalCurrent.append( motiontools.getNominalCurrent(strJoint) * 1.2 );
    
    rTimeTooHighThreshold = 5.; # in sec
    
    nNbrJoint = len( listAllJoint );
    listFirstTimeHigh = [time.time()]*nNbrJoint;
    
    while( True ):
        aResults = mem.getListData( listAllDcmKey );
        timeNow = time.time();
        for idx, rVal in enumerate( aResults ):
            if( rVal != None ):
                if( abs(rVal) > listAllNominalCurrent[idx] ):
                    if( timeNow - listFirstTimeHigh[idx] > rTimeTooHighThreshold ):
                        mem.raiseMicroEvent( strAlarmKeyName, listAllJoint[idx] ); # output the name of the joint alarming
                        print( "INF: diagnostic.detectHighCurrent: high current on %s: %5.2f" % (listAllJoint[idx], rVal) );
                        listFirstTimeHigh[idx] = timeNow; # reset it for some time
                else:
                    listFirstTimeHigh[idx] = timeNow; # will continuously follow the current time
                    
        time.sleep( 1. ); # should be less than rTimeTooHighThreshold
    # while - end    
# detectHighCurrent - end

def detectHighCurrent_stop():
    print( "INF: diagnostic.testAllJoints_stop: sending the stop command !!!" );
    global global_bDetectHighCurrentMustStop;
    global_bDetectHighCurrentMustStop = True; 

def testMicrophoneQuality():
    """
    generate two sounds: one blank and one not blank, then hear how they are played

    return an empty list if everything is ok, or a list of errors, cf getMicrophoneErrorText for the detail
    """
    audiodevice = naoqitools.myGetProxy("ALAudioDevice")
    player = naoqitools.myGetProxy('ALAudioPlayer');
    
    strTmpFolder = "/home/nao/.local/tmp/"; # for romeo it needs to be there
    filetools.makedirsQuiet( strTmpFolder );
    aFileNames = ["testsound_blank.wav", "testsound_noise.wav", "testsound_noise2.wav" ];
    rDuration = 3.;
    aMelody = [ [(-1,rDuration,20000)], [(72,rDuration,20000)], [(72,rDuration,20000)] ]; # C5: 72 (523.25 Hz) # C6: 84 (1046.50 Hz)
    rFreqRef = 523.25;
    aVolume = [50.,15.,39.];
    aListError = [];
    bAtLeastOneHaveSound = False;
    abTested = [False]*4;
    for nNumTest in range( len(aVolume) ):

        strName = strTmpFolder + aFileNames[nNumTest];

        wavObj = sound_analyse.computeMelody( aMelody[nNumTest], nSamplingFrequency=48000 );
        wavObj.write( strName );

        audiodevice.setOutputVolume(aVolume[nNumTest]);
        id = player.post.playFileFromPosition( strName, 0., 1., 0. );

        strNameDest = strName.replace( ".wav", "_rec.wav" );
        print( "%s: Recording to '%s'" % (time.time(), strNameDest ) );
        timeBegin = time.time();
        os.system( "parecord --channels=4 --no-remix --no-remap --rate 48000 > %s &  sleep %f; killall parecord" % (strNameDest,rDuration) );
        rDurationRecord = time.time() - timeBegin;
        print( "%s: Recording to '%s' - end (duration: %5.2fs)" % (time.time(), strNameDest, rDurationRecord ) );

        audiodevice.setOutputVolume(60.); # reset to a normal sound level

        if( rDurationRecord < rDuration ):
            print( "ERR: recording error !!!" );
            return[ -1 ];

        aRes = sound_analyse.computeStat( strNameDest );
        print( "4 max: %s, %s, %s, %s" % (aRes[0][0],aRes[1][0],aRes[2][0], aRes[3][0] ) );
        for nNumChannel in range( 4 ):
            rMax = aRes[nNumChannel][0];
            rFreq = aRes[nNumChannel][2];
            rFreqAmp = aRes[nNumChannel][3];
            if( nNumTest == 0 ):
                # no sound test
                if( rMax < 0.02 ):
                    aListError.append( 10 + nNumChannel );
                elif( rMax > 0.4 ):
                    aListError.append( 20 + nNumChannel );
            else:
                # on each following recording, we should found each time two mics with usable sound (depend on the distance to the speakers
                if( rMax > 0.8 ):
                    bAtLeastOneHaveSound = True;
                if( rMax > 0.1 and rMax < 0.99 ):
                    abTested[nNumChannel] = True;
                    print( "test: %d, channel: %d, found an enough good sound to analyse, freq is: %fHz, amp: %f" % ( nNumTest, nNumChannel, rFreq, rFreqAmp ) );
                    if( abs(rFreq - rFreqRef) > 2. ):
                        aListError.append( 40 + nNumChannel );

        # for each channel - end
    # for each test - end
    if( not bAtLeastOneHaveSound ):
        aListError.append( 30 );
    for nNumChannel in range( 4 ):
        if( not abTested[nNumChannel] ):
            aListError.append( 50+nNumChannel );
    return aListError;
# testMicrophoneQuality - end


def getMicrophoneErrorText( nNumError, nUseLang = -1 ):
    """
        1: the test doesn't works
        10+channel: zero sound (mic not connected?)
        20+channel: channel too noisy (or too much noise in the room?)
        30: hp not working ?
        40+channel: freq not good (too noisy or ...)
        50: non testé
    """
    dictTestError = { 
                "fr": "On dirait que quelquechose ne fonctionne plus. Voici la liste des problèmes probables: ",
                "en": "Something seems broken, here's the list of the potential problems: ",
                };
        
    aDict = [
                    { 
                        "fr": "Le microphone %d semble non connecté, ou ne fonctionne pas.",
                        "en": "The mike %d seems bad connected, or isn't working.",
                    },
                    { 
                        "fr": "Le microphone %d semble trop bruité, ou il y a trop de bruit dans la pièce.",
                        "en": "The mike %d seems too noisy, or there's too much noise in the room.",
                    },
                    { 
                        "fr": "Les hauts parleurs semblent ne pas fonctionner.",
                        "en": "The loudspeaker aren't working?",
                    },
                    { 
                        "fr": "Le microphone %d semble avoir une mauvaise qualité, il ne permettra pas une bonne analyse du son.",
                        "en": "The mike %d seems bad, it won't allow a good sound analyse.",
                    },
                    { 
                        "fr": "Le microphone %d n'as pas pu être testé complétement.",
                        "en": "The mike %d can't be tested totally.",
                    },                      
                ];
    if( nNumError == 1 ):
        return translate.chooseFromDict( dictTestError, nUseLang=nUseLang );
    nTypeError = nNumError / 10;
    nMic = nNumError % 10;
    txt = translate.chooseFromDict( aDict[nTypeError-1], nUseLang=nUseLang );
    if( nTypeError != 3 ):
        txt = txt % nMic;
    return txt;
# getMicrophoneErrorText - end

def getAllLimits( bMoveToComputeRealLimit = False, bTestLegs = False ):
    """
    get all limits (dcm, motion, tested real)
    
    # current state on my romeo
    JointName ; theo min /    max ; thmot min/    max ;  dcm min /    max ; motion min /    max ; real min /    max ;           comments                      ;
    NeckYaw ;   -2.094 /   2.094;   -2.059 /   2.059;   -1.571 /   1.571;     -1.571 /   1.571;   -1.578 /   1.557;  diff firmware-theoric! diff motion-theoric!;
    NeckPitch ;   -0.349 /   0.698;   -0.314 /   0.663;   -0.349 /   0.698;     -0.349 /   0.698;    0.031 /   0.712;  diff motion-theoric! Neg diff current dcm/motion! Diff in real!;
    HeadPitch ;   -0.266 /   0.332;   -0.257 /   0.297;   -0.279 /   0.349;     -0.349 /   0.279;   -0.163 /   0.225;  diff firmware-theoric! diff motion-theoric! Diff dcm-motion Neg diff current dcm/motion! Diff in real!;
    HeadRoll ;   -0.524 /   0.524;   -0.489 /   0.489;   -0.349 /   0.349;     -0.349 /   0.349;   -0.364 /   0.370;  diff firmware-theoric! diff motion-theoric!;
    LShoulderPitch ;   -1.384 /   2.281;   -1.349 /   2.246;   -1.445 /   2.220;     -1.445 /   2.220;   -1.388 /   2.197;  diff firmware-theoric! diff motion-theoric! Neg diff current dcm/motion! Diff in real!;
    LShoulderYaw ;   -0.612 /   0.959;   -0.577 /   0.924;   -0.431 /   1.140;     -0.430 /   1.140;    0.084 /   0.966;  diff firmware-theoric! diff motion-theoric! Neg diff current dcm/motion! Diff in real!;
    LElbowRoll ;   -2.250 /   1.939;   -2.215 /   1.904;   -2.094 /   2.094;     -2.094 /   2.094;   -2.134 /   1.968;  diff firmware-theoric! diff motion-theoric! Diff in real!;
    LElbowYaw ;   -1.558 /   0.013;   -1.523 /   0.004;   -1.571 /   0.000;     -1.571 /   0.000;   -0.598 /  -0.598;  diff firmware-theoric! diff motion-theoric! Diff in real!;
    LWristRoll ;   -3.665 /   0.524;   -3.630 /   0.489;   -3.665 /   0.524;     -3.665 /   0.524;    0.021 /   0.503;  diff motion-theoric! Diff in real!     ;
    LWristYaw ;   -0.436 /   0.436;   -0.401 /   0.401;   -0.436 /   0.436;     -0.436 /   0.436;   -0.431 /   0.408;  diff motion-theoric! Neg diff current dcm/motion!;
    LWristPitch ;   -1.023 /   0.932;   -0.988 /   0.897;   -0.977 /   0.977;     -0.977 /   0.977;   -0.931 /   0.968;  diff firmware-theoric! diff motion-theoric! Diff in real!;
    LHand ;    0.000 /   4.267;   -4.232 /  -0.035;    0.000 /   4.260;      0.000 /   1.000;    0.015 /   0.302;  diff firmware-theoric! diff motion-theoric! Diff dcm-motion Diff in real!;
    TrunkYaw ;   -0.792 /   0.792;   -0.757 /   0.757;   -0.785 /   0.785;     -0.785 /   0.785;   -0.772 /   0.782;  diff firmware-theoric! diff motion-theoric!;
    RShoulderPitch ;   -1.490 /   2.175;   -1.455 /   2.140;   -1.445 /   2.220;     -1.445 /   2.220;   -1.407 /   2.198;  diff firmware-theoric! diff motion-theoric! Neg diff current dcm/motion!;
    RShoulderYaw ;   -1.133 /   0.437;   -1.099 /   0.402;   -1.140 /   0.431;     -1.140 /   0.430;   -1.144 /   0.460;  diff firmware-theoric! diff motion-theoric! Neg diff current dcm/motion!;
    RElbowRoll ;   -1.940 /   2.249;   -1.905 /   2.214;   -2.094 /   2.094;     -2.094 /   2.094;   -1.979 /   2.123;  diff firmware-theoric! diff motion-theoric! Diff in real!;
    RElbowYaw ;   -0.013 /   1.557;   -0.005 /   1.522;    0.000 /   1.571;      0.000 /   1.571;    0.390 /   0.497;  diff firmware-theoric! diff motion-theoric! Diff in real!;
    RWristRoll ;   -0.524 /   3.665;   -0.489 /   3.630;   -0.524 /   3.665;     -0.524 /   3.665;   -0.506 /   3.683;  diff motion-theoric!                   ;
    RWristYaw ;   -0.436 /   0.436;   -0.401 /   0.401;   -0.436 /   0.436;     -0.436 /   0.436;   -0.422 /   0.399;  diff motion-theoric! Neg diff current dcm/motion!;
    RWristPitch ;   -1.022 /   0.933;   -0.987 /   0.898;   -0.977 /   0.977;     -0.977 /   0.977;   -0.927 /   0.928;  diff firmware-theoric! diff motion-theoric! Diff in real!;
    RHand ;    0.000 /   4.267;   -4.267 /   0.000;    0.000 /   4.260;      0.000 /   1.000;    0.055 /   1.022;  diff firmware-theoric! diff motion-theoric! Diff dcm-motion Diff in real!;
    """
    global global_bAllLimitsMustStop;
    global_bAllLimitsMustStop = False;    
    import romeo
    listAllJoint = motiontools.getDcmBodyJointName();
    mem = naoqitools.myGetProxy( "ALMemory" );
    motion = naoqitools.myGetProxy( "ALMotion" );
    mover = motiontools.DCM_Mover("DCM_motion");
    listJointLegs = poselibrary.PoseLibrary.getListJoints( "Legs" );
    listAllDcmKey = [];
    listTemplates = [
                            "Device/SubDeviceList/%s/Position/Actuator/Value",
                            "Device/SubDeviceList/%s/Position/Actuator/Min",
                            "Device/SubDeviceList/%s/Position/Actuator/Max",
                            
                            "Device/SubDeviceList/%s/Position/Sensor/Value",
                            "Device/SubDeviceList/%s/Position/Sensor/Min",
                            "Device/SubDeviceList/%s/Position/Sensor/Max",
                        ];
    print( "\nINF: diagnostic.getAllLimits: beginning..." );
    
    astrListShoulderJoints = ["LShoulderYaw", "RShoulderYaw","LShoulderPitch", "RShoulderPitch"];
    if( bMoveToComputeRealLimit ):
        # put the whole body in a zero position
        motion.setStiffnesses( "Head", 1. );
        motion.setStiffnesses( "Arms", 1. );
        mover.moveJointsWithSpeed( "Head", [0.]*4, 0.2 );
        mover.moveJointsWithSpeed( "Arms", [0.]*4*2, 0.2 );
        
        motion.setStiffnesses( astrListShoulderJoints , 1. );
        mover.moveJointsWithSpeed( astrListShoulderJoints, [0.5,-0.5,0.,0.], 0.2 );
    
    strOut = "\n     JointName ; theo min /    max ; thmot min/    max ;  dcm min /    max ; motion min /    max ; real min /    max ;           comments                      ;\n"; # diff min /     max ; 
    aTestedJoint = [];
    #~ listAllJoint = ["LElbowYaw","RElbowYaw"];
    listJointWithError = [];
    for strJoint in listAllJoint:
        if( global_bAllLimitsMustStop ):
            break;
        if( not bTestLegs ):
            if( strJoint in listJointLegs ):
                continue;
        listValDcm = [s%strJoint for s in listTemplates];
        aResultsDcm = mem.getListData( listValDcm );
        rMinDcm = aResultsDcm[1];
        rMaxDcm = aResultsDcm[2];
        aResultMotion = motion.getLimits( strJoint )[0];
        rMinMotion = aResultMotion[0];
        rMaxMotion = aResultMotion[1];
        #~ print( "%s:" % strJoint );
        #~ print( "aResultsDcm: %s" % aResultsDcm );
        #~ print( "aResultMotion: %s" % aResultMotion );
        rDiffMin = rMinMotion - rMinDcm;
        rDiffMax = rMaxDcm - rMaxMotion;
        rStrictMin = max( rMinDcm, rMinMotion );        
        rStrictMax = min( rMaxDcm, rMaxMotion );
        theoricModelLimits = romeo.model.getLimits( strJoint );
        rThMin = theoricModelLimits[0];
        rThMax = theoricModelLimits[1];
        rThMotMin = theoricModelLimits[2];
        rThMotMax = theoricModelLimits[3];

        rMinReal = rMaxReal = 0.;        
        strAbnormal = "";        
        if( bMoveToComputeRealLimit ):
            nNbrTimeToTest = 3;
            for i in range( nNbrTimeToTest ):
                print( "INF: diagnostic.getAllLimits: moving '%s'" % strJoint );            
                # check min and max is really possible
                rSpeedRatio = 0.2;
                if( "Wrist" in strJoint ):
                    rSpeedRatio = 1.;
                motion.setStiffnesses( strJoint, 1. );
                bMoveError = mover.moveJointsWithSpeed( strJoint, rMinDcm, rSpeedRatio, bWaitEndPosition = True, bVerbose = True ) == None;
                if( bMoveError ):
                    print( "WRN: %s: move error to min" % strJoint );
                rMinReal = min(mem.getData( listValDcm[3] ), rMinReal);
                bMoveError = mover.moveJointsWithSpeed( strJoint, rMaxDcm, rSpeedRatio, bWaitEndPosition = True, bVerbose = True ) == None;
                if( bMoveError ):
                    print( "WRN: %s: move error to max" % strJoint );
                rMaxReal = max( mem.getData( listValDcm[3] ), rMaxReal );
                rZero = 0.;
                if( strJoint == "LShoulderYaw" ):
                    rZero = 0.5;
                elif( strJoint == "RShoulderYaw" ):
                    rZero = -0.5;
                bMoveError = mover.moveJointsWithSpeed( strJoint, rZero, rSpeedRatio, bWaitEndPosition = True, bVerbose = True ) == None;        
                if( bMoveError ):
                    print( "WRN: %s: move error to zero" % strJoint );
        #if( abs(rThMin-rMinDcm) > 0.001 or abs(rThMax-rMaxDcm) > 0.001 ): # if we want the dcm to have the hardware limits
        if( abs(rThMotMin-rMinDcm) > 0.001 or abs(rThMotMax-rMaxDcm) > 0.001 ): # if we want the dcm to have the motion limits
            strAbnormal += " diff firmware-theoric!";
        if( abs(rThMotMin-rMinMotion) > 0.001 or abs(rThMotMax-rMaxMotion) > 0.001 ):
            strAbnormal += " diff motion-theoric!";        
        if( abs(rDiffMin) > 0.04 or abs(rDiffMax) > 0.04 ):
            strAbnormal += " Diff dcm-motion";        
        if( rDiffMin < 0. or rDiffMax < 0. ):
            strAbnormal += " Neg diff current dcm/motion!";
        if( ( abs(rMinReal-rMinMotion) > 0.04 or abs(rMaxReal-rMaxMotion) > 0.04 ) and bMoveToComputeRealLimit ):
            strAbnormal += " Diff in real! (%5.3f/%5.3f)" % ((rMinMotion-rMinReal),(rMaxReal-rMaxMotion));
        if( abs( rMaxReal - rMinReal ) < 0.2 and bMoveToComputeRealLimit ):
            strAbnormal += " NO MOVE!";
        strOut += "%14s ; %8.3f /%8.3f; %8.3f /%8.3f; %8.3f /%8.3f;   %8.3f /%8.3f; %8.3f /%8.3f; %-40s;\n" % (strJoint, rThMin, rThMax, rThMotMin, rThMotMax, rMinDcm,rMaxDcm, rMinMotion, rMaxMotion,  rMinReal, rMaxReal, strAbnormal);  #  %9f /%9f; rDiffMin, rDiffMax,
        if( strAbnormal != "" ):
            listJointWithError.append( strJoint );
    # for - end
    print( strOut );
    print( "Joint with error: %s" % listJointWithError );
    if( bMoveToComputeRealLimit ):
        motion.setStiffnesses( astrListShoulderJoints , 0. );    
    print( "INF: diagnostic.getAllLimits: done" );
# getAllLimits - end


def getAllLimits_stop():
    print( "INF: diagnostic.getAllLimits_stop: sending the stop command !!!" );
    global global_bAllLimitsMustStop;
    global_bAllLimitsMustStop = True;
# getAllLimits_stop - end