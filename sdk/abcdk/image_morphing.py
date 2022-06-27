# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Image processing tools : morphing
# @author lgeorge
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

import numpy as np
import cv2
import numeric

import arraytools
import filetools

def doMorph(aImgA=np.zeros(0), aFeatureImgA=None, aImgB=np.zeros(0), aFeatureImgB=None, aRatioList = [0.25, 0.5, 0.75]):
    """
    Generates a morphing images sequence

    Parameters:
        aImgA - start image (numpy array)
        aFeatureImgA - features points in images A (the more the numbers of point, the better the result) (it's a list of points, each point as a 2D-tuples, exprimed in image pixel)
        aImgB - end image (numpy array)
        aFeatureImgB - features points in image B (sames numbers and same order as features in aFeatureImgA)
        aRatioList - list of intermediate images to generate (ratio between 0 and 1)

    Returns:
        A list of images that show the morphing transformation, one for each ratio in aRatioList
        (image correspond to transformation from imgA to imgB)

    Raises:
        ImagesSizeDifferError - raised if the two image does not have the same image size
    """
    if (aImgA.shape != aImgB.shape):
        raise ImagesSizeDifferError(aImgA.shape, aImgB.shape)

    aResImagesSequence = []
    for num, percentage in enumerate(aRatioList):
        aResFromA = _doMorph(aImgA, aFeatureImgA, aFeatureImgB, rPercentageBarycentre=percentage)
        aResFromB = _doMorph(aImgB, aFeatureImgB, aFeatureImgA, rPercentageBarycentre=1-percentage)
        aRes = cv2.addWeighted(aResFromA, 1-percentage, aResFromB, percentage, gamma=0)
        aResImagesSequence.append(aRes)
    return aResImagesSequence

class ImagesSizeDifferError(Exception):
    def __init__(self, *args):
        self.args = zip(args)

def getFaceImageFeature(aImg):
    raise NotImplementedError()


def _resortListInDict(aTriangles=[], aFeaturesPoints=[]):
    aOrderedTriangleMeshImgA = dict()
    for aTrianglePts in aTriangles:
        index = [(aFeaturesPoints).index(list(x)) for x in aTrianglePts]
        ordered = np.argsort(index)
        index_sorted = sorted(index)
        aOrderedTriangleMeshImgA[tuple(index_sorted)] = [aTrianglePts[ordered[0]], aTrianglePts[ordered[1]], aTrianglePts[ordered[2]]]  # we reordered the triangle points
    return aOrderedTriangleMeshImgA

