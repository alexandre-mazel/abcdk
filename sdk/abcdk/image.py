# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Image tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Image tools"
print( "importing abcdk.image" );

try:
    import Image
    import ImageDraw
except:
    print( "WRN: abcdk.image: NO PIL library ???" );

import os
import struct
import sys

import arraytools
import color
import filetools
# import naoqitools # done later on the fly
import numeric
import pathtools
import stringtools

import camera
import time
import cv2
import math
import numpy as np



try:
    import cv # using willowgarage official opencv 2.1 version # http://opencv.willowgarage.com/documentation/python/ (windows: install full openpackage cv, then copy C:\opencv\build\python\2.6 to sites-package)
except:
    print( "WRN: abcdk.image: NO OpenCV library ???" );
try:
    import cv2 # using opencv 2.4.5 # http://opencv.org # on windows: copy cv2.pyd from ...\opencv\build\python\2.7 to c:\python27\
    import cv2.cv as cv # backward compatible
except:
    print( "WRN: abcdk.image: NO OpenCV2 library ???" );

import time
import numpy
import shutil

def getDebugPath():
    strDebugPath = pathtools.getHomePath() + "abcdk_debug/image/";
    print( "DBG: abcdk.image.getDebugPath: debug path is '%s'" % strDebugPath );
    try:
        os.makedirs( strDebugPath );
    except:
        pass
    return strDebugPath; # TODO

def ariToPng( strStrImage, strDstImage ):
    "transform an Aldebaran Robotics Image to a PNG file"
    "strStrImage: a complete filename (with path). eg: 'C:/Documents and Settings/amazel/Application Data/Aldebaran/naoqi/share/naoqi/vision/visionrecognition/current/database0000000.ari'"
    "strDstImage: eg: c:/temp/toto.png"
    "return true if all's ok"

    nSizeHeader = 32;


    print( "INF: abcdk.image.ariToPng: %s => %s" % ( strStrImage, strDstImage ) );

    try:
        file = open( strStrImage, "rb" );
    except RuntimeError, err:
        print( "ERR: abcdk.image.ariToPng: can't open file '%s'" % strStrImage );
        return False;

    aBufFile = file.read();
    #print( "aBufFile len: %d" % len( aBufFile ) );
    nNbrByte = len( aBufFile ) / struct.calcsize("B");
    aBuf = struct.unpack_from( "B"*nNbrByte, aBufFile );
    file.close();
    #print( "aBufFile nbr pixel: %d" % nNbrByte );
    #print( "0x: %x%x%x%x" % (aBuf[0],aBuf[1],aBuf[2],aBuf[3] ) );

    if( ( aBuf[0] != 0x30 and aBuf[0] != 0x31 ) or aBuf[1] != 0x49 or aBuf[2] != 0x52 or aBuf[3] != 0x41 ):
        # wrong header
        print( "WRN: abcdk.image.ariToPng: wrong header: ARI Header not found in file '%s' (current header is 0x%2x%2x%2x%2x)" % (strStrImage,aBuf[0], aBuf[1], aBuf[2],aBuf[3] ) );
        return False;

    nImageWidth = aBuf[4]+(aBuf[5]<<8)+(aBuf[6]<<16)+(aBuf[7]<<24);
    nImageHeight = aBuf[8]+(aBuf[9]<<8)+(aBuf[10]<<16)+(aBuf[11]<<24);
    print( "INF: abcdk.image.ariToPng: image is %dx%d" % (nImageWidth, nImageHeight)  );
    nTheoricSize = nImageWidth * nImageHeight * 2;
    if( nTheoricSize != nNbrByte - nSizeHeader ):
        print( "WRN: abcdk.image.ariToPng: data in image file hasn't the good size ( theoric: %d != %d )" % (nTheoricSize, nNbrByte - nSizeHeader)  );
    import ImageDraw
    im = Image.new( "RGB", (nImageWidth, nImageHeight) );
    draw = ImageDraw.Draw(im)
    nIdxBuf = nSizeHeader; # skip header
    for y in range(0, nImageHeight):
        for x in range(0, nImageWidth,2):
            #~ nVal = aBuf[x+y*nImageWidth];
            #~ y = ( nVal & 0xF0 ) >> 4;
            #~ u = ( nVal & 0x03 );
            #~ v = ( nVal & 0x0C ) >> 2;

            y1  = aBuf[nIdxBuf];
            nIdxBuf += 1;
            u = aBuf[nIdxBuf];
            nIdxBuf += 1;
            y2  = aBuf[nIdxBuf];
            nIdxBuf += 1;
            v = aBuf[nIdxBuf];
            nIdxBuf += 1;
            r,g,b = color.yuvToRgb( [y1,u,v] );
            draw.point( (x, y), ( r,  g, b ) );
            r,g,b = color.yuvToRgb( [y2,u,v] );
            draw.point( (x+1, y), ( r,  g, b ) );
    try:
        im.save( strDstImage ); # default: found fileformat from extension
    except:
        print( "ERR: abcdk.image.ariToPng: can't write to file '%s'" % strDstImage );
        return False;

    return True;
# ariToPng - end

def ariToPng_ParseDirectory( strSrcDir, strDstDir = None ):
    "convert all ari to png in one directory"
    "return nbr of converted file"
    import filetools # it's not a big deal to make that here every call, we're dealing on folder containing images!
    nNbrConverted = 0;
    if( strDstDir == None ):
        strDstDir = strSrcDir + "pngs/";
    filetools.makedirsQuiet( strDstDir );

    for strFilename in os.listdir( strSrcDir ):
        print( "strFilename: %s" % strFilename );
        if( ".ari" in strFilename ):
            strFullPath = os.path.join( strSrcDir, strFilename );
            strDstFilename = strDstDir + strFilename.replace( ".ari", ".png" );
            if( ariToPng( strFullPath, strDstFilename ) ):
                nNbrConverted += 1;
    return nNbrConverted;
# ariToPng_ParseDirectory - end

def showImage( bufferImage, rTimeAutoClose = -1, strWindowName = "abcdk.image.showImage" ):
    """
    Show a buffer to the user
    - rTimeAutoClose: close image after that time (in sec)
    """
    strDebugWindowName = strWindowName; # "DebugWindow"; # set to false to have no debug windows
    cv.NamedWindow( strDebugWindowName, cv.CV_WINDOW_AUTOSIZE);

    cv.ShowImage( strDebugWindowName, bufferImage );

    nKey = 0;
    if( rTimeAutoClose != -1 ):
        timeToClose = time.time() + rTimeAutoClose;
    while( nKey != ord( 'q' ) and ( rTimeAutoClose == -1 or timeToClose > time.time() ) ):
        nKey =  cv.WaitKey(1);
# showImage - end

def showImage2( bufferImage, rTimeAutoClose = -1, strWindowName = "abcdk.image.showImage" ):
    """
    Show a buffer to the user
    - rTimeAutoClose: close image after that time (in sec)
    """
    strDebugWindowName = strWindowName; # "DebugWindow"; # set to false to have no debug windows
    cv.NamedWindow( strDebugWindowName, cv.CV_WINDOW_AUTOSIZE);

    cv.imshow( strDebugWindowName, bufferImage );
    #cv.moveWindow( strDebugWindowName, 50, 0 ); # don't work on window

    nKey = 0;
    if( rTimeAutoClose != -1 ):
        timeToClose = time.time() + rTimeAutoClose;
    while( nKey != ord( 'q' ) and ( rTimeAutoClose == -1 or timeToClose > time.time() ) ):
        nKey =  cv.WaitKey(1);
# showImage - end

def showImageFromFile( strImageFile, listRect = [] ):
    """
    Show a buffer to the user, print some rect on it
    """
    strDebugWindowName = "Test"; # "DebugWindow"; # set to false to have no debug windows
    cv.NamedWindow( strDebugWindowName, cv.CV_WINDOW_AUTOSIZE);

    imageBuffer = cv.LoadImage( strFilename );

    for rect in listRect:
        cv.Rectangle( imageBuffer, (rect[0], rect[1]), (rect[0]+rect[2], rect[1]+rect[3]), cv.RGB(0, 255, 0), 3, 8, 0);
        center = (rect[0]+rect[2]/2, rect[1]+rect[3]/2);
        size = (rect[2], rect[3]);
        smile = ( (center[0], center[1]+int(size[1]*0.01)), (center[0]-int(size[0]*0.4), center[1]-int(size[1]*0.1) ), (center[0]+0, center[1]+int(size[1]*0.2)),(center[0]+int(size[0]*0.4), (center[1]-int(size[1]*0.1) ) ) );
        cv.FillPoly( imageBuffer, [smile], cv.RGB(255, 255, 255), cv.CV_AA );
        # draw contours
        for i in range( len( smile )  ):
            cv.Line( imageBuffer, smile[i], smile[(i+1)%len(smile)], 0, 2 );


    cv.ShowImage( strDebugWindowName, imageBuffer );
    nKey = 0;
    while( nKey != ord( 'q' ) ):
        nKey =  cv.WaitKey(1);
# showImageFromFile - end

def showImage2( bufferImage, rTimeAutoClose = -1, strWindowName = "abcdk.image.showImage" ):
    """
    Show a numpy buffer image to the user
    - rTimeAutoClose: close image after that time (in sec)
    """
    strDebugWindowName = strWindowName;
    cv2.imshow(strDebugWindowName, bufferImage );

    nKey = 0;
    if( rTimeAutoClose != -1 ):
        timeToClose = time.time() + rTimeAutoClose;
    while( nKey != ord( 'q' ) and ( rTimeAutoClose == -1 or timeToClose > time.time() ) ):
        nKey =  cv.WaitKey(1);
# showImage2 - end



def getExifInfo( strFilename, astrParamList, astrDefaultValue = [] ):
    """
    extract a list of exif info from an image file
    - strFilename: the image file
    - astrParamList: a list of params
    - astrDefaultValue: params to output if no params found. if no default and no params found, the value will be None
    return list of value in the same order than parameter
    """
    # we import that just here, so image module could works even if no PIL present
    import PIL
    import PIL.ExifTags
    im = Image.open( strFilename );
    info = im._getexif();
    ret = {};
    aListReturn = [None]*len(astrParamList);
    # put default params
    aListReturn[:len(astrDefaultValue)] = astrDefaultValue;
    if info == None:
        return aListReturn;

    for tag, value in info.items():
         strDecodedName = PIL.ExifTags.TAGS.get( tag, tag );
         #~ print( "%s: %s" % ( strDecodedName, value ) );
         if( strDecodedName in astrParamList ):
             idx = astrParamList.index( strDecodedName );
             aListReturn[idx] = value;
    #~ print( "aListReturn: %s" % str( aListReturn ) );
    return aListReturn;
# getExifInfo - end


def getImageProperties( bufferImage ):
    """
    Return a string containing all properties of an image
    bufferImage: opencv image buffer
    """
    strOut = "";
    strOut += "Image properties:\n";



    if( hasattr( bufferImage, "width" ) ):
        # image is an IpImage - opencv1
        nWidth, nHeight = bufferImage.width, bufferImage.height;
        nChannels, nDepth = bufferImage.nChannels, bufferImage.depth;
    else:
        # image is a numpy array - opencv2
        nHeight, nWidth, nChannels = bufferImage.shape[:3];
        nDepth = bufferImage.dtype.itemsize * 8;

    strOut += "size  X: %4d, size Y:%4d\n" % ( nWidth, nHeight );
    strOut += "channel: %4d, depth :%4d\n" % ( nChannels, nDepth );
    return strOut;
# getImageProperties - end

def getImageSharpness(  bufferImage, nMethod = 0 ):
    """
    compute image sharpness and luminosity
    return [rSharpness, rLuminosity]
    bufferImage: opencv image buffer
    nMethod: type of computation method: 0: average on Sobel, 1: average on Laplacien, 2: maxLocal on Laplacien, 3: max-min on Laplacien
    """
    
    if( not hasattr( bufferImage, "width" ) ):
        # image is a numpy array - opencv2
        rSharpness = cv2.Laplacian( bufferImage, cv2.CV_64F).var()
        if 0:
            # max of each quarter
            v1 = cv2.Laplacian( bufferImage[0:bufferImage.shape[0]/2,0:bufferImage.shape[1]/2], cv2.CV_64F).var()
            v2 =  cv2.Laplacian( bufferImage[0:bufferImage.shape[0]/2,bufferImage.shape[1]/2:bufferImage.shape[1]], cv2.CV_64F).var()
            v3 = cv2.Laplacian( bufferImage[bufferImage.shape[0]/2:bufferImage.shape[0],0:bufferImage.shape[1]/2], cv2.CV_64F).var()
            v4 = cv2.Laplacian( bufferImage[bufferImage.shape[0]/2:bufferImage.shape[0],bufferImage.shape[1]/2:bufferImage.shape[1]], cv2.CV_64F).var()
            rSharpness = max(v1,v2,v3,v4)
        rLuminosity = numpy.mean( bufferImage );
        # to have the 3
        return [rSharpness, rLuminosity]

    # print( "DBG: getImageSharpness: nMethod: %d" % nMethod );

    # workSize = (bufferImage.width, bufferImage.height);
    currentRoi = cv.GetImageROI( bufferImage );
    workSize = (currentRoi[2], currentRoi[3]);

    if( nMethod == 0 or nMethod == 1 ):
        filtered = cv.CreateImage( workSize, cv.IPL_DEPTH_32F, bufferImage.nChannels );
        if( nMethod == 0 ):
            cv.Sobel( bufferImage, filtered, xorder = 1, yorder = 1 );  # for that it's fine to then filter on < 0.16
        else:
            # for this one filter on < 10
            cv.Laplace( bufferImage, filtered ); #  CV_16S
        # showImage( filtered );
        final = cv.CreateImage( workSize, cv.IPL_DEPTH_32F, bufferImage.nChannels );
        cv.Threshold( filtered, final, 20, 0, cv.CV_THRESH_TOZERO );
    #    showImage( final );
        avgFinal = cv.Avg( final );
        if( bufferImage.nChannels == 3 ):
            rSharpness = ( avgFinal[0]+avgFinal[1]+avgFinal[2] ) / 3;
        else:
            rSharpness = avgFinal[0];
    else:
        # for this one filter on < 24
        filtered = cv.CreateImage( workSize, cv.IPL_DEPTH_16S, 1 );
        if( bufferImage.nChannels == 3 ):
            grayscale = cv.CreateImage( workSize, cv.IPL_DEPTH_8U, 1 );
            cv.CvtColor( bufferImage, grayscale, cv.CV_BGR2GRAY ); # this was crashing
        else:
            assert( bufferImage.nChannels == 1 );
            grayscale = bufferImage;
        #~ print getImageProperties( bufferImage );
        #~ print getImageProperties( grayscale );
        #~ print getImageProperties( filtered );

        cv.Laplace( grayscale, filtered ); #  CV_16S
        minVal, maxVal, minLoc, maxLoc = cv.MinMaxLoc( filtered );
        #~ print( "minVal: %f, maxVal: %f" % (minVal, maxVal,) );

        if( nMethod == 2 ):
            rSharpness = (maxVal)/10.;
        else:
            rSharpness = (maxVal-minVal)/10.;

#    print( str( avgFinal ) );
    return rSharpness;
# getImageSharpness - end

def getImageSharpness_Face(  bufferImage, nMethod = 0, nAddBorderX = 2, nAddBorderY = 18 ):
    """
    compute image sharpness and luminosity based on an image that should be cropped by a previous call of some haarextractor,
    so we could easily locate the left eye, and analyse sharpness on it!
    return [rSharpness, rLuminosity]
    bufferImage: opencv image buffer
    nMethod: type of computation method: 0: average on Sobel, 1: average on Laplacien, 2: maxLocal on Laplacien, 3: max-min on Laplacien
    nAddBorderX: the border automatically around the rectangle from the object detection
    nAddBorderY: ...
    """
    print( "DBG: getImageSharpness_Face: nMethod: %d *****" % nMethod );

    workSize = (bufferImage.width, bufferImage.height);
    #~ currentRoi = cv.GetImageROI( bufferImage );
    #~ workSize = (currentRoi[2], currentRoi[3]);
    print( "current workSize: %s" % str( workSize ) );
    rectFace = ( nAddBorderX, int(nAddBorderY*1.3), bufferImage.width-nAddBorderX*2, bufferImage.height-nAddBorderY*2 );
    xEyeCenter = rectFace[0] + rectFace[2]*33/106; # 34/106 is value from my head recognised by some haarextractor
    yEyeCenter = rectFace[1] + rectFace[3]*43/106;
    widthEye = rectFace[2]*18/106;
    heightEye = rectFace[2]*8/106 + 2;
    rectEye = (xEyeCenter-widthEye/2, yEyeCenter - heightEye/2, widthEye, heightEye );
    print( "INF: getImageSharpness_Face: rectFace: %s, rectEye: %s" % ( str( rectFace ), str( rectEye ) ) );
    results = cv.CreateImage( (rectEye[2], rectEye[3]), bufferImage.depth, bufferImage.nChannels );
    cv.SetImageROI( bufferImage, rectEye );
    currentRoi = cv.GetImageROI( bufferImage );
    workSize = (currentRoi[2], currentRoi[3]);
    print( "current eye rect reduced, worksize: %s" % str( workSize ) );
    cv.Copy( bufferImage, results );
    cv.SaveImage( "d:\\temp\\test_eyes\\FaceEyes_%.3f.png" % time.time(), bufferImage );
    time.sleep(0.1); # just to have another filename, pfff

    return getImageSharpness( bufferImage, nMethod );

# getImageSharpness_Face - end

#~ imageBuffer = cv.LoadImage( r"D:\Dev\git\appu_data\images_to_analyse\blur2\2012_10_19-15h26m35s0959ms_00__0011_Mazel_Alexandre_1.00__0054_Hervier_Thibault_0.50__sharp_3102__thresh_082.jpg", cv.CV_LOAD_IMAGE_GRAYSCALE );
#~ getImageSharpness_Face( imageBuffer );
#~ imageBuffer = cv.LoadImage( r"D:\Dev\git\appu_data\images_to_analyse\blur2\2012_10_19-15h26m34s0194ms_00.jpg", cv.CV_LOAD_IMAGE_GRAYSCALE );
#~ getImageSharpness_Face( imageBuffer );
#~ imageBuffer = cv.LoadImage( r"D:\Dev\git\appu_data\images_to_analyse\blur2\2012_10_19-15h26m35s0346ms_00.jpg", cv.CV_LOAD_IMAGE_GRAYSCALE );
#~ getImageSharpness_Face( imageBuffer );
#~ imageBuffer = cv.LoadImage( r"D:\Dev\git\appu_data\images_to_analyse\blur2\2012_10_19-15h26m50s0886ms_00.jpg", cv.CV_LOAD_IMAGE_GRAYSCALE );
#~ getImageSharpness_Face( imageBuffer );


def getImageQuality( bufferImage, nMethod = 0 ):
    """
    compute image sharpness and luminosity
    return [rSharpness, rLuminosity]
    bufferImage: opencv image buffer
    nMethod: type of computation method: 0: average on Sobel, 1: average on Laplacien, 2: maxLocal on Laplacien
    """
    rSharpness = getImageSharpness( bufferImage, nMethod = nMethod );
#    print( "Sharpness: %.2f" % rSharpness );
    avgLum = cv.Avg( bufferImage );
    #~ print( str( avgLum ) );
    if( bufferImage.nChannels == 3 ):
        rLuminosity = ( avgLum[0] + avgLum[1] + avgLum[2] ) / 3;
    else:
        rLuminosity = avgLum[0];
#    print( "Luminosity: %.1f" % rLuminosity );

    # modify a bit image with extreme luminosity
    if( rLuminosity < 106 ):
        rNormalisedSharpness = rSharpness*(128/rLuminosity);
    elif( rLuminosity > 150 ):
        rNormalisedSharpness = rSharpness*(128/rLuminosity);
    else:
        rNormalisedSharpness = rSharpness;
    return [rSharpness, rLuminosity, rNormalisedSharpness];
# getImageQuality - end

def getImageLuminosity( imageBuffer, nMethod = 0 ):
    """
    compute luminosity
    return [rSharpness, rLuminosity]
    bufferImage: opencv image buffer
    nMethod: type of computation method: 0: average on full image, 1: spot method: boost center weight, 2: super spot method, ...
    """
    avgLum = cv.Avg( imageBuffer );
    if( imageBuffer.nChannels == 3 ):
        rLuminosity = ( avgLum[0] + avgLum[1] + avgLum[2] ) / 3;
    else:
        rLuminosity = avgLum[0];

    if( nMethod > 0 ):
        cv.SetImageROI( imageBuffer, (imageBuffer.width/4, imageBuffer.height/4, imageBuffer.width/2, imageBuffer.height/2) );
        avgLum = cv.Avg( imageBuffer );
        if( imageBuffer.nChannels == 3 ):
            rSpotLuminosity = ( avgLum[0] + avgLum[1] + avgLum[2] ) / 3;
        else:
            rSpotLuminosity = avgLum[0];
        cv.ResetImageROI(imageBuffer);
        nNbrPart = nMethod+1;
        #~ print( "DBG: abcdk.image.getImageLuminosity: avg: %f, spot: %f" % (rLuminosity,rSpotLuminosity) );
        rLuminosity = ( rLuminosity * 1. / nNbrPart ) + (rSpotLuminosity * (nNbrPart-1) / nNbrPart );
    return rLuminosity;
# getImageLuminosity - end




def findFaceInFile( strFilename, strDebugFilename = "", strDebugWindowName = False, strAutoCropDst = False, nWidthMargin = 16, nHeightMargin = 40, nMinNeighbour = 2, nMinSizeAnalyse = 50 ):
    "Use a haar cascade to detect face in a file"
    "see haarDetect for detail"
    "(see haarDetect for detail)"
    strCascadeFileName = pathtools.getABCDK_Path() + "data/haarcascades/haarcascade_frontalface_alt.xml"
    return haarDetectFromFile( strCascadeFileName, strFilename, strDebugFilename, strDebugWindowName, strAutoCropDst , nWidthMargin, nHeightMargin, nMinNeighbour = nMinNeighbour, nMinSizeAnalyse = nMinSizeAnalyse );
