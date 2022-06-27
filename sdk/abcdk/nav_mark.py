# -*- coding: utf-8 -*-
""" Navigation based on landmarks (e.g. datamatrix)

"""

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Navigation tools
# Aldebaran Robotics (c) 2014 All Rights Reserved - This file is confidential.
###########################################################


print( "importing abcdk.nav_mark" )
import config
config.bInChoregraphe = False

import collections
import copy
import json
import logging
import math
import numpy as np
import os
import time

# Our own imports
import datamatrix_topology
import extractortools
import image
import imagePnp
import motiontools
import naoqitools
import numeric
import obstacles
import pathtools
import serialization_tools
import sound
import stringtools
import topology  # etonnant.. ne devrait t'on pas juste dependre de datamatrix_topology ? .. juste pour gedHeadMove ? TODO:
import qi

#-----------------------------------------------------------------------------
# Globals and constants
#-----------------------------------------------------------------------------
logger = logging.getLogger(__name__)
#logger.setLevel(logging.ERROR)  # we ignore message below ERROR
#logger.setLevel(logging.WARN)  # we ignore message below ERROR

#-----------------------------------------------------------------------------
# Local utilities
#-----------------------------------------------------------------------------

def handle_image_error(data):
    """
    For now .. there are some error in getIMageLocalnaoqi (ioctl..)
    """
    logger.error("data is %s looping until one image has been processed", data)
    sound.playSound( "bip_error.wav" )

def _enlargeRect(nX, nY, nWidth, nHeight, nResolution, offset=20):
    """
    enlarge rect by offset on x, y, nResolution is used to stick in the range of image resolution

    >>> _enlargeRect(3, 20, 200, 120, 3)
    (0, 15, 205, 125)
    """
    xMax, yMax = image.getResolutionFromEnum(nResolution)
    xMin, yMin = [0, 0]
    x = max(xMin, nX - offset)
    y = max(yMin, nY - offset)
    nWidth = min(xMax, nWidth+2*offset)
    nHeight = min(yMax, nHeight+2*offset)
    return x, y, nWidth, nHeight

#-----------------------------------------------------------------------------
# Functions and class
#-----------------------------------------------------------------------------

def _lookAtMark(dataDecoded=None, mark=None, bUseMotion=False):
    """ move the head to approximatively look at a mark in a dataDecoded structure"""
    #print("datadecoded")
    #print dataDecoded
    #print("mark")
    #print mark
    headPos = [dataDecoded.imageInfo.cameraPosInFrameTorso[5] + mark.aCenterAngle[0], dataDecoded.imageInfo.cameraPosInFrameTorso[4] + mark.aCenterAngle[1]]
    nMaxSpeed = 0.30
    if bUseMotion:
        motion = naoqitools.myGetProxy( "ALMotion")
        motion.angleInterpolation("Head", headPos, nMaxSpeed, True)
        time.sleep(0.8)
    else:
        motiontools.mover.moveJointsWithSpeed( "Head", headPos, nMaxSpeed )  # TODO :  gerer le clipping

def _getNewMarks(seenMarks, marksToLookFor=None, marksToIgnore=None):
    """ Tool function that's compute the list of marks based on markSeens, marks to ignore, and marks to look for """
    if (marksToLookFor is None) and (marksToIgnore is None):
        return seenMarks
    else:
        nMarksSeen = [mark.strName for mark in seenMarks]
        if marksToLookFor is None:
            newMarks = (set(nMarksSeen)) - set(marksToIgnore)
        elif marksToIgnore is None:
            newMarks = set(nMarksSeen) & set(marksToLookFor)
        else:
            newMarks = (set(nMarksSeen) - set(marksToIgnore)) & set(marksToLookFor)
        #print("FILTERING, marksToLookFor %s, marksToIgnore %s seen Mark %s, res = %s" % (str(marksToLookFor), str(marksToIgnore), str(nMarksSeen), str(newMarks)))
        return newMarks


class MarkDiscover(object):
    """
    Pan head / destiffness/to discover datamatrix mark (no datamatrix process is done here, just movements)
    """
    def __init__(self, bUseSound=True, bDebug=False):
        self.motion = naoqitools.myGetProxy("ALMotion")
        self.yawJointMove = motiontools.JointMove("HeadYaw")
        self.pitchJointMove = motiontools.JointMove("HeadPitch")
        self.nHeadYawLimit = math.pi / 2  # limit to be not strange
        self.nPitchAngle = -0.05
        self.nPanSpeed = 0.005
        self.nMaxSpeed = 0.3
        self.nPanSlices = 5
        #self.nPanSlices = 1  # pour tester
        self.bDebug = bDebug
        self.headNoMoveTimeOut = 5  # 5 sec
        self.state = 'S0'  # current State
        self.motionTaskId = -1
        self.bWasStopped = False
        self.bFirstUpdate = True
        self.marksToLookFor = None
        self.marksToIgnore = None
        self.bMustStop = False
        self.state = 'S0'  # current State
        self.bFirstS3 = True
        self.nStartDate = 0
        self._reset()
        self.bUseSound = bUseSound

    # __init__ - end26

    def update(self):
        """
        return (bIsFinished, bUseFullImage)
        """
        if self.bUseSound:
            import speech
            import translate
        bUseFullImage = False
        if (self.state == 'S0'):
            self._lookLeft()
            self.nextState = 'S1'

        if (self.state == 'S1'):
            if self._panHead():
                self.nextState = 'S2'

        if (self.state == 'S2'):
            ## TODO : avoir dans motion tools un moveJointsWithSpeed avec un mouv non relatif
            motiontools.mover.moveJointsWithSpeed("Head", [0, -0.3], self.nMaxSpeed)
            self.nextState = 'S3'

        if self.state == 'S3':
            headUserMove = motiontools.HeadUserMove(8)
            headUserMove.start()
            #nHeadMoved = headUserMove.update()  # update to let the user to move the head manually wheras nao is talking
            if self.bUseSound:
                speech.sayAndLight(translate.chooseFromDict(
                    {"en": "You can show me a mark manually.", "fr": "Tu peux me montrer une marque manuellement."}))
            while (not (self.bMustStop)):
                nHeadMoved = headUserMove.update()
                if nHeadMoved == 2:
                    if self.bUseSound:
                        speech.sayAndLight(translate.chooseFromDict(
                            {"en": "Ok, I look this.", "fr": "Ok je vais regarder cette marque."}))
                    bUseFullImage = True
                    self.nextState = 'S3'
                    break
                if nHeadMoved == 3:
                    self.nextState = 'end_goto'
                    bUseFullImage = False
                    break
            self.motion.setStiffnesses("HeadYaw", 1)
            self.motion.setStiffnesses("HeadPitch", 1)
        if (self.state == 'end_goto'):
            if self.bUseSound:
                speech.sayAndLight(
                    translate.chooseFromDict({"en": "End of learning movements.", "fr": "Fin des mouvements."}))
            return True, False

        self.state = self.nextState
        return (False, bUseFullImage)

    # update - end

    def stop(self):
        """
        stop all movements
        """
        self.bMustStop = True
        if ( self.motionTaskId == -1 ):
            return False
        time.sleep(0.5)  # be sure update() got it
        self.bWasStopped = True
        try:
            self.motion.stop(self.motionTaskId)
        except BaseException, err:
            print(
                "DBG: abcdk.motiontools.HeadSeeker.stop: if this error complain about a non existing task, it's ok: %s" % str(
                    err) )
        self.motionTaskId = -1
        return True

        # stop - end

    def _reset(self):
        """
        reset class value to default
        """
        self.motionTaskId = -1
        self.bWasStopped = False
        self.bFirstUpdate = True
        self.marksToLookFor = None
        self.marksToIgnore = None
        self.bMustStop = False
        self.state = 'S0'  # current State
        self.bFirstS3 = True
        self.nStartDate = 0

    # _reset - end

    def _lookLeft(self):
        """
        move head to left and, return True when finished
        """
        motiontools.mover.moveJointsWithSpeed("Head", [self.nHeadYawLimit, self.nPitchAngle], self.nMaxSpeed)
        return True

    # _lookLeft - end

    def _panHead(self):
        """
        It pans head using slices. Returns True when a full pan has been done
        """
        bLast = False
        if self.motion is not None:
            nCurrentYaw = motiontools.mover.getAngles("HeadYaw", True)[0]
        else:
            nCurrentYaw = math.pi
        sliceAngle = self.nHeadYawLimit / self.nPanSlices
        if abs(nCurrentYaw - sliceAngle) > self.nHeadYawLimit:
            sliceAngle = abs(-self.nHeadYawLimit - nCurrentYaw)
            bLast = True

        if self.motion is not None:
            if self.bDebug:
                print("abcdk.nav_mark.DiscoverMark.panHead: using yaw of %f" % sliceAngle)

            motiontools.mover.moveJointsWithSpeed("Head", [nCurrentYaw - sliceAngle, self.nPitchAngle], self.nMaxSpeed)
        return bLast
        # panHead - end


