# -*- coding: utf-8 -*-
__author__ = 'lgeorge'
import serialization_tools
import datamatrix_topology
import os
import numpy as np
import imagePnp
import json
import script_draw3d_datamatrix
import cv2
import math
import collections

def convertPnpToPose6D(pnpStructure):
    """
    Do the old pnp computation
    @param: pnpStructure: .translation : np.array, .orientation: np.array shape = 3
    @return: pose6D, return np.array([nan, nan, nan, nan, nan, nan]) if pnp == None
    """
    if pnpStructure != None:
        res = np.array([pnpStructure.translation[0], pnpStructure.translation[1], pnpStructure.translation[2], pnpStructure.orientation[0], pnpStructure.orientation[1], pnpStructure.orientation[2]])
    else:
        res = np.ones(6) * np.nan
    return res

def doPnp(strPickleFname):
    """
    return the 6D pose of the pnp in a numpy array
    @param strPickleFname: file to look for a datamatrix, the first datamatrix in the file is used
    @return: np.array
    """
    print("computing pnp using Pixel improvements %s" % strPickleFname)
    datamatrixInformation = serialization_tools.loadObjectFromFile(strPickleFname)
    if datamatrixInformation.marks != []:
        aCornersPixels = datamatrixInformation.marks[0].aCornersPixels
        rDataMatrixRealSize = datamatrix_topology.getDiagSize(datamatrixInformation.marks[0].strName)

        realWidth = np.sqrt((rDataMatrixRealSize** 2) /2.0)
        realHeight = realWidth
        a = np.array([-0.5 * realWidth, -0.5 * realHeight, 0])
        b = np.array([-0.5 * realWidth, 0.5 * realHeight, 0])
        c = np.array([0.5 * realWidth, 0.5 * realHeight, 0])
        d = np.array([0.5 * realWidth, -0.5 * realHeight, 0])
        #e = np.array([0, 0, 0], dtype=np.float)
        #e = np.array([0.4*realWidth, 0.4*realHeight, 0], dtype=np.float)
        #print("Using point e%s" % e)
        #aRealPts = np.array([a,b,c,d,e])
        aRealPts = np.array([a, b, c, d])
        pnp = imagePnp.getPnP(aCornersPixels, aRealPts, nResolution=3)
        return pnp
    else:
        return None

def doPnpOptimizedCorner(strImageFname, strPickleFname):
    """
    return the 6D pose of the pnp in a numpy array
    @param strPickleFname: file to look for a datamatrix, the first datamatrix in the file is used
    @return: np.array
    """
    import test_opencvCornersDetection
    print("computing pnp using Pixel improvements %s" % strPickleFname)
    datamatrixInformation = serialization_tools.loadObjectFromFile(strPickleFname)
    if datamatrixInformation.marks != []:
        aCornersPixels = datamatrixInformation.marks[0].aCornersPixels
        rDataMatrixRealSize = datamatrix_topology.getDiagSize(datamatrixInformation.marks[0].strName)

        realWidth = np.sqrt((rDataMatrixRealSize** 2) /2.0)
        realHeight = realWidth
        a = np.array([-0.5 * realWidth, -0.5 * realHeight, 0])
        b = np.array([-0.5 * realWidth, 0.5 * realHeight, 0])
        c = np.array([0.5 * realWidth, 0.5 * realHeight, 0])
        d = np.array([0.5 * realWidth, -0.5 * realHeight, 0])
        #e = np.array([0, 0, 0], dtype=np.float)
        e = np.array([0.4*realWidth, 0.4*realHeight, 0], dtype=np.float)
        #print("Using point e%s" % e)
        #aRealPts = np.array([a,b,c,d,e])
        aImage = cv2.imread(strImageFname, cv2.CV_LOAD_IMAGE_GRAYSCALE)
        aCornersPixels[2] = test_opencvCornersDetection.findCrossDotLines(aImage, aCornersPixels)
        aRealPts = np.array([a, b, e, d])
        pnp = imagePnp.getPnP(aCornersPixels, aRealPts, nResolution=3)
        return pnp
    else:
        return None

