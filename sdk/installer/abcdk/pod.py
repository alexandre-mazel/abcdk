# -*- coding: utf-8 -*-
###########################################################
# Aldebaran Behavior Complementary Development Kit
# Charging Station tools (aka pod)
# Author: L. George & A. Mazel
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################
"""
@Title: Pod related methods (going and sitting on pod to charge)
@author: lgeorge@aldebaran-robotics.com
         amazel@aldebaran-robotics.com
"""

from __future__ import print_function
print( "importing abcdk.pod" );

import serialization_tools
import cv2
#import config
#config.bInChoregraphe = False
import debug
import imagePnp
import naoqitools
import numeric
import camera
import system
import filetools
import leds
import navigation
import poselibrary
import speech
import translate
import motiontools

import datetime
import math
import mutex
import numpy as np
import os
import time

module_mutex = mutex.mutex(); # our module to ensure that some methods aren't called in parallel (it should be in the Poder Object and it should be a singleton !)

def getMoveConfig(key='stableRotation'):
    """ different speed config option that provide reliable movements
    key :
        - 'stableRotation' : as in visual compass slow speedConfig
        - 'stableMoveX' : slow move for backwardSteps
    """
    speedConfig = [];
    if key == 'stableRotation':
        speedConfig.append( ['MaxStepTheta', 0.25] );
        speedConfig.append( ['MaxStepFrequency', 0.2] );
    if key == 'stableMoveX':
        speedConfig.append( ['MaxStepX', 0.04] );
        #speedConfig.append( ['MaxStepY', 0.11] );
        speedConfig.append( ['MaxStepTheta', 0.25] );
        speedConfig.append( ['MaxStepFrequency', 0.2] );
    return speedConfig

def absMin(a, b):
    """
    return the min of abs(a), abs(b), and add the sign of a.
    """
    return np.sign(a) * np.min([abs(a), abs(b)])

# ---------------------------------------- Infrared Led detector functions --------
class ledPt:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.score = 0
        self.area = 0
        self.val = -1


def infraLedDetector(cameraImage, percent = 0.1, bFindBluePod = False ):
    """ return a list of possibles infrared leds present in the image

    Args:
        cameraImage: opencv image
        percent : percentage of min-max luminosity range to use for threshold

    Returns:
        list of points (see ledPt class)
    """
    bDebugShow = False
    image = cameraImage
    thresholdImg = computeThresholdImage(cameraImage, percent=percent, bFindBluePod=bFindBluePod, bDebugShow=bDebugShow)
    #~ cv2.imwrite( "c:\\tempo\\work0.jpg", image );

    nTry = 0
    nMaxTry = 2
    while(True):
        if nTry>= 1 :
            print("No pod seen we try to filter it a bit more")
        ledsPt = computeLedPts(thresholdImg, image, bDebugShow=bDebugShow)
        rectangle = PodLocator.bestRectangle(PodLocator.pointMatch6PointsRectangular(ledsPt))
        if rectangle is not None or nTry>nMaxTry or np.max(thresholdImg) == 0:
            break

        element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
        thresholdImg = cv2.erode(thresholdImg, element, iterations=1)
        #cv2.imshow('retry', thresholdImg)
        #cv2.waitKey(0)

        nTry += 1

    return ledsPt, thresholdImg, rectangle
# infraLedDetector - end