# findFaceInFile - end

def findFaceInImage( imgBuffer, strDebugFilename = "", strDebugWindowName = False, strAutoCropDst = False, nWidthMargin = 16, nHeightMargin = 40, nMinNeighbour = 2, nMinSizeAnalyse = 50 ):
    "Use a haar cascade to detect face in a OpenCV Image"
    "see haarDetect for detail"
    "(see haarDetect for detail)"
    strCascadeFileName = pathtools.getABCDK_Path() + "data/haarcascades/haarcascade_frontalface_alt.xml"
    return haarDetect( strCascadeFileName, imgBuffer, strDebugFilename, strDebugWindowName, strAutoCropDst , nWidthMargin, nHeightMargin, nMinNeighbour = nMinNeighbour, nMinSizeAnalyse = nMinSizeAnalyse );
# findFaceInImage - end

def haarDetectFromFile( strCascadeFileName, strFilename, strDebugFilename = "", strDebugWindowName = False, strAutoCropDst = False, nWidthMargin = 16, nHeightMargin = 40, nMinNeighbour = 15, nMinSizeAnalyse = 50 ):
    "Use a haar cascade to detect things in a file"
    "(see haarDetect for detail)"
    try:
        imageBuffer = cv.LoadImage( strFilename );
    except BaseException, err:
        print( "ERR: haarDetectFromFile: image file '%s' not found. (err:%s)" % (strFilename, str(err)) );
        return False;
    return haarDetect( strCascadeFileName, imageBuffer, strDebugFilename, strDebugWindowName, strAutoCropDst , nWidthMargin, nHeightMargin, nMinNeighbour = nMinNeighbour, nMinSizeAnalyse = nMinSizeAnalyse );
# haarDetectFromFile - end

def haarDetectFromNaoCam( strCascadeFileName, nResolution, strDebugFilename = "", strDebugWindowName = False, strAutoCropDst = False, nWidthMargin = 16, nHeightMargin = 40, nMinNeighbour = 15, nMinSizeAnalyse = 50 ):
    "Use a haar cascade to detect things in a file"
    "nResolution: an int describing wanted resolution: kQQVGA = 0; kQVGA = 1; kVGA = 2; k4VGA = 3; # k4VGA work only on a V4"
    "(see haarDetect for detail)"
    timeDebug = time.time();
    import naoqitools # so we don't have to do that at the beginning of the file (less interdependency)
    print( "time of importing naoqi: %fs" % time.time() - timeDebug ); # TODO: check it's ok to do that every call !
    avd = naoqitools.myGetProxy( "ALVideoDevice" );
    strMyClientName = "acdk.image";
    kBGR = 13;
    nFps = 5;
    strMyClientName = avd.subscribe( strMyClientName, nResolution, kBGR, nFps );
    nSizeX, nSizeY = avd.resolutionToSizes( avd.getGVMResolution( strMyClientName ) );
    print( "GVM has Image properties: %dx%d" % (nSizeX,nSizeY) );
    imageBuffer = cv.CreateImage( (nSizeX, nSizeY), cv.IPL_DEPTH_8U, 3 );

    try:
        dataImage = avd.getImageRemote( strMyClientName ); # want to make local, but it doesn't works in python (If I'm right) # TODO: check it!
        avd.unsubscribe( strMyClientName );
        if( dataImage == None ):
            print( "ERR: dataImage is none!" );
        else:
            nSizeX = dataImage[0];
            nSizeY = dataImage[1];
            #~ print( "Image get: %dx%d" % (nSizeX,nSizeY) );
            #~ print( "Image prop: layer: %d, format: %d" % (dataImage[2],dataImage[3]) );
            image = dataImage[6];
            #~ print( "first char: '%s','%s','%s'" % ( image[0+960],image[1],image[2] )  );
            #~ print( "first char orded: %s,%s,%s" % ( ord( image[0] ), ord( image[1] ), ord( image[2] )  ) );
            # bufferImageToDraw.data = image;
            # converted locally in NAO's  head
            cv.SetData( imageBuffer, image );
            return haarDetect( strCascadeFileName, imageBuffer, strDebugFilename, strDebugWindowName, strAutoCropDst , nWidthMargin, nHeightMargin, nMinNeighbour );
    except BaseException, err:
        print( "ERR: haarDetectFromNaoCam: catched error: %s" % str(err) );
    return False;
# haarDetectFromNaoCam - end


def haarDetect( strCascadeFileName, imageBuffer, strDebugFilename = "", strDebugWindowName = False, strAutoCropDst = False, nWidthMargin = 16, nHeightMargin = 40, nMinNeighbour = 15, nMinSizeAnalyse = 50 ):
    "Use a haar cascade to detect things in an image"
    "strCascadeFileName: the file to use"
    "imageBuffer: an OpenCv image buffer"
    "strDebugFilename: when set, save original image with rectangle around detected objects in a file"
    "strDebugWindowName: draw the image in some existant OpenCV windows"
    "strAutoCropDst: the biggest cropped face would be cropped and saved to a file"
    "nWidthMargin: Margin to add around the cropped objects"
    "nHeightMargin: ..."
    "nMinNeighbour: object with less neighbours would be rejected (for face detection, 2 is ok), for nao detection (stage15), I like it between 15 and 30"
    "return False on error (no image, no cascade, and other errors), [] if no objects found or a list of objects: [obj1,obj2, ...]"
    "with obj: [[x,y,w,h],neighbours], neighbours could give an idea of the confidence of the detection"

    timeBegin = time.time();

    if( strDebugWindowName ):
        cv.ShowImage( strDebugWindowName, imageBuffer );
        cv.WaitKey(1);

    image_size = cv.GetSize(imageBuffer);
    print( "INF: haarDetect: image has size %s (%dx%d)" % ( str( image_size ), imageBuffer.width, imageBuffer.height ) );

    # create grayscale version
    grayscale = cv.CreateImage( image_size, cv.IPL_DEPTH_8U, 1 );

    # simple way:
    cv.CvtColor( imageBuffer, grayscale, cv.CV_BGR2GRAY ); # this was crashing

    # workaround when CvtColor crashes:
    #~ newFrameImage32F = cv.CreateImage(image_size, cv.IPL_DEPTH_32F, 3);
    #~ cv.ConvertScale(image,newFrameImage32F);

    #~ newFrameImageGS_32F = cv.CreateImage (image_size, cv.IPL_DEPTH_32F, 1);
    #~ cv.CvtColor(newFrameImage32F,newFrameImageGS_32F,cv.CV_RGB2GRAY);

    #~ cv.ConvertScale(newFrameImageGS_32F,grayscale);

    # create storage
    storage = cv.CreateMemStorage(0);
    # cv.ClearMemStorage(storage)

    # equalize histogram
    cv.EqualizeHist(grayscale, grayscale);

    # detect objects
    try:
        cascade = cv.Load( strCascadeFileName );
    except BaseException, err:
        print( "ERR: haarDetect: haarcascade '%s' not found. (err:%s)" % ( strCascadeFileName, str(err)) );
        return False;
    timeAnalyse = time.time();
    objectsFound = cv.HaarDetectObjects(grayscale, cascade, storage, 1.2, nMinNeighbour, cv.CV_HAAR_DO_CANNY_PRUNING, (nMinSizeAnalyse, nMinSizeAnalyse) );
    print( "INF: haarDetect: analyse takes %.2fs" % ( time.time() - timeAnalyse ) );

    if objectsFound:
        print( "INF: haarDetect: %d Object(s) detected!" % len( objectsFound ) );
        if( not strAutoCropDst or False ):
            for obj in objectsFound:
                print( "object detected: %s" % str( obj ) );
                rect = obj[0];
                cv.Rectangle( imageBuffer, (rect[0], rect[1]), (rect[0]+rect[2], rect[1]+rect[3]), cv.RGB(0, 255, 0), 3, 8, 0);
    else:
        print( "INF: haarDetect: NO OBJECT!" );

    if( strDebugWindowName ):
        cv.ShowImage(strDebugWindowName, imageBuffer );
        cv.WaitKey(1);

    if( strDebugFilename and objectsFound ):
        print( "INF: haarDetect: writing debug image to file '%s'" % strDebugFilename );
        cv.SaveImage( strDebugFilename, imageBuffer );

    if( strAutoCropDst and objectsFound ):
        # found bigger one
        objInfo = None;
        nSizeMax = 0;
        for obj in objectsFound:
            nSize = obj[0][2]*obj[0][3];
            if( nSize > nSizeMax ):
                objInfo = obj[0];
                nSize = nSizeMax;

        rect = (max( objInfo[0]-nWidthMargin, 0), max( objInfo[1]-int(nHeightMargin*1.3), 0 ), objInfo[2]+nWidthMargin*2, objInfo[3]+nHeightMargin*2 ); # the *1.3 is to have more on the top of the face (hair) than on the bottom
        if( rect[0] + rect[2] >= imageBuffer.width ):
            rect = (rect[0], rect[1], imageBuffer.width - rect[0], rect[3] ); # you can't assign in a tuple, argggh
        if( rect[1] + rect[3] >= imageBuffer.height ):
            rect = ( rect[0], rect[1], rect[2], imageBuffer.height - rect[1] );
        results = cv.CreateImage( (rect[2], rect[3]), cv.IPL_DEPTH_8U, 3 );
        print( "INF: haarDetect: rect: %s" % str( rect ) );
        cv.SetImageROI( imageBuffer, rect );
        #~ print( "imageBuffer: " + str( imageBuffer.depth ) );
        #~ print( "results: " + str( results.depth ) );
        #~ print( "imageBuffer: " + str( imageBuffer.nChannels ) );
        #~ print( "results: " + str( results.nChannels ) );
        #~ print( "imageBuffer: " + str( imageBuffer.width ) );
        #~ print( "results: " + str( results.width ) );
        #~ print( "imageBuffer: " + str( imageBuffer.height ) );
        #~ print( "results: " + str( results.height ) );
        #~ print( "imageBuffer: getRoi" + str( cv.GetImageROI(imageBuffer) ) );
        cv.Copy( imageBuffer, results );
        cv.SaveImage( strAutoCropDst, results );
        if( strDebugWindowName ):
            cv.ShowImage(strDebugWindowName, results );
            cv.WaitKey(1);
    print( "INF: haarDetect: end (%.2fs)" % (time.time()-timeBegin) );

    # convert to real array of array and not array of fucking tuple
    i = 0;
    while i < len( objectsFound ):
        objectsFound[i] = list(objectsFound[i]);
        objectsFound[i][0] = list(objectsFound[i][0]);
        i += 1;

    # sort for bigger and having more neighbours
    # ?

    if( objectsFound ):
        return objectsFound;
    return [];
# haarDetect - end

def addRectangles( strImageFilename, listSquare, strImageFilenameDest = "", nStyle = 0, astrListText = [] ):
    """
    add square(s) to an image
    return True if all's ok
    strImageFilename: an image
    listSquare: a list of square: [[x,y,w,h,...], [x,y,w,h,...], ... ] aka format1 or [[ [x,y,w,h],...], [ [x,y,w,h],...], ... ] aka format2
    strImageFilenameDest: optionnal destination file (default: overwrite source)
    nStyle: style of drawing, 0 is photo frame Lamaz style, 1 is blue
    astrListText: optionnal text to put under each people
    """


    if( listSquare == None or len( listSquare ) < 1 ):
        # Nothing to do
        if( strImageFilenameDest != "" ):
            shutil.copyfile(  strImageFilename, strImageFilenameDest );
        return True;

    if( strImageFilenameDest == "" ):
        strImageFilenameDest = strImageFilename;

    try:
        imageBuffer = cv.LoadImage( strImageFilename );
    except BaseException, err:
        print( "ERR: image.addSquare: image source file '%s' error: %s" % ( strImageFilename, str( err ) ) );
        return False;

    colorBase = None;
    colorAround = None;
    if( nStyle == 0 ):
        # Lamaz Style
        colorBase = cv.RGB(0, 0, 0);
        colorAround = cv.RGB(255, 255, 255);
        nThicknessAround = 3;
    else:
        colorBase = None;
        colorAround = cv.RGB(0, 255, 0);
        nThicknessAround = 2;

    if( len( astrListText ) > 0 ):
        nThickness = 2;
        font = cv.InitFont( cv.CV_FONT_HERSHEY_SIMPLEX, 0.5, 0.5, 0, nThickness, 8 );

    for idx, rect in enumerate( listSquare ):
        if( isinstance( rect[0], list ) ):
            # format2
            rect = rect[0];
        pt1 = (rect[0], rect[1]);
        pt2 = (rect[0]+rect[2], rect[1]+rect[3]);
        if( colorBase != None ):
            cv.Rectangle( imageBuffer, pt1, pt2, colorBase, 1, 4, 0);
        if( colorAround != None ):
            nOffset = nThicknessAround;
            pt1 = (pt1[0]-nOffset, pt1[1]-nOffset);
            pt2 = (pt2[0]+nOffset, pt2[1]+nOffset);
            cv.Rectangle( imageBuffer, pt1, pt2, colorAround, nThicknessAround, 16, 0);
        if( idx < len( astrListText ) ):
            textSize = cv.GetTextSize( astrListText[idx], font );
            print( str( textSize ) );
            colorText = colorBase;
            if( colorText == None ):
                colorText = colorAround;
            cv.PutText( imageBuffer, astrListText[idx], ((pt1[0]+pt2[0])/2-(textSize[0][0]/2), pt1[1]-8), font, colorText );
    cv.SaveImage( strImageFilenameDest, imageBuffer );
    return True;
# addRectangles - end
# addRectangles( "D:/Dev/data/photos_de_groupes/image8.jpg", [ [200,80,56,80], [40,40,100,40], [[10,80,10,10], "toto", 0.2], [320,90,50,70],[470,120,50,60] ], "D:/Dev/data/photos_de_groupes/image8_rect.jpg", nStyle = 0, astrListText = ["Remy", "Bug1", "Bu2", "Alexandre", "J.P."] );

def getCroppedImages(strPicName, listSquare, strDestName=""):
    """
    save the rectangles from listSquare into several cropped image files
    strPicName: the full path to the picture file
    listSquare: a list of square: [[x,y,w,h,...], [x,y,w,h,...], ... ] aka format1 or [[ [x,y,w,h],...], [ [x,y,w,h],...], ... ] aka format2
    strDestName: the full path with name without format (example path/to/picfolder/image), the function adds #.jpg after the strDestName by itself. Default writes output as strPicName with a number before the .jpg
    """

    if( listSquare == None or len( listSquare ) < 1 ):
        # Nothing to do
        return True

    if( strDestName == "" ):
        strDestName = strPicName[:-4]

    try:
        imageBuffer = cv.LoadImage( strPicName );
    except BaseException, err:
        print( "ERR: image.addSquare: image source file '%s' error: %s" % ( strPicName, str( err ) ) );
        return False;
    for idx, rect in enumerate( listSquare ):
        if( isinstance( rect[0], list ) ):
            # format2
            rect = rect[0];
        roi= cv.GetSubRect(imageBuffer, tuple(rect[:4]));
        saveName= strDestName + str(idx) + '.jpg'
        cv.SaveImage(saveName, roi)
    return True
# getCroppedImages - end
# getCroppedImages('/home/sebastien/Pictures/image.jpg', [[50, 50, 50, 50], [100, 50, 50, 50], [[50, 100, 75, 25], 'myId', 3], [[100, 100, 25, 100], 'me', 45], [0,0,200,100]])
# getCroppedImages("D:/Dev/data/photos_de_groupes/image8.jpg", [ [200,80,56,80], [40,40,100,40], [[10,80,10,10], "toto", 0.2], [320,90,50,70],[470,120,50,60] ], "D:/Dev/data/photos_de_groupes/image8_rect")

def convertAbsolutePositionToCentredRelative( rectInImage, nMaxX = 640, nMaxY = 480 ):
    """
    take a rectangle (left, top, w, h) from some extractors, and return the centered point, in image relative [-1,1] and the width and height [0,1]
    eg: [504,206,54,54] => [0.659, -0.0292, 0.084, 0.11]
    """
    x = rectInImage[0] + rectInImage[2]/2;
    y = rectInImage[1] + rectInImage[3]/2;
    x = ( (2*x) / float( nMaxX ) ) - 1;
    y = ( (2*y) / float( nMaxY ) ) - 1;
    sx = rectInImage[2] / float( nMaxX );
    sy = rectInImage[3] / float( nMaxY );
    return [x,y,sx,sy];
# convertAbsolutePositionToCentredRelative - end
#~ print( convertAbsolutePositionToCentredRelative( [504,206,54,54] ) );

def convertAbsolutePositionToCameraRelative( ptInImage, nMaxX = 640, nMaxY = 480 ):
    """
    take a point [x,y], and return it in image relative [-1,1]
    eg: [639,479] => [~1.0,~1.0]
    """
    x = ptInImage[0]
    y = ptInImage[1];
    x = ( (2*x) / float( nMaxX-1 ) ) - 1;
    y = ( (2*y) / float( nMaxY-1 ) ) - 1;
    return [x,y];
# convertAbsolutePositionToCameraRelative - end
#~ print( convertAbsolutePositionToCameraRelative( [0,0] ) );
#~ print( convertAbsolutePositionToCameraRelative( [320,240] ) );
#~ print( convertAbsolutePositionToCameraRelative( [639,479], 640,480 ) );


def convertAbsolutePositionToCameraRelative05( ptInImage, nMaxX = 640, nMaxY = 480 ):
    """
    take a point [x,y], and return it in image relative [-0.5,0.5]
    eg: [639,479] => [~1.0,~1.0]
    special case: value at <0, will remains the same ! (-1 => -1, -2 => -2) ...
    """
    x = ptInImage[0];
    y = ptInImage[1];
    if( x >= 0 ):
        x = ( (x) / float( nMaxX-1 ) ) - 0.5;
    if( y >= 0 ):
        y = ( (y) / float( nMaxY-1 ) ) - 0.5;
    return [x,y];
# convertAbsolutePositionToCameraRelative05 - end
#~ print( convertAbsolutePositionToCameraRelative05( [0,0] ) );
#~ print( convertAbsolutePositionToCameraRelative05( [639,479] ) );

def getResolutionFromEnum( nResolutionConstant ):
    """
    AL::kQQVGA  0   Image of 160*120px
    AL::kQVGA   1   Image of 320*240px
    AL::kVGA    2   Image of 640*480px
    AL::k4VGA   3   Image of 1280*960px
    AL::k16VGA  4   Image of 2560*1920px
    AL::k720p   5   Image of 1280*720px
    AL::k1080p  6   Image of 1920*1080px
    AL::kQQQVGA 7   Image of 80*60px
    AL::kQQQQVGA 8   Image of 40*30px
    return an array [res_x,res_y]
    """
    aResolutions = {0:[160,120], 1 : [320,240], 2 : [640,480], 3 : [1280,960], 4 : [2560,1920], 5 : [1280,720], 6 : [1920,1080], 7 : [80,60], 8 : [40,30]}
    return aResolutions[nResolutionConstant]
# getResolutionFromEnum - end

def convertAriToPng():
    #
    # convert ari to png
    #
    # single shot
    # bRet = ariToPng( "C:/Documents and Settings/amazel/Application Data/Aldebaran/naoqi/share/naoqi/vision/visionrecognition/current/database0000000.ari", "c:/temp/toto.png" );

    # an entire folder; results goes to the "original_folder/pngs".
    strFolderPath = "C:/Documents and Settings/amazel/Application Data/Aldebaran/naoqi/share/naoqi/vision/visionrecognition/current/";  # windows path
    # strFolderPath = "~/.local/share/naoqi/vision/visionrecognition/current/" # sous linux
    strFolderPath = "I:/night-rosetta/";
    bRet = 0 < ariToPng_ParseDirectory( strFolderPath );
    if( bRet ):
        os.system( 'explorer "' + strFolderPath.replace( '/', '\\' ) + '"' );
    return bRet;
# convertAriToPng - end

def applyMethodOnFile( strFilename, strMethodName, rCenterRatio = 1., bForceGrayScale = False, extraParams = None ):
    """
    apply a method to an image
    rCenterRatio: launch it only on a percentage of image, eg 0.2 => compute only on the image reduced to 20% centered (1/5 of total image, on each dimension)
    return: None on error or values (depends of the called applyed).
    """
    #print( "DBG: applyMethodOnFile: strFilename: %s" % strFilename );
    try:
        if( bForceGrayScale ):
            imageBuffer = cv.LoadImage( strFilename, cv.CV_LOAD_IMAGE_GRAYSCALE );
        else:
            imageBuffer = cv.LoadImage( strFilename );
        # print getImageProperties( imageBuffer );
    except BaseException, err:
        print( "ERR: applyMethodOnFile: image file '%s' not an image?. (err:%s)" % (strFilename, str(err)) );
        return None;
    if( rCenterRatio != 1. ):
        nReduceX = int( imageBuffer.width*(1-rCenterRatio) );
        nReduceY = int( imageBuffer.height*(1-rCenterRatio) );
        rectReduced = ( nReduceX/2, nReduceY/2, imageBuffer.width-nReduceX, imageBuffer.height-nReduceY );
        # print( rectReduced );
        cv.SetImageROI( imageBuffer, rectReduced );

    # eval( "retVal = %s( imageBuffer )" % strMethodName, globals(), locals() );
    #func = getattr( sys.modules["__main__"], strMethodName ); # works when launched from scite module but not from another module/application
    func = getattr( sys.modules[__name__], strMethodName );
    if( extraParams == None or len(extraParams) == 0 ):
        retVal = func( imageBuffer );
    elif( len(extraParams) == 1 ):
        retVal = func( imageBuffer, extraParams[0] );
    elif( len(extraParams) == 2 ):
        retVal = func( imageBuffer, extraParams[0], extraParams[1] );
    elif( len(extraParams) == 3 ):
        retVal = func( imageBuffer, extraParams[0], extraParams[1], extraParams[2] );
    if( not isinstance( retVal, list ) ):
        retVal = [retVal]; # applyMethodOnFile: return always a list of values
    print( "INF: applyMethodOnFile: %s x %s( %s )\n=> %s" % ( strFilename.split(os.sep)[-1], strMethodName, extraParams, str( retVal ) ) );
    return retVal;
