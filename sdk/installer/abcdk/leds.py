# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Leds tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

# this module should be called file, but risk of masking with the class file.

"""Methods to help controling leds"""
print( "importing abcdk.leds" );

import math
import random
import sys
import time

import config
import color
import naoqitools
import system
import test

def getDCM_ProxyForLeds():
    """
    Get a proxy on DCM, to use to send leds.
    (so if you've got a multi dcm robot, it will be the one managing leds)
    """
    if( system.isOnRomeo() ):
        strLedName = "DCM_video";
    else:
        strLedName = "DCM";
    try:
        dcm = naoqitools.myGetProxy( strLedName );
    except Exception, err:
        print( "ERR: getDCM_ProxyForLeds: can't connect to '%s'" % strLedName );
        dcm = None;
    return dcm;
# getDCM_ProxyForLeds - end    


def getSide( nIndex ):
  """ get side left/right from 0..1 """
  aSide = [ "Left", "Right" ];
  if( nIndex < 0 or nIndex > 1 ):
    print( "ERR: leds.getSide: index %d out of range" % nIndex );
    nIndex = 0;
  return aSide[nIndex];
# getSide - end

def getEarLedName( nIndex, nSideIndex = 0 ):
    "get dcm leds ears device name from index"
    nNbrMax = 10;
    if( nIndex >= nNbrMax or nIndex < 0 ):
        print( "ERR: leds.getEarLedName: index out of range (%d)" % nIndex );
        return "";
    nAngle = (360/nNbrMax) * nIndex;
    strName = "Ears/Led/%s/%dDeg/Actuator/Value" % ( getSide( nSideIndex ), nAngle );
    return strName;
# getEarLedName - end


def circleLedsEyes( nColor, rTime, nNbrTurn ):
  # launch a leds animation using one color
  leds = naoqitools.myGetProxy( "ALLeds" );
  nNbrSegment = 8;
  for i in range( nNbrSegment*nNbrTurn ):
    leds.post.fadeRGB( "FaceLed%d" % (i%nNbrSegment) , nColor, rTime );
    leds.post.fadeRGB( "FaceLed%d" % (i%nNbrSegment) , 0x000000, rTime*1.25 );
    time.sleep( rTime*0.25 );
  time.sleep( rTime*0.5 ); # wait last time
# circleLedsEyes - end

def circleLedsEars( rTime, nNbrTurn ):
  # launch a leds animation using one color
  leds = naoqitools.myGetProxy( "ALLeds" );
  nNbrSegment = 10;
  for i in range( nNbrSegment*nNbrTurn ):
    leds.post.fade( "LeftEarLed%d" % (i%nNbrSegment+1) , 1., rTime );
    leds.post.fade( "RightEarLed%d" % (i%nNbrSegment+1) , 1., rTime );
    leds.post.fade( "LeftEarLed%d" % (i%nNbrSegment+1) , 0., rTime*1.25 );
    leds.post.fade( "RightEarLed%d" % (i%nNbrSegment+1) , 0., rTime*1.25 );
    time.sleep( rTime*0.25 );
  time.sleep( rTime*0.5 ); # wait last time
# circleLedsEars - end

def randomLedsEars( rTime, bDontWait = False  ):
    # light randomly one led in both ears
    leds = naoqitools.myGetProxy( "ALLeds" );
    nNumSegment = random.randint( 1, 10 );
    leds.post.fade( "LeftEarLed%d" % (nNumSegment) , 1., rTime );
    leds.post.fade( "RightEarLed%d" % (nNumSegment) , 1., rTime );
    if( not bDontWait ):
        time.sleep( rTime );
# circleLedsEars - end

def setEarsLedsIntensity( rIntensity = 1.0, nTimeMs = 10, bDontWait = False ):
  # set all leds of the same intensity
    "light on/off all the ears leds"
    dcm = getDCM_ProxyForLeds();
    riseTime = dcm.getTime(nTimeMs);
    for j in range( 2 ):
        for i in range( 10 ):
            strDeviceName = getEarLedName( i, j );
            dcm.set( [ strDeviceName, "Merge",  [[ rIntensity, riseTime ]] ] );    
    if( not bDontWait ):
        time.sleep( nTimeMs / 1000. );
# setEarsLedsIntensity - end

def getBrainLedName( nNumLed ):
    """
    get the name of the dcm led device by it's number
    0 => front left; 1 => next in clock wise
    """
    
       #~ names = [
            #~ 'Head/Led/Front/Right/1/Actuator/Value',
            #~ 'Head/Led/Front/Right/0/Actuator/Value',
            #~ 'Head/Led/Middle/Right/0/Actuator/Value',
            #~ 'Head/Led/Rear/Right/0/Actuator/Value',
            #~ 'Head/Led/Rear/Right/1/Actuator/Value',
            #~ 'Head/Led/Rear/Right/2/Actuator/Value',
            #~ 'Head/Led/Rear/Left/2/Actuator/Value',
            #~ 'Head/Led/Rear/Left/1/Actuator/Value',
            #~ 'Head/Led/Rear/Left/0/Actuator/Value',
            #~ 'Head/Led/Middle/Left/0/Actuator/Value',
            #~ 'Head/Led/Front/Left/0/Actuator/Value',
            #~ 'Head/Led/Front/Left/1/Actuator/Value']
            
    if( nNumLed <= 1 ):
        return "Head/Led/Front/Right/%d/Actuator/Value" % (1-nNumLed);
    if( nNumLed >= 10 ):
        return "Head/Led/Front/Left/%d/Actuator/Value" % (nNumLed-10);

    if( nNumLed <= 2 ):
        return "Head/Led/Middle/Right/%d/Actuator/Value" % (2-nNumLed);
    if( nNumLed >= 9 ):
        return "Head/Led/Middle/Left/%d/Actuator/Value" % (nNumLed-9);

    if( nNumLed <= 5 ):
        return "Head/Led/Rear/Right/%d/Actuator/Value" % (nNumLed-3);
    if( nNumLed >= 6 ):
        return "Head/Led/Rear/Left/%d/Actuator/Value" % (8-nNumLed);

    print( "ERR: getBrainLedName: index out of range (%d)" % nNumLed );
    return "";
# getBrainLedName - end

def setBrainLedsIntensity( rIntensity = 1.0, nTimeMs = 10, bDontWait = False ):
    "light on/off all the brain leds"
    dcm = getDCM_ProxyForLeds();
    riseTime = dcm.getTime(int(nTimeMs));
    for i in range( 12 ):
        strDeviceName = getBrainLedName( i );
        dcm.set( [ strDeviceName, "Merge",  [[ rIntensity, riseTime ]] ] );    
    if( not bDontWait ):
        time.sleep( nTimeMs / 1000. );