def _doMorph(aImgA=None, aFeaturesPointsImgA=None, aFeaturesPointsImgB=None, rPercentageBarycentre=0.5):
    if rPercentageBarycentre == 0:
        return np.array(aImgA, dtype=np.float)
    aFeaturesPointsImgFinal = [( (1-rPercentageBarycentre) * np.array(aPtA) + (rPercentageBarycentre) * np.array(aPtB)).tolist() for aPtA, aPtB in zip(aFeaturesPointsImgA, aFeaturesPointsImgB)]
    aFeaturesPointsImgMiddle = [( (0.5) * np.array(aPtA) + (0.5) * np.array(aPtB)).tolist() for aPtA, aPtB in zip(aFeaturesPointsImgA, aFeaturesPointsImgFinal)]
    print aFeaturesPointsImgMiddle
    print aFeaturesPointsImgFinal
    print aFeaturesPointsImgA
    print('----')
    aBorderPoints = [[0,0], [aImgA.shape[0], 0], [0, aImgA.shape[1]], [aImgA.shape[0], aImgA.shape[1]]]
    aFeaturesMiddle =  _computeFeaturesPoints(aFeaturesPointsImgMiddle, aBorderPoints)
    aFeaturesA = _computeFeaturesPoints(aFeaturesPointsImgA, aBorderPoints)
    aFeaturesFinal =  _computeFeaturesPoints(aFeaturesPointsImgFinal, aBorderPoints)


    aTriangleMeshInFeaturesPointsIndex = getTrianglesMeshIndex(aFeaturesMiddle)
    aTriangleMeshImgA = [[ (aFeaturesA)[aVertexIndex] for aVertexIndex in triangle] for triangle in aTriangleMeshInFeaturesPointsIndex]
    aTriangleMeshImgFinal = [[ (aFeaturesFinal)[aVertexIndex] for aVertexIndex in triangle] for triangle in aTriangleMeshInFeaturesPointsIndex]

    bDebug=False
    if bDebug:
        aTriangleMeshImgMiddle = [[ (aFeaturesMiddle)[aVertexIndex] for aVertexIndex in triangle] for triangle in aTriangleMeshInFeaturesPointsIndex]
        import pylab
        pylab.figure()
        ax1 = pylab.gca()
        ax1.set_ylim(ax1.get_ylim()[::-1])
        pylab.figure()
        ax2 = pylab.gca()
        ax2.set_ylim(ax2.get_ylim()[::-1])
        pylab.figure()
        ax3 = pylab.gca()
        ax3.set_ylim(ax3.get_ylim()[::-1])
        for triangleA,triangleB, triangleMidle in zip(aTriangleMeshImgA, aTriangleMeshImgFinal, aTriangleMeshImgMiddle):
            color=np.random.rand(3,1)
            polygonA = pylab.Polygon(triangleA, facecolor=color)  ## seeems to be inverted compared to opencv
            ax1.add_patch(polygonA)
            polygonB = pylab.Polygon(triangleB, facecolor=color)  ## seeems to be inverted compared to opencv
            ax2.add_patch(polygonB)
            polygonC = pylab.Polygon(triangleMidle, facecolor=color)
            ax3.add_patch(polygonC)
        pylab.show()

    warpAToMiddle = _warp(aImgA, aTriangleMeshImgA, aTriangleMeshImgFinal)
    #warpBToMiddle = _warp(aIMgB, aTriangleMeshImgB, aTriangleMeshImgMiddle)
    return warpAToMiddle

def _computeFeaturesPoints(aFeaturesPoints, aBorderPoints, nRotation=0):
    """ create a list of points wich is aFeaturesPoints + aBorderPoints but with aBorderPoints ordered based on distance to first point in a FeaturesPoints """
    return  aFeaturesPoints + aBorderPoints


def _warp(aImageSrc, aTriangleMeshSrc, aTriangleMeshDest):
    rows, cols = aImageSrc.shape[:2]
    aRes = np.zeros(aImageSrc.shape)
    for aTriangleA, aTriangleB in zip(aTriangleMeshSrc, aTriangleMeshDest):
        aTransform = cv2.getAffineTransform(np.float32(aTriangleA), np.float32(aTriangleB))
        print aTransform
        maskB = np.zeros(aImageSrc.shape, dtype=np.uint8)
        white = (255, 255, 255)
        #cv2.fillPoly(maskA, [np.int32(aTriangleA)], white)
        cv2.fillPoly(maskB, [np.int32(aTriangleB)], white)  # on met de blanc dans le mask..
        aWarpRes = cv2.warpAffine(aImageSrc, aTransform, (cols,rows), borderMode=cv2.BORDER_CONSTANT) #  BORDER_TRANSPARENT)  # sad we do the transform on all points..
        numpymask = np.where(maskB==white)
        aRes[numpymask] = aWarpRes[numpymask]
    return aRes

