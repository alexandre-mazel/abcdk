# -*- coding: utf-8 -*-
## TTTTTTTTTTTTTTTTTTT : trier par luminosité proche pour les cercles
### tester sur un robot
###########################################################
# Aldebaran Behavior Complementary Development Kit
# Topology tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################
"""
@Title: object pose estimation tools and goToPod methods
@author: lgeorge@aldebaran-robotics.com
"""
from __future__ import print_function
print( "importing abcdk.imagePnp" );

import collections
import numpy as np
import cv2
#import config
#config.bInChoregraphe = False

import multiprocessing
import numeric
import camera
import image
import math
import sound

# ---------------------------------------- Useful functions --------
# These bunch of function should maybee be moved to numeric.
def colinear(a,b,c):
    x1, y1 = a[0], a[1]
    x2, y2 = b[0], b[1]
    x3, y3 = c[0], c[1]
    aligned = abs((y1 - y2) * (x1 - x3) - (y1 - y3) * (x1 - x2))
    return aligned

# ---------------------------------------- PNP resolution functions --------
def PnPransac(q, realObjectPts, imgPts, cameraMatrix, distorsionCoef, iteration=100):
    """ embeded solvePnPRansac call to be used with multiprocessing.. and to
    become segfault tolerant """
    res = cv2.solvePnPRansac(realObjectPts, imgPts, cameraMatrix, distorsionCoef, iterationsCount=iteration, flags=cv2.CV_P3P)
    if q!=None:
        q.put(res)
    else:
        return res

def PnP(q, realObjectPts, imgPts, cameraMatrix, distorsionCoef):
    """ embeded solvePnP call to be used with multiprocessing.. and to
    become segfault tolerant """

    #cameraMatrix = np.array([[1.3e+03, 0., 6.0e+02], [0., 1.3e+03, 4.8e+02], [0., 0., 1.]], dtype=np.float32)
    #distorsionCoef = np.array([-2.4-01, 9.5e-02, -4.0e-04, 8.9e-05, 0.], dtype=np.float32)
    res = cv2.solvePnP(realObjectPts, imgPts, cameraMatrix, distorsionCoef) # itterative..
    #imgPts = np.reshape(imgPts, (4, 1, 2))
    #realObjectPts = np.reshape(realObjectPts, (5,1,2))
    #res = cv2.solvePnP(realObjectPts, imgPts, cameraMatrix, distorsionCoef, flags = cv2.CV_EPNP)
    #res = cv2.solvePnP(realObjectPts, imgPts, cameraMatrix, distorsionCoef, flags = cv2.CV_EPNP)
    #res = cv2.solvePnP(realObjectPts, imgPts, cameraMatrix, distorsionCoef, flag = 1)
    ## la methode EPNP semble la plus efficace dans notre cas.. a verifier..
    #res = cv2.solvePnP(realObjectPts, imgPts, cameraMatrix, distorsionCoef, flags = cv2.CV_P3P)
    if q != None:
        q.put(res)
    else:
        return res

def getPNP(impts, realpts, debug=False, resolution=camera.camera.k4VGA):
    """
    deprecated please use getPnP . Here for no api breakage
    @param impts:
    @param realpts:
    @param debug:
    @param resolution:
    @return:
    """
    return getPnP(impts, realpts, bDebug=debug, nResolution=resolution, bUseRansac=False)

retPnp = collections.namedtuple('PerspectiveRelativeToCam',
                                ['orientation', 'translation', 'projectedImPts', 'opencvPnpR', 'opencvPnpT'])
