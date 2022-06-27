# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# analyse and store images "autonomously"
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################


"""Tools to display image on tablet, picoproj..."""


print( "importing abcdk.vision_extraction" )

import cv2
import numpy as np
import os
import time

import camera
import filetools


def mse(imageA, imageB):
        # the 'Mean Squared Error' between the two images is the
        # sum of the squared difference between the two images;
        # NOTE: the two images must have the same dimension
        
        # astype("float"): 0.28s in HD astype("int"): 0.15s astype("int16"): 0.11s (on raspberry3)
        # on jetsonTX2 VGA RGB python3: int8: , 0.007, int16: 0.009, int: 0.024, float:  0.024
        err = np.sum( ((imageA.astype("int16") - imageB.astype("int16")) ** 2) )                                                                                   
        
        err /= float(imageA.shape[0] * imageA.shape[1])

        # return the MSE, the lower the error, the more "similar"
        # the two images are
        return abs(err)

class VisionExtractor(object):
    """
    A simple object to start/stop a camera connection and analyse image
    """
    def __init__(self, nImageResolution=2, aCameras=[0,1], nColorSpace=13, nFps=30, strImagesPath='/tmp/', strExtension='jpg', nImageCompression=10):
        self.nImageResolution = nImageResolution # 0..4..7 (best is 4) # even if 4 is noisy it worth the case compared to 3.
        self.aCameras = aCameras  # list of cameras to use (0: top, 1: bottom)
        self.nColorSpace = nColorSpace # 0: luma, 11: RGB, 13: kBGRColorSpace
        self.nFps = nFps
        self.strImagesPath = strImagesPath
        self.bMustStop = False;
        self.bDisableImWrite = False
        self.strExtension = strExtension.lower()
        self.nImageCompression = nImageCompression

    def stop(self):
        if( not self.bMustStop ):
            self.bMustStop = True
            print( "INF: abcdk.vision_extraction.VisionExtractor: stopping..." )
            print("List of subscribed camera %s" % camera.camera.dictOpenedSubscriber)
            time.sleep(0.5) # we wait for current image to be processed
            for nCamera in self.aCameras:
                camera.camera.getImageCV2_unsubscribeCamera(nImageResolution=self.nImageResolution, nCamera=nCamera, colorSpace=self.nColorSpace)  # unsubscribe

    def start(self, bDebug=True):
        """
        save a bunch of image using a timestamp
        """
        print( "INF: abcdk.vision_extraction.VisionExtractor: started..." )
        print("INF: Using Local Image %s" % camera.camera.bUseLocalProxy)
        self.bMustStop = False
        self.nImageSaved = 0
        
        try:
            os.makedirs(self.strImagesPath)
        except: pass # already exists

        aImLast = [None,None]
        for nCamera in self.aCameras:
            aImLast[nCamera] = camera.camera.getImageCV2(nImageResolution=self.nImageResolution, nCamera=nCamera, colorSpace=self.nColorSpace, fps=self.nFps, bNoUnsubscribe=True, bVerbose=False)

        rStartTime = time.time()
        while not(self.bMustStop):
            for nCamera in self.aCameras:
                rStartTime_getImage = time.time()
                im = camera.camera.getImageCV2(nImageResolution=self.nImageResolution, nCamera=nCamera, colorSpace=self.nColorSpace, fps=self.nFps, bNoUnsubscribe=True, bVerbose=False)
                if im == None:
                    print( "WRN: VisionExtractor: image is None..." )
                    time.sleep(1.)
                    continue
                rDuration_getImage = time.time() - rStartTime_getImage
                    
                rDiff = mse(aImLast[nCamera], im)
                
                print( "DBG: diff between image: rDiff: %s, process time: %5.3fs" % (rDiff,(time.time() - rStartTime_getImage)) )
                    
                aImLast[nCamera] = im

                bMustSave = rDiff>100 # 90 but when noisy => declenche plus souvent
                    
                if bMustSave:
                    strMyClientNameKey = camera.camera.getClientNameFromProperties( nImageResolution = self.nImageResolution, nCamera = nCamera, colorSpace = self.nColorSpace);
                    #timestamp = camera.camera.getLastImageTimeStamp(strMyClientNameKey)
                    timestamp = time.time() # else it's always 1970...
                    rStartTime_timestampManagement = time.time()
                    strFileOut = self.strImagesPath + str(nCamera) + "_" + filetools.getFilenameFromTime(timestamp=timestamp) + "__" + str(int(rDiff)) + "." + self.strExtension
                    rDuration_timestampManagement = time.time() - rStartTime_timestampManagement
                    rStartTime_imwrite = time.time()
                    if "jpg" in self.strExtension:
                        bRet = cv2.imwrite( strFileOut, im, [cv2.IMWRITE_JPEG_QUALITY, self.nImageCompression] );
                    else:
                        bRet = cv2.imwrite( strFileOut, im );
                    if not bRet:
                        print( "WRN: can't write on disk to '%s'" % strFileOut )
                        os.unlink( strFileOut ) # erase empty file if it exists
                    rDuration_imwrite = time.time() - rStartTime_imwrite
                    rFullDuration = time.time() - rStartTime_getImage
                    if rFullDuration > 0.2:
                        print("WARNING: SLOW (full is %s): Saving image took %ssec, getImageCv2 took %s sec, timestamp management took %s" % (rFullDuration, rDuration_imwrite, rDuration_getImage, rDuration_timestampManagement))

            self.rElapsedTime = time.time() - rStartTime

            self.nImageSaved += 1
            time.sleep( 0.005 ) # leave a bit of cpu to system
        return(self.rElapsedTime, self.nImageSaved, self.nImageSaved/self.rElapsedTime)
   # with black and white ( 2 cameras, 10seconds, in /tmp/, using   self.videoMaker.nImageCompression = 60) : (9.730589866638184, 285, 29.28907742552554)
   # with color ( 2 cameras, 10seconds, in /tmp/, using  self.videoMaker.nImageCompression=60) :  (9.742464065551758, 130, 13.343646856206037)  (9.690371036529541, 152, 15.685673894942674)


# End - VisionExtractor
