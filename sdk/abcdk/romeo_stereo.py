# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Actors
# @author The usage team - Living Labs
# Aldebaran Robotics (c) 2016 All Rights Reserved - This file is confidential.
###########################################################


# some constants

kQQVGA = 0;
kQVGA = 1;
kVGA = 2;
k4VGA = 3; # work only on a NAO V4
kGrey = 0;
kYUV422 = 9;
kRGB = 11;
kBGR = 13;
kFlipH = 7;
kFlipV = 8;
kSelectCamera = 18;

# Configuration
strNaoIp = "10.0.161.8"

nWantedResolution = kVGA;
bStereoMode = False;
bStereoMode = True; # else it's top/bottom

nColorSpace = kYUV422;

import cv2
import cv2.cv as cv
import numpy
import time

def convertYUV_ToBGR_cv2( image, nSizeX, nSizeY ):
    """
    using the cv2 convert method
    """
    #~ timeBegin = time.time();
    numpyBuf = (numpy.reshape(numpy.frombuffer(image, dtype='%iuint8' % 1), ( nSizeX, nSizeY, 2)))
    rgb = cv2.cvtColor(numpyBuf, cv2.COLOR_YUV2BGR_YUYV); # COLOR_YUV2RGB_Y422 # cv2.COLOR_YUV2RGB_YUYV
    imageRgb = rgb.tostring();
    #~ rDuration = time.time() - timeBegin;
    #~ print( "rDuration: %s" % rDuration ); # ~1ms per conversion!
    return imageRgb;
# convertYUV_ToBGR_cv2 - end

import naoqi
from naoqi import ALBroker
from naoqi import ALModule
from naoqi import ALProxy




# # variable
# nFps = 30;

# kQQVGA = 0;
# kQVGA = 1;
# kVGA = 2;
# k4VGA = 3; # work only on a NAO V4
# kBGR = 13;
# kYUV422 = 9;
# kGrey = 0;
# nWantedResolution = kVGA
# nColorSpace = kYUV422;

# kSelectCamera = 18;
# kTopCamera = 0;
# kBottomCamera = 1;
# nCameraToUse = kTopCamera;

# strDebugWindowName1 = "Video Monitor"; # "DebugWindow"; # set to false to have no debug windows
# cv.NamedWindow( strDebugWindowName1, cv.CV_WINDOW_AUTOSIZE);
# cv.MoveWindow( strDebugWindowName1, 0, -1 );
# strDebugWindowName2 = "Video Monitor Right (or Bottom)"; # "DebugWindow"; # set to false to have no debug windows
# cv.NamedWindow( strDebugWindowName2, cv.CV_WINDOW_AUTOSIZE);

# # time.sleep(5)


# avd = ALProxy( "ALVideoDevice",  strNaoIp, 9559 );
# strMyClientName = "nao_camera_viewer";

# print( "INF: Camera subscribing: before..." );
# strMyClientName = avd.subscribeCameras( strMyClientName, [0,1], [nWantedResolution,nWantedResolution], [nColorSpace,nColorSpace], nFps );
# nUsedResolution, nDumb = avd.getResolutions( strMyClientName );
# print( "INF: Camera subscribing: after..." );

# nSizeX, nSizeY = avd.resolutionToSizes( nUsedResolution );
# print( "GVM has Image properties: %dx%d" % (nSizeX,nSizeY) );

# nNbrColorPlanes = 3;


# bufferImageToDraw1 = cv.CreateImage( (nSizeX, nSizeY), cv.IPL_DEPTH_8U, nNbrColorPlanes );
# bufferImageToDraw2 = cv.CreateImage( (nSizeX, nSizeY), cv.IPL_DEPTH_8U, nNbrColorPlanes );

strDebugWindowName = "Video Monitor"; # "DebugWindow"; # set to false to have no debug windows
cv.NamedWindow( strDebugWindowName, cv.CV_WINDOW_AUTOSIZE);
strDebugWindowName2 = "Video Monitor Right (or Bottom)"; # "DebugWindow"; # set to false to have no debug windows
cv.NamedWindow( strDebugWindowName2, cv.CV_WINDOW_AUTOSIZE);