def getPnP(aImPts, aRealPts, bDebug=False, nResolution=camera.camera.k4VGA, bUseRansac=False):
    """ Estimate the pose of an object using OpenCV solvePnp.

    Estimate the pose (orientation and position) of an object using the
    coordinate of the viewed objects. 4 points are required (more is better).
    The object point should be known (i.e. measurement between the different
    points/corners etc..)

    I len(imPts) == len(realPts) : cv2.solvePnP is used
    If len(imPts) > len(realPts) : cv2.solvePnPRansac is used
    if bUseRancac is set, cv2.solvePnPRansac is used.

    @param aImPts: coordinates of object in image points (i.e pixels)
    @param aRealPts: coordinates of object in object coordinates (i.e in meters)
    @param bDebug: enable debugging information
    @param nResolution: camera.camera.k4VGA,VGA, etc. (used to know which camera matrix/distortion to use)
    @param bUseRansac: if enabled use Ransac algorithm
    @return: collections.namedtuple('PerspectiveRelativeToCam', ['orientation', 'translation', 'projectedImPts',
                                    'opencvPnpR', 'opencvPnpT'])
        with:
        - orientation = dWx, dWy, dWz (rotation around axis x, y and z) in naoqi orientation
        - translation = dx, dy, dz (translation on axis x, y and z)
        - projectImPts = projections of points using the translation/orientation
        - opencvPnpR: rotation in OpenCV coordinate system
        - opencvPnpT: translation in OpenCV coordinate system

    None is returned if something went wrong (i.e segfault or wrong reprojected points to far from aImgPts)
    """
    aCameraMatrix = camera.camera.aCameraMatrix[nResolution]
    aDistorsionCoefs = camera.camera.distorsionCoef

    if len(aImPts) < len(aRealPts) or len(aRealPts) < 4:
        print("Not enought points")
        return  # NDEV: raise error

    realObjectPts = np.array(aRealPts, dtype='float32')
    imgPts = np.array(aImPts, dtype='float32')
    bUseMultiProcessing = False
    if bUseMultiProcessing:
        queue = multiprocessing.Queue()

    if len(aImPts) == len(aRealPts) or not(bUseRansac):
        bUsingPnpRansac = False
        #if bDebug:
            #print("USING pnp")
        if bUseMultiProcessing:
            p = multiprocessing.Process(target=PnP, args=(queue, realObjectPts, imgPts, aCameraMatrix, aDistorsionCoefs))
        else:
            pnpOpencv = PnP(None, realObjectPts, imgPts, aCameraMatrix, aDistorsionCoefs)
    else:
        bUsingPnpRansac = True
        #if bDebug:
        #    print("USING pnpRansac")
        if bUseMultiProcessing:
            p = multiprocessing.Process(target=PnPransac,
                                        args=(queue, realObjectPts, imgPts, aCameraMatrix, aDistorsionCoefs))
        else:
            pnpOpencv = PnPransac(None, realObjectPts, imgPts, aCameraMatrix, aDistorsionCoefs)

    if bUseMultiProcessing:
        p.start()
        p.join(1)  # block until finish.. or timeout = 1s

        try:
            pnpOpencv = queue.get_nowait()
        except Exception, e:
           # if bDebug:
            print("PNP segfault, return None")  # it already have happens (maybe in old version of OpenCV?)
            args=(queue, realObjectPts, imgPts , aCameraMatrix, aDistorsionCoefs)
            import serialization_tools
            import filetools
            import pathtools
            serialization_tools.saveObjectToFile(args, pathtools.getVolatilePath() + filetools.getFilenameFromTime())
            return None

    if len(pnpOpencv) >= 3:  # depends to OpenCV version
        if bUsingPnpRansac:
            res = np.array(pnpOpencv[0:2])
        else:
            res = np.array(pnpOpencv[1:])
    else: # otherwise
        res = pnpOpencv
    orientation = np.array([res[0][2], -res[0][0], -res[0][1]]).flatten()
    orientation = np.array([res[0][2], -res[0][0], -res[0][1]]).flatten()
    translation = np.array([res[1][2], -res[1][0], -res[1][1]]).flatten()
    aProjectedPts = cv2.projectPoints(realObjectPts, res[0], res[1], aCameraMatrix, aDistorsionCoefs)[0]

    res = retPnp(orientation, translation, aProjectedPts, res[0], res[1])

    if not(np.allclose(aImPts, aProjectedPts[:, 0], atol=2)):
        if not(np.allclose(aImPts, aProjectedPts[:, 0], atol=4)):
            ## PNP projected point is not close to the image point.. we don't return the result
            print("imagePnp: Warning projected points not close to imagePoints.. returning None")
            print("aImPts %s" % str(aImPts))
            print("projected pts %s" % str(aProjectedPts))
            print("imagePnp: Warning projected points not close to imagePoints.")
            return None
        try:
            sound.playSound( "bip_error.wav" );  # beep in case project points a bit far but not too much
        except:
            pass

    return res