# applyMethodOnFile - end
#~ applyMethodOnFile( "/home/likewise-open/ALDEBARAN/amazel/dev/git/appu_applications/facevacs/data_to_learn/test_ju/2012_09_30-21h18m14s0717ms_00__too_blury__760__0011_Mazel_Alexandre_1.00__sharp_760__thresh_139.jpg", "getImageQuality", 0.6, False, [2] );
#~ applyMethodOnFile( "/home/likewise-open/ALDEBARAN/amazel/dev/git/appu_applications/facevacs/data_to_learn/test_ju/2012_09_30-21h18m27s0024ms_00__0011_Mazel_Alexandre_1.00__sharp_3440__thresh_082.jpg", "getImageQuality", 0.6, False, [2] );
#~ applyMethodOnFile( "/home/likewise-open/ALDEBARAN/amazel/dev/git/appu_applications/facevacs/data_to_learn/test_ju/2012_09_30-21h19m01s0090ms_00__0011_Mazel_Alexandre_0.99__0058_Gouaillier_David_0.67__0117_Boudot_Nicolas_0.62__sharp_6759__thresh_092.jpg", "getImageQuality", 0.6, False, [2] );
#~ applyMethodOnFile( "/home/likewise-open/ALDEBARAN/amazel/dev/git/appu_applications/facevacs/data_to_learn/test_ju/2012_09_30-21h35m33s0731ms_00__too_blury__840__0074_Clerc_Vincent_0.65__0014_Rolland_Manuel_0.62__0054_Hervier_Thibault_0.58__sharp_840__thresh_136.jpg", "getImageQuality", 0.4, False, [2] );
#~ applyMethodOnFile( "/home/likewise-open/ALDEBARAN/amazel/dev/git/appu_applications/facevacs/data_to_learn/test_ju/2012_09_30-22h08m33s0223ms_00__0055_Gelin_Rodolphe_1.00__0051_Houssin_David_0.58__0123_Mestre_Andrea_0.51__sharp_4100__thresh_082.jpg", "getImageQuality", 0.4, False, [2] );
#~ applyMethodOnFile( "/home/likewise-open/ALDEBARAN/amazel/dev/git/appu_applications/facevacs/data_to_learn/test_ju/2012_09_30-22h08m38s0613ms_00__too_blury__1320.jpg", "getImageQuality", 0.4, False, [2] );
#~ applyMethodOnFile( "/home/likewise-open/ALDEBARAN/amazel/dev/git/appu_applications/facevacs/data_to_learn/test_ju3/2012_10_01-19h06m17s0347ms_00__0004_Beyne_Caroline_0.96__0005_Boudier_Celine_0.83__0058_Gouaillier_David_0.80__sharp_12303__thresh_089.jpg", "getImageQuality", 0.4, True, [3] );


def launchMethodOnDirectory( strPath, strMethodName, rCenterRatio = 1., bForceGrayScale = False, extraParams = None ):
    """
    apply a method to all images in a directory
    rCenterRatio: see launchMethodOnFile
    """
    import filetools # it's not a big deal to make that here every call, we're dealing on folder containing images!

    nCpt = 0;
    stats = [None]*16;  # make stats on returned variables
    timeBegin = time.time();
    for strFilename in os.listdir( strPath ):
        if( os.path.isdir(strPath+strFilename) ):
            continue;
        #~ if( nCpt > 2 ):
            #~ break;
        timeBegin = time.time();
        retVal = applyMethodOnFile( strPath + strFilename, strMethodName, rCenterRatio = rCenterRatio, bForceGrayScale = bForceGrayScale, extraParams = extraParams );
        print( "time Method: %f" % (time.time() - timeBegin ) );
        if( retVal == None ):
            continue;
        nCpt += 1;
        # specific process to make specifically: sort image related to blur values
        if( True ):
            rValToComp = retVal[0]; # 0.16 / 10 / 24 // for getImageSharpness_Face = retVal[2];
            #~ rValToComp = retVal[2]; # 18
            if( rValToComp < 20 ):
                strCopyToDest = "blur";
            else:
                strCopyToDest = "not_blur";
            strDest = strPath + os.sep + strCopyToDest + os.sep;
            filetools.makedirsQuiet( strDest );
            strFileDest = strFilename.replace( ".jpg", ("_sharpness_%03d" % ( rValToComp * 100 )) + ".jpg"  );
            filetools.copyFile( strPath + strFilename, strDest + strFileDest, bVerbose = False );

        # compute stats
        for idx,val in enumerate( retVal ):
            if( stats[idx] == None ):
                # create new stats
                stats[idx] = [999999,0,-99999999];
            if( val < stats[idx][0] ):
                stats[idx][0] = val;
            if( val > stats[idx][2] ):
                stats[idx][2] = val;
            stats[idx][1] += val;
        # for - end

    # for - end
    # print stats
    print( "\n" );
    for idx,val in enumerate( stats ):
        if( val != None ):
            print( "var %d: min: %.2f, avg: %.2f, max: %.2f" % (idx, val[0], val[1] / nCpt, val[2] ) );
    print( "\n" );
    print( "INF: launchMethodOnDirectory: end: %d successfully proceeded file(s) (avg time:%f)\n" % (nCpt, (time.time() - timeBegin)/nCpt ) );
# launchMethodOnDirectory - end
# launchMethodOnDirectory( "D:/Dev/git/appu_applications/facevacs/rough/selected9_faces/", "getImageQuality", 0.6 );
# launchMethodOnDirectory( "D:/Dev/git/appu_applications/facevacs/data_to_learn/blur_test/", "getImageQuality", 0.6 );
#~ for method in range(3):
    #~ launchMethodOnDirectory( "/home/likewise-open/ALDEBARAN/amazel/dev/git/appu_applications/facevacs/data_to_learn/blur_test_short/", "getImageQuality", 0.6, False, [method] );
#launchMethodOnDirectory( "/home/likewise-open/ALDEBARAN/amazel/dev/git/appu_applications/facevacs/data_to_learn/test_ju4/", "getImageQuality", 0.4, True, [3] );
# launchMethodOnDirectory( "D:/Dev/git/appu_applications/facevacs/data_to_learn/good/0", "getImageQuality", 0.4, True, [2] );
#launchMethodOnDirectory( "D:/Dev/git/appu_data/images_to_analyse/blur2/", "getImageSharpness_Face" );

def reduceBigger( strSrcFile, strDstFile = None, nWidthMax = 1600, nHeightMax = 1600 ):
    """
    If the image is bigger than a specific geometry, it will reduce them
    (a bit more smart than a raw "convertimage.jpg -resize 50% image.jpg
    strDstFile: optionnal destination filename or None if overwriting mode.
    nWidthMax,nHeightMax: The size to not oversize
    return: 1 if it has been reduced, 0 if nothing has been done, -1 on error
    """
    try:
        imageBuffer = cv.LoadImage( strSrcFile );
    except BaseException, err:
        print( "ERR: image.reduceBigger: while loading image source file '%s', error: %s" % ( strSrcFile, str( err ) ) );
        return -1;
    # try - end

    if( imageBuffer.width <= nWidthMax and imageBuffer.height <= nHeightMax ):
        return 0;

    if( strDstFile == None ):
        strDstFile = strSrcFile;

    half_size = ( imageBuffer.width/2,imageBuffer.height/2 );
    print( "INF: image.reduceBigger: %s => %s" % (strSrcFile, strDstFile) );
    while( 1 ):
        print( "INF: image.reduceBigger: %d,%d => %s" % (imageBuffer.width,imageBuffer.height, half_size ) );
        small_image = cv.CreateImage( half_size, imageBuffer.depth, imageBuffer.nChannels );
        cv.PyrDown( imageBuffer, small_image, cv.CV_GAUSSIAN_5x5 ); # PyrDown only divide by 2
        if( half_size[0] <= nWidthMax and half_size[1] <= nHeightMax ):
            break;
        half_size = ( half_size[0] / 2,half_size[1] / 2 );
        imageBuffer = small_image;
    # while - end

    cv.SaveImage( strDstFile, small_image );

    return 1;
# reduceBigger - end

def foundSubFeatures( imageBuffer, listCascadeToApply, strDebugFilename = "", strDebugWindowName = False, ):
    """
    Apply a cascade to an image, then a cascade to the area found and so one...
    return a list of rectangle in absolute position in the complete image
    """
    timeBegin = time.time();

    if( strDebugWindowName ):
        cv.ShowImage( strDebugWindowName, imageBuffer );
        cv.WaitKey(1);

    image_size = cv.GetSize(imageBuffer);
    print( "INF: haarDetect: image has size %s (%dx%d)" % ( str( image_size ), imageBuffer.width, imageBuffer.height ) );

    # create grayscale version
    grayscale = cv.CreateImage( image_size, cv.IPL_DEPTH_8U, 1 );

    # simple way:
    cv.CvtColor( imageBuffer, grayscale, cv.CV_BGR2GRAY ); # this was crashing

    # create storage
    storage = cv.CreateMemStorage(0);
    # cv.ClearMemStorage(storage)

    # equalize histogram
    cv.EqualizeHist(grayscale, grayscale);

    listLoadedCascade = [] ; # a list of loaded cascade, if needed
    nNumCascade = 0;
    listRectCurrent = [[0,0,imageBuffer.width, imageBuffer.height]]; # the full image
    listRectNext = [];
    while( nNumCascade < len( listCascadeToApply ) ):
        if( nNumCascade >= len(listLoadedCascade) ):
            # load the cascade for that level
            try:
                listLoadedCascade.append( cv.Load( listCascadeToApply[nNumCascade] ) );
            except BaseException, err:
                print( "ERR: haarDetect: haarcascade '%s' not found or ?. (err:%s)" % ( listCascadeToApply[nNumCascade], str(err)) );
                return False;
        for rect in listRectCurrent:
            cv.SetImageROI( grayscale, ( rect[0], rect[1], rect[2], rect[3] ) ); # rect to tuple
            nMinNeighbour = 10+40*nNumCascade;
            nMinNeighbour = 10;
            nMinSizeAnalyse = 30;
            timeAnalyse = time.time();
            objectsFound = cv.HaarDetectObjects( grayscale, listLoadedCascade[nNumCascade], storage, 1.2, nMinNeighbour, cv.CV_HAAR_DO_CANNY_PRUNING, (nMinSizeAnalyse, nMinSizeAnalyse) );
            print( "INF: haarDetect: level %d: analyse takes %.2fs" % (nNumCascade, ( time.time() - timeAnalyse ) ) );

            if objectsFound:
                print( "INF: haarDetect: %d Object(s) detected in rect:%s !" % ( len( objectsFound ), str(rect) ) );
                print( "object detected at %s" % str( objectsFound ) );
                for obj in objectsFound:
                    subRect = obj[0];
                    # subRect = ( subRect[0]+rect[0], subRect[1]+rect[1], subRect[2], subRect[3] ); # is rect local to ROI ?
                    listRectNext.append( [subRect[0], subRect[1], subRect[0]+subRect[2], subRect[1]+subRect[3] ] );
                    #~ cv.Rectangle( imageBuffer, (rect[0], rect[1]), (rect[0]+rect[2], rect[1]+rect[3]), cv.RGB(0, 255, 0), 3, 8, 0);
        # for each rect to analyse - end
        listRectCurrent = arraytools.dup( listRectNext );
        listRectNext = [];
        if( len( listRectCurrent ) == 0 ):
            break; # quick return
        nNumCascade += 1;

    # end for each while cascade

    return listRectCurrent;
# foundSubFeatures - end
if( False ):
    strFilename = "../../../appu_data/images_to_analyse/face_test_crop.jpg";
    aCascadeList = ["/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_alt.xml", "/usr/local/share/OpenCV/haarcascades/haarcascade_mcs_mouth.xml"];
    #aCascadeList = ["/usr/local/share/OpenCV/haarcascades/haarcascade_mcs_mouth.xml"];
    listRect = applyMethodOnFile( strFilename, "foundSubFeatures", extraParams =  [aCascadeList] );
    showImageFromFile( strFilename, listRect );

def launchProcessOnDirectory( strPath, strMethodName ):
    """
    apply a method to files present in a directory
    """
    nCpt = 0;
    timeBegin = time.time();
    listFile = sorted( os.listdir( strPath ) );
    for strFilename in listFile:
        if( os.path.isdir(strPath+strFilename) ):
            continue;
        timeBegin = time.time();
        func = getattr( sys.modules[__name__], strMethodName );
        retVal = func( strPath+strFilename );
        # print( "INF: launchProcessOnDirectory: time Method: %.3fs" % ( time.time() - timeBegin ) );
        nCpt += 1;
    # for - end
    print( "INF: launchProcessOnDirectory: end: %d successfully proceeded file(s) (avg time:%f)\n" % (nCpt, (time.time() - timeBegin)/nCpt ) );
# launchProcessOnDirectory - end
# launchProcessOnDirectory( "/home/likewise-open/ALDEBARAN/amazel/dev/git/appu_applications/facevacs/data_to_learn/good/", "reduceBigger" );

def reduceImageTo( strSrc, strDst, nWidthMax, nHeightMax ):
    """
    If image is wider or higher than max, reduce image, preserving ratio
    """
    imageBuffer = cv.LoadImage( strSrc );
    if( imageBuffer.width > nWidthMax or imageBuffer.height > nHeightMax ):
        nW = nWidthMax
        nH = int( nW * imageBuffer.height / imageBuffer.width );
        if( nH > nHeightMax ):
            nH = nHeightMax;
            nW = int( nH * imageBuffer.width / imageBuffer.height );
            assert( nW <= nWidthMax );
        print( "INF: abcdk.reduceImageTo: %s [%dx%d] => %s [%dx%d]" % (strSrc, imageBuffer.width, imageBuffer.height, strDst, nW, nH ) );
        small_image = cv.CreateImage( (nH, nW), imageBuffer.depth, imageBuffer.nChannels );
        cv.Resize( imageBuffer, small_image, interpolation=cv.CV_INTER_CUBIC );
        cv.SaveImage( strDst, small_image );
# reduceImageTo - end

def getColorValue( strColor ):
    """
    Return a typical color (rgb) related to a name
    - strColor: could be "Red", "red", "R", "r", "Green", ..., "Yellow", ...
    """
    strColor = strColor[0].lower();
    color = (0,0,0);
    if( strColor == "y" ):
        color = (0,255,255);
    else:
        color = ((strColor=="b")*255,(strColor=="g")*255,(strColor=="r")*255);
    #~ print( "strColor: %s => %s" % ( strColor, str(color) ) );
    return color;
# getColorValue - end


def equalizeColorImage( imageBuffer, bEqualiseEachChannelIndependantly = False ):
    """
    Take a rgb image and maximize its contrast
    - bEqualiseEachChannelIndependantly:
        - False: expand it so that at least one channel have maximum value and one have minimum value (it could be the same). colors are preserved
        - True: expand it so that every channel has its maximum range, independantly (resulting color balance could be unnatural, biased, ...)
    Return True if the image has been equalized (or else it doesn't need or can't be)
    """
    nNbrChannel = 3;
    aMin = [255] * 3;
    aMax = [0] * 3;
    for i in range( nNbrChannel ):
        cv.SetImageCOI(  imageBuffer, i+1 ); # COI: 0: all, 1: first channel, ...
        retVal = cv.MinMaxLoc( imageBuffer );
        if( aMin[i] > retVal[0] ):
            aMin[i] = retVal[0];
        if( aMax[i] < retVal[1] ):
            aMax[i] = retVal[1];

    nMin = min( aMin );
    nMax = max( aMax );
    cv.SetImageCOI(  imageBuffer, 0 ); # remove COI

    #~ print( "INF:equalizeColorImage: min: %d, max: %d (channel: %s, %s)" % ( nMin, nMax, str(aMin), str(aMax) ) );

    if( not bEqualiseEachChannelIndependantly ):
        if( nMin <  10 and nMax > 230 ):
            # it's not so bad...
            return False;
    else:
        aWorstMin = max( aMin );
        aWorstMax = min( aMax );
        if( aWorstMin < 10 and aWorstMax > 230 ):
            # even the worst channel's not so bad...
            return False;

    if( nMin == nMax  ):
        # it's far too bad...
        return False;

    if( not bEqualiseEachChannelIndependantly ):
        cv.AddS( imageBuffer, -nMin, imageBuffer );
        rScale = 255. / (nMax - nMin);
        #~ print( "rScale: %f" % rScale );
        # cv.Mul( imageBuffer, None, imageBuffer, scale = rScale ); # complaints
        # imageBuffer.point(lambda i: i * 1.5 ); # doesn't work
        #imageBuffer = imageBuffer * 5; # doesn't work
        neutralImage = cv.CreateImage( cv.GetSize(imageBuffer), 8, nNbrChannel );
        cv.Set( neutralImage, [1]*nNbrChannel );
        cv.Mul( imageBuffer, neutralImage, imageBuffer, scale = rScale );
    else:
        bufferR = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );
        bufferG = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );
        bufferB = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );
        cv.Split( imageBuffer, bufferB, bufferG, bufferR, None );

        neutralImage = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );
        cv.Set( neutralImage, [1]*nNbrChannel );

        cv.AddS( bufferB, -aMin[0], bufferB );
        rScale = 255. / (aMax[0] - aMin[0])
        #~ print( "rScale: %f" % rScale );
        cv.Mul( bufferB, neutralImage, bufferB, scale = rScale );

        cv.AddS( bufferG, -aMin[1], bufferG );
        rScale = 255. / (aMax[1] - aMin[1]);
        #~ print( "rScale: %f" % rScale );
        cv.Mul( bufferG, neutralImage, bufferG, scale = rScale );

        cv.AddS( bufferR, -aMin[2], bufferR );
        rScale = 255. / (aMax[2] - aMin[2]);
        #~ print( "rScale: %f" % rScale );
        cv.Mul( bufferR, neutralImage, bufferR, scale = rScale );

        cv.Merge( bufferB, bufferG, bufferR, None, imageBuffer );
    return True;
# equalizeColorImage - end

def getHotPoint( imageBuffer, bAsBinary = False ):
    """
    compute the average of position of an image (it's the average of every pixel, leveled by its' value)
    return the hot center point position and an idea of its size: (x,y,w,h)  (in image coordinate or [-1,-1,-1,-1] if no hot point found
    - bAsBinary: use every non null pixel as a full pixel
    """
    nSumX = 0;
    nSumY = 0;
    nSumWeightedX = 0;
    nSumWeightedY = 0;
    nSumXX = 0;
    nSumYY = 0;
    nWeightedSum = 0;
    nNbrPixelHit = 0;
    nNbrPixel = imageBuffer.width * imageBuffer.height;
    x = 0;
    y = 0;
    while( y < imageBuffer.height ):
        nVal = imageBuffer[y,x];
        if( nVal > 0 ):
            #~ print( "x: %d, y: %d, val: %d" % (x,y,nVal) );
            if( bAsBinary ):
                nVal = 1;
            nSumX += x;
            nSumY += y;
            nSumWeightedX += nVal*x;
            nSumWeightedY += nVal*y;
            nSumXX += x*x;
            nSumYY += y*y;
            nWeightedSum += nVal;
            nNbrPixelHit += 1;

        x += 1;
        if( x == imageBuffer.width ):
            x = 0;
            y += 1;
    if( nWeightedSum < 1 ):
        return [-1,-1,-1,-1];
    nMedX = nSumX/nNbrPixelHit;
    nMedY = nSumY/nNbrPixelHit;
    nMedXX = nSumXX/nNbrPixelHit;
    nMedYY = nSumYY/nNbrPixelHit;
    nVarianceX = nMedXX-(nMedX*nMedX);
    nVarianceY = nMedYY-(nMedY*nMedY);

    rThreshold = 1400;
    if( nVarianceX > rThreshold or nVarianceY > rThreshold ):
        print( "WRN: abcdk.image.getHotPoint: Too much variance: nVarianceX: %d, nVarianceY: %d" % ( nVarianceX, nVarianceY ) );
        return [-1,-1,-1,-1];

    return [int(nSumWeightedX/nWeightedSum), int(nSumWeightedY/nWeightedSum), nVarianceX/8, nVarianceY/8];
# getHotPoint - end

