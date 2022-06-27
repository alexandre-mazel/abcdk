# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Obstacles tools
# @author The usage team - Living Labs
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Obstacles tools: some method useful to deal with obstacles (mainly when NAO's walking)"""

import mutex
import time

import laser
import naoqitools
#import nav_mark
import numeric
import numpy as np
import logging
import math
import random


global_aObstacleStates = {'none':0, 'leftSide':1, 'left':2, 'center':3, 'right':4, 'rightSide':5 }
global_bSonarEnabled = False;
def enableSonar( bNewValue ):
    global global_bSonarEnabled;
    logging.info("changing from %s to %s" % ( global_bSonarEnabled, bNewValue ) );
    global_bSonarEnabled = bNewValue;

class Manager:
    def __init__( self ):
        self.listBumperEventsName = ["LeftBumperPressed", "RightBumperPressed"];
        self.aLastEvent = []; # a list of pair [time, event value]
        self.mutex = mutex.mutex();
        self.mem = naoqitools.myGetProxy( "ALMemory" );
        self.sonar = naoqitools.myGetProxy( "ALSonar" );
        self.aStrSideName = ["side_left", "left", "center", "right", "side_right"];
        if( self.mem != None ):
            for side in self.aStrSideName:
                self.mem.insertData( "Obstacles/" + side, [time.time()-1000, 0.] );
    # __init__ - end

    def getName( self ):
        return "abcdk.Obstacles";

    def getNameFromIndex( self, nNumEvent ):
        return self.aStrSideName[nNumEvent-1];


    def start( self ):
        self.nNbrHitSonar = 0;
        for event in self.listBumperEventsName:
            naoqitools.subscribe( event, "abcdk.obstacles.manager.onBumper" ); # pb: this is not very portable (todo?)

        global global_bSonarEnabled;
        self.bSonarEnabled = global_bSonarEnabled;
        if( not self.bSonarEnabled ):
            logging.warning( "sonar are DISABLED" );

        if( self.bSonarEnabled ):
            if( self.sonar != None ):
                self.sonar.subscribe( self.getName(), 0.5, 0. );
        self.bStarted = True;
    # start - end

    def stop( self ):
        for event in self.listBumperEventsName:
            try:
                naoqitools.unsubscribe( event, "abcdk.obstacles.manager.onBumper" );
            except BaseException, err:
                logging.warning( "Normal error (bStarted=%s), when unsub bumper, and no sub: err: %s" % (self.bStarted,err) );
        try:
            if( self.bSonarEnabled ):
                if( self.sonar != None ):
                    self.sonar.unsubscribe( self.getName() );
        except BaseException, err:
            logging.warning( "Normal error (bStarted=%s), when unsub sonar, and no sub: err: %s" % (self.bStarted,err) );
        self.bStarted = False;
    # stop - end

    def update( self ):
        """
        return obstacles state:
          0: none
          1: seems to be on the left side (arms)
          2: ... on the left
          3: ... center
          4: ... right
          5: ... right side

        WARNING: obstacles is automatically erased after 2 seconds. (so you need to call update at least every seconds)
        """
        global global_aObstacleStates
        logging.info("Start update")
        while( self.mutex.testandset() == False ):
            logging.info( "locked" );
            time.sleep( 0.05 );

        # update stuffs
        if( self.bSonarEnabled ):
            sonarValues = self.sonar.getFilteredValues();
            rSonarLimit = 0.30; # was 0.34
            logging.debug( "sonarValues: %s" % str(sonarValues) );
            if( sonarValues[0] < rSonarLimit or sonarValues[1] < rSonarLimit ):
                self.nNbrHitSonar += 1;
            else:
                self.nNbrHitSonar = 0;
            if( self.nNbrHitSonar > 2 ):
                logging.info( "Obstacles SONAR triggering" );
                rDiff = sonarValues[0] - sonarValues[1]; # seems to be right, left !!!
                if( abs( rDiff ) < 0.2 ):

                    self.__addEvent(global_aObstacleStates['left']);
                    #nav_mark.navMarkMover.addObstacle( aOffset = [rSonarLimit, 0.1, 0.0] );
                elif( rDiff > 0. ):
                    self.__addEvent(global_aObstacleStates['center']);
                    #nav_mark.navMarkMover.addObstacle( aOffset = [rSonarLimit, 0.0, 0.0] );
                else:
                    self.__addEvent(global_aObstacleStates['right']);
                    #nav_mark.navMarkMover.addObstacle( aOffset = [rSonarLimit, -0.1, 0.0] );

        # eat events
        i = 0;
        logging.info("just before while aLastEvent is %s" % str(self.aLastEvent))
        while( i < len( self.aLastEvent ) ):
            logging.info("in while while")
            if( time.time() - self.aLastEvent[i][0] > 2. ):
                logging.debug("deleting last event %s (timeout)"  % self.aLastEvent[i])
                del self.aLastEvent[i];
            else:
                logging.debug("returning last event %s"  % self.aLastEvent[i])
                ret = self.aLastEvent[i][1];
                self.mutex.unlock();
                return ret;
        self.mutex.unlock();
        return 0;
    # update - end

    def __addEvent( self, nNumEvent ):
        self.mem.raiseMicroEvent( "Obstacles/" + self.getNameFromIndex(nNumEvent), [time.time(), 0.5] );
        self.aLastEvent.append( [ time.time(), nNumEvent ] );
    # __addEvent - end

    def onBumper( self, strVariableName, rVal ):
        logging.info( "Manager.callback: events name: %s, value: %s" % (strVariableName, rVal ) );
        if( rVal < 0.5 ):
            return;
        while( self.mutex.testandset() == False ):
            logging.info( "Manager.callback: locked" );
            time.sleep( 0.05 );
        global global_aObstacleStates
        logging.info("adding event %s" % global_aObstacleStates['center'] )
        self.__addEvent( global_aObstacleStates['center'] );
        self.mutex.unlock();
    # onBumper - end

# class Manager - end

# commenting this code, as it's no more used!
#manager = Manager(); # singleton


class Avoider:
    """
    A small avoider du pauvre using current path way to get centered
    """
    def __init__(self):
        self.timeLastBloqued = time.time()-1000;
        self.aTotalOffset = [0,0,0];
        self.nNbrRetryThisObstacle = 0;
        self.prevPosition = [-150,-150,-150];
        self.motion = naoqitools.myGetProxy( "ALMotion" );

    def getMoveDirection(self):
        """
        Return a [move direction (x,y,t), bNewObstacle, bImpossible]
        """
        rTimeSinceLast = time.time() - self.timeLastBloqued;
        logging.info( "rTimeSinceLast: %s" % str( rTimeSinceLast ) );

        bImpossible = False;
        bNewObstacle = False;

        posApprox = self.motion.getRobotPosition( True );
        rDistSinceLast = numeric.dist3D( posApprox, self.prevPosition );
        logging.info( "rDistSinceLast: %s" % str( rDistSinceLast ) );

        # if( time.time() - self.timeLastBloqued > 20. ):
        if( rDistSinceLast > 0.6 ):
            logging.info( "new obstacle!" );
            bNewObstacle = True;
            self.aTotalOffset = [0,0,0];
            self.nNbrRetryThisObstacle = 0;

            arNewDir = [ -0.05, 0.4, 0. ]; # 2013-10-11: Alma Y was 0.28

            #futurePath = nav_mark.navMarkMover.getPath();
            logging.info( "futurePath: %s" % str( futurePath ) );
            if( futurePath != None and len( futurePath ) > 0 ):
                nextPointAngle = futurePath[0][2];
                logging.info( "nextPointAngle: %s" % str( nextPointAngle ) );
                if( np.array_equal( nextPointAngle, [0.]*6 ) ):
                    nextPointAngle = futurePath[1][2]; # first point ? take second


                if( nextPointAngle[1] < 0. ):
                    arNewDir[1] *= -1.;
                if( nextPointAngle[0] < -0.2 ):
                    arNewDir[0] = -0.15;
            self.arPrevDir = arNewDir;

        for i in range( 3 ):
            self.aTotalOffset[i] += self.arPrevDir[i];

        logging.info( "arPrevDir: %s" % self.arPrevDir );
        logging.info( "aTotalOffset: %s" % self.aTotalOffset );
        if( abs( self.aTotalOffset[1] ) > 1.5 or self.nNbrRetryThisObstacle > 5 ):
            bImpossible = True;
            self.aTotalOffset = [0,0,0];

        self.timeLastBloqued = time.time();
        self.nNbrRetryThisObstacle += 1;
        self.prevPosition = self.motion.getRobotPosition( True );
        return [self.arPrevDir, bNewObstacle, bImpossible];
    # getMoveDirection - end

# class Avoider - end

# commenting this code, as it's no more used!
#avoider = Avoider();

class DepthObstacleDetector:

    """
    This class takes depth image and analyse them to discover obstacles
    use:
        dod = DepthObstacleDetector;
        while( your choice ):
            aObstaclesList = getDepthObstacles();
    """
    
    def __init__( self ):
        self.avd = None; # set to False when no depth camera
        self.strDepthSubscriberName = "";
        self.nObstaclesNbrBand = 16;
        
    def __del__( self ):
        self.stop();
        
    def stop( self ):
        """
        Call me to stop subscription !
        """
        if( self.avd == False ):
            return;
            
        if( self.avd != None ):
            self.avd.unsubscribe(self.strDepthSubscriberName);
            self.avd = None;
        
    def detectObstacles( self, rawDepthMap, w, h ):
        """
        detect obstacles.    
        return an array of minimal distance ostacles in mm on every bands (usually 16 vertical bands)
        - rawDepthMap: a numpy 1D buffer of uint16 (depth in mm)
        """

        image = np.reshape( rawDepthMap, (h,w) );
        # we will find the nearest point of a number of vertical band
        self.nObstaclesNbrBand = 16; 
        nWidthBand = w/self.nObstaclesNbrBand;
        aMinPerBand = [];
        for i in range( self.nObstaclesNbrBand ):
            band = image[0:h,i*nWidthBand:(i+1)*nWidthBand];
            band = band[band != 0]              
            nMin = 1; # default => if we have only zeros, it means we don't see the ground and therefore we know that we're facing an obstacle very near
            if( len(band) > 0 ):
                nMin = np.amin(band)
                # if we have zeros at the bottom of the band, it's a no go also
                lowerband = image[h-20:h,i*nWidthBand:(i+1)*nWidthBand];
                lowerband = lowerband[lowerband != 0]
                if( len(lowerband) < 10 ):
                    nMin = 2; # we could put 1, but that's great to see the different case
            aMinPerBand.append( nMin );
            
        return aMinPerBand;    
    # detectObstacles - end
    
    def getDepthObstacles( self ):
        """
        takes a depth image and compute it
        return [] if no camera or [r1,r2,r3...] a list of ratio of obstacle proximity [0..1]: 1 near obstacles 0: no obstacle from left to right
        """
        if( self.avd == None ):
            self.avd = naoqitools.myGetProxy( "ALVideoDevice" );
            nCameraID = 2; # kDepthCamera
            nResolution = 1;
            nColorSpace = 17; # AL::kDepthColorSpace
            # nColorSpace = 19; # AL::kXYZColorSpace
            nFps = 5;
            bHasDepthCamera = self.avd.hasDepthCamera();
            logging.info( "avd.hasDepthCamera(): %s" % bHasDepthCamera );
            if( not bHasDepthCamera ):
                self.avd = False;
            self.strDepthSubscriberName = "NAO_3D_Viewer";
            self.strDepthSubscriberName = self.avd.subscribeCamera( self.strDepthSubscriberName, nCameraID, nResolution, nColorSpace, nFps );
        if( self.avd == False ):
            return [];
           
        timeBegin = time.time();
        dataImage = self.avd.getImageRemote(self.strDepthSubscriberName); # Image is in 320*240, (sometimes)
        logging.debug( "duration get buffer: %5.2fs" % ((time.time()-timeBegin) ) );
        
        if( dataImage == None ):
            logging.error( "dataImage is none!" );
            return [];
        # obstacles detection
        # minimal distance on my pepper is 69cm to the camera, 54cm to the front of the base
        w = dataImage[0];
        h = dataImage[1];
        image = np.frombuffer( dataImage[6], dtype='uint16' );
        aMinPerBand = self.detectObstacles( image, w, h );

        nDistMin = 800;
        nDistBlind = 400; # but in real mesured it's 690
        nObstaclesNbrBand = len(aMinPerBand)        
        aDistProxi = [];
        for i in range(nObstaclesNbrBand):
            rProxi = 0.;
            if( aMinPerBand[i] < nDistMin ):
                rProxi = (nDistMin-aMinPerBand[i])/float(nDistMin-nDistBlind);
                if( rProxi > 1. ): rProxi = 1.;
            aDistProxi.append(rProxi);
            
        logging.debug( "duration total: %5.2fs" % ((time.time()-timeBegin) ) );
        return aDistProxi;
    # getDepthObstacles - end
    
    def getAngles( self ):
        """
        Return the angles of each band
        """ 
        rXtionAperture = 0.; # aperture in radian on each side TODO: find the value!
        arAngles = [];
        for i in range( self.nObstaclesNbrBand ):
            arAngles.append( rXtionAperture*((self.nObstaclesNbrBand/2)-i) );
        return None # arAngles  # TODO: not tested  !!!
    
# class DepthObstacleDetector - end    

depthObstacleDetector = DepthObstacleDetector(); 

class ObstaclesRetriever:
    """
    A nice object to retrieve obstacles
    """
    
    def __init__( self ):
        self.mem = None;    
        
    def getPepperSonar( self ):
        """
        return a list [front_dist, rear_dist] of pepper sonar.
        """
        if( self.mem == None ):
            self.mem = naoqitools.myGetProxy( "ALMemory" );
        strTemplate = "Device/SubDeviceList/Platform/%s/Sonar/Sensor/Value";
        aSonars = self.mem.getListData( [ strTemplate % "Front", strTemplate % "Back" ] );
        return aSonars;       
    # getPepperSonar - end
    
    def getPepperLaser( self, rDistThreshold ):        
        """
        return a list of tuples (angle,dist) for each angle bearing from the laser returning a distance bellow distThreshold. Tuples remain grouped by their respective side
        """
        aLasers = laser.baseLaserScan.get_all_laser_scan();
        toReturn = []
        for side in aLasers:
            tmp = []
            tmp += [ x for x in side if x[1] < rDistThreshold ]
            toReturn.append(tmp)
        #return aLasers
        return toReturn
    # getPepperLaser - end

    def getPepperBumper( self ):
        """
        return a list [left_bumper, right_bumper, rear_bumper] of pepper bumper values. 0.0 means that the bumper is not pressed. 1.0 means that the bumper is pressed
        """
        if( self.mem == None ):
            self.mem = naoqitools.myGetProxy( "ALMemory" );

        strTemplate = "Device/SubDeviceList/Platform/%s/Bumper/Sensor/Value";
        aBumpers = self.mem.getListData( [ strTemplate % "FrontLeft", strTemplate % "FrontRight" , strTemplate % "Back" ] );
        return aBumpers;       
    # getPepperBumper - end

# class ObstaclesRetriever - end

class ObstaclesMap:
    """
    A 2D map of surrounding obstacles
    
    It's a distance of the nearest obstacles in the 8 direction:    
        1  0  7
        2  x  6
        3  4  5
        
        but in fact, we want it in 10 direction (to be more precise on the front)
        
        2 1 0 9 8
        3    x    7
        4    5    6
        
    two standard uses:
    """
    
    def __init__( self ):
        self.retriever = None;
        self.aLastComputedMap = [9.]*10;
 
        
    def update( self, bUseSonar = True, bUseLaser = True, bUseDepth = True, bVerbose = False ):
        """
        update the map and return it
        """
        
        loggin.debug( "bUseSonar = %s, bUseLaser = %s, bUseDepth: %s" %  ( bUseSonar, bUseLaser, bUseDepth ) )       
        
        aMap = [9.] * 10;
        if( self.retriever == None ):
            self.retriever = ObstaclesRetriever();
          
        if( bUseSonar ):
            timeBegin = time.time()
            aSonars = self.retriever.getPepperSonar();
            logging.debug( "getPepperSonar takes %5.2fs" % (time.time() - timeBegin) )
            aMap[0] = min( aMap[0], aSonars[0] );
            aMap[5] = min( aMap[5], aSonars[1] );

        if( bUseLaser ):
            timeBegin = time.time()
            aLasers = self.retriever.getPepperLaser();
            logging.debug( "getPepperLaser takes %5.2fs" % (time.time() - timeBegin) )
            aLaserPosConverterToMapIdx = [
                1,0,9,
                2,3,4,
                8,7,6        
            ];
            for nNumLaser in range( len(aLasers) ):
                nMapIdx = aLaserPosConverterToMapIdx[nNumLaser];
                aMap[nMapIdx] = min( aMap[nMapIdx], aLasers[nNumLaser] );
            
        if( bUseDepth ):
            aDepthObstacles = depthObstacleDetector.getDepthObstacles();
            logging.debug( "aDepthObstacles: %s" % aDepthObstacles )
            nNbrBand = len(aDepthObstacles);
            nNbrBeamPerMapArea = nNbrBand / 3;
            aDepthAreaPosConverterToMapIdx = [
                1,0,9,
            ];        
            for i in range(3):
                rMax = aDepthObstacles[i*nNbrBeamPerMapArea];
                for j in range(1,nNbrBeamPerMapArea):
                    rMax = max( rMax, aDepthObstacles[i*nNbrBeamPerMapArea+j] );
                if( rMax >= 0. ):
                    logging.debug( "rMax: %s" % rMax )
                    rDistObstacle = (1 - rMax)*1.5; # transform a probability in a distance (nearest the problablest)
                    nMapIdx = aDepthAreaPosConverterToMapIdx[i];
                    aMap[nMapIdx] = min( aMap[nMapIdx], rDistObstacle );
            
        self.aLastComputedMap = aMap;
        return aMap;      
    # update - end
    
    def __str__( self ):
        strOut = "";
        m = self.aLastComputedMap
        strOut += "%6.2f  %6.2f  %6.2f %6.2f %6.2f\n" % ( m[2], m[1], m[0], m[9], m[8] )
        strOut += "%6.2f             x           %6.2f\n" % ( m[3],        m[7] )
        strOut += "%6.2f          %6.2f          %6.2f\n" % ( m[4], m[5], m[6] )
        return strOut;
        
    # __str__ - end
        
# class ObstaclesMap - end        

class Dodger:
    """
    A class to displace a robot at a wanted position, but he has to dodge obstacles!
        example of use:
        rPeriod = 0.05
        dodger = Dodger(bUseDepthCamera = False, bUseSonar = True)
        dodger.setDirection( someDirection );
        while(1):
                aPos = self.dodger.update();
                motion.post.moveTo( aPos[0], aPos[1], 0. );
                time.sleep( rPeriod );

        
    """
    def __init__( self, bUseDepthCamera = True, bUseSonar = True , bUseUnstuck = True):
        self.mem = None;
        self.laserSide = ["Front","Left", "Right"];        
        self.aPrevDir = [0.,0.];
        self.dest = [0.,0.];
        self.rDistLimit = 0.8;  # threshold to dodge obstacles
        self.bUseDepthCamera = bUseDepthCamera;
        self.bUseSonar = bUseSonar;
        self.nFilterThreshold = 0.03

        self.bUseUnstuck = bUseUnstuck
        self.nMaxUnstuckTime = 10
        self.nStuckRecord = 10
        self.bIsStucked = False
        self.aTmpDirection = []
        self.aPrevUpdates = []
        self.nUnstuckTime = 0

        self.retriever = None
        
    def __del__( self ):
        self.stop();
        
    def stop( self ):
        depthObstacleDetector.stop();
        
    def setDirection( self, dest ):
        """
        Change or set a goal to the robot.
        - dest: a list [x,y] in meters of the goal given in the robot frame. You'll have to refresh it frequently: because the robot is moving, the goal could be lost soon...
        """        
        # normalisation:
        dest = numeric.normalise2D( dest );
        
        # ignore the setDirection if we are trying to get unstucked
        if self.nUnstuckTime > 0:
            self.dest = self.aTmpDirection
        else:
            self.dest = dest

        logging.debug("new direction: " + str(self.dest))
        
    def getDirectionFromXY( self, x, y, bEvenSmallDirection =False ):
        """
        return a direction angle relative to a vector not normalised (its norm count)
        """
        
        rBigEnough = 0.2;
        if( bEvenSmallDirection ):
            rBigEnough = 0.06;
        
        polar = []
        rAngle = math.atan2(y,x)
        polar.append(rAngle)
        rNorm = math.sqrt(x ** 2 + y ** 2)
        if rNorm > rBigEnough:
            polar.append(rNorm)
        else:
            polar.append(0)
        return polar
            
        
    # getDirectionFromXY - end
        
    def resetBlockedDirection( self ):
        self.aBlockedDir = [False]*8;
        
    def addBlockedDirection( self, x, y ):
        """
        if the force if high, we block this direction to prevent going into this point
        """
        logging.debug( "add: %5.2f, %5.2f" % (x, y) );
        nDir = self.getDirectionFromXY( x, y );
        if( nDir == -1 ):
            return;
        nDir = (nDir-4)%8; # invert the force
        self.aBlockedDir[nDir] = True;
        logging.debug( "aBlockedDir: %s" % self.aBlockedDir );
        
    def removeBlockedDirection( self, v, bVerbose = False ):
        """
        return the movement direction, without the blocked direction composante
        """
        vn = numeric.normalise2D( v );
        nDir = self.getDirectionFromXY( v[0], v[1] );
        if( nDir != -1 and self.aBlockedDir[nDir] ):
            logging.info( "can't go to dir %s / normalised: %s, dir: %s, full block: %s" % (v, vn, nDir, self.aBlockedDir) );
            return [0.,0.];
        return v;

    def diffAngle(self, a, b):
        diff = a -b
        while diff < -( 2 * math.pi ):
            diff += 4 * math.pi
        while diff > ( 2 * math.pi ):
            diff -= 4 * math.pi
        return diff

    def getStucked(self):
        bStucked = True
        for aPos in self.aPrevUpdates:
            if aPos[0] != 0 or aPos[1] != 0:
                bStucked = False
                break
        return bStucked
        
    def update( self, bVerbose = False ):
        """
        return the resulting direction to walk to [x,y]
        """
        logging.debug( "***** update begin..." );
        bAnything = False;
        #self.resetBlockedDirection();

        if self.nUnstuckTime <= 0 and len(self.aPrevUpdates) == self.nStuckRecord:
            self.bIsStucked = self.getStucked()
            if self.bIsStucked == True:
                self.nUnstuckTime = self.nMaxUnstuckTime + 1
                self.aTmpDirection = []
                for i in range(2):
                    rRand = 0.
                    while rRand < 0.7:
                        rRand = random.random()*2-1
                    self.aTmpDirection.append(rRand)
                logging.debug("Trigger unstuck in direction: " + str(self.aTmpDirection))

        if self.nUnstuckTime > 0:
            self.nUnstuckTime -= 1
            self.dest = self.aTmpDirection

        if self.nUnstuckTime == 0 and self.bIsStucked == True:
            logging.debug("End unstuck")
            self.bIsStucked = False

        if self.retriever is None:
            self.retriever = ObstaclesRetriever()
        
        # We associate each obstacles to a resulting force that will try to push the robot from it
        # we then just additionnate them
        
        # We start by looking at the bumper.
        # If there was something on the bumper, we apply the repulsive force immediatly
        # and ignore the rest.
        aBumper = self.retriever.getPepperBumper()
        logging.debug("aBumper " + str(aBumper))
        if aBumper[0] == 1.0:
            return (True,[0,-0.5])
        if aBumper[1] == 1.0:
            return (True,[0,0.5])
        if aBumper[2] == 1.0:
            return (True,[0.5,0])
        

        aForceLaser = [0,0];        

        aMin = self.retriever.getPepperLaser(self.rDistLimit)
        aForceLaserPerSide = []
        logging.debug("aMin " + str(aMin))
        for side in aMin:
            rSx = 0;
            rSy = 0;
            nNbrTouch = 0;
            for i in range( len(side) ):
                # get an exponential answer to the closeness of the obstacle, i.e. the closest the stronger the Ratio. It is a good idea to take a look at the answer curve with pyplot
                rRatio = (math.exp(2*(((self.rDistLimit-side[i][1])/(self.rDistLimit-0.3))-0.5))/2)-0.184
                if rRatio > 1 : rRatio = 1
                if rRatio < 0 : rRatio = 0
                logging.debug( "laser touch: i: %d, min: %5.2f %5.2f %5.2f" % (i,math.degrees(side[i][0]),side[i][1],rRatio) );
                xr = -math.cos(side[i][0])*rRatio;
                yr = math.sin(side[i][0])*rRatio;
                #self.addBlockedDirection( xr, yr );
                rSx += xr;
                rSy += yr;
                nNbrTouch += 1;     
                bAnything = True;

            aSideForce = [0,0]
            if( nNbrTouch > 0 ):
                aSideForce[0] += rSx/nNbrTouch;
                aSideForce[1] += rSy/nNbrTouch;
                logging.debug( "laser: nNbrTouch: %d, rSx: %5.2f, rSy: %5.2f" % (nNbrTouch,rSx,rSy) );
                aForceLaserPerSide.append(aSideForce)

        if len(aForceLaserPerSide) > 0:
            for side in aForceLaserPerSide:
                aForceLaser[0] += side[0]
                aForceLaser[1] += side[1]
            aForceLaser[0] = aForceLaser[0] / len(aForceLaserPerSide)
            aForceLaser[1] = aForceLaser[1] / len(aForceLaserPerSide)
        
        logging.debug( "aForceLaser : %s" % aForceLaser );

        aForceSonar = [0,0];
        
        if( self.bUseSonar ):
            # add sonar
            logging.debug( "adding sonar..." );
            aSonars = self.retriever.getPepperSonar();
            
            aForceFromSonar = [[-1,0],[1,0]];

            for i in range( len(aSonars) ):
                if( aSonars[i] < self.rDistLimit ):
                    logging.debug( "sonar touch: i: %d, sonar: %5.2f" % (i,aSonars[i]) );
                    rRatio = self.rDistLimit-aSonars[i];
                    xr = aForceFromSonar[i][0]*rRatio;
                    yr = aForceFromSonar[i][1]*rRatio;
                    #self.addBlockedDirection( xr, yr );
                    aForceSonar[0] += xr;
                    aForceSonar[1] += yr;
                    bAnything = True;

        logging.debug( "aForceSonar : %s" % aForceSonar );
        
        aForceCamera = [0,0]
        if( self.bUseDepthCamera ):
            logging.debug( "adding depth..." );
            aDepthObstacles = depthObstacleDetector.getDepthObstacles();
            nNbrBand = len(aDepthObstacles);
            rHalfMax = (nNbrBand-1)/2.;
            rQuarterMax = (nNbrBand)/4.;
            rSx = 0;
            rSy = 0;
            nNbrTouch = 0;
            for i in range(nNbrBand):
                # in fact we always want a bit of movement on the X axis
                rForceBandX = (-(1-(abs(rHalfMax-i)/rHalfMax)/2))/rQuarterMax; # we divide by sth relative to the nbr of band to prevent having a too big impact (we wish to have a force inferior to 1)
                rForceBandY = ((i - rHalfMax)/rHalfMax)/rQuarterMax;
                rRatio = aDepthObstacles[i];
                logging.debug( "depth: touch on %d, rRatio: %5.2f, rForceBandX: %5.2f, rForceBandY: %5.2f" % (i,rRatio,rForceBandX,rForceBandY) );
                if( rRatio > 0.2 ):
                    xr = rForceBandX*rRatio;
                    yr = rForceBandY*rRatio;

                    rSx += xr;
                    rSy += yr;
                    nNbrTouch += 1;
                    bAnything = True;
                    
            if( nNbrTouch > 0 ):
                logging.debug( "depth: nNbrTouch: %d, rSx: %5.2f, rSy: %5.2f" % (nNbrTouch,rSx,rSy) );
                aForceCamera[0] += rSx/nNbrTouch;
                aForceCamera[1] += rSy/nNbrTouch;            
                    
                    
            logging.debug( "aForceCamera : %s" % aForceCamera );
                        

        logging.debug( "prevDir: %s" % self.aPrevDir );

        nLaserFactor = 0.6
        nSonarFactor = 0.2
        nCameraFactor = 0.4

        if aForceSonar[0] == 0 and aForceSonar[1] == 0:
            nLaserFactor += 0.2
            nSonarFactor = 0.0

        if aForceCamera[0] == 0 and aForceCamera[1] == 0:
            nLaserFactor += 0.2
            nCameraFactor = 0.0

        aForceRepulsive = [ nLaser * nLaserFactor + nSonar * nSonarFactor + nCamera * nCameraFactor for nLaser, nSonar, nCamera in zip(aForceLaser,aForceSonar,aForceCamera) ]
        logging.debug( "aForceRepulsive: %s" % aForceRepulsive );
        
        rRepulsiveAngle,rRepulsiveNorm = self.getDirectionFromXY( aForceRepulsive[0], aForceRepulsive[1], bEvenSmallDirection=True );

        
        # add goal
        rAttractiveAngle,rAttractiveNorm = self.getDirectionFromXY( self.dest[0], self.dest[1] );
        logging.debug( "adding direction: %s,%s" % (self.dest[0],self.dest[1]) );

        nDestFactor = 0.15;
        if( rRepulsiveNorm == 0 or (rAttractiveNorm != 0 and abs(self.diffAngle(rAttractiveAngle,rRepulsiveAngle))<1.75 ) ): # the force aren't contradictory
            logging.debug("diff angle: " + str(abs(self.diffAngle(rAttractiveAngle,rRepulsiveAngle))) )  # the force aren't contradictory
            nDestFactor = 0.4
        
        # if the robot is stucked it is very motivated to follow the random direction
        if self.bIsStucked == True:
            nDestFactor = 0.4

        aSumDir = aForceRepulsive
        for i in range(2):        
            aSumDir[i] = aSumDir[i] * (1 - nDestFactor ) +  self.dest[i] * nDestFactor 

        logging.debug( "aSumDir after add dest: %s" % aSumDir );



        #TODO security: can't go directly against a vector directed to me
        #aSumDir = self.removeBlockedDirection( aSumDir, bVerbose = bVerbose );

        logging.debug( "repulsive: %s,%s ; attractive: %s,%s" % (math.degrees(rRepulsiveAngle),rRepulsiveNorm,math.degrees(rAttractiveAngle),rAttractiveNorm) );        

        aRatioNew = 0.8; # we should use another algorithm to avoid oscillation (cycle in odometry or ...)
        aSumDir[0] = aSumDir[0] * aRatioNew + self.aPrevDir[0] * (1.-aRatioNew);
        aSumDir[1] = aSumDir[1] * aRatioNew + self.aPrevDir[1] * (1.-aRatioNew);
        
        self.aPrevDir = aSumDir[:];
        
        logging.debug( "aSumDir after smoothing: %s" % aSumDir );

        # avoid little movements that look bad
        for i in range(2):
            if( abs(aSumDir[i]) < self.nFilterThreshold ):
                aSumDir[i] = 0.;
        logging.debug( "aSumDir after filtering: %s" % aSumDir );

        self.aPrevUpdates.append(aSumDir)
        if len(self.aPrevUpdates) > self.nStuckRecord:
            del self.aPrevUpdates[0]


        return (self.bIsStucked,aSumDir);
    # update - end
# class Gaiter - end

#dodger = Dodger()



def autoTest():
    import test
    test.activateAutoTestOption();
    manager.start();
    time.sleep( 1.5 );
    manager.stop();

# autoTest

if __name__ == "__main__":
    autoTest();