class MarkDetector(object):
    """
    MarkDetector class with tool functions like procces with a goodTimestamp

    if bDebug is on, each acquired image is saved in pathtools.getVolatilePath/markDetector, whith name = timestamp.jpg
    the extracted information of image is saved in pathtools.getVolativePath/markDetector as timestamp_datamatrixInfo.pickle
    """
    def __init__(self, markDetectorProxy = None, bDebug=False):
        #NDEV : avoir un debug pour activer le save des images de debug datamtrix
        # avoir  un autre debug pour activer le save des pickle et des images brutes
        if markDetectorProxy is None:
            self.proxy = naoqitools.myGetProxy("ALDataMatrixDetection")
        else:
            self.proxy = markDetectorProxy

        self.kbDebug = bDebug
        self.setDefaultSetting()
        self.bMustStop = False

    def stop(self):
        if not(self.bMustStop):
            self.bMustStop = True

    def _start(self):
        self.bMustStop = False

    def setDefaultSetting(self):
        """ default setting for datamatrixDetection """
        self.knShrink = 80
        self.knWidthHeightRatio = 0.6
        self.knSymbolShape = 0
        self.knEdgeThreshold = 1
        self.knPropSquareDevn = 0
        self.knDatamatrixToDetect = 2
        self.knResolution = 3
        self.kbUseOpenCvFilter = True
        self.knScoreMethod = 8
        self.knGeometricScoreMethod = 3
        self.knTimeOut = 1200
        self.knBestPointX = 640
        self.knBestPointY = 480
        self.proxy.setShrink(self.knShrink)
        self.proxy.setDebugMode(self.kbDebug)  # NDEV: virer le debug !
        self.proxy.setWidthHeightRatio(self.knWidthHeightRatio)
        self.proxy.setSymbolShape(self.knSymbolShape)
        self.proxy.setEdgeThreshold(self.knEdgeThreshold)
        self.proxy.setPropSquareDevn(self.knPropSquareDevn)
        self.proxy.setNumDataMatricesToDetect(self.knDatamatrixToDetect)
        self.proxy.setResolution(self.knResolution)
        self.proxy.setUsePreprocessing(self.kbUseOpenCvFilter)
        self.proxy.setScoreMethod(self.knScoreMethod)
        self.proxy.setGeometricScoreMethod(self.knGeometricScoreMethod)
        self.proxy.setDetectionTimeOut(self.knTimeOut)
        self.proxy.setBestPoint(self.knBestPointX, self.knBestPointY)
        self.kstrDebugPath = os.path.join(pathtools.getVolatilePath(), "markDetector") + '/'
        if self.kbDebug:
            if not os.path.exists(self.kstrDebugPath):
                os.mkdir(self.kstrDebugPath)
        self.proxy.setDebugPath(self.kstrDebugPath)

    def setLearningSetting(self):
        """ Set setting for learning of place. (Update the setting that are different from the default one for the learning). """
        self.knTimeOut = 3000
        self.proxy.setDetectionTimeOut(self.knTimeOut)

    def setLocalisationSetting(self):
        self.knTimeOut = 3000
        self.proxy.setDetectionTimeOut(self.knTimeOut)

    def setNavigationSetting(self):
        """ Set setting for navigation. (Update the setting that are different from the default one for the navigation). """
        self.knTimeOut = 1200
        self.proxy.setDetectionTimeOut(self.knTimeOut)
    # default settings :

    def addLogMarkerRobotHasMoved(self):
        """
        add a file in the kstrDebugPath with name timestamp.moved
        """
        if self.kbDebug:
            strFilename = str(int(time.time() * 1000000)) + '.moved'

            strPath = os.path.join(self.kstrDebugPath, strFilename)
            with open(strPath, 'a'):
                os.utime(strPath, None)
        else:
            return

    def _saveDataDecoded(self, dataDecoded):
        """
        create a .pickle file with dataMatrixInfo object
        """
        #print("Saving dataDecoded")
        if self.kbDebug:
            nTimeStampMicroSec = int(1000000 * dataDecoded.imageInfo.nTimeStamp)
            strDataDecodePickleFile = os.path.join(self.kstrDebugPath, (str(nTimeStampMicroSec) + '.pickle'))
            serialization_tools.saveObjectToFile(dataDecoded, strDataDecodePickleFile)
            print("saving dataDecoded into %s" % strDataDecodePickleFile)

    def processOneShotRectangleWithTime(self, rectX, rectY, rectWidth, rectHeight):
        """
        Do a processoneShot but using a picture not more recent that the current time.
        returns dataDecoded
        """
        self._start()
        timestamp = time.time()  # Warning using time.time in remote will cause problem if desktop and robot are not synchronised
        ## solution pour synch rapidement: date +%Y%m%d%T -s "`ssh nao@10.2.1.75 'date "+%Y%m%d %T"'`"
        nSec = int(timestamp)
        nMicroSec = int(1000000 * (timestamp - nSec))
        #data = None
        while not(self.bMustStop):
            data = self.proxy.processRectangleOneShot(False, [rectX, rectY, rectWidth, rectHeight], [nSec, nMicroSec])
            logger.info("datamatrix return value is %s", data)
            if data != None:
                break
            handle_image_error(data)
        dataDecoded = extractortools.datamatrix_decodeInfo(data)
        self._saveDataDecoded(dataDecoded)
        return dataDecoded

    def processRectangleOneShot(self, bReleaseCam, rectX, rectY, rectWidth, rectHeight, nSec = 0, nMicroSec=0):
        """ procces a specific rectangle using nSec and nMicroSec for timestamp """
        self._start()
        while not(self.bMustStop):
            data = self.proxy.processRectangleOneShot(bReleaseCam, [rectX, rectY, rectWidth, rectHeight], [nSec, nMicroSec])
            logger.info("datamatrix return value is %s", data)
            if data != None:
                break
            handle_image_error(data)

        dataDecoded = extractortools.datamatrix_decodeInfo(data)
        self._saveDataDecoded(dataDecoded)
        return dataDecoded

    def processOneShotWithTime(self):
        """
        Do a processoneShot but using a picture not more recent that the current time.
        returns dataDecoded
        """
        self._start()
        timestamp = time.time()
        nSec = int(timestamp)
        nMicroSec = int(1000000 * (timestamp - nSec))
        #data = None
        while not(self.bMustStop):
            data = self.proxy.processOneShot(False, [nSec, nMicroSec])
            if self.bMustStop:
                raise NavMarkError("Stop")
            logger.info("datamatrix return value is %s", data)
            if data !=  None:
                break
            handle_image_error(data)
        dataDecoded = extractortools.datamatrix_decodeInfo(data)
        self._saveDataDecoded(dataDecoded)
        return dataDecoded

    def processFullImage(self, timeOut=6000):
        """ long process of the full image.. """
        #import speech
        #import translate
        #### TODO .. .TODO : resolution en dure ????????
        #rectX, rectY, rectWidth, rectHeight = (0, 0, 1280, 960)  # TODO ne pas mettre en dure  la resolution
        lastShrink = self.knShrink # big value to ensure no shrink
        lastTimeOut = self.knTimeOut
        lastNumDatamatrixToDetect = self.knDatamatrixToDetect
        self.proxy.setShrink(10000) # big value to ensure no shrink
        self.proxy.setDetectionTimeOut(timeOut)
        self.proxy.setNumDataMatricesToDetect(1)
        ## settings are done in processOe
        #dataDecoded = self.processOneShotRectangleWithTime(rectX, rectY, rectWidth, rectHeight)
        dataDecoded = self.processOneShotWithTime()
        # reseting the old setting
        self.proxy.setShrink(lastShrink)
        self.proxy.setDetectionTimeOut(lastTimeOut)
        self.proxy.setNumDataMatricesToDetect(lastNumDatamatrixToDetect)
        #self.proxy.setDetectionTimeOut(self.knTimeOut)
        return dataDecoded

    def processImageFile(self, strImagePath, strPickle ):
        """
        strPickle: is a pickle file (see extractorTools), that allow to get camera image position etc.. (for saving)
        """
        self._start()
        if self.kbDebug:
            print("Processing image %s" % strImagePath)
        data = self.proxy.processImage(strImagePath)
        dataDecoded = extractortools.datamatrix_decodeInfo(data)

        # we use default value :
        #dataDecoded.imageInfo.nTimeStamp =   #data[0][0] + data[0][1]/1000000.0 # meme format que time.time()
        usepickle = True
        if usepickle:
            dataFromPickle = serialization_tools.loadObjectFromFile(strPickle)
            dataDecoded.imageInfo = copy.deepcopy(dataFromPickle.imageInfo)

        elif dataDecoded.imageInfo.cameraPosInNaoSpace == []:
            dataDecoded.imageInfo.cameraPosInNaoSpace = [0.07543542236089706, 0.00804947130382061, 0.4227728247642517, 0.0023152604699134827, -0.056213777512311935, 0.10107704997062683]
#cameraPosInWorldSpace: [0.0884934663772583, 0.005659856833517551, 0.4227728247642517, 0.0023152611684054136, -0.05621378496289253, 0.07442028820514679]
#cameraPosFrameTorso: [0.049693889915943146, 0.004892378114163876, 0.19723539054393768, 0.0, -0.10948837548494339, 0.09813404828310013]
        self._saveDataDecoded(dataDecoded)
        return dataDecoded


class NavigationDebugInfo(object):
    """
    Class use to store debug information in a structure (for debug only)
    """
    def __init__(self):
        self.rDurationPnPCalculation = 0
        self.rDurationWalk = 0
        self.rDurationDataMatrixRectangle = 0
        self.rDurationDataMatrixRectangleNothingFound = 0
        self.rDurationDataMatrixOneShot = 0
        self.rDurationDatamatrixNoMatrixFound = 0
        self.rDurationProcessingMap = 0
        self.rDurationHeadMoveSeeker = 0
        self.rDurationHeadMove = 0
        self.rDurationDataMatrixOneShotIfFail = 0
        self.rDurationLearnAMark = 0
        self.nFailToAverageRectangle = 0
        self.rTotalDuration = 0
        self.rDistanceDone = 0
        self.nLocalize = 0

    def reset(self):
        """ reset all class variables to 0 """
        for key in self.__dict__.keys():
            self.__dict__[key] = 0


class NavMarkError(Exception):
    """Base class for errors in the NavMark package."""
    def __init__(self, strMessage, nErrorCode=1):
        """

        :param strMessage: error message
        :param nErrorCode: code error
        ( 1: unknown error, 10: entity can't be overwritten)

        :return:
        """
        self.strMessage = strMessage
        self.nErrorCode = nErrorCode

    def __str__(self):
        return "NavMarkError %s: %s" % (self.nErrorCode, self.strMessage)


class NavMark(object):
    """ generic class for navigation (learn+move)

    """
    def __init__(self, bDebug=False, bUseSound=False):
        #: :type: datamatrix_topology.DataMatrixTopologicalMap
        self.tMap = datamatrix_topology.DataMatrixTopologicalMap()
        #: :type: datamatrix_topology.DataMatrixTopologicalMap
        self.lastLearnedMap = None
        self.mem = naoqitools.myGetProxy("ALMemory")
        self.motion = naoqitools.myGetProxy( "ALMotion")
        self.bMustStop = False
        self.markDetector = None
        self.bDebug = bDebug
        self.nCurLocalVse = None  # position of the robot   # TODO : rename in aCurRobotPos
        self.aLastMotionWorldPos6D = None
        self.aLastMotionWorldPos6DDuringLastSuccessfullLocalizion = None
        try:
            self.markDiscover = MarkDiscover()
        except NameError:
            ## pas de ALProxy par exemple
            pass
        except AttributeError:
            pass
        except RuntimeError:
            pass

        self.debugInfo = NavigationDebugInfo()
        self.debugInfo.reset()
        self._reset()
        self.nDebugMarkAnalysis = 0
        self.usuableMarks =  ['2', '4', '5', '6', '9', '7']
        self.bUseSound = bUseSound
        self.strLogMovementsFilename = pathtools.getBehaviorRoot() + 'logMovements.json'
        self.bKidnappedLastTime = False #

        self.strMapOrigin = 'origin'
        self.aPOIs = dict()  # point of interests relative to the origin of the current map {'name':a6Dcoordinates, ...}

    def _createPOI(self, strName, a6DCoordinates):
        #print("Creating poi %s at coordinate %s" % (strName, a6DCoordinates))
        self.aPOIs[strName] = a6DCoordinates
        #print(self.aPOIs)

    def _readPOIs(self):
        """
        :return: list of known poi
        """
        #print(self.aPOIs)
        return self.aPOIs.keys()

    def _getPOICoordinates(self, strKey):
        return self.aPOIs[strKey]

    def _deletePOIs(self, strName):
        """
        delete a poi by name
        :return:
        """
        self.aPOIs.pop(strName)


    def stop(self, timeOut=10):
        """ stop movements"""
        if self.bUseSound:
            import speech
        if (True):  # test the mutex
            print('the mutex is ok')
            self.bMustStop = True
            if self.markDiscover is not None:
                self.markDiscover.stop()
            if self.bUseSound:
                speech.stopSay()
            motionProxy = naoqitools.myGetProxy( "ALMotion")
            if motionProxy is not None:
                motiontools.mover.stopCurrentMovements("Head")
                motionProxy.stopMove()  # it also stop backwardStep
        return True


    def addObject(self, strName, bOverwrite=True):
        """ Add the current robot pose to the map.

        Warning this method do a localize call.

        :type strName: str
        :param strName: unique name of the object
        :type bOverwrite: boolean
        :param bOverwrite: enable overwritting if name already presents
        :rtype: boolean
        :return: True if success, False otherwise
        """
        #: :type: datamatrix_topology.DataMatrixTopologicalMap
        self.lastLearnedMap = copy.deepcopy(self.tMap)

        strVssKey = None
        for k, v in self.lastLearnedMap.aVss.iteritems():
            if v.strLabel == strName:
                if not(bOverwrite):
                    raise NavMarkError('ERR: abcdk.navMarkErr.addObject: Impossible to add the pose, bOverwrite is (%s) and a Vs named(%s) is already present' % (str(bOverwrite), strName))
                strVssKey = k
                break
        if self.bDebug:
            print("INF: abcdk.navMark.learn : strNameVs = %s, strVssKey = %s" % (strName, str(strVssKey)) )
        if strVssKey is None:  ## we add a new local map in this case
            if self.bDebug:
                print("INF: abcdk.nav_mark.addObject : adding a new local map named %s" % strVssKey)
            self.lastLearnedMap.forgetViewerPos()  # creation of a local map
            strVssKey = self.lastLearnedMap.nCurLocalVs

        self.lastLearnedMap.aVss[strVssKey].strLabel = strName

        learnedMarks = self.__fastLocalize(nNumAverage=3, bCenterMark=False)

        if not learnedMarks:
            return False
            #raise NavMarkError("Impossible to localize")

        for learnedMark in learnedMarks:
            for infos in learnedMark:
                imagePnp.matrixName = "{0:d}".format(int(infos[3].nTimeStamp * 1000000)) + infos[3].nCameraName + "_debugPnp" # pour debug
                self.lastLearnedMap.updateAmer( infos[2].strName, infos[2].aCornersRefinedPixels, infos[3] , bDebug = self.bDebug)
        self.lastLearnedMap.updateGlobalMapUsingLocalVectorSpace(strVssKey)  # we add the VS to the map..
        bConnectedToOtherVs = self.lastLearnedMap.aWayPoints.has_key(self.lastLearnedMap.nCurLocalVs)

        # on ajoute ca pour avoir la completion après un deepcopy
        #: :type: datamatrix_topology.DataMatrixTopologicalMap
        self.tMap = copy.deepcopy(self.lastLearnedMap)  # deepCopy necessaire ?
        if not(bConnectedToOtherVs):
            if self.bDebug:
                print("WARN: abcdk.navMark.addObject : new VS is not connected to the rest of the map")
        return bConnectedToOtherVs


    def loadMap(self, filename = None):
        """
        Load the map into the current NavMark (`NavMarkMover` or `NavMarkLearner`) object.

        :param filename: filename of the map to load (.pickle file).
        :type filename: str
        :rtype: boolean
        :return: True on success
        """
        # NDEV: renvoyer un bSuccess à loadmap.. regarder le with dans serialization_tools
        print("Loading %s ..." % (str(filename))),

        try:
            tMap = serialization_tools.loadObjectFromFile(filename)
            self.tMap = tMap
            bSuccess = True
        except IOError, err:
            bSuccess = False
            print(err)

        return bSuccess

    #def loadMap(self, pNavMarkInstance):
    #    """
    #    Load map from a NavMarkInstance.

    #    We just do a deepCopy
    #    """
    #    self.tMap = copy.deepcopy(pNavMarkInstance.tMap)