def draw3DSquare(pnp, nResolution):
    """
    Draw the orientation of a square
    @param pnpRes: result of getPnP  (collections.namedtuple('PerspectiveRelativeToCam', ['orientation', 'translation', 'projectedImPts', 'opencvPnpR', 'opencvPnpT']))
    @param nResolution: resolution of image
    @return: a coloured image with only the 3D view
    """
    height, width = image.getResolutionFromEnum(nResolution)
    colouredImg = np.zeros((width,height, 3), np.uint8)
    axis = np.float32([[-1,-1,0], [-1,1,0], [1,1,0], [1,-1,0], [-1,-1,-3],[-1,1,-3],[1,1,-3],[1,-1,-3] ])/100
    aImgPts, jac = cv2.projectPoints(axis, pnp.opencvPnpR, pnp.opencvPnpT, camera.camera.aCameraMatrix[3], camera.camera.distorsionCoef)
    #debugImg = draw3D(colouredImg, None, pnp.projectedImPts[:4], aImgPts)
    debugImg = draw3D(colouredImg, None, pnp.projectedImPts, aImgPts)
    return debugImg

def draw3D(colouredImg, corners, projectedCorners, imgPts, distance=None):
    """ draw debug information assiociated to the pnp solution

    ARGS:
        img: coloured image
        corners: 4 points in image coordinate (corners of the rectangle provided by datamatrix for instance)  (Warning : sometimes it could be None for instance for the pod)
        projectedCorners: result of reprojection thx to pnp rvect and tvect
        imgPts: projected 3D points in image space of a square to show the normal for instance
        (axis = np.float32([[-1,-1,0], [-1,1,0], [1,1,0], [1,-1,0], [-1,-1,-3],[-1,1,-3],[1,1,-3],[1,-1,-3] ])/100)

    returns the coloured image with the different draw
    """
    projectedCorners = np.int32(projectedCorners)
    imgPts = np.int32(imgPts).reshape(-1, 2)

    # draw ground floor in green
    cv2.drawContours(colouredImg, [imgPts[:4]], -1, (0, 255, 0, 0.9), -3)
    cv2.drawContours(colouredImg, [projectedCorners], -1, (0, 255, 255, 0.9), 0)
    if corners!=None:
        corners = np.int32(corners)
        cv2.drawContours(colouredImg, [corners], -1, (0, 255, 0, 0.9), 0)
    if distance!=None:
        np.set_printoptions(precision=3)
        text = 'Pod dist: {:.2f}'.format(distance) + " m"
        cv2.putText(colouredImg, '{:.2f}'.format(distance) + "m", (projectedCorners[0][0][0], projectedCorners[0][0][1]), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,200,50))
        #cv2.cvAddText(colouredImg, text, (projectedCorners[0][0][0], projectedCorners[0][0][1])
        #cv2.putText(colouredImg, 'Pod dist: {:.2f}'.format(distance) + " m", (0, 0), cv2.FONT_HERSHEY_COMPLEX, 1, (0,200,50))

    for i, j in zip(range(4), range(4, 8)):
        cv2.line(colouredImg, tuple(imgPts[i]), tuple(imgPts[j]), (255), 3)
    cv2.drawContours(colouredImg, [imgPts[4:]], -1,(0, 210, 255), 3)

    return colouredImg

matrixName = 'not_set_'
num = 0

def _getPnpDataMatrix(dataMatrixTrapeze, nResolution, dataMatrixRealSize, bDebug=False, strDebugFname='/home/nao/debug_out.jpg'):
    """
    return pose estimation (see getPnP), for a square datamatrix. Corners points are refined using opencv Corner subpix
    @param dataMatrixTrapeze: 6Points refined corners
    @param nResolution:
    @param dataMatrixRealSize:
    @param bDebug:
    @param strDebugFname:
    @return:
    """
    import traceback
    try:
        realWidth = np.sqrt((dataMatrixRealSize** 2) /2.0)
        realHeight = realWidth
        a = np.array([-0.5 * realWidth, -0.5 * realHeight, 0])
        b = np.array([-0.5 * realWidth, 0.5 * realHeight, 0])
        #c = np.array([0.5 * realWidth, 0.5 * realHeight, 0])
        d = np.array([0.5 * realWidth, -0.5 * realHeight, 0])
        e = np.array([0.4*realWidth, 0.4*realHeight, 0], dtype=np.float)  # corner of bottom/right point
        f = np.array([0.0, 0.5*realHeight, 0.0], dtype=np.float)  # middle of bottom ( the inside corner)
        g = np.array([0.5*realWidth, 0.0, 0.0], dtype=np.float)  # middle of right (the inside corner)

        aRealPts = np.array([a, b, f, e, g, d])
        imPts = np.array(dataMatrixTrapeze, dtype='float32')

        pnpOpencv = getPnP(imPts, aRealPts, bDebug=bDebug, nResolution=nResolution)
        #print(pnpOpencv)
        if pnpOpencv == None:
            print("ERR: abcdk.nav_mark._getPnpDatamatrix(): pnp.. none..")
            return
        #print("datamatrix pos: \n Frame Cam: \n Orientation: %s \n Pos: %s \n Frame Torso: \n Orientation: %s \n Pos: %s \n" % (str(pnpOpencv.orientation), str(pnpOpencv.translation), str(orientationFrameTorso), str(translationFrameTorso)))
        #ret = collections.namedtuple('PerspectiveRelativeToCam', ['orientation', 'translation', 'projectedImPts', 'opencvPnpR', 'opencvPnpT'])
