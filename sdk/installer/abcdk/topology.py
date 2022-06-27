# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Topology tools
# Aldebaran Robotics (c) 2010 All Rights Reserved
# This file is confidential.
###########################################################
"""Topology tools"""
print("importing abcdk.topology")

import mutex
import time
import numeric
import numpy as np
import math
import copy  # used it for deepcopy
import collections
import path_planner

#import scipy.sparse
from operator import itemgetter
import logging

logger = logging.getLogger('__name__')


#logger.setLevel(logging.INFO)  # enable only debug message
#logger.propagate = False   # disable logging for this file

## tool functions

def _getCameraLookingFrontPose6DInRobotRef():
    """
    pose of camera if it's looking to front direction
    """
    import naoqitools
    motion = naoqitools.myGetProxy("ALMotion")
    if motion is None:
        #camPos6DInRobotRef = np.array([0.04696042090654373, -0.0004342024330981076, 0.19924230873584747, 0.0, -0.15090644359588623, -0.009245872497558594])  # this is the value when the robot is straight after a move
        #camPos6DInRobotRef = np.array([0.04696042090654373, -0.0004342024330981076, 0.19924230873584747, 0.0, 0.0, 0.0])  # this is the value when the robot is straight after a move
        #for debug/ if no motion we consider the head is at 1meter au dessur des pieds (completement faux, mais plus simple pour tester
        camPos6DInRobotRef = np.array([0, 0, 1, 0.0, 0.0, 0.0])
        camPos6DInRobotRef = np.array([0, 0, 0, 0.0, 0.0, 0.0])
    else:
        FRAME_ROBOT = 2
        camPos6DInRobotRef = np.array(motion.getPosition('CameraTop', FRAME_ROBOT, True))
    camPos6DInRobotRef[3:]  = 0  # we are interested in case the camera is orriented in robot direction, so it explain the 0 for the orientation
    return camPos6DInRobotRef

def _decomposeInRotationTranslation(rDx=0, rDy=0, rDtheta=0, rMinThetaThreshold=math.pi/3, rMinTranslationDist=0.1):
    """
    Decomposed movements if huge rotation+translation

    if dtheta > rMinThetaThreshold  and  if trnalsation if above rMinTranslationDist then the movement is decomposed in two movements: first rotation, then transaltion
    """
    rNewDxIfRotateFirst = math.sqrt(rDx**2+rDy**2)
    if (abs(rDtheta) > rMinThetaThreshold and rNewDxIfRotateFirst>0.1):  # in case of "big angle" we decompose the move in first rotation then translation
        aMoveWayPoints = [[0,0,rDtheta], [rNewDxIfRotateFirst, 0, 0]]
    else:
        aMoveWayPoints = [[rDx, rDy, rDtheta]]
    return aMoveWayPoints

def computeGlobalObjectP6DUsingAmer(aP6DObjectLocal=None, aP6DPivotLocal=None, aP6DPivotGlobal=None):
    """
    Une fonction qui pour une pose6D dans un localVs renvoie la pos6D dans le globalVs en se basant sur un pivot.

    @rtype : object
    @param aP6DObjectLocal: p6D of object in a local VS
    @param aP6DPivotLocal: p6D of a reference amer in the local VS
    @param aP6DPivotGlobal: p6D of reference in the global Vs
    @rtype: np.array
    @return:
    """
    if False:
        #le code suivant ne fonctionne pas !! WARNING ! -> normal c'est pas ca qu'on veut..
        #pRefAInRefB =   -> il faut d'abord faire la translation puis les rotations puis revenir.. et la le change repere marchera.. logique !
        #aP6ObjectToPivotInLocal = numeric.changeReference(aP6DObjectLocal, -aP6DPivotLocal)  ### le pb est ici pRefA in RefB c'est pas juste un - .. car on n'est pas centré ...
        #newPose = numeric.changeReference(aP6ObjectToPivotInLocal, aP6DPivotGlobal)

        #newPose = numeric.changeReference(aP6DPivotGlobal, aP6ObjectToPivotInLocal)
        return None
        #return newPose
    else:
        rotationPoint = aP6DPivotLocal[:3]
        diff = np.array(aP6DPivotGlobal) - np.array(aP6DPivotLocal)
        dX, dY, dZ = diff[:3]  # translation vector
        dwX, dwY, dwZ = diff[3:6]  # rotation angles

        oldPose = aP6DObjectLocal  # position + orrientation
        newPosition = (numeric.chgRepere(oldPose[0] - rotationPoint[0],
                                        oldPose[1] - rotationPoint[1],
                                        oldPose[2] - rotationPoint[2], dX,
                                        dY, dZ, dwX, dwY, dwZ) + rotationPoint)
        newOrientation = oldPose[3:6] + np.array([dwX, dwY, dwZ])
        newPose = np.array([newPosition[0], newPosition[1], newPosition[2], newOrientation[0], newOrientation[1], newOrientation[2]])
        return newPose


def computePoseAfterMove(aCurPose6D, dxTorso=0, dyTorso=0, dtheta=0):
    """
    Compute the theoretical pose of the robot after a move (in case of a perfect move).

    @param aCurPose6D: current robot Pose (pos6d - np.array)
    @param dxTorso: dx move
    @param dyTorso: dy move
    @param dtheta: dtheta move  (cropped to -3.1415, 3.1415)
    @return: pose6D in world reference (np.array, dtype=np.float)
    """
    #    logger.info("INF topology.computePoseAfterMove call with aCurPose6D= %s, dxTorso = %f , dyTorso = %f, dtheta = %f" % (str(aCurPose6D), dxTorso, dyTorso, dtheta))
    aTheoreticalP6DInFrameRobot = np.zeros(6, dtype=np.float)
    aTheoreticalP6DInFrameRobot[0] = dxTorso
    aTheoreticalP6DInFrameRobot[1] = dyTorso
    # using motion move limits
    if dtheta > 3.1415:
        dtheta = 3.1415
    if dtheta < -3.1415:
        dtheta = -3.1415
    aTheoreticalP6DInFrameRobot[5] = dtheta
    aTheoriticalPoseAfterMove = numeric.changeReference(aTheoreticalP6DInFrameRobot, aCurPose6D)  # # BUG ici .. ca ne va pas du tout !!!
    return aTheoriticalPoseAfterMove


def getHeadMove(aRobotPoseInWorldRef, aMarkPoseInWorldRef):
    """
    return the headmove (pitch/yaw) to use in order to look(using cameraTop) at a pose6D from a specific targetPoint

    @param aRobotPose: pose6D of robot in topological map (it's FRAME_ROBOT in topological world)
    @param markToLookPose6D: pose6D of mark in topological map
    @return: [yaw, pitch]
    """
    #logger.info("INF getHeadMove(aRobotPose6D=%s, markToLookPose6D=%s" % (str(targetPoint), str(markToLookPose6D)))
    if aMarkPoseInWorldRef is None or aRobotPoseInWorldRef is None:
        return TopologicalMap.retYawPitch(-0.1, 0)  # default value, no mark to look

    aMarkPoseInRobotRef = numeric.convertPoseWorldToFrameRobot(aMarkPoseInWorldRef, aRobotPoseInWorldRef)
    camPos6DInRobotRef = _getCameraLookingFrontPose6DInRobotRef()
    aRobotRefInRefCam = numeric.inversePose(camPos6DInRobotRef)
    aMarkPoseInRefCam = numeric.changeReference(aMarkPoseInRobotRef, aRobotRefInRefCam)

    yaw = math.atan2(aMarkPoseInRefCam[1], aMarkPoseInRefCam[0])   # azimuth
    pitch = -math.atan2(aMarkPoseInRefCam[2], math.sqrt(aMarkPoseInRefCam[0] ** 2 + aMarkPoseInRefCam[1] ** 2))  # - = vers le haut, + = vers le bas
    #yaw = numeric.cartesianToPolar( aMarkPoseInRefCam[0], aMarkPoseInRefCam[1])[1]
    #itch = numeric.cartesianToPolar( aMarkPoseInRefCam[0], aMarkPoseInRefCam[2] )[1]
    #logger.info("yaw %s pitch %s, aMarkPoseInRefCam %s" % (yaw, pitch, aMarkPoseInRefCam))
    return TopologicalMap.retYawPitch(yaw, pitch)


