# -*- coding: utf-8 -*-
#!/usr/bin/env python
###########################################################
# TEst pnp datamatrix
# Author: L. George & A. Mazel
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################
"""
@author: lgeorge@aldebaran-robotics.com
         amazel@aldebaran-robotics.com
"""
__author__ = 'lgeorge'

import serialization_tools
import datamatrix_topology
import os
import numpy as np
import imagePnp
import json
import script_draw3d_datamatrix
import cv2

def computeDefaultPnp(strImageFname, strPickleFname):
    return doPnpComputation(strPickleFname)


def computeDefaultPnpRansac(strImageFname, strPickleFname):
    return doPnpComputation(strPickleFname, bUseRansac=True)


def doPnpComputation(strPickleFname, bUseRansac=False):
    """
    return the 6D pose of the pnp in a numpy array
    @param strPickleFname: file to look for a datamatrix, the first datamatrix in the file is used
    @return: np.array
    """
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
        pnp = imagePnp.getPNP(aCornersPixels, aRealPts, nResolution=3, bUseRansac=bUseRansac)
        return pnp
    else:
        return None

def generateAutoTestLine(strImageFname, strPickleFname):
    pnp = doPnpComputation(strPickleFname)
    aPose6D = np.array([pnp.translation[0], pnp.translation[1], pnp.translation[2], pnp.orientation[0], pnp.orientation[1], pnp.orientation[2]])
    if aPose6D == None:
        return None
    return  [strImageFname, strPickleFname, aPose6D.tolist()]

def generateAutoTestFile(strPath, strJsonDest):
    """
    for .pickle in strPath, compute the pnp, display the pnp on the image, and save the name of jpg/pickle and result of pnp into a file.
    The result is saved in a .json file

    The user is also asked to press a key (Y or N) to say if the pnp seems correct.
    If No is enter the result of pnp is set to NONE  (the user will have to edit it later
    @param strPath:
    @param strJsonDest
    @return:
    """
    aList = []
    if os.path.exists(os.path.join(strPath, strJsonDest)):
        with open(strJsonDest, 'r') as destJson:
            aList = json.load(destJson)
    for file in sorted(os.listdir(strPath)):
        print file
        if '.pickle' in file:
            strPickleFname = os.path.join(strPath, file)
            strImageFname = os.path.join(strPath, strPickleFname.split('.pickle')[0] + 'CameraTop.jpg')
            pnp = doPnpComputation(strPickleFname)
            if pnp == None:
                continue

            datamatrixInformation = serialization_tools.loadObjectFromFile(strPickleFname)
            aCornersPixels = datamatrixInformation.marks[0].aCornersPixels
            aLine = generateAutoTestLine(strImageFname, strPickleFname)
            nResolution = 3
            imageDebug = script_draw3d_datamatrix.draw3D(pnp, nResolution, strImgFname=strImageFname, strDebugFname='/tmp/out.png', aCornersPixels = aCornersPixels)
            cv2.imshow('Ok?', imageDebug)
            key = cv2.waitKey()
            print("retured key is %s" % key)
            if key != 121:  # 121 = y key
                aLine[2] = None
            aList.append(aLine)
            with open(strJsonDest, 'w') as destJson:
                json.dump(aList, destJson, indent=4)

def main():
    generateAutoTestFile('/home/lgeorge/projects/navigation/apprentissage_acceuil/markDetector', '/tmp/out.json')
    generateAutoTestFile('/home/lgeorge/projects/navigation/reloc_debug_croix_laurent_chaise_bug', '/tmp/out.json')

if __name__ == "__main__":
    main()