#        if True:
        if bDebug:
            height, width = image.getResolutionFromEnum(nResolution)
            colouredImg = np.zeros((width,height, 3), np.uint8)
            axis = np.float32([[-1,-1,0], [-1,1,0], [1,1,0], [1,-1,0], [-1,-1,-3],[-1,1,-3],[1,1,-3],[1,-1,-3] ])/100
            imgPts, jac = cv2.projectPoints(axis, pnpOpencv.opencvPnpR, pnpOpencv.opencvPnpT, camera.camera.aCameraMatrix[3], camera.camera.distorsionCoef)
            debugImg = draw3D(colouredImg, dataMatrixTrapeze, pnpOpencv.projectedImPts, imgPts)
            ## TODO : a virer pour debug only
            import time
            cv2.imwrite(strDebugFname, debugImg)
            print("Saving debug pnp to %s" % fName)
            num += 1


        return pnpOpencv
        #return ret(orientationFrameTorso, translationFrameTorso)
    except:
        return traceback.format_exc()

retPoseToCam = collections.namedtuple('poseRelativeToCam', ['orientation', 'translation'])
retPoseToTorso = collections.namedtuple('poseRelativeToTorso', ['orientation', 'translation'])
def getPose(dataMatrixTrapeze, imageInfo, dataMatrixRealSize, frame='Robot', bDebug=False):
    """
    return pose estimation in corresponding frame
    # Warning this function is for datamatrix only !!! please use getPnP directly for other purpose

    Args:
     //   datamatrixTraepeze: a list of 4 points (corners of the datamatrix)
     apiBreakage.. now dataMatrixTrapeze -> 6Points.. (refined corners)
        imageInfo: a structur with .nResolution = resolution, .cameraPosInFrameTorso : position of cam in frameTorso

    """
    pnpOpencv = _getPnpDataMatrix(dataMatrixTrapeze, imageInfo.nResolution, dataMatrixRealSize, bDebug=bDebug)
    #print("pnpOpencv is.. %s" % pnpOpencv)
    if pnpOpencv != None:
    #print("pnpOpencv %s" % str(pnpOpencv))
        if frame == 'Cam':
            return retPoseToCam(pnpOpencv.orientation, pnpOpencv.translation)
        if frame == 'Torso':
            dx, dy, dz, dwx, dwy, dwz = imageInfo.cameraPosInFrameTorso
        #    print("tranlation cam to torso :%s " % (str([dx,dy,dz])))
            orientationFrameTorso, translationFrameTorso = numeric.chgRepereT(pnpOpencv.orientation, pnpOpencv.translation, dx, dy, dz, dwx, dwy, dwz)
            return retPoseToTorso(orientationFrameTorso, translationFrameTorso)
        if frame == 'Robot':
            dx, dy, dz, dwx, dwy, dwz = imageInfo.cameraPosInNaoSpace
            #    print("tranlation cam to torso :%s " % (str([dx,dy,dz])))
            orientationFrameRobot, translationFrameRobot = numeric.chgRepereT(pnpOpencv.orientation, pnpOpencv.translation, dx, dy, dz, dwx, dwy, dwz)
            return retPoseToTorso(orientationFrameRobot, translationFrameRobot)