def computeViewAngle(aCameraPose6D, aTargetPose6D):
    """ compute the view angle between camera pose and target point

    viewAngle is difference between orientation of camera and target orrientation
    """
    viewAngle = abs(numeric.computeVectAngle(numeric.polarToCartesian(1, aCameraPose6D[5]), numeric.polarToCartesian(1, aTargetPose6D[5])))
    return viewAngle


def evaluateLabel(aRobotPose6D=None, labelPose6D=None, maxDistance=4.5, maxYaw=math.pi / 2.0, maxPitch=0.34, maxViewAngle=math.pi / 4):
    """
    Evaluate if a mark at a specific pose is viewable by the robot at a specific robotPose.

    @param aRobotPose6D: robot pose 6D
    @param labelPose6D: mark pose 6D
    @param maxDistance: maximum distance to view a mark
    @param maxYaw: maximum yaw usable by the robot
    @param maxPitch: maximum pitch usable by the robot
    @param maxViewAngle: maximum view angle
    @return: (bIsNear, bIsViewable, nDistance3D)
    """
    distToLabel3D = numeric.dist3D(aRobotPose6D[:3], labelPose6D[:3])
    bIsNear = distToLabel3D < maxDistance
    yawToLabel, pitchToLabel = getHeadMove(aRobotPose6D, labelPose6D)
    cameraPose6DAfterYawPitch = np.array([aRobotPose6D[0], aRobotPose6D[1], aRobotPose6D[2], aRobotPose6D[3], aRobotPose6D[4] - pitchToLabel, aRobotPose6D[5] + yawToLabel])
    viewAngle = computeViewAngle(cameraPose6DAfterYawPitch, labelPose6D)
    bIsViewable = (abs(yawToLabel) < maxYaw) and (abs(pitchToLabel) < maxPitch) and (viewAngle < maxViewAngle)
    logger.error("yawToLabel %s (max is %s), pitchToLabel %s (max is %s), viewAngle %s (max is %s)", yawToLabel, maxYaw, pitchToLabel, maxPitch, viewAngle, maxViewAngle )
    nDistance3D = numeric.dist3D(labelPose6D[:3], aRobotPose6D[:3])
    #logger.info("INF: abcdk.topology.evaluateLabel(aRobotPose6D=%s, labelPose6D=%s, maxDistance=%f, maxYaw=%f, maxPitch=%f. Returns: (bIsNear=%s, bIsViewable=%s (yawToLabel=%f, pitchToLabel=%f, viewAngle=%f), nDistance3D=%f" % (str(aRobotPose6D), str(labelPose6D), maxDistance, maxYaw, maxPitch, str(bIsNear), str(bIsViewable), yawToLabel, pitchToLabel, viewAngle, nDistance3D))
    return (bIsNear, bIsViewable, nDistance3D)


def getProjCoord(pose6D, axis='Z'):
    """ tool function to project "vue de dessus"""
    if axis == 'Z':
        x2D = pose6D[0]
        y2D = pose6D[1]
        vectDir = numeric.polarToCartesian(1, -math.pi + pose6D[-1])
        return x2D, y2D, vectDir
    if axis != 'Z':
        return None

## Tool functions - end

class VectorSpace(object):
    """
    A container to handle a local vectorSpace
    """

    def __init__(self, strLabel=None, bDebug=True):
        self.bDebug = bDebug
        self.aRobotPose6D = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])  # robot pose in the local space
        self.aRobotPose6D.flags.writeable = False  # in a localSpace the robot is always at 0
        # pour chaque amer on stock ses cooord (dans le repere du robot) et l'orientation (pour tourner le robot vers la marque)
        # un moveTo(coord) nous amene donc sur la marque
        # un moevToAngle ( orientation) nous fait regarder la marque

        #: :type: dict of (str, np.array)
        self.aAmersPose6D = dict()  # pose of each amer (using median ?) TODO a verifier
        #: :type: dict of (str, np.array)
        self.aAmersAveragePose6D = dict()  # average pose of each amer
        #: :type: dict of (str, np.array)
        self._aAmersSubDictPose6D = dict()  # list of pose for each amer
        #: :type: dict of (str, np.array)
        self.aAmersScores = dict()  # score for each amer
        #: :type: dict of (str, np.array)
        self.aAmersDiagSize = dict()  # diagonal size of each amer
        #: :type: dict of (str, np.array)
        self._aAmersSubViewedSize = dict()  #
        #: :type: np.array
        self.aRobotLocalLocalize6D = None  # # could be use for debug purpose, after learning we pan and try to relocalize..
        self.rMinNbrAverage = 5  # minimum number of the same amers to compute a good score
        self.rMaxAngleScore = 100.0  # Score for angles, if the mark has been seen less than self.rMinNbrAverage
        #def updateScores(self):
        #    ## update scores to correct a saved map (USe it for debug only)
        #    # for debug only
        #    for key, value in self.aAmersScores.iteritems():
        #    #    if len(self._aAmersSubDictPose6D[key]) >5:
        #    #        self._aAmersSubDictPose6D[key] = self._aAmersSubDictPose6D[key][:5]
        #        std_z = np.std(np.array(self._aAmersSubDictPose6D[key]), 0)[5]
        #        sqrtN = np.sqrt(len(self._aAmersSubDictPose6D[key]))
        #        #logger.info sqrtN *sqrtN
        #   #         logger.info("key %s : %f" % (str(key), len(self._aAmersSubDictPose6D[key])))
        #        distance = numeric.dist3D(np.array([0,0,0]), self.aAmersPose6D[key][:3])
        #        if len(self._aAmersSubDictPose6D[key]) < 5:  # .. pas super.. mais pour tester c'est un peu mieux
        #            self.aAmersScores[key] = 500
        #        else:
        #            self.aAmersScores[key] = std_z / (sqrtN * distance * 1000)
        #        ## TODO : revoir les cartos.. est ce que dans self.aRobotLocalLocalize6D on met la pos par rapport a une marque particuliere revue.. ou est ce que c'est la moyenne par rapport a toutes les marques..
        #        ## c'est peut etre pas un super indicateur de est ce que la carte a ete bien apprise en fait..

        #        if self.aRobotLocalLocalize6D == None or self.aRobotLocalLocalize6D ==  []:
        #            self.aAmersScores[key] = 505
        #   #         ## test nouveau score
        #   #         if self.aRobotLocalLocalize6D == None or self.aRobotLocalLocalize6D ==  []:
        #   #             self.aAmersScores[key] =  self.aAmersScores[key]
        #   #         else:
        #   #             self.aAmersScores[key] =  self.aAmersScores[key] *  numeric.dist3D(np.mean(self.aRobotLocalLocalize6D[:3], axis=0), np.array([0,0,0,0,0,0])[:3])
        #    else:
        #        res = 0
        #    return res

    def delete(self, key):
        """
        Delete a mark in the vectorspace
        """
        logger.info("Deleting %s in vs" % key)
        ## c'est assez moche : Ndev avoir une structure plus propres, genre un dictionnaire, indexé par key, qui contient tous les autres dictionnaires.. TODO
        for aDict in [self._aAmersSubDictPose6D, self._aAmersSubViewedSize, self.aAmersAveragePose6D, self.aAmersDiagSize, self.aAmersPose6D, self.aAmersScores]:
            aDict.pop(key, None)

    def addPoint6D(self, strLabel, aPose6D, rViewedSize, rDiagSize):
        """
        Add amer information to a local vectorSpace

        If amer is new, a novel amer is created in the local vector space.
        If an amer with the same `strLabel` exists, then the amersPose6D is updated using median of allPreviousPose6D +theNewPose6D

        The score attached to an amers is a confidence score (with 0 = perfect, and 1 = bad)
        it's based on the variation of estimated pose6D over different snapshot of the same amer
        @param strLabel: label of the amer
        @param aPose6D: pose estimation of the
        @param rViewedSize: diagonal viewed size in pixel
        @param rDiagSize: real diagonal size in meters  ## is it necessary ??? NDEV
        """
        #logger.info("rDiagSize %s" % rViewedSize)
        #if rViewedSize < 50:
        #    logger.info("rejet")
        #    ## Juste pour tester rapidement le rejet
        #    return
        #else:
        #    logger.info("Ok")
        if not(strLabel in self._aAmersSubDictPose6D):
            self._aAmersSubDictPose6D[strLabel] = []
            self._aAmersSubViewedSize[strLabel] = []
        self._aAmersSubDictPose6D[strLabel].append(np.array(aPose6D, dtype=np.float))
        self.aAmersPose6D[strLabel] = np.median(np.array(self._aAmersSubDictPose6D[strLabel]), 0)  # Warning if even number (example 2) the value is the average of the middle values (see numpy.median) documentation
        self.aAmersAveragePose6D[strLabel] = np.mean(np.array(self._aAmersSubDictPose6D[strLabel]), 0)
        self.aAmersDiagSize[strLabel] = rDiagSize
        self._aAmersSubViewedSize[strLabel].append(rViewedSize)

        # Score computation: it's just the Relative Standard Error (RStdE) of the pose6D[5] over the different pose estimation of the same landmark)
        # See : http://en.wikipedia.org/wiki/Standard_error  - it's equal to the coefficient of variation :   coefficient of variation
        ## En fait on fait juste un std sur les angles.. car souci avec le Rstde qui diverge pret de 0
        #aPoses = np.array(self._aAmersSubDictPose6D[strLabel])  # NDEV / TODO : le faire avec toutes les dim pas juste la 5
        aAngles = np.array(self._aAmersSubDictPose6D[strLabel])[: , 3:]
        if len(self._aAmersSubDictPose6D[strLabel]) < self.rMinNbrAverage:
            rAngleScore = np.mean(self._aAmersSubViewedSize[strLabel])   # self.rMaxAngleScore
        else:
            #rRStdE = np.std(aPoses, 0) / ( np.mean(aPoses, 0) * np.sqrt(aPoses.shape[0]) )
            rAnglesSTD = np.std(aAngles, 0) / np.sqrt(aAngles.shape[0])
            rAngleScore = np.max(rAnglesSTD)

        self.aAmersScores[strLabel] = rAngleScore / np.mean(self._aAmersSubViewedSize[strLabel])   # score is related to the angle Std variation and to the viewed size in camera space
        if self.aAmersScores[strLabel] > 1:
            logger.info("Score above 1")

