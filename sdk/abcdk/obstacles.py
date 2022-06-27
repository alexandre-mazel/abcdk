# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Obstacles tools
# @author The usage team - Living Labs
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Obstacles tools: some method useful to deal with obstacles (mainly when NAO's walking)"""

print( "importing abcdk.obstacles" );

import mutex
import time

import laser
import naoqitools
#import nav_mark
import numeric
import numpy as np
import logging

logging.basicConfig(level=logging.DEBUG, format=('%(filename)s:%(lineno)d:''%(levelname)s: ' ' %(funcName)s(): '   '%(message)s') )
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

global_aObstacleStates = {'none':0, 'leftSide':1, 'left':2, 'center':3, 'right':4, 'rightSide':5 }
global_bSonarEnabled = False;
def enableSonar( bNewValue ):
    global global_bSonarEnabled;
    print( "INF: abcdk.obstacles.enableSonar: changing from %s to %s" % ( global_bSonarEnabled, bNewValue ) );
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
            print( "WRN: abcdk.obstacles.Manager.start: sonar are DISABLED" );

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
                print( "WRN: abck.obstacles.Manager.: Normal error (bStarted=%s), when unsub bumper, and no sub: err: %s" % (self.bStarted,err) );
        try:
            if( self.bSonarEnabled ):
                if( self.sonar != None ):
                    self.sonar.unsubscribe( self.getName() );
        except BaseException, err:
            print( "WRN: abck.obstacles.Manager.: Normal error (bStarted=%s), when unsub sonar, and no sub: err: %s" % (self.bStarted,err) );
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
        logger.info("Start update")
        while( self.mutex.testandset() == False ):
            print( "%s: INF: abck.obstacles.Manager.update: locked" % time.time() );
            time.sleep( 0.05 );

        # update stuffs
        if( self.bSonarEnabled ):
            sonarValues = self.sonar.getFilteredValues();
            rSonarLimit = 0.30; # was 0.34
            print( "DBG: abck.obstacles.Manager.update.sonarValues: %s" % str(sonarValues) );
            if( sonarValues[0] < rSonarLimit or sonarValues[1] < rSonarLimit ):
                self.nNbrHitSonar += 1;
            else:
                self.nNbrHitSonar = 0;
            if( self.nNbrHitSonar > 2 ):
                print( "INF: Obstacles SONAR triggering" );
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
        logger.info("just before while aLastEvent is %s" % str(self.aLastEvent))
        while( i < len( self.aLastEvent ) ):
            logger.info("in while while")
            if( time.time() - self.aLastEvent[i][0] > 2. ):
                logger.debug("deleting last event %s (timeout)"  % self.aLastEvent[i])
                del self.aLastEvent[i];
            else:
                logger.debug("returning last event %s"  % self.aLastEvent[i])
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
        print( "%s: INF: abcdk.obstacles.Manager.callback: events name: %s, value: %s" % (time.time(), strVariableName, rVal ) );
        if( rVal < 0.5 ):
            return;
        while( self.mutex.testandset() == False ):
            print( "%s: INF: abcdk.obstacles.Manager.callback: locked" % time.time() );
            time.sleep( 0.05 );
        global global_aObstacleStates
        logger.info("adding event %s" % global_aObstacleStates['center'] )
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
        print( "INF: abck.obstacles.Avoider.getMoveDirection: rTimeSinceLast: %s" % str( rTimeSinceLast ) );

        bImpossible = False;
        bNewObstacle = False;

        posApprox = self.motion.getRobotPosition( True );
        rDistSinceLast = numeric.dist3D( posApprox, self.prevPosition );
        print( "rDistSinceLast: %s" % str( rDistSinceLast ) );

        # if( time.time() - self.timeLastBloqued > 20. ):
        if( rDistSinceLast > 0.6 ):
            print( "INF: abck.obstacles.Avoider.getMoveDirection: new obstacle!" );
            bNewObstacle = True;
            self.aTotalOffset = [0,0,0];
            self.nNbrRetryThisObstacle = 0;

            arNewDir = [ -0.05, 0.4, 0. ]; # 2013-10-11: Alma Y was 0.28

            #futurePath = nav_mark.navMarkMover.getPath();
            print( "INF: abck.obstacles.Avoider.getMoveDirection: futurePath: %s" % str( futurePath ) );
            if( futurePath != None and len( futurePath ) > 0 ):
                nextPointAngle = futurePath[0][2];
                print( "INF: abck.obstacles.Avoider.getMoveDirection: nextPointAngle: %s" % str( nextPointAngle ) );
                if( np.array_equal( nextPointAngle, [0.]*6 ) ):
                    nextPointAngle = futurePath[1][2]; # first point ? take second


                if( nextPointAngle[1] < 0. ):
                    arNewDir[1] *= -1.;
                if( nextPointAngle[0] < -0.2 ):
                    arNewDir[0] = -0.15;
            self.arPrevDir = arNewDir;

        for i in range( 3 ):
            self.aTotalOffset[i] += self.arPrevDir[i];

        print( "INF: abck.obstacles.Avoider.getMoveDirection: arPrevDir: %s" % self.arPrevDir );
        print( "INF: abck.obstacles.Avoider.getMoveDirection: aTotalOffset: %s" % self.aTotalOffset );
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

class DepthObstacleDetecter:

    """
    This class takes depth image and analyse them to discover obstacles
    use:
        dod = DepthObstacleDetecter;
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
        #~ print ("image shape: %s, %s" % (image.shape[0], image.shape[1] ) );
        # we will find the nearest point of a number of vertical band
        self.nObstaclesNbrBand = 16; 
        nWidthBand = w/self.nObstaclesNbrBand;
        aMinPerBand = [];
        for i in range( self.nObstaclesNbrBand ):
            band = image[0:h,i*nWidthBand:(i+1)*nWidthBand];
            band = band[band != 0]              
            #~ for j in range(20):
                #~ print( "%d:%d" % (j,band[0,j]))
            nMin = 1; # default => if we have only zero, we don't see the ground and so we're facing an obstacles very near
            if( len(band) > 0 ):
                nMin = np.amin(band)
            # if we have zero in the low of band, it's a no go also
                if( 1 ):
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
            print( "avd.hasDepthCamera(): %s" % bHasDepthCamera );
            if( not bHasDepthCamera ):
                self.avd = False;
            self.strDepthSubscriberName = "NAO_3D_Viewer";
            self.strDepthSubscriberName = self.avd.subscribeCamera( self.strDepthSubscriberName, nCameraID, nResolution, nColorSpace, nFps );
        if( self.avd == False ):
            return [];
           
        timeBegin = time.time();
        dataImage = self.avd.getImageRemote(self.strDepthSubscriberName); # Image is in 320*240, (sometimes)
        print( "DBG: DepthObstacleDetecter.getDepthObstacles: duration get buffer: %5.2fs" % ((time.time()-timeBegin) ) );
        #~ print( len(dataImage ) );
        #~ for i in range( 11 ):
            #~ print( "%d: %s" % (i, str( dataImage[i] ) ) );
        
        # print( dumpHexa( dataImage ) );        
        
        if( dataImage == None ):
            print( "ERR: dataImage is none!" );
            return [];
        # obstacles detection
        # minimal distance on my pepper is 69cm to the camera, 54cm to the front of the base
        w = dataImage[0];
        h = dataImage[1];
        image = np.frombuffer( dataImage[6], dtype='uint16' );
        aMinPerBand = self.detectObstacles( image, w, h );
        #~ print( "aMinPerBand: %s " % aMinPerBand );
        nDistMin = 800;
        nDistBlind = 400; # but in real mesured it's 690
        nObstaclesNbrBand = len(aMinPerBand)        
        aDistProxi = [];
        for i in range(nObstaclesNbrBand):
            rProxi = 0.;
            if( aMinPerBand[i] < nDistMin ):
                rProxi = (nDistMin-aMinPerBand[i])/float(nDistMin-nDistBlind);
                if( rProxi > 1. ): rProxi = 1.;
                #~ print( "%d: rProxi: %s" % (i, rProxi ) );
            aDistProxi.append(rProxi);
            
        print( "DBG: DepthObstacleDetecter.getDepthObstacles: duration total: %5.2fs" % ((time.time()-timeBegin) ) );
        #~ print( "aDistProxi: %s" % aDistProxi );
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
    
# class DepthObstacleDetecter - end    

depthObstacleDetecter = DepthObstacleDetecter(); 

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
    
    def getPepperLaser( self ):        
        """
        return a list of 9 values: minimal touch of each laser in each direction (front left, front center, front right, side: left front, left middle, left rear, last side: right front, right middle, right rear
        """
        aLasers = laser.baseLaserScan.get_all_laser_scan();
        #~ print( "aLasers: %s" % aLasers );
        # we'll cut each laser in 3 part, and takes the minimal value
        aMin = [];        
        for nSide in range(len(aLasers) ):
            print( "DBG: abcdk.obstacles.Gaiter: adding laser side: %s..." % nSide );            
            nNbrSegmentAnalyse = 3;
            nNbrPointPerSegment = 15 / nNbrSegmentAnalyse; # assume laser range = 15
            for i in range( nNbrSegmentAnalyse ):
                aMin.append( min(aLasers[nSide][(i*nNbrPointPerSegment)*2:((i+1)*nNbrPointPerSegment)*2:2]) );
        # invert L side
        t = aMin[3];
        aMin[3] = aMin[5];
        aMin[5] = t;
        # aMin had now the 3 min value for each side FrontLeft, FrontCenter, FrontRight,    LeftFront, LeftCenter, LeftRear,      RightFront, RightCenter, RightRear
        #~ print aMin;        
        return aMin
    # getPepperLaser - end

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
        
        if bVerbose: print( "DBG: ObstaclesMap.update: bUseSonar = %s, bUseLaser = %s, bUseDepth: %s" %  ( bUseSonar, bUseLaser, bUseDepth ) )       
        
        aMap = [9.] * 10;
        if( self.retriever == None ):
            self.retriever = ObstaclesRetriever();
          
        if( bUseSonar ):
            if bVerbose: timeBegin = time.time()
            aSonars = self.retriever.getPepperSonar();
            if bVerbose: print( "DBG: ObstaclesMap.update: getPepperSonar takes %5.2fs" % (time.time() - timeBegin) )
            aMap[0] = min( aMap[0], aSonars[0] );
            aMap[5] = min( aMap[5], aSonars[1] );

        if( bUseLaser ):
            if bVerbose: timeBegin = time.time()
            aLasers = self.retriever.getPepperLaser();
            if bVerbose: print( "DBG: ObstaclesMap.update: getPepperLaser takes %5.2fs" % (time.time() - timeBegin) )
            aLaserPosConverterToMapIdx = [
                1,0,9,
                2,3,4,
                8,7,6        
            ];
            for nNumLaser in range( len(aLasers) ):
                nMapIdx = aLaserPosConverterToMapIdx[nNumLaser];
                aMap[nMapIdx] = min( aMap[nMapIdx], aLasers[nNumLaser] );
            
        if( bUseDepth ):
            aDepthObstacles = depthObstacleDetecter.getDepthObstacles();
            print( "aDepthObstacles: %s" % aDepthObstacles )
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
                    print( "rMax: %s" % rMax )
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

class Gaiter:
    """
    A class to displace a robot at a wanted position, but he has to dodge obstacles!
        example opf use:
        self.gaiter.setDirection( someDirection );
        while(1):
                aPos = self.gaiter.update();
                motion.post.moveTo( aPos[0], aPos[1], 0. );
                time.sleep( rPeriod );

        
    """
    def __init__( self, bUseDepthCamera = True ):
        self.mem = None;
        self.laserSide = ["Front","Left", "Right"];        
        self.aPrevDir = [0.,0.];
        self.dest = [0.,0.];
        self.rDistLimit = 0.6;  # threshold to dodge obstacles
        self.bUseDepthCamera = bUseDepthCamera;
        self.retriever = None
        
    def __del__( self ):
        self.stop();
        
    def stop( self ):
        depthObstacleDetecter.stop();
        
    def setDirection( self, dest ):
        """
        Change or set a goal to the robot.
        - dest: a list [x,y] in meters of the goal given in the robot frame. You'll have to refresh it frequently: because the robot is moving, the goal could be lost soon...
        """        
        # normalisation:
        dest = numeric.normalise2D( dest );
        
        # mise a l'echelle, couramment, on est a peu prés a 1/12 au max, mais en fait, ca dépend si on divise ou pas par le nombre de segment
        self.dest = dest;
        
    def getDirectionFromXY( self, x, y, bEvenSmallDirection =False ):
        """
        return a direction index [-1, 0..7] relative to a vector not normalised (its norm count)
        0 is full rear, 1 is rear and to the right, 2 is full right, 3 is front and right ...
        -1 if no great direction
        
        1  0  7     x < -0.3     x&y negatif     .....    x neg & y  pos
        2  x  6
        3  4  5     x > 0.3      x pos & y neg     .....    x&y pos
        """
        
        
        rBigEnough = 0.2;
        if( bEvenSmallDirection ):
            rBigEnough = 0.06;
        
            
        if( x < -rBigEnough ):
            if( y < -rBigEnough ):
                return 1;
            if( y > +rBigEnough ):
                return 7;
            return 0;

        if( x > rBigEnough ):
            if( y < -rBigEnough ):
                return 3;
            if( y > +rBigEnough ):
                return 5;                
            return 4;

        if( y < -rBigEnough ):
            return 2;
            
        if( y > +rBigEnough ):
            return 6;
            
        return -1;        
        
    # getDirectionFromXY - end
        
    def resetBlockedDirection( self ):
        self.aBlockedDir = [False]*8;
        
    def addBlockedDirection( self, x, y ):
        """
        if the force if high, we block this direction to prevent going into this point
        """
        print( "DBG: Gaiter.addBlockedDirection: add: %5.2f, %5.2f" % (x, y) );
        nDir = self.getDirectionFromXY( x, y );
        if( nDir == -1 ):
            return;
        nDir = (nDir-4)%8; # invert the force
        self.aBlockedDir[nDir] = True;
        print( "DBG: Gaiter.addBlockedDirection: aBlockedDir: %s" % self.aBlockedDir );
        
    def removeBlockedDirection( self, v, bVerbose = False ):
        """
        return the movement direction, without the blocked direction composante
        """
        vn = numeric.normalise2D( v );
        nDir = self.getDirectionFromXY( v[0], v[1] );
        if( nDir != -1 and self.aBlockedDir[nDir] ):
            print( "INF: Gaiter.removeBlockedDirection: can't go to dir %s / normalised: %s, dir: %s, full block: %s" % (v, vn, nDir, self.aBlockedDir) );
            return [0.,0.];
        return v;
        
    def update( self, bVerbose = False ):
        """
        return the resulting direction to walk to [x,y]
        """
        if bVerbose: print( "DBG: abcdk.obstacles.Gaiter: ***** update begin..." );
        bAnything = False;
        self.resetBlockedDirection();


        if self.retriever is None:
            self.retriever = ObstaclesRetriever()

        
        # we associate each obstacles to a resulting force that will try to push the robot from it
        # we them just additionnate them
        
        aSumDir = [0,0];        
        
        # for each segment, the direction it push us [x,y]
        aForceFromSegment = [
                                            [-1,-1], [-1, 0], [-1,+1],
                                            [-1,-1], [ 0,-1], [+1,-1],
                                            [-1,+1], [0,+1], [+1,+1],
                                        ];        
        rSx = 0;
        rSy = 0;
        nNbrTouch = 0;

        aMin = self.retriever.getPepperLaser()
        for i in range( len(aMin) ):
            if( aMin[i] < self.rDistLimit ):
                if bVerbose: print( "DBG: abcdk.obstacles.Gaiter: laser touch: i: %d, min: %5.2f" % (i,aMin[i]) );
                rRatio = self.rDistLimit-aMin[i];
                xr = aForceFromSegment[i][0]*rRatio;
                yr = aForceFromSegment[i][1]*rRatio;
                self.addBlockedDirection( xr, yr );
                rSx += xr;
                rSy += yr;
                nNbrTouch += 1;     
                bAnything = True;

        if( nNbrTouch > 0 ):
            if bVerbose: print( "DBG: abcdk.obstacles.Gaiter: laser: nNbrTouch: %d, rSx: %5.2f, rSy: %5.2f" % (nNbrTouch,rSx,rSy) );
            aSumDir[0] += rSx/nNbrTouch;
            aSumDir[1] += rSy/nNbrTouch;
        
        #~ aSumDir[0] /= len(aMin);
        #~ aSumDir[1] /= len(aMin);
        
        if bVerbose: print( "DBG: abcdk.obstacles.Gaiter: aSumDir after laser: %s" % aSumDir );
        
        if( 1 ):
            # add sonar
            if bVerbose: print( "DBG: abcdk.obstacles.Gaiter:  adding sonar..." );
            aSonars = self.retriever.getPepperSonar();
            #~ print( "aSonars: %s" % aSonars );
            
            aForceFromSonar = [
                                                [-1,0],[1,0]
                                            ];

            for i in range( len(aSonars) ):
                if( aSonars[i] < self.rDistLimit ):
                    if bVerbose: print( "DBG: abcdk.obstacles.Gaiter: sonar touch: i: %d, sonar: %5.2f" % (i,aSonars[i]) );
                    rRatio = self.rDistLimit-aSonars[i];
                    xr = aForceFromSonar[i][0]*rRatio;
                    yr = aForceFromSonar[i][1]*rRatio;
                    self.addBlockedDirection( xr, yr );
                    aSumDir[0] += xr;
                    aSumDir[1] += yr;
                    bAnything = True;
                    

            #~ aSumDir[0] /= len(aSonars);
            #~ aSumDir[1] /= len(aSonars);

        print( "DBG: abcdk.obstacles.Gaiter: aSumDir after sonar: %s" % aSumDir );
        
        if( self.bUseDepthCamera ):
            if bVerbose: print( "DBG: abcdk.obstacles.Gaiter: adding depth..." );
            bOnlyDepth = 0;
            if( bOnlyDepth ):
                aSumDir[0] = 0.;
                aSumDir[1] = 0.;
            aDepthObstacles = depthObstacleDetecter.getDepthObstacles();
            nNbrBand = len(aDepthObstacles);
            rHalfMax = (nNbrBand-1)/2.;
            rQuarterMax = (nNbrBand)/4.;
            rSx = 0;
            rSy = 0;
            nNbrTouch = 0;
            for i in range(nNbrBand):
                #rForceBandX = -(rHalfMax-abs(i - rHalfMax))/rHalfMax;
                # in fact we always want a bit of X
                rForceBandX = (-(1-(abs(rHalfMax-i)/rHalfMax)/2))/rQuarterMax; # we divide by sth relative to the nbr of band to prevent having a too big impact (we wish to have a force inferior to 1)
                rForceBandY = ((i - rHalfMax)/rHalfMax)/rQuarterMax;
                rRatio = aDepthObstacles[i];
                #~ print( "rForceBandX: %s, rForceBandY: %s, rRatio:%s" % ( rForceBandX,rForceBandY,rRatio) );
                if( rRatio > 0.2 ):
                    if bVerbose: print( "DBG: abcdk.obstacles.Gaiter: depth touch: i: %d, rRatio: %5.2f" % (i,rRatio) );
                    xr = rForceBandX*rRatio;
                    yr = rForceBandY*rRatio;
                    self.addBlockedDirection( xr, yr );
                    rSx += xr;
                    rSy += yr;
                    nNbrTouch += 1;
                    bAnything = True;
                    
            if( nNbrTouch > 0 ):
                if bVerbose: print( "DBG: abcdk.obstacles.Gaiter: depth: nNbrTouch: %d, rSx: %5.2f, rSy: %5.2f" % (nNbrTouch,rSx,rSy) );
                aSumDir[0] += rSx/nNbrTouch;
                aSumDir[1] += rSy/nNbrTouch;            
                    
                    
            if bVerbose: print( "DBG: abcdk.obstacles.Gaiter: aSumDir after depth: %s" % aSumDir );
                        

        if bVerbose: print( "DBG: abcdk.obstacles.Gaiter: prevDir: %s" % self.aPrevDir );
        
        nDirForce = self.getDirectionFromXY( aSumDir[0], aSumDir[1], bEvenSmallDirection=True );
        
        aRatioNew = 0.3;
        aRatioNew = 1.; # we will use another algorithm to avoid oscillation (cycle in odometry or ...)
        #~ aRatioNew = 0.5;
        aSumDir[0] = aSumDir[0] * aRatioNew + self.aPrevDir[0] * (1.-aRatioNew);
        aSumDir[1] = aSumDir[1] * aRatioNew + self.aPrevDir[1] * (1.-aRatioNew);
        
        self.aPrevDir = aSumDir[:];
        
        if bVerbose: print( "DBG: abcdk.obstacles.Gaiter: aSumDir after avg: %s" % aSumDir );
        
        
        
        # add goal
        nDirGoal = self.getDirectionFromXY( self.dest[0], self.dest[1] );
        #aRatioDest = 0.3; # set too much, and your robot will enter obstacles !!!
        aRatioDest = 0.1;
        for i in range(2):        
            aSumDir[i] = self.dest[i] * aRatioDest + aSumDir[i] * (1.-aRatioDest);

        if bVerbose: print( "DBG: abcdk.obstacles.Gaiter: aSumDir after add dest: %s" % aSumDir );

        # walk straight / don't walk just a bit
        for i in range(2):
            if( abs(aSumDir[i]) < 0.02 ):
                aSumDir[i] = 0.;


        # security: can't go directly against a vector directed to me
        aSumDir = self.removeBlockedDirection( aSumDir, bVerbose = bVerbose );

        if bVerbose: print( "DBG: abcdk.obstacles.Gaiter: nDirGoal: %s, nDirForce: %s" % (nDirGoal, nDirForce) );        
        # move faster!
        #~ if( not any(self.aBlockedDir) ):
        if( nDirForce == -1 or (nDirGoal != -1 and abs(nDirGoal-nDirForce)<3 ) ): # the force aren't totally contradictory
            if( ( abs(self.dest[0]) > 0.01 or abs(self.dest[1]) > 0.01 ) ):         # previously tested by the nDirGoal != -1 
                # if no direction blocked and have a goal: move faster!!!
                if bVerbose: print( "DBG: abcdk.obstacles.Gaiter: no blockage => sprint" + " !" * 10 );
                rMultiplicator = 3;
                if( not bAnything ):
                    # if nothing, move very faster!
                    if bVerbose: print( "DBG: abcdk.obstacles.Gaiter: no blockage => MEGA sprint" + " !" * 100 );
                    rMultiplicator = 20;
                aSumDir[0] *= rMultiplicator;
                aSumDir[1] *= rMultiplicator;        
        
            if bVerbose: print( "DBG: abcdk.obstacles.Gaiter: aSumDir after mul: %s" % aSumDir );        
        return aSumDir;
    # update - end

        
    
    
# class Gaiter - end

gaiter = Gaiter();





def autoTest():
    import test
    test.activateAutoTestOption();
    manager.start();
    time.sleep( 1.5 );
    manager.stop();

# autoTest

if __name__ == "__main__":
    autoTest();