def computeLedPts(thresholdImg, image, bDebugShow=False):
    res = []
    contours, hierarchy = cv2.findContours(thresholdImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if bDebugShow:
        drawing = np.zeros(image.shape,np.uint8) # Image to draw the contours
        for cnt in contours:
            color = np.random.randint(200,255,(3)).tolist() # Select a random color
            cv2.drawContours(drawing,[cnt],0,color,2)
        cv2.imshow('contour', drawing)
    for num, contour in enumerate(contours):
        m = cv2.moments(contour)
        # ** regionprops **
        Area          = m['m00']
        Perimeter     = cv2.arcLength(contour,True)
        #~ print( "Area: %s" % Area );
        if Area > 8: # 2013-10-11 LG: avec l'ancien pod c'etait 10, je mets 8 pour etre plus tolerant sur le nouveau
        ## and Perimeter < 200 and Area < 1000:
            Centroid      = ( m['m10']/m['m00'],m['m01']/m['m00'] )
            pt = ledPt(Centroid[0], Centroid[1])
            pt.area = Area
            pt.perimeter = Perimeter
            pt.val = image[pt.y, pt.x]
            (x, y), radius = cv2.minEnclosingCircle(contour)
            #~ print( "x,y: %s, %s, val:%s" % (x, y, pt.val) );
            pt.score = pt.area / (math.pi * radius ** 2)
            res.append(pt)
            #~ print( "pt: %s" % pt );
    return res

def computeThresholdImage(cameraImage, percent=0.1, bFindBluePod = True, bDebugShow = False):

    if( bFindBluePod ):
        thresholdImg = cameraImage;
        #r, thresholdImg = cv2.threshold(image, 100, 255, cv2.THRESH_BINARY)  # we filter a bit in order to disconnet dots if they are connected
        #element = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
        #thresholdImg = cv2.erode(thresholdImg, element)

        element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
        #cv2.imshow('start', thresholdImg)
        thresholdImg = cv2.morphologyEx(thresholdImg, cv2.MORPH_OPEN, element, iterations=1)  # removing noise
        #cv2.imshow('1', thresholdImg)
        #thresholdImg = cv2.morphologyEx(thresholdImg, cv2.MORPH_CLOSE, element, iterations=3)  # removing hole in blob
        #cv2.imshow('2', thresholdImg)

        if bDebugShow:
            cv2.imshow('beforeOtsu', thresholdImg)
        #r, thresholdImg = cv2.threshold(thresholdImg, 100, 255, cv2.THRESH_TOZERO)
        thresholdImg[thresholdImg< np.max(thresholdImg)/2] = 0
        #cv2.imshow('3', thresholdImg)
        #cv2.waitKey(0)

        #r, thresholdImg = cv2.threshold(thresholdImg, 100, 255, cv2.THRESH_BINARY)  # we filter a bit in order to disconnet dots if they are connected

## we add an other erode operation at the end.. to facilitate far pod detection
        #thresholdImg = cv2.erode(thresholdImg, element, iterations=1)
        #thresholdImg = cv2.morphologyEx(thresholdImg, cv2.MORPH_CLOSE, element, iterations=2)  # removing hole in blob
        #thresholdImg = cv2.dilate(thresholdImg, element, iterations=2)
        #cv2.destroyAllWindows()
        if bDebugShow:
            cv2.imshow('out', thresholdImg)
        #cv2.waitKey()
        #cv2.destroyAllWindows()
        #imagecp = thresholdImg.copy()  # TODO: why are we doing a copy here ?


    else:
        #print "threshold", str(threshold), "min max", str(fMin), str(fMax)
        if percent==0:
            r, thresholdImg = cv2.threshold(cameraImage, 235, 255, cv2.THRESH_BINARY)  # 2013-10-11 LG: 235 was 240
        else:
            fMin, fMax, locMin, locMax = cv2.minMaxLoc(cameraImage)
            threshold = int((1-percent) * (fMax))
            r, thresholdImg = cv2.threshold(cameraImage, threshold, 255, cv2.THRESH_BINARY)

        #~ cv2.imwrite( "c:\\tempo\\work.jpg", thresholdImg );
        #element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        element = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
        thresholdImg = cv2.erode(thresholdImg, element)
        #thresholdImg = cv2.erode(thresholdImg, element)
        #thresholdImg = cv2.erode(thresholdImg, element)
        thresholdImg = cv2.dilate(thresholdImg, element)
        #imagecp = thresholdImg.copy()  # TODO: why are we doing a copy here ?
        #cv2.imshow('a', imagecp)
        #cv2.waitKey()

        #~ cv2.imwrite( "c:\\tempo\\work2.jpg", thresholdImg );
        ## TODO : essayer avec un hough circle !
    return thresholdImg

def getLedDifference(pts, img, sizeSquare=0):
    """
    This method compute the difference in luminosity between points in an image
    Args:
        pts: list of (x,y) coordinate
        img: the image to search for the poitns (greyscale)
        sizeSquare: size of the square to use around each point to compute the luminosity, if 1 , 9 points are used
    returns:
        percentage of difference betwen min and max luminosity
    """
    if sizeSquare == 0:
        luminositys = [img[pt[1], pt[0]] for pt in pts]
    else:
        luminositys = [(np.median(img[pt[1]-sizeSquare:pt[1]+sizeSquare, pt[0]-sizeSquare:pt[0]+sizeSquare])) for pt in pts]
    maxIndex = np.argmax(luminositys)
    minIndex = np.argmin(luminositys)
    #return np.round((luminositys[maxIndex] - luminositys[minIndex]) / 255, 2)

    diff = luminositys[maxIndex] - luminositys[minIndex]
    print("difference luminosity %f" % diff)


    cv2.rectangle(img, (int(pts[minIndex][0]-sizeSquare-1), int(pts[minIndex][1]-sizeSquare-1)), (int(pts[minIndex][0])+sizeSquare+1, int(pts[minIndex][1])+sizeSquare+1), (0,200,80), 0)
    cv2.rectangle(img, (int(pts[maxIndex][0]-sizeSquare-1), int(pts[maxIndex][1]-sizeSquare-1)), (int(pts[maxIndex][0])+sizeSquare+1, int(pts[maxIndex][1])+sizeSquare+1), (0,200,80), 0)
    #cv2.circle(img, (int(pts[maxIndex][0]), int(pts[maxIndex][1])), sizeSquare*2 +1, (0,200,80), 10)
    cv2.imwrite('/tmp/FOUND_'+  str(diff) + '_diff.png', img)
    return diff
# getLedDifference -  end

def detectBluePodRoughly( originalImg, bVeryApproximative = False, strPathTestOut = "" ):
    """
    detect something that could be the pod (a blue shape)
    return [x,y] the position in the image of a place that could be perhaps the pod...
    with x and y in range [-0.5,0.5]
    [-1,-1] means no pod seen
    """

    print( "INF: detectBluePodRoughly entering...(strPathTestOut: '%s')" % strPathTestOut );

    retVal = [-1,-1];
    #~ img = np.array([
                                #~ [(1,2,3), (4,5,6)],
                                #~ [(7,8,9), (10,11,12)]
                        #~ ]);
    #~ img = np.array([
                                #~ [(1,2,3), (4,5,6),(255,0,0)],
                                #~ [(128,128,128), (128,128,255),(255,64,64)],
                                #~ [(1,2,3), (4,5,6),(255,0,0)],
                                #~ [(200,50,78), (4,5,6),(255,0,0)],
                        #~ ]);

    # first resize the img dramatically
    # interpolation comparison, on my computer 8core, in 4VGA:
    # INTER_NEAREST: 0.0
    # INTER_LINEAR: 0.001
    # INTER_AREA: 0.003
    # INTER_CUBIC : 0.003
    # INTER_LANCZOS4: 0.006
    img = cv2.resize( originalImg, (0,0), fx=0.125, fy=0.125, interpolation = cv2.INTER_NEAREST );
    #~ print( img );
    width = len(img[0]);
    height = len( img );
    img = np.reshape( img, (height*width,3) );
    #~ print( img[:,0] );
    #~ img = img[:,0]; # only blue
     # convert them in int on the fly, as we want to keep the sign to clip the negative value
    img = np.clip( np.array(img[:,0], dtype=int)*1.4 - img[:,1] - img[:,2], 0,255 ); # here you can choose if you want really blue, or somekind of nearly blue (somekind => multiply the blue array channel =>np.array(img[:,0], dtype=int)*2. ) (all combinations possible (*1.2) ...)

    #~ print( img );
    img = np.reshape( img, (height, width) );
    img = np.array( img, dtype=np.uint8);
    #~ print( img );
    print( "max: %s" % str(np.max( img ) ));

    if( max > 40 and bVeryApproximative == True ):
        # there's blue, let's go to it ?
        return [0,0];

    kernel = np.ones((4,1),np.uint8)
    img = cv2.dilate( img, kernel, iterations = 1 );

    kernel = np.ones((2,1),np.uint8)
    img = cv2.erode( img, kernel, iterations = 1 );

    contours, hierarchy = cv2.findContours( img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    nNbrContours = len( contours );
    print( "nNbrContours: %s" % nNbrContours );
    if( nNbrContours > 2 ):
        print( "Too much contour, reducing image..." );
        if( True ):
            # write it:
            cv2.imwrite( strPathTestOut + "detectedblue.jpg", img );
        imgReduced = cv2.resize( originalImg, (0,0), fx=0.5, fy=0.5, interpolation = cv2.INTER_NEAREST );
        return detectBluePodRoughly( imgReduced, bVeryApproximative = bVeryApproximative, strPathTestOut = strPathTestOut + "_r_" );
    aContourProperties = [];
    for num, contour in enumerate(contours):
        print( "candidate: num: %s, contour: %s" % (num, contour) );

        m = cv2.moments(contour)
        # ** regionprops **
        rArea          = m['m00']
        #~ if( nArea < 2 ):
            #~ continue;
        print( "rArea: %s" % rArea );

        rPerimeter     = cv2.arcLength(contour,True)
        #~ if( nPerimeter < 2. ):
            #~ continue;
        print( "rPerimeter: %s" % rPerimeter );

        #~ Centroid      = ( m['m10']/m['m00'],m['m01']/m['m00'] )
        (x, y), rRadius = cv2.minEnclosingCircle(contour)
        #~ print( "x: %s" % x );
        #~ print( "y: %s" % y );
        print( "rRadius: %s" % rRadius );

        print( "x,y: %s, %s" % (x,y) );

        aContourProperties.append( [rArea, rPerimeter, rRadius, x, y ] );

    if( len( aContourProperties ) == 2 ):
        #~ if( aContourProperties[0][0] == 0 ):
            #~ # detected blobs are small
            #~ bTheTwoBlobsAreTheSameSize = (aContourProperties[0][:3] == aContourProperties[1][:3] );
        #~ else:
            #~ rDiff = 0;
            #~ for i in range( 3 ):
                #~ rDiff += abs(aContourProperties[0][i] - aContourProperties[1][i])/aContourProperties[0][i];
            #~ print( "rDiff: %s" % rDiff );
            #~ bTheTwoBlobsAreTheSameSize = ( rDiff < 0.3 );
        rDiff = abs( aContourProperties[0][2] - aContourProperties[1][2])/aContourProperties[0][2];
        print( "rDiff: %s" % rDiff );
        bTheTwoBlobsAreTheSameSize = ( rDiff < 0.3 );
        dx = abs( aContourProperties[0][3] - aContourProperties[1][3] );
        dy = abs( aContourProperties[0][4] - aContourProperties[1][4] );
        bSameHeight = dy < 7 and (dx>dy);
        if( bTheTwoBlobsAreTheSameSize and bSameHeight ):
            rDist = abs( aContourProperties[0][3] - aContourProperties[1][3] );
            print( "rDist: %s" % rDist );
            if( False ): # aContourProperties[0][0] < 1.3 ):
                bProportionRatioIsOk = abs( rDist - aContourProperties[0][1] * 2 ) < 2;
            else:
                rProportionDistRadius = rDist / aContourProperties[0][2];
                print( "rProportionDistRadius: %s" % rProportionDistRadius );
                bProportionRatioIsOk = (4.<= rProportionDistRadius <= 7.0) or rDist < 17; # theoric proportion is around 5
            if( bProportionRatioIsOk ):
                x = ( aContourProperties[0][3] + aContourProperties[1][3] ) / 2;
                y = ( aContourProperties[0][4] + aContourProperties[1][4] ) / 2;

                return[ (x / img.shape[1]) - 0.5, (y / img.shape[0]) - 0.5];

    if( True ):
        # write it:
        cv2.imwrite( strPathTestOut + "detectedblue.jpg", img );
    return retVal;
# detectBluePodRoughly - end

def detectBluePodRoughly_test( strPathTest, strPathTestOut ):
    strPathTest = strPathTest + "blue_pod\\";
    listFile = [
                    #~ "pod_low_intensity_01_2m", [-0.03125,-0.0708], # pb: bad wb balancy so white is a bit blue...
                    #~ "pod_low_intensity_02_3m5", [12,12], # should be seen ! (todo: compute the right position!)
                    #~ "pod_low_intensity_02_3m5_desaturate_glass", [12,12], # should be seen ! (todo: compute the right position!)

                    "pod_low_intensity_03_1m", [-0.128,0.195],
                    "pod_low_intensity_04_2m", [0.075,0.025],
                    "pod_low_intensity_05_3m5", [-0.025,0.308],
                    "pod_low_intensity_06_0m5", [-0.0156,-0.054],
                    "pod_low_intensity_07_0m5", [0.01875,0.0666],

                    "pod_low_intensity_07_1m", [0.025, 0.3375],
                    "pod_low_intensity_08_3m5", [-0.025, 0.308],
                    "pod_low_intensity_08b_3m5", [-0.025, 0.308],
                    "pod_low_intensity_09_1m5", [-0.128,0.195],
                    "pod_low_intensity_10_2m", [-0.40625, 0.0312],

                    "pod_low_intensity_10b_2m", [-0.395, -0.135],
                    "pod_low_intensity_10_flou_2m", [-0.128,0.195],

                    "pod_low_intensity_30_no_pod", [],
                    "pod_low_intensity_31_no_pod", [],
                    "pod_low_intensity_32_no_pod", [],

                    # 16th file
                    "/in_situ/pod/2014_08_01-14h56m21s418594ms.jpg", [-0.128,0.195],


                ];
    nCptSuccess = 0;
    nCptSuccessOfflineDetect = 0;
    aListOfflineDetected = [];
    for i in range( 15*2, len( listFile ) / 2 ):
        strImage = listFile[i*2+0];
        aWantedRes = listFile[i*2+1];
        strPathImage = strPathTest + strImage + ".jpg";
        print( "\n *** Analysing '%s.jpg'" % strImage );
        print( "aWantedRes: %s" % aWantedRes );
        if( True ):
            res = offlinePodDetect( strPathImage, strPathTestOut, bFindBluePod = True );
            print( "offlinePodDetect: res: %s" % str(res) );
            if( res != None ):
                avgPos = np.mean(res.projectedImPts, axis=1).mean(axis=0);
                print( "avgPos: res: %s" % str(avgPos) );
                res = [avgPos[1]/1280-0.5, avgPos[0]/960-0.5];
                if( abs(np.mean( np.array(res) - np.array(aWantedRes) )) < 0.08 ):
                    print( "SEEN OK " * 10 );
                    nCptSuccessOfflineDetect += 1;
                    aListOfflineDetected.append( strImage );
        if( True ):
            res = detectBluePodRoughly( cv2.imread( strPathImage ), strPathTestOut = strPathTestOut );
            print( "detectBluePodRoughly: res: %s" % res );
            bGood = False;
            if( res == None or res == [-1,-1] ):
                if( aWantedRes == [] ):
                    bGood = True;
            else:
                if( aWantedRes != [] ):
                    if( abs(np.mean( np.array(res) - np.array(aWantedRes) )) < 0.08 ):
                        bGood = True;
            if( bGood ):
                print( "GOOD !!!" );
                nCptSuccess += 1;
            else:
                print( "BAD !!!" );
                break;
            if( i == 3 ):
                # choose when to break the loop !
                pass
                #~ break;

    print( "nCptSuccess: %s" % nCptSuccess );
    print( "nCptSuccessOfflineDetect: %s" % nCptSuccessOfflineDetect );
    print( "aListOfflineDetected: %s" % aListOfflineDetected );
    # current list is:
    # without bFindBluePod:
    # aListOfflineDetected: ['pod_low_intensity_03_1m', 'pod_low_intensity_06_0m5', 'pod_low_intensity_07_0m5', 'pod_low_intensity_07_1m', 'pod_low_intensity_09_1m5']
    # with bFindBluePod
    # aListOfflineDetected: ['pod_low_intensity_03_1m', 'pod_low_intensity_07_0m5', 'pod_low_intensity_07_1m', 'pod_low_intensity_09_1m5']
    assert( nCptSuccess >= 15 );
    assert( nCptSuccessOfflineDetect >= 6 );
# detectBluePodRoughly_test - end

def _maskTrueIfOneInKernelIsTrue(aMask):
    """
    une methode qui va nous permettre de verifier qu'on a un au moins un bleu autour du point actuel..

    """
    nY = 10
    nX = 10
    kernel = np.ones((nX,nY),np.uint8)
    #kernel[int(nY/2), int(nX/2)] = 0
    nDepth = -1 # same depth as input image/mask
    aMask[aMask>0] = 1
    aFilter2D = cv2.filter2D(aMask, nDepth, kernel)  # convolution (sum)
    aMaskRes = np.array(aFilter2D > 20, dtype='uint8')  # si on a au moins 10 des pixels bleu
    aMaskRes[aMaskRes >0] = 255
    return aMaskRes

def _testMaskTrueIfOneInKernelIsTrue():
    aMask = np.zeros( (100,100) )

    aMask[8,8] = 10
    aResMask = _maskTrueIfOneInKernelIsTrue(aMask)
    import pylab
    pylab.figure()
    pylab.imshow(aMask)
    pylab.figure()
    pylab.imshow(aResMask)
    pylab.show()




def prepareImageForBluePodDetection(colouredImg):
    """
    takes a coloured image and output a bw image with (nearly) only the blue channel keeped
    return the bw image
    """
    # we work in hsv space and want to select Hue = blue http://i.stack.imgur.com/gCNJp.jpg  blue is between 180 degree and 240 in hue..

    if True:
        colouredImg = np.array(colouredImg, dtype=np.uint8)  # we use 8 bits so hsv values are between H: 0- (360/2), S: 0-255, V: 0-255
        img_hsv = cv2.cvtColor(colouredImg,  cv2.COLOR_BGR2HSV)
        #import IPython
        #IPython.embed()
        #cv2.imshow('hsv', img_hsv)
        #cv2.waitKey(0)
        #BLUE_MIN = np.array([170/2, 50, 50], np.uint8)  # we divide by 2 to be in opencv hsv range..
        # we detect real blue with a lot of color
        BLUE_MIN = np.array([170/2, 100, 0], np.uint8)  # we divide by 2 to be in opencv hsv range..
        #BLUE_MAX = np.array([310/2, 255, 255], np.uint8)
        BLUE_MAX = np.array([224/2, 255, 255], np.uint8)
        mask_blue = cv2.inRange(img_hsv, BLUE_MIN, BLUE_MAX)

        # then we look for Luminous point (blue or not)
        #WHITE_MIN = np.array([0, 0, 100], np.uint8)  # we divide by 2 to be in opencv hsv range..
        nVMinWhite = np.max(img_hsv[:,:,2]) / 2.0
        WHITE_MIN = np.array([0, 0, nVMinWhite], np.uint8)
        WHITE_MAX = np.array([179, 255, 255], np.uint8)
        mask_white = cv2.inRange(img_hsv, WHITE_MIN, WHITE_MAX)  # on prend du blanc la..

        # we check that luminous point ar near blue point.. if it's the case it's pod led
        pixelsNearBlue = _maskTrueIfOneInKernelIsTrue(mask_blue)
        mask_white_if_blue_near = cv2.bitwise_and(pixelsNearBlue, mask_white)

        # we keep white only if there is a blue pixel near it..
        mask = cv2.add(mask_blue, mask_white_if_blue_near)  # 0,0 -> 0; 0,255 -> 255; 255,255 -> 255
        #mask = mask_white
        #mask = mask_white_if_blue_near
        #mask[mask==1] = 0
        img_blue = cv2.bitwise_and(colouredImg,colouredImg, mask=mask)
        #img_hsv_filtered = cv2.bitwise_and(img_hsv, img_hsv, mask=mask)
        #whitePointsIMg = cv2.bitwise_and(img_hsv, img_hsv, mask=mask_white)
        #inverted_mask = cv2.bitwise_not(mask)
        #img_hsv_inverted = cv2.bitwise_and(img_hsv, img_hsv, mask=inverted_mask)
        #cv2.imshow('white', whitePointsIMg)
        #cv2.imshow('blue', img_hsv_filtered)
        #cv2.imshow('not', img_hsv_inverted)
        #cv2.imshow('out', img_blue)
        #cv2.imshow('inverted', img_hsv_inverted)
        #cv2.imshow('invertedH', img_hsv_inverted[:,:,0])
        #cv2.imshow('invertedS', img_hsv_inverted[:,:,1])
        #cv2.imshow('invertedV', img_hsv_inverted[:,:,2])
        #cv2.waitKey()
        img_bw= cv2.cvtColor(img_blue, cv2.COLOR_BGR2GRAY)

        #import IPython
        #IPython.embed()
        return img_bw, img_blue


    # convert the image keeping the blue information

    else:
        width = len(colouredImg[0]);
        height = len( colouredImg );


        img = np.reshape( colouredImg, (height*width,3) );
        # convert them in int on the fly, as we want to keep the sign to clip the negative value
        img = np.clip( np.array(img[:,0], dtype=int)*1.4 - img[:,1] - img[:,2], 0,255 ); # here you can choose if you want really blue,
                                                                                        # or somekind of nearly blue (somekind => multiply the blue array channel
                                                                                        # =>np.array(img[:,0], dtype=int)*2. ) (all combinations possible (*1.2) ...)
        #~ print( img );
        img = np.reshape( img, (height, width) );
        blueImg = np.array( img, dtype=np.uint8);
        # change range to match former version+
        nMax = np.max( blueImg );
        print( "max: %s" % str(nMax ));
        blueImg = blueImg*(255./nMax);
        blueImg = np.array(blueImg, dtype=np.uint8);
        return blueImg
# prepareImageForBluePodDetection - end


class PodLocator(object):
    """ locates pods using 6leds patterns in image coordinate
        Comments: !! 4kvga is recommended !!
            - *using 4kvga*: allow to detect the pod at 2 meter in straight line,
            1m50 using math.pi/4 angle, the maximum angle for 1 meter distance
            is near math.pi/6
            - *using vga*: allow to detect the pod at 0.9 m in straight line,
            0.9m using math.pi/4 angle, max angle at 0.9 near math.pi/4
        nCameraMode:
            - 0: auto lightning and white research
            - 1: fixed gain and white research (officially for red pod)
            - 2: fixed gain and blue pod research
    """
    def __init__(self, bDebug=False, resolution=camera.camera.k4VGA, camsToUse =['CameraTop', 'CameraBottom'], debugPath = '/tmp', timeOut=120, nCameraMode = 0, bVerbose=False ):
        self.bMustStop = False
        self.bRunning = False; # at least something is running (somewhere) (all method using bMustStop should enable this flag)
        self.bDebug = bDebug
        self.dbgImagePath = debugPath
        self.camerasToUse = camsToUse
        self.kResolution = resolution
        self.timeOutDuration = timeOut
        self.bVerbose = bVerbose;
        self.nCameraMode = nCameraMode;
        # old pod
      #  rA = np.array([-0.0525, -0.018, 0])
      #  rB = np.array([-0.0525, 0, 0])
      #  rC = np.array([-0.0525, 0.018, 0])
      #  rD = np.array([0.0525, 0.018, 0])
      #  rE = np.array([0.0525, 0.00, 0])
      #  rF = np.array([0.0525, -0.018, 0])

        rA = np.array([-0.052, -0.016, 0])
        rB = np.array([-0.052, 0, 0])
        rC = np.array([-0.052, 0.016, 0])
        rD = np.array([0.052, 0.016, 0])
        rE = np.array([0.052, 0.00, 0])
        rF = np.array([0.052, -0.016, 0])

        self.realObjectPts = np.array([rA,rB, rC, rD, rE, rF])
        self.ledPts = []
        self.strDebugFolder = "/home/nao/debug_pod_locator/";
        try:
            os.makedirs( self.strDebugFolder );
        except: pass # folder already exist

        self._aSetCameraSubscribed = set()  # list of subscribed camera

    def __del__(self):
        print( "INF: abcdk.pod.PodLocator: deleting..." );
        self.stop()

    def stop(self, timeout=0):
        """ return True if it was running, and stop it"""
        if( not self.bMustStop ):
            self.bMustStop = True;
            print( "INF: abcdk.pod.PodLocator: stopping..." );
            if( self.bRunning ):
                print( "INF: abcdk.pod.PodLocator: stopping running thread..." );
                ## ??? ici il manque des stop non ?
                self.setCameraModeForPod( False );
                #camera.camera.unsubscribeCamera(0)
                #camera.camera.unsubscribeCamera(1)
                time.sleep(timeout) ## wait all code is stopped

            for tupleSubscribedCamera in self._aSetCameraSubscribed:
                print("INFO: Unsubscribing %s" % str(tupleSubscribedCamera))
                camera.camera.getImageCV2_unsubscribeCamera(*tupleSubscribedCamera)
            return True
        return False

    def setCameraModeForPod( self, bSet = True ):
        """
        put the setting allowing camera to detect the pod or reset it to "normal settings"
        - bSet: True: set it for us, False: set it for normal use
        """
        if( bSet ):
            if( self.nCameraMode == 0 ):
                camera.camera.setFullAuto(0); # ensure to reset camera to auto
                camera.camera.setFullAuto(1);
            else:
                if( self.nCameraMode == 1 ):
                    # settings to detect the red pod using the quicker exposure time
                    nGain = 250;
                    nExposureTimeMs = 4;
                    nWB = 2700;
                elif( self.nCameraMode == 2 ):
                    # settings to detect the blue pod using the quicker exposure time
                    #nGain = 255;
                    nExposureTimeMs = 50; # current bug !?!: when too dark, the image becomes as in grey level (or normal due to poor sensibility)
                    ## 50 seems to provide good results..
                    #nWB = 6500;
                else:
                    raise( BaseException( "Wrong camera mode TODO: good user msg" ) );
                avd = naoqitools.myGetProxy( "ALVideoDevice" );
                cam = camera.camera;
                nNumCamera = 0;
                avd.setParameter( nNumCamera, cam.kCameraAutoExpositionID, 0 );
                avd.setParameter( nNumCamera, cam.kCameraExposureID, nExposureTimeMs*2 );

                #avd.setParameter( nNumCamera, cam.kCameraGainID, nGain );
                #avd.setParameter( nNumCamera, cam.kCameraAutoWhiteBalanceID, 0 );
                #avd.setParameter( nNumCamera, cam.kCameraWhiteBalanceID, nWB ); # WRN: this line needs the last sdk >= 1.22.3 to function correctly
        else:
            camera.camera.setFullAuto(0);
            camera.camera.setFullAuto(1);


    @staticmethod
    def pointMatch6PointsRectangular(l):
        """ return the oriented polygon of 6 points
            A : up/left
            B: middle/left
            C: bottom/left
            D: bottom/right
            E: middle/right
            F: up/right

        Args: l : list of points (with pt.x and pt.y to get x and y coordinate)
        Test:
            l = [[5,8],[1,-1],  [2,-1], [1,1], [2,1], [1+8,-1+8],  [2+8,-1+8], [1+8,1+8], [2+8,1+8]]
            b = pointMatch4PointsRectangular(l)
        """
        #l = np.array(l)
        res = []

        if len(l) < 6:
            return None
        for num, curPt in enumerate(l):
            pts = []
            for pt in l:
                if curPt != pt and (curPt.area * 0.3 < pt.area < curPt.area * (1 + 0.7) ) and curPt.val - 12 < pt.val < curPt.val + 12: # change -4 +4 en -12/+12 for val
                #if curPt != pt and curPt.val - 4 < pt.val < curPt.val + 4 :
            #    if curPt!=pt:
                    pts.append((pt.x, pt.y))
                #~ else:
                    #~ print( "curpt pas bon: curPt.area: %s, pt.area: %s" % (curPt.area, pt.area) );
                    #~ print( "curpt pas bon: curPt.val: %s, pt.val: %s" % (curPt.val, pt.val) );
                    #~ pass

            if len(pts) < 5:
                pts = [(a.x, a.y) for a in l]
                pts.pop(num)
                #continue
            othersPts = np.array(pts)

            #print "othersPts", str(othersPts)
            dists = np.sqrt((othersPts[:, 0] - curPt.x)**2 + (othersPts[:, 1]- curPt.y)**2)
            othersPts_sortedByDistance = othersPts[np.argsort(dists)]
            fiveClosestPts = othersPts_sortedByDistance[0:5]

            sixPoints = np.vstack([fiveClosestPts, [curPt.x, curPt.y]])
            #print "fourPoints", str(fourPoints)
            threeOnLeft = sixPoints[np.argsort(sixPoints[:,0])][0:3]
            threeOnRight = sixPoints[np.argsort(sixPoints[:,0])][3:6]

            threeOnLeft = threeOnLeft[np.argsort(threeOnLeft[:,1])]  # sorted
            threeOnRight = threeOnRight[np.argsort(threeOnRight[:,1])] #sorted

            A = threeOnLeft[0]
            B = threeOnLeft[1]
            C = threeOnLeft[2]
            D = threeOnRight[2]
            E = threeOnRight[1]
            F = threeOnRight[0]
            a =  np.array([A,B,C,D,E,F])
            if any((a == x).all() for x in res):
                pass   #Already in the list
            else:
                res.append(a)
        #~ print( "DBG: pointMatch6PointsRectangular: return: %s" % res );
        return res

    @staticmethod
    def scoreRectangle(pts):
        """ Return a score for POD pattern..

        Args:
            pts: list of pod pod patterns point (6 points in image coordinate)

        Returns:
            score : None if rectange could not be a pod patterns, area of
            patterns otherwise.
        """
        A,B,C,D,E,F = np.array(pts)

        thAligned = math.pi/30 # Alma: change /40 in /30
        epsilonAngle = math.pi/40

        ## check 3 points aligned left/right
        isAlignedLeft = abs(numeric.computeVectAngle( (C-A), (B-A) )) < thAligned
        isAlignedRight = abs(numeric.computeVectAngle( (E-F), (D-F) )) <  thAligned

        #~ print( str( numeric.computeVectAngle( (C-A), (B-A) ) ) )

        ## check left and right close to parallel
        isParallel = numeric.computeVectAngle((C-A), (E-F)) < math.pi / 8.0

        internalsAngles = np.array([numeric.OrientedAngle(A,F,D),
                           numeric.OrientedAngle(F,D,C),
                           numeric.OrientedAngle(D,C,A),
                           numeric.OrientedAngle(C,A,F)])

        isAngleSumCorrect = (abs(np.sum(internalsAngles)) - (2*math.pi)) < epsilonAngle
        isWellOrrientated = np.all(internalsAngles > 0) or np.all(internalsAngles < 0)
        isSmallAngle = np.all(abs(internalsAngles) < math.pi)

        distanceTh = 20
        isPtInMidleLeft  = abs(numeric.dist2D(A,B) - numeric.dist2D(B,C)) < distanceTh
        isPtInMidleRight = abs(numeric.dist2D(D,E) - numeric.dist2D(E,F)) < distanceTh

        lenMin = 50
        isBigEnough = (numeric.dist2D(A,F) > lenMin) and (numeric.dist2D(C,D)>lenMin)

        #~ print( "scoreRectangle: isAlignedLeft: %s" % isAlignedLeft );
        #~ print( "scoreRectangle: isAlignedRight: %s" % isAlignedRight );
        #~ print( "scoreRectangle: isParallel: %s" % isParallel );
        #~ print( "scoreRectangle: isAngleSumCorrect: %s" % isAngleSumCorrect );
        #~ print( "scoreRectangle: isWellOrrientated: %s" % isWellOrrientated );
        #~ print( "scoreRectangle: isBigEnough: %s" % isBigEnough );
        #~ print( "scoreRectangle: isBigEnough: %s" % isBigEnough );


        if isBigEnough and isAlignedLeft and isAlignedRight and isAngleSumCorrect and isWellOrrientated and isSmallAngle and isPtInMidleLeft and isPtInMidleRight and isParallel:
            return cv2.moments(np.array([pts], dtype='float32'))['m00']  # l'aire..
        return None


    @staticmethod
    def bestRectangle(ledPts):
        """ returns the bestledPatterns in the list ledPts using
        scoreRectangle method.
        Returns:
            a list of points (6 points)
        """
        if ledPts!=None and len(ledPts)>0:
            scores = [PodLocator.scoreRectangle(pts) for pts in ledPts]
            print( "scores: %s" % scores );
            index = np.argsort(scores)
            bestIndex = index[-1]
            if scores[bestIndex] != None:
                return ledPts[bestIndex]

    def _locatePodOneShot(self, camName='CameraTop'):
        """ return pod pattern location
        Args:
            camName: CameraTop or CameraBottom
        Returns:
        """
        self.bRunning = True;
        if camName == 'CameraTop':
            numCam = 0
        elif camName == 'CameraBottom':
            numCam = 1
        else:
            print( "ERR: abcdk.pod.PodLocator.locatePodOneShot: cameraNameUnknown")
            return

        motionProxy = naoqitools.myGetProxy( "ALMotion")
        if self.bMustStop:
            self.bRunning = False;
            return None
        try:
            cameraImage = None;
            if self.bDebug or self.nCameraMode == 2:
                nColorSpace = 13
                cameraImageColored = camera.camera.getImageCV2(nImageResolution = self.kResolution, nCamera = numCam, colorSpace=nColorSpace, bNoUnsubscribe=True,bVerbose=self.bVerbose)
                aTupleUseForCameraSubscribing = (self.kResolution, numCam, nColorSpace)
                self._aSetCameraSubscribed.add(aTupleUseForCameraSubscribing)

                if( cameraImageColored != None ):
                    if( self.nCameraMode == 2 ):
                        cameraImage = prepareImageForBluePodDetection(cameraImageColored)[0];
                    else:
                        cameraImage = cv2.cvtColor( cameraImageColored, cv2.COLOR_BGR2GRAY );
            else:
                nColorSpace = 0
                cameraImage = camera.camera.getImageCV2(nImageResolution = self.kResolution, nCamera = numCam, colorSpace=nColorSpace, bNoUnsubscribe=True, bVerbose=self.bVerbose );
                aTupleUseForCameraSubscribing = (self.kResolution, numCam, nColorSpace)
                self._aSetCameraSubscribed.add(aTupleUseForCameraSubscribing)
        except BaseException, err:
            print( "ERR: abcdk.pod.PodLocator.locatePodOneShot: catching this error: %s" % err );
        camPos6D = motionProxy.getPosition(camName, 0, True)
        torsoPose6D = motionProxy.getPosition('Torso', 1, True)
        if self.bMustStop:
            self.bRunning = False;
            return None

        if cameraImage == None:
            print( "ERR: abcdk.pod.PodLocator.locatePodOneShot: image is empty !!!" );
            debug.raiseCameraFailure();
            self.bRunning = False;
            return None;

        if self.bDebug:
            name = filetools.getFilenameFromTime()
            filename =  self.strDebugFolder + name + "_arig.jpg";
            cv2.imwrite(filename, cameraImageColored)
            pickleFileName = os.path.splitext(filename)[0]
            pickleFileName += '.pickle'
            serialization_tools.saveObjectToFile([self.realObjectPts, self.kResolution, camPos6D, torsoPose6D], pickleFileName)

        ledPts, thresholdImg, rectangle = infraLedDetector(cameraImage, bFindBluePod=(self.nCameraMode==2) )
        if self.bMustStop:
            self.bRunning = False;
            return None
        #rectangle = PodLocator.bestRectangle(PodLocator.pointMatch6PointsRectangular(ledPts))
        if self.bMustStop:
            self.bRunning = False;
            return None
        if rectangle == None:
            self.bRunning = False;
            return None
        else:
            pnpOpencv = imagePnp.getPnP(rectangle, self.realObjectPts, nResolution=self.kResolution)
            if self.bDebug:
                if pnpOpencv!=None:
                    i = 0
                    for (x,y) in rectangle:
                        cv2.circle(cameraImage, (int(x), int(y)), i+2, (0,200,80), 2)
                        i+=2
            if pnpOpencv == None:
                #print "pod not found in this image"
                self.bRunning = False;
                return None
            if self.bDebug:
                circleFilename = self.strDebugFolder + name + '._circle.jpg'
                #print "filemm.. %s" % circleFilename
                cv2.imwrite(circleFilename, cameraImage)
        self.bRunning = False;
        return pnpOpencv, camPos6D, torsoPose6D

    def locate(self):
        """ Locates the pod.
        Returns:
            - 6 points (A,B,C,D,E,F, in image coordinate) that corresponds to the
            pods leds pattern where A is top left and F top Right
            - cameraUse: camera's name of used camera
            - cam6d : position of cam relative to torso
            - torso6D: position of torso relative to world
            or None if time out
        """
        self.bMustStop = False;
        self.bRunning = True;
        podLocation = None
        timeLastPodSeen = time.time();
        self.setCameraModeForPod( True );
        while( podLocation == None ):
            if( self.bVerbose ):
                print("DBG: abcdk.pod.PodLocator.locate: instance %s: looping..."  % self );
            for cam in self.camerasToUse:
                if (self.bMustStop):
                    self.bRunning = False;
                    return None
        #        print "cam", str(cam)
                podLocation = self._locatePodOneShot(cam)
                if podLocation != None:
                    self.bRunning = False;
                    return podLocation[0], cam, podLocation[1], podLocation[2]
            rTimeSinceLast = time.time() - timeLastPodSeen;
            if( rTimeSinceLast > self.timeOutDuration ):
                print("INF: abcdk.pod.PodLocator.locate: timeout ! (%5.3fs elapsed)" % rTimeSinceLast );
                break;
        # while - end
        self.bRunning = False;
        return podLocation;
    # locate - end

# class PodLocator - end

class Poder(object):
    def __init__(self, bDebug=True, res = camera.camera.k4VGA, camerasToUse=['CameraTop'], numTrialId = None , timeOut=600, nCameraMode = 0, bVerbose=False ):
        """
        - nCameraMode: 0: auto, 1: IR fixed setting, 2: Blue fixed setting
        """
        self.podDistanceX =  0.32
        self.backwardStepDistance = self.podDistanceX - 0.10;  # 13-11-13 Alma: adding a bit (was -0.14)

        self.curAsynchThread = None  # asynch thread object to run panner in a parallel thread
        self.motionProxy = naoqitools.myGetProxy( "ALMotion")
        self.mem = naoqitools.myGetProxy( "ALMemory" );
        self.resolution = res
        self.camerasToUse = camerasToUse
        self.bMustStop = False
        self.bRunning = False; # at least something is running (somewhere)
        self.timeOutDuration = timeOut
        self.bDebug = bDebug
        self.bVerbose = bVerbose;
        self.nCameraMode = nCameraMode;
        self.podLocator = PodLocator(bDebug=self.bDebug, resolution=self.resolution, camsToUse=self.camerasToUse, timeOut = self.timeOutDuration, nCameraMode = self.nCameraMode, bVerbose=bVerbose);

        self.panner = motiontools.Panner( rPanSpeed = 0.034, rBaseHeadPitch=0.45, rRangeHeadPitch = 0.4 );
        self.headSeeker = motiontools.HeadSeeker()
        self.numTrialId = numTrialId ## num id of current poder trial !
        self.strDebugFolder = "/home/nao/debug_poder/";
        try:
            os.makedirs( self.strDebugFolder );
        except: pass # folder already exist

        if self.numTrialId != None:
            self.csvFileName = self.strDebugFolder + "debug_poder_id_" + str(self.numTrialId) + "_" + filetools.getFilenameFromTime() + '.csv'
        else:
            self.csvFileName = self.strDebugFolder + "cur.csv";
        self.csvFileNameAll = self.strDebugFolder + "all_detailed.csv";

    def __del__(self):
        print( "INF: abcdk.pod.Poder: deleting..." );
        self.stop();

    def stop(self, timeout=0.4):
        """ Stop the pod go and sit and also waitUntilCharged.

        Return:
            True if it was running, and stopped.
        """
        if( not self.bMustStop ):
            print( "INF: abcdk.pod.Poder: stopping..." );
            self._saveToCsv( 'stop has been called... *** END (soon)' );
            self.bMustStop = True
            if( self.bRunning ):
                print( "INF: abcdk.pod.Poder: stopping running thread..." );
                if self.curAsynchThread !=None:
                    self.curAsynchThread.stop(0)
                self.panner.stop()
                self.headSeeker.stop()
                self.podLocator.stop(timeout=0)
                self.motionProxy.stopMove()  # it also stop backwardStep
                time.sleep(timeout) ## wait all code is stopped
            print( "INF: abcdk.pod.Poder: stop - end" );
            return True
        return False


    def isSitting( self ):
        sitPos = motiontools.getLastPositionFromAnimation( self._getSitOnPodMovement() );
        rDistToPose = poselibrary.PoseLibrary.comparePosition( sitPos , aListGroupToIgnore=["UpperBody"] );
        bIsSitting = rDistToPose < 0.24; # 0.07 should be enough, was 0.23 (0.268: it's a standinit position !!!)
        rAngleY = self.mem.getData( "Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value" );
        bIsSitting &= (rAngleY > -0.7 and rAngleY < -0.25);

        print( "DBG: abcdk.pod.isSitting: dist to sit: %f, rAngleY: %f, bIsSitting: %s" % ( rDistToPose, rAngleY, bIsSitting ) );
        return bIsSitting;
    # isSitting - end

    def checkFall( self ):
        if( motiontools.hasFall() ): # can't check this while sitting (unknown posture family)
            self._saveToCsv( 'fall' );
            self.bMustStop = True;
    # checkFall - end


    def goAndSit(self):
        """
        Find the pod and sit on it.

        The pod should be in visible area (between 0.30 to 1 meter from the robot)

        Return:
            True when succeed. False otherwise
        """
        self.bMustStop = False;
        self._saveToCsv('goAndSit', 'starting *** BEGIN')

        if( self.isSitting() or system.isPlugged() ):
            self._saveToCsv('isSitting', 'True')
            return True

        global module_mutex;
        if( module_mutex.testandset() == False ):
            self._saveToCsv( 'goAndSit', 'already running... Leaving...' );
            return False;

        self.bRunning = True;

        # on cree un nouvel podLocator a chaque fois..
        bRet = False;
        posture = naoqitools.myGetProxy("ALRobotPosture")
        for _ in xrange( 3 ): # so we'll try 9 times (we dont change setMaxTryNumber, as it will change globally the settings)
            if self.bMustStop:
                self.bRunning = False;
                module_mutex.unlock();
                return False
            bSuccess = posture.goToPosture("StandInit", 0.8)
            if bSuccess:
                print("DEBUG: abcdk.pod.goAndSit goToPosture StandInit: return: %s" % bSuccess)
                break
            time.sleep( 0.5 );
        else:
            print("DEBUG: abcdk.pod.goAndSit goToPosture fail")
            self.bRunning = False;
            module_mutex.unlock();
            return False  ## unable to wakeUp.. we return False and quit


        if self.bMustStop:
            self.bRunning = False;
            module_mutex.unlock();
            return False
        if( self.bVerbose ):
            speech.sayAndLight(translate.chooseFromDict({'en':"I am going to charge my battery.", 'fr':"Je vais aller me recharger."}))
        if self.numTrialId != None:
            if( self.bVerbose ):
                speech.sayAndLight("TRIAL %s" % str(self.numTrialId))

        self._saveToCsv('goToPod', 'start')
        bNearPod = self._goToPod(x=self.podDistanceX)
        self._saveToCsv('goToPod', 'stop')
        if self.bMustStop:
            self.bRunning = False;
            module_mutex.unlock();
            return False

        if not bNearPod:
            if( self.bVerbose ):
                speech.sayAndLight(translate.chooseFromDict({'en':"Something went wrong.", 'fr':"Je n'y arrrive pas"}))
            print("Stop requested (%s) or error" % self.bMustStop)
            self.bRunning = False;
            module_mutex.unlock();
            return False

        if bNearPod:

            if( self.isSitting() ):
                self._saveToCsv('isSitting', 'True')
                self.bRunning = False;
                module_mutex.unlock();
                return True

            if( self.bVerbose ):
                speech.sayAndLight(translate.chooseFromDict({'en':"I am well positioned.", 'fr':"Je suis bien placé."}))
            names  = ["HeadYaw", "HeadPitch"]
            angles  = [0.0, 0.0]
            fractionMaxSpeed  = 0.2
            self.motionProxy.angleInterpolationWithSpeed(names, angles, fractionMaxSpeed)

            self._saveToCsv('MoveTango', 'start')
            self._moveTango()  # on leve les bras
            self.checkFall();
            if self.bMustStop:
                self.bRunning = False;
                module_mutex.unlock();
                return False
            self._saveToCsv('MoveTango', 'stop')
            time.sleep(2)
            self._saveToCsv('rotateForPod', 'start')
            rotationSuccess = self._rotateForPod( angles=[math.pi-math.pi/6.0] );
            self.checkFall();
            if self.bMustStop:
                self.bRunning = False;
                module_mutex.unlock();
                return False
            self._saveToCsv('rotateForPod', 'stop succes?: %s' % str(rotationSuccess))
            self.motionProxy.setWalkArmsEnabled(True, True)
            if rotationSuccess:
                self._saveToCsv('backwardStep', 'start')
                self._backwardSteps(distance=self.backwardStepDistance)
                self.checkFall();
                if self.bMustStop:
                    self.bRunning = False;
                    module_mutex.unlock();
                    return False
                self._saveToCsv('backwardStep', 'stop')
                if( self.bVerbose ):
                    speech.sayAndLight(translate.chooseFromDict({'en':"Ok, now I can sit.", 'fr':"Ok, maintenant je vais m'assoir."}))
                self._saveToCsv('sitOnPod', 'start')
                self.sitOnPod()
                self._saveToCsv('sitOnPod', 'stop')
                self._saveToCsv('checkCharging', 'start')
                bRet = self._checkPluggedOrMoveABit();
                self._saveToCsv('checkCharging', 'stop')
                if bRet:
                    if( self.bVerbose ):
                        speech.sayAndLight(translate.chooseFromDict({'en':"Charging.", 'fr':"Je me recharge."}))
        self.bRunning = False;
        self._saveToCsv('goAndSit', 'finished *** END');
        module_mutex.unlock();
        return bRet;
    # goAndSit - end


    def waitUntilCharged(self, rMinimalChargeLevelToReach = 0.8 ):
        """
        Wait until the battery is fully recharge, if it's the case stand from pod.
        - rMinimalChargeLevelToReach: level minimal to finish to charge [0..1]

        Warning: this method should be call only if the robot is on the pod

        Return True when charge is complete
        """
        self.bMustStop = False;
        global module_mutex;
        if( module_mutex.testandset() == False ):
            self._saveToCsv( 'waitUntilCharged', 'already running... Leaving...' );
            return False;

        self.bRunning = True;
        strMemWaitInProgress = "PowerStation/WaitUntilCharged";
        #speech.sayAndLight(translate.chooseFromDict({'en':"Charging.", 'fr':"En charge."}))
        self._saveToCsv( 'charging', 'start' );
        self.mem.insertData( strMemWaitInProgress, True );


        rMinimalChargeLevelToReach = min( rMinimalChargeLevelToReach, 1. );

        nCpt = 0
        while( True ):
            if( self.bVerbose ):
                print("DBG: abcdk.pod.Poder.waitUntilCharged: instance %s: looping..."  % self );

            if( not self._checkPluggedOrMoveABit() ):
                self.mem.insertData( strMemWaitInProgress, False );
                self.bRunning = False;
                module_mutex.unlock();
                return False;

            rCurrentCharge = system.getBatteryLevel();
            if( rCurrentCharge >= rMinimalChargeLevelToReach and nCpt >= 7 ):
                break;
            #self._randomFunSentence()
            #print "waiting.. battery charging"
            rTime = 1.;
            leds.dcmMethod.setEarsLoading( rCurrentCharge, rTime, bHadAnimatedChest = True );
            time.sleep( rTime );
            nCpt += 1;
            if self.bMustStop:
                self.mem.insertData( strMemWaitInProgress, False );
                self.bRunning = False;
                module_mutex.unlock();
                return False;
        # while - end
        self.mem.insertData( strMemWaitInProgress, False );
        self._saveToCsv('charging', 'stop')
        #speech.sayAndLight(translate.chooseFromDict({'en':"Full battery. I am ready for action.", 'fr':"Mes batteries sont pleines. Je suis prêt."}))
        if( self.bVerbose ):
            speech.sayAndLight(translate.chooseFromDict({'en':"Full battery.", 'fr':"Mes batteries sont pleines."}))
        if self.bMustStop:
            self.bRunning = False;
            module_mutex.unlock();
            return False
        self._saveToCsv('standFromPod', 'start')
        self._standFromPod()
        self._saveToCsv('standFromPod', 'stop')
        self.bRunning = False;
        module_mutex.unlock();
        return True;
    # waitUntilCharged - end

    def _saveToCsv(self, strEventName, value = "" ):
        print( "INF: _saveToCsv: event: %s, value: %s" % ( strEventName, value ) );
        import datetime
        strHour = datetime.datetime.now().strftime( "%Hh%Mm%Ss" );
        strToWrite = strHour + "," + strEventName + "," + str( value );
        with open(self.csvFileName, 'a') as f:
            print( strToWrite, file=f );
            f.close();
        strDate = datetime.datetime.now().strftime( "%Y_%m_%d-" );
        strToWrite = strDate+strToWrite;
        with open(self.csvFileNameAll, 'a') as f:
            print( strToWrite, file=f );
            f.close();
            return True;
        return False;
    # _saveToCsv - end

    def _goToPod(self, x = 0.40, y = 0.00, theta = math.pi/6.0, bUseWholeBody=True):
        """
        Positionate near the pod (eg. 0.40 m on x axis)
        return True if we succeed (to positionnate near the pod)
        """
        tracker = naoqitools.myGetProxy("ALTracker")
        camera.camera.setFullAuto(0, 2)
        camera.camera.setFullAuto(1, 2)

        moveThreshold = 0.015;  # 13-10-23 Alma: was 0.01 (1cm)
        angleThreshold = math.pi / 30.0;
        frameTorso = 0;
        frameWorld = 1;
        effector_id = 0; #  addParam("pEffectorId","effector id {Middle of eyes = 0, Camera Top = 1, "Camera Bottom = 2}.");
        speed=0.3;

        bLookAround = True
        bRet = False;

        while True:
            if( self.isSitting() ):
                self._saveToCsv('isSitting', 'True')
                bRet = True;
                break;

            if( self.bVerbose ):
                print("DBG: abcdk.pod.Poder._goToPod: instance %s: looping..."  % self );
                
            self.motionProxy.setExternalCollisionProtectionEnabled( "All", False );
            motiontools.setFallManagerState(True);
            self.checkFall();

            if self.bMustStop:
                break;
            if bLookAround:
                ## look and turn at the beginning..
                self.curAsynchThread = system.asyncEval('self.panner.run()', globals(), locals())
            else:
                ## just move the head using headSeeker
                self.curAsynchThread = system.asyncEval(['time.sleep(2)', 'print("INF: headseeker...")', 'self.headSeeker.run()', 'print("INF: Now big move...")', 'self.panner.run()'], globals(), locals()) ## ajouter un timeWait au debut ?


            self.podLocator.camerasToUse = self.camerasToUse
            resPosLocator = self.podLocator.locate()

            if self.curAsynchThread !=None:
                self.curAsynchThread.stop(0)
            self.headSeeker.stop();
            self.panner.stop();
            #self.podLocator.bDebug=False ## pas besoin des images quand ca marche

            if resPosLocator == None:
                self._saveToCsv('_goToPod', 'pod not found (timeout?)')
                break;
            pnpOpencv, cameraUsed, imgCam6dToTorso, imgTorso6D = resPosLocator
            if cameraUsed == 'CameraBottom':
                effector_id = 2
            elif cameraUsed == 'CameraTop':
                effector_id = 1
            else:
                effector_id = 0

            if pnpOpencv == None :
                print("error pnp.. continuing")
                continue

            if self.bMustStop:
                break;

            if bLookAround:
                if( self.bVerbose ):
                    speech.sayAndLight(translate.chooseFromDict({"en":"Cool, I have seen my powerstation!", "fr":"Super, j'ai vu ma station de rechargement."}))
                bLookAround = False

            # compute pod position
            curTorsoPose6D = self.motionProxy.getPosition('Torso', frameWorld, True)
            diffPos6D = np.array(imgTorso6D) - np.array(curTorsoPose6D) # in FrameWorld
            diffDx, diffDy, diffDz, diffDwx, diffDwy, diffDwz = diffPos6D
            camDx, camDy, camDz, camDwx, camDwy, camDwz = imgCam6dToTorso
            objOrientation, objTranslation = numeric.chgRepereT(pnpOpencv.orientation, pnpOpencv.translation, camDx + diffDx, camDy + diffDy, camDz + diffDz, camDwx + diffDwx, camDwy + diffDwy, camDwz + diffDwz)

            # looks at the pod before the move
            pos = [objTranslation[0], objTranslation[1], objTranslation[2]]

            try:
                tracker._lookAtWithEffector(pos, frameTorso, effector_id, speed, bUseWholeBody)
            except:
                tracker.lookAt(pos, speed, bUseWholeBody)

            time.sleep( 0.1 ); # stabilize a bit!

            if self.bMustStop:
                break;

            # moves
            bTestRotate = False
            if not(bTestRotate):
                if self.bMustStop:
                    break;
                distanceToPod = np.sqrt(objTranslation[0]**2 + objTranslation[1]**2)
                if distanceToPod > 1.0:
                    cmOrder = imagePnp.getPoseMove(objTranslation, objOrientation, x=x, y=y, torsoOrientation=None, thresholdMove=0.4)  # we look at the pod
                    print("I am far (%f) using specific orientation (%f) i.e. direction to pod" % (distanceToPod, cmOrder.rotationTorso))
                else:
                    cmOrder = imagePnp.getPoseMove(objTranslation, objOrientation, x=x, y=y, torsoOrientation=theta)
                    print(" I am near pod. (%f). ok rotation" % distanceToPod)

                if not(abs( cmOrder.moveX ) > moveThreshold or abs( cmOrder.moveY ) > moveThreshold or abs( cmOrder.rotationTorso ) > angleThreshold ):
                    print("Positionate Done")
                    bRet = True;
                    break;
                if self.bMustStop:
                    break;
                if( distanceToPod < 0.50 ):
                    self._moveArmsThink();
                    self.motionProxy.setWalkArmsEnabled(False, False)
                else:
                    self.motionProxy.setWalkArmsEnabled(True, True)
                self.motionProxy.moveTo(cmOrder.moveX, cmOrder.moveY, cmOrder.rotationTorso)
                if self.bMustStop:
                    break;
                # looks at the pod after the move
                try:
                    tracker._lookAtWithEffector(cmOrder.afterMoveObjPos, frameTorso, effector_id, speed, bUseWholeBody)
                except: # if not available
                    tracker.lookAt(cmOrder.afterMoveObjPos, speed, bUseWholeBody);
                if self.bMustStop:
                    break;
                time.sleep( 0.6 ); # stabilize!

        # end while

        camera.camera.setFullAuto(0)
        camera.camera.setFullAuto(1)
        camera.camera.unsubscribeCamera(0)
        camera.camera.unsubscribeCamera(1)
        return bRet;
    # _goToPod - end


    def _rotateForPod(self, angles = [math.pi, -math.pi], methodToUse = 'moveCalibrated', angleEpsilon = math.pi/60.0, enableArms=False):
        """
        Try to use visual Compass to do the rotate, if fail use calibrated rotate

        Args:
            angle: angle of desired rotation

        do the rotation, return True if success.. False otherwise.
        """
        self.motionProxy.setWalkArmsEnabled(enableArms, enableArms)  # deactivate arms
        if methodToUse == 'moveCalibrated':
            moveCalibrated = motiontools.getMoveCalibrated(0, 0, angles[0] );
            speedConfig = getMoveConfig('stableRotation')
            self.motionProxy.moveTo(moveCalibrated[0], moveCalibrated[1], moveCalibrated[2], speedConfig)
            return True

        if methodToUse == 'visualCompass':
            ## DEprecated..
            compass = naoqitools.myGetProxy("ALVisualCompass")

            #checking left and right for best image
            quality = []
            for angle in angles:
                self.motionProxy.angleInterpolationWithSpeed("HeadYaw", [angle/2.0], 0.5)
                time.sleep(0.1)
                compass.setCurrentImageAsReference()
                print("Quality return: %s" % str( compass.getMatchingQuality() ))
                quality.append([angle] + compass.getMatchingQuality())
            quality = np.array(quality)
            #angleToUse = quality[quality[:,2].argsort()][-1][0]  # on trie par le inliner score
            angleToUse = angles[0]/2.0
            print("OK using angle: %s" % str(angleToUse))

            # doing rotation with retry if fail..
            compass._setOdometryMode(True)  # desactive le mode terminer le movt sans compas
            angleDone = 0  # angle allready done
            newData = self.mem.insertData("VisualCompass/FinalDeviation", None)
            while (abs(abs(angleToUse) - abs(angleDone)) > angleEpsilon) and (not(self.bMustStop)):
                compass.moveTo(0, 0, absMin(angleToUse - angleDone, angleToUse))
                time.sleep(1)
                newData = self.mem.getData("VisualCompass/FinalDeviation")
                print("getting data done %s" % str(newData))
                ## pressed_key = raw_input()  # for debugging purpose
                self.mem.insertData("VisualCompass/FinalDeviation", None)
                if newData == None:
                    return False
                    #time.sleep(1)
                    #return False
                if newData[1] != 0:
                    print("RETRY... !")
                    angleDone += newData[1]
                if newData[1] == 0:
                    print("lost")
                    return False
                ## we set FinalDeviation to None, as we do not use event here.
            print("angle parcouru %f" % (angleDone))
            return True
        return True ## TODO : etrange on ne devrait pas avoir besoin du true ici..


    def _backwardSteps(self, distance=0.22, methodToUse='moveCalibrated'):
        """
        Args:
            methodToUse: visualCompass or 'moveCalibrated'
        """
        if methodToUse == 'visualCompass':
            ## deprecated
            compass = naoqitools.myGetProxy("ALVisualCompass")
            compass.moveStraightTo(-distance)  # est ce que ca peut fail ??? si oui si lost il se passe quoi ?
        if methodToUse == 'moveCalibrated':
            moveCalibrated = motiontools.getMoveCalibrated( -distance, 0, 0 );
            speedConfig = getMoveConfig('stableMoveX')
            self.motionProxy.moveTo(moveCalibrated[0], moveCalibrated[1], moveCalibrated[2], speedConfig)

    def checkPluggedOrMoveABit( self, bHasRightToStand = True ):
        """
        return True if plugged (loop while trying)
        """
        global module_mutex;
        if( module_mutex.testandset() == False ):
            self._saveToCsv( 'checkPluggedOrMoveABit', 'already running... Leaving...' );
            return False;
        self.bRunning = True;
        ret = self._checkPluggedOrMoveABit( bHasRightToStand = bHasRightToStand );
        self.bRunning = False;
        module_mutex.unlock();
        return ret;

    # checkPluggedOrMoveABit - end

    def _checkPluggedOrMoveABit( self, bHasRightToStand = True ):
        """
        internal - no armored
        """
        nCpt = 0;
        nMaxRetry = 12;
        bWasNotCharging = False;
        while( nCpt < nMaxRetry ):
            if( self.bVerbose ):
                print("DBG: abcdk.pod.Poder._checkPluggedOrMoveABit: instance %s: looping..."  % self );
            time.sleep( 2. ); # wait for charger to charge/activate
            bPlugged = system.isPlugged();
            if( False ):
                rChargeLevel = system.getBatteryLevel();
                if( rChargeLevel > 0.97 ):
                    return True; # when the power is full, and the robot has been forced to go to charge, the charger doesn't want to send current, and we think the robot isn't docked properly...                    
                # patch rotten batteries: sometimes the charger doesn't charge the battery enough
                if( bPlugged ):
                    rChargingCurrent = self.mem.getData( "Device/SubDeviceList/Battery/Current/Sensor/Value" );
                    if( rChargeLevel < 0.8 and rChargingCurrent < 0.07 ):
                        self._saveToCsv( 'charger battery error, charging current is just: %s' % rChargingCurrent );
                        bPlugged = False; # the charging is not good enough: the charger is in "just maintain the power instead of real one"
                
            if( bPlugged ):
                if( bWasNotCharging ):
                    if( self.bVerbose ):
                        speech.sayAndLight(translate.chooseFromDict({'en':"OK!", 'fr':"OK!"}))
                return True;
            self._saveToCsv('bad_contact', 'info');
            if( not bWasNotCharging ):
                if( self.bVerbose ):
                    speech.sayAndLight(translate.chooseFromDict( {'en':"Bad contact.", 'fr':"Il y a un mauvais contact."}) );

            bWasNotCharging = True;

            # check if lying on the ground
            rAngleY = self.mem.getData( "Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value" );
            if( abs( rAngleY ) > 0.75 ):
                # lying on the ground ( ~ 0.0 is vertical (sitting on the pod is around -0.365)
                # restart !!!
                print( "INF: abcdk.pod.checkPluggedOrMoveABit: seems to be lying on the ground (rAngleY: %f)" % rAngleY );
                self._saveToCsv( 'seems to be lying on the ground!' );
                break;

            # move a bit
            if( nCpt != 0 and (nCpt%(nMaxRetry/4) == 0) and bHasRightToStand ):
                self._standFromPod();
                self.motionProxy.moveTo( -0.16, 0., 0. );
            else:
                self._spreadYourLegs();                
            self.sitOnPod();

            if self.bMustStop:
                break;

            nCpt += 1;
        # while - end
        print( "INF: abcdk.pod.checkPluggedOrMoveABit: returning False" );
        return False;
    # _checkPluggedOrMoveABit - end


    def _getSitOnPodMovement( self ):
        # Choregraphe bezier export in Python.
        names = list()
        times = list()
        keys = list()

        rChairBackOrientationOffset = 0.1;

        names.append("HeadPitch")
        times.append([ 1.40000, 1.92000, 2.60000])
        keys.append([ [ 0.23926, [ 3, -0.46667, 0.00000], [ 3, 0.17333, 0.00000]], [ 0.36826, [ 3, -0.17333, 0.00000], [ 3, 0.22667, 0.00000]], [ 0.19017, [ 3, -0.22667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("HeadYaw")
        times.append([ 1.40000, 2.60000])
        keys.append([ [ -0.00311, [ 3, -0.46667, 0.00000], [ 3, 0.40000, 0.00000]], [ 0.00763, [ 3, -0.40000, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LAnklePitch")
        times.append([ 1.40000, 1.92000, 2.60000])
        keys.append([ [ -0.16265, [ 3, -0.46667, 0.00000], [ 3, 0.17333, 0.00000]], [ -0.11868, [ 3, -0.17333, -0.04321], [ 3, 0.22667, 0.05650]], [ 0.13648, [ 3, -0.22667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LAnkleRoll")
        times.append([ 1.40000, 2.60000])
        keys.append([ [ 0.02305, [ 3, -0.46667, 0.00000], [ 3, 0.40000, 0.00000]], [ -0.01223, [ 3, -0.40000, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LElbowRoll")
        times.append([ 1.40000, 1.92000, 2.60000])
        keys.append([ [ -1.25017, [ 3, -0.46667, 0.00000], [ 3, 0.17333, 0.00000]], [ -1.39277, [ 3, -0.17333, 0.00000], [ 3, 0.22667, 0.00000]], [ -1.03387, [ 3, -0.22667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LElbowYaw")
        times.append([ 1.40000, 2.60000])
        keys.append([ [ -1.23798, [ 3, -0.46667, 0.00000], [ 3, 0.40000, 0.00000]], [ -2.03566, [ 3, -0.40000, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LHand")
        times.append([ 1.40000, 2.60000])
        keys.append([ [ 0.00540, [ 3, -0.46667, 0.00000], [ 3, 0.40000, 0.00000]], [ 0.00540, [ 3, -0.40000, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LHipPitch")
        times.append([ 1.40000, 2.60000])
        keys.append([ [ -1.00166, [ 3, -0.46667, 0.00000], [ 3, 0.40000, 0.00000]], [ -0.95717 + rChairBackOrientationOffset, [ 3, -0.40000, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LHipRoll")
        times.append([ 1.40000, 2.60000])
        keys.append([ [ -0.08433, [ 3, -0.46667, 0.00000], [ 3, 0.40000, 0.00000]], [ -0.00303, [ 3, -0.40000, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LHipYawPitch")
        times.append([ 1.40000, 1.92000, 2.60000])
        keys.append([ [ -0.23773, [ 3, -0.46667, 0.00000], [ 3, 0.17333, 0.00000]], [ -0.27227, [ 3, -0.17333, 0.00000], [ 3, 0.22667, 0.00000]], [ 0.02765, [ 3, -0.22667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LKneePitch")
        times.append([ 1.40000, 2.60000])
        keys.append([ [ 1.00780, [ 3, -0.46667, 0.00000], [ 3, 0.40000, 0.00000]], [ 1.27011, [ 3, -0.40000, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LShoulderPitch")
        times.append([ 1.40000, 2.60000])
        keys.append([ [ 1.30386, [ 3, -0.46667, 0.00000], [ 3, 0.40000, 0.00000]], [ 1.60299, [ 3, -0.40000, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LShoulderRoll")
        times.append([ 1.40000, 2.60000])
        keys.append([ [ 0.11347, [ 3, -0.46667, 0.00000], [ 3, 0.40000, 0.00000]], [ 0.30369, [ 3, -0.40000, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LWristYaw")
        times.append([ 1.40000, 2.60000])
        keys.append([ [ 0.11347, [ 3, -0.46667, 0.00000], [ 3, 0.40000, 0.00000]], [ 0.42948, [ 3, -0.40000, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RAnklePitch")
        times.append([ 1.40000, 1.92000, 2.60000])
        keys.append([ [ -0.15796, [ 3, -0.46667, 0.00000], [ 3, 0.17333, 0.00000]], [ -0.11868, [ 3, -0.17333, -0.03928], [ 3, 0.22667, 0.05136]], [ 0.19793, [ 3, -0.22667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RAnkleRoll")
        times.append([ 1.40000, 2.60000])
        keys.append([ [ -0.02297, [ 3, -0.46667, 0.00000], [ 3, 0.40000, 0.00000]], [ 0.04913, [ 3, -0.40000, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RElbowRoll")
        times.append([ 1.40000, 1.92000, 2.60000])
        keys.append([ [ 1.25025, [ 3, -0.46667, 0.00000], [ 3, 0.17333, 0.00000]], [ 1.53065, [ 3, -0.17333, 0.00000], [ 3, 0.22667, 0.00000]], [ 1.12140, [ 3, -0.22667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RElbowYaw")
        times.append([ 1.40000, 2.60000])
        keys.append([ [ 1.23636, [ 3, -0.46667, 0.00000], [ 3, 0.40000, 0.00000]], [ 1.88218, [ 3, -0.40000, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RHand")
        times.append([ 1.40000, 2.60000])
        keys.append([ [ 0.00545, [ 3, -0.46667, 0.00000], [ 3, 0.40000, 0.00000]], [ 0.00545, [ 3, -0.40000, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RHipPitch")
        times.append([ 1.40000, 2.60000])
        keys.append([ [ -1.00174, [ 3, -0.46667, 0.00000], [ 3, 0.40000, 0.00000]], [ -0.96493 + rChairBackOrientationOffset, [ 3, -0.40000, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RHipRoll")
        times.append([ 1.40000, 2.60000])
        keys.append([ [ 0.08595, [ 3, -0.46667, 0.00000], [ 3, 0.40000, 0.00000]], [ -0.00149, [ 3, -0.40000, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RHipYawPitch")
        times.append([ 1.40000, 1.92000, 2.60000])
        keys.append([ [ -0.23773, [ 3, -0.46667, 0.00000], [ 3, 0.17333, 0.00000]], [ -0.27227, [ 3, -0.17333, 0.00000], [ 3, 0.22667, 0.00000]], [ 0.02765, [ 3, -0.22667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RKneePitch")
        times.append([ 1.40000, 2.60000])
        keys.append([ [ 1.00481, [ 3, -0.46667, 0.00000], [ 3, 0.40000, 0.00000]], [ 1.23951, [ 3, -0.40000, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RShoulderPitch")
        times.append([ 1.40000, 2.60000])
        keys.append([ [ 1.29781, [ 3, -0.46667, 0.00000], [ 3, 0.40000, 0.00000]], [ 1.68898, [ 3, -0.40000, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RShoulderRoll")
        times.append([ 1.40000, 2.60000])
        keys.append([ [ -0.11663, [ 3, -0.46667, 0.00000], [ 3, 0.40000, 0.00000]], [ -0.40042, [ 3, -0.40000, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RWristYaw")
        times.append([ 1.40000, 2.60000])
        keys.append([ [ 0.08279, [ 3, -0.46667, 0.00000], [ 3, 0.40000, 0.00000]], [ -0.00004, [ 3, -0.40000, 0.00000], [ 3, 0.00000, 0.00000]]])

        return (names, times, keys);
    # _getSitOnPodMovement - end

    def sitOnPod(self):
        motion = naoqitools.myGetProxy("ALMotion")
        motiontools.setFallManagerState(False)
        motion.setStiffnesses( "Body", 1. );

        names, times, keys = self._getSitOnPodMovement();
        motion.angleInterpolationBezier(names, times, keys);

        motion.rest()
        #motiontools.setFallManagerState(True) # 13-10-29 Alma: commenting this: seems silly and bugging !
        
    def _getSpreadYourLegsMovement( self ):
        # Choregraphe bezier export in Python.
        names = list()
        times = list()
        keys = list()
        
        names.append("LAnklePitch")
        times.append([1])
        keys.append([[0.331302, [3, -0.333333, 0], [3, 0, 0]]])

        names.append("LAnkleRoll")
        times.append([1])
        keys.append([[0.0291879, [3, -0.333333, 0], [3, 0, 0]]])

        names.append("LHipPitch")
        times.append([1])
        keys.append([[-0.914222, [3, -0.333333, 0], [3, 0, 0]]])

        names.append("LHipRoll")
        times.append([1])
        keys.append([[0.142704, [3, -0.333333, 0], [3, 0, 0]]])

        names.append("LHipYawPitch")
        times.append([1])
        keys.append([[-0.673384, [3, -0.333333, 0], [3, 0, 0]]])

        names.append("LKneePitch")
        times.append([1])
        keys.append([[1.13052, [3, -0.333333, 0], [3, 0, 0]]])

        names.append("RAnklePitch")
        times.append([1])
        keys.append([[0.345192, [3, -0.333333, 0], [3, 0, 0]]])

        names.append("RAnkleRoll")
        times.append([1])
        keys.append([[-0.00609398, [3, -0.333333, 0], [3, 0, 0]]])

        names.append("RHipPitch")
        times.append([1])
        keys.append([[-0.897432, [3, -0.333333, 0], [3, 0, 0]]])

        names.append("RHipRoll")
        times.append([1])
        keys.append([[-0.15029, [3, -0.333333, 0], [3, 0, 0]]])

        names.append("RHipYawPitch")
        times.append([1])
        keys.append([[-0.673384, [3, -0.333333, 0], [3, 0, 0]]])

        names.append("RKneePitch")
        times.append([1])
        keys.append([[1.0493, [3, -0.333333, 0], [3, 0, 0]]])    

        return (names, times, keys);
    # _getSpreadYourLegsMovement - end        
        
    def _spreadYourLegs(self):
        motion = naoqitools.myGetProxy("ALMotion")
        motiontools.setFallManagerState(False)
        motion.setStiffnesses( "Body", 1. );

        names, times, keys = self._getSpreadYourLegsMovement();
        motion.angleInterpolationBezier(names, times, keys);
        
        motion.rest();
    # _spreadYourLegs - end

    def standFromPod(self):
        # TODO: Armoring if necessary
        return self._standFromPod();
    # standFromPod - end

    def _standFromPod(self):
        if( not self.isSitting() ):
            print( "WRN:abcdk.pod._standFromPod: not sitting, so not standing !!!" );
            return False;
        motiontools.setFallManagerState( False );
        motion = naoqitools.myGetProxy("ALMotion");
        motion.setStiffnesses( "Body", 1. );
        #motion.stiffnessInterpolation("Body", stiffness, 0.1);

        names = list()
        times = list()
        keys = list();
        
        rTime0 = 0.52;
        rTime1 = 1.12;
        rTime2 = 1.8;
        rTime3 = 2.6;
        
        rHipPitchAdd = 0;
        rShoulderPitchAdd = 0;
        
        #~ rHipPitchAdd = 0.3;
        rShoulderPitchAdd = -0.8; # for carton pod
        #~ rTime1 += 0.2
        #~ rTime2 += 1.
        #~ rTime3 += 3.
        
        names.append("HeadPitch")
        times.append([ rTime0, rTime1,rTime2, rTime3])
        keys.append([ [ -0.02094, [ 3, -0.17333, 0.00000], [ 3, 0.20000, 0.00000]], [ 0.41713, [ 3, -0.20000, 0.00000], [ 3, 0.22667, 0.00000]], [ 0.23926, [ 3, -0.22667, 0.08903], [ 3, 0.26667, -0.10474]], [ -0.16418, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("HeadYaw")
        times.append([rTime2, rTime3])
        keys.append([ [ -0.00311, [ 3, -0.60000, 0.00000], [ 3, 0.26667, 0.00000]], [ -0.00311, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LAnklePitch")
        times.append([ rTime0, rTime1,rTime2, rTime3])
        keys.append([ [ 0.58818, [ 3, -0.17333, 0.00000], [ 3, 0.20000, 0.00000]], [ -0.17977, [ 3, -0.20000, 0.00000], [ 3, 0.22667, 0.00000]], [ -0.16265, [ 3, -0.22667, -0.01712], [ 3, 0.26667, 0.02014]], [ 0.08586, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LAnkleRoll")
        times.append([ rTime1,rTime2, rTime3])
        keys.append([ [ -0.11170, [ 3, -0.37333, 0.00000], [ 3, 0.22667, 0.00000]], [ 0.02305, [ 3, -0.22667, 0.00000], [ 3, 0.26667, 0.00000]], [ -0.13035, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LElbowRoll")
        times.append([ rTime0, rTime1,rTime2, rTime3])
        keys.append([ [ -1.20079, [ 3, -0.17333, 0.00000], [ 3, 0.20000, 0.00000]], [ -1.54462, [ 3, -0.20000, 0.00000], [ 3, 0.22667, 0.00000]], [ -1.25017, [ 3, -0.22667, -0.17384], [ 3, 0.26667, 0.20452]], [ -0.40954, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LElbowYaw")
        times.append([ rTime1,rTime2, rTime3])
        keys.append([ [ -1.74358, [ 3, -0.37333, 0.00000], [ 3, 0.22667, 0.00000]], [ -1.23798, [ 3, -0.22667, -0.04564], [ 3, 0.26667, 0.05369]], [ -1.18429, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LHand")
        times.append([rTime2, rTime3])
        keys.append([ [ 0.00540, [ 3, -0.60000, 0.00000], [ 3, 0.26667, 0.00000]], [ 0.00540, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LHipPitch")
        times.append([ rTime1,rTime2, rTime3])
        keys.append([ [ -1.77325+rHipPitchAdd, [ 3, -0.37333, 0.00000], [ 3, 0.22667, 0.00000]], [ -1.00166+rHipPitchAdd, [ 3, -0.22667, -0.29226], [ 3, 0.26667, 0.34384]], [ 0.13503, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LHipRoll")
        times.append([rTime2, rTime3])
        keys.append([ [ -0.08433, [ 3, -0.60000, 0.00000], [ 3, 0.26667, 0.00000]], [ 0.10129, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LHipYawPitch")
        times.append([ rTime1,rTime2, rTime3])
        keys.append([ [ -0.26180, [ 3, -0.37333, 0.00000], [ 3, 0.22667, 0.00000]], [ -0.23773, [ 3, -0.22667, -0.01473], [ 3, 0.26667, 0.01733]], [ -0.16563, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LKneePitch")
        times.append([ rTime0, rTime1,rTime2, rTime3])
        keys.append([ [ 0.84648, [ 3, -0.17333, 0.00000], [ 3, 0.20000, 0.00000]], [ 1.42244, [ 3, -0.20000, 0.00000], [ 3, 0.22667, 0.00000]], [ 1.00780, [ 3, -0.22667, 0.23195], [ 3, 0.26667, -0.27289]], [ -0.09208, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LShoulderPitch")
        times.append([ rTime1,rTime2, rTime3])
        keys.append([ [ 2.02807+rShoulderPitchAdd, [ 3, -0.37333, 0.00000], [ 3, 0.22667, 0.00000]], [ 1.30386, [ 3, -0.22667, 0.00000], [ 3, 0.26667, 0.00000]], [ 1.48027, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LShoulderRoll")
        times.append([ rTime1,rTime2, rTime3])
        keys.append([ [ 0.49044, [ 3, -0.37333, 0.00000], [ 3, 0.22667, 0.00000]], [ 0.11347, [ 3, -0.22667, 0.00000], [ 3, 0.26667, 0.00000]], [ 0.12114, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("LWristYaw")
        times.append([rTime2, rTime3])
        keys.append([ [ 0.11347, [ 3, -0.60000, 0.00000], [ 3, 0.26667, 0.00000]], [ 0.12421, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RAnklePitch")
        times.append([ rTime0, rTime1,rTime2, rTime3])
        keys.append([ [ 0.58818, [ 3, -0.17333, 0.00000], [ 3, 0.20000, 0.00000]], [ -0.17977, [ 3, -0.20000, 0.00000], [ 3, 0.22667, 0.00000]], [ -0.15796, [ 3, -0.22667, -0.02181], [ 3, 0.26667, 0.02566]], [ 0.09668, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RAnkleRoll")
        times.append([ rTime1,rTime2, rTime3])
        keys.append([ [ 0.11170, [ 3, -0.37333, 0.00000], [ 3, 0.22667, 0.00000]], [ -0.02297, [ 3, -0.22667, 0.00000], [ 3, 0.26667, 0.00000]], [ 0.12890, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RElbowRoll")
        times.append([ rTime0, rTime1,rTime2, rTime3])
        keys.append([ [ 1.29678, [ 3, -0.17333, 0.00000], [ 3, 0.20000, 0.00000]], [ 1.54462, [ 3, -0.20000, 0.00000], [ 3, 0.22667, 0.00000]], [ 1.25025, [ 3, -0.22667, 0.17336], [ 3, 0.26667, -0.20395]], [ 0.41269, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RElbowYaw")
        times.append([ rTime1,rTime2, rTime3])
        keys.append([ [ 1.74358, [ 3, -0.37333, 0.00000], [ 3, 0.22667, 0.00000]], [ 1.23636, [ 3, -0.22667, 0.03651], [ 3, 0.26667, -0.04295]], [ 1.19341, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RHand")
        times.append([rTime2, rTime3])
        keys.append([ [ 0.00545, [ 3, -0.60000, 0.00000], [ 3, 0.26667, 0.00000]], [ 0.00545, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RHipPitch")
        times.append([ rTime1,rTime2, rTime3])
        keys.append([ [ -1.77325+rHipPitchAdd, [ 3, -0.37333, 0.00000], [ 3, 0.22667, 0.00000]], [ -1.00174+rHipPitchAdd, [ 3, -0.22667, -0.29178], [ 3, 0.26667, 0.34327]], [ 0.13188, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RHipRoll")
        times.append([rTime2, rTime3])
        keys.append([ [ 0.08595, [ 3, -0.60000, 0.00000], [ 3, 0.26667, 0.00000]], [ -0.10274, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RHipYawPitch")
        times.append([ rTime1,rTime2, rTime3])
        keys.append([ [ -0.26180, [ 3, -0.37333, 0.00000], [ 3, 0.22667, 0.00000]], [ -0.23773, [ 3, -0.22667, -0.01473], [ 3, 0.26667, 0.01733]], [ -0.16563, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RKneePitch")
        times.append([ rTime0, rTime1,rTime2, rTime3])
        keys.append([ [ 0.84648, [ 3, -0.17333, 0.00000], [ 3, 0.20000, 0.00000]], [ 1.42244, [ 3, -0.20000, 0.00000], [ 3, 0.22667, 0.00000]], [ 1.00481, [ 3, -0.22667, 0.23100], [ 3, 0.26667, -0.27177]], [ -0.08586, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RShoulderPitch")
        times.append([ rTime1,rTime2, rTime3])
        keys.append([ [ 2.02807+rShoulderPitchAdd, [ 3, -0.37333, 0.00000], [ 3, 0.22667, 0.00000]], [ 1.29781, [ 3, -0.22667, 0.00000], [ 3, 0.26667, 0.00000]], [ 1.48342, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RShoulderRoll")
        times.append([ rTime1,rTime2, rTime3])
        keys.append([ [ -0.49044, [ 3, -0.37333, 0.00000], [ 3, 0.22667, 0.00000]], [ -0.11663, [ 3, -0.22667, 0.00000], [ 3, 0.26667, 0.00000]], [ -0.11816, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        names.append("RWristYaw")
        times.append([rTime2, rTime3])
        keys.append([ [ 0.08279, [ 3, -0.60000, 0.00000], [ 3, 0.26667, 0.00000]], [ 0.05518, [ 3, -0.26667, 0.00000], [ 3, 0.00000, 0.00000]]])

        #~ for nNumJoint in range( len(times)):
            #~ for nNumKey in range(len(times[nNumJoint])):
                #~ times[nNumJoint][nNumKey] *= 0.8;
                
        motion.angleInterpolationBezier(names, times, keys);
        print("Relevage ok")
        time.sleep( 0.5 );
        motiontools.setFallManagerState(True)
        return True

    def _safeArmsSit(self):
        # Choregraphe bezier export in Python.
        names = list()
        times = list()
        keys = list()

        names.append("LElbowRoll")
        times.append([1])
        keys.append([[-0.0551819, [3, -0.333333, 0], [3, 0, 0]]])

        names.append("LElbowYaw")
        times.append([1])
        keys.append([[-1.5141, [3, -0.333333, 0], [3, 0, 0]]])

        names.append("LHand")
        times.append([1])
        keys.append([[0.4204, [3, -0.333333, 0], [3, 0, 0]]])

        names.append("LShoulderPitch")
        times.append([1])
        keys.append([[2.0678, [3, -0.333333, 0], [3, 0, 0]]])

        names.append("LShoulderRoll")
        times.append([1])
        keys.append([[0.401426, [3, -0.333333, 0], [3, 0, 0]]])

        names.append("LWristYaw")
        times.append([1])
        keys.append([[-1.55398, [3, -0.333333, 0], [3, 0, 0]]])

        names.append("RElbowRoll")
        times.append([1])
        keys.append([[0.0614019, [3, -0.333333, 0], [3, 0, 0]]])

        names.append("RElbowYaw")
        times.append([1])
        keys.append([[1.51708, [3, -0.333333, 0], [3, 0, 0]]])

        names.append("RHand")
        times.append([1])
        keys.append([[0.4216, [3, -0.333333, 0], [3, 0, 0]]])

        names.append("RShoulderPitch")
        times.append([1])
        keys.append([[2.04486, [3, -0.333333, 0], [3, 0, 0]]])

        names.append("RShoulderRoll")
        times.append([1])
        keys.append([[-0.506145, [3, -0.333333, 0], [3, 0, 0]]])

        names.append("RWristYaw")
        times.append([1])
        keys.append([[1.56617, [3, -0.333333, 0], [3, 0, 0]]])

        # end safeArmsSit
        motion = naoqitools.myGetProxy("ALMotion")
        motion.wakeUp()
        motion.angleInterpolationBezier(names, times, keys);
        return True

    def _moveTango(self):
        # Choregraphe bezier export in Python.
        motion = naoqitools.myGetProxy("ALMotion")
        motion.wakeUp()
        names = list()
        times = list()
        keys = list()

        names.append("LElbowRoll")
        times.append([0.6, 1])
        keys.append([[-1.49101, [3, -0.2, 0], [3, 0.133333, 0]], [-1.52169, [3, -0.133333, 0], [3, 0, 0]]])

        names.append("LElbowYaw")
        times.append([0.6, 1])
        keys.append([[-0.403483, [3, -0.2, 0], [3, 0.133333, 0]], [-0.408086, [3, -0.133333, 0], [3, 0, 0]]])

        names.append("LHand")
        times.append([0.6, 1])
        keys.append([[0.42, [3, -0.2, 0], [3, 0.133333, 0]], [0.4208, [3, -0.133333, 0], [3, 0, 0]]])

        names.append("LShoulderPitch")
        times.append([0.6, 1])
        keys.append([[0.493905, [3, -0.2, 0], [3, 0.133333, 0]], [1.04, [3, -0.133333, 0], [3, 0, 0]]]) # 13-10-31 Alma: was 0.44175 => 1.04: trying to reduce wobbling by nearing COM

        names.append("LShoulderRoll")
        times.append([0.6, 1])
        keys.append([[-0.159578, [3, -0.2, 0], [3, 0.133333, 0]], [-0.193327, [3, -0.133333, 0], [3, 0, 0]]])

        names.append("LWristYaw")
        times.append([0.6, 1])
        keys.append([[-0.971065, [3, -0.2, 0], [3, 0.133333, 0]], [-0.980268, [3, -0.133333, 0], [3, 0, 0]]])

        names.append("RElbowRoll")
        times.append([0.6, 1])
        keys.append([[0.365133, [3, -0.2, 0], [3, 0.133333, 0]], [1.49723, [3, -0.133333, 0], [3, 0, 0]]])

        names.append("RElbowYaw")
        times.append([0.6, 1])
        keys.append([[0.0735901, [3, -0.2, 0], [3, 0.133333, 0]], [-0.556884, [3, -0.133333, 0], [3, 0, 0]]])

        names.append("RHand")
        times.append([0.6, 1])
        keys.append([[0.9816, [3, -0.2, 0], [3, 0.133333, 0]], [0.984, [3, -0.133333, 0], [3, 0, 0]]])

        names.append("RShoulderPitch")
        times.append([0.6, 1])
        keys.append([[1.67517, [3, -0.2, 0], [3, 0.133333, 0]], [2.04486, [3, -0.133333, 0], [3, 0, 0]]])

        names.append("RShoulderRoll")
        times.append([0.6, 1])
        keys.append([[-0.656595, [3, -0.2, 0], [3, 0.133333, 0]], [-0.0107799, [3, -0.133333, 0], [3, 0, 0]]])

        names.append("RWristYaw")
        times.append([0.6, 1])
        keys.append([[1.77633, [3, -0.2, 0], [3, 0.133333, 0]], [1.78247, [3, -0.133333, 0], [3, 0, 0]]])

        motion.angleInterpolationBezier(names, times, keys);
        print("Tango ok")
    #end _moveTango
    
    def _moveArmsThink(self):
        """
        set the arm in a rear spaces to prevent shooting armrests (while near approach walking)
        """
        names = ["LElbowRoll", "LElbowYaw", "LHand", "LShoulderPitch", "LShoulderRoll", "LWristYaw", "RElbowRoll", "RElbowYaw", "RHand", "RShoulderPitch", "RShoulderRoll", "RWristYaw" ];
        values = [-0.783832, 0.24233, 0.476, 2.01257, 0.05825, -0.374338, 0.575292, -0.289968, 0.6316, 2.02185, 0.0950661, 1.15046];
        motion = naoqitools.myGetProxy( "ALMotion" )
        motion.post.angleInterpolation( names, values, 1., True );
    # _moveArmsThink - end

    def _randomFunSentence(self):
        import random
        sentences = {'fr':"Tiens je vais en profiter pour faire caca.. vous pouvez tourner la tête ?/Aie, j'ai pris du courant/Valentin viens me cirer mes chaussures pendant que je suis assis/D'où je suis je vois sous les jupes, image sauvée en 09 point jpeg.",
                     'en':"How to poo at work."}
        if random.random() > 0.7:
            if( self.bVerbose ):
                speech.sayAndLight(translate.chooseFromDictRandom(sentences))
# class Poder - end

# example of a fake motionProxy / usefull for testing on desktop.. should be integrated in naoqitools when no remote detected..
# import flexmock
# fakeProxy = flexmock.flexmock(operational=True, name = 'ALMotion', getPosition=lambda: None, moveTo=lambda: None, stopMove=lambda: True)

def offlinePodDraw(path=None, bFindBluePod = False ):
    """ function used for generating a video of 3D positioning.
    path = image to process path

    for each image in path, process the image to detect the pod, create an
    image with 3D orrientation and others information like distance
    """
    import os
    for filename in os.listdir(path):
        if not('jpg' in filename):
            continue
        colouredImg = cv2.imread(os.path.join(path, filename))
        try:
            pickleFileName = os.path.splitext(filename)[0]
            pickleFileName += '.pickle'
            #print("PICKLE file to look for %s" % pickleFileName)
            realObjectPts, kResolution, camPos6D, torsoPose6D = serialization_tools.loadObjectFromFile(os.path.join(path, pickleFileName))
        except IOError:
            #print("no pickle file %s for image file  %s" % (str(pickleFileName), str(filename)))
            continue
        #print("FILE FOUNLD")
        cameraImage = cv2.cvtColor(colouredImg, cv2.COLOR_BGR2GRAY)
        ledPts, thresholdImg, rectangle = infraLedDetector(cameraImage, bFindBluePod=bFindBluePod)
        #rectangle = PodLocator.bestRectangle(PodLocator.pointMatch6PointsRectangular(ledPts))
        if rectangle == None:
            continue

        pnpOpencv = imagePnp.getPnP(rectangle, realObjectPts, nResolution=kResolution)
        if pnpOpencv != None:
            i = 0
            for (x, y) in rectangle:
                cv2.circle(cameraImage, (int(x), int(y)), i+2, (0, 200, 80), 2)
                i += 2

            height, width = cameraImage.shape
            colouredImg3D = np.zeros((width,height, 3), np.uint8)
            axis = np.float32([[-1,-1,0], [-1,1,0], [1,1,0], [1,-1,0], [-1,-1,-3],[-1,1,-3],[1,1,-3],[1,-1,-3] ])/100
            imgPts, jac = cv2.projectPoints(axis, pnpOpencv.opencvPnpR, pnpOpencv.opencvPnpT, camera.camera.aCameraMatrix[kResolution], camera.camera.distorsionCoef)
            distance3D = numeric.dist3D(np.zeros(6), pnpOpencv.opencvPnpT)
            debugImg = imagePnp.draw3D(colouredImg, imgPts, pnpOpencv.projectedImPts, imgPts, distance=distance3D)
            pnpFileName = os.path.splitext(filename)[0] + '3d_pnp.png'
            cv2.imwrite(os.path.join(path, pnpFileName), debugImg)
            print("processing image %s .. done" % filename)
            #print(pnpOpencv.projectedImPts.shape)

        #cv2.imwrite(os.path.join(path, circleFileName), cameraImage)



def offlinePodDetect(filename, pathOutPut, bFindBluePod = False ):
    """
    Return None if no rectangle found or a pnpOpencv (TODO: document me!)
    """
    bDebugShow = False
    colouredImg = cv2.imread(filename)
    if( colouredImg == None ):
        print("ERR: offlinePodDetect: file '%s' not found!" % filename );
        return None;
    kResolution = 3
    podLocator0 = PodLocator(bDebug=True, resolution=kResolution)
    if( not bFindBluePod or 0 ):
        cameraImage = cv2.cvtColor(colouredImg, cv2.COLOR_BGR2GRAY)
    else:
        cameraImage, cameraImage_color = prepareImageForBluePodDetection( colouredImg );
        if bDebugShow:
            cv2.imshow('before', colouredImg)
        #cv2.resizeWindow('before', 240, 240)
            cv2.imshow('afterPreprocess', cameraImage)
    strFilenamePrepared = os.path.join(pathOutPut, filetools.getFilenameFromTime() + '_prepared.jpg')
    strFilenameRaw = os.path.join(pathOutPut, filetools.getFilenameFromTime() + '_raw.jpg')
    cv2.imwrite( strFilenamePrepared , cameraImage_color );
    cv2.imwrite( strFilenameRaw , colouredImg );

    #print( "max: %s" % str(np.max( cameraImage ) ));
    ledPts, thresholdImg, rectangle = infraLedDetector( cameraImage, bFindBluePod = bFindBluePod);  # we use old point detector..
    cv2.imwrite(os.path.join(pathOutPut, os.path.basename(filename).replace('.jpg', '_threshold.jpg')), thresholdImg)
    #rectangle = PodLocator.bestRectangle(PodLocator.pointMatch6PointsRectangular(ledPts))
    if rectangle == None:
        strFname = os.path.join(pathOutPut, 'NOT_FOUND' +  os.path.basename(filename ))
        #rint("INF: no rectangle found saving image to %s, number of ledptrs are %s" % (strFname, ledPts))
        #hmport IPython
        #Python.embed()
        cv2.imwrite(strFname, colouredImg)
        #cv2.imshow('No rectangle', colouredImg)
        #cv2.imshow('No rectangle - trhsehold', thresholdImg)
        #cv2.waitKey()

        return None


    pnpOpencv = imagePnp.getPnP(rectangle, podLocator0.realObjectPts, nResolution=kResolution)
    bDrawDetected = True
    if bDrawDetected:
        if pnpOpencv != None:
            i = 0
            for (x, y) in rectangle:
                cv2.circle(cameraImage, (int(x), int(y)), i+2, (0, 200, 80), 2)
                i += 2

            height, width = cameraImage.shape
            colouredImg3D = np.zeros((width,height, 3), np.uint8)
            axis = np.float32([[-1,-1,0], [-1,1,0], [1,1,0], [1,-1,0], [-1,-1,-3],[-1,1,-3],[1,1,-3],[1,-1,-3] ])/100

            imgPts, jac = cv2.projectPoints(axis, pnpOpencv.opencvPnpR, pnpOpencv.opencvPnpT, camera.camera.aCameraMatrix[kResolution], camera.camera.distorsionCoef)
            i = 0
            for pt in pnpOpencv.projectedImPts:
                (x, y) = pt[0]
                cv2.circle(colouredImg, (int(x), int(y)), i+2, (0, 200, 80), 2)
                i += 2


            distance3D = numeric.dist3D(np.zeros(6), pnpOpencv.opencvPnpT)
            debugImg = imagePnp.draw3D(colouredImg, None, pnpOpencv.projectedImPts, imgPts, distance=distance3D)
            pnpFileName = os.path.splitext(os.path.basename(filename)) #[0] + '3d_pnp.png'
            cv2.imwrite(os.path.join(pathOutPut, os.path.basename(filename)), debugImg)
            print("processing image %s .. done" % filename)
            #print(pnpOpencv.projectedImPts.shape)

        if pnpOpencv == None:
            i = 0
            for (x, y) in rectangle:
                cv2.circle(colouredImg, (int(x), int(y)), i+2, (0, 200, 80), 2)
                i += 2
            cv2.imwrite(os.path.join(pathOutPut, os.path.basename(filename)), colouredImg)

        circleFileName = os.path.splitext(os.path.basename(filename))[0] + 'circle.jpg'
        cv2.imwrite(os.path.join(pathOutPut, circleFileName), cameraImage)





    return pnpOpencv

def offlinePodDrawBis(path=None, pathOutPut='/tmp/out/'):
    """ function used for generating a video of 3D positioning based on image only
    path = image to process path
    """
    import os
    for filename in os.listdir(path):
        if ('jpg' in filename):
            pnpOpencv = offlinePodDetect(filename, pathOutPut=pathOutPut)


def testOneImageFromDisk(aListFile, strPathOutput='/tmp/', bFindBluePod=True): # TODO : compatibility linux/windows on /tmp
    #strPath = "C:\\nao_debug_poder\\";
    ##~ listFile.append( "2014_01_22-18h19m51s819318ms_gain_100.jpg" );
    ##~ listFile.append( "2014_01_22-18h19m39s804078ms_gain_128.jpg" );
    ##~ listFile.append( "2014_01_22-18h19m55s952752ms_gain_164.jpg" );
    ##~ listFile.append( "2014_01_22-18h28m57s339375ms.jpg" );
    #alistFile.append( "2014_01_23-11h14m05s403684ms_2m90.jpg" );

    listRet = [];
    nFound = 0
    nNotFound = 0
    for filename in aListFile:
        print( "testing: %s" % filename );
        ret = offlinePodDetect( filename, strPathOutput, bFindBluePod=bFindBluePod );
        print("END testing")
        listRet.append( ret );
    for ret in listRet:
        if( ret != None ):
            nFound +=1
            print( "found: %s" % str( ret ) );
        else:
            print( "NOT FOUND!!!" );
            nNotFound +=1
    return (nFound, nNotFound)
    
def analyseCsv( strFilename ):
    """
    Analyse the debug csv log and output some stats
    """
    data = filetools.loadCsv( strFilename );
    #~ print( data );
    nbrSuccess = 0;
    nbrStopped = 0;
    nbrFail = 0;
    bInGoto = False;
    bWaitNextToConfirm = False;
    bChargingStarted = False;
    nCurrentDay = -1;
    strCurrentKeyDay = "";
    aDictStatPerDay = {}; # for each record: nbr success, min goto, max goto, sum goto, nbr stopped, nbr fail
    nIdxDay = 0;    
    
    #~ 2014_08_29-10h05m05s,goAndSit,finished *** END
#~ 2014_08_29-10h05m05s,charging,start
#~ 2014_08_29-10h09m23s,charging,stop
#~ 2014_08_29-10h09m25s,standFromPod,start
#~ 2014_08_29-10h09m36s,standFromPod,stop
#~ 2014_08_29-10h09m36s,stop has been called... *** END (soon),

    for record in data:
        #~ print( "record: %s" % record );
        strTime = record[0];
        if( len(strTime) == 0 or ord(strTime[0]) == 0 ):
            continue; # the line is rotten
        strCategory = record[1];
        strMsg = record[2];
        #~ print( "strTime: '%s'" % strTime  );
        timeRecord = datetime.datetime.strptime(strTime, "%Y_%m_%d-%Hh%Mm%Ss");        
        nDay = timeRecord.day;
        nMonth = timeRecord.month;
        if( bWaitNextToConfirm ):
            #~ print( "attente de confirmation record: %s" % record );
            rTimeSec = (timeRecord-timeStartCharge).total_seconds();
            if( strCategory == "charging" and strMsg == "start" ):
                print( "start truc");
                nbrSuccess += 1;
                bWaitNextToConfirm = False;
                bChargingStarted = True;
                aDictStatPerDay[strCurrentKeyDay][0] += 1;
                if( aDictStatPerDay[strCurrentKeyDay][1] > rTimeSec ):
                    aDictStatPerDay[strCurrentKeyDay][1] = rTimeSec;
                if( aDictStatPerDay[strCurrentKeyDay][2] < rTimeSec ):
                    aDictStatPerDay[strCurrentKeyDay][2] = rTimeSec;
                aDictStatPerDay[strCurrentKeyDay][3] += rTimeSec
            elif( "stop has been called..." in strCategory ):
                print( "stopped ?: %s: '%s' '%s' after %ss" % (strTime, strCategory, strMsg, rTimeSec) );
                if( rTimeSec < 500 ):
                    # stop
                    aDictStatPerDay[strCurrentKeyDay][4] += 1;
                    nbrStopped += 1;                    
                else:
                    # fail
                    aDictStatPerDay[strCurrentKeyDay][5] += 1;
                    nbrFail += 1;                    
                bWaitNextToConfirm = False;
            else:
                print( "unhandled: %s: '%s' '%s'" % (strTime, strCategory, strMsg) );
        elif( ("stop has been called..." in strCategory) and bInGoto ):
            if( bChargingStarted ):
                # in that case, the power stop giving power, or we force a stop charge, so it's ok.
                print( "%s: charger error?" % strTime);
            else:
                #~ print( strTime )
                rTimeSec = (timeRecord-timeStartCharge).total_seconds();            
                print( "stopped before finished? (while in goto): %s: '%s' '%s' after %ss" % (strTime, strCategory, strMsg, rTimeSec) );
                if( rTimeSec < 300 ):
                    # stop
                    aDictStatPerDay[strCurrentKeyDay][4] += 1;
                    nbrStopped += 1;                    
                else:
                    # fail
                    aDictStatPerDay[strCurrentKeyDay][5] += 1;
                    nbrFail += 1;                    
                bInGoto = False;
        
        if( strMsg == "starting *** BEGIN" ):
            bChargingStarted = False;
            #~ print( "starting at %s" % strTime );
            if( bWaitNextToConfirm or bInGoto ):
                #print( "restarting but previous is unfinished! (bWaitNextToConfirm:%s): %s: '%s' '%s'" % (bWaitNextToConfirm,strTime, strCategory, strMsg) );
                aDictStatPerDay[strCurrentKeyDay][4] += 1;
                nbrStopped += 1;                    
            if( nDay != nCurrentDay ):
                nIdxDay += 1;
                nCurrentDay = nDay;
                strCurrentKeyDay = "%04d_%02d_%02d" % (nIdxDay,nMonth, nCurrentDay);
                aDictStatPerDay[strCurrentKeyDay] = [0,1000,0,0,0,0];
            bInGoto = True;
            timeStartCharge = timeRecord;
        elif( strMsg == "finished *** END" ):
            if( not bInGoto ):
                print( "WRN: wasn't in charge ! at time: %s" % strTime );
                bWaitNextToConfirm = False;
            else:
                bWaitNextToConfirm = True;
            bInGoto = False;
    print( "aDictStatPerDay: %s" % aDictStatPerDay );
    print( "Day per day:" );
    print( "-"*50 );
    print( "index and date of day --- min/avg/max time docking in sec" );
    for nDay, stats in sorted(aDictStatPerDay.iteritems()):
        nbr, rMin, rMax, rSum, nStop, nFail = stats;
        if( nbr > 0 ):
            print( "day %s: %3d success, %5.2fs/%5.2fs/%5.2fs  stop: %d, fail: %d" % (nDay, nbr, rMin, rSum/nbr, rMax,nStop, nFail) );
    print( "-"*50 );
    print( "" );
    print( "Total:" );
    print( "nbrSuccess: %s" % nbrSuccess );
    print( "nbrStopped: %s" % nbrStopped );
    print( "nbrFail: %s" % nbrFail );
        
# analyseCsv - end
            
            


def autotest():
    #strPathTest = "C:\\work\\Dev\\git\\appu_data\\images_to_analyse\\"; # sorry laurent :)
    #strPathTestOut = "c:\\tempo\\";
    #detectBluePodRoughly_test(strPathTest, strPathTestOut);

#    _testMaskTrueIfOneInKernelIsTrue()
    strPath = "../../../appu_data/images_to_analyse/blue_pod/in_situ/pod/"
    #strPath = "../../../appu_data/images_to_analyse/blue_pod/pod_high/with_pod/"
    strPath = "../../../appu_data/images_to_analyse/blue_pod/pod_low_new_version/without_pod/" #
    #strPath = "../../../appu_data/images_to_analyse/blue_pod/toBeDetected" # 29 vs 1
    #strPath = "../../../appu_data/images_to_analyse/blue_pod/pod_low_new_version/with_pod/" # 130 - 4  *good
    #strPath = "../../../appu_data/images_to_analyse/blue_pod/pod_high/no_pod/" # aprem (0,221)
    #strPath = "/tmp/notfound"
    #strPath = "../../../appu_data/images_to_analyse/blue_pod/not_found" # 17 vs 1   Weep.. on augmente le nombre d'image
    #strPath = "/home/lgeorge/tmpTest/with_pod/"

    #strPath = "../../../appu_data/images_to_analyse/blue_pod/pod_low_new_version/with_pod/" # 113 - 21  *good
    #strPath = "../../../appu_data/images_to_analyse/blue_pod/pod_high/no_pod/" # aprem (0,221)
    #strPath = "/tmp/notfound"
    #strPath = "../../../appu_data/images_to_analyse/blue_pod/not_found" # 17 vs 1   Weep.. on augmente le nombre d'image
    #strPath = "/tmp/toTest/"
    aListFile = [os.path.join(strPath, filename) for filename in os.listdir(strPath) if filename.endswith('.jpg')]
#    aListFile = aListFile[0:10]
    print(testOneImageFromDisk(aListFile, bFindBluePod=True))

# autotest - end


def main():
    #res = cv2.solvePnP(realObjectPts, imgPts, cameraMatrix, distorsionCoef) # itterative..

    #offlinePodDrawBis('/home/lgeorge/projects/media/podImages')
    #import config
    #config.bInChoregraphe = False
    #p = Poder(numTrialId = 1)
    #p.saveToCsv('session id : %s' % str(p.numTrialId), 'start')
    #p.goAndSit()
    #p.saveToCsv('session id :%s' % str(p.numTrialId), 'stop')
    #~ print("*" * 20)
    #~ #offlinePodDetect('/home/lgeorge/image_nouveau_pod.jpg', '/tmp/')
    path = '/home/lgeorge/nao9/'
    for file in os.listdir(path):
        try:
            offlinePodDetect(os.path.join(path, file), '/tmp/')
        except:
            print("error")
    print("*" * 20)


if __name__=="__main__":
    analyseCsv( "c:\\all_detailed.csv" );
    #autotest();

#~ img = np.array([
                            #~ [(1,2,3), (4,5,6),(255,0,0)],
                            #~ [(128,128,128), (128,128,255),(255,64,64)],
                            #~ [(1,2,3), (4,5,6),(255,0,0)],
                            #~ [(200,50,78), (4,5,6),(255,0,0)],
                    #~ ]);

#~ print( np.mean( img, axis = 1 ).mean(axis=0) );