# class VectorSpace - end

class TopologicalMap(object):
    """
    Container to handle a map of amers, observations points, robotPosition, and navigations points. It provides
    function to look at mark, and move in the map.
    """

    ## named tuple are defined here for optimization purpose (one dectaration)
    retYawPitch = collections.namedtuple('headYawPitch', ['yaw', 'pitch'])
    retMoveCmd = collections.namedtuple('moveCmd', ['dx', 'dy', 'dtheta', 'theoriticalPose'])
    retMoveToTarget = collections.namedtuple('move', ['dx', 'dy', 'dtheta', 'theoriticalPose'])

    def __init__(self):
        logger.info("INF: abcdk.topology: INIT of a TOPOLOGICAL MAP (address %s)" % hex(id(self)))
        self.mutex = mutex.mutex()
        #: :type: dict of (int, VectorSpace)
        self.aVss = dict()
        self.nCurLocalVs = -1  # current vectorSpace id
        #: :type: dict of (str, np.array)
        self._aGlobalVs = dict()  # the map container itself
        #: :type: dict of (str, float)
        self.aAmersScore = dict()  # score of confidence attached to each amer
        self.topologycalMap2D = TopologicalMap2D()
        #self._aRobotCurPos6d = np.zeros(6)  # robot pos6D in global
        self.aRobotCurPos6d = np.zeros(6)  # robot pos6D in global   # we use the setter

        self.bDebug = False
        #: :type: dict of (str, np.array)
        self.aWayPoints = dict()  # # list of passage points (updated when doing update global map)
        #: :type: dict of (str, dict of (str, float))
        self.aNeighbors = dict()  # {VsId: {VsId:cout, VsId:cout}, VsId: {VsId:cout}}
        #self.aCurPath = []  # Current computed path to reached destination, exemple : {'1':{'2':1, '3':1}, '2':{'3':1}}

        #: :type: str
        self.strLastUsedAmer = None  # named of the last used amer
        #: :type: boolean
        self.bUseObstaclesMap = False
        #self.motion = naoqitools.myGetProxy( "ALMotion" );

        self.forgetViewerPos()  # it allows to create a new local vectorSpace and incremment nCurLocalVs
        self.rMinConfidence = 0.999200
        self.aObstacles = ObstaclesContainer()
        self._ObstacleBehindDatamatrix = []  # list of obstacle added behind each datamatrix
        self.aAttractiveRegion = ObstaclesContainer()  # TODO: provide a region container ?
        self._AttractiveRegionInFrontDatamatrix = []  # list of attractiveRegion added inf front of each datamatrix
        self.aNextWayPointsPose6D = []
        self._aLastDestPose6D = None  ## last pose for path planning usefull to check it has changed and a new path have to be recomputed


    def __repr__(self):
        passage = [key for key, ptPassage in self.aWayPoints.iteritems()]
        Vss = [(key, val.aAmersPose6D.keys()) for key, val in self.aVss.iteritems()]
        strTologger = "TopologicalMap, current globalMap %s, list of Vs = {%s}" % (str(passage), str(Vss))
        return strTologger

    def __getstate__(self):
        """
        Useful for pickle serialization
        """
        return self.__dict__

    def __setstate__(self, d):
        """
        Useful for pickle serialization
        """
        self.__dict__.update(d)

    @property
    def aRobotCurPose6d(self):
        return self._aRobotCurPos6d

    @aRobotCurPose6d.setter
    def aRobotCurPos6d(self, aPose6D):
        logger.info("setting new robot cur pos %s" % aPose6D)
        self._aRobotCurPos6d = aPose6D
        # updating pose in 2D map
        aNewPose2D = aPose6D[:2]
        logger.info("updating pose2D using %s -> %s" % (aPose6D, aNewPose2D))
        self.topologycalMap2D.aCurPose2D = aNewPose2D  # # TODO : faire une vrai projection /// urgent

    def forgetViewerPos(self):
        """
        Init a new viewer position and create the associated local vector space.
        """
        while not(self.mutex.testandset()):  # # grab the mutex
            if self.bDebug:
                logger.info("INF: abcdk.topology.forgetViewerPos: already using the object, waiting...")
            time.sleep(0.1)

        self.nCurLocalVs += 1  # increment of current vectorSpace id
        self.aVss[self.nCurLocalVs] = VectorSpace()  # create an empty vector space
        self.mutex.unlock()

    def deleteVectorSpacesContainingMark(self, strMarkLabel):
        """
        Tool functions to update the map by deleting all vectorSpaces that contains a specific amer.
        @param strMarkLabel: name of the amer to delete
        """
        vssToDelete = []
        while not(self.mutex.testandset()):  # # grab the mutex
            if self.bDebug:
                logger.info("INF: abcdk.topology.deleteVectorSpacesContainingMark: already using the object, waiting...")
            time.sleep(0.1)

        for vsKey, vs in self.aVss.iteritems():
            containedMarks = vs.aAmersPose6D.keys()
            if strMarkLabel in containedMarks:
                if self.bDebug:
                    logger.info("aVss (%s) containing (%s) is going to be deleted" % (str(vsKey), str(strMarkLabel)))
                vssToDelete.append(vsKey)
                continue
        for key in vssToDelete:
            self.aVss.pop(key)
        self.mutex.unlock()

    def deleteMarkVss(self, strMarkLabel):
        """ Delete a specific mark in all vectorSpace.

        @param strMarkLabel: name of the amer to delete
        """
        while not(self.mutex.testandset()):  # # grab the mutex
            if self.bDebug:
                logger.info("INF: abcdk.topology.deleteMarkVss: already using the object, waiting...")
            time.sleep(0.1)
        for vsKey, vs in self.aVss.iteritems():
            if strMarkLabel in vs.aAmersPose6D:
                if self.bDebug:
                    logger.info("deleting mark (%s) in aVss (%s)" % (strMarkLabel, vsKey))
                vs.aAmersPose6D.pop(strMarkLabel)
                vs.aAmersAveragePose6D.pop(strMarkLabel)
                vs._aAmersSubDictPose6D.pop(strMarkLabel)
        self.mutex.unlock()

    def removeAmersWithLowConfidence(self, rMinConfidence=None):
        if rMinConfidence is None:
            rMinConfidence = self.rMinConfidence
        if self.bDebug:
            logger.info("abcdk.topology removing amer with confidence below %s" % rMinConfidence)

        rMaxScore = 1 - rMinConfidence
        for vsKey, vs in self.aVss.iteritems():
            for key, rScore in vs.aAmersScores.items():
                if rScore > rMaxScore:
                    vs.delete(key)

    def addPoint6DToLocal(self, vs=None, strLabel=None, aPose=None, nViewedSize=100, rDiagSize=0.10):
        """
        add a point using pose6D to a local vectorSpace
        Args:
            strLabel: strLabel of the point
            aPose: pose6D ( np.array([dx, dy, dz, dwx, dwy, dwz]) )
            vsId: the id of the local Vs to append the point, if vsId == None then the current vectorSpace is used
        """
        if aPose is None:
            return

        if strLabel is None:
            return

        if vs is None:
            vs = self.aVss[self.nCurLocalVs]
        #while not(self.mutex.testandset()):  ## grab the mutex
        #    if self.bDebug:
        #        logger.info("INF: abcdk.topology.addPoint6D: already using the object, waiting...")

        vs.addPoint6D(strLabel, aPose, nViewedSize, rDiagSize)
        #self.mutex.unlock()

    def updateGlobalMap(self):
        """ update the global map by trying to connect the different local maps using intersection.

        The aWayPoints dictionnary is created and filled.
        The aGlobalVs that contains the global map is created and filled.
        NDEV/TODO : essayer de faire un gros test unitaire qui prend tous les cas en compte
        """
        self.aWayPoints = dict()
        self.aGlobalVs = dict()

        while not(self.mutex.testandset()):  # # grab the mutex
            if self.bDebug:
                logger.info("INF: abcdk.topology.updateGlobalMap: already using the object, waiting...")


        if self.rMinConfidence is not None:
            self.removeAmersWithLowConfidence()
        for _ in range(0, len(self.aVss.keys())):  # on refait n fois.. pour etre certain qu'on a exploré toutes les possibilités
        ## TODO : ici il faut sort par score des amers..
        #keyVssSortedByScore = sorted(self.aVss.keys(), cmp=lambda indexA, indexB: cmp(self.aVss[indexA].getVsScore(), self.aVss[indexB].getVsScore()), reverse=True)
            keyVssSortedByScore = self.aVss.keys()
            # logger.info "*"*20
            for key in keyVssSortedByScore:
            #    if self.aVss[key].aAmersScores> 50:
            #        logger.info("Score Vs: %s" % str(self.aVss[key].a()))

            #        self.aVss[key].updateScores()  # TODO : a virer si on refait un apprentissage la c'est pour etre certain d'avoir la derniere version du score meme sur une ancienne map
                self.updateGlobalMapUsingLocalVectorSpace(key)
                #self.addObstacleBehindEachDatamatrixMark()

        self.mutex.unlock()

    ## NEEDEED / private
    def updateGlobalMapUsingLocalVectorSpace(self, VsId):
        """ Try to find an amer that can be used to update the global space and run the update if possible """
        if self.aGlobalVs == {}:  # any amer could be used..
            intersection = self.aVss[VsId].aAmersPose6D.keys()
        else:
            intersection = [val for val in self.aVss[VsId].aAmersPose6D.keys() if val in self.aGlobalVs.keys()]

        if intersection != []:
            # we sort by the score the lowest the better
            intersectionSorted = sorted(intersection, cmp=lambda indexA, indexB: cmp(self.aVss[VsId].aAmersScores[indexA], self.aVss[VsId].aAmersScores[indexB]), reverse=False)
            label = intersectionSorted[0]
            if self.bDebug:
                logger.info("Updating aGlobalVs using Vs (%s) and pivot/amer (%s)" % (str(VsId), str(label)))
            self._updateGlobalVectorSpaceUsingAmer(VsId, label)
        else:
            if self.bDebug:
                logger.info("Update is not possible, no strLabel could be used")
        return self.aGlobalVs

    def _updateGlobalVectorSpaceUsingAmer(self, vsId, refAmer):
        """ Update global vector space based on `VsId` vector space information and using refAmer as the "pivot" amer.

        3D Rotation and translation are done to add all information from VsId
        into global space, if the information was already present in the global
        space the information with the highest score is kept.

        Input :
            vsId: local vector space to use
            refAmer: is used as a "amer" to make the fusion of information.
        """
        if not(refAmer in  self.aVss[vsId].aAmersPose6D):
            logger.error("ERR abcdk.topology._updateGlobalVectorSpaceUsingAmer: Local VectorSpace (%s) does not have any reference strLabel point %s, no update done" % (str(vsId), str(refAmer)))
            # should never happen
            return

        if {} == self.aGlobalVs:
            self.aGlobalVs = copy.deepcopy(self.aVss[vsId].aAmersPose6D)
            self.aAmersScore = copy.deepcopy(self.aVss[vsId].aAmersScores)
            self.aWayPoints[vsId] = self.aVss[vsId].aRobotPose6D
            if self.bDebug:
                logger.info("INF abcdk.topology.UpdateGlobalPosUsingAmer: global vector space is now equal to local vectorSpace %s (strLabel %s)" % (str(vsId), str(refAmer)))

            self.aRobotCurPos6d = self.aVss[vsId].aRobotPose6D
            return self.aGlobalVs

        if not(refAmer in  self.aGlobalVs):
            logger.error("Err abcdk.topology.UpdateGlobalPosUsingAmer:  Global VectorSpace does not have any reference strLabel point %s, no update done" % (str(refAmer)))
            # should never happen
            return
        else:
            refGlobalPose6D = self.aGlobalVs[refAmer]
            refLocalPose6D = self.aVss[vsId].aAmersPose6D[refAmer]

        for key, value in self.aVss[vsId].aAmersPose6D.iteritems():
            if key in self.aGlobalVs:
                if self.bDebug:
                    logger.info("key (%s) already in global" % (str(key)))
                scoreInLocal = self.aVss[vsId].aAmersScores[key]
                scoreInGlobal = self.aAmersScore[key]
                if self.bDebug:
                    logger.info("key (%s) already in global scoreInLocal %f, scoreInGlobal %f" % (str(key), scoreInLocal, scoreInGlobal))
                    #logger.info("Score in local (%s), score in global (%s)" % (str(scoreInLocal), str(scoreInGlobal)))
                if scoreInLocal > scoreInGlobal:
                    if self.bDebug:
                        logger.info("Keeping information from global")
                    continue

                if self.bDebug:
                    logger.info("using information from local")

            self.aGlobalVs[key] = computeGlobalObjectP6DUsingAmer(aP6DObjectLocal=value, aP6DPivotLocal=refLocalPose6D, aP6DPivotGlobal=refGlobalPose6D)
            self.aAmersScore[key] = self.aVss[vsId].aAmersScores[key]
            #boxObstacle = Obstacle3D(0.01, 0.8, 2.0, aPose6D=self.aGlobalVs[key])  # adding obstacle behind the datamatrix
            #self.addObstacle(boxObstacle)


            # we update current pos in global vector space based on pos in local VS
        localCurPose = self.aVss[vsId].aRobotPose6D
        newCurPose = computeGlobalObjectP6DUsingAmer(aP6DObjectLocal=localCurPose, aP6DPivotLocal=refLocalPose6D, aP6DPivotGlobal=refGlobalPose6D)
        self.aRobotCurPos6d = newCurPose
        if vsId >= 0:
            self.aWayPoints[vsId] = self.aRobotCurPos6d.copy()
        return self.aGlobalVs

    def updateTopology(self, option=None):
        """
        Update neighbors graph

        Use all the local Vs to update intra topological information (i.e connection between local Vector space)
        Args:
            option:
                - 'simple' : two vector space are linked only if they have been recorded consecutively
                - None : (default option) two Vector spaces are linked if there is an intersection (an amer) between them
        """
        # if option=='distance':
        #     for key in self.aWayPoints.keys():
        #         for key_sub in self.aWayPoints.keys():
        #             if key_sub != key:
        #                 if numeric.dist3D(self.aWayPoints[key], self.aWayPoints[key_sub]) < 2.0:
        #                     self.aNeighbors[key][key_sub] = 1  #on utilise un cout = 1
        if option is None:
            for key in self.aWayPoints.keys():
                self.aNeighbors[key] = {}
                for key_sub in self.aWayPoints.keys():
                    if key_sub != key:
                        if len(set(self.aVss[key].aAmersPose6D.keys()) & set(self.aVss[key_sub].aAmersPose6D.keys())) > 0:  # intersection non vide
                            self.aNeighbors[key][key_sub] = 1  # on utilise un cout = 1
                            #self.aNeighbors[key_sub] = {key:1}  #on utilise un cout = 1

        elif option == 'simple':
            ## TODO : a revoir
            for key in self.aWayPoints.keys():
                self.aNeighbors[key] = {}
                try:
                    self.aNeighbors[key][key + 1] = 1
                    if key > 0:
                        self.aNeighbors[key][key - 1] = 1
                except:
                    pass
        return self.aNeighbors

    def _computeRobotPoseUsingAmer(self, vs=None, refAmer=''):
        """
        Compute robot position in global VS using the robot position in a localVS and a specific amer (pivot).

        @param vs: a vector Space.
        @param refAmer: the amer to use in this vector space.
        return an array (Pose6D)
        """

        if not(refAmer in vs.aAmersPose6D):
            logger.error("ERR abcdk.topology._computeRobotPoseUsingAmer: Local VectorSpace (%s) does not have any reference strLabel point %s, no update done" % (str(vs), str(refAmer)))
            # should never happen
            return
        if {} == self.aGlobalVs:
            logger.error("Err abcdk.topology._computeRobotPoseUsingAmer: aGlobalVs is empty")
            return

        if not(refAmer in  self.aGlobalVs):
            logger.error("Err abcdk.topology._computeRobotPoseUsingAmer:  Global VectorSpace does not have any reference strLabel point %s, no update done" % (str(refAmer)))
            # should never happen
            return
        else:
            refGlobalPose6D = self.aGlobalVs[refAmer]
            refLocalPose6D = vs.aAmersPose6D[refAmer]
            localCurPose = vs.aRobotPose6D

            aRoboPos = computeGlobalObjectP6DUsingAmer(localCurPose, refLocalPose6D, refGlobalPose6D)
            return aRoboPos

    def computeLocalRobotPos(self, strAmerLabel, pose6D, bUseTempMap=True):
        ## TODO : this method should be deprecated.. but it's sometimes used.. TODO : a revoir
        tempVs = VectorSpace()
        tMap = TopologicalMap()  # << bien necessaire de recreer un objet?
        tMap.aGlobalVs = copy.deepcopy(self.aVss[self.nCurLocalVs].aAmersPose6D)
        tMap.aAmersScore = copy.deepcopy(self.aVss[self.nCurLocalVs].aAmersScores)
        tMap.aWayPoints[self.nCurLocalVs] = self.aVss[self.nCurLocalVs].aRobotPose6D
        tMap.aRobotCurPos6d = self.aVss[self.nCurLocalVs].aRobotPose6D
        tMap.addPoint6DToLocal(vs=tempVs, strLabel=strAmerLabel, aPose=pose6D)
        res = tMap._computeRobotPoseUsingAmer(vs=tempVs, refAmer=strAmerLabel)
        return res

    def computeRobotPos(self, strAmerLabel, pose6D, bUseTempMap=True):
        """
        Update and return the current position of robot using the information about the seen mark strAmerLabel (which has pose6D).

        Args:
            strAmerLabel: the name of the amer
            pose6D: the pose of the amer in robot reference
            bUseTemMap: a *fake* temporay vectorSpace is created  (to reuse merge vector space operation python code)
        returns:
            curPos: pose6D ([dx,dy,dz,dwX,dwY, dwZ])

            None if the amer was not found in the global map

        # TODO / NDEV / WARNING bUseTempMap = False.. show some errors !
        """
        if not(strAmerLabel in  self.aGlobalVs):
            logger.error("Err: Global map does not have any reference strLabel point named (%s), no position update done" % (str(strAmerLabel)))
            return None

        bUseTempMap = True
        if bUseTempMap:
            tempVs = VectorSpace()
            self.addPoint6DToLocal(vs=tempVs, strLabel=strAmerLabel, aPose=pose6D)
            if self.rMinConfidence is not None:
                self.removeAmersWithLowConfidence()
            res = self._computeRobotPoseUsingAmer(vs=tempVs, refAmer=strAmerLabel)
            return res

        else:
            ## TODO : corriger le code suivant..
            ## POUR l'instant toujours utiliser bUseTempMap = True
            amerPose6DInGlobal = self.aGlobalVs[strAmerLabel]
            aP6DRobot = numeric.changeReference(-pose6D, amerPose6DInGlobal)   # < -- ne fonctionne pas..  # feb 2014.. bah faire un -pose6D le pb semble venir de la non ?
            return aP6DRobot
            #dx, dy, dz, dwx, dwy, dwz = amerPose6DInGlobal
            ##newCurPose = amerPose6DInGlobal - pose6D
            #coordRobotInMarkReper = -pose6D
            #orientation, translation = numeric.chgRepereT(coordRobotInMarkReper[3:6], coordRobotInMarkReper[0:3], dx, dy, dz, dwx, dwy, dwz)
            #robotPose = np.array([translation[0], translation[1], translation[2], orientation[0], orientation[1], orientation[2]])

            #self.aRobotCurPos6d = robotPose
            #return self.aRobotCurPos6d

    def getMove(self, aDestPose6D, rMaxLenStep=0.40, bOriented=False, bRecomputePath=False):
        """
        return movements parameter to be used to get closer to the destination

        :param aFinalDestCoordinates: final destination
        :param rMaxLenStep: maximum distance allow for walk (in meters)
        :param bOriented: if True use the orientation of aFinalDestCoordinates
        :return:  collections.namedtuple('moveCmd', ['dx', 'dy', 'dtheta', 'theoriticalPose'])
        dx,dy,dtheta could be used directly to ALMotion.moveTo() call
        theoreticalPose is the end pose that should be reach if the motion move is done perfectly
        """
        bRecomputePath = bRecomputePath or np.any(aDestPose6D != self._aLastDestPose6D)
        self._aLastDestPose6D = aDestPose6D

        try:
            self.aNextWayPointsPose6D
            #print("path %s" % self.aNextWayPointsPose6D)
        except AttributeError:
            self.aNextWayPointsPose6D = []

        if numeric.dist2D(self.aRobotCurPos6d[:2], aDestPose6D[:2]) < rMaxLenStep:
            logger.info("Destination is close to current position, using destination point as the unique wayPoint")
            self.aNextWayPointsPose6D = [aDestPose6D]
        else:
            logger.info("Destination is far from current position, using path_planning to find next wayPoint")
            if bRecomputePath:
                print("recomputing path")
                self.aNextWayPointsPose6D = self.getNextWayPoints(aDestPose6D=aDestPose6D, rMaxLenStep=rMaxLenStep, bOriented=bOriented)
            else:
                print("Not recomputing path")
            logger.info("aNextWayPointsPose6D %s" % self.aNextWayPointsPose6D)
            if len(self.aNextWayPointsPose6D) < 1:
                logger.error("NO path found it could occurs if the movements is really too small (strange)")  # TODO ; inverstigate
                self.aNextWayPointsPose6D = [aDestPose6D]
                #assert(len(aNextWayPointsPose6D) >= 1)

        move, bDestinationReached = self._getMoveToTarget(self.aNextWayPointsPose6D[0], rMaxLenStep, bOriented=False)
        res = TopologicalMap.retMoveCmd(move.dx, move.dy, move.dtheta, move.theoriticalPose)
        if bDestinationReached:
            self.aNextWayPointsPose6D.pop(0)  # we pop it cause it has been consummed
        return res

    ### shortcut
    def getNextWayPoints(self, aDestPose6D, rMaxLenStep=0.4, bOriented=True):
        """
        Return the path to go to a pose6D destination using the current robot pose.

        bOriented: Not implemented right now TODO
        return:
            list of pose6D
        """
        aPath = []
        rMinLenStep = min(rMaxLenStep / 2.0, 0.1)
        aTargetP2D = getProjCoord(aDestPose6D)[:2]  # TODO : FIX laurent ici utiliser le plan qui correspond au plan du robot, pas forcement 0,0 mais bon..
        self.topologycalMap2D.aGoalPose2D = aTargetP2D
        aPath2D = self.topologycalMap2D.getPath2D(rMaxLenStep)
        logger.info("current pos2D %s" % self.topologycalMap2D.aCurPose2D)
        logger.info("dest pos 2D is %s " % str(aTargetP2D))
        logger.info("found path is %s" % aPath2D)
        logger.info("found motion path is %s" % aPath2D)

        for aPos2D in aPath2D:
            logger.info("Apose2d is %s" % str(aPos2D))
            aPose6D = np.array(self.aRobotCurPos6d, dtype=np.float)
            aPose6D[0] = aPos2D[0]  # TODO : faire une vrai projection ?
            aPose6D[1] = aPos2D[1]
            #logger.info(aPos2D[0])
            #logger.info aPose6D[0]
            if (numeric.dist2D(aPos2D, self.topologycalMap2D.aCurPose2D) > rMinLenStep):  # parfois on a un point qui est vraiment trop proche du point precedent.. resultat le robot reste bloque a un endroit ?? donc on verifie qu'on a bien un mouvement..
                aPath.append(aPose6D)

        return aPath

    ## TODO: urgent: Faire un autotest pour cette fonction !!!
    def _getMoveToTarget(self, aTargetP6D, rMaxDistance, bOriented=False):
        """
        return dx, dy, dtheta (in frame torso) to reach a target (based on the current pose). You can use this dx,dy,dtheta for motion commands.

        The function return the 'best' movements to do based on the rMaxDistance
        If bOriented is true orientation of targetPoint is used.
        else:
        if robot is close to dest : the orientation is the current orientation

        :param aTargetP6D: pose6D of the target
        :param rMaxDistance: max distance the robot can do
        :param bOriented: use the target orientation  WARNING: not implemented anymore TODO fix it
        :return: collections.namedtuple('move', ['dx', 'dy', 'dtheta', 'theoriticalPose'])
        """
        robot = self.aRobotCurPos6d.copy()
        aRobot = np.array(robot, dtype=np.float)
        if aTargetP6D is None:
            logger.info("SOMETHING wrong aTargetP6D = %s" % (aTargetP6D))
            return
        tPInFrameRobot = numeric.convertPoseWorldToTorso(aTargetP6D, aRobot)
        dx, dy = tPInFrameRobot[0], tPInFrameRobot[1]
        norm = numeric.norm2D(np.array([dx, dy]))
        if norm != 0:
            dx = numeric.getAbsMin((dx / norm) * rMaxDistance, dx)
            dy = numeric.getAbsMin((dy / norm) * rMaxDistance, dy)
        else:
            dx, dy = 0, 0
        if bOriented:
            dtheta = aTargetP6D[5] - self.aRobotCurPos6d[5]
            # logger.info("USING orrientation of aTargetP6D dtheta (%s) = aTargetP6D[5] (%s) - self.aRobotCurPos6d[5] (%s)" % (str(dtheta), str(aTargetP6D[5]), str(self.aRobotCurPos6d[5])))
        else:
            if numeric.dist2D(aTargetP6D[:2], self.aRobotCurPos6d[:2]) < 0.05:  # 0.15 cm -> pas de reorientation (c'est moche de tourner sur soit meme trop souvent)
                dtheta = 0  # # pas de direction on garde la direction 11111111
            else:
                dtheta = numeric.computeVectAngle(numeric.polarToCartesian(1, self.aRobotCurPos6d[5]), aTargetP6D[:2] - self.aRobotCurPos6d[:2])


        aMoves = _decomposeInRotationTranslation(dx, dy, dtheta)
        dx, dy, dtheta = aMoves[0]
        bDestinationReached = (len(aMoves) == 1)  # only one move is required/no decomposition
        # computing theoriticalPose :
        theoriticalPose = computePoseAfterMove(robot, dx, dy, dtheta)
        res = TopologicalMap.retMoveToTarget(dx, dy, dtheta, theoriticalPose)
        return res, bDestinationReached

    def isRelocalizationEasyPossibleHere(self, aRobotPose6D):
        """
        return True if the current location will allow to relocalize easily (near a mark), False otherwise
        """
        aSortedVisibleMark = self.sorteVisibleMark(aRobotPose6D)
        return bool(aSortedVisibleMark)  # an empty list is equivalent to boolean False

    def getBestLabel(self, targetPointPose6D, maxDistance=10, maxYaw=2.07, maxPitch=0.34):
        """
        return the bestDatamatrix to look at when the robot is at a specific position : targetPointPose6D
        Args:
        """
        aSortedVisibleMark = self.sorteVisibleMark(targetPointPose6D)
        if aSortedVisibleMark != []:
            logger.info("Best marks are %s" % aSortedVisibleMark)
            return aSortedVisibleMark[0][0]
        return None
        #bestDist = None
        #bestLabel = None
        #aRobotPose6D = targetPointPose6D
        #logger.info("INF abcdk.topology.getBestLabel(%s, maxDistance=%s, maxYaw = %s, maxPitch = %s" % (str(targetPointPose6D), str(maxDistance), str(maxYaw), str(maxPitch)))
        #
        #marksSorted = sorted(self.aGlobalVs.iteritems(), key=itemgetter(0), cmp=lambda indexA, indexB: cmp(numeric.dist3D(self.aGlobalVs[indexA], self.aRobotCurPos6d[:3]), numeric.dist3D(self.aGlobalVs[indexB], self.aRobotCurPos6d[:3])))
        #
        #for label, markPose6D in marksSorted:
        ##for strLabel, markPose6D in self.aGlobalVs.iteritems():
        #    (isNear, isViewable, distToLabel3D) = evaluateLabel(aRobotPose6D=aRobotPose6D, labelPose6D=markPose6D, maxDistance=maxDistance, maxYaw=maxYaw, maxPitch=maxPitch)
        #    logger.info("INF: strLabel: %s, isNear %s, isViewable %s, distToLabel3D %s",  label, isNear, isViewable, distToLabel3D)
        #
        #    if distToLabel3D > maxDistance:
        #        break  # pas la peine de continuer comme c'est triée par la distance..
        #    if ((bestDist is None) or (bestDist > distToLabel3D)) and isNear and isViewable:
        #        #bestDist = abs(distToLabel3D)
        #        bestLabel = label
        #        break
        #
        #return bestLabel

    def sorteVisibleMark(self, aRobotCurPos6d):
        """
        compute a list of visible marks and sorted them by visibility score
        """
        _rMinDistance = 0.10  # in meters
        _rMaxDistance = 2.50  # in meters
        _rAbsAlphaVertical = math.pi / 4.0
        _rAbsAlphaHorizontal = math.pi / 4.0
        _rAbsBetaHorizontal = math.pi * 2/3.0  # 120 degre
        _rAbsBetaVertical = 0.34  ## should maybee be increased a bit ?  ajouter 22 degrees TODO

        aVisibleMarksScore = []
        aCamPoseInRefRobot = _getCameraLookingFrontPose6DInRobotRef()
        aRobotPoseInRefCam = numeric.inversePose(aCamPoseInRefRobot)
        aCamPoseInRefWorld = numeric.changeReference(aCamPoseInRefRobot, aRobotCurPos6d)

        for strLabel, aMarkPose6D in self.aGlobalVs.iteritems():
            aMarkPose6D = np.copy(aMarkPose6D)
            aMarkPose6D[-1] = aMarkPose6D[-1] - math.pi  # we invert the direction here....  THERE IS SOMETHING WRONG IN OUR MAP... inverted somewhere..
            logger.info("%s pose6d is %s", strLabel ,aMarkPose6D)
            rDist = numeric.dist3D(aMarkPose6D[:3], aCamPoseInRefWorld[:3])
            if rDist < _rMinDistance:  # too close
                logger.debug('%s: too close (rDist is %s, whereas _rMinDistance is %s)' , strLabel, rDist, _rMinDistance)
                continue
            if rDist > _rMaxDistance:  # too far
                logger.debug('%s: too far (rDist is %s, whereas _rMaxDistance is %s)' , strLabel, rDist, _rMinDistance)
                continue

            # for alpha angles (angles done between mark orientation and robot pose3D)
            #aWorldPoseInRefMark = numeric.inversePose(aMarkPose6D)
            aMarkPoseInRobotRef = numeric.convertPoseWorldToFrameRobot(aMarkPose6D, aRobotCurPos6d)
            logger.debug("%s pos in robot ref is %s ", strLabel, aMarkPoseInRobotRef)
            aMarkPose6DInRefCam = numeric.changeReference(aMarkPoseInRobotRef, aRobotPoseInRefCam)
            logger.debug("%s pos in cam ref is %s ", strLabel, aMarkPose6DInRefCam)
            aCamPoseInRefMark = numeric.inversePose(aMarkPose6DInRefCam)
            ## juste pour test
            logger.debug(" cam pose in ref mark %s is %s ", strLabel, aCamPoseInRefMark)
            #rAlphaVertical =
            rAlphaVertical = -math.atan2(aCamPoseInRefMark[2], math.sqrt(aCamPoseInRefMark[0] ** 2 + aCamPoseInRefMark[1] ** 2))
            if abs(rAlphaVertical) > _rAbsAlphaVertical:
                logger.debug("%s: vertical alpha angle too big %s (max is %s)", strLabel, rAlphaVertical, _rAbsAlphaVertical )
                continue
            # rAlphaHorizontal
            rAlphaHorizontal = math.atan2(aCamPoseInRefMark[1], aCamPoseInRefMark[0])   # azimuth
            logger.debug("%s: horizontal alpha angle too big %s (max is %s)", strLabel, rAlphaHorizontal, _rAbsAlphaHorizontal )
            if abs(rAlphaHorizontal) > _rAbsAlphaHorizontal:
                logger.debug("%s: horizontal alpha angle too big %s (max is %s)", strLabel, rAlphaHorizontal, _rAbsAlphaHorizontal )
                logger.debug("aCamPoseInRefMark is %s", aCamPoseInRefMark)
                continue

            # for beta angles (angle done between robot orientation and mark pose3d)
            #aMarkPose6DInRefCam = numeric.inversePose(aCamPoseInRefRobot)
            rBetaVertical = -math.atan2(aMarkPose6DInRefCam[2], math.sqrt(aMarkPose6DInRefCam[0] ** 2 + aMarkPose6DInRefCam[1] ** 2))
            if abs(rBetaVertical) > _rAbsBetaVertical:
                logger.debug("%s: vertical beta angle too big %s (max is %s)", strLabel, rBetaVertical, _rAbsBetaVertical )
                continue

            rBetaHorizontal = math.atan2(aMarkPose6DInRefCam[1], aMarkPose6DInRefCam[0])   # azimuth
            if abs(rBetaHorizontal) > _rAbsBetaHorizontal:
                logger.debug("%s: horizontal beta angle too big %s (max is %s)", strLabel, rBetaHorizontal, _rAbsBetaHorizontal )
                continue

            ## score :
            def _score(val, maxVal):
                return 1 + abs(val)/maxVal

            rScore = _score(rAlphaHorizontal, _rAbsAlphaHorizontal) * _score(rBetaHorizontal, _rAbsBetaHorizontal) * _score(rDist, _rMaxDistance)
            aVisibleMarksScore.append((strLabel, rScore))

        aVisibleMarksScore.sort(key=lambda tup: tup[1])
        logger.info('dict with score is %s', aVisibleMarksScore)
        return aVisibleMarksScore

    def delAllAttractiveRegion(self):
        #for key in range(0, self.aAttractiveRegion._nIdx):
        for key in self._AttractiveRegionInFrontDatamatrix:
            self.delAttractiveRegion(key)
        self._AttractiveRegionInFrontDatamatrix = []

    def addAttractiveRegionInFrontOfDatamatrix(self):
        for key in self._AttractiveRegionInFrontDatamatrix:
            self.delAttractiveRegion(key)
        #    self._AttractiveRegionInFrontDatamatrix = []

        for k, aPose6D in self.aGlobalVs.iteritems():
            #import pdb
            #pdb.set_trace()
            nMaxVisibilityDistX = 1.00
            nMaxVisibilityDistY = 0.51  # max visibility dist when we are at nMaxVisibilityDistX/2 in axis X
            nMaxVisibilityDistZ = 10.01  # max visibility dist High when we are at nMaxVisibilityDistX/2 in axis X
            aP6DRegion3DInRefDatamatrixObject = np.array([-0.20 + -nMaxVisibilityDistX / 2.0,0,0,0,0,0])
            aP6DRegion3DInWorld = numeric.changeReference(aP6DRegion3DInRefDatamatrixObject, aPose6D)
            boxAttractiveRegion = Obstacle3D(nMaxVisibilityDistX, nMaxVisibilityDistY, nMaxVisibilityDistZ, aPose6D=aP6DRegion3DInWorld, rProbability=0.8)  # Maybee refactor.. TODO , and dont' use a rProbability here
            nIdx = self.addAttractiveRegion(boxAttractiveRegion)
            self._AttractiveRegionInFrontDatamatrix.append(nIdx)

    def addObstacleBehindEachDatamatrixMark(self):
        """
        add an obstable at the position of each datamatrix
        :return:
        """
        #import datamatrix_topology
        # import pdb
        # TODO optimization ne pas effacer les obstacles des anciennes datamatrix (a condition que la position soit la meme) mais juste rajouter les nouvelles
        try:
            for key in self._ObstacleBehindDatamatrix:
                self.delObstacle(key)

        except AttributeError:
            pass
        self._ObstacleBehindDatamatrix = []

        for k, aPose6D in self.aGlobalVs.iteritems():
            #boxObstacle = Obstacle3D(0.01, 0.8, 1.0, aPose6D=aPose6D)
            boxObstacle = Obstacle3D(0.01, 0.4, 2.0, aPose6D=aPose6D)
            nIdx = self.addStaticObstacle(boxObstacle)
            self._ObstacleBehindDatamatrix.append(nIdx)

    def addCubeObstacleInFrontOfRobotPosition(self, rXdist=0.1, rWidth=0.20, rHeight=3.0):
        """ add an obstacle at a specific position relative to current robot position
        it's just a shortcut

        rXdist: distance to obstacle in X axis frame robot
        rWidth: width of cube obstacle
        rHeight: height (1m seems to be good.. so obstacle is sure to cut the ground)
        """
        print("ADDING CUBE OBSTACLE in front of robot pos")
        aObstaclePose6DinWorld = numeric.convertPoseTorsoToWorld([rXdist,0,0,0,0,0], self.aRobotCurPos6d)
        boxObstacle = Obstacle3D(rWidth, rWidth, rHeight, aPose6D=aObstaclePose6DinWorld)
        boxObstacle._rProbability = 0.02
        self.addObstacle(boxObstacle)
        print("adding done")

    def addCubeObstacleBetweenTwoPosition6D(self, rWidth=0.20, rLength=0.20, rHeight=3.0, aPose6DA=None, aPose6DB=None):
        """
        add an obstacle between two 6D position, the obstacle pos3D correspond
        to the computeBarycenter between the two points, it's orrientation is equal to the orientation of aPose6DB

        @param aPose3DA: np.array, 6D
        @param aPose3DD: np.array, 6D
        """
        if aPose6DA is None or aPose6DB is None:
            logger.error("Pose6D is none : aPose6DA %s, aPose6DB %s" % (aPose6DA, aPose6DB))
            return
        aObstaclePose6D = np.zeros(6)
        aObstaclePose6D[:3] = numeric.computeBarycenter([aPose6DA[:3], aPose6DB[:3]])
        aObstaclePose6D[3:] = aPose6DB[3:]   # for orientation of obstacle we use orientation of the second point
        ## TODO : l'orientation du cube n'est pas bonne il faut la calculer a partir des vecteurs..
        return self.addCubeObstacleAtPose6D(rWidth, rLength, rHeight, aObstaclePose6D)
    ## TODO : appellere cette methode

    def addCubeObstacleAtPose6D(self, rWidth, rLength, rHeight, aPose6D):
        logger.info("adding obstacle at %s" % aPose6D)
        boxObstacle = Obstacle3D(rWidth, rWidth, rHeight, aPose6D=aPose6D)
        boxObstacle._rProbability = 0.02
        self.addObstacle(boxObstacle)

    def addStaticObstacle(self, aObstacle3D):
        aObstacle3D._rProbability = 0.9  # static obstacle have a high _rProbability
        return self.addObstacle(aObstacle3D=aObstacle3D, rTTL=-1)

    def addAttractiveRegion(self, aRegion3D):
        """
        add a region in the attractiveRegion 3D dictionary (it also add it to 2D map)
        """
        try:
            nIdx = self.aAttractiveRegion.addObstacle(aRegion3D)
        except AttributeError:
            self.aAttractiveRegion = ObstaclesContainer()
            nIdx = self.aAttractiveRegion.addObstacle(aRegion3D)

        self.topologycalMap2D.addAttractiveRegion(aRegion3D, nIdx)  # we share same idx for 3D and 2D for convenience purpose
        return nIdx

    def addObstacle(self, aObstacle3D=None, rTTL=40):
        nIdx = self.aObstacles.addObstacle(aObstacle3D)
        #logger.info("NEW OBSTACLE _rProbability %s" % aObstacle3D._rProbability)
        self.topologycalMap2D.addObstacle2D(aObstacle3D, nIdx)
        return nIdx

    def delObstacle(self, nObstacleIdx):
        self.topologycalMap2D.delObstacles2D(nObstacleIdx)
        self.aObstacles.delObstacle(nObstacleIdx)

    def delAttractiveRegion(self, nObstacleIdx):
        self.topologycalMap2D.delAttractiveRegion2D(nObstacleIdx)
        try:
            self.aAttractiveRegion.delObstacle(nObstacleIdx)
        except KeyError:
            logger.error("No key %s" % nObstacleIdx)

    def delAllObstacles(self):
        aKeysToDelete = self.aObstacles.aObstacles.keys()
        for key in aKeysToDelete:
            self.delObstacle(key)
        self._ObstacleBehindDatamatrix = []