def getHotPoint_AlternateMethod( imageBuffer, nNbrAreaToDetectMax = 1 ):
    """
    as getHotPoint, but using only opencv primitive: highly fastest !!! (from 500ms to 2ms on a QVGA simple image)
    NB: imageBuffer is altered !!!
    - nNbrAreaToDetectMax: n dev !!!
    return [-1,-1,-1,-1] or a point [centerX, centerY, width, height]
    """
    retValNoHotPoint = [-1,-1,-1,-1];
    # TODO; look if faster using blob ?
    storage = cv.CreateMemStorage(0);
    contours = cv.FindContours( imageBuffer, storage, mode=cv.CV_RETR_LIST, method = cv.CV_CHAIN_APPROX_SIMPLE ); # CV_CHAIN_APPROX_SIMPLE or CV_RETR_EXTERNAL
    if( len( contours ) < 1 ):
        return retValNoHotPoint;
    #~ print( "contour len: %d" % len( contours ) );
    allPointsfromAllInterestingContours = contours[:];
    nNbrContour = 1;
    next = contours.h_next(); # this is crashing naoqi to do that without testing len !
    while( next != None ):
        #~ print( "contour len n: %d" % len( next ) );
        if( len( next ) > 6 ):
            allPointsfromAllInterestingContours.extend( next );
            nNbrContour += 1;
        next = next.h_next();
    #~ print( "allpoints len n: %d" % len( allPointsfromAllInterestingContours ) );
    #~ print( "nNbrContour: %d" % nNbrContour );

    #~ cv.DrawContours( imageBuffer, contours, external_color = (255,255,255), hole_color = (0,255,0), max_level = 10 );
    #~ for pt in allPointsfromAllInterestingContours:
        #~ cv.Circle( imageBuffer, pt, 2, (255,255,0) );

    if( nNbrContour > 2 ):
        print( "WRN: abcdk.image.getHotPoint_AlternateMethod: should be a bad detection: nNbrContour: %d" % nNbrContour );
        # there's should be an error...
        return retValNoHotPoint;
    bb = cv.BoundingRect( allPointsfromAllInterestingContours );
    if( 0 ):
        print( "bb: " + str( bb ) );
        cv.Rectangle( imageBuffer, ( bb[0], bb[1] ), ( bb[0]+bb[2]-1, bb[1]+bb[3]-1 ), (255,0,0) );
    #~ bb = numeric.findBoundingBox( contours );
    #~ cv.Rectangle( imageBuffer, ( bb[0], bb[1] ), ( bb[2], bb[3] ), (255,255,0) );

    return [bb[0]+bb[2]/2,bb[1]+bb[3]/2,bb[2],bb[3]];
# getHotPoint_AlternateMethod - end

def getHotPoints2( imageBuffer, nNbrAreaToDetectMax = 1 ):
    """
    as getHotPoint_AlternateMethod, but it should detect more point
    NB: imageBuffer is altered !!!
    return [] or a list of point [ [centerX, centerY, width, height], ... ]
    """
    retVal = [];
    # TODO; look if faster using blob ?
    storage = cv.CreateMemStorage(0);
    contours = cv.FindContours( imageBuffer, storage, mode=cv.CV_RETR_LIST, method = cv.CV_CHAIN_APPROX_SIMPLE ); # CV_CHAIN_APPROX_SIMPLE or CV_RETR_EXTERNAL
    if( len( contours ) < 1 ):
        return retVal;
    #~ print( "contour len: %d" % len( contours ) );
    allPointsfromAllInterestingContours = contours[:];
    bbs = []; # all bounding boxes
    bbs.append( cv.BoundingRect( allPointsfromAllInterestingContours ) );
    nNbrContour = 1;
    next = contours.h_next(); # this is crashing naoqi to do that without testing len !
    while( next != None ):
        #~ print( "contour len n: %d" % len( next ) );
        if( len( next ) > 3 ): # was 6 (but 3 is interesting too...)
            bbs.append( cv.BoundingRect( next ) );
            nNbrContour += 1;
        next = next.h_next();
    # convert bbs to the right stuffs
    bbs = numeric.simplifyBoundingBoxList( bbs );
    for bb in bbs:
        retVal.append( [bb[0]+bb[2]/2,bb[1]+bb[3]/2,bb[2],bb[3]] );
    print( "INF: abcdk.image.getHotPoints2: hot points detected: %d" % len( retVal ) );
    return retVal;
# getHotPoints2 - end

def extractColoredPixel( imageBuffer, resultBuffer, strColor, bBinary = False ):
    """
    extract pixel that have a specific color, even if not very saturated nor lighten.
    eg for green: 63,115,70 is ok but 110,180,140, or 20,50,20...
    imageBuffer: an bgr 3 channel image (previously allocated)
    resultBuffer: resulting image (one channel image) (previously allocated, with the same size than imageBuffer)
    strColor: color to extract "R" "G" or "B"
    bBinary: does we output all in 0/1 or did we keep a feeling of coloritude on it (255: sure it's the right color, 1: it's unlikely not the good one)
    return the number of pixel of that colour found
    """
    nNbrPixel = imageBuffer.width * imageBuffer.height;
    x = 0;
    y = 0;
    cv.Set( resultBuffer, [0]*3 );
    if( strColor == "R" ):
        nIdxSelect = 2;
        nIdxNot1 = 0;
        nIdxNot2 = 1;
    elif( strColor == "G" ):
        nIdxSelect = 1;
        nIdxNot1 = 0;
        nIdxNot2 = 2;
    else:
        nIdxSelect = 0;
        nIdxNot1 = 1;
        nIdxNot2 = 2;
    while( y < imageBuffer.height ):
        val = imageBuffer[y,x]; # B,G,R
        nAvg = (val[nIdxNot1]  + val[nIdxNot2])/2;
        # 1.65 ... 0.3 was good but 1.95 0.5 is better !
        if( val[nIdxSelect] > 10 ):
            if(

                    ( val[nIdxSelect] > nAvg * 1.95 and abs( val[nIdxNot1] - nAvg ) < nAvg * 0.5 ) # more than x% of the other colors, and other colors are quite the same!
#                or ( val[nIdxSelect] > nAvg * 1.4 and abs( val[nIdxNot1] - nAvg ) < nAvg * 0.1 ) # more than x% of the other colors, and other colors are quite the same! # try for fake image, but can't succeed on green layer!

                or ( val[nIdxSelect] > nAvg * 3. ) # very strong color
            ):
                resultBuffer[y,x] =255; # (255*(val[nIdxSelect]-nAvg))/val[nIdxSelect];

        x += 1;
        if( x == imageBuffer.width ):
            x = 0;
            y += 1;
    # while - end
# extractColoredPixel - end


def findColoredMarks( imageBuffer, strColorTop = "B", strColorBottom = "R", imageBufferForDrawingDebug = None, nReduceDetectionMethodNumberTo = -1, _nDetectionMethod = 0 ):
    """
    find two colored marks vertically aligned. (it couldn't be twice the same color)
    - imageBuffer: image to analyse
    - strColorTop: the top color ("R": Red, "B": Blue, "G": Green)
    - strColorBottom: the bottom color
    - imageBufferForDrawingDebug: image to draw intermediate image computation
    - nReduceDetectionMethodNumberTo: if you don't want alternate longer method, reduce that value to 2, 1, ...
    - _nDetectionMethod: internal, in case of not found, we could test others method
    return [[xTop, yTop],[xBottom, yBottom]] or [[-1,y], [-1, y]] if not found
    """

    kDetectionMethodNbr = 3; # total is 4, but I haven't any pictures working with the last method...
    if( nReduceDetectionMethodNumberTo != -1 ):
        kDetectionMethodNbr = nReduceDetectionMethodNumberTo;
    #~ _nDetectionMethod += 2; #to debug a specific version

    equalizeColorImage( imageBuffer, bEqualiseEachChannelIndependantly = False );

    #~ cv.Threshold( imageBuffer, imageBuffer, 127, 18, cv.CV_THRESH_BINARY );
    #~ cv.SetImageCOI(  imageBuffer, 1 ); # a retester: c'est peut etre plus optimal (non: plein de méthode ne marche pas avec les COI)
    #~ grey = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );
    workT = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 ); # buffer to store image worked about color waited for the top
    workB = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );

    if( True ):
        # removing other channels
        bufferR = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );
        bufferG = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );
        bufferB = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );
        if( _nDetectionMethod == 2 ):
                extractColoredPixel( imageBuffer, workT, strColorTop );
                extractColoredPixel( imageBuffer, workB, strColorBottom );
        else:
            cv.Split( imageBuffer, bufferB, bufferG, bufferR, None ); # a tester et voir aussi pour le COI ?!?
            # possible value for threshold: CV_THRESH_BINARY, CV_THRESH_TOZERO, CV_THRESH_TOZERO_INV, ...
            nLimit = 64;
            if( _nDetectionMethod == 3 ):
                nLimit = 130; # hardest limit (because of too much noise) # for red_green_marks_03 the red part needs 160 to be detected
            if( True ):
                # set bad pixel to zero
                nType = cv.CV_THRESH_TOZERO;
                nReplace = 0;
            else:
                # set good pixel to full
                nType = cv.CV_THRESH_BINARY;
                nReplace = 255;
            cv.Threshold( bufferR, bufferR, nLimit, nReplace, nType );
            cv.Threshold( bufferG, bufferG, nLimit, nReplace, nType );
            cv.Threshold( bufferB, bufferB, nLimit, nReplace,  nType );

            if( strColorTop == "R" ):
                cv.Sub( bufferR, bufferG, workT );
                cv.Sub( workT, bufferB,workT );
            elif( strColorTop == "G" ):
                cv.Sub( bufferG, bufferR, workT );
                cv.Sub( workT, bufferB,workT );
            elif( strColorTop == "B" ):
                cv.Sub( bufferB, bufferR, workT );
                cv.Sub( workT, bufferG,workT );

            if( strColorBottom == "R" ):
                cv.Sub( bufferR, bufferG, workB );
                cv.Sub( workB, bufferB,workB );
            elif( strColorBottom == "G" ):
                cv.Sub( bufferG, bufferR, workB );
                #~ cv.Add( workB, bufferG, workB ); # boost color
                cv.Sub( workB, bufferB,workB );
                #~ cv.Threshold( workB, workB, 120, 255, cv.CV_THRESH_BINARY );
            elif( strColorBottom == "B" ):
                cv.Sub( bufferB, bufferR, workB );
                cv.Sub( workB, bufferG,workB );
        # else _nDetectionMethod != 2 - end
    else:
        # selecting pixels by color (not working fine) (oldies !)
        cv.InRangeS( imageBuffer, (0,0,64), (60,60,255), workR );
        cv.InRangeS( imageBuffer, (64,0,0), (255,60,60), workB );

    # find blobs
    #~ blopParams = cv.SimpleBlobDetector.params();

    if( strColorBottom == "Y" ):
        # TODO: clean way to bypass previous computation
        print( "*"*40)
        #~ anColorRange = [(120,200,200),(200,255,255)]; # yellow post it!
        anColorRange = [(45,180,180),(120,255,255)]; # yellow post it not fluo!
        cv.InRangeS( imageBuffer, anColorRange[0],anColorRange[1], workB );


    if( _nDetectionMethod == 0  ):
        cv.Erode( workT, workT, iterations = 1 ); # with 1 it's better when surrounded by yellow
        cv.Erode( workB, workB, iterations = 1 ); # was 2, but faster with one, so...
    elif( _nDetectionMethod == 1 ):
        # erode more specialized
        if( strColorBottom != "R" ): # don't erode when B is on the bottom
            morphShape = cv.CreateStructuringElementEx( 1, 3, 0, 1, shape=cv.CV_SHAPE_RECT );
            cv.Erode( workB, workB, element = morphShape, iterations = 1 );
        if( strColorTop != "R" ): # don't erode when B
            morphShape = cv.CreateStructuringElementEx( 1, 13, 0, 6, shape=cv.CV_SHAPE_RECT );
            cv.Erode( workT, workT, element = morphShape, iterations = 1 );
    elif( _nDetectionMethod == 2 ):
        # erode harder
        morphShape = cv.CreateStructuringElementEx( 5, 7, 2, 3, shape=cv.CV_SHAPE_RECT );
        cv.Erode( workT, workT, element = morphShape, iterations = 2 );
        cv.Erode( workB, workB, element = morphShape, iterations = 1 );
        pass
    else:
        if( strColorTop != "G" ):
            morphShape = cv.CreateStructuringElementEx( 2, 7, 1, 4, shape=cv.CV_SHAPE_RECT );
        else:
            morphShape = cv.CreateStructuringElementEx( 1, 5, 0, 3, shape=cv.CV_SHAPE_RECT );
        cv.Erode( workT, workT, element = morphShape, iterations = 1 );
        if( strColorBottom != "G" ):
            morphShape = cv.CreateStructuringElementEx( 3, 5, 1, 3, shape=cv.CV_SHAPE_RECT );
        else:
            morphShape = cv.CreateStructuringElementEx( 1, 5, 0, 3, shape=cv.CV_SHAPE_RECT );
            pass
        cv.Erode( workB, workB, element = morphShape, iterations = 1 );
        pass

    if( strColorTop == "R" ):
        cv.Threshold( workT, workT, 92, 255, cv.CV_THRESH_BINARY ); # remove weak red like orange or yellow ...
        pass
    else:
        cv.Threshold( workT, workT, 40, 0, cv.CV_THRESH_TOZERO ); # remove weak point

    if( strColorBottom == "R" ):
        cv.Threshold( workB, workB, 92, 255, cv.CV_THRESH_BINARY ); # remove weak red like orange or yellow ...
    else:
        cv.Threshold( workB, workB, 40, 0, cv.CV_THRESH_TOZERO ); # remove weak point
        pass

    #~ retVal = cv.MinMaxLoc( workR );
    #~ print( "retVal: %s" % str( retVal ) );
    #~ retVal = cv.Norm( workR, None, cv.CV_L2 );
    #~ print( "retVal: %s" % str( retVal ) );
    #~ retVal = cv.Moments( bufferG, binary=True );
    #~ print( "retVal: %s" % str( retVal ) );
    #~ retVal = cv.MinMaxLoc( workR );
    #~ x = retVal[3][0];
    #~ y = retVal[3][1];
    xT, yT, w, h = getHotPoint( workT );

    #~ retVal = cv.MinMaxLoc( workB );
    #~ x = retVal[3][0];
    #~ y = retVal[3][1];
    xB, yB, w, h = getHotPoint( workB );

    if( True ):
        # enable alternate look up
        if( xT == -1 or xB == -1 ):
            if( _nDetectionMethod + 1 < kDetectionMethodNbr ):
                print( "INF: abcdk.image.findColoredMarks: trying with alternate detection method %d" % (_nDetectionMethod+1) );
                return findColoredMarks( imageBuffer, strColorTop = strColorTop, strColorBottom = strColorBottom, imageBufferForDrawingDebug = imageBufferForDrawingDebug, nReduceDetectionMethodNumberTo = nReduceDetectionMethodNumberTo, _nDetectionMethod = _nDetectionMethod+1 );

    if( 1 ):
        # to debug: write results in the image, to see selected pixels
        zeroChannel = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );
        cv.Set( zeroChannel, [0]*1 );
        #~ bufferToDraw = workT;
        #~ cv.Threshold( bufferToDraw, bufferToDraw, 90, 255, cv.CV_THRESH_BINARY ); # highlight some areas
        #~ cv.Threshold( bufferToDraw, bufferToDraw, 40, 255, cv.CV_THRESH_BINARY ); # highlight all areas
        #~ cv.Merge( bufferToDraw, zeroChannel, zeroChannel, None, imageBuffer );
        cv.Merge( zeroChannel, workB, workT, None, imageBuffer );

    colorT = getColorValue( strColorTop );
    colorB = getColorValue( strColorBottom);
    cv.Circle( imageBuffer, (xT, yT), 10, colorT );
    cv.Circle( imageBuffer, (xB, yB), 10, colorB );

    if( yT > yB ):
        # bottom is above top: error!
        xT = xB = -1;
    else:
        if( abs( xB - xT ) > abs( yB-yT ) ):
            # the point are not enough vertical
            xT = xB = -1;

    if( imageBufferForDrawingDebug != None ):
        imageBufferForDrawingDebug = workR;

    return [ [xT,yT], [xB,yB] ];
# findColoredMarks - end

def findColoredMarks_test():
    strPath = "D:/Dev/git/appu_data/images_to_analyse/colored_marks/";
    nCptGood = nCptTotal = nCptBad = 0;
    aRef = [
        # blue and red
        [[120, 65], [122, 106] ],
        [[140, 70], [143, 102] ],
        [[66, 79], [83, 125]],
        [[160, 17], [162,  61]],
        [[160, 17], [162,  61]],

        [[160, 17], [162,  61]],
        [[132, 33], [136,  62]],
        [ [174, 26], [174,  47]],
        [[87, 13], [87,  24] ],
        [[263, 145], [250,  195] ],

        [[208, 103], [205,  132]],
        [[208, 103], [205,  132]],
        [[207, 89], [204,  135]],
        [[147, 10], [151,  30]],
        [[162, 4], [163,  21]],

        # red and green
        [[125,  158], [125, 187]],
        [[107,   20], [107,  30]],
        [[108,   51], [108,  60]],
        [[115,  125], [115, 138]],
        [[365,  126], [369, 219]], # red_green_marks_05_hanovre.jpg

        [[411,  155], [413, 247]],
        [[297,  226], [304, 317]],
        [[391,  123], [392, 216]],
        [[391,  123], [392, 216]], # red_green_marks_09_faked.jpg
        [[391,  123], [392, 216]],
        [[391,  123], [392, 216]],
        [[391,  123], [392, 216]],

        [[108,  124], [111, 154]], # new_green

        [[108,  165], [113, 213]], # red yellow
        [[120,  125], [116, 174]],
        [[178,  148], [173, 191]],
        [[184,  28], [179, 71]],
        [[184,  28], [179, 71]],
        [[184,  27], [183, 63]],
        [[82,  84], [87, 147]],
        [[125,  99], [123, 135]],

        # tester
        [[391,  123], [392, 216]], # red_green_marks_99_tester.png
        [[-1,  124], [-1, -1]],
    ];

    nReduceDetectionMethodNumberTo = -1; # for all type of method
    #~ nReduceDetectionMethodNumberTo = 2; # to limit to first 2

    for strFilename in sorted( os.listdir( strPath ) ):
        #~ if( strFilename != "red_green_marks_05_hanovre.jpg" and strFilename != "red_green_marks_20_tester.png"  ): # work on a specific image
        #~ if( not "faked" in strFilename ): # work on a specific image
        #~ if( not "yellow" in strFilename ):
            #~ nCptTotal += 1;
            #~ continue;
        if( "tester" in strFilename ): # don't analyse this one!
            nCptTotal += 1;
            continue;
        strPathFilename = strPath + strFilename;
        imageBuffer = cv.LoadImage( strPathFilename );
        if( "blue_red" in strPathFilename ):
            # blue_red*
            retVal = findColoredMarks( imageBuffer, nReduceDetectionMethodNumberTo = nReduceDetectionMethodNumberTo );
        elif( "red_green" in strPathFilename ):
            retVal = findColoredMarks( imageBuffer, strColorTop = "R", strColorBottom = "G", nReduceDetectionMethodNumberTo = nReduceDetectionMethodNumberTo );
        elif( "red_yellow" in strPathFilename ):
            retVal = findColoredMarks( imageBuffer, strColorTop = "R", strColorBottom = "Y", nReduceDetectionMethodNumberTo = nReduceDetectionMethodNumberTo );
        print( "%d: %s: %s" % ( nCptTotal, strFilename, retVal ) );
        if( retVal[0][0] != -1 and retVal [1][0] != -1  ):
            print( "DETECTED (ref: %s)" % (aRef[nCptTotal]) );
            bBad = False;
            for j in range( 2 ):
                for i in range( 2 ):
                    nDiff = abs( retVal[j][i] - aRef[nCptTotal][j][i]);
                    if( nDiff > 10 ):
                        print( "FALSE DETECTION (nDiff:%d)" % nDiff );
                        bBad = True;
                        nCptBad += 1;
                        break;
            if( not bBad ):
                print( "GOOD" );
                nCptGood += 1;
        #~ showImage( imageBuffer, rTimeAutoClose = 2. );
        if( nCptTotal >= 35 ): # permit to see a specific image
            showImage( imageBuffer, rTimeAutoClose = 2. );
            pass
        nCptTotal += 1;
    print( "RESULTS: %d/%d (bad:%d)" % (nCptGood, nCptTotal,nCptBad) );
    assert( nCptGood >= 24 ); # current performance !
# findColoredMarks_test() - end


def findColoredInterest( imageBuffer, nType = 0, bDebugAddCircle = False ):
    """
    find a specific colored object in an image so we could track it or ... It ensure the object has a consistance (ie one block).
    return the center, width and height of the bounding box (in absolute image position), and the average color of seen object
    - nType: an int that permits to search for a specific one (so you can cycle between different), cf anColorRange for details
    """
    #~ print( "DBG: image.findColoredInterest: nType: %d" % nType );
    anColorRange = [
        [(0,0,120),(80,90,255)], # red!
        [(120,10,10),(255,130,80)], # blue ball
        [(20,120,20),(150,255,80)], # green ball
        [(20,200,200),(100,255,255)], # yellow ball
        [(180,90,210),(255,210,255)], # pink pig
        [(120,200,200),(200,255,255)], # yellow post it!
        [(250,250,250),(255,255,255)], # pure white

    ];

    #~ [(150,170,150),(200,255,200)], # green salad (bof)
        #~ [(170,20,20),(255,150,150)], # blue flyer


    nType = nType % len( anColorRange );

    work = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );
    cv.InRangeS( imageBuffer, anColorRange[nType][0],anColorRange[nType][1], work );
    #~ morphShape = cv.CreateStructuringElementEx( 9, 9, 4, 4, shape=cv.CV_SHAPE_RECT );
    morphShape = cv.CreateStructuringElementEx( 5, 5, 2, 2, shape=cv.CV_SHAPE_RECT );
    cv.Erode( work,  work, element = morphShape, iterations = 1 );

    #~ timeCompute = time.time();
    #~ x, y, w, h = getHotPoint( work );
    #~ print( "time getHotPoint: %5.2fs" % (time.time() - timeCompute) );

    timeCompute = time.time();
    x, y, w, h = getHotPoint_AlternateMethod( work ); # Alma 13-11-29: removing the [0] , wtf ! (bug #16707)
    #~ print( "time getHotPoint_AlternateMethod: %5.2fs" % (time.time() - timeCompute) );

    avgColor = [(anColorRange[nType][0][0]+anColorRange[nType][1][0])/2,(anColorRange[nType][0][1]+anColorRange[nType][1][1])/2,(anColorRange[nType][0][2]+anColorRange[nType][1][2])/2 ];
    if( bDebugAddCircle ):
        # to debug: write results in the image, to see selected pixels
        #~ cv.Merge( work, work, work, None, imageBuffer );
        cv.Circle( imageBuffer, (x+1, y+1), 10+(w+h)/4, ( 0,0,0 ) ); # shadow for better view
        cv.Circle( imageBuffer, (x, y), 10+(w+h)/4, avgColor );

    return [x, y, w, h, avgColor];