# setBrainLedsIntensity - end

def setOneBrainIntensity( nLedIndex, rIntensity = 1.00, nTimeMs = 10, bDontWait = False ):
    """
    set one led beyond all the brain leds
    nLedIndex in [0,11]
    """
    dcm = getDCM_ProxyForLeds();
    riseTime = dcm.getTime(int( nTimeMs ));
    strDeviceName = getBrainLedName( nLedIndex );
    dcm.set( [ strDeviceName, "Merge",  [[ float( rIntensity ), riseTime ]] ] );         # le float ici est ultra important car sinon venant de chorégraphe 1.0 => 1 (depuis les sliders de params)
    if( not bDontWait ):
        time.sleep( nTimeMs/1000. );
# setOneBrainIntensity - end

def setMouthLeds( anColor, rTimeSec = 1., bDontWait = False ):
    """
    Light on/off all the romeo mouth leds
    - anColor: the three RGB color of each mouth led (left top, right top, bottom)
    WRN: Too much DCM call, so moved to dcmMethod "setMouthColor" using alias.
    but this one is working also !!!
    """
    dcm = getDCM_ProxyForLeds();
    riseTime = dcm.getTime(int(rTimeSec*1000));
    for i in range( 3 ):
        for nColor in range(3):
            rIntensity = (((anColor[i])>>(nColor*8))&0xFF)/255.;
            nIndexBrain = 3+nColor+i*3;
            strDeviceName = getBrainLedName( nIndexBrain );
            #~ print( "strDeviceName: %s" % strDeviceName );
            dcm.set( [ strDeviceName, "Merge",  [[ rIntensity, riseTime ]] ] );
    if( not bDontWait ):
        time.sleep( rTimeSec );
# setMouthLeds - end

def setBrainVuMeter( nLeftLevel, nRightLevel, rIntensity = 1.0, bDontWait = False, bInverseSide = False ):
    """
    use the brain leds as vu meter (left and right separated)
    the 0 is in the front of Nao
    nXxxLevel in [0,6] => 0: full lightoff; 6 => full litten
    bInverseSide: the 0 becomes at bottom of Nao
    """
    dcm = getDCM_ProxyForLeds();
    rTime = 0.05
    riseTime = dcm.getTime(int( rTime*1000 ));
    for i in range( 6 ):
        if( not bInverseSide ):
            strDeviceNameR = getBrainLedName( i );
            strDeviceNameL = getBrainLedName( 11-i );
        else:
            strDeviceNameR = getBrainLedName( 5-i );
            strDeviceNameL = getBrainLedName( 11-(5-i) );            
        if( i < nLeftLevel ):
            rIntL = rIntensity;
        else:
            rIntL = 0.;
        if( i < nRightLevel ):
            rIntR = rIntensity;
        else:
            rIntR = 0.;        
        dcm.set( [ strDeviceNameL, "Merge",  [[ float( rIntL ), riseTime ]] ] );         # le float ici est ultra important car sinon venant de chorégraphe 1.0 => 1 (depuis les sliders de params)
        dcm.set( [ strDeviceNameR, "Merge",  [[ float( rIntR ), riseTime ]] ] );
    if( not bDontWait ):
        time.sleep( rTime );
# setBrainVuMeter - end

def setColorToEyes( anList8Color, rTime = 1.,  nEyesMask = 0x3 ):
    """
    set a list of 8 color to eyes
    rTime: time in sec of the fade
    nEyesMask: 1: left, 2: right, 3: both
    """
#    print( "anList8Color: %s" % str( anList8Color ) );
    leds = naoqitools.myGetProxy( 'ALLeds' );
    for nNumSide in range( 2 ):
        nSideValMask = 1 << nNumSide;
        if( True ): # nEyesMask & nSideValMask ): TODO: bien gerer le mask
            for nNumLed in range( len( anList8Color ) ):
                strName = "FaceLed%s%d" % ( getSide(nNumSide), nNumLed );
                nColor = anList8Color[nNumLed];
                # no need of a mirror: already handled in ALLeds !
                # nIndexMirror = 7 - nNumLed;
#                print( "strName: %s, color: %x, time: %f" % ( strName, nColor, rTime ) );
                leds.post.fadeRGB( strName, nColor, rTime );
        # if - end
    # for - end
# setColorToEyes - end


def setEyeVuMeter( rLevel, nEyesMask = 0x3, rIntensity = 1., bDontWait = False ):
    """
    use one eye as vu a meter (left and right separated)
    rLevel: [0,1], level to set to eyes
    nEyesMask: 1: left, 2: right, 3: both
    rIntensity: set full intensity
    """
    dcm = getDCM_ProxyForLeds();
    rTime = 0.03;
    anColor = [0]*8;
    if( rLevel > 0.999 ):
        rLevel = 0.999; # so, we will have an rIntensity set to full
    nLevel = int(rLevel*8);
    
    for i in range( nLevel + 1 ):
        if( i == nLevel ):
            rIntensity *= ((rLevel*8)-nLevel);
        nBaseColor = (int)(rIntensity*0xFF);
        anColor[i] = (nBaseColor<<16)+(nBaseColor<<8)+(nBaseColor<<0);

    setColorToEyes(anColor, rTime, nEyesMask );
    if( not bDontWait ):
        time.sleep( rTime );
# setEyeVuMeter - end

def getEyeLedName( nNumLed, nSide, nColor = 3 ):
    """
    get the name of the dcm led device by it's number"
    nNumLed: 0 => Top internal led, 1 => internal high led, 2 => internal low led, 3 => bottom internal led ...
    nSide: 0 => left; 1 => right
    nColor: 0 => Blue, 1 => Green, 2 => Red, 3 => all
    return name or an array of 3 name (when nColor is set 3)
    """
    
    # device are on the form of  "Face/Led/Red/Right/315Deg/Actuator/Value"
    strTemplate = "Face/Led/%s/%s/%dDeg/Actuator/Value";

    if( nNumLed > 7 or nNumLed < 0 ):
        print( "ERR: abcdk.led.getEyeLedName: index out of range (%d)" % nNumLed );
        return;
    if( nSide > 1 or nSide < 0 ):
        print( "ERR: abcdk.led.getEyeLedName: side out of range (%d)" % nSide );
        return;
    if( nColor > 3 or nColor < 0 ):
        print( "ERR: abcdk.led.getEyeLedName: color out of range (%d)" % nColor );
        return;

    astrColor = [ "Blue", "Green", "Red"];
    astrSide = [ "Left", "Right"];
    anAngle = [0, 45, 90, 135, 180, 225, 270, 315];
    if( nSide == 1 ):
        nNumLed = 7 - nNumLed;
    if( nColor < 3 ):
        return strTemplate % ( astrColor[nColor], astrSide[nSide], anAngle[nNumLed] );
    
    return  [
                    strTemplate % ( astrColor[0], astrSide[nSide], anAngle[nNumLed] ),
                    strTemplate % ( astrColor[1], astrSide[nSide], anAngle[nNumLed] ),
                    strTemplate % ( astrColor[2], astrSide[nSide], anAngle[nNumLed] )
                ];
    
    return "";