# class TopologicalMap - end

class TopologicalMap2D(object):  # the name topological map.. is maybee not good.. it's a navigation map not a topologicalmap
    def __init__(self):
        self._aOriginPose2D = np.zeros(2)  # fixed
        self._aCurPose2D = np.zeros(2)
        self._aGoalPose2D = np.zeros(2)
        self._aObstacles2D = {}  # dict of 2D polygons that represent obstacles
        self.aAttractiveRegion2D = {}  # dict of 2D region (2Dpolygons + .rProbability) that represent attractiveRegion

    @property
    def aCurPose2D(self):
        return self._aCurPose2D

    @aCurPose2D.setter
    def aCurPose2D(self, aPose2D):
        #logger.info("Apos2d is %s" % aPose2D)
        self._aCurPose2D = aPose2D

    @property
    def aGoalPose2D(self):
        return self._aGoalPose2D

    @aGoalPose2D.setter
    def aGoalPose2D(self, aPose2D):
        self._aGoalPose2D = aPose2D

    @property
    def aObstacles2D(self):
        return self._aObstacles2D

    def addAttractiveRegion(self, region3D, nRegionId):
        """
        Add an attractiveRegion to the 2D map

        :param region 3D: an object with attribute: ._rProbability, ._rTimestamp and .aPolygon2D (which is a list of 3D positions)
        and a method get2DPolygon which returns a 2D polygon
        :param nRegionId: an unique id for the region
        """
        try:
            if (None != self.aAttractiveRegion2D.pop(nRegionId, None)):
                logger.info("INF addObstacle2D, object with same id (%s) already presented in dictionary, overwriting it" % nRegionId)
        except AttributeError:
            self.aAttractiveRegion2D = dict()

        polygon2D = region3D.get2DPolygon()
        if polygon2D is None:
            logger.info("INF addObstacle2D: obstacle not crossing the 2D plane")
            return
        self.aAttractiveRegion2D[nRegionId] = Obstacle2D(polygon2D, rProbability=region3D._rProbability, rTimestamp=region3D._rTimestamp)

    def delAttractiveRegion2D(self, nObstacleId):
        aObstacle2D = self.aAttractiveRegion2D.pop(nObstacleId, None)
        if aObstacle2D is None:
            logger.info("INF delAttraciveRegion2D: can't delete item with id (%s), not present in the dict" % nObstacleId)

    def addObstacle2D(self, obstacle3d, nObstacleId):
        """
        add an obstacle to the 2D map using a 3D obstacle
        aObstacle2D : a list of 2D points that constitute a polygon
        """
        if (None != self.aObstacles2D.pop(nObstacleId, None)):
            logger.info("INF addObstacle2D, object with same id (%s) already presented in dictionary, overwriting it" % nObstacleId)

        polygon2D = obstacle3d.get2DPolygon()
        if polygon2D is None:
            logger.info("INF addObstacle2D: obstacle not crossing the 2D plane")
            return
        self.aObstacles2D[nObstacleId] = Obstacle2D(polygon2D, rProbability=obstacle3d._rProbability, rTimestamp=obstacle3d._rTimestamp)

    def delObstacles2D(self, nObstacleId):
        aObstacle2D = self.aObstacles2D.pop(nObstacleId, None)
        if aObstacle2D is None:
            logger.info("INF delObstacles2D: can't delete item with id (%s), not present in the dict" % nObstacleId)

    def getPath2D(self, rMaxDistance, rResolution=0.15):
        """
        return the list of next pose2D to reach the desired _goalPose2D
        """
        aCorners = [[-20,-20], [-20,20], [20,20], [20,-20]]  # TODO : fix it.. should be determined automaticly
        rD = 20
        aCorners = [[-rD,-rD], [-rD, rD], [rD,rD], [rD,-rD]]  # TODO : fix it.. should be determined automaticly
        planner = path_planner.GridOccupancyMapPlanner(rResolution, aStartPos2D=self.aCurPose2D, aGoalPos2D=self._aGoalPose2D, aCSpaceCorners=aCorners, aObstaclesPolygons=self.aObstacles2D, aAttractiveRegion=self.aAttractiveRegion2D)
        planner.updatePath()
        planner.updateMotionPath(rMaxStepDist=rMaxDistance)
        #aPath = planner._aPath
        aPath = planner.aMotionPath
        #logger.info("INF: abcdk.TopologicalMap2DgetPath2D: returned path is %s" % (aPath))
        return aPath