avd = ALProxy( "ALVideoDevice",  strNaoIp, 9559 );
strMyClientName = "nao_camera_viewer";
nFps = 30;
print( "INF: Camera subscribing: before..." );
strMyClientName = avd.subscribeCameras( strMyClientName, [0,1], [nWantedResolution,nWantedResolution], [nColorSpace,nColorSpace], nFps );
nUsedResolution, nDumb = avd.getResolutions( strMyClientName );
print( "INF: Camera subscribing: after" );

nSizeX, nSizeY = avd.resolutionToSizes( nUsedResolution );
nNbrColorPlanes = 3;
bufferImageToDraw  = cv.CreateImage( (nSizeX, nSizeY), cv.IPL_DEPTH_8U, nNbrColorPlanes );
bufferImageToDraw2 = cv.CreateImage( (nSizeX, nSizeY), cv.IPL_DEPTH_8U, nNbrColorPlanes );

bKeyPressed = False;

while(not bKeyPressed):

	# dataImage = avd.getImagesRemote( strMyClientName );
	# # print len(dataImage)
	# if dataImage:
	# 	nSizeX1 = dataImage[0][0];
	# 	nSizeY1 = dataImage[0][1];

	# 	if( dataImage[0] != 0 ):
	# 		image1 = dataImage[0][6];
	# 	else:
	# 		image1 = None;

	# 	if( dataImage[1] != 0 ):
	# 		image2 = dataImage[1][6];
	# 	else:
	# 		print( "ERR: multistream: second image is empty... (dataImage[1]: %s)" % str(dataImage[1]) );                        
	# 		image2 = None;

	# 	if( image1 != None ):
	# 		rgb1 = convertYUV_ToBGR_cv2( image1, nSizeX1, nSizeY1 );
	# 		cv.SetData( bufferImageToDraw1, rgb1 );
	# 	if( image2 != None ):
	# 		rgb2 = convertYUV_ToBGR_cv2( image2, nSizeX1, nSizeY1 );
	# 		cv.SetData( bufferImageToDraw2, rgb2 );

	# 	cv.ShowImage( strDebugWindowName1, bufferImageToDraw1 );
	# 	cv.ShowImage( strDebugWindowName2, bufferImageToDraw2 );
    dataImage = avd.getImagesRemote( strMyClientName );
        #~ print( "getImagesRemote: apres" );
    if( dataImage == None ):
        print( "ERR: dataImage is none!" );
    else:
        #~ print("image len: %d" % len(dataImage) );                
        nSizeX = dataImage[0][0]; # read only properties of image 1
        nSizeY = dataImage[0][1];

        if( dataImage[0] != 0 ):
            image1 = dataImage[0][6];
        else:
            image1 = None;
        if( dataImage[1] != 0 ):
            image2 = dataImage[1][6];
        else:
            print( "ERR: multistream: second image is empty... (dataImage[1]: %s)" % str(dataImage[1]) );                        
            image2 = None;
        if( image1 == None or image2 == None ):
            print( "ERR: multistream: one or more image is None, im1: %s, im2: %s" % (image1, image2) )
        if( image1 != None ):
            rgb1 = convertYUV_ToBGR_cv2( image1, nSizeX, nSizeY );
            cv.SetData( bufferImageToDraw, rgb1 );
        if( image2 != None ):
            rgb2 = convertYUV_ToBGR_cv2( image2, nSizeX, nSizeY );
            cv.SetData( bufferImageToDraw, rgb2 );

        cv.ShowImage( strDebugWindowName, bufferImageToDraw );
        cv.ShowImage( strDebugWindowName2, bufferImageToDraw2 );    
	
    nKey =  cv.WaitKey(1) & 0xFF;

avd.unsubscribe( strMyClientName );