#NDEV : revoir cette mtehode
    #def deleteAMark(self):
    #    """
    #    Delete the first mark visible to nao form all VSS
    #    """
    #    import speech
    #    import translate


    #    if self.markDetector == None:
    #        self.markDetector = MarkDetector()
    #    self.markDetector.setLearningSetting()
    #    self.lastLearnedMap = copy.deepcopy(self.tMap)
    #    if self.lastLearnedMap == None:
    #        raise NavMarkError('ERR: abcdk.navMarkErr.learn(): abcdk.nav_mark.learn: Impossible to get a topological map')

    #    dataDecoded = self.markDetector.processOneShotWithTime()
    #    marksInMap = self.lastLearnedMap.globalVs.keys()  #labels
    #    if dataDecoded.marks == []:
    #        speech.sayAndLight(translate.chooseFromDict({"en":"No Mark have been seen.", "fr":"Je n'ai pas vu de marques."}))
    #        return False

    #    for mark in dataDecoded.marks:
    #        if mark.strName in marksInMap:
    #            speech.sayAndLight(translate.chooseFromDict({"en":"Deleting %s.", "fr":"J'efface %s."}) % mark.strName)
    #            self.lastLearnedMap.deleteMarkVss(mark.strName)
    #            break
    #    else:
    #        speech.sayAndLight(translate.chooseFromDict({"en":"This mark is not in the map.", "fr":"Cette marque n'est pas dans la carte."}))
    #        return False



    #    speech.sayAndLight(translate.chooseFromDict({"en":"Ok updating global.", "fr":"Je met a jour la carte globale."}))
    #    self.lastLearnedMap.updateGlobalMap()
    #    if self.bMustStop:
    #        return
    #    speech.sayAndLight(translate.chooseFromDict({"en":"Ok updating topology.", "fr":"Je met a jour la topology."}))
    #    self.lastLearnedMap.updateTopology()

    #    speech.sayAndLight(translate.chooseFromDict({"en":"Done.", "fr":"Ok."}))

    #    self.tMap = copy.deepcopy(self.lastLearnedMap)

    #    return True


    def learnAMark(self, mark, dataDecoded, numAverage=4, nMaxCapture=4):
        """
        Use the info on a viewed mark to detect it again numerous time.

        :param mark:
        :param dataDecoded:
        :param numAverage: number of image to stop (it counts the init image)
        :param nMaxCapture: number of picture per datamatrix (it counts the init image allready taken)
        :return: a list of marks ( [[mark.aCornersRefinedPixels, dataDecoded.imageInfo.cameraPosInFrameTorso[5], mark, dataDecoded.imageInfo]] )  ## WARNING.. there is some reduntant information here the first init image is included in the list
        """
        avd = naoqitools.myGetProxy("ALVideoDevice")
        camNum = {'CameraTop':0, 'CameraBottom':1}[dataDecoded.imageInfo.nCameraName]
        markSeen = []
        markSeen.append([mark.aCornersRefinedPixels, dataDecoded.imageInfo.cameraPosInFrameTorso[5], mark, dataDecoded.imageInfo])

        st = [ camNum, [mark.aPosXY[0], mark.aPosXY[1], mark.aSizeWH[0], mark.aSizeWH[1]], dataDecoded.imageInfo.nResolution, 0, 0 ]
        #print("CALL  %s " % str(st))
        rect = avd.getImageInfoFromAngularInfoWithResolution(camNum, [mark.aPosXY[0], mark.aPosXY[1], mark.aSizeWH[0], mark.aSizeWH[1]], dataDecoded.imageInfo.nResolution)
        rectX, rectY, rectWidth, rectHeight = _enlargeRect(rect[0], rect[1], rect[2], rect[3] , dataDecoded.imageInfo.nResolution)

        i = 0
        for _ in range(nMaxCapture-1):
            if self.bMustStop:
                break
            dataDecoded_ = self.markDetector.processRectangleOneShot(False, rectX, rectY, rectWidth, rectHeight, 0, 0)


            if self.bUseSound:
                for mark in dataDecoded_.marks:
                    try:
                        nNumMark = int( mark.strName[1:], 16 )
                        if self.bUseSound:
                            sound.playSound( sound.getNoteSound( nNumMark ), bWait=False, nSoundVolume=30 - i*(25/numAverage))
                    except BaseException, err:
                        print( "WRN: abcdk.navMarkErr.learnAMark: can't play sound for %s, err: %s" % ( mark.strName, err ) )

            for mark_ in dataDecoded_.marks:
                if mark_.strName == mark.strName:
                    markSeen.append([mark_.aCornersRefinedPixels,
                                     dataDecoded_.imageInfo.cameraPosInFrameTorso[5],
                                     mark_, dataDecoded_.imageInfo])

            if len(markSeen) >= numAverage:
                break
            i += 1

        if self.bDebug:
            print("J'ai moyenne sur " + str(i) + " marques, pour apprendre " + mark.strName)
            #serialization_tools.saveObjectToFile(markSeen, '/home/nao/debug/markSeen_run' + str(self.nDebugMarkAnalysis) + "_markSeen.pickle")
        self.nDebugMarkAnalysis += 1

        return markSeen