# getEyeLedName - end

def getBrainLedNumberByAngle( rAngle ):
    """
    get breain led number from its angle, and ratio of pointing 0..1
    angle in radians (0 is front, pi/2 is left, pi is rear...)
    """
    rPi = 3.14159;
    arAngleOfLed = [ 
            rPi / 8,
            rPi / 2 - rPi / 8,
            rPi / 2,
            rPi / 2 + rPi / 8,
            rPi / 2 + rPi / 4,
            rPi / 2 + rPi / 4 + rPi / 8,
            rPi + rPi / 8,
            rPi + rPi / 4,
            rPi + rPi / 4 + rPi / 8,
            rPi + rPi / 2,
            rPi + rPi / 2 + rPi / 8,
            rPi * 2 - rPi / 8,
            rPi * 2, # for remaining computing (not used!)
    ];
    nNbrLeds = 12;
    
    if( rAngle < 0. ):
        rAngle += 2*rPi;
    if( rAngle >= 2*rPi ):
        rAngle -= 2*rPi;
    
    for i in range( len( arAngleOfLed ) ):
        if( rAngle <= arAngleOfLed[i] ):
            break;
    nOther = i - 1;
    if( nOther < 0 ):
        nOther += nNbrLeds;
        rAngleOther = arAngleOfLed[nNbrLeds-1] - rPi * 2;
    else:
        rAngleOther = arAngleOfLed[nOther];
    return [nNbrLeds-i-1,1. - ( (arAngleOfLed[i]-rAngle)/(arAngleOfLed[i]-rAngleOther) ), nNbrLeds-nOther-1 ];
# getBrainLedNumberByAngle - end

#print( str( getBrainLedNumberByAngle( 1.570000 ) ) );

def setBrainLedByAngle( rAngle, bCleanOther = True ):
    "light brain leds at a given angle (0: front, pi/2: left)"
    if( bCleanOther ):
        setBrainLedsIntensity( 0., bDontWait = True );
    nLed1, rRatio, nLed2 = getBrainLedNumberByAngle( rAngle );
    strDeviceName1 = getBrainLedName( nLed1 );
    strDeviceName2 = getBrainLedName( nLed2 );
    dcm = getDCM_ProxyForLeds();
    dcm.set( [ strDeviceName1, "Merge",  [[ rRatio, dcm.getTime(20) ]] ] );
    dcm.set( [ strDeviceName2, "Merge",  [[ 1. - rRatio, dcm.getTime(20) ]] ] );        
# setBrainLedByAngle - end          
            

def getEyeColor( nNumLed, nSide, nColor = 3 ):
    """
    return the color of one RGB leds, only one channel or the 3
    nNumLed: 0 => Top internal led, 1 => internal high led, 2 => internal low led, 3 => bottom internal led ...
    nSide: 0 => left; 1 => right
    nColor: 0 => Blue, 1 => Green, 2 => Red, 3 => all
    return a value 0..0xff or a value [r,g,b] if nColor == 3
    """
    leds = naoqitools.myGetProxy( "ALLeds" );
    name = getEyeLedName( nNumLed, nSide, nColor );
    if( len( name ) == 3 ):
        anRet = [];
        for i in range( 3 ):
            anRet.append( int(leds.getIntensity( name[i] ) * 255 ));
        return anRet;
    return int( leds.getIntensity( name ) * 255 );
# getEyeColor - end
    