# class TopologicalMap2D - end

class ObstaclesContainer(object):
    def __init__(self):
        self._aObstacles = dict()
        self._nIdx = 0

    @property
    def aObstacles(self):
        return self._aObstacles

    def addObstacle(self, obstacle):
        self._nIdx += 1
        self._aObstacles[self._nIdx] = obstacle
        logger.info(self._aObstacles)
        return self._nIdx

    def delObstacle(self, nIdx):
        self._aObstacles.pop(nIdx)

    def iteritems(self):
        return self._aObstacles.iteritems()

# class ObstaclesContainer - end

class Obstacle(object):
    def __init__(self, rProbability=0.1, rTimestamp=None):
        self._rProbability = rProbability
        #logger.info("rProb is %s" % self._rProbability)
        if rTimestamp is None:
            self._rTimestamp = time.time()
        else:
            self._rTimestamp = rTimestamp

    @property
    def rProbability(self):
        #logger.info("rProbability is %s" % self._rProbability)
        return self._rProbability

# class Obstacle - end

class Obstacle2D(Obstacle):
    def __init__(self, aObstacle2D, **kwargs):
        super(Obstacle2D, self).__init__(**kwargs)
        #super(Obstacle2D, self).__init__(rProbability=rProbability, rTimestamp=rTimestamp)
        self._aPolygon2D = aObstacle2D

    @property
    def aPolygon2D(self):
        return self._aPolygon2D

    @aPolygon2D.setter
    def aPolygon2D(self, aPolygon2D):
        self._aPolygon2D = aPolygon2D

    @property
    def rProbability(self):
        #logger.info("rProbability is %s" % self._rProbability)
        return self._rProbability