#def debugPlot(orientation, translation):
#    """
#    plot the pod with specific orientation, and a specific position (translation) relative to robot (camera, or torso)
#    """
#    def plotibis(orientation, translation, usemayavi = False, usepylab = True):
#        x,y,z = translation
#        normVectXorig = [1,0,0]
#        normVectYorig = [0,1,0]
#        normVectZorig = [0,0,1]
#        pod_shape = (0.1,0.1,0)
#
#        Y = np.linspace(-pod_shape[0]/2, pod_shape[0]/2, 100)
#        Z = np.linspace(-pod_shape[1]/2, pod_shape[1]/2, 100)
#        X = np.zeros((np.size(Y), np.size(Z)))
#        #Z = np.zeros((np.size(X), np.size(Y)))
#
#        Y, Z = np.meshgrid(Y, Z)
#        newCoords = np.array([X, Y, Z])
#        oldCoords = newCoords.copy()
#
#        # rotation :
#        dWX, dWY, dWZ = np.array(orientation)
#        rotMatX = np.array([[1,0,0],[0,np.cos(dWX), -np.sin(dWX)], [0, np.sin(dWX), np.cos(dWX)]])
#        rotMatY = np.array([[np.cos(dWY), 0, np.sin(dWY)], [0, 1, 0], [-np.sin(dWY), 0, np.cos(dWY)]])
#        rotMatZ = np.array([[np.cos(dWZ), -np.sin(dWZ), 0], [np.sin(dWZ), np.cos(dWZ), 0], [0, 0, 1]])
#        newCoords = np.tensordot(rotMatX, newCoords, 1)
#        newCoords = np.tensordot(rotMatY, newCoords, 1)
#        newCoords = np.tensordot(rotMatZ, newCoords, 1)
#        normVectXTrans = (np.dot(rotMatX, normVectXorig)).tolist()
#        normVectYTrans = (np.dot(rotMatY, normVectYorig)).tolist()
#        normVectZTrans = (np.dot(rotMatZ, normVectZorig)).tolist()
#        print np.array(normVectXorig).shape
#        print (normVectXTrans)
#        print (normVectYTrans)
#        print (normVectZTrans)
#
#        newCoords[0,:] += translation[0]
#        newCoords[1,:] += translation[1]
#        newCoords[2,:] += translation[2]
#
#        if usepylab:
#            import matplotlib.pyplot as plt
#            fig = plt.figure()
#            ax = fig.add_subplot(111, projection='3d')
#            #ax.plot_surface(oldCoords[0], oldCoords[1], oldCoords[2], color='r')
#            #ax.plot_surface(newCoords[0], newCoords[1], newCoords[2], shade=True, rstride=100, cstride=1000, color='r') #cmap=plt.cm.coolwarm, linewidth=0.2)
#            ax.plot_surface(newCoords[0], newCoords[1], newCoords[2],color='r') # rstride=100, cstride=1000, color='r') #cmap=plt.cm.coolwarm, linewidth=0.2)
#            #ax.scatter([translation[0]], [translation[1]], [translation[2]], c='g')
#            #ax.auto_scale_xyz([0, 1.5], [-0.5, 0.5], [-0.5, 0.5])
#            ax.auto_scale_xyz([0, 1.0], [-0.5, 0.5], [-0.5, 0.5])
#            ax.view_init(elev=0., azim=-180)
#            plt.axis('equal') # orthonormal axis
#            plt.show()
#
#        if usemayavi:
#            import mayavi.mlab as mlab
#            mlab.mesh(oldCoords[0], oldCoords[1], oldCoords[2], color=(0.2,0.2,0.2))
#            mlab.mesh(newCoords[0], newCoords[1], newCoords[2], color=(0.7,0.7,0.7))
#           # mlab.quiver3d(translation[0], translation[1], translation[2], arc)
#            mlab.quiver3d(0, 0, 0, normVectXorig[0], normVectXorig[1], normVectXorig[2], color=(1,0,0))
#            mlab.quiver3d(0, 0, 0, normVectYorig[0], normVectYorig[1], normVectYorig[2], color=(0,1,0))
#            mlab.quiver3d(0, 0, 0, normVectZorig[0], normVectZorig[1], normVectZorig[2], color=(0,0,1))
#
#           # mlab.quiver3d(x, y, z, normVectXTrans[0], normVectXTrans[1], normVectXTrans[2], color=(1,0,0))
#           # mlab.quiver3d(x, y, z, normVectYTrans[0], normVectYTrans[1], normVectYTrans[2], color=(0,1,0))
#           # mlab.quiver3d(x, y, z, normVectZTrans[0], normVectZTrans[1], normVectZTrans[2], color=(0,0,1))
#
#            mlab.show()
#
#
#    print "drawing.."
#    plotibis(orientation, translation)
#    print "done"