class DcmMethod:
    "This class is intended to put (and get) color to eyes leds, with the less cpu and thread (ab)uses"
    def __init__( self ):
        self.dcm = None;
        
    def createProxy(self):
        self.dcm = getDCM_ProxyForLeds();
        self.dcmDefault = naoqitools.myGetProxy( "DCM" );        
        self.mem = naoqitools.myGetProxy( "ALMemory" );
        if( self.mem == None ):
            print( "WRN: leds.DcmMethod: ALMemory/Naoqi not found" );
            return False;
        if( self.dcm == None ):
            print( "WRN: leds.DcmMethod: DCM proxy/Naoqi not found" );
            return False;            
        return True;
            
    def reset(self):
        if( self.dcm == None ):
            if( not self.createProxy() ):
                return;
        self.createAliases();
        # some memory for EyeCircle: 
        self.nEyeCircle_NextLedPosition = 0; # position of next led to lighten
        self.tEyeCircle_timeNextSent = -sys.maxint; # time at when lighten this led (in dcm time)
        self.EarsLoading_bLastLit = False; # a flip flop to make the blinking
        self.EarsLoading_nLastNbrEarToLit=-1; # last number to prevent erasing too much
        self.EarsLoading_timeLastCall = time.time()-1000;
        
        self.tBrainCircle_timeNextSent = time.time()-100; # time at when lighten this led (in python time)
        
        self.nNbrBrainSegment = 12;        
        
    def createAliases( self ):
        # create alias for easy access: all eyes, and one leds by one for each side or both
        
        bVerbose = False;
        
        strEyeTemplate = "Device/SubDeviceList/Face/Led/%s/%s/%dDeg/Actuator/Value"; # color, side, angle
        astrColorRGB = ["Red", "Green", "Blue"];
        astrSide = ["Left", "Right"];
        anOrientation = [0,45,90,135,180,225,270,315];
        
        self.eyesDevice = [];
        self.eyesAliasName = "Face";
        for strSide in astrSide:
            for nAngle in anOrientation:    
                for strColor in astrColorRGB:
                    self.eyesDevice.append( strEyeTemplate % ( strColor, strSide, nAngle ) );
        self.dcm.createAlias( [self.eyesAliasName, self.eyesDevice] );
        
        self.eyesDeviceL = [];
        self.eyesDeviceR = [];        
        self.eyesAliasNameL = "FaceL";
        self.eyesAliasNameR = "FaceR";
        for nAngle in anOrientation:
            for strColor in astrColorRGB:
                self.eyesDeviceL.append( strEyeTemplate % ( strColor, astrSide[0], nAngle ) );
                self.eyesDeviceR.append( strEyeTemplate % ( strColor, astrSide[1], nAngle ) );
        self.dcm.createAlias( [self.eyesAliasNameL, self.eyesDeviceL] );
        self.dcm.createAlias( [self.eyesAliasNameR, self.eyesDeviceR] );
        
        # one by one: creating FaceL0, FaceL1, ... and FaceR0,... and Face0,... (but not saving alias name)
        strTemplateNameL = "FaceL%d";
        strTemplateNameR = "FaceR%d";
        strTemplateName = "Face%d";        
        for nIdxAngle, nValAngle in enumerate(anOrientation):
            self.eyesDeviceL = [];
            self.eyesDeviceR = [];
            self.eyesDevice = [];            
            for strColor in astrColorRGB:
                strL = strEyeTemplate % ( strColor, astrSide[0], anOrientation[7-nIdxAngle] );
                strR = strEyeTemplate % ( strColor, astrSide[1], nValAngle );
                self.eyesDeviceL.append( strL );
                self.eyesDeviceR.append( strR );
                self.eyesDevice.append( strL );
                self.eyesDevice.append( strR );
            strAliasName = strTemplateNameL % nIdxAngle;
            #~ print( "DBG: leds.DcmMethod.createAliases: '%s' => %s" % (strAliasName,self.eyesDeviceL) );
            self.dcm.createAlias( [strAliasName, self.eyesDeviceL] );
            strAliasName = strTemplateNameR % nIdxAngle;
            if( bVerbose ):
                print( "DBG: leds.DcmMethod.createAliases: '%s' => %s" % (strAliasName,self.eyesDeviceR) );            
            self.dcm.createAlias( [ strAliasName, self.eyesDeviceR] );
            strAliasName = strTemplateName % nIdxAngle;
            if( bVerbose ):
                print( "DBG: leds.DcmMethod.createAliases: '%s' => %s" % (strAliasName,self.eyesDevice) );
            self.dcm.createAlias( [strAliasName, self.eyesDevice] );
        # for - end
        
        strChestTemplate = "Device/SubDeviceList/ChestBoard/Led/%s/Actuator/Value";
        aChestDevice = [];
        for strColor in astrColorRGB:
            strDevice = strChestTemplate % ( strColor );
            aChestDevice.append( strDevice );
        self.strChestAliasName = "Chest";
        self.dcm.createAlias( [self.strChestAliasName, aChestDevice] );
        if( bVerbose ):
            print( "DBG: leds.DcmMethod.createAliases: '%s' => %s" % (self.strChestAliasName,aChestDevice) );
        
        # Creating Ears, EarL, EarR, Ears0, EarsL0, ...
        nNbrEarSegment = 10;
        strTemplate = "Device/SubDeviceList/Ears/Led/%s/%dDeg/Actuator/Value";
        aAllDevice = [];
        aAllDeviceLR = [[],[]];
        for i in range( nNbrEarSegment ):
            aBothDevice = [];
            for idx,side in enumerate(astrSide):
                strDevice = strTemplate % ( side, (i*36) );
                aAllDevice.append( strDevice );
                aAllDeviceLR[idx].append( strDevice );
                aBothDevice.append( strDevice );
                self.dcm.createAlias( ["Ear%s%d"%(astrSide[idx][0],i), [strDevice]] );
            self.dcm.createAlias( ["Ear%d"%i, aBothDevice] );
        for idx,side in enumerate(astrSide):
            self.dcm.createAlias( ["Ear"+astrSide[idx][0], aAllDeviceLR[idx]] );    
        self.dcm.createAlias( ["Ears", aAllDevice] );
        
        # Romeo Leds mouth
        if( system.isOnRomeo() ):
            aAllDevice = [];
            strTemplate = "Device/SubDeviceList/FaceBoard/%sLed%d/Value";
            for i in range(3):
                for strColor in astrColorRGB:
                    strDevice = strTemplate % ( strColor, i+1 );
                    aAllDevice.append( strDevice );
            self.dcm.createAlias( ["Mouth", aAllDevice] );            
        
            # Alternate mouth commanded by the brain alias
            aAllDevice = [];
            nIdxBrainLed = 3;
            for i in range(3):
                nInvertRGB = 2;
                for strColor in astrColorRGB:
                    strDevice = getBrainLedName( nIdxBrainLed+nInvertRGB ); nIdxBrainLed += 1;nInvertRGB-=2;
                    aAllDevice.append( strDevice );
            #~ print( "aAllDevice-MouthAlt: name: %s" % aAllDevice );
            self.dcm.createAlias( ["MouthAlt", aAllDevice] );
        
    # createAliases - end
    
    def getEyesAliasName( self, nEyesMask = 0x3 ):
        "nEyesMask: 1: left, 2: right, 3: both"
        if( self.dcm == None ):
            self.reset();
        if( nEyesMask == 0x3 ):
            return self.eyesAliasName;
        if( nEyesMask == 0x1 ):
            return self.eyesAliasNameL;
        if( nEyesMask == 0x2 ):
            return self.eyesAliasNameR;
    # getEyesAliasName - end
    
    def setEyesIntensity( self, rTime, rIntensity = 1. ):
        "set a grey intensity to all face leds"
        nRiseTime = self.dcm.getTime(int(rTime*1000));
        self.dcm.set( [self.eyesAliasName, "Merge",  [[ float( rIntensity ), nRiseTime ]] ] ); # set only grey intensity    
    # setEyesIntensity - end
    
    def setEyesColor( self, rTime = 0.1, nColor = 0xFFFFFF, nEyesMask = 0x3 ):
        """
        set a color to all face leds (non blocking method)
        - nEyesMask: 1: left, 2: right, 3: both
        - rTime: time to set them (in sec)
        """
        if( self.dcm == None ):
            self.reset();        
        rIntensityB = (( nColor  & 0xFF ) >> 0 ) / 255.;
        rIntensityG = (( nColor  & 0xFF00 ) >> 8 ) / 255.;
        rIntensityR = (( nColor  & 0xFF0000 ) >> 16 ) / 255.; 
        riseTime = self.dcm.getTime(int(rTime*1000));
        commands = [];
        nNbrLum = 8;
        if( nEyesMask == 0x3 ):
            nNbrLum *= 2;
        for i in range( nNbrLum ):
            commands.append( [[ rIntensityR, riseTime ]] );
            commands.append( [[ rIntensityG, riseTime ]] );
            commands.append( [[ rIntensityB, riseTime ]] );            
    #    print( " commands: %s" % str( commands ) );
        self.dcm.setAlias( [self.getEyesAliasName(nEyesMask), "Merge",  "time-mixed", commands] );
    # setEyesColor - end

    def setChestColor( self, rTime = 0.1, nColor = 0xFFFFFF ):
        """
        set a color to all face leds (non blocking method)
        - rTime: time to set them (in sec)
        """
        if( self.dcm == None ):
            self.reset();        
        rIntensityB = (( nColor  & 0xFF ) >> 0 ) / 255.;
        rIntensityG = (( nColor  & 0xFF00 ) >> 8 ) / 255.;
        rIntensityR = (( nColor  & 0xFF0000 ) >> 16 ) / 255.; 
        riseTime = self.dcm.getTime(int(rTime*1000));
        commands = [];
        commands.append( [[ rIntensityR, riseTime ]] );
        commands.append( [[ rIntensityG, riseTime ]] );
        commands.append( [[ rIntensityB, riseTime ]] );            
    #    print( " commands: %s" % str( commands ) );
        self.dcm.setAlias( [self.strChestAliasName, "Merge",  "time-mixed", commands] );
    # setChestColor - end
    
    def setMouthColor( self, rTime = 0.1, color = 0xFFFFFF, bUseAltDevice = False ):
        """
        set a color to all face leds (non blocking method)
        - color: an int or an array of 3 ints (one for each led: left top, bottom, and right top) and for each value an hexa 0xRRGGBB
        - rTime: time to set them (in sec)
        """
        if( self.dcm == None ):
            self.reset();        
        riseTime = self.dcm.getTime(int(rTime*1000));
        commands = [];
        if( isinstance( color, int ) ):
            color = [color]*3;
        assert( len(color) == 3 );
        for nColor in color:
            rIntensityB = (( nColor  & 0xFF ) >> 0 ) / 255.;
            rIntensityG = (( nColor  & 0xFF00 ) >> 8 ) / 255.;
            rIntensityR = (( nColor  & 0xFF0000 ) >> 16 ) / 255.; 
            commands.append( [[ rIntensityR, riseTime ]] );
            commands.append( [[ rIntensityG, riseTime ]] );
            commands.append( [[ rIntensityB, riseTime ]] );

        strAliasName = "Mouth";
        if( bUseAltDevice ):
            strAliasName = "MouthAlt";
        self.dcm.setAlias( [strAliasName, "Merge",  "time-mixed", commands] );
    # setMouthColor - end
    
    
    
    def setMouthOneLed( self, nLedIndex = 0, rTime = 0.1, rIntensity = 1., nColorIndex = 0 ):
        """
        set a color to all face leds (non blocking method)
        - nIndex: 0: left top, 1: right top, 2: bottom
        - rTime: time to set them (in sec)
        - nColorIndex: 0: blue, 1: green, 2: red (because on romeo mouth, it's so blinking that we don't want to erase other leds just for nothing)
        """
        if( self.dcm == None ):
            self.reset();        
        riseTime = self.dcm.getTime(int(rTime*1000));
        nIndexBrain = 3+nColorIndex+nLedIndex*3;
        strDeviceName = getBrainLedName( nIndexBrain );
        #~ print( "strDeviceName: %s" % strDeviceName );
        self.dcm.set( [ strDeviceName, "Merge",  [[ rIntensity, riseTime ]] ] );    # setMouthColor - end     
    # setMouthOneLed - end
    
    def setEyesOneLed( self, nIndex, rTime, nColor = 0xFFFFFF, nEyesMask = 0x3 ):
        """
        set a color to one face leds
        - nIndex: 0-7
        - rTime: in sec
        - nEyesMask: 1: left, 2: right, 3: both
        """
        if( self.dcm == None ):
            self.reset();        
        rIntensityB = (( nColor  & 0xFF ) >> 0 ) / 255.;
        rIntensityG = (( nColor  & 0xFF00 ) >> 8 ) / 255.;
        rIntensityR = (( nColor  & 0xFF0000 ) >> 16 ) / 255.; 
        riseTime = self.dcm.getTime(int(rTime*1000));
        commands = [];
        
        strAliasName = "Face";
        if( nEyesMask == 1 ):
            strAliasName += "L";
        elif( nEyesMask == 2 ):
            strAliasName += "R";
        strAliasName += str( nIndex );
        
        nNbrLum = 1;
        if( nEyesMask == 0x3 ):
            nNbrLum *= 2;
        for i in range( nNbrLum ):
            commands.append( [[ rIntensityR, riseTime ]] );
        for i in range( nNbrLum ):
            commands.append( [[ rIntensityG, riseTime ]] );
        for i in range( nNbrLum ):
            commands.append( [[ rIntensityB, riseTime ]] );            
    #    print( " commands: %s" % str( commands ) );
        self.dcm.setAlias( [strAliasName, "Merge",  "time-mixed", commands] );
    # setEyesOneLed - end    
    
    
    def setEyesRandom( self, rTime, rLuminosityMax = 1. ):
        "set random eyes colors"
        riseTime = self.dcm.getTime(int(rTime*1000));
        commands = [];
        for i in range( 2*8*3 ):
            commands.append( [[ random.random()%rLuminosityMax, riseTime ]] );
        self.dcm.setAlias( [self.eyesAliasName, "Merge",  "time-mixed", commands] );
    # setEyesColor - end       
        
    def getEyesState( self, nEyesMask = 0x3 ):
        """
        return current eyes configuration
        nEyesMask: 1: left, 2: right, 3: both
        """
        if( self.dcm == None ):
            self.reset();        
        if( nEyesMask == 0x3 ):
            return self.mem.getListData( self.eyesDevice );
        if( nEyesMask == 0x1 ):
            return self.mem.getListData( self.eyesDeviceL );
        if( nEyesMask == 0x2 ):
            return self.mem.getListData( self.eyesDeviceR );
    # getEyesState - end
    
        
    def setEyesState( self, arVal, rTime = 1., nEyesMask = 0x3 ):
        """
        set previously saved eyes configuration
        nEyesMask: 1: left, 2: right, 3: both
        """        
        if( self.dcm == None ):
            self.reset();        
        riseTime = self.dcm.getTime(int(rTime*1000));
        commands = [];
        
        nNbrLum = 8*3;
        if( nEyesMask == 0x3 ):
            nNbrLum *= 2;        
        
        for i in range( nNbrLum ):
            commands.append( [[ arVal[i], riseTime ]] );
        self.dcm.setAlias( [self.getEyesAliasName(nEyesMask), "Merge",  "time-mixed", commands] ); 
    # setEyesState - end
    
    def mulEyesIntensity( self, rTime, rMul ):
        "change the intensity of each leds, without changing too much the color (although a multiplication by 0. or a small value will erase all colors informations)"
        allVal = self.getEyesState();
        riseTime = self.dcm.getTime(int(rTime*1000));
        commands = [];
        for i in range( len( allVal ) ):
            rNewVal = allVal[i] * rMul;
            rNewVal = max( min( rNewVal, 1. ), 0. );
            commands.append( [[ rNewVal, riseTime ]] );
    #    print( " commands: %s" % str( commands ) );        
        self.dcm.setAlias( [self.eyesAliasName, "Merge",  "time-mixed", commands] );    
    # mulIntensity - end
    
    def rotateEyes( self, rTime, nDec = 1 ):
        # rotate eyes, using current color (even a mixed color on every eyes)
        if( self.dcm == None ):
            self.reset();        
        allVal = self.getEyesState();
        print( "current val: %s" % str( allVal ) );        
        riseTime = self.dcm.getTime(int(rTime*1000));
        commands = [];
        for j in range( 2 ):        
            for i in range( 8 ):    
                commands.append( [[ allVal[j*8*3+((i+nDec)%8)*3+0], riseTime ]] );
                commands.append( [[ allVal[j*8*3+((i+nDec)%8)*3+1], riseTime ]] );
                commands.append( [[ allVal[j*8*3+((i+nDec)%8)*3+2], riseTime ]] );
            nDec *=-1; # invert direction after first eye
        print( "commands: %s" % str( commands ) );
        self.dcm.setAlias( [self.eyesAliasName, "Merge",  "time-mixed", commands] );        
    # rotateEyes - end
    
    def updateEyeCircle( self, nColor1, nColor2 = 0, rSpeed = 1 ):
        """
        this method is intended to be called frequently to update eyes color in a circling movement, 
        without taking any thread and enabling to make an infinity of contiguous circle.
        Just call it about every 250ms (we send 500ms moves in the future)
        
        - rSpeed: time to make one turn in sec
        """
        
        currentTime = self.dcm.getTime(0);
        timeToEndMove = self.tEyeCircle_timeNextSent - currentTime;
        
        #~ print( "DBG: leds.DcmMethod.updateEyeCircle: next: %s, current: %s, timeToEndMove: %s" % (str(self.tEyeCircle_timeNextSent ), str(currentTime), str(timeToEndMove) ) );

        if( timeToEndMove > 350 ):
            return False;
        if( timeToEndMove < -500 ):
            # it's a first call, reset time
            #~ print( "DBG: leds.DcmMethod.updateEyeCircle: First call ? next: %s, current: %s" % (str(self.tEyeCircle_timeNextSent ), str(currentTime)) );
            self.tEyeCircle_timeNextSent = currentTime;

        rIntensityB1 = (( nColor1  & 0xFF ) >> 0 ) / 255.;
        rIntensityG1 = (( nColor1  & 0xFF00 ) >> 8 ) / 255.;
        rIntensityR1 = (( nColor1  & 0xFF0000 ) >> 16 ) / 255.;
        rIntensityB2 = (( nColor2  & 0xFF ) >> 0 ) / 255.;
        rIntensityG2 = (( nColor2  & 0xFF00 ) >> 8 ) / 255.;
        rIntensityR2 = (( nColor2  & 0xFF0000 ) >> 16 ) / 255.;

        # the number of leds to send in the future is depending on the speed
        nMoves = int(math.ceil(8 * 0.5 /  rSpeed)); # 0.5 for 500ms
        rDT = rSpeed * 1000 / 8. ; # DT in ms
        
        #~ print( "DBG: leds.DcmMethod.updateEyeCircle: Sending nMoves: %d, dt: %f " % (nMoves, rDT) );
        
        for i in range( nMoves ):
            nLedOn = ( i + self.nEyeCircle_NextLedPosition ) % 8;
            nLedOff = ( i + self.nEyeCircle_NextLedPosition -1) % 8;
            riseTime = int( self.tEyeCircle_timeNextSent + i*rDT );
            
            #~ print( "nLedOn: %d, nLedOff: %d, riseTime: %d" % (nLedOn, nLedOff,riseTime) );
            
            strAliasName = "FaceL%d" % nLedOn;            
            commands = [];
            commands.append( [[ rIntensityB1, riseTime ]] );
            commands.append( [[ rIntensityG1, riseTime ]] );
            commands.append( [[ rIntensityR1, riseTime ]] );
            self.dcm.setAlias( [strAliasName, "Merge",  "time-mixed", commands] );
            
            strAliasName = "FaceL%d" % nLedOff;
            commands = [];
            commands.append( [[ rIntensityB2, riseTime ]] );
            commands.append( [[ rIntensityG2, riseTime ]] );
            commands.append( [[ rIntensityR2, riseTime ]] );
            self.dcm.setAlias( [strAliasName, "Merge",  "time-mixed", commands] );

            strAliasName = "FaceR%d" % (nLedOn);
            commands = [];
            commands.append( [[ rIntensityB1, riseTime ]] );
            commands.append( [[ rIntensityG1, riseTime ]] );
            commands.append( [[ rIntensityR1, riseTime ]] );
            self.dcm.setAlias( [strAliasName, "Merge",  "time-mixed", commands] );
            
            strAliasName = "FaceR%d" % (nLedOff);
            commands = [];
            commands.append( [[ rIntensityB2, riseTime ]] );
            commands.append( [[ rIntensityG2, riseTime ]] );
            commands.append( [[ rIntensityR2, riseTime ]] );
            self.dcm.setAlias( [strAliasName, "Merge",  "time-mixed", commands] );

            # this should work also:
            #~ strAliasName = "FaceL%d" % nLedOn;            
            #~ commands = [];
            #~ commands.append( [[ rIntensityB2, riseTime ]] );
            #~ commands.append( [[ rIntensityG2, riseTime ]] );
            #~ commands.append( [[ rIntensityR2, riseTime ]] );            
            #~ commands.append( [[ rIntensityB1, riseTime+int(rDT) ]] );
            #~ commands.append( [[ rIntensityG1, riseTime+int(rDT) ]] );
            #~ commands.append( [[ rIntensityR1, riseTime+int(rDT) ]] );
            #~ commands.append( [[ rIntensityB2, riseTime+int(rDT*2) ]] );
            #~ commands.append( [[ rIntensityG2, riseTime+int(rDT*2) ]] );
            #~ commands.append( [[ rIntensityR2, riseTime+int(rDT*2) ]] );
            
            #~ self.dcm.setAlias( [strAliasName, "Merge",  "time-mixed", commands] );
        
        self.nEyeCircle_NextLedPosition = (self.nEyeCircle_NextLedPosition+nMoves)%8;
        self.tEyeCircle_timeNextSent += nMoves*rDT;

        return True;
    # updateEyeCircle - end
    
    def updateBrainCircle( self, rPeriod = 1., rIntensity = 1. ):
        """
        Update the brain rotation, you should call this from time to time, at least a bit faster than every "period time" sec
        for instance, for a rPeriod of 1 sec, 0.9 is enough :)        
        if you call it too slowly the movement will be slower or irregular, but there's no problem to call it too often...
        - rPeriod: period of one full lap
        """
        currentTime = time.time();
        timeBeforeNextSent = self.tBrainCircle_timeNextSent - currentTime;
        
        #~ print( "DBG: leds.DcmMethod.updateBrainCircle: time: %s, tBrainCircle_timeNextSent: %s, timeBeforeNextSent: %s" % (time.time(), str(self.tBrainCircle_timeNextSent), str(timeBeforeNextSent) ) );

        if( timeBeforeNextSent > rPeriod ):
            # wait a bit more
            #~ print( "DBG: leds.DcmMethod.updateBrainCircle: waiting to send for next call..." );
            return False;
        if( timeBeforeNextSent < 0 ):
            # we miss it, damn, let's send it now !
            #~ print( "DBG: leds.DcmMethod.updateBrainCircle: First call ? or missed, resetting to now" );
            self.tBrainCircle_timeNextSent = currentTime;

        rIntensity = float(rIntensity); # le float ici est ultra important car sinon venant de chorégraphe 1.0 => 1 (depuis les sliders de params)
        nFirstRaiseMs = int((self.tBrainCircle_timeNextSent - currentTime)*1000);
        nTimeForEachLedsMs = int( rPeriod * 1000 / self.nNbrBrainSegment );
        
        for nLedIndex in range( self.nNbrBrainSegment ):
            nRiseDecay = nFirstRaiseMs+nTimeForEachLedsMs*nLedIndex;
            #~ print( "DBG: leds.DcmMethod.updateBrainCircle: rise decay allumage led %d: %s" % ( nLedIndex, nRiseDecay ) );
            strDeviceName = getBrainLedName( nLedIndex );
            preDownTime = self.dcm.getTime( nRiseDecay - nTimeForEachLedsMs);
            riseTime = self.dcm.getTime( nRiseDecay );
            downTime = self.dcm.getTime( nRiseDecay + nTimeForEachLedsMs);
            self.dcm.set( [ strDeviceName, "Merge",  [[ 0., preDownTime ]] ] );
            self.dcm.set( [ strDeviceName, "Merge",  [[ rIntensity, riseTime ]] ] );
            self.dcm.set( [ strDeviceName, "Merge",  [[ 0., downTime ]] ] );
        self.tBrainCircle_timeNextSent += rPeriod;
    # updateBrainCircle - end
    
    def setBrainIntensity( self, rTime, rIntensity = 1. ):
        nTime = self.dcmDefault.getTime( int(rTime*1000) );
        for nLedIndex in range( self.nNbrBrainSegment ):
            strDeviceName = getBrainLedName( nLedIndex );        
            self.dcmDefault.set( [ strDeviceName, "Merge",  [[ rIntensity, nTime ]] ] );
    # setBrain - end
    
    def setEarsLoading( self, rProgress, rBlinkingTime = 1., bHadAnimatedChest = True ):
        """
        Update the ears to make them represent the progression of something 
        (the last segment is blinking after each update, so you should call it regularly even if the progress hasn't changed)
        - rProgress: progression to represent[0..1]
        - rBlinkingTime: blinking time in sec
        """
        #~ print( "INF: setEarsLoading: rProgress: %s, rBlinkingTime: %s" % ( rProgress, rBlinkingTime ) );
        nNbrEarSegment = 10;
        nNbrEarToLit = int( rProgress * nNbrEarSegment );

        currentTime = self.dcm.getTime(0);        
        # instant light of current progression:
        if( self.EarsLoading_nLastNbrEarToLit != nNbrEarToLit or time.time() - self.EarsLoading_timeLastCall > 10. ): # every x sec we force a full refresh (because ears could be used by other process)
            self.EarsLoading_nLastNbrEarToLit = nNbrEarToLit;
            self.EarsLoading_timeLastCall = time.time();
            commands = [];
            commands.append( [[ 1., currentTime ]] );
            for i in range( nNbrEarToLit ):
                self.dcm.setAlias( ["Ear%d"%i, "Merge",  "time-mixed", commands*nNbrEarToLit*2] );
            commands[0][0][0]=0.;
            for i in range( nNbrEarToLit+1, nNbrEarSegment ):
                self.dcm.setAlias( ["Ear%d"%i, "Merge",  "time-mixed", commands*(nNbrEarSegment-nNbrEarToLit)*2] );            
                
        # blinking animation (even if we're full, we make the chest blink)
        riseTime = currentTime + int(rBlinkingTime*1000);            
        commands = [];
        commands.append( [[ 0., riseTime ]] );
        nChestColor = 0;
        if( self.EarsLoading_bLastLit ):
            commands[0][0][0]=1.;
            nChestColor = 0xFF;
        if( nNbrEarToLit < nNbrEarSegment - 1 ):
            self.dcm.setAlias( ["Ear%d"%nNbrEarToLit, "Merge",  "time-mixed", commands*2] );
        if( bHadAnimatedChest ):
            self.setChestColor( rBlinkingTime, nChestColor );
        self.EarsLoading_bLastLit = not self.EarsLoading_bLastLit;
    # setEarsLoading - end
    
    
