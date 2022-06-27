# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Vision Recognition surcouche method
# Author A. Mazel
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Vision Recognition surcouche method"

print( "importing abcdk.visionrecognition" );

import cv2

import numpy as np
import os
import time

import naoqitools


def learnFromFile( strPathFilename, bGenerateLowerResolution = False ):
    """
    - strPathFilename: an absolute path filename
    Object filename are described as this template:
    "Bordeau_Chesnel_Rillettes__front.JPG"
    or
    "Madrange_Mousse_de_Canard.JPG"
    """
    #~ print( "DBG: visionrecognition.learnFromFile: strPathFilename: '%s'" % strPathFilename );
    strFilename = os.path.basename( strPathFilename )
    strFilename = os.path.splitext(strFilename)[0];
    
    astrFielded = os.path.abspath( strPathFilename ).split( os.sep );
    #~ print( "astrFielded: %s" % astrFielded );
    if( len( astrFielded ) > 1 ):
        strCategory = astrFielded[-2];
    else:
        strCategory = "";
    
    astrFielded = strFilename.split( "__" );
    strObjectName = astrFielded[0];
    
    strSide = "";
    if( len( astrFielded ) > 1 ):
        strSide = astrFielded[1];
    print( "INF: visionrecognition.learnFromFile: filename: '%s', object name: '%s', side: '%s', category: '%s', learning..." % (strFilename, strObjectName, strSide, strCategory) );
    timeBegin = time.time();
    vr = naoqitools.myGetProxy( "ALVisionRecognition" );
    bIsWholeImage = False;
    aMetadata = ["side:", strSide, "category:", strCategory];
    bForced = True;
    bSuccess = vr.learnFromFile( strPathFilename, strObjectName, aMetadata, bIsWholeImage, bForced );
    if( not bSuccess ):
        print( "WRN: visionrecognition.learnFromFile: the object in '%s' hasn't been learned!" % strNewName );
    
    if( bGenerateLowerResolution ):
        imageBuffer = cv2.imread( strPathFilename );
        for rScale in [0.1, 0.2,0.5]:
            timeBeginSmall = time.time();            
            imageSmall = cv2.resize( imageBuffer, dsize=(0,0), fx=rScale, fy=rScale );
            strNewName = "/tmp/" + strFilename + ("_small%5.2f.jpg" % rScale);
            cv2.imwrite( strNewName, imageSmall );
            aMetadata = ["side:", strSide + ("_small%5.2f.jpg" % rScale), "category:", strCategory];
            bSuccess = vr.learnFromFile( strNewName, strObjectName, aMetadata, bIsWholeImage, bForced );            
            if( not bSuccess ):
                print( "WRN: visionrecognition.learnFromFile: the object in '%s' hasn't been learned!" % strNewName );
            rDuration = time.time() - timeBeginSmall;
            print( "INF: visionrecognition.learnFromFile: filename: '%s', small image (%5.2f) learned in %5.2fs" % (strNewName, rScale, rDuration) );    
    rDuration = time.time() - timeBegin;        
    print( "INF: visionrecognition.learnFromFile: filename: '%s', learned in %5.2fs" % (strFilename, rDuration) );
# learnFromFile - end

#~ learnFromFile( "/home/nao/Food/Bordeau_Chesnel_Rillettes__front.JPG" );

def learnFromFolder( strPath, bGenerateLowerResolution = False ):
    print( "INF: visionrecognition.learnFromFolder: '%s' (bGenerateLowerResolution:%s)" % ( strPath, bGenerateLowerResolution ) );
    timeBegin = time.time();
    for filename in sorted( os.listdir( strPath ) ):
        strFullPath = strPath + os.sep + filename;
        if( os.path.isdir( strFullPath ) ):
            learnFromFolder( strFullPath, bGenerateLowerResolution = bGenerateLowerResolution );
        else:
            learnFromFile( strFullPath, bGenerateLowerResolution = bGenerateLowerResolution );
    rDuration = time.time() - timeBegin;
    print( "INF: visionrecognition.learnFromFolder: learned '%s', in %5.2fs" % (strPath, rDuration) );
# learnFromFolder - end

def loadCurrentBase():
    """
    load the current base so we can start to launch a recognition
    """
    print( "INF: visionrecognition.loadCurrentBase: loading..." );
    timeBegin = time.time();
    height,width = 16,16;
    blank_image = np.zeros((height,width,3), np.uint8)
    strBlanckFilename = "/tmp/blanck.jpg";
    cv2.imwrite( strBlanckFilename, blank_image );
    vr = naoqitools.myGetProxy( "ALVisionRecognition" );    
    dummy = vr.detectFromFile( strBlanckFilename );
    rDuration = time.time() - timeBegin;
    print( "INF: visionrecognition.loadCurrentBase: loaded  in %5.2fs" % (rDuration) );
# loadCurrentBase - end

if( __name__ == "__main__" ):
    learnFromFolder( "C:/work/Dev/git/appu_data/objects_database" );