# deprecated
    #def getPathToVs(self, strNameVS):
    #    """
    #    return the way points to go to a specific localMap (i.e.
    #    observation point) using the last current location.
    #
    #    :param strNameVS: targetVs strName
    #    :return: [tuple(nextVsId, nextVsName, nextVsVectorDirectorInFrameTorso), ..., tuple(nextVsId, nextVsName, finalVsVectorDirectorInFrameTorso)]
    #    """
    #    tMap = self.tMap
    #    if tMap is None:
    #        print("ERR: abcdk.nav_mark.getPathToVs: Impossible to get a topological map from parameter")
    #        return
    #
    #    vsPath = tMap.getNextWayPoints(strNameVS)
    #    names = [tMap.aVss[vsId].strLabel for vsId in vsPath]
    #    #tMap.aWayPoints[vsId]
    #    pose6Ds = [tMap.aWayPoints[vsId] for vsId in vsPath]
    #
    #    ## TODO : peut etre un bug dans ocnvertPoseWorldToTorso..
    #    # Pour l'instant on fait comme si le robot etait paralele au sol (bien droit)
    #    poseTorso = []
    #    for pose in pose6Ds:
    #        robotPose = tMap.aRobotCurPos6d.copy()
    #        robotPose[3] = 0
    #        robotPose[4] = 0
    #        poseTorso.append(numeric.convertPoseWorldToTorso(pose, robotPose))
    #
    #    res = zip(vsPath, names, poseTorso)
    #    return res

    def getVs(self):
        """
        provides the list of all named local map (e.g kitchen, office, etc..) that are reachable in the map

        :return: list of string
        """
        tMap = self.tMap
        if tMap is None:
            print("ERR: abcdk.nav_mark.getVs: Impossible to get a topological map")
            return

        ret = []
        for key, vs in tMap.aVss.iteritems():
            label = tMap.aVss[key].strLabel
            if label is not None:
                ret.append(label)
        return ret

    def saveMap(self, filename=None):
        if filename is None:
            raise NavMarkError("ERR: abcdk.nav_mark.saveMap: filename == None.")
        serialization_tools.saveObjectToFile(self.tMap, filename)

    def saveMapToMemory(self):
        serialization_tools.exportObjectToAlMemory(self.tMap, 'topoMap')

    def addPreviousLearnedToMap(self):

        if (self.lastLearnedMap is not None):
            #: :type: datamatrix_topology.DataMatrixTopologicalMap
            self.tMap = copy.deepcopy(self.lastLearnedMap)

            return True

        return False


    def addTempPose(self, strName=None, bOverwrite=True):
        """

        :param strName: name of the pose (e.g. Kitchen)
        :param bOverwrite: replace existing one if present (e.g Kitchen already in the Map)
        :return: True if success
        """
        if self.markDetector is None:
            self.markDetector = MarkDetector()
        self.markDetector.setLearningSetting()

        res = self.addObject(strName, bOverwrite=bOverwrite)
        return res

    def _reset(self):
        """ reset to default """
        self.nDebugMarkAnalysis = 0
        #self.bMustStop = False
        self.aCurDest = None
        self.debugInfo.reset()
        try:
            self.markDiscover._reset()
        except AttributeError:
            pass

    #def _localLocalize(self, tMap = None):
    #    """
    #    use the current VS to determine where are the mark, and try to localize based on that !
    #    return average robot pose thanks to all mark viewable in the current aVss
    #    """
    #    if tMap is None:
    #        tMap = self.tMap
    #
    #    #motion = naoqitools.myGetProxy( "ALMotion")
    #    #:type currentVs: topology.VectorSpace
    #    currentVs = tMap.aVss[tMap.nCurLocalVs]
    #    #learnedMark = []
    #    pos = []
    #
    #
    #    for key, markPose in currentVs.aAmersPose6D.iteritems():
    #        if self.bMustStop:
    #            return None
    #        pos_ = []
    #        #motion.angleInterpolation("Head", [0,0], 0.8, True)
    #        #### theoriticalPose = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]) <<< ---- what the fuck !!!!!
    #        theoriticalPose = self.move.theoriticalPose
    #        print("LOOOKING at %s, with pose %s (my pose = %s)" % (key, str(markPose), str(theoriticalPose)))
    #        time.sleep(0.01)
    #        headMove = topology.getHeadMove(theoriticalPose, markPose)
    #        bUseMotion = False
    #        if bUseMotion:
    #            motion = naoqitools.myGetProxy( "ALMotion")
    #            motion.angleInterpolation("Head", headMove, 0.8, True)
    #            time.sleep(0.2)
    #        else:
    #            motiontools.mover.moveJointsWithSpeed( "Head", headMove, 0.4 )
    #            time.sleep(0.1)  # pour la stabilisation.. (ne devrait pas etre necessaire)
    #        dataDecoded = self.markDetector.processOneShotWithTime()
    #        if dataDecoded.marks == []:  # on fait un nouvel essaie
    #            dataDecoded = self.markDetector.processOneShotWithTime()
    #
    #        for mark in dataDecoded.marks:
    #            print("Mark detected %s" % mark.strName)
    #            if not(mark.strName[0] in self.usuableMarks):  # NDEV usualble mark n'est pas dispo dans navMark mais dans navMarkMover seulement
    #                print("INF: abcdk.nav_mark.learn() : mark %s non geree" % (mark.strName))
    #                continue
    #            if mark.strName != key:
    #                continue
    #            if self.bUseSound:
    #                sound.playSound(sound.getNoteSound(int( mark.strName[1:],16 )), bWait=False, nSoundVolume=60)
    #
    #            learnedMark = self.learnAMark(mark, dataDecoded, numAverage = 5, nMaxCapture=5)
    #
    #
    #            for infos in learnedMark:
    #                imagePnp.matrixName = "{0:d}".format(int(infos[3].nTimeStamp * 1000000)) + infos[3].nCameraName + "_debugPnp" # pour debug
    #                pose = tMap.computeRobotPose(infos[2].strName, infos[2].aCornersRefinedPixels, infos[3], bDebug= False, bLocalVs=True)
    #                if pose is not None:
    #                    pos_.append(pose)  # <-- ici a timer..
    #        if pos_ != []:
    #            pos.append(np.mean(pos_, axis=0))
    #    return pos


    def __fastLocalizeRewritten(self, nNumAverage=3, bCenterMark=False, nMaxMovements=12):
        """
        fastLocalize processing methods that do the movement and acquisitions of datamatrix.

        :param nNumAverage: number of capture to use for each mark to analyze.
        :param bCenterMark: enable centering of mark when seen.
        :param nMaxMovements: max seeker movements
        :return:a list of learned marks [[[mark.aCornersRefinedPixels, dataDecoded.imageInfo.cameraPosInFrameTorso[5], mark, dataDecoded.imageInfo]]]
        """
        def processZoneInCenterOfCamera(dataDecoded, mark):
            avd = naoqitools.myGetProxy("ALVideoDevice")
            camNum = {'CameraTop':0, 'CameraBottom':1}[dataDecoded.imageInfo.nCameraName]
            x, y, width, height = avd.getImageInfoFromAngularInfoWithResolution(camNum, [0 , 0, mark.aSizeWH[0], mark.aSizeWH[1]], dataDecoded.imageInfo.nResolution)
            rect = [x-width/2, y-height/2, width, height]  # (x,y) center of image in pixels
            rectX, rectY, rectWidth, rectHeight = _enlargeRect(rect[0], rect[1], rect[2], rect[3] , dataDecoded.imageInfo.nResolution)
            dataDecoded_ = self.markDetector.processOneShotRectangleWithTime(rectX, rectY, rectWidth, rectHeight) # process small part of image (where the mark should be )
            return dataDecoded_


        headSeeker = motiontools.HeadSeeker()
        headSeeker.reset()
        aLearnedMarks = []
        nNbrUpdate = 0
        bFound = False
        while(not self.bMustStop and not bFound):
            dataDecoded = self.markDetector.processOneShotWithTime()
            aMarkUsable = [mark for mark in dataDecoded.marks if mark.strName in self.tMap.aGlobalVs]  # markUsable = mark seen and in Map
            for mark in aMarkUsable:
                sound.playSound(sound.getNoteSound(int( mark.strName[1:],16 )), bWait=False, nSoundVolume=60)
                if bCenterMark:
                    _lookAtMark(dataDecoded, mark)
                    dataDecoded = processZoneInCenterOfCamera(dataDecoded, mark)
                    if dataDecoded.marks == []:
                        dataDecoded = self.markDetector.processOneShotWithTime()  # process full image in this case

                for mark_ in dataDecoded.marks:
                    if not(mark_.strName == mark.strName):
                        if self.bDebug:
                            print("INF: abcdk.nav_mark.learn() : mark_ %s is not the map previously seen %s" % (mark_.strName, mark.strName))
                        continue
                    aLearnedMarks  =  self.learnAMark(mark_, dataDecoded, numAverage = nNumAverage, nMaxCapture=8)  # *ICI* le bug est sans doute dans ce call TODO / pourquoi 8 ?
                    if aLearnedMarks != []:
                        bFound = True

            if bFound or headSeeker.update() or nNbrUpdate > nMaxMovements:
                break  # fin du seeker #end while
            nNbrUpdate +=1
        headSeeker.stop()
        headSeeker.reset()
        return [aLearnedMarks]



    def __fastLocalize(self, nNumAverage=3, bCenterMark=False, nMaxMovements=12):
        """
        fastLocalize processing methods that do the movement and acquisitions of datamatrix.

        :param nNumAverage: number of capture to use for each mark to analyze.
        :param bCenterMark: enable centering of mark when seen.
        :param nMaxMovements: max seeker movements
        :return:a list of learned marks [[[mark.aCornersRefinedPixels, dataDecoded.imageInfo.cameraPosInFrameTorso[5], mark, dataDecoded.imageInfo]]]
        """
        avd = naoqitools.myGetProxy("ALVideoDevice")
        bFound = False
        learnedMarks = []
        headSeeker = motiontools.HeadSeeker()
        headSeeker.reset()
        nNbrUpdate = 0
        while (not(self.bMustStop)):
            dataDecoded = self.markDetector.processOneShotWithTime()
            for mark in dataDecoded.marks:
                if not(mark.strName in self.tMap.aGlobalVs.keys()):
                    if self.bDebug:
                        print("INF: abcdk.nav_mark.learn() : mark %s not in map" % (mark.strName))
                    continue
                if self.bUseSound:
                    sound.playSound(sound.getNoteSound(int( mark.strName[1:],16 )), bWait=False, nSoundVolume=60)
                if bCenterMark:
                    _lookAtMark(dataDecoded, mark)
                    camNum = {'CameraTop':0, 'CameraBottom':1}[dataDecoded.imageInfo.nCameraName]
                    x, y, width, height = avd.getImageInfoFromAngularInfoWithResolution(camNum, [0 , 0, mark.aSizeWH[0], mark.aSizeWH[1]], dataDecoded.imageInfo.nResolution)
                    rect = [x-width/2, y-height/2, width, height]  # (x,y) center of image in pixels
                    rectX, rectY, rectWidth, rectHeight = _enlargeRect(rect[0], rect[1], rect[2], rect[3] , dataDecoded.imageInfo.nResolution)
                    dataDecoded_ = self.markDetector.processOneShotRectangleWithTime(rectX, rectY, rectWidth, rectHeight) # process small part of image (where the mark should be )
                    if dataDecoded_.marks == []:
                        sound.playSound( "bip_error.wav", bWait=False, nSoundVolume=85)
                        dataDecoded_ = self.markDetector.processOneShotWithTime()  # process full image
                    dataDecoded = dataDecoded_
                for mark_ in dataDecoded.marks:
                    if not(mark_.strName == mark.strName):
                        if self.bDebug:
                            print("INF: abcdk.nav_mark.learn() : mark_ %s is not the map previously seen %s" % (mark_.strName, mark.strName))
                        continue
                    learnedMark  =  self.learnAMark(mark_, dataDecoded, numAverage = nNumAverage, nMaxCapture=8)  # *ICI* le bug est sans doute dans ce call TODO / pourquoi 8 ?
                    if learnedMark != []:
                        bFound = True
                        learnedMarks.append(learnedMark)
            if bFound:
                break

            startTime = time.time()
            if self.bMustStop:
                if self.bDebug:
                    print ("abcdk.nav_mark.__fastLocalize: bMustStop has been set quitting")
                break

            if headSeeker.update() or nNbrUpdate > nMaxMovements:
                break  # fin du seeker
            nNbrUpdate +=1
        headSeeker.stop()
        headSeeker.reset()
        return learnedMarks

    def _fastLocalize(self, nNumAverage=5, bCenterMark=False):
        """
        Use seeker, when mark is found, nNum pictures are processed to update the robot position.
        """
        pos = []
        #learnedMarks = self.__fastLocalize(nNumAverage=nNumAverage, bCenterMark=bCenterMark, nMaxMovements=99)
        learnedMarks = self.__fastLocalizeRewritten(nNumAverage=nNumAverage, bCenterMark=bCenterMark, nMaxMovements=99)

        if self.bMustStop:
            return None

        startTime = time.time()
        if self.bMustStop:
            return None
        for learnedMark in learnedMarks:
            for infos in learnedMark:
                #imagePnp.matrixName = "{0:d}".format(int(infos[3].nTimeStamp * 1000000)) + infos[3].nCameraName + "_debugPnp" # pour debug
                if not(infos[2].strName in self.tMap.aGlobalVs.keys()):
                    continue
                pose = self.tMap.computeRobotPose(infos[2].strName, infos[2].aCornersRefinedPixels, infos[3], bDebug=False)
                if pose is not None:
                    pos.append(pose)
        self.debugInfo.rDurationPnPCalculation += time.time() - startTime
        if pos == []:
            return None
        self.tMap.aRobotCurPos6d = np.median(np.array(pos), 0)
        #print("resOf localisation %s" % str(pos))
        #print("on averagemedian.. %s" % str(self.tMap.aRobotCurPos6d))
        self.nCurLocalVse = self.tMap.aRobotCurPos6d