# class DcmMethod - end    
        
    
    def autoTest( self ):
        backup = self.getEyesState();
        
        self.setEyesIntensity( 0., 0. );
        time.sleep( 1. );
        self.setEyesColor( 1., 0x0000FF );
        time.sleep( 1. );
        
        self.setEyesColor( 1., 0xFF0000, 0x1 );
        self.setEyesColor( 1., 0x00FF00, 0x2 );
        time.sleep( 1. );
        # invert eyes
        eyeL = self.getEyesState( 0x1 );
        eyeR = self.getEyesState( 0x2 );
        self.setEyesState( eyeR, 1., 0x1 );
        self.setEyesState( eyeL, 1., 0x2 );
        time.sleep( 1. );
        
        
        self.mulEyesIntensity( 1., 0.1 );
        time.sleep( 1. );
        self.mulEyesIntensity( 1., 10.0 );
        time.sleep( 1. );
        
        self.setEyesRandom( 1., 0.5 );
        time.sleep( 1. );
        
        rTime = 0.1;
        for i in range( 100 ):
            self.rotateEyes( rTime, 1 );
            time.sleep( rTime * 1.1 );
            
        time.sleep( 1. );

        # restore leds state
        self.setEyesState( backup, 2. );
    # autoTest - end
    
# class DcmMethod - end