# findColoredInterest - end


def findColoredInterest_test():
    strPath = "C:/work/Dev/git/appu_data/images_to_analyse/colored_interest/";
    nCptGood = nCptTotal = nCptBad = 0;
    aRef = [
        [-1, -1, -1, -10 ], #  none
        [28, 151, 40, 32 ], # red ball
        [250, 192, 45, 39 ], # blue ball
        [200, 140, 32, 28 ], # green ball
        [266, 146, 35, 35 ], # yellow ball


        [142, 135, 49, 63 ], # pink pig
        [230, 212, 56,30 ], # post it
        [71, 223, 99,42 ], # pure white

        [96, 205, 104, 58 ], # red plate
        [20, 211, 45, 45 ], # blue flyer

        [129, 211, 45, 43 ], # alternate green ball trouee lestee
    ];

    for strFilename in sorted( os.listdir( strPath ) ):
        #~ if( strFilename != "8_interest_redplates.png" ): # work on a specific image
            #~ nCptTotal += 1;
            #~ continue;
        strPathFilename = strPath + strFilename;
        imageBuffer = cv.LoadImage( strPathFilename );
        retVal = findColoredInterest( imageBuffer, nType = nCptTotal-1, bDebugAddCircle = True );
        print( "%s: %s" % ( strFilename, retVal ) );
        if( retVal[0] != -1 ):
            print( "DETECTED" );
            bBad = False;
            for i in range( 2 ):
                if( abs( retVal[i] - aRef[nCptTotal][i]) > 16 ):
                    print( "FALSE DETECTION" );
                    bBad = True;
                    nCptBad += 1;
                    break;
            if( not bBad ):
                print( "GOOD" );
                nCptGood += 1;
        else:
            if( aRef[nCptTotal][0] == -1 ):
                print( "NOT DETECTED but NOTHING !!!" );
                nCptGood = True;
        showImage( imageBuffer, rTimeAutoClose = 1. );
        if( nCptTotal == 9 ): # permit to see a specific image
            showImage( imageBuffer, rTimeAutoClose = 1. );
            pass
        nCptTotal += 1;
    print( "RESULTS: %d/%d (bad:%d)" % (nCptGood, nCptTotal,nCptBad) );
    assert( nCptGood >= 9 ); # current performance ! # Alma 13-11-29: no today it's 9/11 and not 11 !?!
# findColoredInterest_test() - end


def stereo_findNearestPoint( imageBufferL, imageBufferR ):
    """
    Analyse two stereo image and return the nearest point
    cf:
    http://blog.martinperis.com/2011/08/opencv-stereo-matching.html
    http://docs.opencv.org/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html
    """

    gray_l = cv.CreateImage( cv.GetSize(imageBufferL), cv.IPL_DEPTH_8U, 1 );
    gray_r = cv.CreateImage( cv.GetSize(imageBufferL), cv.IPL_DEPTH_8U, 1 );
    cv.CvtColor( imageBufferL, gray_l, cv.CV_BGR2GRAY );
    cv.CvtColor( imageBufferR, gray_r, cv.CV_BGR2GRAY );
    work = cv.CreateImage( cv.GetSize(imageBufferL), cv.IPL_DEPTH_16S, 1 );
    params = cv.CreateStereoBMState()
    params.SADWindowSize = 19
    params.preFilterType = 1
    params.preFilterSize = 5
    params.preFilterCap = 61
    params.minDisparity = -39
    params.numberOfDisparities = 112
    params.textureThreshold = 507
    params.uniquenessRatio= 0
    params.speckleRange = 8
    params.speckleWindowSize = 0
    cv.FindStereoCorrespondenceBM(gray_l, gray_r, work, params );
    #~ disparity_visual = cv.CreateMat(c, r, cv.CV_8U)
    #~ cv.Normalize(disparity, disparity_visual, 0, 255, cv.CV_MINMAX)
    #~ disparity_visual = numpy.array(disparity_visual)
    #~ print dir(work);
    #~ for j in range( 240 ):
        #~ for i in range( 320 ):
            #~ if( work[j,i] != -16 ):
                #~ print( "%d,%d: %d" % (j,i,work[j,i] ) );
    i = 231;
    j = 216;
    print( "%d,%d: %d" % (j,i,work[j,i] ) );
    if( 1 ):
        cv.ConvertScale(work, gray_l, 1./16, 0);
        #~ for i in range( 32 ):
            #~ print( "%d" % gray_l[10,i] );
        cv.Merge( gray_l, gray_l, gray_l, None, imageBufferL );
    i = 231;
    j = 216;
    print( "%d,%d: %d" % (j,i,gray_l[j,i] ) );
    return [-1,-1,-1,-1];
# stereo_findNearestPoint - end

def stereo_findNearestPoint_test():
    strPath = "D:/Dev/git/appu_data/images_to_analyse/stereo/";
    nCptGood = nCptTotal = nCptBad = 0;
    aRef = [
        [-1, -1, -1, -10 ], #  none
        [-1, -1, -1, -10 ], #  none
    ];

    for strFilename in sorted( os.listdir( strPath ) ):
        if( "_r." in strFilename ): # read only left
            continue;
        strPathFilename = strPath + strFilename;
        imageBuffer = cv.LoadImage( strPathFilename );
        imageBuffer2 = cv.LoadImage( strPathFilename.replace( "_l.", "_r." ) );
        retVal = stereo_findNearestPoint( imageBuffer, imageBuffer2 );
        print( "%s: %s" % ( strFilename, retVal ) );
        if( retVal[0] != -1 ):
            print( "DETECTED" );
            bBad = False;
            for i in range( 2 ):
                if( abs( retVal[i] - aRef[nCptTotal][i]) > 16 ):
                    print( "FALSE DETECTION" );
                    bBad = True;
                    nCptBad += 1;
                    break;
            if( not bBad ):
                print( "GOOD" );
                nCptGood += 1;
        else:
            if( aRef[nCptTotal][0] == -1 ):
                print( "NOT DETECTED but NOTHING !!!" );
                nCptGood = True;
        showImage( imageBuffer, rTimeAutoClose = 1. );
        if( nCptTotal == 9 ): # permit to see a specific image
            showImage( imageBuffer, rTimeAutoClose = 1. );
            pass
        nCptTotal += 1;
    print( "RESULTS: %d/%d (bad:%d)" % (nCptGood, nCptTotal,nCptBad) );
    assert( nCptGood >= 11 ); # current performance !
# findColoredInterest_test() - end

def matchPoint( listDesc1, listDesc2, rThreshold = 0.6 ):
    """
    find matching point in two descriptor list
    return a pair
    """
def filter_matches(kp1, kp2, matches, ratio = 0.75):
    mkp1, mkp2 = [], []
    for m in matches:
        if len(m) == 2 and m[0].distance < m[1].distance * ratio:
            m = m[0]
            mkp1.append( kp1[m.queryIdx] )
            mkp2.append( kp2[m.trainIdx] )
    p1 = numpy.float32([kp.pt for kp in mkp1])
    p2 = numpy.float32([kp.pt for kp in mkp2])
    kp_pairs = zip(mkp1, mkp2)
    return p1, p2, kp_pairs
# matchPoint - end

def computeHomotethy(kp1, kp2, matched ):
    matched_p1 = numpy.array([kp1[i].pt for i, j in matched])
    matched_p2 = numpy.array([kp2[j].pt for i, j in matched])
    print( matched_p1 );
    print( matched_p2 );
    H, status = cv2.findHomography(matched_p1, matched_p2, cv2.RANSAC, 5.0)
    print '%d / %d  inliers/matched' % (numpy.sum(status), len(status))

    return (matched_p1, matched_p2, status, H);
# computeHomotethy - end

def generateMatchedPointImage(win, img1, img2, kp_pairs, status = None, H = None):
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    vis = numpy.zeros((max(h1, h2), w1+w2), numpy.uint8)
    vis[:h1, :w1] = img1
    vis[:h2, w1:w1+w2] = img2
    vis = cv2.cvtColor(vis, cv2.COLOR_GRAY2BGR)

    if H is not None:
        corners = numpy.float32([[0, 0], [w1, 0], [w1, h1], [0, h1]])
        corners = numpy.int32( cv2.perspectiveTransform(corners.reshape(1, -1, 2), H).reshape(-1, 2) + (w1, 0) )
        cv2.polylines(vis, [corners], True, (255, 255, 255))

    if status is None:
        status = numpy.ones(len(kp_pairs), numpy.bool_)
    p1 = numpy.int32([kpp[0].pt for kpp in kp_pairs])
    p2 = numpy.int32([kpp[1].pt for kpp in kp_pairs]) + (w1, 0)

    green = (0, 255, 0)
    red = (0, 0, 255)
    white = (255, 255, 255)
    kp_color = (51, 103, 236)
    for (x1, y1), (x2, y2), inlier in zip(p1, p2, status):
        if inlier:
            col = green
            cv2.circle(vis, (x1, y1), 2, col, -1)
            cv2.circle(vis, (x2, y2), 2, col, -1)
        else:
            col = red
            r = 2
            thickness = 3
            cv2.line(vis, (x1-r, y1-r), (x1+r, y1+r), col, thickness)
            cv2.line(vis, (x1-r, y1+r), (x1+r, y1-r), col, thickness)
            cv2.line(vis, (x2-r, y2-r), (x2+r, y2+r), col, thickness)
            cv2.line(vis, (x2-r, y2+r), (x2+r, y2-r), col, thickness)
    vis0 = vis.copy()
    for (x1, y1), (x2, y2), inlier in zip(p1, p2, status):
        if inlier:
            cv2.line(vis, (x1, y1), (x2, y2), green)

    cv2.imshow(win, vis)
    def onmouse(event, x, y, flags, param):
        cur_vis = vis
        if flags & cv2.EVENT_FLAG_LBUTTON:
            cur_vis = vis0.copy()
            r = 8
            #~ print( p1 - (x, y) );
            m = (numeric.anorm(p1 - (x, y)) < r) | (numeric.anorm(p2 - (x, y)) < r)
            idxs = numpy.where(m)[0]
            kp1s, kp2s = [], []
            for i in idxs:
                 (x1, y1), (x2, y2) = p1[i], p2[i]
                 col = (red, green)[status[i]]
                 cv2.line(cur_vis, (x1, y1), (x2, y2), col)
                 kp1, kp2 = kp_pairs[i]
                 kp1s.append(kp1)
                 kp2s.append(kp2)
            cur_vis = cv2.drawKeypoints(cur_vis, kp1s, flags=4, color=kp_color)
            cur_vis[:,w1:] = cv2.drawKeypoints(cur_vis[:,w1:], kp2s, flags=4, color=kp_color)

        cv2.imshow(win, cur_vis)
    cv2.setMouseCallback(win, onmouse)
    return vis
# drawMatchedPoint - end

def filter_matches(kp1, kp2, matches, ratio = 0.75):
    mkp1, mkp2 = [], []
    for m in matches:
        if len(m) == 2 and m[0].distance < m[1].distance * ratio:
            m = m[0]
            mkp1.append( kp1[m.queryIdx] )
            mkp2.append( kp2[m.trainIdx] )
    p1 = numpy.float32([kp.pt for kp in mkp1])
    p2 = numpy.float32([kp.pt for kp in mkp2])
    kp_pairs = zip(mkp1, mkp2)
    return p1, p2, kp_pairs
# filter_matches - end

def compareObject( imageBufferRef, imageBuffer, bDrawDebug = False ):
    """
    try to recognize object blablab todo
    """

    #~ equalizeColorImage( imageBuffer, bEqualiseEachChannelIndependantly = False );
    import cv2
    print cv2.__version__;
    print cv2.__package__
    print cv2.__name__
    print cv2.__file__
    print cv.__file__

    FLANN_INDEX_KDTREE = 1  # bug: flann enums are missing
    FLANN_INDEX_LSH    = 6

    if( True ):
        detector = cv2.SURF(800)
        norm = cv2.NORM_L2
    if( True ):
        detector = cv2.ORB(400)
        norm = cv2.NORM_HAMMING

    if False:
        if norm == cv2.NORM_L2:
            flann_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        else:
            flann_params= dict(algorithm = FLANN_INDEX_LSH,
                               table_number = 6, # 12
                               key_size = 12,     # 20
                               multi_probe_level = 1) #2
        matcher = cv2.FlannBasedMatcher(flann_params, {})  # bug : need to pass empty dict (#1329)
    else:
        matcher = cv2.BFMatcher(norm)

    timeBegin = time.time();
    kp1, desc1 = detector.detectAndCompute(imageBufferRef, None)
    kp2, desc2 = detector.detectAndCompute(imageBuffer, None)
    print 'imgref: %d features, img: %d features' % (len(kp1), len(kp2))

    raw_matches = matcher.knnMatch(desc1, trainDescriptors = desc2, k = 2) #2
    p1, p2, kp_pairs = filter_matches(kp1, kp2, raw_matches)
    if len(p1) >= 4:
        H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
        print '%d / %d  inliers/matched' % (numpy.sum(status), len(status))
    else:
        H, status = None, None
        print '%d matches found, not enough for homography estimation' % len(p1)

    rDuration = time.time() - timeBegin;
    print( "Duration: %5.2fs" % rDuration );
    if( bDrawDebug ):
        imageToDraw = generateMatchedPointImage('compareObject', imageBufferRef, imageBuffer, kp_pairs, status, H)
    cv2.waitKey();
    # TODO: repartir du bon exemple C:\opencv\samples\python2\find_obj.py
# compareObject - end

def compareObject_test():
    strPath = "D:/Dev/git/appu_data/images_to_analyse/object_recognition/";
    nCptGood = nCptTotal = nCptBad = 0;
    strFilenameRef = strPath + "003_zanimo_ref_crop.png";
    strFilename = strPath + "003_zanimo_01.png";

    strPath = "c:/opencv/samples/python2/";
    strFilenameRef = strPath + '../c/box.png'
    strFilename = strPath + '../c/box_in_scene.png'
    assert( os.path.exists( strFilenameRef ) );
    assert( os.path.exists( strFilename ) );
    imageBufferRef = cv2.imread( strFilenameRef ); # cv.CV_LOAD_IMAGE_GRAYSCALE doestn't seem to work anymore
    imageBuffer = cv2.imread( strFilename );
    #~ compareObject( imageBufferRef, imageBuffer );

    imageBufferRefGrey = cv2.cvtColor(imageBufferRef, cv2.COLOR_BGR2GRAY);
    imageBufferGrey = cv2.cvtColor(imageBuffer, cv2.COLOR_BGR2GRAY);
    compareObject( imageBufferRefGrey, imageBufferGrey );
# compareObject_test() - end

def findColoredMarks2( imageBuffer, strColor = "R", limitToRangeX = None, imageBufferForDrawingDebug = None, bSortFromCenter = True ):
    """
    find one or some colored marks.
    - imageBuffer: image to analyse
    - strColor: the color to find ("R": Red, "B": Blue, "G": Green,...)
    - limitToRangeX: limit to a X range.eg: (200,300): analyse mark only in x in [200,300]
    - imageBufferForDrawingDebug: image to draw intermediate image computation
    - bSortFromCenter: if set, detected are from center, else is from left to right (then top to bottom)
    return [detected_mark1,detected_mark2], with for each detected mark: [[xCenter, yCenter,width, height]])
            or [] if not found
    """
    #~ equalizeColorImage( imageBuffer, bEqualiseEachChannelIndependantly = False );

    if( limitToRangeX != None ):
        aRoi = (limitToRangeX[0],0,limitToRangeX[1]-limitToRangeX[0],imageBuffer.height);
        cv.SetImageROI( imageBuffer, aRoi );
        print( "WRN: abcdk.image.findColoredMarks2: reduced to ROI: %s" % str(cv.GetImageROI( imageBuffer )) );
    work = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 ); # buffer to store image worked about color waited for the top
    workCIE = cv.CreateImage( cv.GetSize(imageBuffer), 8, 3 );
    cv.CvtColor(imageBuffer, workCIE, cv2.COLOR_BGR2LAB);
    #~ print( "DBG: abcdk.image.findColoredMarks2: workCIE size : %s" % str(cv.GetSize( workCIE )) );
    #~ print( "DBG: abcdk.image.findColoredMarks2: workCIE ROI : %s" % str(cv.GetImageROI( workCIE )) );
    #~ cv.SaveImage( "d:\\temp\\%.3f.png" % time.time(), workCIE );
    if( 0 ):
        #~ apt = [[208,96], [212,157]]; # red and green point
        #~ apt = [[213, 35], [219, 98] ]
        apt = [[139, 93], [132, 148] ]
        for pt in apt:
            print( "bgr: %s" % str(imageBuffer[pt[1],pt[0]]) );
            print( "cie: %s" % str(workCIE[pt[1],pt[0]]) );


    # on two image (bw balanced, and extreme)
        #~ red:
            #~ bgr: (10.0, 9.0, 86.0)
            #~ cie: (42.0, 162.0, 150.0)
            #~ and
            #~ bgr: (89.0, 51.0, 71.0) (wb 120)
            #~ cie: (64.0, 145.0, 109.0)
            #~ and
            #~ bgr: (23.0, 29.0, 103.0) (wb -36)
            #~ cie: (59.0, 161.0, 151.0)

            # cie: 168, 161, 181 (other taken)

        #~ green:
            #~ bgr: (14.0, 74.0, 12.0)
            #~ cie: (68.0, 96.0, 157.0)
            #~ and
            #~ bgr: (78.0, 117.0, 24.0) (wb 120)
            #~ cie: (111.0, 92.0, 142.0)
            #~ and
            #~ bgr: (17.0, 86.0, 18.0) (wb -36)
            #~ cie: (80.0, 93.0, 160.0)

    if( strColor == "R" ):
        #~ aCenter = (0,162,150);
        #~ rRange1 = 18;
        #~ rRange2 = 41;
        # using medium from extrem wb:
        #aCenter = (20,154,130);
        aCenter = (20,162,140);
        rRange1 = 9+4+7;
        rRange2 = 21+5+2+0;  # +27 for enlarging color case (405_red_green_object__and_intrus_hard.png) (but we detect too much with that!)
        # using medium from extrem wb and specious case
        #~ aCenter = (0,154,145);
        #~ rRange1 = 9;
        #~ rRange2 = 36;
    elif( strColor == "G" ):
        #~ aCenter = (0,96,157);
        #~ rRange1 = 5;
        #~ rRange2 = 20;
        # using medium from extrem wb:
        aCenter = (20,94,151);
        rRange1 = 2+5+1;    # +1 for enlarging color case (405_red_green_object__and_intrus_hard.png)
        rRange2 = 9+7+15;   # +15 for enlarging color case (405_red_green_object__and_intrus_hard.png)
    elif( strColor == "B" ):
        aCenter = (20,122,81);
        rRange1 = 9+10;
        rRange2 = 19+12;

    aRange = [(aCenter[0],aCenter[1]-rRange1,aCenter[2]-rRange2), (255,aCenter[1]+rRange1,aCenter[2]+rRange2)];
    cv.InRangeS( workCIE, aRange[0], aRange[1], work );
    #~ cv.Erode( work, work, iterations = 1 );
    morphShape = cv.CreateStructuringElementEx( 1, 3, 0, 1, shape=cv.CV_SHAPE_RECT );
    cv.Erode( work, work, element = morphShape, iterations = 1 );

    if( imageBufferForDrawingDebug != None ):
        #~ cv.Merge( work, work, work, None, imageBufferForDrawingDebug );
        pass
    pts = getHotPoints2( work ); # WRN: getHotPoints2 will destruct work !!!
    if( imageBufferForDrawingDebug != None ):
        colorDebug = getColorValue( strColor );
        for pt in pts:
            cv.Rectangle(imageBufferForDrawingDebug, (pt[0]-pt[2]/2,pt[1]-pt[3]/2),(pt[0]+pt[2]/2,pt[1]+pt[3]/2), colorDebug );

    if( limitToRangeX != None ):
        for i in range( len(pts) ):
            pts[i][0] += limitToRangeX[0];

    if( bSortFromCenter ):
        center = (imageBuffer.width/2,imageBuffer.height/2 );
        pts.sort( key=lambda a:numeric.dist2D_squared(a,center) );
        return pts;
    return sorted(pts); # left to right
# findColoredMarks2 - end