## WE update the robotPose6D in almemory.. NDEV: embeded this in a function?
        self.mem.raiseMicroEvent("NavBar2D/CurrentPosition", self.tMap.aRobotCurPos6d.tolist())
        # saving distance done in a file #
        #self.tMap.last  NDEV ici
        return self.tMap.aRobotCurPos6d

    #def _strongLocalize(self, nNumAverage=5):
    #    """
    #    Pan the head to find all marks, for each marks found pose of robot is estimated using nNumAverage picture,
    #    the average position of median pos for each mark is used to compute the final robot position
    #    """
    #    listPoses = []
    #    marksLearned = []
    #    marksInMap = self.tMap.aGlobalVs.keys()  #labels
    #    while (not(self.bMustStop)):
    #        print("call to discoverMarks.. with marksToIgnore == %s" % (str(marksLearned)))
    #        #novelMarks, rawExtractorData = self.discoverMarks(marksToLookFor = marksInMap, marksToIgnore = marksLearned)
    #        novelMarks, rawExtractorData =  (set([]), None)
    #        break # TODO

    #        if novelMarks == set([]):
    #            break ## fin
    #        if (self.bMustStop):
    #            break  # on quitte vite pas au prochain tour de boucle
    #        data = extractortools.datamatrix_decodeInfo( rawExtractorData );
    #        for mark in data.marks:
    #            pose = self._localize(data, mark.strName, nNumAverage)
    #            if pose != None:
    #                listPoses.append(pose)
    #                print("new mark learn %s" % mark.strName)
    #                marksLearned.append(mark.strName)
    #    if listPoses == []:
    #        return None

    #    self.tMap.aRobotCurPos6d = np.average(np.array(listPoses), 0)
    #    return self.tMap.aRobotCurPos6d

    def _localize(self, data, markStrName, nNumAverage = 1):
        """
        use the provided data from datamatrix extractor, and a filtering name (to use only one mark) to get the pose of the robot

        :param data:
        :param markStrName:
        :param nNumAverage:  number of capture to use for each mark to analyze
        :return:
        None is returned if fail
        """
        marksInMap = self.tMap.aGlobalVs.keys()  #labels
        avd = naoqitools.myGetProxy("ALVideoDevice")
        camNum = {'CameraTop':0, 'CameraBottom':1}[data.imageInfo.nCameraName]

        if not(markStrName in marksInMap):
            print("INF: abcdk.nav_mark._localize, markStrName(%s) not in global Map.. no update of pos" % (markStrName))
            return

        mark = extractortools.getMark(data, markStrName)
        if mark is None:
            print("INF: abcdk.nav_mark._localize, markStrName(%s) not data, no update of pos" % (markStrName))
            return

        timestamp = time.time()
        nSec = int(timestamp)
        nMicroSec = 1000000 * (timestamp - nSec)
        rect = avd.getImageInfoFromAngularInfoWithResolution(camNum, [0 - mark.aSizeWH[0]/2, 0-mark.aSizeWH[1], mark.aSizeWH[0], mark.aSizeWH[1]], data.imageInfo.nResolution)
        rectX, rectY, rectWidth, rectHeight = _enlargeRect(rect[0], rect[1], rect[2], rect[3] , data.imageInfo.nResolution)
        listPoses = []
        i = 0
        for _ in xrange(nNumAverage):
            i += 1
            dataMatrix = self.markDetector.processRectangleOneShot(False, rectX, rectY, rectWidth, rectHeight, nSec, nMicroSec)
            data_ = extractortools.datamatrix_decodeInfo(dataMatrix)
            mark_ = extractortools.getMark(data_, markStrName)
            if mark_ is not None:
                pos = self.tMap.computeRobotPose(mark_.strName, mark_.aCornersRefinedPixels, data_.imageInfo, bDebug=False)

                if self.bUseSound:
                    for mark in data.marks:
                        sound.playSound(sound.getNoteSound(int( mark.strName[1:],16 )), bWait=False, nSoundVolume=30 - i*(25/nNumAverage))

                if pos is not None:
                    print("pos: %s" % str(pos))
                    listPoses.append(pos)

        if len(listPoses) == 0:
            return None
        return np.median(np.array(listPoses), 0)

    def _getPossibleVs(self):
        """ provides the list of all named local map (e.g kitchen, office, etc..) that are reachable in the map

        :return: list of string
        """
        tMap =  self.tMap
        if tMap is None:
            print("ERR: abcdk.nav_mark.getPathToVs: Impossible to get a topological map")
            return

        if tMap is None:
            return []
        ret = []
        for key, vs in tMap.aWayPoints.iteritems():
            #print("key %s , vs %s vs, strLabel %s" % ( str(key), str(vs), str(tMap.aVss[key].strLabel)))
            strLabel = tMap.aVss[key].strLabel
            if strLabel is not None:
                ret.append(strLabel)
        return ret

    def _getMap(self):
        """ for debug purpose (for instance to print using self.log in choregraphe) """
        return self.tMap

    def _emptyMap(self):
        self.tMap = datamatrix_topology.DataMatrixTopologicalMap()


class NavMarkLearner(NavMark):
    """ Class for learning/modifying a map.
    """
    def __init__(self, bDebug=False, bUseSound=False):
        NavMark.__init__(self, bDebug=bDebug, bUseSound=bUseSound)
        #self.lastLearnedMap = None


    def forgetPreviousLearned(self):
        self.lastLearnedMap = None

## Public methods :
    def startLearn(self, strName=None, bOverwrite=False, bDebug=True):
        """
        Look at marks around, and add the current robot pose into the lastLearnedMap as an observation point.

        :type strName: str
        :param strName: optional name of the current robot location.
        :type bOverwrite: boolean
        :param bOverwrite: overwrite existing location with same name if it exists
        :return: A namedtuple:
            - nbrUsedMark: int - number of marks used during this learning
            - bConnected : boolean -- is the new local map attached to the global map

        :raise: NavMarkError: a `NavMarkError` is raised with an error message if something went wrong (e.g. mutex error)
        """
        ret = collections.namedtuple('aResLearn', ['nNbrUsedMark', 'bConnected'])

        self.bMustStop = False
        if self.markDetector is None:
            self.markDetector = MarkDetector(bDebug=self.bDebug)
        self.markDetector.setLearningSetting()
        self._reset()
        if self.bDebug:
            self.markDetector.addLogMarkerRobotHasMoved() # for debug purpose
        res = self._learn(strNameVS=strName, bOverwrite=bOverwrite)  # doing the real work
        #self.stop()  # on stop..
        if self.bMustStop:
            raise NavMarkError("startLearn Has been stopped by user (bMustStop: %s)" % self.bMustStop, nErrorCode=16)
            #return ret(0,False) # NDEV: peut etre raisé une erreur ici ?
        return ret(res.nbrUsedMark, res.bConnectedToOtherVs)

    def startLiteLearn(self, bDebug=True, strPath=None):
        """
        Perform a learn at a specific position, and return the markInfos list
        :return: the list of markInfos  [ return a list of marks Info ( [dataDecoded.imageInfo, mark]] )
        with mark a DatamatrixInfo see (extractorTools)
        """
        self.bDebug = bDebug


        if self.markDetector is None:
            self.markDetector = MarkDetector(bDebug=self.bDebug)

        if strPath is not None:
            self.markDetector.kstrDebugPath = strPath
        self.markDetector.setLearningSetting()
        self._reset()
        self.markDetector.addLogMarkerRobotHasMoved()
        res =  self._getDatamatrixArround()

        return res

    def startLearnOnFiles(self, strPath=None, bProcessImage=True):
        """

        :param strPath:
        :param bProcessImage:
        :return:
        """
        if bProcessImage:
            self.markDetector = MarkDetector(bDebug=True)
        if strPath is None:
            strPath = self.markDetector.kstrDebugPath  #
        for filename in sorted(os.listdir(strPath)):  # sorted by timestamp in name
            if 'debug' in filename:
                continue
            elif '.jpg' in filename and bProcessImage:
                if 'debug' not in filename and 'out' not in filename:
                    strPickleFile = os.path.join(strPath, filename.split('C')[0] + '.pickle')
                    dataDecoded = self.markDetector.processImageFile(os.path.join(strPath, filename), strPickleFile)
                    for mark in dataDecoded.marks:
                        print("dataDecoded %s, %s, %s" % (dataDecoded, dataDecoded.imageInfo, dataDecoded.marks))
                        self.tMap.updateAmer( mark.strName, mark.aCornersRefinedPixels, dataDecoded.imageInfo, bDebug=self.bDebug)

            elif '.pickle' in filename and not bProcessImage:
                dataDecoded = serialization_tools.loadObjectFromFile(os.path.join(strPath, filename))

                for mark in dataDecoded.marks:
                    #if hasattr(mark, 'aCornersRefinedPixels'):
                    self.tMap.updateAmer( mark.strName, mark.aCornersRefinedPixels, dataDecoded.imageInfo, bDebug=self.bDebug)
            elif '.moved' in filename:
                self._initNewLocalVs()
                self.tMap = copy.deepcopy(self.lastLearnedMap)

        if self.lastLearnedMap is not None:
            self.tMap = copy.deepcopy(self.lastLearnedMap)
        return self.tMap



    def _initNewLocalVs(self, strNameVS=None, bOverwrite=False):
        """
        Init a local VS before a new learn
        :return: None
        """
        if self.bUseSound:
            import speech
            import translate
        #: :type: datamatrix_topology.DataMatrixTopologicalMap
        self.lastLearnedMap = copy.deepcopy(self.tMap)
        if self.lastLearnedMap is None:
            raise NavMarkError('ERR: abcdk.navMarkErr.learn(): abcdk.nav_mark.learn: Impossible to get a topological map')
        try:
            if self.bUseSound:
                speech.sayAndLight(translate.chooseFromDict({"en":"I will learn the poses of marks around me.", "fr":"Je vais mémoriser la position des marques qui sont autour de moi."}))
        except AttributeError:
            pass
        if( strNameVS is not None ):
            if self.bUseSound:
                strTxt = translate.chooseFromDict({"en":"And so here will become: %s.", "fr":"Et ainsi ici cela sera: %s."})
                speech.sayAndLight( strTxt % stringtools.correctSentence(strNameVS) )

            ## check if a new local map should be created or a map with the same name could be overwritten
        if strNameVS is not None:
            for k, v in self.lastLearnedMap.aVss.iteritems():
                if v.strLabel == strNameVS:
                    if not( bOverwrite ):
                        if self.bDebug:
                            print("INF: abcdk.nav_mark.navMarkLearner._learn(): bOverwrite is False, return without modification")
                            ## TODO: raise error here
                            raise NavMarkError('ERR: Impossible to add the pose, bOverwrite is (%s) and a Vs named(%s) is already present' % (str(bOverwrite), strNameVS), nErrorCode=10)
                        #return ret(0, False, None, None, None)
                    del(self.lastLearnedMap.aVss[k])  # TODO: maybee use a delVs subFunction that clean everything that need to be cleanned
                    break

        self.lastLearnedMap.forgetViewerPos()

        VssKey = self.lastLearnedMap.nCurLocalVs
        if strNameVS is not None:
            self.lastLearnedMap.aVss[VssKey].strLabel = strNameVS
            print("INF: abcdk.navMark.learn : setting strLabel of (%s) to (%s)" % (VssKey, str(strNameVS)) )

    def _getDatamatrixArround(self):
        """
        Look around using markDiscover update and return the list of markInfos

        :return: the list of markInfos discovered [ [DatamatrixInfo, dataDecoded.imageInfo ] ]
        """
        if self.bUseSound:
            import speech
            import translate
        aLearnedMarks = []  # list of mark infos discovered
        marksToIgnore = []
        nbrUsedMark = 0
        bShouldStop = False
        avd = naoqitools.myGetProxy("ALVideoDevice")
        while (not(self.bMustStop) and not(bShouldStop)):
            bShouldStop, bFullImage = self.markDiscover.update()  # do the head movement
            if self.bMustStop:
                return
            if bShouldStop: # end of moves
                break
            if bFullImage:
                dataDecoded = self.markDetector.processFullImage()
                if dataDecoded.marks == []:
                    if self.bUseSound:
                        speech.say(translate.chooseFromDict({"en":"No mark seen.", "fr":"Je ne vois pas de marque."}))

                bOneNewMark = False
                for mark in dataDecoded.marks:
                    if not(mark.strName in marksToIgnore):
                        bOneNewMark = True
                        break
                if not(bOneNewMark):
                    if self.bUseSound:
                        speech.say(translate.chooseFromDict({"en":"No new mark seen.", "fr":"Je ne vois pas de nouvelle marque."}))  ## ON va avoir 2 fois le say (pas de marques et pas de new marques)

                if self.bMustStop:
                    break
            else:
                dataDecoded = self.markDetector.processOneShotWithTime()
                if self.bMustStop:
                    break

            for mark in dataDecoded.marks:
                if mark.strName in marksToIgnore:
                    continue
                if not(mark.strName[0] in self.usuableMarks):  # TODO  a virer plus tard..
                    if self.bDebug:
                        print("INF: abcdk.nav_mark.learn() : mark %s non geree" % (mark.strName))
                    continue
                if self.bUseSound:
                    sound.playSound(sound.getNoteSound(int( mark.strName[1:],16 )), bWait=False, nSoundVolume=60 )
                _lookAtMark(dataDecoded, mark)

                camNum = {'CameraTop':0, 'CameraBottom':1}[dataDecoded.imageInfo.nCameraName]
                x, y,width, height = avd.getImageInfoFromAngularInfoWithResolution(camNum, [0 , 0, mark.aSizeWH[0], mark.aSizeWH[1]], dataDecoded.imageInfo.nResolution)
                rect = [x-width/2, y-height/2, width, height]  # (x,y) center of image in pixels
                rectX, rectY, rectWidth, rectHeight = _enlargeRect(rect[0], rect[1], rect[2], rect[3] , dataDecoded.imageInfo.nResolution)
                dataDecoded_ = self.markDetector.processOneShotRectangleWithTime(rectX, rectY, rectWidth, rectHeight)

                if dataDecoded_.marks == []:   # ca peut arriver si quelq'un passe devant la marque ou que le lookAtMark a failled à cause du clipping
                    if bFullImage:
                        dataDecoded_ = self.markDetector.processFullImage()
                    else:
                        dataDecoded_ = self.markDetector.processOneShotWithTime()
                for mark_ in dataDecoded_.marks:
                    if mark_.strName != mark.strName:
                        continue
                        ## TODO : ici
                    learnedMark = self.learnAMark(mark_, dataDecoded_, numAverage = 7, nMaxCapture=10)
                    for aMarkInfo in learnedMark:
                        aLearnedMarks.append([aMarkInfo[2], aMarkInfo[3]])
                       # if self.bDebug:
                       #     imagePnp.matrixName = "{0:d}".format(int(infos[3].nTimeStamp * 1000000)) + infos[3].nCameraName + "_debugPnp" # for debug
                        ## TODO : refactoring ici
                    #    self.lastLearnedMap.updateAmer( infos[2].strName, infos[2].aCornersRefinedPixels, infos[3] , bDebug = self.bDebug);  # cette ligne est moche
                    if len(learnedMark) > 0:
                        marksToIgnore.append(mark.strName) # on l'apprend on peut l'ignorer à partir de maintenant.
                    if self.bUseSound:
                        speech.say(translate.chooseFromDict({"en":"Ok.", "fr":"Ok."}))
                    nbrUsedMark += 1
                    #end while
        return aLearnedMarks

    def _learn(self, strNameVS=None, bOverwrite=False):
        """
        :param strNameVS: the optional name of the current robot location.
        :param bOverwrite: if a position with the same name allready exists it's overwritten if this variable is True.
        :return: A namedtuple [nbrUsedMark, bConnectedToOtherVs, topoMap, aPose6Ds, bRelocalizeOk]

        Raises : NavMarkError: a NavMarkError is raised with an error message if something went wrong
        """
        if self.bUseSound:
            import speech
            import translate
        ret = collections.namedtuple('learnReturns', ['nbrUsedMark', 'bConnectedToOtherVs', 'topoMap'])

        self._initNewLocalVs(strNameVS=strNameVS, bOverwrite=bOverwrite)
        if self.bMustStop:
            return
        aMarkInfos = self._getDatamatrixArround()  # this function call the mover

        if self.bMustStop:
            return
        for aMarkInfo in aMarkInfos:
            self.lastLearnedMap.updateAmer( aMarkInfo[0].strName, aMarkInfo[0].aCornersRefinedPixels, aMarkInfo[1] , bDebug = self.bDebug)
        if self.bMustStop:
            return



        self.lastLearnedMap.updateGlobalMap()
        if self.bMustStop:
            return
        self.lastLearnedMap.updateTopology()

        if self.bMustStop:
            return
        #print("aWayPoints  = %s , nCurLocalVs = %s " % (str(self.lastLearnedMap.aWayPoints), str(self.lastLearnedMap.nCurLocalVs)))
        bConnectedToOtherVs = self.lastLearnedMap.aWayPoints.has_key(self.lastLearnedMap.nCurLocalVs)
        #if self.bUseSound:
        #    speech.sayAndLight(translate.chooseFromDict({"en":"I will check that I have learned the position correctly by looking each mark.", "fr":"Je vais vérifier que  j'ai bien appris les marques en les regardant une par une."}))
        #if self.bMustStop:
        #    return
        #aPos = self._localLocalize(self.lastLearnedMap)
        #if self.bMustStop:
        #    return
        #self.lastLearnedMap.aVss[self.lastLearnedMap.nCurLocalVs].robotLocalLocalize6D = aPos  # revoir le type ici
        #try:
        #    dX, dY = np.mean(aPos, axis=0)[:2]
        #    bRelocalizeOk = np.sqrt(dX**2 + dY**2) < 0.15
        #except IndexError:  # si on n'a pas revu les marques.. le mean fail.. (d'ou le try/catch)
        #    bRelocalizeOk = False
        ##topology.VectorSpace()
        nNbrUsedMark = len(self.lastLearnedMap.aVss[self.lastLearnedMap.nCurLocalVs].aAmersAveragePose6D)
        return ret(nNbrUsedMark, bConnectedToOtherVs, self.lastLearnedMap)