dcmMethod = DcmMethod();


def changeFavoriteEyesColor( nNewColor ):
    config.nFavoriteEyesColor = nNewColor;
    
def getFavoriteColorEyes( bActive = True ):
    nColor = config.nFavoriteEyesColor;
    nColor = color.ensureBrightOrDark( nColor, bBright = bActive );
    return nColor;
    
def changeFavoriteEyesColorToDefault( ):
    nDefaultColor = 0x000020;
    config.nFavoriteEyesColor = nDefaultColor
    
def setFavoriteColorEyes( bActive = True, rTime = 0.6 ):
    """
    Set the favorite color to the eyes, you could choose them to be active or not (active=bright, not=dark)
    """
    nColor = getFavoriteColorEyes( bActive = bActive );
    dcmMethod.setEyesColor( rTime, nColor = nColor );
    
global_FakeLeds_bAlreadyInstalled = False;
def installFakeALLeds():
    """
    on Romeo, for instance, the speech recognition fail doing silly leds access.
    So we've removed the standard one, and installing a new a-bit-dumb one, on the fly.
    
    To test from a python interactive session:
    
import abcdk.config
abcdk.config.bInChoregraphe=False
import abcdk.leds
abcdk.leds.installFakeALLeds()

or, manually:

# cut and paste the strCode below, then:
import naoqi
pb = naoqi.ALProxy( "ALPythonBridge", "localhost", 9559 );
pb.eval( strCode );
pb.eval( "ALLeds = FakeALLeds( 'ALLeds' )" );
leds = naoqi.ALProxy( "ALLeds", "localhost", 9559 );
leds.off();
asr = naoqi.ALProxy( 'ALSpeechRecognition', 'localhost', 9559)
asr.setVisualExpression( True );
asr.setVisualExpression( False );
asr.setVocabulary( ["papa", "maman"], True );
asr.subscribe( "moi" );

asr.unsubscribe( "moi" );


    """
    global global_FakeLeds_bAlreadyInstalled;
    if( global_FakeLeds_bAlreadyInstalled ):
        return;

    #global_FakeLeds_bAlreadyInstalled = True; # shouldn't we do it somewhere?
        
    print( "INF: abcdk.leds.installFakeALLeds: begin..." );
    
    strCode = """
import naoqi
class FakeALLeds(naoqi.ALModule):
    "Use this object to create a fake leds movement for compatibility usage"

    def __init__( self, strModuleName ):
        try:
            ALModule.__init__(self, strModuleName );
            self.BIND_PYTHON( self.getName(),"fadeRGB" );
        except BaseException, err:
            print( "ERR: abcdk.leds.FakeLeds: loading error: %s" % str(err) );
            
    # __init__ - end
    def __del__( self ):
        print( "INF: abcdk.leds.FakeLeds.__del__: cleaning everything" );
        
    def version( self ):
        print( "INF: abcdk.leds.FakeLeds.version: version called" );
        return "abcdk.fake_leds.has_no_version";
        
    def fade( self, strGroup, rIntensity, rDuration ):
        print( "INF: abcdk.leds.FakeLeds.fade - mock" );
        
    def fadeRGB( self, strGroup, nColor, rDuration ):
        print( "INF: abcdk.leds.FakeLeds.fadeRGB - mock" );
        
    def earLedsSetAngle(self, nDegrees, rDuration, bLeaveOnAtEnd ):
        #print( "INF: abcdk.leds.FakeLeds.earLedsSetAngle - mock" );
        pass
        
    def setIntensity(self, strName, rIntensity ):
        print( "INF: abcdk.leds.FakeLeds.setIntensity - mock" );
        
    def off( self, strName ):
        print( "INF: abcdk.leds.FakeLeds.off - mock" );
        
    def on( self, strName ):
        print( "INF: abcdk.leds.FakeLeds.on - mock" );
        
    def rotateEyes( self, nColor, rTimeForRotation, rTotalDuration ):
        #print( "INF: abcdk.leds.FakeLeds.rotateEyes - mock" );        
        pass
        
# class FakeALLeds - end
    """;
    
    pb = naoqitools.myGetProxy( "ALPythonBridge" );
    pb.eval( strCode );
    pb.eval( "ALLeds = FakeALLeds( 'ALLeds' )" );
    #~ pb.eval( "from abcdk.leds import ALLeds" );
    pb.eval( "asr = ALProxy( 'ALSpeechRecognition', 'localhost', 9559)" );
    pb.eval( "asr.setVisualExpression( True )" ); # recreate the proxy on our new fake leds module
    
    print( "INF: abcdk.leds.installFakeALLeds: end..." );