def getTrianglesMeshIndex(aPoints):
    aBoundingRect = numeric.boundingRect(aPoints)
    print("START")
    #print aBoundingRect
    aMap = cv2.Subdiv2D(aBoundingRect)
    for pt in aPoints:
        aMap.insert(tuple(pt))
    # opencv provide no documentation but c++ code show that the return of getTriangleList is : [(a.x, a.y, b.x, b.y, c.x, c.y) ... (a.x, a.y, ...)]
    aTriangleList = aMap.getTriangleList()
    aTriangleList = [[(ax,ay),(bx, by), (cx,cy)] for ax,ay, bx,by,cx,cy in aTriangleList]  # we convert it to [[ptA_1, ptB_1, ptC_1], .... [ptA_n, ptB_n, ptC_n] ]
    #aTriangleList = [[(ay,ax),(by, bx), (cy,cx)] for ax,ay, bx,by,cx,cy in aTriangleList]  # we convert it to [[ptA_1, ptB_1, ptC_1], .... [ptA_n, ptB_n, ptC_n] ]

    # we filter out triangle outside of image boundingRect defined by aPointsBounding rect for now
    aTriangleListRes = []
    for aTrianglePoints in aTriangleList:
        for aPoint in aTrianglePoints:
            if ( (abs(aPoint[0]) > aBoundingRect[2]) or (abs(aPoint[1]) > aBoundingRect[3] ) ):  # triangle outside of boundingRect
                break
        #        pass
        else:
            aTriangleListRes.append(aTrianglePoints)

    bDebug = False
    if bDebug:
        import pylab
        pylab.figure()
        for aTrianglePoints in aTriangleListRes:
            polygon = pylab.Polygon(aTrianglePoints, facecolor='red')  ## seeems to be inverted compared to opencv
            pylab.gca().add_patch(polygon)
        pylab.show()
    aTriangleListResIndex = []
    for aTrianglePoints in aTriangleListRes:
        aVertexesIndex = []
        for aVertex in aTrianglePoints:
            try:
                aVertexIndexInaPoint = (aPoints.index(list(aVertex)))
            except ValueError:  # the point has not been found in the list it's due to approxmation in opencv ?
                # we try to find the closest point in this case
                originalPoint = aVertex
                approximatePointIndex = np.argmin(np.abs((np.array(aPoints) - (aVertex))), axis=0)
                approximationPoint = aPoints[approximatePointIndex[0]]
                print("point not found in list point %s.. using approximation %s" % (originalPoint, approximationPoint))
                aVertexIndexInaPoint = approximatePointIndex[0]
            aVertexesIndex.append(aVertexIndexInaPoint)
        aTriangleListResIndex.append(aVertexesIndex)

    #import IPython
    #IPython.embed()

    return aTriangleListResIndex



#def _imageMorphing
def test_noMorphletter():
    aImgA = cv2.imread('./data/images/F.png')#, cv2.CV_LOAD_IMAGE_GRAYSCALE)#, cv2.CV_LOAD_IMAGE_COLOR)
    aImgB = cv2.imread('./data/images/F_rotated_translated.png')#, cv2.CV_LOAD_IMAGE_GRAYSCALE) #, cv2.CV_LOAD_IMAGE_COLOR )
    aCornersLetterF = [[14, 15], [33, 15], [33, 19], [20, 19], [20, 27], [32,27], [32, 30],[20, 30], [20, 43], [14, 43]]
    aCornersLetterFRotated = [[53,28], [53, 47], [49, 47], [49, 34], [42,34], [42, 46], [38, 46], [38, 34], [26, 34], [26, 28]]
    aRes = _doMorph(aImgA, aCornersLetterF, aCornersLetterFRotated, rPercentageBarycentre=0)
    cv2.imshow('nomorph', aRes)
    cv2.waitKey()

def test_noMorphletterBack():
    aImgA = cv2.imread('./data/images/F.png')#, cv2.CV_LOAD_IMAGE_GRAYSCALE)#, cv2.CV_LOAD_IMAGE_COLOR)
    aImgB = cv2.imread('./data/images/F_rotated_translated.png')#, cv2.CV_LOAD_IMAGE_GRAYSCALE) #, cv2.CV_LOAD_IMAGE_COLOR )
    aCornersLetterF = [[14, 15], [33, 15], [33, 19], [20, 19], [20, 27], [32,27], [32, 30],[20, 30], [20, 43], [14, 43]]
    aCornersLetterFRotated = [[53,28], [53, 47], [49, 47], [49, 34], [42,34], [42, 46], [38, 46], [38, 34], [26, 34], [26, 28]]
    aRes = _doMorph(aImgB, aCornersLetterFRotated, aCornersLetterF, rPercentageBarycentre=0)
    cv2.imshow('nomorphBack', aRes)
    cv2.waitKey()

