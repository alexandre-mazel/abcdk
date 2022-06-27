# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Object Recognition CNN
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################


"""Object Recognition based on CNN in the Cloud"""
print( "importing abcdk.object_recognition_cnn" );

import copy
import math
import numpy

# some constants

kQQVGA = 0;
kQVGA = 1;
kVGA = 2;
k4VGA = 3; # work only on a NAO V4

kGrey = 0;
kYUV422 = 9;
kBGR = 13;

kTopCamera = 0;
kBottomCamera = 1;
kSelectCamera = 18;


openSocket = None
def recognizeFromImage( cvImage ):
    """
    return results from cloud
    """
    import socket_send
    import socket_receive
    
    global openSocket
    if openSocket == None:
        openSocket = socket_send.SocketSender()
        openSocket.connect("10.0.161.80")
    ret = openSocket.sendData( cvImage,  socket_receive.kTypeImageCv2, socket_receive.kActionObjectRecognitionCnn, bWaitResult = True, bVerbose = True )
    #ret = s.recv(1024)
    #openSocket.disconnect()
    return ret
# recognizeFromImage - end


def recognizeFromCamera( strNaoIp = "localhost", bVerbose = True ):
    """
    Recognize image from camera
    """
    nWantedResolution = kVGA;

    nColorSpace = kBGR;
    nColorSpace = kYUV422;
    #~ nColorSpace = kGrey;

    nWantedResolution = kVGA; # kVGA to record nice databse, but for the moment kQVGA is enough!
    nCameraToUse = kTopCamera;
    #~ nCameraToUse = kBottomCamera;

    try:
        import cv # using willowgarage official opencv 2.1 version # http://opencv.willowgarage.com/documentation/python/ (windows: install full openpackage cv, then copy C:\opencv\build\python\2.6 to sites-package)
    except:
        print( "WRN: nao_camera_viewer: NO OpenCV library ???" );
    try:    
        import cv2 # using opencv 2.4.5 # http://opencv.org # on windows: copy cv2.pyd from ...\opencv\build\python\2.7 to c:\python27\
        import cv2.cv as cv # backward compatible
    except:
        print( "WRN: nao_camera_viewer: NO OpenCV2 library ???" );
        
    try:
        import numpy
    except:
        print( "WRN: nao_camera_viewer: NO numpy found, you won't have yuv => bgr conversion!" );

    import os
    import sys
    import time
    import naoqi

    def convertYUV_ToBGR_cv2( image, nSizeX, nSizeY ):
        """
        yuv cv1 => bgr cv2/numpy
        """
        #~ timeBegin = time.time();
        numpyBuf = (numpy.reshape(numpy.frombuffer(image, dtype='%iuint8' % 1), ( nSizeX, nSizeY, 2)))
        rgb = cv2.cvtColor(numpyBuf, cv2.COLOR_YUV2BGR_YUYV); # COLOR_YUV2RGB_Y422 # cv2.COLOR_YUV2RGB_YUYV
        #~ rDuration = time.time() - timeBegin;
        #~ print( "rDuration: %s" % rDuration ); # ~1ms per conversion!
        return rgb;
    # convertYUV_ToBGR_cv2 - end

    avd = naoqi.ALProxy( "ALVideoDevice",  strNaoIp, 9559 );
    mem = naoqi.ALProxy( "ALMemory",  strNaoIp, 9559 );

    strMyClientName = "object_recognition_cnn"
    nFps = 5
    try: avd.unsubscribe( strMyClientName )
    except: pass
    try: avd.unsubscribeAllInstances( strMyClientName )
    except: pass    
    
    strMyClientName = avd.subscribe( strMyClientName, nWantedResolution, nColorSpace, nFps );
    if( strMyClientName == "" ):
        print( "ERR: subscribe error" )
        return False
    nUsedResolution = avd.getGVMResolution( strMyClientName );

    print( "INF: Camera subscribing: after" );

    nSizeX, nSizeY = avd.resolutionToSizes( nUsedResolution );
    print( "GVM has Image properties: %dx%d" % (nSizeX,nSizeY) );
    nNbrColorPlanes = 3;
    if( nColorSpace == kGrey ):
        nNbrColorPlanes = 1;
    bufferImage = cv.CreateImage( (nSizeX, nSizeY), cv.IPL_DEPTH_8U, nNbrColorPlanes );
    avd.setParam( kSelectCamera, nCameraToUse ); # change camera

    nCptFrame = 0
    prevImg = numpy.zeros( (640,480), numpy.int16)
    timeBegin = time.time()
    while( 1 ):
        timeBeginLocal = time.time()
        dataImage = avd.getImageRemote( strMyClientName );
        print( "DBG: getimage: %5.2fs" % (time.time() - timeBeginLocal) )
        if( dataImage == None ):
            print( "ERR: dataImage is none!" );
        else:
            nSizeX = dataImage[0];
            nSizeY = dataImage[1];
            rTimeStamp = dataImage[4] + dataImage[5]/(1000000.);
            #~ print( "Image get: %dx%d" % (nSizeX,nSizeY) );
            #~ print( "Image prop: layer: %d, format: %d" % (dataImage[2],dataImage[3]) );
            image = dataImage[6];
            #~ print( "first char: '%s','%s','%s'" % ( image[0+960],image[1],image[2] )  );
            #~ print( "first char orded: %s,%s,%s" % ( ord( image[0] ), ord( image[1] ), ord( image[2] )  ) );
            # bufferImage.data = image;
            
            if( nColorSpace != kYUV422 ):
                # converted locally in NAO's  head
                cv.SetData( bufferImage, image );
            else:
                rgb = convertYUV_ToBGR_cv2( image, nSizeX, nSizeY );
                #cv.SetData( bufferImage, rgb );
                bufferImage = rgb
                
            # compage image with previous one
            bufferImageB,gDummy,rDummy = cv2.split(bufferImage) # should be in grey, but faster in B
            diff = prevImg - bufferImageB  # elementwise for scipy arrays
            rMeanDiff = numpy.mean(abs(diff))
            print( "rMeanDiff: %s" % rMeanDiff )
            if( rMeanDiff > 10 ):
                # image is different enough
                prevImg = bufferImageB.astype(numpy.int16) # for diff, we'll need int16 array (should be optimised ?)
                
                print( "DBG: analyse image: before" )
                timeBeginLocal = time.time()
                ret = recognizeFromImage( bufferImage )
                print( "DBG: analyse image: %5.2fs" % (time.time() - timeBeginLocal) )
                
                if bVerbose: print( "DBG: analyse image: returned: %s" % str(ret) )
                
                timeBeginLocal = time.time()
                mem.raiseMicroEvent( "ObjectRecoCNN", ret )
                print( "DBG: raise event: %5.2fs" % (time.time() - timeBeginLocal) )
            
            nCptFrame += 1
            if( nCptFrame == 10 ):
                rDuration = time.time() - timeBegin;
                rLastComputedFps = 10/rDuration;
                print( "fps: %f" % (rLastComputedFps) );
                nCptFrame = 0;
                timeBegin = time.time();
    # while - end

    print("Unsubscribing..." );
    avd.unsubscribe( strMyClientName );    
# recognizeFromCamera - end



if( __name__ == "__main__" ):
    #recognizeFromCamera( "10.0.204.63" )
    recognizeFromCamera( "localhost" )