retGetPoseMove = collections.namedtuple('poseMove', ['version', 'moveX', 'moveY', 'moveZ', 'rotationTorso', 'afterMoveObjPos'])
def getPoseMove(objTranslation, objOrientation, x=0, y=0, z=0, torsoOrientation=math.pi, thresholdMove = 0.15):
    """ Compute movement orders and rotation to go to the point x,y,z relatively to the object pose (objTranslation, objOrientation)

    Args:
        objTranslation: object position
        objOrientation: object orientation
        x y z: distance to object on x,y,z axis (unit : meter)
        torsoOrientation: orientation of the torso versus the object orientation
        if None, we use the direction to the pod for the orientation
        thresholdMove: maximum distance on x and y to use for the movement (unit: meter)

    Returns:
        namedTuple: ['version', 'moveX', 'moveY', 'moveZ', 'rotationTorso', 'afterMoveObjPos']
        afterMoveObjPos: position of object after movement (x,y,z) no orientation provided TODO?

    # example of usage and return:
    >>> getPoseMove( [3,4,0], [0,0,math.pi], 0, 0, 0, 0)
    poseMove(version=0.1, moveX=-3, moveY=-4, moveZ=0, rotationTorso=3.141592653589793, afterMoveObjPos=[0, 0, 0])
    >>> getPoseMove( [3,4,0], [0,0,0], 0, 0, 0, 0)
    poseMove(version=0.1, moveX=3.0, moveY=4.0, moveZ=0, rotationTorso=0.0, afterMoveObjPos=[0.0, 0.0, 0.0])
    >>> getPoseMove( [3,4,0], [0,0,math.pi/2], 0, 0, 0, 0)
    poseMove(version=0.1, moveX=4.0, moveY=-2.9999999999999996, moveZ=0, rotationTorso=1.5707963267948966, afterMoveObjPos=[0.0, 0.0, 0.0])
    """

    dx, dy, dz = objTranslation  # position of object in robot torso reper
    dWX, dWY, dWZ = objOrientation
    dest_point_inTorsoReper = numeric.chgRepereCorrected(x,y,z, -dx, -dy, -dz, dWX, dWY, dWZ + math.pi)  # +math.pi.. car on a lorientation inverse avec opencv.. a corriger ailleurs..
    px,py,pz = dest_point_inTorsoReper
    print("Dest_point : %s" % dest_point_inTorsoReper)
    #dest_point_inTorsoReper = chgRepere(x,y,z, -dx, -dy, -dz, -dWX, -dWY, -dWZ)
    if torsoOrientation !=None:
        rZ = numeric.computeVectAngle( np.array([1,0]), numeric.polarToCartesian(1, dWZ)) + torsoOrientation
    else:
        rZ = numeric.computeVectAngle( np.array([1,0]), np.array([dest_point_inTorsoReper[0], dest_point_inTorsoReper[1]]) )
    print("rotation of rZ: %f" % rZ)
    dest_point_inTorsoReper = numeric.chgRepereCorrected(px, py, pz, 0, 0, 0, 0, 0, -rZ)  # TODO
    print("destPoint in torso reper after rotation %s" % str(dest_point_inTorsoReper))
  # after rotation
    move = np.array([dest_point_inTorsoReper[0], dest_point_inTorsoReper[1], dest_point_inTorsoReper[2]])
    move = np.array([np.sign(move[0]) * np.min([abs(move[0]), thresholdMove]), np.sign(move[1]) * np.min([abs(move[1]), thresholdMove]), 0])
    ## utiliser le chgRepere corrected ???
    afterMoveObjPos = numeric.chgRepereCorrected(dx, dy, dz, move[0], move[1], 0, 0, 0, -rZ)
    return retGetPoseMove(0.1, move[0], move[1], 0,  rZ, afterMoveObjPos.tolist())


def wait_opencv(keycode=27):
    key =  cv2.waitKey(0) & 0xFF
    while key != keycode:
        key =  cv2.waitKey(0) & 0xFF
        cv2.destroyAllWindows()