# installFakeALLeds - end


def autoTest():
    test.activateAutoTestOption();
    dcmMethod = DcmMethod(); # recreate alias with good proxy address
    if( True ):
        print getEarLedName( 2 );
        print getEarLedName( 0, 1 );
        print getEyeLedName( 0, 0, 1 );
        print getEyeLedName( 0, 1, 3 );
        print getEyeColor( 0, 0, 3 );
        print getEyeColor( 0, 1, 3 );    
        print getEyeColor( 0, 0, 0 );
        print getEyeColor( 0, 1, 0 );
        for i in range( 41 ):
            rLevel = i / 40.;
            print( "setEyeVuMeter: %f" % rLevel );
            setEyeVuMeter( rLevel );
            time.sleep( 0.01 );
    if( True ):
        dcmMethod.autoTest();
    if( True ):
        for i in range( 8 ):
            rTime = 1.;
            dcmMethod.rotateEyes( rTime, 1 );
            time.sleep( rTime+0.1 );
        
# autoTest - end

# autoTest();
#~ s = "2012/01/03";
#~ s = s[:3] + chr( ord( s[3] ) + -1 ) + s[4:];
#~ print s

#~ import numpy as np
#~ data = np.array([1,2,3,0,-5,6]);
#~ print abs(data)>3;
#~ print np.argmax( data[1:]>3 );
#~ print abs(np.array([1,2,3,0,-5,6]))

#~ import numpy as np
#~ a = [[1,2,3],[4,5,6]];
#~ print np.mean( a, axis=0 );