# class Obstacle2D - end

class Obstacle3D(Obstacle):
    """
    An object that represent a rectangular obstacle (in fact it's more a cuboid
    than a rectangle).
    """

    def __init__(self, rLengthX, rLengthY, rLengthZ, aPose6D=None, **kwargs):
        """
        @param rLengthX: length of obstacles in meters (X)
        @param rLengthY: width of obstacles in meters  (Y)
        @param rLengthZ: height of obstacles in meters (Z)
        @param aPose6D: center of mass pose6D
        """
        super(Obstacle3D, self).__init__(**kwargs)
        self._rLengthX = rLengthX
        self._rLengthY = rLengthY
        self._rLengthZ = rLengthZ
        self._aPose6D = aPose6D

    def getVertex(self):
        if self._aPose6D is not None:
            return numeric.getVertexCuboid(self._aPose6D, self._rLengthX, self._rLengthY, self._rLengthZ)

    def get2DPolygon(self, planePt=np.array([0,0,0]), planeNormalVector=np.array([0,0,1])):
        """
        return the polygon that is the interesction on the plane and the cuboid
        """
        return numeric.get2DPolygonProjection(planePt, planeNormalVector, self.getVertex())
# class Obstacle3D - end

if __name__ == "__main__":
    pass
    # for autoTests see tests/test_topology.py
    #test_fakeMap()