def findTwoColoredMarks2( imageBuffer, strColorTop = "R", strColorBottom = "G", limitToRangeX = None, imageBufferForDrawingDebug = None ):
    """
    find one colored marks.
    - imageBuffer: image to analyse
    - strColorTop: the top color ("R": Red, "B": Blue, "G": Green,...)
    - strColorBottom: the bottom color
    - limitToRangeX: limit to a X range.eg: (200,300): analyse mark only in x in [200,300]
    - imageBufferForDrawingDebug: image to draw intermediate image computation
    return [[xTop, yTop],[xBottom, yBottom]] or [[-1,y], [-1, y]] if not found
    """
    notDetected = [[-1,0], [-1, 0]];

    #~ imageBufferMat = cv.CreateMat( imageBuffer.width, imageBuffer.height, cv.CV_8UC1 );
    aTop = findColoredMarks2( imageBuffer, strColorTop, limitToRangeX = limitToRangeX, imageBufferForDrawingDebug = imageBufferForDrawingDebug );
    aBottom = findColoredMarks2( imageBuffer, strColorBottom, limitToRangeX = limitToRangeX, imageBufferForDrawingDebug = imageBufferForDrawingDebug );

    if( aBottom == [] or aTop == [] ):
        return notDetected;
    #~ print( "aTop: %s" % aTop );
    xT = aTop[0][0];
    yT = aTop[0][1];
    xB = aBottom[0][0];
    yB = aBottom[0][1];

    # geometrical check
    nTry = 0;
    nNbrTry = 2;
    xB2 = xB;
    yB2 = yB;
    xT2 = xT;
    yT2 = yT;
    while( True and ( xB2 == -1 or xT2 == -1 or abs( xB2 - xT2 ) > abs( yB2-yT2 ) or yT2 > yB2 ) and nTry < nNbrTry and limitToRangeX == None ):
        if( yT2 > yB2 ):
            # bottom is above top: error!
            print( "INF: abcdk.image.findColoredMarks2: marks are upside down %d,%d,%d,%d - trying in sub image" % (xT, yT, xB, yB) );
        else:
            # the point are not enough vertical
            print( "INF: current match is: %d,%d,%d,%d, trying in sub image" % (xT, yT, xB, yB) );

        # let's try to cut the image in two part, so that we could find the good stuffs even if there's two on the screen
        xB2 = xB;
        yB2 = yB;
        xT2 = xT;
        yT2 = yT;
        rRange = 14;
        if(  nTry == 0 ):
            # keep bottom:
            aRangeX = (xB-rRange, xB+rRange);
            aRangeX = (max(0,aRangeX[0]), min(imageBuffer.width-1, aRangeX[1]) );
            aTop = findColoredMarks2( imageBuffer, strColorTop, limitToRangeX = aRangeX );
            if( aTop != [] ):
                xT2,yT2, w, h = aTop[0];
                print( "INF: trying to reduce to a smaller image part: keep bottom: x=%s => top: %d,%d,%d,%d (all areas are: %s)" % (aRangeX,xT2, yT2,w,h, str(aTop)) );
            else:
                print( "INF: trying to reduce to a smaller image part: keep bottom: x=%s => not detected" % (str(aRangeX)) );
        elif(  nTry == 1 ):
            # keep top:
            aRangeX = (xT-rRange, xT+rRange);
            aRangeX = (max(0,aRangeX[0]), min(imageBuffer.width-1, aRangeX[1]) );
            aBottom = findColoredMarks2( imageBuffer, strColorBottom, limitToRangeX = aRangeX );
            if( aBottom != [] ):
                xB2,yB2, w, h = aBottom[0];
                print( "INF: trying to reduce to a smaller image part: keep top: x=%s => bottom: %d,%d,%d,%d (all areas are: %s)" % (aRangeX, xB2, yB2,w,h, str(aBottom)) );
            else:
                print( "INF: trying to reduce to a smaller image part: keep top: x=%s => not detected" % (str(aRangeX)) );
        nTry += 1;
    # while - end
    if( abs( xB2 - xT2 ) > abs( yB2-yT2 ) or yT2 > yB2 ):
        xT = xB = -1;
        print( "INF: abcdk.image.findColoredMarks2: marks are not enough vertical (or many marks)" );
    elif nTry > 0:
        # we find it in sub image
        xB = xB2;
        yB = yB2;
        xT = xT2;
        yT = yT2;


    cv.ResetImageROI( imageBuffer );
    if( imageBufferForDrawingDebug ):
        colorT = getColorValue( strColorTop );
        colorB = getColorValue( strColorBottom);
        cv.Circle( imageBufferForDrawingDebug, (xT, yT), 10, colorT );
        cv.Circle( imageBufferForDrawingDebug, (xB, yB), 10, colorB );

    if( limitToRangeX != None ):
        xT += limitToRangeX[0];
        xB += limitToRangeX[0];

    return [ [xT,yT], [xB,yB] ];

# findTwoColoredMarks2 - end


def findColoredMarks2_test():
    strPath = "D:/Dev/git/appu_data/images_to_analyse/color_detection/";
    nCptGood = nCptTotal = nCptBad = 0;
    aRef = [
        # red-green
        [[208, 96], [213, 157] ], # 100
        [[110, 101], [98, 164] ],
        [[213, 35], [219, 98] ],
        [[136, 96], [129, 167] ],
        [[139, 93], [132, 148] ], # 104
        [[266, 61], [279, 114] ],
        [[94, 108], [82, 164] ],
        [[167, 58], [165, 78] ],

        [[139, 108], [78, 100] ], # 300: many red
        [[140, 152], [101, 124] ],

        [[78, 100], [72, 163] ], # 400 intrus
        [[129, 99], [140, 152] ],
        [[129, 99], [140, 152] ],  # many
        [[114, 118], [105, 140] ], # hard

        [[69, 126], [63, 162] ], # 500
        [[185, 95], [175, 136] ],
        [[78, 132], [80, 164] ],
        [[134, 96], [135, 119] ],
        [[145, 84], [144, 108] ],

        [[-1, 118], [-1, 140] ], # 800 nothing


    ];

    nReduceDetectionMethodNumberTo = -1; # for all type of method
    #~ nReduceDetectionMethodNumberTo = 2; # to limit to first 2

    for strFilename in sorted( os.listdir( strPath ) ):
        #~ if( "50" in strFilename ): # work on a specific image
        #~ if( not "many_red" in strFilename ):
            #~ nCptTotal += 1;
            #~ continue;
        if( "tester" in strFilename ): # don't analyse this one!
            nCptTotal += 1;
            continue;
        strPathFilename = strPath + strFilename;
        if( not os.path.isfile( strPathFilename ) ):
            continue;
        print( "TEST --- %d: %s: " % (nCptTotal, strFilename) );
        imageBuffer = cv.LoadImage( strPathFilename );
        bAlternateRetFormat = False;
        if( "red_green" in strPathFilename ):
            retVal = findTwoColoredMarks2( imageBuffer, "R", "G", imageBufferForDrawingDebug = imageBuffer );
            #~ retVal = findColoredMarks2( imageBuffer, "R", imageBufferForDrawingDebug = imageBuffer );
            #~ bAlternateRetFormat = True;

        elif( "green_red" in strPathFilename ):
            retVal = findTwoColoredMarks2( imageBuffer, "G", "R", imageBufferForDrawingDebug = imageBuffer );
        elif( "blue_red" in strPathFilename ):
            retVal = findTwoColoredMarks2( imageBuffer, "B", "R", imageBufferForDrawingDebug = imageBuffer );
            #~ retVal = findColoredMarks2( imageBuffer, "R", imageBufferForDrawingDebug = imageBuffer );
            #~ bAlternateRetFormat = True;

        elif( "many_red" in strPathFilename ):
            retVal = findColoredMarks2( imageBuffer, "R", imageBufferForDrawingDebug = imageBuffer );
            bAlternateRetFormat = True;
        else:
            raise Exception("not handled");
        if( bAlternateRetFormat ):
            if( len( retVal ) < 2 ):
                print( "Not enough detected marks for automatic check: retVal: %s" % str(retVal) );
                retVal = [ [-1,-1],[-1,-1] ];
            else:
                retVal = [  [ retVal[0][0],retVal[0][1]],[retVal[1][0],retVal[1][1]]  ];
        print( "TEST RESULTS --- %d: %s: %s" % ( nCptTotal, strFilename, retVal ) );
        strOut = "not detected";
        if( retVal[0][0] != -1 and retVal [1][0] != -1  ):
            strOut = "DETECTED (ref: %s)" % (aRef[nCptTotal]);
            bBad = False;
            for j in range( 2 ):
                for i in range( 2 ):
                    nDiff = abs( retVal[j][i] - aRef[nCptTotal][j][i]);
                    if( nDiff > 6 ):
                        strOut = "FALSE DETECTION (nDiff:%d)" % nDiff;
                        bBad = True;
                        nCptBad += 1;
                        break;
            if( not bBad ):
                strOut = "GOOD";
                nCptGood += 1;
        elif( aRef[nCptTotal][0][0] == -1 ):
            strOut = "NOT DETECTED BUT NOTHING TO DETECT => GOOD";
            nCptGood += 1;
        print strOut;
        if( strOut != "GOOD" ):
            showImage( imageBuffer, rTimeAutoClose = 0.3, strWindowName = strOut );
        if( nCptTotal >= 20 ): # permit to see a specific image
            showImage( imageBuffer, rTimeAutoClose = 2., strWindowName = strOut );
            pass
        nCptTotal += 1;
    print( "RESULTS: %d/%d (bad:%d)" % (nCptGood, nCptTotal,nCptBad) );
    assert( nCptGood >= 18 ); # current performance !
# findColoredMarks2_test() - end

def findText( imageBuffer, imageBufferForDrawingDebug =False ):
    """
    return find text as a matrix of text:
    "
    LOVE IS
    ALL
    "=>
    [
        ["LOVE", "IS"],
        ["ALL"],
    ]
    or [] if nothing detected

    """

    currentRoi = cv.GetImageROI( imageBuffer );
    workSize = (currentRoi[2], currentRoi[3]);
    print( "workSize: %s" % str( workSize ) );
    cannyImg = cv.CreateImage( workSize, cv.IPL_DEPTH_8U, imageBuffer.nChannels );
    rCannyThresh1 = 140;
    rCannyThresh2 = 80;
    cv.Canny( imageBuffer, cannyImg, rCannyThresh1,  rCannyThresh2)
    storage = cv.CreateMemStorage(0);
    contours = cv.FindContours( cannyImg, storage, mode = cv.CV_RETR_CCOMP, method = cv.CV_CHAIN_APPROX_SIMPLE );
    #~ , storage, mode=cv.CV_RETR_LIST, method = cv.CV_CHAIN_APPROX_SIMPLE );
    cv.DrawContours( imageBuffer, contours, external_color = (255,255,255), hole_color = (0,255,0), max_level = 10 );


    rect = [0,0,10,10];
    if( imageBufferForDrawingDebug ):
        cv.Rectangle( imageBuffer, (rect[0], rect[1]), (rect[0]+rect[2], rect[1]+rect[3]), cv.RGB(0, 255, 0), 3, 8, 0);

    return [];
# findText - end

def findText_test():
    strPath = "D:/Dev/git/appu_data/images_to_analyse/ocr/";
    nCptGood = nCptTotal = nCptBad = 0;

    for strFilename in sorted( os.listdir( strPath ) ):
        strPathFilename = strPath + strFilename;
        if( not "picture_2012_06_02-16h18m27s822467ms__EXIT_SALON_BUREAU_CHOCOLATE.jpg" in strFilename ):
            continue;
        if( not os.path.isfile( strPathFilename ) ):
            continue;
        if( nCptTotal > 3 ):
            return;
        print( "TEST --- %d: %s: " % (nCptTotal, strFilename) );
        imageBuffer = cv.LoadImage( strPathFilename, cv.CV_LOAD_IMAGE_GRAYSCALE );
        if( True ):
            retVal = findText( imageBuffer, imageBufferForDrawingDebug = imageBuffer );
        else:
            raise Exception("not handled");
        print( "TEST RESULTS --- %d: %s: %s" % ( nCptTotal, strFilename, retVal ) );
        aRef = strFilename.replace(".jpg", "").split( "__" )[1].split("_");
        print( "aRef: %s" % str( aRef ) );
        strOut = "not detected";
        if( retVal != [] ):
            strOut = "DETECTED (ref: %s)" % (aRef[nCptTotal]);
            for strText in aRef:
                if strText in retVal:
                    strOut = "GOOD";
                    nCptGood += 1;
                    break;
            else:
                nCptBad += 1;
        print strOut;
        if( strOut != "GOOD" ):
            showImage( imageBuffer, rTimeAutoClose = 0.3, strWindowName = strOut );
        if( nCptTotal >= 0 ): # permit to see a specific image
            showImage( imageBuffer, rTimeAutoClose = 2., strWindowName = strOut );
            pass
        nCptTotal += 1;
    print( "RESULTS: %d/%d (bad:%d)" % (nCptGood, nCptTotal,nCptBad) );
    assert( nCptGood >= 18 ); # current performance !
# findText_test() - end


def findRect( imageBuffer, colorBorder ):
    """
    Find an outlining rectangle in an area, return its 4 squares or None NDEV  !!!
    """
    print( "INF: image.findRect: imageBuffer shape: w: %d, h: %d" % ( imageBuffer.shape[1], imageBuffer.shape[0] ) );
    lines = cv2.HoughLinesP( imageBuffer, 1, cv.CV_PI/180, 20, 20, 10 );
    #~ print( "INF: image.findRect: lines: %s" % lines );


    # NDEV  !!! # TODO

    return lines;
# findRect - end