def test_doMorph():
    aImgA = cv2.imread('./data/images/F.png')#, cv2.CV_LOAD_IMAGE_GRAYSCALE)#, cv2.CV_LOAD_IMAGE_COLOR)
    aImgB = cv2.imread('./data/images/F_rotated_translated.png')#, cv2.CV_LOAD_IMAGE_GRAYSCALE) #, cv2.CV_LOAD_IMAGE_COLOR )
    aCornersLetterF = [[14, 15], [33, 15], [33, 19], [20, 19], [20, 27], [32,27], [32, 30],[20, 30], [20, 43], [14, 43]]
    aCornersLetterFRotated = [[53,28], [53, 47], [49, 47], [49, 34], [42,34], [42, 46], [38, 46], [38, 34], [26, 34], [26, 28]]
    doMorph(aImgA, aCornersLetterF, aImgB, aCornersLetterFRotated)

def test_morph_letter():
    aImgA = cv2.imread('./data/images/F.png')#, cv2.CV_LOAD_IMAGE_GRAYSCALE)#, cv2.CV_LOAD_IMAGE_COLOR)
    aImgB = cv2.imread('./data/images/F_rotated_translated.png')#, cv2.CV_LOAD_IMAGE_GRAYSCALE) #, cv2.CV_LOAD_IMAGE_COLOR )
    cv2.imwrite('originalStart.jpg', aImgA)
    cv2.imwrite('originalEnd.jpg', aImgB)

    aCornersLetterF = [[14, 15], [33, 15], [33, 19], [20, 19], [20, 27], [32,27], [32, 30],[20, 30], [20, 43], [14, 43]]
    aCornersLetterFRotated = [[53,28], [53, 47], [49, 47], [49, 34], [42,34], [42, 46], [38, 46], [38, 34], [26, 34], [26, 28]]

    #_doMorph(aImgA, aImgA, aCornersLetterF, aCornersLetterF)
    #_doMorph(aImgA, aImgA, aCornersLetterF, aCornersLetterFRotated)

    for num, percentage in enumerate([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]):
        aResFromA = _doMorph(aImgA, aCornersLetterF, aCornersLetterFRotated, rPercentageBarycentre=percentage)
        aResFromB = _doMorph(aImgB, aCornersLetterFRotated, aCornersLetterF, rPercentageBarycentre=1-percentage)
        #aRes = (percentage * aResFromA + (1-percentage) * aResFromB)/2.0
        print aResFromA.dtype
        print aResFromB.dtype
        aRes = cv2.addWeighted(aResFromA, 1-percentage, aResFromB, percentage, gamma=0)
        #aRes = aResFromA
        print("num is %s" % num)
        cv2.imshow('fromB', aResFromB)
        cv2.imshow('fromA', aResFromA)
        cv2.imshow('mix', aRes)
        cv2.waitKey()
        cv2.imwrite('result%s.png' % num, aRes)

    #for x,y in aCornersLetterF:
    #    aImgA[y,x] = [0, 255, 0]
    #
    #for x,y in aCornersLetterFRotated:
    #    aImgB[y,x] = [0, 255, 0]
    #
    #import pylab
    #pylab.imshow(aImgA)
    #pylab.show()
    #cv2.imshow('imgA', aImgA)
    #cv2.imshow('imgB', aImgB)
    #keyPressed = None
    #while keyPressed != 'q':
    #    keyPressed = chr(cv2.waitKey() & 0xFF)
    #    print("keyPressed is %s" % keyPressed)
    #print("exit imgshow")

def test_fakeImage():
    aImgA = np.ones((1000,1000))
    aImgB = np.ones((1000,1000))
    doMorph(aImgA, [],  aImgB, [])

def test_wrongImageSize():
    aImgA = np.ones((10,10))
    aImgB = np.ones((20,10))
    try:
        doMorph(aImgA, aImgB)
    except ImagesSizeDifferError:
        return True
    raise AssertionError()  # wrong image size test fail
    

##########################################################
# gros bordel a nettoyer a partir de la!
##########################################################
import image_morphing
import time
import cv2
import pathtools
    
