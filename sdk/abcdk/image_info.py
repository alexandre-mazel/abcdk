# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Image tools and structures
# @author The usage team - Living Labs
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Camera tools: some constants useful to use camera modules, a camera object to help handling camera..."""

print( "importing abcdk.camera" );

class ImageInfo:
    """
    Some extra information about an image taken from the camera (position in the world, ...)
    """
    
    def __init__( self ):
        self.reset();    
        
    def reset( self ):
        self.nTimeStamp = 0;
        self.cameraPosInNaoSpace = [];
        self.cameraPosInWorldSpace = [];
        self.cameraPosInFrameTorso = [];
        self.nCameraName = "";
        self.nResolution= -1;
        
    def __str__( self ):
        strOut = "";
        strOut += "nTimeStamp: %d\n" % self.nTimeStamp;
        strOut += "cameraPosInNaoSpace: %s\n" % self.cameraPosInNaoSpace;
        strOut += "cameraPosInWorldSpace: %s\n" % self.cameraPosInWorldSpace;
        strOut += "cameraPosFrameTorso: %s\n" % self.cameraPosInFrameTorso;
        strOut += "nCameraName: %s\n" % self.nCameraName;
        strOut += "nResolution: %s\n" % self.nResolution;
        return strOut;

    
# class ImageInfo