def doPnpOptimizedLandOpositeCorner(strImageFname, strPickleFname):
    """
    return the 6D pose of the pnp in a numpy array
    @param strPickleFname: file to look for a datamatrix, the first datamatrix in the file is used
    @return: np.array
    """
    import test_opencvCornersDetection
    print("computing pnp using Pixel improvements %s" % strPickleFname)
    datamatrixInformation = serialization_tools.loadObjectFromFile(strPickleFname)
    if datamatrixInformation.marks != []:
        aCornersPixels = datamatrixInformation.marks[0].aCornersPixels
        rDataMatrixRealSize = datamatrix_topology.getDiagSize(datamatrixInformation.marks[0].strName)

        realWidth = np.sqrt((rDataMatrixRealSize** 2) /2.0)
        realHeight = realWidth
        a = np.array([-0.5 * realWidth, -0.5 * realHeight, 0])
        b = np.array([-0.5 * realWidth, 0.5 * realHeight, 0])
        c = np.array([0.5 * realWidth, 0.5 * realHeight, 0])
        d = np.array([0.5 * realWidth, -0.5 * realHeight, 0])
        #e = np.array([0, 0, 0], dtype=np.float)
        e = np.array([0.4*realWidth, 0.4*realHeight, 0], dtype=np.float)
        #print("Using point e%s" % e)
        #aRealPts = np.array([a,b,c,d,e])
        aImage = cv2.imread(strImageFname, cv2.CV_LOAD_IMAGE_GRAYSCALE)
        aCornersPixels[2] = test_opencvCornersDetection.findCrossDotLines(aImage, aCornersPixels)
        aCornersPixels[0] = test_opencvCornersDetection.findLCorner(aImage, aCornersPixels)
        aRealPts = np.array([a, b, e, d])
        pnp = imagePnp.getPnP(aCornersPixels, aRealPts, nResolution=3)
        return pnp
    else:
        return None

def doPnpOptimizedAllCorners(strImageFname, strPickleFname):
    """
    return the 6D pose of the pnp in a numpy array
    @param strPickleFname: file to look for a datamatrix, the first datamatrix in the file is used
    @return: np.array
    """
    import test_opencvCornersDetection
    print("computing pnp using Pixel improvements %s" % strPickleFname)
    datamatrixInformation = serialization_tools.loadObjectFromFile(strPickleFname)
    if datamatrixInformation.marks != []:
        aCornersPixels = datamatrixInformation.marks[0].aCornersPixels
        rDataMatrixRealSize = datamatrix_topology.getDiagSize(datamatrixInformation.marks[0].strName)

        realWidth = np.sqrt((rDataMatrixRealSize** 2) /2.0)
        realHeight = realWidth
        a = np.array([-0.5 * realWidth, -0.5 * realHeight, 0])
        b = np.array([-0.5 * realWidth, 0.5 * realHeight, 0])
        c = np.array([0.5 * realWidth, 0.5 * realHeight, 0])
        d = np.array([0.5 * realWidth, -0.5 * realHeight, 0])
        #e = np.array([0, 0, 0], dtype=np.float)
        e = np.array([0.4*realWidth, 0.4*realHeight, 0], dtype=np.float)
        #print("Using point e%s" % e)
        #aRealPts = np.array([a,b,c,d,e])
        aImage = cv2.imread(strImageFname, cv2.CV_LOAD_IMAGE_GRAYSCALE)

        import copy
        aCornersPixelsCopy = copy.deepcopy(aCornersPixels)

        aCornersPixels[2] = test_opencvCornersDetection.findCrossDotLines(aImage, aCornersPixels)
        aCornersPixels[0] = test_opencvCornersDetection.findLCorner(aImage, aCornersPixels)
        aCornersPixels[1] = test_opencvCornersDetection.findBottomCorner(aImage, aCornersPixels)
        aCornersPixels[3] = test_opencvCornersDetection.findTopCorner(aImage, aCornersPixels)
        aRealPts = np.array([a, b, e, d])
        pnp = imagePnp.getPnP(aCornersPixels, aRealPts, nResolution=3)

        imgDebug = script_draw3d_datamatrix.draw3D(pnp, 3,  strImgFname=strImageFname, strDebugFname='/tmp/out.png', aCornersPixels=aCornersPixels)

        for aCorner  in aCornersPixelsCopy:
            nX = int(round(aCorner[0]))
            nY = int(round(aCorner[1]))
            cv2.circle(imgDebug, (nX, nY), 1, (0, 0, 255))
        cv2.imshow('Proccessed', imgDebug)
        cv2.waitKey()
        return pnp
    else:
        return None

