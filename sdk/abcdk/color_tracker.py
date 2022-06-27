# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# slam
# @author The usage team - Living Labs
# Aldebaran Robotics (c) 2016 All Rights Reserved - This file is confidential.
###########################################################

from naoqi import ALProxy
from naoqi import qi

import cv2
import numpy as np
import time
import sys
import platform

def nothing(x):
    pass

class EnableTracking:
    """
    Enum
    """

    OBJECT_NOT_TRACKED = 0
    OBJECT_TRACKED     = 1


class ColorDetector:
    """
    Color detector class
    """

    def __init__(self,robotIp="127.0.0.1",display=False):
        """
        Constructor
        """

        self.I_LOW_H                    = 81
        self.I_HIGH_H                   = 120
        self.I_LOW_S                    = 146
        self.I_HIGH_S                   = 215
        self.I_LOW_V                    = 142
        self.I_HIGH_V                   = 235
        self.NB_TRACKED_OBJECTS = 1
        self.ENABLE_TRACKING    = EnableTracking.OBJECT_NOT_TRACKED
        self.ENABLE_DISPLAY = display

        self.strId = "blobTracker_" + str(time.time())

        self.capture              = None
        self.originalFrame        = None
        self.imageHSV             = None
        self.imageThresholded = None
        self.trackingImage    = None
        self.kernel               = None
        self.contours             = None

        self.video = ALProxy("ALVideoDevice",robotIp,9559)
        status = self.video.subscribeCamera(self.strId,1,2,13,30)
        if status == "":
            raise Exception("subscribtion to camera failed")
        else:
            self.strId = status
        nUsedResolution = self.video.getResolution( self.strId );
        self.nSizeX, self.nSizeY = self.video.resolutionToSizes( nUsedResolution );

        self.contoursPoly     = list()
        self.targetZone           = list()
        self.centers              = list()


    def computeTracking(self, iLowH, iHighH, iLowS, iHighS, iLowV, iHighV, nbTrackedObjects, enableTracking):
        """
        Loop launch, takes the HSV parameters, and returns the frame to be displayed
        """

        self.I_LOW_H                = iLowH
        self.I_HIGH_H                   = iHighH
        self.I_LOW_S                    = iLowS
        self.I_HIGH_S                   = iHighS
        self.I_LOW_V                    = iLowV
        self.I_HIGH_V                   = iHighV
        self.NB_TRACKED_OBJECTS = nbTrackedObjects
        self.ENABLE_TRACKING    = enableTracking

        #Get image remote for debug purpose
        #Swithc to local for increased perf
        resultCamera = self.video.getImageRemote(self.strId)[6]

        if resultCamera is None:
            raise Exception("Cannot read a frame from the video feed")
        else:
          image = resultCamera;
          tmp = np.fromstring(image, dtype=np.uint8)
          imagenp = np.reshape(tmp, ( self.nSizeY, self.nSizeX,3))
          self.originalFrame = imagenp

        self.trackingImage    = self.originalFrame

        self.imageHSV         = cv2.cvtColor(self.originalFrame, cv2.COLOR_BGR2HSV)
        self.imageThresholded = cv2.inRange(self.imageHSV, np.array([self.I_LOW_H, self.I_LOW_S, self.I_LOW_V],np.uint8), np.array([self.I_HIGH_H, self.I_HIGH_S, self.I_HIGH_V],np.uint8))

        self.kernel           = np.ones((5,5),np.uint8)

        # Morphological opening (remove small objects from the foreground)
        self.imageThresholded = cv2.erode(self.imageThresholded, self.kernel, iterations = 1)
        self.imageThresholded = cv2.dilate(self.imageThresholded, self.kernel, iterations = 1)

        # Morphological closing (fill small holes in the foreground)
        self.imageThresholded = cv2.dilate(self.imageThresholded, self.kernel, iterations = 1)
        self.imageThresholded = cv2.erode(self.imageThresholded, self.kernel, iterations = 1)

        if self.ENABLE_TRACKING:
            self.imageThresholded = cv2.dilate(self.imageThresholded, self.kernel, iterations = 1)
            
            if platform.system() == "Windows":
                _, self.contours, _ = cv2.findContours(self.imageThresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            else:
                self.contours, _    = cv2.findContours(self.imageThresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            del self.contoursPoly[:]
            del self.targetZone[:]
            del self.centers[:]

            for element in self.contours:
                approximationPoly = cv2.approxPolyDP(element, 3,True)

                self.contoursPoly.append(approximationPoly)
                self.targetZone.append(cv2.boundingRect(approximationPoly))


            if len(self.contours) is not 0:
                self.defineTargets()
                self.defineCenters()

                if self.ENABLE_DISPLAY:
                    for i in range(len(self.targetZone)):
                        cv2.rectangle(self.trackingImage, (self.targetZone[i][0], self.targetZone[i][1]), (self.targetZone[i][0] + self.targetZone[i][2], self.targetZone[i][1] + self.targetZone[i][3]), (0, 0, 255), 3)
                        cv2.circle(self.trackingImage, self.centers[i], 1, (0, 255, 0), 7, 24)
                        cv2.putText(self.trackingImage, "X : " + str(self.centers[i][0]) + "; Y : " + str(self.centers[i][1]), self.centers[i], cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0))
                        print(str(i) + " : " + str(self.centers[i][0]) + " ; " + str(self.centers[i][1]))

                    return self.trackingImage
                else:
                    return self.centers

            else:
                if self.ENABLE_DISPLAY:
                    return self.originalFrame

                else:
                    return list()

        else:
            return self.imageThresholded


    def defineTargets(self):
        """
        Used to sort the different targets
        """

        self.targetZone =  sorted(self.targetZone, key= lambda x: x[2]*x[3], reverse = True)

        if len(self.targetZone) > self.NB_TRACKED_OBJECTS:
            del self.targetZone[self.NB_TRACKED_OBJECTS:]


    def defineCenters(self):
        """
        Used to specify the centers of the targets
        """

        for element in self.targetZone:
            self.centers.append((element[0] + element[2]/2, element[1] + element[3]/2))


def main():
    # create trackbars for color change
    I_LOW_H                    = 92
    I_HIGH_H                   = 111
    I_LOW_S                    = 164
    I_HIGH_S                   = 233
    I_LOW_V                    = 180
    I_HIGH_V                   = 255
    NB_TRACKED_OBJECTS         = 1
    ENABLE_TRACKING            = EnableTracking.OBJECT_NOT_TRACKED
    ENABLE_DISPLAY             = True

    if len(sys.argv) >= 2:
        colorDetector = ColorDetector(robotIp=sys.argv[1], display=ENABLE_DISPLAY)

    else:
        colorDetector = ColorDetector(display=ENABLE_DISPLAY)

    cv2.namedWindow('Trackbar', cv2.WINDOW_NORMAL)
    cv2.createTrackbar('LowH', 'Trackbar', I_LOW_H, 179, lambda x:x)
    cv2.createTrackbar('HighH', 'Trackbar', I_HIGH_H, 179, lambda x:x)

    cv2.createTrackbar('LowS', 'Trackbar', I_LOW_S, 255, lambda x:x)
    cv2.createTrackbar('HighS', 'Trackbar', I_HIGH_S, 255, lambda x:x)

    cv2.createTrackbar('LowV', 'Trackbar', I_LOW_V, 255, lambda x:x)
    cv2.createTrackbar('HighV', 'Trackbar', I_HIGH_V, 255, lambda x:x)

    cv2.createTrackbar('nb tracked objects', 'Trackbar', NB_TRACKED_OBJECTS, 100, lambda x:x)
    cv2.createTrackbar('tracking OFF 0 / ON 1', 'Trackbar', ENABLE_TRACKING, 1, lambda x:x)

    try:
        while True:
            I_LOW_H                    = cv2.getTrackbarPos('LowH','Trackbar')
            I_HIGH_H                   = cv2.getTrackbarPos('HighH','Trackbar')
            I_LOW_S                    = cv2.getTrackbarPos('LowS','Trackbar')
            I_HIGH_S                   = cv2.getTrackbarPos('HighS','Trackbar')
            I_LOW_V                    = cv2.getTrackbarPos('LowV','Trackbar')
            I_HIGH_V                   = cv2.getTrackbarPos('HighV','Trackbar')
            NB_TRACKED_OBJECTS = cv2.getTrackbarPos('nb tracked objects', 'Trackbar')
            ENABLE_TRACKING    = cv2.getTrackbarPos('tracking OFF 0 / ON 1', 'Trackbar')

            if ENABLE_DISPLAY:
                cv2.imshow('image', colorDetector.computeTracking(I_LOW_H, I_HIGH_H, I_LOW_S, I_HIGH_S, I_LOW_V, I_HIGH_V, NB_TRACKED_OBJECTS, ENABLE_TRACKING))

            else:
                print "centers : " + str(colorDetector.computeTracking(I_LOW_H, I_HIGH_H, I_LOW_S, I_HIGH_S, I_LOW_V, I_HIGH_V, NB_TRACKED_OBJECTS, ENABLE_TRACKING))

            cv2.waitKey(1)

    except KeyboardInterrupt:
        pass

    cv2.destroyAllWindows()
    print "End tracking"



if __name__ == "__main__":
    main()