def cropImgToShape( img, shape, aListPoint = [], rMarginCoef = 1. ):
    """
    crop the image to the face
    """         
    w = img.shape[1];
    h = img.shape[0];
    center = arraytools.convertAngleToImagePixels(shape[0],shape[1],w,h)
    print( "cropImgToShape: center: %s" % str(center) );
    size = arraytools.convertSizeToImagePixels(shape[2],shape[3],w,h)
    print( "cropImgToShape: size: %s" % str(size) );
    size = (size[0], size[1]*2); # more nice when cropping a face
    size = ( int( size[0] *rMarginCoef), int(size[1]*rMarginCoef) );            
    left = (center[0]-size[0]/2, center[1]-size[1]/2 );
    crop_img = img[left[1]:left[1]+size[1], left[0]:left[0]+size[0]];
    listPointOut = [];
    for pt in aListPoint:
        newx = pt[0]-left[0]; # )/(w/size[0]);
        newy = pt[1]-left[1];
        listPointOut.append( (newx, newy) );
    return crop_img, listPointOut;
    
def addPointForBorder( listpoint, imgShape, rExtraPointPosition = 0. ):
    """
    NB: shape are [y,x] and origin is [x,y] !
    - rExtraPointPosition: put the point a bit into the image instead of in the border
    """
    incx = int(imgShape[1]*rExtraPointPosition);
    incy = int(imgShape[0]*rExtraPointPosition);
    origin = [incx, incy];
    listpoint.append( (origin[0],origin[1]) );
    listpoint.append( (imgShape[1]-1-incx, origin[1]) );
    listpoint.append( (imgShape[1]-1-incx,imgShape[0]-1-incy) );
    listpoint.append( (origin[0], imgShape[0]-1-incy) );
    return listpoint;
    