def doPnpOptimizedAllCornersAddingTimePattern(strImageFname, strPickleFname):
    """
    return the 6D pose of the pnp in a numpy array
    @param strPickleFname: file to look for a datamatrix, the first datamatrix in the file is used
    @return: np.array
    """
    import test_opencvCornersDetection
    print("computing pnp using Pixel improvements %s" % strPickleFname)
    datamatrixInformation = serialization_tools.loadObjectFromFile(strPickleFname)
    if datamatrixInformation.marks != []:
        aCornersPixels = datamatrixInformation.marks[0].aCornersPixels
        rDataMatrixRealSize = datamatrix_topology.getDiagSize(datamatrixInformation.marks[0].strName)

        realWidth = np.sqrt((rDataMatrixRealSize** 2) /2.0)
        realHeight = realWidth
        a = np.array([-0.5 * realWidth, -0.5 * realHeight, 0])
        b = np.array([-0.5 * realWidth, 0.5 * realHeight, 0])
        c = np.array([0.5 * realWidth, 0.5 * realHeight, 0])
        d = np.array([0.5 * realWidth, -0.5 * realHeight, 0])
        #e = np.array([0, 0, 0], dtype=np.float)
        e = np.array([0.4*realWidth, 0.4*realHeight, 0], dtype=np.float)
        f = np.array([0.0, 0.5*realHeight, 0.0], dtype=np.float)  # middle of bottom ( the inside corner)
        g = np.array([0.5*realWidth, 0.0, 0.0], dtype=np.float)  # middle of right (the inside corner)
        #print("Using point e%s" % e)
        #aRealPts = np.array([a,b,c,d,e])
        aImage = cv2.imread(strImageFname, cv2.CV_LOAD_IMAGE_GRAYSCALE)

        import copy
        aCornersPixelsCopy = copy.deepcopy(aCornersPixels)

        aCornersPixels[0] = test_opencvCornersDetection.findLCorner(aImage, aCornersPixels)
        aCornersPixels[1] = test_opencvCornersDetection.findBottomCorner(aImage, aCornersPixels)
        aCornersPixels[3] = test_opencvCornersDetection.findTopCorner(aImage, aCornersPixels)
        aCornersPixels.append(test_opencvCornersDetection.getCornerMidleOfBottomTimingPattern(aImage, aCornersPixelsCopy))
        aCornersPixels.append(test_opencvCornersDetection.getCornerMidleOfRightTimingPattern(aImage, aCornersPixelsCopy))
        ## celui ci toujours le faire en dernier car on casse les corners de la datamatrix:
        aCornersPixels[2] = test_opencvCornersDetection.findCrossDotLines(aImage, aCornersPixels)
        aRealPts = np.array([a, b, e, d, f, g])
        pnp = imagePnp.getPnP(aCornersPixels, aRealPts, nResolution=3)

        imgDebug = script_draw3d_datamatrix.draw3D(pnp, 3,  strImgFname=strImageFname, strDebugFname='/tmp/out.png', aCornersPixels=aCornersPixels)

        for aCorner  in aCornersPixelsCopy:
            nX = int(round(aCorner[0]))
            nY = int(round(aCorner[1]))
            cv2.circle(imgDebug, (nX, nY), 1, (0, 0, 255))
        cv2.imshow('Proccessed', imgDebug)
        cv2.waitKey()
        return pnp
    else:
        return None


def doPnpOptimizedCornerFivePoints(strImageFname, strPickleFname):
    return _doPnpOptimizedCornerFivePoints(strImageFname, strPickleFname, bUseRansac=False)

def doPnpOptimizedCornerFivePointsRansac(strImageFname, strPickleFname):
    return _doPnpOptimizedCornerFivePoints(strImageFname, strPickleFname, bUseRansac=True)

def doPnpOptimizedCornerFivePoints(strImageFname, strPickleFname):
    """
    return the 6D pose of the pnp in a numpy array
    @param strPickleFname: file to look for a datamatrix, the first datamatrix in the file is used
    @return: np.array
    """
    import test_opencvCornersDetection
    print("computing pnp using Pixel improvements %s" % strPickleFname)
    datamatrixInformation = serialization_tools.loadObjectFromFile(strPickleFname)
    if datamatrixInformation.marks != []:
        aCornersPixels = datamatrixInformation.marks[0].aCornersPixels
        rDataMatrixRealSize = datamatrix_topology.getDiagSize(datamatrixInformation.marks[0].strName)

        realWidth = np.sqrt((rDataMatrixRealSize** 2) /2.0)
        realHeight = realWidth
        a = np.array([-0.5 * realWidth, -0.5 * realHeight, 0])
        b = np.array([-0.5 * realWidth, 0.5 * realHeight, 0])
        c = np.array([0.5 * realWidth, 0.5 * realHeight, 0])
        d = np.array([0.5 * realWidth, -0.5 * realHeight, 0])
        #e = np.array([0, 0, 0], dtype=np.float)
        e = np.array([0.4*realWidth, 0.4*realHeight, 0], dtype=np.float)
        #print("Using point e%s" % e)
        #aRealPts = np.array([a,b,c,d,e])
        aImage = cv2.imread(strImageFname, cv2.CV_LOAD_IMAGE_GRAYSCALE)
        aCornersPixels.append(test_opencvCornersDetection.findCrossDotLines(aImage, aCornersPixels))
        aRealPts = np.array([a, b, c, d, e])
        pnp = imagePnp.getPnP(aCornersPixels, aRealPts, nResolution=3, bUseRansac=False)
        return pnp
    else:
        return None