class NavMarkMover(NavMark):
    """ state machine for Going to a VS.
    It inherits from :class: `NavMark`
    """
    ## TODO : mettre des _ devant les methodre private, et des __ quand il ne faut vraiment pas l'utiliser.
    def __init__(self, initialState = 'localizing', bUseSound=False, bDebug=False):
        NavMark.__init__(self, bDebug=bDebug, bUseSound=bUseSound)
        self.initialState = initialState
        self.reset()

    def reset(self):
        self.currentState = self.initialState
        self.nextState = None
        self.bOriented = False
        self.fThresholdDistance = 0.40
        self.fMaxStep = 0.05
        self.fMaxSpeed = 0.3  # head max speed
        self.rHeadDefaultPitch = -0.4
        self.aPoseEstimated = None

        self.nPoseEstimationFail = 0
        self.fmaxDistanceBlindWalk = 0.5  # TODO: a bien expliquer/definir
        #: :type: np.array
        self.aCurDest = None
        #: :type: np.array
        self.pose6DToDest = None   # TODO: a virer
        #: :type: topololgy.TopologicalMap.retMoveCmd
        self.move = None  # n'est pas reset pour garder une memoire d'un run a l'autre  --> ???, il est reset a None la non ?
        self.nRemainingFootStepsToStartHeadMovement = 6
        self.rMinDistanceBeforeRelocalisation =  2 * self.fMaxStep
        self.rMinDistanceBeforeFullRelocalisation = 2 * self.rMinDistanceBeforeRelocalisation
        self.bShouldRecomputePath = True  # at the beginning we ask for path reconstruction
        self.rMaxRotationWithoutReloc = 2 * (math.pi/3.0)
        self.rSleepDuration = 0.1
        # for debug:
        self.startGoToVs = time.time()  # TODO : a virer
        self.listToSave = []
        self.bUnexceptedEventOccursSinceLastLocalization = False
        self.strEventDestinationWorldCoordinates = "NavBar2D/DestinationWorldCoordinates"
        if( self.mem is not None ):
            self.mem.raiseMicroEvent("NavBar2D/CurrentState", self.currentState )
            self.mem.raiseMicroEvent(self.strEventDestinationWorldCoordinates, self.aCurDest )
            #self.mem.raiseMicroEvent("NavBar2D/CurrentVS", None )
            #self.mem.raiseMicroEvent("NavBar2D/CurrentTaggedVS", None)
            self.mem.raiseMicroEvent("NavBar2D/DestinationPOI", None )
            self.mem.raiseMicroEvent("NavBar2D/Finished", None )
            self.mem.raiseMicroEvent("NavBar2D/Impossible", None)
            self.mem.raiseMicroEvent("NavBar2D/CurrentPosition", None)

    def startGoTo(self, aDestCoordinates=None, bOriented = False):
        """
        Go To a coordinate destination (3D or 6D).

        :param aDestCoordinates: 6D destination coordinates (numpy array)
        :param bOriented: destination point is oriented
        :return: bSuccess
        """
        #print("Start GotO call %s" % str(locals()))
        self.bMustStop = False
        if self.shouldRelocalize():
            #self.currentState = 'localizing'
            self.currentState = 'lookAtPossibleMark'
        else:
            self.currentState = 'getMove'
        self.aCurDest = aDestCoordinates

        if self.markDetector is None:
            self.markDetector = MarkDetector()  ## TODO : usefull ?
        self.markDetector.setNavigationSetting()

        self._setOriented(bOriented)
        #if self.aCurDest != strName:
        #    self.tMap.aCurPath = None  #reinit
        #    self._setDestVs(strName)

        self.mem.raiseMicroEvent("NavBar2D/DestinationWorldCoordinate", str(self.aCurDest) )
        bSuccess = self._run()

        if self.bMustStop:
            raise NavMarkError("startGoTo Has been stopped by user (bMustStop: %s)" % self.bMustStop, nErrorCode=16)

        return bSuccess


    def relocalize(self, bForce=False, bDebug=False):
        """
        Relocalize if necessary.
        Necessary means self.nCurLocalVse == None or self.aLastMotionWorldPos6D != naoqi.motion.getRobotPosition or bForce == True

        :param bForce:
        :param bDebug:
        :return: True if relocalizing has been done.
        """
        self.bMustStop = False
        self.markDetector = MarkDetector(bDebug=bDebug)
        bUseSensors = True
        aCurrentMotionWorldPos6D = self.motion.getRobotPosition(bUseSensors)
        if not(self.nCurLocalVse is None or aCurrentMotionWorldPos6D is None or not(np.allclose(aCurrentMotionWorldPos6D , self.aLastMotionWorldPos6D, atol=0.1))  or bForce) :
            #print("abcdk.nav_mark: relocalizing is not necessary")
            return False
        else:
            #print("abcdk.nav_mark: relocalizing is necessary")
            aNewPos = self._fastLocalize()

            if aNewPos is None:
                if self.bMustStop:
                    raise NavMarkError("Has been stopped by user (bMustStop: %s)" % self.bMustStop, nErrorCode=16)
                return False
            self.aLastMotionWorldPos6D = aCurrentMotionWorldPos6D
            #print("INF: abcdk.nav_mark.relocalize: NEW POS=%s" % self.nCurLocalVse)
            return True