def generateMorphData( strHumanFilename, aFacePosHuman, aListPointHuman, strRefFilename, aFacePosRef, aListPointRef ):
    """
    return the list of the created file!
    """
    astrFilenameOut = [];
    print( "INF: generateMorphData: '%s' <=> '%s'" % (strHumanFilename,strRefFilename) );
    print( "INF: generateMorphData: aFacePosHuman: %s" % aFacePosHuman );
    print( "INF: generateMorphData: aListPointHuman: %s" % aListPointHuman );
    print( "INF: generateMorphData: aFacePosRef: %s" % aFacePosRef );
    print( "INF: generateMorphData: aListPointRef: %s" % aListPointRef );
    
    timeBegin = time.time();
    imH = cv2.imread( strHumanFilename );
    assert( imH != None );
    
    imRef = cv2.imread( strRefFilename );    
    assert( imRef != None );
    imRef = cv2.cvtColor(imRef, cv2.COLOR_BGR2GRAY);
    imRef = cv2.cvtColor(imRef, cv2.COLOR_GRAY2BGR);
    aListPointHuman = arraytools.convertTupleListAngleToImagePixels( aListPointHuman, imH.shape[1], imH.shape[0] );
    aListPointRef = arraytools.convertTupleListAngleToImagePixels( aListPointRef, imRef.shape[1], imRef.shape[0] );
    
    # here assume both faces are centered and convert all point to each good point in pixels, the two image must remains of the same size at the end
    rMarginCoef = 1.1;
    imH, aListPointHuman = cropImgToShape( imH, aFacePosHuman, aListPointHuman, rMarginCoef );
    imRef, aListPointRef = cropImgToShape( imRef, aFacePosRef, aListPointRef, rMarginCoef );
    fx = imRef.shape[1] / float(imH.shape[1]);
    fy = imRef.shape[0] / float(imH.shape[0]);
    print( "fx: %s" % fx );
    print( "fy: %s" % fy );            
    
    imH = cv2.resize(imH, (imRef.shape[1], imRef.shape[0]));
    for i in range(len(aListPointHuman) ):
        aListPointHuman[i] = (int(aListPointHuman[i][0]*fx), int(aListPointHuman[i][1]*fy) );
    
    
    aListPointHuman = addPointForBorder( aListPointHuman, imH.shape );
    aListPointRef = addPointForBorder( aListPointRef, imRef.shape );
    
    rExtraPointPosition = 0.1;
    aListPointHuman = addPointForBorder( aListPointHuman, imH.shape, rExtraPointPosition );
    aListPointRef = addPointForBorder( aListPointRef, imRef.shape, rExtraPointPosition );
    
    # debug: add point for each point
    if( 1 ):
        for pt in aListPointHuman:
            cv2.circle( imH, pt, 1, (255,0,0) );
        for pt in aListPointRef:
            cv2.circle( imRef, pt, 1, (0,255,0) );
    
    arAdvancing = [x/10. for x in range(11)]
    #~ arAdvancing = [0.0, 0.25, 0.5, 0.75, 1.0];
    #~ arAdvancing = [0.0, 0.5, 1.0];    
    #~ arAdvancing = [0.,1.];
    aImgRes = image_morphing.doMorph( imH, aListPointHuman, imRef, aListPointRef, arAdvancing );
    print( "len img: %s" % len( aImgRes ) );
    print( "len img: nbrlayer: %s" % aImgRes[0].shape[2] );
    nCpt = 0;         
    
    for img in aImgRes:
        strDest = pathtools.getVolatilePath()
        if( "/tmp" in strDest ):
            strDest += filetools.getFilenameFromTime() + "_";
        strDest += ( "morph_img_%02d.jpg" % nCpt );
        
        astrFilenameOut.append( strDest );
        print( "saving to %s" % strDest );
        cv2.imwrite( strDest, img  );
        if( 0 ):
            cv2.imshow("Original", img)
            key = cv2.waitKey(1000)
        nCpt += 1;
    rDuration = time.time() - timeBegin;
    print( "INF: generateMorphData: end, duration: %5.2fs" % rDuration );
    
    if( False ):
        # resize for video
        for i in range( len(aImgRes) ):
            aImgRes[i] = cv2.resize( aImgRes[i], (640,480) );
            cv2.circle( aImgRes[i], (40*(i+1),40), 10, (255,255,0) );                    
            
        
        # nothing seem to work in opencv2 ?
        #~ fourcc = -1;
        #~ codec = cv2.cv.CV_FOURCC('M','J','P','G');
        #~ codec = cv2.cv.CV_FOURCC('D','I','V','X')
        codec = cv2.cv.CV_FOURCC('D','I','V','3')
        #~ codec = cv2.cv.CV_FOURCC('i','Y','U', 'V')
        
        print( "video codec: %s" % str( codec ) );
        videoFile = cv2.VideoWriter();
        nFps = 1;
        aImageSize = (aImgRes[0].shape[1],aImgRes[0].shape[0]);
        print( "video aImageSize: %s" % str( aImageSize ) );
        videoFile.open( pathtools.getVolatilePath() + "morph.avi", codec, nFps, aImageSize, 1 );
        print( "cv2.VideoWriter.isOpened(): %s" % videoFile.isOpened() );
        assert( videoFile.isOpened() );
        for img in aImgRes:
            videoFile.write(img);
            if( 0 ):
                cv2.imshow("Original", img)
                key = cv2.waitKey(400)
            
    if( False ):
        import images2gif
        from PIL import Image
        images2gif.writeGif( pathtools.getVolatilePath() + "morph.gif", aImgRes, 3, dither=0)
        """
          File "C:\work\Dev\git\appu_shared\sdk\abcdk\images2gif.py", line 438, in writeGifToFile
            fp.write(header.encode('utf-8'))
            UnicodeDecodeError: 'ascii' codec can't decode byte 0xd1 in position 6: ordinal not in range(128)
            
            je pense que j'ai des images en numpy au lieu de pil et donc bam...
        """
    return astrFilenameOut;
# generateMorphData - end

##########################################################
def autotest():
    test_doMorph()
    #test_noMorphletterBack()
    #test_noMorphletter()
    #test_wrongImageSize()
#    test_morph_letter()
    #test_fakeImage()
    pass

if __name__ == "__main__":
    autotest()