def runTest(strJsonFname, pFunctionPose6D, bDraw=False):
    """
    Run the functiion on each files present in strJsonFname. If distance is too different (more than 0.5m) or angle is too different (more than pi/2)
    @param strJsonFname: the list of good results for pose estimation
    @param pFunctionPose6D: a pointer (i.e name) of the function to test. The function signature is function(strImageFname, strPickleFname) and it return a pnp object (with trnalsation/orientation)
    @param bDraw: if True, draw the pose if a fail occurs
    @return: nSuccess, nFail, nSuccess/nTotal, aFailed (list of failed), aSuccess (list of succes files)
    """
    ret = collections.namedtuple('resTest', ['nSucces', 'nFailed', 'nSuccesRate', 'aFailed', 'aSuccess'])
    aList = []
    aFailed = []
    aSuccess = []
    rMaxDiffAngle = math.pi/8.0
    rMaxDiffDistance = 0.1
    with open(strJsonFname, 'r') as f:
        aList = json.load(f)
    for strImageFname, strPickleFname, aGoodPose6D in aList:
        bSuccess = False
        pnpStructure = pFunctionPose6D(strImageFname, strPickleFname)
        aPose6D = convertPnpToPose6D(pnpStructure)
        #if np.all(np.abs(aPose6D - aGoodPose6D)[0:3] < rMaxDiffDistance ) and np.all(np.abs(aPose6D - aGoodPose6D)[3:] < rMaxDiffAngle ):
        if np.all(np.abs(aPose6D - aGoodPose6D)[3:] < rMaxDiffAngle ):
            bSuccess = True

        if bSuccess:
            aSuccess.append([strImageFname, strPickleFname, aGoodPose6D, aPose6D])
        else:
            aFailed.append([strImageFname, strPickleFname, aGoodPose6D, aPose6D])
            if bDraw:
                imgDebug = script_draw3d_datamatrix.draw3D(pnpStructure, 3,  strImgFname=strImageFname, strDebugFname='/tmp/out.png', aCornersPixels=[])
                cv2.imshow('failed', imgDebug)
                cv2.waitKey()


    res = ret(len(aSuccess), len(aFailed), len(aSuccess)/ float(len(aSuccess) + len(aFailed)), aFailed, aSuccess)
    print("Failed : %s" % len(aFailed))
    print aFailed
    return res

def main():
    #import generate_autotest_pnp
    #print("Using default methods:")  # sur les angles 4 erreurs
    #res = runTest('pnp_debug_file.json', generate_autotest_pnp.computeDefaultPnp)
    #print res

    #print("Using default methods (+ransac):")  # 2 erreurs sur les angles.. mais des soucis.. dans le draw (grosses erreurs sur les distances
    #res = runTest('pnp_debug_file.json', generate_autotest_pnp.computeDefaultPnpRansac)
    #print res
#
    #print("Using improved bottom corners:")  # Failed 3 sur les angles
    #res = runTest('pnp_debug_file.json', doPnpOptimizedCorner)
    #print res

    #print("Using improved bottom corners with 5 points:") # failed 3 sur les angles
    #res = runTest('pnp_debug_file.json', doPnpOptimizedCorner)
    #print res
#    raw_input()


    #print("Using improved bottom corners with 5 points:") #nSucces=54, nFailed=4, nSuccesRate=0.9310344827586207,
    #res = runTest('pnp_debug_file.json', doPnpOptimizedCornerFivePoints)  # on ne gagne rien par rapport au default
    #print res
#

    #print("Using improved bottom corners with 5 points ransac:")
    #res = runTest('pnp_debug_file.json', doPnpOptimizedCornerFivePointsRansac) # failed = 9
    #print res

    #print("Using improved L and opposite corners:")
    #res = runTest('pnp_debug_file.json', doPnpOptimizedLandOpositeCorner) # 3 erreurs
    #print res


    #print("Using improved 4 corners:")
    #res = runTest('pnp_debug_file.json', doPnpOptimizedAllCorners) # 2 erreurs sur les angles
    #print res

    print("Using improved 4 corners + 2 middle corners:")
    res = runTest('pnp_debug_file.json', doPnpOptimizedAllCornersAddingTimePattern)
    print res




if __name__ == "__main__":
    main()