def findSquaredLogo( imageBufferRef, imageBufferForDrawingDebug = None ):
    """
    return a list of found logo: (top left, top right, bottomleft, bottomright) for each or []

    takes around 350ms-600ms in 4VGA on NAO v4 (Atom)
    """
    width = imageBufferRef.shape[1];
    height = imageBufferRef.shape[0];
    nNbrChannels = imageBufferRef.shape[2];

    print( "INF: abcdk.image.findSquaredLogo: imput: %dx%d %d channel(s)" % (width, height, nNbrChannels) );

    if( imageBufferForDrawingDebug != None ):
        imageBufferForDrawingDebug = imageBufferRef.copy();
        #~ colorT = getColorValue( strColorTop );
        #~ colorB = getColorValue( strColorBottom);
        #~ cv.Circle( imageBufferForDrawingDebug, (xT, yT), 10, colorT );
        #~ cv.Circle( imageBufferForDrawingDebug, (xB, yB), 10, colorB );
        pass

    if( nNbrChannels == 3 ):
        bwImg = cv2.cvtColor( imageBufferRef, cv2.COLOR_BGR2GRAY );
    else:
        assert( "ERR: abcdk.image.findSquaredLogo: input needs to be in 3-channel rgb (current channel nbr is: %d)" %  nNbrChannels );
        bwImg = cv2.copy( imageBufferRef );
    ret, thresh = cv2.threshold( bwImg, 0, 255, cv2.cv.CV_THRESH_BINARY+cv2.cv.CV_THRESH_OTSU)
    #print "thresh:", str(thresh)
    #print "+-" * 10
    #print "ret", str(ret)
    #print "--" * 10
    cannyImg = cv2.Canny(bwImg, int(ret * 0.5),  ret)
    #cannyImg = cv2.Canny(bwImg, int(ret * 0.5),  ret)
    #~ element = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    #~ cannyImg = cv2.dilate(cannyImg, element) # makes 07_ to work!
    if( imageBufferForDrawingDebug != None ):
        cv2.imshow('canny', cannyImg)
    contours, hierarchy = cv2.findContours(cannyImg, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    #cv2.drawContours(bwImg, contours, -1, (0,0,10), 2)
    #contours, hierarchy = cv2.findContours(cannyImg,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    #~ mask = numpy.zeros(bwImg.shape,numpy.uint8)


    #~ printDebug( "nbr contours: %d" % len( contours ) );

    nMaxLenContour = 0;
    for contour in contours:
        if( len( contour ) > nMaxLenContour ):
            nMaxLenContour = len( contour );
    #~ print( "nMaxLenContour: %d" % nMaxLenContour );

    if( nMaxLenContour < len( contours ) / 4 ):
        print( "INF: abcdk.image.findSquaredLogo: input seems too simple, reducing resolution per 2..." );
        imageBuffer2 = cv2.resize( imageBufferRef, dsize=(0,0), fx=0.5, fy=0.5 );
        retVal = findSquaredLogo( imageBuffer2, imageBufferForDrawingDebug = imageBufferForDrawingDebug );
        # multiply results:
        for iRect in range( len(retVal) ):
            for ipt in range(4):
                for icoord in range(2):
                    retVal[iRect][ipt][icoord] *= 2;
        return retVal;

    for i in range( len(contours) ):
        contours[i] = cv2.approxPolyDP( contours[i],0.08*cv2.arcLength(contours[i],True),True ) # was 0.1*cv2.arcLength # 0.08

    for h,cnt in enumerate(contours):
        if( imageBufferForDrawingDebug != None ):
            #~ cv2.drawContours(imageBufferForDrawingDebug,[cnt],-1,255,-1)
            pass
        pass
        #~ mean = cv2.mean(imageBufferRef,mask = mask)

    ret = []
    rects = []
    rMinLength = 4;
    rWidthHeightRatio = 4/3.
    rMinArea = 100;
    listCorners = [];

    for contour in contours:
        if len(contour) < rMinLength:
            #pass
            continue

        c = contour
        #c = cv2.approxPolyDP(contour, 0.1*cv2.arcLength(contour, True), True)
        x, y, w, h = cv2.boundingRect(c)
       # p = numpy.int0(cv2.cv.BoxPoints(cv2.minAreaRect(contour)))
        ratio = w / float(h)

        #~ print( "\nNew contour: x, y, w, h: %d, %d, %d, %d" % ( x, y, w, h ) );

        #~ print( "ratio: %f" % ratio );
        if( rWidthHeightRatio * 0.4 > ratio or rWidthHeightRatio * 1.6 < ratio ):
            #~ pass
            continue

        area = w * h
        #~ print( "area: %f" % area );
        if (area < rMinArea):
            continue
            #pass


        xCenter = x+w/2;
        yCenter = y+h/2;

        rRectSize = max( 1, w/10 );

        if(
                xCenter < rRectSize or xCenter > width - rRectSize
            or yCenter < rRectSize or yCenter > height - rRectSize
        ):
            continue;

        #~ print( "\nNew contour: x, y, w, h: %d, %d, %d, %d" % ( x, y, w, h ) );

        anInnerColor = imageBufferRef[yCenter,xCenter]; # only one point
        #~ print( "nInnerColor at %dx%d: %s" % ( xCenter, yCenter, anInnerColor ) );

        #~ rInnerMean = cannyImg[yCenter-rRectSize:yCenter+rRectSize,xCenter-rRectSize:xCenter+rRectSize].mean();

        #~ if( rInnerMean < 12 ):
            #~ # it's not filled shape (or it's too near !!! (so it's a bad test!)
            #~ continue;
        #~ print( "rInnerMean at %dx%d: %f" % ( xCenter, yCenter, rInnerMean ) );

        # compute the average color in the rectangle
        anInnerColor = imageBufferRef[yCenter-rRectSize:yCenter+rRectSize,xCenter-rRectSize:xCenter+rRectSize];
        #~ print( "anInnerColor at %dx%d: %s" % ( xCenter, yCenter, anInnerColor ) );
        anInnerColor = anInnerColor.mean(0);
        #~ print( "anInnerColor at %dx%d: %s" % ( xCenter, yCenter, anInnerColor ) );
        anInnerColor = anInnerColor.mean(0);
        #~ print( "anInnerColor at %dx%d: %s" % ( xCenter, yCenter, anInnerColor ) );
        nSumOtherColor = anInnerColor[1] +anInnerColor[2];
        if( nSumOtherColor != 0 ):
            rBlueRatio = ( anInnerColor[0] * 2. ) / nSumOtherColor;
        else:
            rBlueRatio = anInnerColor[0] / 8.; # so we need, at least 4 to be blue !!!
        #~ print( "rBlueRatio: %f" % ( rBlueRatio ) );
        if( rBlueRatio < 0.8 ): # 1.4 # 0.95 # 1.05
            # it's not a center with blue
            continue;


        if( imageBufferForDrawingDebug != None ):
            #~ cv2.rectangle(imageBufferForDrawingDebug, (x, y), (x+w, y+h), (0, 200, 50))
            pass
        rect = (x,y,w,h)

        bHoughTest = True;
        if( bHoughTest ):
            subRect = cannyImg[y:y+h,x:x+w];
            #~ print( "subRect: %s" % str( subRect ) );
            rectFound = cv2.HoughLinesP( subRect, 1, cv.CV_PI/180, 20, 20, 10 ); # doesn't work with opencv '$Rev: 4557 $' (as on 1.17) leadings to: "<unknown> is not a numpy array" but works fine on 2.4.5 and 2.4.6

            #~ print( "rectFound: %s" % str( rectFound ) );
            if( rectFound == None ):
                #~ cv2.circle(imageBufferForDrawingDebug, (x+w/2, y+h/2), 10, (0, 0, 255))
                continue;
            lines = rectFound[0];
            for line in lines:
                pass
                if( imageBufferForDrawingDebug != None ):
                    #~ print( "line: %s" % str( line ) );
                    cv2.line( imageBufferForDrawingDebug, (x+line[0], y+line[1]), (x+line[2], y+line[3]), (255,0,0), 2);
            #~ if( len(lines) < 3 ):
                #~ continue; # when logo is small, we don't have a lot of lines

        listContour = arraytools.simplifyArray( contour.tolist() );
        #~ print( "contour: %s" % listContour );
        corner = numeric.findCorner( listContour );
        #~ print( "corner: %s" % corner );
        if( not numeric.isRhombus( corner ) ):
            continue;

        # check blackiness at corner
        anColorCorner = [0,0,0];
        kanOffset = [2,-2]; # peek the color a bit into the rectangle
        for j in range(len(corner)):
            pt = imageBufferRef[corner[j][1]+kanOffset[j/2],corner[j][0]+kanOffset[j%2]];
            #~ print( "pt in rect: %s" % pt );
            for i in range( 3 ):
                anColorCorner[i] += pt[i];

        #~ print( "anColorCorner: %s" % str( anColorCorner ) );
        nMaxBlackThreshold = 80*4;
        if( anColorCorner[0] > nMaxBlackThreshold or anColorCorner[1] > nMaxBlackThreshold or anColorCorner[2] > nMaxBlackThreshold ):
            continue;

        bEqualOther = False;
        for shape in listCorners:
            nDiff = numeric.getShapeDifference( corner, shape );
            if( nDiff < 10 ):
                bEqualOther = True;
                #~ print( "getShapeDifference: %s is equal to %s (diff:%d)!" % ( corner, shape, nDiff ) );
                break;
        if( bEqualOther ):
            continue;

        if( imageBufferForDrawingDebug != None ):
            print( "*** corner found at finish: %s" % corner );
            for i,c in enumerate(corner):
                cv2.circle(imageBufferForDrawingDebug, (c[0],c[1]), 4+i*2, (0, 255, 255))
        listCorners.append( corner );

    # remove rectangle into others
    listOut = [];
    for i in range( len( listCorners ) ):
        for j in range( len( listCorners ) ):
            if( i == j ):
                continue;
            if( numeric.isShapeRoughlyInto( listCorners[i], listCorners[j] ) ):
                #~ print( "isShapeRoughlyInto: %s is into %s !" % ( listCorners[i], listCorners[j] ) );
                break;
        else:
            listOut.append( listCorners[i] );

    if( imageBufferForDrawingDebug != None ):
        for shape in listOut:
            for i,c in enumerate(shape):
                cv2.circle(imageBufferForDrawingDebug, (c[0],c[1]), 4+i*2, (255, 255, 0),1)

        cv2.imshow('debug', imageBufferForDrawingDebug);
        #~ cv2.imshow('bwImg (must be unchanged)', bwImg);

    print( "INF: abcdk.image.findSquaredLogo: found: %s" % listOut );
    return listOut;
# findSquaredLogo - end


def findSquaredLogo_test():
    strPath = "C:/work/Dev/git/appu_data/images_to_analyse/square_logo/";
    nCptGood = nCptTotal = nCptBad = 0;
    aRef = [
        [  [[652, 890], [673, 885], [654, 910], [677, 906]]    ],
        [  [[389, 587], [448, 595], [381, 636], [440, 643]]    ],
        [  [[854, 308], [887, 308], [853, 338], [884, 338]]    ],
        [  [[492, 116], [570, 121], [488, 181], [565, 185]]    ],
        [  [[741, 183], [837, 183], [737, 258], [834, 258]]    ],

        [  [[530, 326], [743, 334], [528, 494], [732, 501]]    ],
        [  [[224, 466], [1032, 486], [304, 920], [928, 930]]    ],
        [  [[243, 204], [592, 204], [267, 471], [584, 455]]    ],
        [  [[873, 450], [961, 456], [867, 524], [954, 529]]    ],
        [  [[728, 458], [798, 460], [725, 516], [795, 519]]    ],

        # 11
        [  [[1054, 472], [1174, 454], [1078, 592], [1222, 566]]    ], # just one of them!
        [  [[524, 452], [556, 448], [528, 491], [562, 485]]    ],
        [  [[620, 388], [752, 388], [616, 500], [748, 496]]    ], # just one of them!
        [  [[504, 434], [558, 438], [503, 478], [555, 480]]    ], # the top one

        # 20: not to be found !
        [      ],
        [      ],
        [      ],
        [      ],
    ];

    for strFilename in sorted( os.listdir( strPath ) ):
        #~ if( "50" in strFilename ): # work on a specific image
        #~ if( not "many_red" in strFilename ):
            #~ nCptTotal += 1;
            #~ continue;
        if( not "_square_logo" in strFilename ): # don't analyse this one!
            nCptTotal += 1;
            continue;
        strPathFilename = strPath + strFilename;
        if( not os.path.isfile( strPathFilename ) ):
            continue;
        print( "TEST --- %d: %s: " % (nCptTotal, strFilename) );
        imageBuffer = cv2.imread( strPathFilename );
        #~ imageBuffer = cv2.resize( imageBuffer, dsize=(0,0), fx=0.5, fy=0.5 ); # test
        timeBegin = time.time();
        retVal = findSquaredLogo( imageBuffer, imageBufferForDrawingDebug = imageBuffer );
        print( "TEST RESULTS --- %d: %s (duration:%5.3fs): %s" % ( nCptTotal, strFilename, time.time() - timeBegin, retVal ) );
        strOut = "not detected";
        if( retVal != [] ):
            print( "ref: %s" % (aRef[nCptTotal] ) );
            strOut = "DETECTED (ref: %s)" % (aRef[nCptTotal]);
            bBad = False;
            nDiffMin = 421421;
            if( aRef[nCptTotal] != [] ):
                for square in retVal:
                    nDiff = 0;
                    for i in range( 4 ):
                        nDiffOnePoint = numeric.dist2D_squared( square[i], aRef[nCptTotal][0][i] );
                        nDiff += nDiffOnePoint;
                        print( "nDiffOnePoint: %d, nDiff: %d" % (nDiffOnePoint, nDiff) );
                    if( nDiffMin > nDiff ):
                        nDiffMin = nDiff;

            if( nDiffMin > 12 ):
                strOut = "FALSE DETECTION (nDiffMin:%d)" % nDiffMin;
                bBad = True;
                nCptBad += 1;
            if( not bBad ):
                strOut = "GOOD";
                nCptGood += 1;
        elif( aRef[nCptTotal] == [] ):
            strOut = "NOT DETECTED BUT NOTHING TO DETECT => GOOD";
            nCptGood += 1;
        print( "analysed: " + strOut );
        cv.WaitKey(1000);
        if( strOut != "GOOD" ):
            showImage2( imageBuffer, rTimeAutoClose = 0.3, strWindowName = strOut );
        if( nCptTotal >= 20 ): # permit to see a specific image
            showImage2( imageBuffer, rTimeAutoClose = 2., strWindowName = strOut );
            pass
        nCptTotal += 1;
    print( "RESULTS: %d/%d (bad:%d)" % (nCptGood, nCptTotal,nCptBad) );
    assert( nCptGood >= 15 ); # current performance !
# findSquaredLogo_test - end

def isMoveDetected(aImage1, aImage2, nMoveThreshold, bDebug=False):
    d1 = cv2.absdiff(aImage1, aImage2)
    if bDebug:
        print("Movement of %f" % numpy.mean(d1))
    return numpy.mean(d1) > nMoveThreshold
# isMoveDetected - end

class MovementDetecter:
    """
    Wait until movement
    """
    def __init__(self, nCamera=0, rStepTime=0.2, kResolution=camera.camera.kVGA, nMoveThreshold=10):
        self.bMustStop = False
        self.nCamera = nCamera
        self.nColorSpace = 0
        self.lastImage = None
        self.curImage = None
        self.kResolution = kResolution
        self.rStepTime = rStepTime  # in second
        self.nMoveThreshold = nMoveThreshold  # mean of difference in pixel over the whole image
        self.bDebug = False

    def update(self):
        aImage = camera.camera.getImageCV2(nImageResolution = self.kResolution,
                                           nCamera = self.nCamera,
                                           colorSpace=self.nColorSpace,
                                           bNoUnsubscribe=False)
        if self.lastImage != None:
            if isMoveDetected(aImage, self.lastImage, self.nMoveThreshold, bDebug = self.bDebug):
                print("Move detected " )
                self.bMustStop = True
        else:
            print("No move detected")
        self.lastImage = aImage

    def start(self):
        self.bMustStop = False
        while not(self.bMustStop):
            self.update()
            time.sleep(self.rStepTime)

    def stop(self):
        if not(self.bMustStop):
            self.bMustStop = True
            time.sleep(1)
        return True


class PictureTaker:
    """
    Takes picture when a movement is detected
    """
    def __init__(self, nCamera=0, rStepTime=0.2, kResolution=camera.camera.kVGA, nMoveThreshold=10 , strPicturePath='/tmp/'):
        self.bMustStop = False
        self.nCamera = nCamera
        self.nColorSpace = 0
        self.lastImage = None
        self.curImage = None
        self.kResolution = kResolution
        self.rStepTime = rStepTime  # in second
        self.nMoveThreshold = nMoveThreshold  # mean of difference in pixel over the whole image
        self.bDebug = False
        self.strPicturePath = strPicturePath


    def update(self):
        aImage = camera.camera.getImageCV2(nImageResolution = self.kResolution,
                                           nCamera = self.nCamera,
                                           colorSpace=self.nColorSpace,
                                           bNoUnsubscribe=True)
        if self.lastImage != None:
            if isMoveDetected(aImage, self.lastImage, self.nMoveThreshold, bDebug = self.bDebug):
                strName = self.strPicturePath + filetools.getFilenameFromTime() + ".jpg";
                print("Move detected taking picture (file %s)" % strName)
                cv2.imwrite(strName, aImage,[cv2.IMWRITE_JPEG_QUALITY, 70]);
            else:
                if self.bDebug:
                    print("No move detected")
        else:
            if self.bDebug:
                print("Last image is None")


        self.lastImage = aImage

    def start(self):
        self.bMustStop = False
        while not(self.bMustStop):
            self.update()
            time.sleep(self.rStepTime)

    def stop(self):
        if not(self.bMustStop):
            self.bMustStop = True
            time.sleep(1)
        return True

# PictureTaker - end

def convertToAscii( imageBuffer, nReduceToWidth = -1, nReduceToHeight = -1 ):
    """
    load a filename and return it in ascii mode (usefull to draw image on text terminal thru serial or ...)
    Return a big string with all the char
    """
    strTable = " .:oilIH"; # character table sorted by luminosity

    h, w, nNbrChannels = imageBuffer.shape;

    if( nReduceToWidth != -1 or nReduceToHeight != -1 ):
        neww = w;
        newh = h;
        if( nReduceToWidth != -1 ):
            if( w > nReduceToWidth ):
                neww = nReduceToWidth;
        if( nReduceToHeight != -1 ):
            if( h > nReduceToHeight ):
                newh = nReduceToHeight;
        #~ small_image = cv.CreateImage( (h,w), 8, nNbrChannels );
        #~ cv.Resize( imageBuffer, small_image, interpolation=cv.CV_INTER_CUBIC );
        print( "INF: convertToAscii: reducing from %dx%d to %dx%d" % (w,h,neww,newh) );
        # fx is the ratio (so 0.5 divide by 2)
        imageBuffer = cv2.resize(imageBuffer,(neww,newh), interpolation = cv2.INTER_CUBIC)
        w = neww;
        h = newh;
    if( nNbrChannels > 1 ):
        # not optimal
        #workGrey = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );
        workGrey = cv2.cvtColor(imageBuffer, cv2.COLOR_BGR2GRAY);
        imageBuffer = workGrey;

    #~ cv2.imwrite( "c:/tempo/test.jpg", imageBuffer );
    strOut = "";
    for j in xrange( h ):
        for i in xrange( w ):
            nColor = imageBuffer[j,i]; # not optimal
            iColor = ( nColor * len(strTable) )/ 256;
            #~ if( nColor != 255 ):
                #~ print( "i:%d, j:%d, color: %s, icolor: %s" % (i,j,nColor,iColor) );
            strOut += strTable[iColor];
        strOut += "\n";
    return strOut;
# convertToAscii - end

def acquireAndViewInAscii( strCommandToGetImage, strTempFilename, nReduceToWidth = -1, nReduceToHeight = -1, rSleepTime = 0.3 ):
    """
    launch a command to get a new image, print it, then get another one...
    Here's an example on romeo head:
        import abcdk.image
        abcdk.image.acquireAndViewInAscii( "./testcamerav4l2 -i -w320 -h240", "output1.ppm", 160, 120, 0.5 );
    """
    while( True ):
        os.system( strCommandToGetImage );
        im = cv2.imread( strTempFilename );
        print( convertToAscii( im, nReduceToWidth = nReduceToWidth, nReduceToHeight = nReduceToHeight ) );
        time.sleep( rSleepTime );
# acquireAndViewInAscii - end



def autotest_convertToAscii():
    #im = cv2.imread( "c:/work/Dev/git/appu_data/images_to_analyse/4_interest_green_bad.png" );
    #~ im = cv2.imread( "c:/work/graph/1_ACI_Associate.jpg" );
    im = cv2.imread( "c:/tempo/1_ACI_Associate_grey.jpg" );
    print convertToAscii( im, nReduceToWidth = 160, nReduceToHeight = 120 );


def detectLine( img, bVerbose = False ):
    """
    detect a line in an img.
    Return [rOffset, rOrientation]
    - rOffset: rough position of the line on screen [-1, +1] (-1: on the extreme left, 1: on the extreme right, 0: centered)
    - rOrientation: it's orientation [-pi/2,pi/2]
    or [None,None], if no line detected
    """
    nWidth = img.shape[1];
    nHeight = img.shape[0];
    #~ kernel = numpy.array([ -1., +1]); # detect horiz line if anchor is -1,-1
    #~ kernel = numpy.array( [1, -2, 1, 2, -4, 2, 1, -2, 1] );
    #~ kernel = numpy.array( [0,1,0, 0, -2, 0, 0,1, 0] );
    #~ kernel = numpy.array( [-1,-1,-1, -1, -0, 1, 1,1, 1] );
    #~ dst=numpy.copy( img );
    #~ img2 = cv2.filter2D( img, dst = dst, ddepth = -1, kernel=kernel, anchor=(-1, -1) );
    #~ kernel = numpy.ones((7,7), dtype=numpy.float)/49.0 # mega blur

    # multi directionnel:
    kernel = -numpy.ones((3,3), dtype=numpy.float);
    kernel[1,1] = 8;

    # vertical: (just front montant)
    #~ kernel = -numpy.ones((1,2), dtype=numpy.float);
    #~ kernel[0,1] = 1;

    # vertical: (double front)
    kernel = -numpy.ones((1,3), dtype=numpy.float);
    kernel[0,1] = 2;

    img = cv2.filter2D(img, -1, kernel);

    retval, img = cv2.threshold( img, 45, 255, cv2.THRESH_TOZERO ); # was 60
    #~ element = cv2.getStructuringElement( cv2.MORPH_RECT,(1,2) );
    #~ img = cv2.erode(img, element);

    aMaxL = numpy.argmax(img, axis=1 );
    aMaxLWithoutZeros = aMaxL[aMaxL>0];

    print( "Line Length: %s" % len(aMaxLWithoutZeros) );

    if( len( aMaxLWithoutZeros ) < 4 ):
        print( "WRN: abcdk.image.detectLine: detected line is very short: %s" % aMaxLWithoutZeros );
        return [None, None];

    aNonZeroIdx = numpy.where(aMaxL != 0)[0]; # here we retravelling thru the list, it's not optimal (TODO)
    nFirstNonZero = aNonZeroIdx[0];
    nLastNonZero = aNonZeroIdx[-1];
    nHeightSampling = nLastNonZero - nFirstNonZero;

    print( "nFirstNonZero: %s" % nFirstNonZero );
    print( "nLastNonZero: %s" % nLastNonZero );
    print( "nHeightSampling: %s" % nHeightSampling );
    print( "nHeight: %s" % nHeight );
    print( "nWidth: %s" % nWidth );

    # here instead of take the average of left and right border, we just keep left, sorry...
    aLine = aMaxLWithoutZeros;
    #~ print( "aLine: %s" % aLine );

    #~ cv2.imwrite( "/tmp/line.jpg", img );
    #~ showImage2( img, rTimeAutoClose = 2., strWindowName = "detectLineTemp" );
    if( bVerbose ):
        import filetools
        cv2.imwrite( getDebugPath() + filetools.getFilenameFromTime() + "_detect_line.jpg", img );

    # averaging
    nSamplingSize = max( min(len(aLine) / 40, 8), 1 );
    print( "nSamplingSize: %s" % nSamplingSize );
    rTop = numpy.average(aLine[:nSamplingSize]); # first points
    rMed =  numpy.average(aLine[len(aLine)/2:len(aLine)/2+nSamplingSize]);
    rBase = numpy.average(aLine[-nSamplingSize:]); # last points

    #~ rOrientation = 0.; # TODO: regression lineaire ou filtrage puis moyenne des deltas ?

    # trying a rough direction
    rOrientation = ((rTop-rBase))/nHeightSampling; # WRN: here it could be wrong as the aLine has zero removed, so perhaps the top and bottom are not at top or bottom !
    print( "rOrientation rough: %s" % rOrientation );
    #~ rOrientation = rOrientation*(nHeight/nHeightSampling)/nWidth;
    #~ print( "rOrientation normalised: %s" % rOrientation );
    print( "rBase: %f, rMed: %f, rTop: %f, rOrientation: %f" % (rBase, rMed, rTop, rOrientation) );
    return( [(rMed/nWidth)*2-1, rOrientation] );
# detectLine - end

def autotest_detectLine():
    astrImg = [
        "test_line.jpg",
        "test_line2.jpg",
        "test_line_diag_to_left.jpg",
        "test_line_diag_to_right.jpg", # ~40° => 0.7 rad
        "test_line_diag_to_right_alt.jpg", # ~60° => 1.0 rad
        "test_line_diag_to_right_alt_crop.jpg", # ~60° => 1.0 rad
        "detect_line_blurred.jpg",
    ];
    for strImg in astrImg:
        print( "***** detectLine on %s" % strImg );
        img = cv2.imread( "/home/likewise-open/ALDEBARAN/amazel/" + strImg, cv2.CV_LOAD_IMAGE_GRAYSCALE );
        #~ showImage2( img, rTimeAutoClose = 1., strWindowName = "orig" );
        ret = detectLine( img, True );
        print( "detectLine return: %s" % ret );



def detectGreenLine( img, nMinContiguousPixel = 10 ):
    """
    Is there some pure green line (often caused by camera parasites) in the image ?
    a green line is a contiguous plain green (0x00FF00) pixels (at least 10)
    return the index of the line containing green line. or [] if none or False on error
    """
    nNbrChannels = img.shape[2];
    if( nNbrChannels != 3 ):
        print( "ERR: abcdk.image.detectGreenLine: error: the image needs to be in color (current channel number is %d)" % nNbrChannels );
        return False;

    imgTreshold = cv2.inRange( img, (0,255,0), (0,255,0) );
    #~ print( "imgTreshold: %s" % str(imgTreshold) );

    kernel = numpy.ones((1,nMinContiguousPixel),numpy.uint8)
    #~ print( "kernel: %s" % str(kernel) );
    imgTreshold = cv2.erode( imgTreshold, kernel, iterations = 1 );
    #~ print( "imgTreshold: %s" % str(imgTreshold) );

    res = numpy.sum( imgTreshold, axis=1 );
    #~ print( "res sum: %s" % str(res) );
    res = numpy.nonzero( res )[0];
    #~ print( "res nonzero: %s" % str(res) );

    return res;
# detectGreenLine - end

def detectGreenLine_test():
    img = numpy.array( [
                [(0,0,0), (0,1,2), (2,1,3), (2,1,3)],
                [(0,0,0), (0,1,2), (2,1,3), (2,1,3)],
            ] );
    res = detectGreenLine( img );
    #assert( [] == numpy.array( [] ) );
    #assert( numpy.array(res) == numpy.array([]) );
    assert( list(res) == list([]) );


    img = numpy.array( [
                [(0,0,0), (0,1,2), (2,1,3), (2,1,3)],
                [(0,0,0), (0,1,2), (2,1,3), (2,1,3)],
                [(0,0,0), (0,255,0), (0,255,0),(0,1,2)],
                [(0,0,0), (0,255,0), (0,255,0), (0,255,0)],
                [(0,0,0), (0,255,0), (0,255,0),(0,1,2)],
                [(0,0,0), (0,255,0), (0,255,0), (0,255,0)],
            ] );

    res = detectGreenLine( img, nMinContiguousPixel = 3 );
    assert( list(res) == list([3,5]) );

    img = cv2.imread( "C:\\work\\Dev\\git\\appu_data\\images_to_analyse\\fake_parasite.png" );
    res = detectGreenLine( img, nMinContiguousPixel = 3 );
    print( "res fake image: %s" % res );
    assert( list(res) == list([54,85]) );


def calibrateCamera(aPatternSize, rSquareSize, nMinDetectedChessBoard=20):
    """
    Return camera information based on chessboards detected

    Usage:
    import config
    config.bInChoregraphe = False
    import image
    image.calibrateCamera((9,6), 1)
    """
    aImgs = []
    nDetectedChessboard = 0
    while(len(aImgs)) < nMinDetectedChessBoard:
        img = camera.camera.getImageCV2(nImageResolution=3, colorSpace=0, bNoUnsubscribe=True)
        res = detectChessboard(img, aPatternSize=aPatternSize)  # TODO : optimized here we call two times detectChessboard, here and in _cameraCalibrate
        if res.bFound:
            aImgs.append(img)
            nDetectedChessboard += 1
            print("abcdk.image.cameraCalibrate %s / %s chessboardDetected" % (nDetectedChessboard, nMinDetectedChessBoard))
    return _calibrateCamera(aImgs, aPatternSize, rSquareSize)

def detectChessboard(img, aPatternSize=(9, 6), bDebug=False):
    """
    detect a black and white rectangular chessboard in an img.
    Return points detected
    """
    bFound, aCorners = cv2.findChessboardCorners(img, aPatternSize)
    if bFound:
       term = ( cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1 )
       cv2.cornerSubPix(img, aCorners, (5, 5), (-1, -1), term)  # ca fait un truc ca ?

    if bDebug:
       debugImg= cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
       cv2.drawChessboardCorners(debugImg, aPatternSize, aCorners, bFound)
       cv2.imshow("Debug", debugImg)
       cv2.waitKey(-1)
    import collections
    ret = collections.namedtuple("detectChessboard", ['bFound', 'aCorners'])
    res = ret(bFound, aCorners)
    return res

# TODO : il faudrait faire une methode qui appelle juste imagePnp avec la sortie de detectChessboard
def autotest_detectChessboard():
    img = cv2.imread("./data/images/pattern_9_6.png", 0)
    detectChessboard(img)

def _calibrateCamera(aPoints, aPatternSize, rSquareSize=1.0):
    """
    Run calibration process using  a list of image containing the same black/with chessboard
    (it's inspired by cameraCalibration code in opencv python examples)

    :param aPoints: a list of list of points detected (showing the same pattern)
    """
    import numpy as np
    import collections
    ret = collections.namedtuple("CameraImage", ["rms", "camera_matrix", "dist_coefs", "rvecs", "tvecs"])
    pattern_points = np.zeros( (np.prod(aPatternSize), 3), np.float32 )
    pattern_points[:,:2] = np.indices(aPatternSize).T.reshape(-1, 2)
    pattern_points *= rSquareSize

    aImgPts = []  # list of images points corresponding to pattern_points (same order)
    aSetH = set()
    aSetW = set()
    for img in aImgs:
        adetectChessboard = detectChessboard(img, aPatternSize=aPatternSize)
        if adetectChessboard.bFound:
            aImgPts.append(adetectChessboard.aCorners)
            h, w = img.shape[:2]
            aSetH.add(h)
            aSetW.add(w)

    if len(aSetH)>1 or len(aSetW)>1:
        strError = "Images should have the same shape"  # TODO : we should have an abcdk Exception
        print("abcdk.image.calibrateCamera: %s" % strError)
        return ret[[None]*5]
    if len(aImgPts) == 0:
        strError = "No chessboard detected"
        print("abcdk.image.calibrateCamera: %s" % strError)
        return ret[[None]*5]

    aObjectPts = [pattern_points for imgPts in aImgPts]  # same number of patterns than detected corners
    rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera(aObjectPts, aImgPts, (aSetW.pop(), aSetH.pop() ))
    res = ret(rms, camera_matrix, dist_coefs, rvecs, tvecs)
    return res

def autotest_cameraCalibration():
    img = cv2.imread("./data/images/pattern_9_6.png", 0)
    aImgs = [img] * 10
    res =  _calibrateCamera(aImgs, aPatternSize=(9, 6))
    print res


def addText(aImage, strText='subtitle text'):
    """
    aImage: opencv image
    strText: subtitle text

    return Image with text above it
    """
    #pt1 = (0, aImage.shape[1])
    #pt2 = (0 + rRectangleWidth, aImage.shape[1] - rRectangleHeight)
    #cv2.rectangle( aImage, pt1,pt2, (255,0,0) );
    textSize = cv2.getTextSize( strText, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1 );
    print( str( textSize ) );
    colorText = (255,255,0);
    cv2.putText( aImage, strText, (0, aImage.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colorText );
    return aImage
    
def addTextAboveLocation(aImage, strText='subtitle text', pt = [10,10], color = (0,0,255), rTextSize = 0.5 ):
    """
    aImage: opencv image
    strText: subtitle text

    return Image with text above it
    """
    #pt1 = (0, aImage.shape[1])
    #pt2 = (0 + rRectangleWidth, aImage.shape[1] - rRectangleHeight)
    #cv2.rectangle( aImage, pt1,pt2, (255,0,0) );
    textSize = cv2.getTextSize( strText, cv2.FONT_HERSHEY_SIMPLEX, rTextSize, int(2*rTextSize) );
    #~ print( "text size: %s" % str( textSize ) );
    cv2.putText( aImage, strText, (int(pt[0]-textSize[0][0]/2), int(pt[1]) - textSize[0][1]/2), cv2.FONT_HERSHEY_SIMPLEX, rTextSize, color, int(2*rTextSize) );
    return aImage    

def addTextToImage(strImageFullFilename, strText='subtitle text'):
    """
    add a text to an image on disk
    """
    aImage = cv2.imread(strImageFullFilename)
    res = addText(aImage)
    cv2.imwrite(strImageFullFilename, res)
    
def drawLabelledPoint( img, aListPoint ):
    """
    draw letters or numbers over a list of point
    """
    for idx, pt in enumerate( aListPoint ):
        addTextAboveLocation( img,  chr(ord('A')+idx), pt );
# drawLabelledPoint - end
    
    
def foundVehicle( cameraImage, bDebugShow = False ):
    """
    Find the vehicle in the space, return it's 6d position in the foot space
    return [] if unknown
    """
    
    def _prepareImageForBluePodDetection(colouredImg, bDebugShow = False):
        """
        takes a coloured image and output a bw image with (nearly) only the blue channel keeped
        return the bw image
        """
        # we work in hsv space and want to select Hue = blue http://i.stack.imgur.com/gCNJp.jpg  blue is between 180 degree and 240 in hue..


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
        if bDebugShow:
            strWindowDebug = "0: prepareImageForBluePodDetection: at end";
            cv2.imshow( strWindowDebug, img_bw );
            cv2.moveWindow( strWindowDebug, 0, 0 );
        return img_bw
    # prepareImageForBluePodDetection - end
    
    def  _is4Valid( contours, bDebugShow = False ):
        """
        is there exactly 4 point or 4 point with an average size
        return True if yes
        """
        if( bDebugShow ):
            print( "_is4Valid: len(contours): %s" % len(contours) );
        if( len(contours) == 4 ):
            return True;
            
        if( len(contours)  < 4 ):
            return False;
        
        arArea = [];
        for num, contour in enumerate(contours):
            m = cv2.moments(contour)
            rArea = m['m00']
            if( bDebugShow ):
                print( "_is4Valid: rArea: %s" % rArea );
            arArea.append( rArea );
            
        rAreaAvg = sum(arArea)/len(arArea);
        if( bDebugShow ):
            print( "_is4Valid: rAreaAvg: %s" % rAreaAvg );
        if( rAreaAvg > 16 ):
            rLimit = 8.
        elif rAreaAvg > 6:
            rLimit = 3.;
        else:
            rLimit = 1.;
        
        nCptBigger = 0;
        for r in arArea:
            if( r > rLimit ):
                nCptBigger += 1;
        if( bDebugShow ):
            print( "_is4Valid: nCptBigger: %s" % nCptBigger );
        return nCptBigger == 4;
    # _is4Valid - end
    
    def _computeThresholdImage( cameraImage, bDebugShow = False ):
        
        thresholdImg = cameraImage;
        
        r, thresholdImg = cv2.threshold(thresholdImg, 230, 255, cv2.THRESH_BINARY)  # we filter a bit in order to disconnet dots if they are connected        
        contours, hierarchy = cv2.findContours(thresholdImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if bDebugShow:
            strWindowDebug = "0: _computeThresholdImage: after threshold";
            cv2.imshow(strWindowDebug, thresholdImg)
            cv2.moveWindow( strWindowDebug, 0, 240 );        
            print( "len cont 1: %s" % len(contours) );
            
        if( _is4Valid(contours) ):
            # it's already ok, returning !
            return thresholdImg;            
        
        r, thresholdImg = cv2.threshold(thresholdImg, 190, 255, cv2.THRESH_BINARY)  # we filter a bit in order to disconnet dots if they are connected
        #~ element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        #~ thresholdImg = cv2.erode(thresholdImg, element,iterations=1)
        
        if bDebugShow:
            strWindowDebug = "1: _computeThresholdImage: after threshold";
            cv2.imshow(strWindowDebug, thresholdImg)
            cv2.moveWindow( strWindowDebug, 320, 240 );
            
        contours, hierarchy = cv2.findContours(thresholdImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if( _is4Valid(contours) ):
            # it's already ok, returning !
            return thresholdImg;      

                
            
        # else try thresholding gentlier
        thresholdImg = cameraImage;
        
        r, thresholdImg = cv2.threshold(thresholdImg, 155, 255, cv2.THRESH_BINARY)  # we filter a bit in order to disconnet dots if they are connected
        element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        thresholdImg = cv2.erode(thresholdImg, element,iterations=1)
        
        if bDebugShow:
            strWindowDebug = "2: _computeThresholdImage: after threshold2";
            cv2.imshow(strWindowDebug, thresholdImg)
            cv2.moveWindow( strWindowDebug, 640, 240 );  

            
        contours, hierarchy = cv2.findContours(thresholdImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if( _is4Valid(contours) ):
            # it's already ok, returning !
            return thresholdImg;      

        element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2))
        #cv2.imshow('start', thresholdImg)
        thresholdImg = cv2.morphologyEx(thresholdImg, cv2.MORPH_OPEN, element, iterations=1)  # removing noise
        #cv2.imshow('1', thresholdImg)
        #thresholdImg = cv2.morphologyEx(thresholdImg, cv2.MORPH_CLOSE, element, iterations=3)  # removing hole in blob
        #cv2.imshow('2', thresholdImg)

        if bDebugShow:
            strWindowDebug = "3: _computeThresholdImage: after morpho";
            cv2.imshow(strWindowDebug, thresholdImg);
            cv2.moveWindow( strWindowDebug, 0, 480 );            
         
            
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
            strWindowDebug = "4: _computeThresholdImage: after threshold2";
            cv2.imshow( strWindowDebug, thresholdImg );
            cv2.moveWindow( strWindowDebug, 320, 480 );
        #cv2.waitKey()
        #cv2.destroyAllWindows()
        #imagecp = thresholdImg.copy()  # TODO: why are we doing a copy here ?
        return thresholdImg;
    # computeThresholdImage - end
    
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
    # _maskTrueIfOneInKernelIsTrue - end
    
    def _computeLedPts( thresholdImg, image, rAreaTreshold = 3., bDebugShow=False ):
        res = []
        contours, hierarchy = cv2.findContours(thresholdImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if bDebugShow:
            drawingDebug = np.zeros(image.shape,np.uint8) # Image to draw the contours
            for cnt in contours:
                color = np.random.randint(200,255,(3)).tolist() # Select a random color
                cv2.drawContours(drawingDebug,[cnt],0,color,1)
            
        for num, contour in enumerate(contours):
            m = cv2.moments(contour)
            # ** regionprops **
            Area          = m['m00']
            Perimeter     = cv2.arcLength(contour,True)
            if( bDebugShow ):
                print( "Area: %s" % Area );
            if Area > rAreaTreshold:
            ## and Perimeter < 200 and Area < 1000:
                (x, y), radius = cv2.minEnclosingCircle(contour)            
                if( m['m00'] > 0.01 ):
                    Centroid      = ( m['m10']/m['m00'],m['m01']/m['m00'] )
                else:
                    Centroid      = ( x, y )                    
                pt = _LedPt(Centroid[0], Centroid[1])
                pt.area = Area
                pt.perimeter = Perimeter
                pt.val = image[pt.y, pt.x]
                if( bDebugShow ):
                    print( "x,y: %s, %s, val:%s, Centroid: %s" % (x, y, pt.val,Centroid) );
                pt.score = pt.area / (math.pi * radius ** 2)
                res.append(pt)
                #~ print( "pt: %s" % pt );
                if( bDebugShow ):
                    cv2.circle( drawingDebug, (int(Centroid[0]),int(Centroid[1])),3, (0,255,0) );
                
        if bDebugShow:
            strWindowDebug = "5: _computeLedPts";
            cv2.imshow( strWindowDebug, drawingDebug );
            cv2.moveWindow( strWindowDebug, 0, 720 );
                
        return res    
    # _computeLedPts - end
    
    class _LedPt:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.score = 0
            self.area = 0
            self.val = -1
    # class _LedPt - end
        def __getitem__(self, idx):
            if(idx==0):
                return self.x;
            if(idx==1):
                return self.y;
            raise( error );
            
        def __str__( self ):
            return "x: %s, y: %s" % ( self.x, self.y )
                
    def _find4Leds(thresholdImg, cameraImage, bDebugShow = False ):
        nTry = 0
        nMaxTry = 2
        arThreshold = [ 8., 3., 2., 1., -0.01 ];
        while( nTry < len(arThreshold) ):

            rAreaTreshold = arThreshold[nTry];
            if( bDebugShow ):
                print("INF: _computeLedPts: using threshold of %s" % rAreaTreshold );
                
            # not optimal: we redo the compute contour every time
            ledsPt = _computeLedPts(thresholdImg, cameraImage, rAreaTreshold =  rAreaTreshold, bDebugShow=bDebugShow)
            if( bDebugShow ):
                print( "INF: _computeLedPts: len: ledsPt: %s" % len(ledsPt) );
            #~ print( "ledsPt: %s" % ledsPt );
            if len(ledsPt) == 4:
                return ledsPt

            #~ element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
            #~ thresholdImg = cv2.erode(thresholdImg, element, iterations=1)
            #cv2.imshow('retry', thresholdImg)
            #cv2.waitKey(0)

            nTry += 1

        return []
    # _find4Leds - end
    
    #
    # real begin of the function !!!
    #
    
    if( cameraImage.shape[1] > 320 ):
        cameraImage = cv2.resize( cameraImage, (0,0), fx=0.5, fy=0.5 );
    img = _prepareImageForBluePodDetection( cameraImage, bDebugShow = bDebugShow );
    thresholdImg = _computeThresholdImage( img, bDebugShow = bDebugShow );
    aLedPos = _find4Leds( thresholdImg, cameraImage, bDebugShow = bDebugShow );
    if( len(aLedPos) != 4 ):
        return [];
    aLedPos = numeric.findCorner( aLedPos );    
    if( bDebugShow ):
        drawingDebug = cameraImage.copy();
        drawLabelledPoint( drawingDebug, aLedPos );
        strWindowDebug = "9: ordered";
        cv2.imshow( strWindowDebug, drawingDebug );
        cv2.moveWindow( strWindowDebug, 0, 720 );        
        
    import imagePnp
    #~ print(dir(imagePnp))
    
    # top left, top right, bottom left, bottom right
    rA = np.array([-0.0295, 0.026, 0])
    rB = np.array([+0.0295, 0.0255, 0])
    rC = np.array([-0.0295, -0.026, 0])    
    rD = np.array([+0.0295, -0.0255, 0])

    realObjectPts = np.array([rA, rB, rC, rD])

    pnpOpencv = imagePnp.getPnP(aLedPos, realObjectPts, nResolution=2)
    print( "pnpOpencv: %s" % str(pnpOpencv) );
    if( pnpOpencv == None ):
        return [];
    return list(pnpOpencv.translation) +  list(pnpOpencv.orientation);
# foundVehicle - end



def autotest_foundVehicle():
    strMyAppuDataPath = "c:/work/Dev/git/appu_data/"; # change it to match your own !
    strPath = strMyAppuDataPath + "images_to_analyse\moto/";
    listFiles = sorted(os.listdir( strPath ))
    nCpt = 0;
    nCptGood = 0;
    timeBegin = time.time();
    bRender = 1;
    for filename in listFiles:
        print( "*****\n%d: filename: %s" % (nCpt,filename) );
        pathandfilename =  strPath + filename;
        if( os.path.isdir(pathandfilename) ):
            continue;
            
        #~ if( "04" != filename[:2] ): # 12: pod not seen as blue
            #~ continue;            
            
        img = cv2.imread( pathandfilename );
        #~ continue;
        
        pos = foundVehicle( img, bDebugShow = bRender );
        print( "autotest_foundVehicle: return: %s" % pos );
        if( len(pos) != 0 ):
            nCptGood += 1;
            
        if( bRender ):
            # render stuffs
            pass
            
        if(bRender):
            cv2.imshow( filename, img );
            cv2.moveWindow( filename, 960, 0 );
            cv2.waitKey(2000)
            #~ exit()
            
        nCpt += 1;

    if( nCpt > 0 ):
        print( "nCptGood: %d/%d (%5.0f%%)" % (nCptGood,nCpt,nCptGood*100/float(nCpt)) ) # current: 11/12
    print( "time total: %5.2fs" % (time.time() - timeBegin) ); # ~0.12s (opening: 0.05s)
    cv2.destroyAllWindows()
# autotest_foundVehicle - end

def classifyImages( strSrcFolder, strDstFolder, function, aThreshold = [1], aClassName = ["false", "true"], bForceToGrey = False ):
    """
    browse a folder containing images, apply a function on each and copy them in subfolder in destination according to the result on the function on each.
    aThreshold: value to be greater or equal to go to next class
    """
    strSrcFolder += '/'
    strDstFolder += '/'
    nCpt = 0;
    stats = [None]*16;  # make stats on returned variables
    timeBegin = time.time();
    files = os.listdir( strSrcFolder )
    
    flag = 0
    if bForceToGrey: flag = cv2.CV_LOAD_IMAGE_GRAYSCALE
    
    for strFilename in files:
        strFullName = strSrcFolder+strFilename
        if( os.path.isdir(strFullName) ):
            continue
        #~ if not "0_1970_01_01-18h17m04s455083m" in strFilename and not "0_1970_01_01-18h17m44s425023" in strFilename:
            #~ continue
        print( "DBG: file: '%s'" % strFullName )
        im = cv2.imread(strFullName, flag)

        if im == None:
            continue
        rVal = function( im )
        i = 0
        while i < len(aThreshold):
            v = aThreshold[i]
            print( "rVal: %s, v: %s" % (rVal, v ) )
            if rVal < v:
                break
            i += 1
        print( "class: %d" % (i) )
        strExt = '.' + strFilename.split('.')[-1]
        strDst = strDstFolder+aClassName[i]+'/'
        try:
            os.makedirs( strDst )
        except: pass
        strDst += strFilename.replace( strExt, ("_%5.3f" % rVal)+ strExt )
        if 0:
            # copy processed
            cv2.imwrite( strDst, im )
        else:
            # copy original
            shutil.copyfile( strFullName, strDst )
        
        nCpt += 1
        
        #~ if nCpt > 100: break  # temp for debug
        
        print( "processed: %d/%d" % ( nCpt, len(files) ) )
 # classifyImages - end
 
def getSharpnessValue(im):
     r = getImageSharpness( im )
     print r
     r = r[0]
     return r

def sortImageByBlurness( strSrcFolder, strDstFolder ):
    # certains images du franprix sont correct avec 81. (etagere un peu vide et quelques reflets)
    # en fait le laplacien n'est pas sensible au diagonale, ca vaudrait le coup de tester les 2 sens par exemple 18h21m29
    # 18h23m41: interessant aussi
    # 18h26m05
    # 18h26m50
     # 18h27m06
     # 18h27m10
     # 18h27m12
    classifyImages(strSrcFolder, strDstFolder, getSharpnessValue, [100.], ["blurred", "not_blurred"], bForceToGrey=False)

if( __name__ == "__main__" ):
    #~ autotest_foundVehicle()
    sortImageByBlurness( "c:/2018_recording_franprix", "c:/tmpClassify")
        
    exit(0)


def autoTest():
    strMyAppuDataPath = "D:/Dev/git/appu_data/"; # change it to match your own !
    if( False ):
        bRet = convertAriToPng();
        assert( bRet );
    if( False ):
        print( "\n* Testing image quality is quite the same in rgb and grey" );
        for nMethod in range( 4 ):
            print( "-- nMethod: %d" % nMethod );
            imageBuffer = cv.LoadImage( strMyAppuDataPath + "images_to_analyse/0011_Mazel_Alexandre_027.jpg" );
            print getImageQuality( imageBuffer, nMethod = nMethod );
            imageBuffer = cv.LoadImage( strMyAppuDataPath + "images_to_analyse/0011_Mazel_Alexandre_027_grey.jpg" );
            print getImageQuality( imageBuffer, nMethod = nMethod );
    if( False ):
        print( "\n* Testing image quality change if image is blur or not" );
        for nMethod in range( 4 ):
            print( "-- nMethod: %d" % nMethod );
            print( "- blur:" );
            imageBuffer = cv.LoadImage( strMyAppuDataPath + "images_to_analyse/0011_Mazel_Alexandre_053_blur.jpg" );
            print getImageQuality( imageBuffer, nMethod = nMethod );
            imageBuffer = cv.LoadImage( strMyAppuDataPath + "images_to_analyse/0011_Mazel_Alexandre_054_blur.jpg" );
            print getImageQuality( imageBuffer, nMethod = nMethod );
            imageBuffer = cv.LoadImage( strMyAppuDataPath + "images_to_analyse/0011_Mazel_Alexandre_058_a_bit_blur.jpg" );
            print getImageQuality( imageBuffer, nMethod = nMethod );
            print( "- not blur:" );
            imageBuffer = cv.LoadImage( strMyAppuDataPath + "images_to_analyse/0011_Mazel_Alexandre_046.jpg" );
            print getImageQuality( imageBuffer, nMethod = nMethod );
            imageBuffer = cv.LoadImage( strMyAppuDataPath + "images_to_analyse/0011_Mazel_Alexandre_055.jpg" );
            print getImageQuality( imageBuffer, nMethod = nMethod );
            imageBuffer = cv.LoadImage( strMyAppuDataPath + "images_to_analyse/0011_Mazel_Alexandre_027.jpg" );
            print getImageQuality( imageBuffer, nMethod = nMethod );
    if( False ): # testing getCroppedImages()
        if ( getCroppedImages('/home/sebastien/Pictures/test/lulu.jpg', [[50, 50, 50, 50], [100, 50, 50, 50], [[50, 100, 75, 25], 'myId', 3], [[100, 100, 25, 100], 'me', 45], [0,0,200,100]]) ):
            print "success, check your folder /home/sebastien/Pictures/test/lulu.jpg"
    if( False ):
        findColoredMarks_test();
    if( False ):
        findColoredInterest_test();
    if( True ):
        detectGreenLine_test();
# autoTest- end



if( __name__ == "__main__" ):
    autoTest();
    #~ findColoredMarks_test();
    # findColoredInterest_test();
    #~ stereo_findNearestPoint_test();
    #~ compareObject_test();
    #~ findColoredMarks2_test();
    #~ findText_test();
    #~ findSquaredLogo_test();
    #~ autotest_convertToAscii();
    #autotest_detectLine();
    #autotest_detectChessboard()
    #~ autotest_cameraCalibration()
    pass

# numpy.std( [[13,15,11],[3,5,1]] ) == numpy.std( [13,15,11,3,5,1] )
#~ std = numpy.std( [[13,15,11],[3,5,1]], 0 ); # => ok
#~ elems = [ [ [607.0, 253.0], [607.0, 290.0], [642.0, 291.0], [643.0, 253.0] ], [ [607.0, 253.0], [607.0, 292.0], [642.0, 291.0], [643.0, 254.0] ] ];
#~ std = numpy.std( elems, 0 );
#~ print( "std: %s" % str(std) );


#~ print numpy.mean( [[ 0.55551215,  0.33071891],
 #~ [ 0.60917465 , 0.52663436],
 #~ [ 0.48412292 , 0.48412292],
 #~ [ 0.33071891 , 0.59947894]], 0 );


#~ a = [ [1,2,3,2], [12,20,10,20], [1,2,5,1] ];
#~ aMaxL = numpy.argmax(a, axis=1 );
#~ print "max from Left:" + str(aMaxL);
#~ maxR = numpy.argmax(a, axis=1 );
#~ print "max from Right:" + str(maxR); # doesn't works!

#~ occurences = numpy.where(a == numpy.max(a, axis=1))
#~ print occurences