#def testPnpPod():
#    #scale = 2  # scale ratio compared to 640x480, for example in 320x240 scale ratio = 0.5, in 1280x960 scale ration = 2 , calibration matrix has been computed based on 640x480 resolution
#    #cameraMatrix = np.array([[ 533.48550633,    0.        ,  298.20393548], [   0.        ,  530.006434  ,  258.74421405], [   0.        ,    0.        ,    1.        ]]) * scale
#    #distorsionCoef = np.array([[ -1.12257723e-01], [  5.35782365e-01], [  1.08637612e-03], [ -4.06574346e-03], [ -1.70570660e+00]])  # distorsion does need to be scaled
#    #name = filetools.getFilenameFromTime()
#    path = "/home/lgeorge/tmp/PODS/6Leds/"
#    path = "/home/lgeorge/test_led/"
#    path = "/home/lgeorge/nao4/"
#    path = "/tmp/cur/"
#    #path = "/home/lgeorge/tmp/att/"
#    #i = 0
#
#    ## 0,0,0 in the middle of the object !
#    rA = np.array([-0.0525, -0.018, 0])
#    rB = np.array([-0.0525, 0, 0])
#    rC = np.array([-0.0525, 0.018, 0])
#    rD = np.array([0.0525, 0.018, 0])
#    rE = np.array([0.0525, 0.00, 0])
#    rF = np.array([0.0525, -0.018, 0])
#    realObjectPts = np.array([rA,rB, rC, rD, rE, rF])
#
#    ldiff = []
#
#    try:
#        for fname in os.listdir(path):
#            print "NEWWW"
#            print fname
#            image = cv2.imread(os.path.join(path, fname), cv2.CV_LOAD_IMAGE_GRAYSCALE)
#            ledPts, thimage = infraLedDetector(image)
#            rectangle = podLocator.bestRectangle(podLocator.pointMatch6PointsRectangular(ledPts))
#            if rectangle !=None:
#                #print rectangle
#                pnpOpencv = getPnP(rectangle, realObjectPts)
#                #print("projected points %s" % str(pnpOpencv.projectedImPts))
#                #print " prjected diff"
#                #print pnpOpencv.projectedImPts[:,0]
#                #print "rectangle"
#                #print rectangle
#
#                #print np.allclose(rectangle, pnpOpencv.projectedImPts[:,0], atol=3)
#
#
#               # if not(np.allclose(rectangle, pnpOpencv.projectedImPts[:,0], atol=3)): ## sometimes the projected and imagepoints are too differents -> it means that pnp results cant provide good correspondance between patterns and img pts
#               #     ## ne dois plus arriver
#               #     print "error pnp"
#               #     rectangle = None
#               # else:
#                if pnpOpencv != None:
#                    print "ii"
#                    diff = getLedDifference(rectangle, image, 1)
#                    ldiff.append(diff)
#                    for num, t in enumerate(pnpOpencv.projectedImPts):
#                        x, y = t[0]
#                        cv2.circle(image, (int(x), int(y)), 1*num, (0,200,0), 2)
#
#                    for num, t in enumerate(rectangle):
#                        x, y = t
#                        cv2.circle(image, (int(x), int(y)), 10, (0,200,0), 4)
#
#        #            print("num %f, x %f, y %f" % (num, x, y))
#                #cv2.imwrite('/tmp/'+ fname + '_debug.jpg', image)
#                    cv2.imwrite('/tmp/FOUND_'+ fname +  '_debug.jpg', image)
#                    cv2.imwrite('/tmp/FOUND_'+ fname + '_debug.jpg_black', thimage)
#            if rectangle== None:
#                for num, pt in enumerate(ledPts):
#                    cv2.circle(image, (int(pt.x), int(pt.y)), 5, (0,200,0), 2)
#                cv2.imwrite('/tmp/NOTHING_FOUND_'+ fname + '_debug.jpg', image)
#                cv2.imwrite('/tmp/NOTHING_FOUND_'+ fname + '_debug.jpg_black', thimage)
#    except:
#        pass
#    if ldiff!=[]:
#        print("diff moyen %f" % np.mean(ldiff))
#    return ldiff


#def lookArround(speed=0.1):
#    return # desactive pour l'instant
#    #motion = naoqitools.myGetProxy("ALMotion")
#    #taskId = motion.post.angleInterpolation(["HeadYaw"], [math.pi/3.0, 0, -math.pi/3.0, 0], [2, 4, 8, 10], True)
#    #return taskId
#    ##motion.angleInterpolationWithSpeed("HeadYaw", -math.pi, speed)




def main():
    print("Main vide")

if __name__=="__main__":
    main()