# deprecated
    #def getPath(self):
    #    """ return the current path
    #        [tuple(nextVsId, nextVsName, nextVsVectorDirectorInFrameTorso), ..., tuple(nextVsId, nextVsName, finalVsVectorDirectorInFrameTorso)]
    #    """

    #    if not(self.mutex.testandset()):  ## grab the mutex
    #        raise NavMarkError("err: abcdk.nav_mark.getPathToVs: already using the mutex.")

    #    if self.aCurDest is not None:
    #        res = self.getPathToVs(self.aCurDest)
    #    else:
    #        print("ERR: abcdk.getPath() no current destination")
    #        res =  None
    #    self.mutex.unlock()
    #    return res

    #def getPossibleDest(self):
    #    ## TODO : mutexer ?
    #    return self._getPossibleVs()

    #def getVs(self):
    #    ## TODO : mutexer ?
    #    return self._getPossibleVs()

    def _setOriented(self, bOriented=False):
        self.bOriented = bOriented

    #def _setDestVs(self, destVs):
    #    self.aCurDest = destVs

    def _setInitialState(self, strInitialState):
        self.currentState = strInitialState

    def _setThDistance(self, fthresholDistance=0.10):
        """ set the minimum distance to the final vs to consider it reached """
        self.fThresholdDistance = fthresholDistance

    def _setMaxStep(self, maxStep=0.50):
        """ set maximum step for movements """
        self.fMaxStep = maxStep

    def _pause(self):
        """ change state to waiting state (sleeping)
        NDEV: a tester
        """
        self.currentState = 'waiting'

    def _lookAtPossibleMark(self):
        """ look at the last possible mark known.
        For now we just look at the best/closest mark
        """
        if self.move is not None:   # on vient de se deplacer..
            strLabelBestMark = self.tMap.getBestLabel(self.move.theoriticalPose)
            if strLabelBestMark is not None:
                aCoordinatesBestMark = self.tMap.aGlobalVs[strLabelBestMark]
                rYaw, rPitch = topology.getHeadMove(self.move.theoriticalPose, aCoordinatesBestMark)
                logger.info("USING yaw and pitch %s, %s for label %s" % (rYaw, rPitch, strLabelBestMark))
                motiontools.mover.moveJointsWithSpeed( "Head", [rYaw, rPitch], self.fMaxSpeed/2.0 , bWaitEnd=True)  # TODO :  gerer le clipping
                #if self.bUseSound:
                #    import speech
                #    import translate
                #    speech.sayAndLight(translate.chooseFromDict({"en":"I should look at the best datamatrix %s." % strLabelBestMark, "fr":"Looking at %s." % strLabelBestMark}))
            #else:
            #    if self.bUseSound:
            #        import speech
            #        import translate
            #        speech.sayAndLight(translate.chooseFromDict({"en":"No best datamatrix found" , "fr":"No best datamatrix" }))


        #else:
        #    if self.bUseSound:
        #        import speech
        #        import translate
        #        speech.sayAndLight(translate.chooseFromDict({"en":"No move found.", "fr":"no move."}))

        while(not(self.bMustStop)):
            if not(self.motion.moveIsActive()):
                break  # we start localizing using datamatrix only if all movements are finished
            time.sleep(0.1)
        self.nextState = 'localizing'

    def _localizing(self):
        """
        Do a fast localizing
        """
        logger.info("LOCALISATION start")
        self.lastPoseEstimated = self.aPoseEstimated
        self.aPoseEstimated = self._fastLocalize()  # TODO :check de la valeur timeout
        if self.bMustStop:
            return  # quit as fast a possible

        if self.aPoseEstimated is None:
            ## we retry at 0,0 pose
            motiontools.mover.moveJointsWithSpeed( "Head", [0, 0], self.fMaxSpeed, bWaitEnd = True )  # look ahead
            self.aPoseEstimated = self._fastLocalize()  # TODO :check de la valeur timeout
        if self.bMustStop:
            return  # quit as fast a possible

        # we reset to 0 the head pose
        motiontools.mover.moveJointsWithSpeed( "Head", [0, 0], self.fMaxSpeed, bWaitEnd = True )  # look ahead
        if self.bMustStop:
            return  # quit as fast a possible

        if self.aPoseEstimated is not None:  # succes
            self.nPoseEstimationFail = 0
            logger.info("localization success, nextState should be getMove")
            self.nextState = 'getMove'
            bUseSensors = True
            self.aLastMotionWorldPos6DDuringLastSuccessfullLocalizion = np.array(self.motion.getRobotPosition(bUseSensors))
            self.bUnexceptedEventOccursSinceLastLocalization = False
            self.rMaxErrorToleratedBeforeRecomputingPath = 0.15 # in meters
            if self.move is not None:
                self.bShouldRecomputePath =  self.bShouldRecomputePath or (numeric.dist2D(self.move.theoriticalPose[:2], self.aPoseEstimated[:2]) > self.rMaxErrorToleratedBeforeRecomputingPath)

        else:  # fail localization
            self.nPoseEstimationFail += 1
            logger.info("INF: abcdk.nav_mark.GotoVsManager.localizing() : impossible to find my localization..,")

            if self.shouldFullRelocalize():
                logger.info("nest state should be turnover, cause full reloca")
                self.nextState = 'turnOver'
            else:
                logger.info("nest state should be blindWalk")
                self.nextState = 'blindWalk'

            logger.info("next state is %s", self.nextState)
          #  if self.nPoseEstimationFail < 1:
          #      self.nextState = 'localizing'  # or kidnapping_check NDEV
          #  else:
          #      if self.move is not None and not(self.bBlind):
          #          self.nextState = 'blindWalk'
          #      else:
          #          #TODO ici appeler un slow localize, puis si ca ne marche pas un turnOver
          #          self.nextState = 'turnOver'

    def _handleKidnaping(self):
        """
        Handling kidnapping.

        We do not save distance when kidnapping had occured.
        :return:
        """
        ## gestion kidnapping.. ou deplacement trop grand
        if self.lastPoseEstimated is not None and self.aPoseEstimated is not None:
            rDistance = numeric.dist2D(self.aPoseEstimated[:2], self.lastPoseEstimated[:2])  # 2D distance
            if rDistance > 4 * self.fMaxStep:
                if self.bUseSound:
                    import speech
                    import translate
                    speech.sayAndLight(translate.chooseFromDict({"en":"Kidnapping detected.", "fr":"Kidnapping."}))
                #self.tMap.aCurPath = None
                self.bKidnappedLastTime = True
            else:
                if not(self.bKidnappedLastTime):
                    aToLog = [time.time(), self.aPoseEstimated.tolist(), rDistance] # [timestamp, position, distance 2D walked in meters]
                    with open(self.strLogMovementsFilename, 'a') as f:
                        json.dump(aToLog, f)
                self.bKidnappedLastTime = False

    def _getMove(self):
        """
        Compute the next move to be done using the current location
        """
        # execution
        ##self.bDebug = True
        self.move = None
        #if self.bDebug:
        #  startTime = time.time()
        #  self.debugInfo.rDurationProcessingMap += time.time() - startTime

        #print("aCurDest is %s" % self.aCurDest)
        #print("ACurPos is %s" % self.tMap.aRobotCurPos6d)
        #print("MaxStep is %s" % self.fMaxStep)
        #print("bOriented is %s" % self.bOriented)



        self.move = self.tMap.getMove(self.aCurDest, rMaxLenStep=self.fMaxStep, bOriented=self.bOriented, bRecomputePath=self.bShouldRecomputePath)
        #print("Self.move is %s" % str(self.move))

        if self.move is None: ## c'est l'erreur qu'on recupere
        #    if self.bDebug:
        #        print("ERR: abcdk.nav_mark.GotoVsManager.getMove() : return of tMap.getMove(%s, maxStep=%s)" % (str(self.aCurDest), str(self.fMaxStep)))
            raise NavMarkError("ERR: abcdk.nav_mark.GotoVsManager.getMove() : return of tMap.getMove(%s, maxStep=%s) is None" % (str(self.aCurDest), str(self.fMaxStep)))

        #if self.bDebug:
        #    print("Using dx (%f), dy (%f), dtheta (%f)" % (self.move.dx, self.move.dy, self.move.dtheta))
        #    #print("using yaw (%f) /pitch (%f)" % (self.move.yaw, self.move.pitch))
        #    ## on sauvegarde  pour debug
        #    self.debugInfo.rTotalDuration = time.time() - self.startGoToVs
        #    #self.listToSave.append({'move':self.move._asdict(), 'self':self.__dict__})
        #    self.listToSave.append({'move':self.move._asdict(), 'timeStamp':time.time(), 'maxStep':self.fMaxStep, 'bBlind':self.bBlind, 'pose6DToDest':self.pose6DToDest, 'pose':self.tMap.aRobotCurPos6d, 'self.debugInfo':self.debugInfo.__dict__})
        #    filename = '/tmp/fullLastRun' + '_replay.pickle'
        #    #serialization_tools.saveObjectToFile(self.listToSave, filename)

        #transition
        self.pose6DToDest = numeric.norm2D((self.aCurDest - self.move.theoriticalPose)[:2])  # temporary
        if  self.pose6DToDest > self.fThresholdDistance:
            self.nextState = 'walking'
            #print("Next state is walking")
        else:
            motiontools.mover.moveJointsWithSpeed( "Head", [0, self.rHeadDefaultPitch], 0.3, bWaitEnd = True )  # NDEV ne devrait pas être ici
            print("next state is finish .. distance is %s" % self.pose6DToDest)
            self.nextState = 'end_goto'

    def _doBlindWalk(self):
        if self.bUseSound:
            import translate
            import speech
            speech.sayAndLight(translate.chooseFromDict({"en":"Blind.", "fr":"Aveugle."}))
        self.tMap.aRobotCurPos6d = self.move.theoriticalPose
        self.nextState = 'getMove'

    def _doMove(self):
        """ send the movement to motion proxy """
        self.motion.setExternalCollisionProtectionEnabled("All", False)  # required to perform move now

        bShouldDoRelocalisationAfterMove = (self.shouldRelocalize() and self.isRelocalizationEasyHere(self.move.theoriticalPose)) or self.mustReLocalize() or self.shouldFullRelocalize()
        logger.info("bShouldDoRelocalisationAfterMove is %s", bShouldDoRelocalisationAfterMove)
        bHeadTurned = False
        obstacles.manager.start()
        motiontools.mover.moveJointsWithSpeed( "Head", [0, -0.3], self.fMaxSpeed, bWaitEnd = False )  # look ahead
        if not(motiontools.isWalkPossible()):
            return False

        logger.info("Calling ALMOTION.moveTo(%s, %s, %s)" , self.move.dx, self.move.dy, self.move.dtheta)
        aMoveWayPoints = [[self.move.dx, self.move.dy, self.move.dtheta]]
        aMotionTaskId = self.motion.post.moveTo(aMoveWayPoints)
        while(not(self.bMustStop)):  #  we wait for move to begin
            if not(self.motion.isRunning( aMotionTaskId )):
                logger.error("The motion task has been interupted..before really starting.")
                return
            if not(motiontools.isWalkPossible()):
                return
            aFootSteps = self.motion.getFootSteps()
            nRemainingFootSteps = len(aFootSteps[1]) + len(aFootSteps[2])  # uncheangeable + changeable footsteps = total footsteps
            if nRemainingFootSteps > 0  : # we wait for a real movements has been send to Almotion
                print("move has really started")
                break
            if motiontools.hasFall():
                logger.info("Fall occurs during wait for move start")  # it would be handle in the second loop
                break

            time.sleep(self.rSleepDuration)
        logger.info("move start")
        while(not(self.bMustStop)):
            print("Loop move")
            nObstacleState = obstacles.manager.update()
            print("Obstacle states is %s" % nObstacleState)
            if nObstacleState != obstacles.global_aObstacleStates['none']:
                logger.info("obstacle detected")
                self._lastObstacleState = nObstacleState
                self.bUnexceptedEventOccursSinceLastLocalization = True  # obstacle can be considered as an "imprevu"
                self.nextState = 'handleObstacle'
                obstacles.manager.stop()
                return

            if motiontools.hasFall():
                logger.info("fall detected")
                self._lastObstacleState = 'fall'
                self.bUnexceptedEventOccursSinceLastLocalization = True  # obstacle can be considered as an "imprevu"
                self.nextState = 'handleObstacle'
                obstacles.manager.stop()
                return

            if not(motiontools.isWalkPossible()):
                logger.info("Move is not possible and no fall...it means flying..")
                self.nextState = 'localizing'
                return

            aFootSteps = self.motion.getFootSteps()
            nRemainingFootSteps = len(aFootSteps[1]) + len(aFootSteps[2])  # uncheangeable + changeable footsteps = total footsteps
            logger.info("footsteps %s" % nRemainingFootSteps)
            if not(bHeadTurned):
                if (nRemainingFootSteps < self.nRemainingFootStepsToStartHeadMovement):
                    if bShouldDoRelocalisationAfterMove:
                        self._lookAtPossibleMark()  # on commence a tourner la tete
                        bHeadTurned = True

            if (nRemainingFootSteps ==0):
                logger.info("end of walk movements")
                if not(motiontools.hasFall()): # fall will be handle in next turn of loop
                    print("no fall detected, end movement")
                    break
            time.sleep(self.rSleepDuration)
        else:
            return  # bMustStop occurs

        self.bShouldRecomputePath = False  # move has been done without obstacle
        self.tMap.aRobotCurPos6d = self.move.theoriticalPose
        if bShouldDoRelocalisationAfterMove:
            logger.info("Next state should be localizing")
            self.nextState = 'localizing'
            obstacles.manager.stop()
        else:
            logger.info("Next state should be getMove")
            self.nextState = 'getMove'
            # obstacles.manager.stop()  # on ne le stop pas car on va revenir ici

    def _doTurnOver(self):
        speedConfig = []
        motiontools.mover.moveJointsWithSpeed( "Head", [0, -0.3], self.fMaxSpeed, bWaitEnd = True )  # look ahead
        #speedConfig.append( ['MaxStepTheta', 0.25] )
        #speedConfig.append( ['MaxStepFrequency', 0.2] )
        self.motion.moveTo(-0.15, 0, math.pi, speedConfig)

        self.nextState = 'localizing'

    def _handleObstacle(self):
        import sound
        self.motion.stopMove()

        if motiontools.hasFall():
            self._lastObstacleState = 'fall'  # sometimes bumper are activated
#during fall
        if self._lastObstacleState == 'fall':
            #sound.playSound('/usr/share/naoqi/wav/outch.wav')
            #sound.playSound('/usr/share/naoqi/wav/outch.wav')
            #sound.playSound('/usr/share/naoqi/wav/outch.wav')
            self.tMap.addCubeObstacleBetweenTwoPosition6D(aPose6DA = self.tMap.aRobotCurPos6d, aPose6DB=self.move.theoriticalPose)
            print("trying to standup")
            motiontools.standup(nNbrRetries=5)
            print("ok now moving")
            self.motion.post.moveTo(-0.5, 0, 0)# on recule de 50 cm

        if self._lastObstacleState == obstacles.global_aObstacleStates['center']:
            if True:
                sound.playSound('/usr/share/naoqi/wav/outch.wav')
            #if self.bUseSound:
                #import speech
                #import translate
                #speech.sayAndLight(translate.chooseFromDict({"en": "Obstacle detected.", "fr": "Un obstacle a été détecté."}))

            self.tMap.addCubeObstacleBetweenTwoPosition6D(aPose6DA = self.tMap.aRobotCurPos6d, aPose6DB=self.move.theoriticalPose)
            #self.tMap.addCubeObstacleInFrontOfRobotPosition(rXdist=0.1)
           # self.tMap.addCubeObstacleInFrontOfRobotPosition(rXdist=0.1)

            self.motion.post.moveTo(-0.5, 0, 0)# on recule de 50 cm

        self.bShouldRecomputePath = True  # oH shit I forgot to set it to true here..
        self.nextState = 'lookAtPossibleMark'

    def _handleMoveNotPossible(self):
        """
        return True if we manage to stand up, false otherwise
        """
        rStartTime = time.time()
        rDuration = 0
        self.rTimeoutMoveNotPossible = 10  # in seconds
        bWakeUpSucces = False
        while(not(self.bMustStop)):
            motiontools.standup()
            rDuration = time.time() - rDuration
            if motiontools.isWalkPossible():
                bWakeUpSucces = True
                break
            if (rDuration > self.rTimeoutMoveNotPossible):
                logger.error("timeout %s reached (rDuration is %s), setting bMustStop to true", self.rTimeoutMoveNotPossible, rDuration)
                self.bMustStop = True
                break
            time.sleep(self.rSleepDuration)
        else:
            logger.error("quitting because bMustStop is %s", self.bMustStop)

        return bWakeUpSucces

    def _update(self):
        """
        return True if lastState is reached
        """
        self.mem.raiseMicroEvent("NavBar2D/CurrentState", self.currentState )
       # print('update current state is %s' % self.currentState)
        #print("NAVbAR2D/CURRENTSTATE", self.currentState )
        #print("NAVbAR2D/C******URRENTSTATE", self.currentState )
        if (motiontools.isWalkPossible() or self._handleMoveNotPossible()):  # on est debout ou on a reussi a se lever, on lance la machine a etat
            if self.currentState == 'lookAtPossibleMark':
                self._lookAtPossibleMark()
            elif self.currentState == 'localizing':
                self._localizing()
            elif self.currentState == 'getMove':
                self._getMove()

            elif self.currentState == 'walking':
                self._doMove()
            elif self.currentState == 'handleObstacle':
                self._handleObstacle()
            elif self.currentState == 'blindWalk':
                self._doBlindWalk()
            elif self.currentState == 'turnOver':
                self._doTurnOver()
            elif self.currentState == 'waiting':
                time.sleep(0.1)  #le robot ne fait rien
            elif self.currentState == 'end_goto':
                self.mem.raiseMicroEvent("NavBar2D/Finished", self.aCurDest )
                self.nextState = 'end_goto'
                return True
            else:
                raise NavMarkError("ERR: self.currentState (%s) is not known" % str(self.currentState))
            self.currentState = self.nextState
        return False

    def _run(self):
        """ start the state machine and loop until self.bMustStop == True, or endState is reached """
        if self.tMap is None:
            print("ERR: abcdk.nav_mark.GotoVsManager.run: Impossible to get a topological map")
            self.mem.raiseMicroEvent("NavBar2D/Impossible", self.aCurDest)
            raise NavMarkError("ERR: abcdk.GoToVsManager.run(objectState = %s) no topoMap" % (str(self.__dict__)))
        #self.tMap.updateTopology()  # done only once .. is it necessary ? TODO virer si pas nececssaire ?

        #if not(self.aCurDest in self._getPossibleVs()):
        #    self.mem.raiseMicroEvent("NavBar2D/Impossible", self.aCurDest)
        #    self.mutex.unlock()
        #    raise NavMarkError("ERR: abcdk.GoToVsManager.run(objectState = %s) destination not in reachable dest (%s) " % ((str(self.__dict__)), str(self._getPossibleVs())))

        self.startGoToVs = time.time()
        while not(self.bMustStop):
            bIsFinished = self._update()  # follow state machine states
            #serialization_tools.exportObjectToAlMemory(self.tMap, 'topoMap')  # commented cause it could be slow
            if bIsFinished:
                break
        else:  # bMustStop is true
            logger.info("INF: abcdk.nav_mark.run: stop has been received quitting( current state = %s, nextState %s )" % (str(self.currentState), str(self.nextState)))
            return False
        return True

    def isRelocalizationEasyHere(self, aRobotCurPos6d):
        bRes = self.tMap.isRelocalizationEasyPossibleHere(aRobotCurPos6d)
        import speech
        if not(bRes):
            speech.sayAndLight("relocalization difficult here")
        else:
            speech.sayAndLight("relocalization should be ok")
        return bRes

    def mustReLocalize(self):
        bMustRelocalize = False
        bUseSensors = True
        if self.aLastMotionWorldPos6DDuringLastSuccessfullLocalizion is None:
            return True

        aCurrentMotionWorldPos6D = np.array(self.motion.getRobotPosition(bUseSensors))
        rDistanceDoneSinceLastLocalization = numeric.dist2D(self.aLastMotionWorldPos6DDuringLastSuccessfullLocalizion[:2], aCurrentMotionWorldPos6D[:2])
        bMustRelocalize = (rDistanceDoneSinceLastLocalization > np.mean([self.rMinDistanceBeforeFullRelocalisation, self.rMinDistanceBeforeRelocalisation]))
        return bMustRelocalize

    def shouldRelocalize(self):
        """
        return True if a relocalization is required before doing new movements
        return False otherwise
        """
        bShouldRelocalize = False


        bUseSensors = True
        if self.aLastMotionWorldPos6DDuringLastSuccessfullLocalizion is None:
            return True
        #else

        aCurrentMotionWorldPos6D = np.array(self.motion.getRobotPosition(bUseSensors))
        rDistanceDoneSinceLastLocalization = numeric.dist2D(self.aLastMotionWorldPos6DDuringLastSuccessfullLocalizion[:2], aCurrentMotionWorldPos6D[:2])
        bShouldRelocalize = bShouldRelocalize or (rDistanceDoneSinceLastLocalization >= self.rMinDistanceBeforeRelocalisation)

        bShouldRelocalize = bShouldRelocalize or self.bUnexceptedEventOccursSinceLastLocalization

        if self.move is not(None):
            bShouldRelocalize = bShouldRelocalize or (abs(self.move.dtheta) > self.rMaxRotationWithoutReloc )

        logger.info("bShouldRelocalize is %s" % bShouldRelocalize)
        #if self.bUseSound and bShouldRelocalize:
        #    import speech
        #    import translate
        #    speech.sayAndLight(translate.chooseFromDict( {"en": "Relocalize is required.", "fr": "Relocalization nécessaire."}))

        #self.bShouldRecomputePath = bShouldRelocalize  ## TODO: for now we use the same value
        return bShouldRelocalize

    def shouldFullRelocalize(self):
        """
        return True if a full relocalization (moving to find a datamatrix) is required before doing new movements
        return False otherwise
        """
        bShouldFullRelocalize = False
        bUseSensors = True
        aCurrentMotionWorldPos6D = np.array(self.motion.getRobotPosition(bUseSensors))
        rDistanceDoneSinceLastLocalization = numeric.dist2D(self.aLastMotionWorldPos6DDuringLastSuccessfullLocalizion[:2] , aCurrentMotionWorldPos6D[:2])
        bShouldFullRelocalize = bShouldFullRelocalize or (rDistanceDoneSinceLastLocalization > self.rMinDistanceBeforeFullRelocalisation)
        logger.info("bShouldRelocalize is %s" % bShouldFullRelocalize)

        #if self.bUseSound and bShouldFullRelocalize:
        #    import speech
        #    import translate
        #    speech.sayAndLight(translate.chooseFromDict( {"en": "Relocalize is required.", "fr": "Relocalization nécessaire."}))

        return bShouldFullRelocalize


class fakeDetector(object):
    def __init__(self, jsonPath=None):
        self.version = 0.01
        self.jsonPath = jsonPath
        self.curNum = 0

    def processOneShot(self, b, nSec, nMicroSec):
        print "fake"

    def setLearningSetting(self):
        print("Fake set setting")

    def update(self):
        print "fake"

