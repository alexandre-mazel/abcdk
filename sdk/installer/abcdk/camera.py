# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Camera tools
# @author The usage team - Living Labs
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Camera tools: some constants useful to use camera modules, a camera object to help handling camera..."""

print( "importing abcdk.camera" );

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

import numpy as np
import traceback
import debug
import filetools
import mutex

import ctypes

# old constants
class Constantes:
    def __init__( self ):
        # Image Format
        self.VGA = 2;                # 640*480
        self.QVGA =1;               # 320*240
        self.QQVGA = 0;            # 160*120
        self.k4VGA = 3;             # 1280*960

        # Standard Id
        self.BrightnessID       = 0;
        self.ContrastID         = 1;
        self.SaturationID       = 2;
        self.SID       = 2;
        self.HueID              = 3;
        self.RedChromaID        = 4;
        self.BlueChromaID       = 5;
        self.GainID             = 6;
        self.HFlipID            = 7;
        self.VFlipID            = 8;
        self.LensXID            = 9;
        self.LensYID            = 10;
        self.AutoExpositionID   = 11;
        self.AutoWhiteBalanceID = 12;
        self.AutoGainID         = 13;
        self.FormatID           = 14;
        self.FrameRateID        = 15;
        self.BufferSizeID       = 16;
        self.ExposureID         = 17;
        self.SelectID           = 18;
        self.SetDefaultParamsID = 19;
        self.ColorSpaceID       = 20;
        self.ExposureCorrectionID = 21;
        self.CameraAecAlgorithmID     = 22;
        self.CameraFastSwitchID       = 23;
        self.CameraSharpnessID        = 24;



class FOV_ctypes(ctypes.Structure):
    _fields_ = [
        ("leftAngle", ctypes.c_float),
        ("topAngle", ctypes.c_float),
        ("rightAngle", ctypes.c_float),
        ("bottomAngle", ctypes.c_float),
        ]

class ALImage_ctypes(ctypes.Structure):
    _fields_ = [
        ("fWidth", ctypes.c_int),  #  /// width of the image
        ("fHeight", ctypes.c_int), #  /// height of the image
        ("fNbLayers", ctypes.c_int), # /// number of layers of the image
        ("fColorSpace", ctypes.c_int), # /// color space of the image
        ("fTimeStamp", ctypes.c_longlong), #  /// Time in microsecond when the image was captured
        ("fData", ctypes.c_uint), # /// pointer to the image data  #  unsigned char* fData -> pointeur = uint
        ("fCameraId", ctypes.c_char), # #  /// ID of the camera that shot the picture
        ("fAllocatedSize", ctypes.c_int ), #  /// Size of memory allocation
        ("fMaxResolution", ctypes.c_int ), #  /// Maximum resolution accepted in the reserved memory
        ("fMaxNumberOfLayers", ctypes.c_int ), #  /// Maximum number of layers accepted in the reserved memory
        ("fDataAreExternal", ctypes.c_bool ), #  /// If false, data buffer was allocated while creating instance. If true, image points to an external data buffer.
        ("FOV", FOV_ctypes), # /// Manage the field of view of the image that changes with camera model and cropping

        ## WARNING (lgeorge - 11/04/2014): Je ne sais pas comment faire pour avoir un std::vector en ctypes.. resultat je ne le met pas pas pour l'instant
        #  std::vector<ROI> fROIs;
        #  bool fROIEnabled;
        ]
#end of ALImage_ctypes

class ALImage(object):
    def __init__(self):
        #self.aCtypeStructure = ALImage_ctypes()  ## everything is set to 0 / null
        self.nWidth = None
        self.nHeight = None
        self.nNbLayers = None
        self.nColorSpace = None
        self.rTimeStamp = None # timestamp in seconds (similar to time.time())
        self.nCameraID = None # (kTop=0, kBottom=1).
        self.aData = None  # array of size height * width * nblayers containing image data.
        self.ownedDataCopy = None# owned copy of data
        self.aCtypeStructure = None

    def loadFromALMemory(self, aALValueList):
        self.nWidth = int(aALValueList[0])
        self.nHeight = int(aALValueList[1])
        self.nNbLayers = int(aALValueList[2])
        self.nColorSpace = int(aALValueList[3])
        self.rTimeStamp = float(aALValueList[4]) + float(aALValueList[5])/(1000.0*1000.0)
        self.nCameraID = int(aALValueList[7])
        self.aData = (np.reshape(np.frombuffer(aALValueList[6], dtype='%iuint8' % self.nNbLayers), (self.nHeight, self.nWidth, self.nNbLayers)))
        self.ownedDataCopy = self.aData ## here we already OWNDATA

    def loadFromMemory(self, nMemoryPointer):
        self.aCtypeStructure = ALImage_ctypes.from_address(nMemoryPointer)
        aCtypeStructure = self.aCtypeStructure
        self.nWidth = aCtypeStructure.fWidth
        self.nHeight = aCtypeStructure.fHeight
        self.nNbLayers = aCtypeStructure.fNbLayers
        self.nColorSpace = int(aCtypeStructure.fColorSpace)
        self.rTimeStamp = float(aCtypeStructure.fTimeStamp)/(1000.0*1000.0) # TODO
        #if aCtypeStructure.fCameraId != '':
        #    self.nCameraID = int(aCtypeStructure.fCameraId)
        self._updateData(aCtypeStructure)
        #self.ownedDataCopy = None ## already done in _updateData

    def _updateData(self, aCtypeStructure):
        """ return a numpy array to the data well formated (warning no copy is
            done so don't release the image or use getCopyData
            # NO COPY IS DONE !@
        """
        #print("loading array with (hxWxNbLayers = %sx%sx%s)" % (self.nHeight, self.nWidth, self.nNbLayers))
        self.aData = np.ctypeslib.as_array((ctypes.c_ubyte*self.nHeight*self.nWidth*self.nNbLayers).from_address(aCtypeStructure.fData))    # ubyte car on a des unsigned char
        #print("array not reshape is %s " % aData)
        self.aData.shape =  (self.nHeight, self.nWidth, self.nNbLayers)  # reshape in place
        self.ownedDataCopy = None
        #print("array is %s" % self.aData)
        ## TODO !! WARNING // ! NOT OPTIMAL
        #self.getDataOwnedCopy()  # juste pour tester..  ## bordel si on ne le fait pas maintenant on perd le aData.. il faudrait changer le flag.. pour etre certain que le ramasseur de miette ne le detruise pas.. ou juste lui dire.. non mais attend c'est pas owned ca a voir.. il y a un truc pour l'instant on laisse le updateData..
        ## TODO : quand on sort de cette fonction self.aData = None !!! Why the fuck !


    def getDataOwnedCopy(self):
        """
        Copy data to ownedData if neccessary, and return it
        """
        #print("aData in getDataOwnedCopy is %s" % self.aData)
        if self.aData is not None:
        #    print("Doing copy ?")
            if (self.aData.flags['OWNDATA']):
        #       print("No copy required")
                self.ownedDataCopy = self.aData  #not required.. but just in case
            else:
        #       print("Copying data.."),
                rStartTime = time.time()
                aCopyData = np.copy(self.aData)
                rDuration = rStartTime - time.time()
        #       print(".Done copying (duration: %s)" % rDuration)
                self.ownedDataCopy = aCopyData


        self.data = self.ownedDataCopy  ## no more reference to memory
        #print("owned data is %s" % self.ownedDataCopy)
        return self.ownedDataCopy

#ALImage = collections.namedtuple('ALImage_v001', ['
#class ALImage:
#    def __init__(s

class Camera:
    def __init__ ( self ):
        self.kQQVGA = 0;            # 160*120
        self.kQVGA =1;               # 320*240
        self.kVGA = 2;                # 640*480
        self.k4VGA = 3;             # 1280*960

        self.kRGB = 11;
        self.kBGR = 13;  ## RRGGBB ?? et pas BBGGRR .. a bien regarder

        self.kCameraGainID = 6;

        self.kCameraAutoExpositionID = 11;
        self.kCameraAutoWhiteBalanceID = 12;
        self.kCameraExposureID = 17;
        self.kCameraSelectID = 18;
        self.kCameraAecAlgorithmID     = 22;

        self.kCameraWhiteBalanceID = 33;


        self.nMaxGain = 255;
        self.nMaxExpo = self.nMaxExposure = 512;

        self.nManualExposure_nMode = -1;
        self.nManualExposure_nExposure = 0;
        self.nManualExposure_nGain = 0;
        self.bManualExposure_bMustStop = False;

        self.dictOpenedSubscriber = dict();  # sometimes we don't unsubscribe for speed purpose, so we store a {"unique_opening_string" => "vision device id"} for each suscribing
        self.dictImageLastTimeStamp = dict() # we store {"unique_opening_string" => last_timeStamp
        self.dictTimestampLastGetImageCall = dict()
        # optic configuration
        #self.cameraMatrixRef640 = np.array( [[ 533.48550633,    0.        ,  298.20393548], [   0.        ,  530.006434  ,  258.74421405], [   0.        ,    0.        ,    1.        ]] );

        #self.cameraMatrixRef640 = np.array( [[538.46685548 ,    0.        ,  309.00283277], [   0.        ,  534.65721038 ,  250.79608012], [   0.        ,    0.        ,    1.        ]] );
        #self.cameraMatrixRef1080 = np.array( [[  1.10369096e+03,   0.0,   6.54850913e+02], [  0.0,   1.10323382e+03 ,  4.94239401e+02], [  0.0,    0.0 ,  1.0]] )
        self.cameraMatrixRef1080 = np.array([[  1.10561144e+03 ,  0.00000000e+00 ,  6.42505603e+02], [  0.00000000e+00 ,  1.11245814e+03 ,  4.96053152e+02], [  0.00000000e+00 ,  0.00000000e+00 ,  1.00000000e+00]])



        self.aCameraMatrix = []; # intrinsics for each resolution
        for rScale in [ 0.125, 0.25, 0.5, 1.0 ]:
            self.aCameraMatrix.append( self.cameraMatrixRef1080 * rScale );         # scale ratio compared to 640x480, for example in 320x240 scale ratio = 0.5, in 1280x960 scale ration = 2 , calibration matrix has been computed based on 640x480 resolution
        #self.distorsionCoef = - np.array([[ -1.12257723e-01], [  5.35782365e-01], [  1.08637612e-03], [ -4.06574346e-03], [ -1.70570660e+00]])  # distorsion does not need to be scaled

        # old
        #self.distorsionCoef =  -np.array([[ -1.12257723e-01], [  5.35782365e-01], [  1.08637612e-03], [ -4.06574346e-03], [ -1.70570660e+00]])  # distorsion does not need to be scaled

        #self.distorsionCoef =  -np.array([[ -1.12257723e-01], [  5.35782365e-01], [  1.08637612e-03], [ -4.06574346e-03], [ -1.70570660e+00]])  # distorsion does not need to be scaled
        #self.distorsionCoef =  -np.array([[ -1.12257723e-01], [  5.35782365e-01], [  1.08637612e-03], [ -4.06574346e-03], [ -1.70570660e+00]])
        # new :
        #self.distorsionCoef = np.array([  [ -5.21462339e-02] , [  2.76655307e-02] , [ -1.56052912e-03] , [ -1.72784913e-03] , [  5.40969698e+00] , [  6.15701876e-02] , [ -2.22455576e-01] , [  6.49515514e+00]])
        #self.distorsionCoef = - np.array( [[-0.03667461] ,[ 0.66478952] ,[ 0.00185989] ,[ 0.00320262] ,[-1.34058444] ,[ 0.02394984] ,[ 0.73017674] ,[-1.60547494]] )
#        self.distorsionCoef = - np.array( [[-0.03667461] ,[ 0.66478952] ,[ 0.00185989] ,[ 0.00320262] ,[-1.34058444] ,[ 0.02394984] ,[ 0.73017674] ,[-1.60547494]] ) *  0
        self.distorsionCoef = np.array([[ -3.14724137e-03],[  3.09723474e-01],[  1.13771499e-03],[  5.07460018e-05],[  3.39670453e+00],[  6.74398801e-03],[  7.48274002e-01],[  2.14113693e+00]])

        #self.distorsionCoef = 0 * self.distorsionCoef

        self.strDebugPath = "/home/nao/abcdk_debug/camera/";
        self.bMustStop = False
        filetools.makedirsQuiet( self.strDebugPath );

        self.aSubsribersInUse = set() # list of subscriber currently in used, we shouldn't unsubscribe when the subscriber is in the list, we need to wait the image has been released before unsubscribing
        self.bUseLocalProxy = False  ## use getALImageremote by default
        
        self.mutexGetImageCV2 = mutex.mutex();
    # __init__ - end

    def getCurrentSettings( self ):
        """
        Return a string describing the current setting of the camera
        """
        import naoqitools # prevent cycling import
        avd = naoqitools.myGetProxy( "ALVideoDevice" );
        strOut = "Camera current settings:\n";

        strOut += "Active Camera: %s\n" % avd.getParam( self.kCameraSelectID );
        for nNumCamera in range( 2 ):
            strOut += "\n* Camera: %s\n" % nNumCamera;
            strOut += "AutoExpo: %s\n" % avd.getParameter( nNumCamera, self.kCameraAutoExpositionID );
            strOut += "Gain: %s\n" % avd.getParameter( nNumCamera, self.kCameraGainID );
            strOut += "Expo: %sms\n" % ( avd.getParameter( nNumCamera, self.kCameraExposureID ) / 2 );
            strOut += "AWB: %s\n" % avd.getParameter( nNumCamera, self.kCameraAutoWhiteBalanceID );
            strOut += "WB: %s\n" % avd.getParameter( nNumCamera, self.kCameraWhiteBalanceID );
        return strOut;
    # getCurrentSettings - end

    def setUseLocalProxy( self, bUseLocalProxy ):
        """
        Enables the direct access to the memory containing image, it's a bit ugly but so fast...
        """
        print( "WRN: abcdk.camera.setUseLocalProxy: trying to change UseLocalProxy from %s to %s" % (self.bUseLocalProxy, bUseLocalProxy ) );
        if( bUseLocalProxy ):
            import naoqitools
            if( naoqitools.isMethodExist( "ALVideoDevice", "getImageLocal2" ) ):
                self.bUseLocalProxy = bUseLocalProxy;
            else:
                print( "WRN: abcdk.camera.setUseLocalProxy: can't access directly to image in memory because the binded method 'getImageLocal2' doesn't exists in the video module." );

        else:
            self.bUseLocalProxy = bUseLocalProxy;
    # setUseLocalProxy - end


    def setAutoExposure( self ):
        import naoqitools # prevent cycling import
        self.bManualExposure_bMustStop = True;
        avd = naoqitools.myGetProxy( "ALVideoDevice" );
        avd.setParam( self.kCameraGainID, self.nMaxGain/2 );
        avd.setParam( self.kCameraExposureID, self.nMaxExpo/2 );
        avd.setParam( self.kCameraAutoExpositionID, 1 );

    def setManualExposure( self, nExposureTimeMs, nGain, nNumCamera = -1 ):
        """
        Set a camera to fixed exposure
        - nExposureTimeMs: yes it's really in millisec [0..256]
        - nGain: (no comments) [0..255]
        - nNumCamera: a specific camera num or current set (-1)
        """
        import naoqitools # prevent cycling import
        self.bManualExposure_bMustStop = True;
        avd = naoqitools.myGetProxy( "ALVideoDevice" );
        if( nNumCamera == -1 ):
            nNumCamera = avd.getParam( self.kCameraSelectID );
        avd.setParam( self.kCameraSelectID, nNumCamera );
        avd.setParam( self.kCameraAutoExpositionID, 0 );
        avd.setParam( self.kCameraGainID, nGain );
        avd.setParam( self.kCameraExposureID, nExposureTimeMs*2 );
    # setManualExposure - end


    def changeExposureMode( self, nMode = 0, nTargetLuminosity = 127 ):
        """
        change exposure settings using a specific politics
        - mode:
            - 0: normal (average)
            - 1: sport
            - 2: photo

        return: True if ok, or false if can't have the required setting
        """

        print( "INF: abcdk.camera.changeExposureMode( %d ), last: mode: %d, expo: %d, gain: %d" % ( nMode, self.nManualExposure_nMode, self.nManualExposure_nExposure, self.nManualExposure_nGain ) );

        import image
        import naoqitools # prevent cycling import

        self.bManualExposure_bMustStop = False;

        rLumMargin = 20;

        timeBegin = time.time();

        #~ # take a picture and change exposure
        #~ im = self.getImage();
        #~ rLum = image.getImageLuminosity( im, 1 );
        #~ print( "INF: abcdk.camera.changeExposureMode: current luminosity: %f" % rLum );

        avd = naoqitools.myGetProxy( "ALVideoDevice" );
        nNumCamera = avd.getParam( self.kCameraSelectID );



        # check useness
        if( self.nManualExposure_nMode == nMode ):
            nActualExpo = avd.getParam( self.kCameraExposureID );
            if( nActualExpo == self.nManualExposure_nExposure ):
                im = self.getImage();
                rLum = image.getImageLuminosity( im, 1 );
                if( abs( rLum - nTargetLuminosity ) < rLumMargin ):
                    print( "INF: abcdk.camera.changeExposureMode: finished time taken: %5.3fs (already set)" % (time.time() - timeBegin ) );
                    return True;
                # perhaps just a gain problem
                avd.setParam( self.kCameraGainID, self.nManualExposure_nGain );
                time.sleep( 1.2 );
                im = self.getImage();
                rLum = image.getImageLuminosity( im, 1 );
                if( abs( rLum - nTargetLuminosity ) < rLumMargin ):
                    print( "INF: abcdk.camera.changeExposureMode: finished time taken: %5.3fs (already set but gain was wrong)" % (time.time() - timeBegin ) );
                    return True;
            # else, retry the full package

        if( self.bManualExposure_bMustStop ):
            return False;

        # if( abs( rLum - nTargetLuminosity ) > 40 or avd.getParam( kCameraAutoExpositionID) == 0 ):
        if( True ): # always update
            # change exposition or it was in automatic mode

            nActualGain = avd.getParam( self.kCameraGainID );
            nActualExpo = avd.getParam( self.kCameraExposureID );

            if( nMode == 0 ):
                # average
                nNewExpo = 250;
            elif( nMode == 1 ):
                nNewExpo = (1000/100)*5/2; # 1/100th is not fast for a sport photo ! # Exposure (time in ms = (value * 2) / 5
            elif( nMode == 2 ):
                nNewExpo = self.nMaxExpo; # but doesn't we gather too much noise ?

            if( False ):
                # one shot (but not working: too harsh and not the good formulae)
                rRatioNewActual = float(nActualExpo)/nNewExpo;
                nNewGain = int( rRatioNewActual * nActualGain * nTargetLuminosity / rLum );

                print( "INF: abcdk.camera.changeExposureMode: actual gain/expo: %d, %d, new: %d, %d" % (nActualGain, nActualExpo, nNewGain, nNewExpo) );

                # TODO: need a formulae for how to combine gain and expo
                if( nNewGain > self.nMaxGain ):
                    rMultiply = float(nNewGain) / self.nMaxGain;
                    nNewExpo = int(nNewExpo*rMultiply*2/5);
                    nNewGain = 255;
                print( "INF: abcdk.camera.changeExposureMode: after equilibrating: actual gain/expo: %d, %d, new: %d, %d" % (nActualGain, nActualExpo, nNewGain, nNewExpo) );


                avd.setParam( self.kCameraSelectID, nNumCamera );
                avd.setParam( self.kCameraAutoExpositionID, 0 );
                avd.setParam( self.kCameraGainID, nNewGain );
                avd.setParam( self.kCameraExposureID, nNewExpo );
            else:
                if( nNumCamera != avd.getParam( self.kCameraSelectID ) ):
                    avd.setParam( self.kCameraSelectID, nNumCamera );
                    time.sleep( 1. ); # time for kCameraAutoExpositionID to finish their work
                avd.setParam( self.kCameraAutoExpositionID, 0 );

                nActualExpo = avd.getParam( self.kCameraExposureID );
                print( "INF: abcdk.camera.changeExposureMode: nActualExpo: %d" % nActualExpo );

                im = self.getImage();
                rLum = image.getImageLuminosity( im, 1 );
                print( "INF: abcdk.camera.changeExposureMode: current luminosity: %f (current)" % rLum );

                if( abs( nNewExpo - nActualExpo ) < 80 and abs( rLum - nTargetLuminosity ) < rLumMargin ):
                    print( "INF: abcdk.camera.changeExposureMode: finished time taken: %5.3fs (nothing to do)" % (time.time() - timeBegin ) );
                    self.nManualExposure_nMode = nMode;
                    self.nManualExposure_nExposure = nActualExpo;
                    self.nManualExposure_nGain = nActualGain;
                    return True;

                # find a good exposition range: a one that is dark when gain is 0 and bright when gain is full, with an exposition near the wanted one
                nRange1 = 0;
                nRange2 = self.nMaxExpo;
                nActualExpo = nNewExpo;
                while( True ):
                    if( self.bManualExposure_bMustStop ):
                        return False;

                    aMinMax = [];
                    for nActualGain in [0, self.nMaxGain]:
                        print( "\nINF: abcdk.camera.changeExposureMode: changing gain/expo: %d, %d (range1: %d, range2: %d)" % (nActualGain, nActualExpo, nRange1, nRange2) );
                        avd.setParam( self.kCameraGainID, nActualGain );
                        avd.setParam( self.kCameraExposureID, nActualExpo );
                        time.sleep( 1.2 ); # a certaines expo, c'est un peu plus long a setter
                        im = self.getImage();
                        rLum = image.getImageLuminosity( im, 1 );
                        print( "\nINF: abcdk.camera.changeExposureMode: current luminosity: %f (after setting test exposure)" % rLum );
                        aMinMax.append( rLum );
                    if( aMinMax[0] < nTargetLuminosity + rLumMargin and aMinMax[1] > nTargetLuminosity - rLumMargin ):
                        break; # this is a good exposition
                    if( aMinMax[0] >= nTargetLuminosity + rLumMargin ):
                        nRange2 = nActualExpo;
                    else:
                        nRange1 = nActualExpo;
                    if( nRange1 == nRange2 ):
                        print( "ERR: abcdk.camera.changeExposureMode: can't achieve good exposure" );
                        return False;
                    nActualExpo = int( ( ( nRange1 + nRange2 + 1 ) / 2 ) * 0.2 + nActualExpo * 0.8 ); # it's not really a dichotomy, because we want to stay near the asked value
                # while - set expo

                print( "\nINF: abcdk.camera.changeExposureMode: good exposure find: %d" % (nActualExpo) );

                # find the  good gain
                nRange1 = 0;
                nRange2 = self.nMaxGain;
                nActualGain = self.nMaxGain/2;
                while( True ):
                    if( self.bManualExposure_bMustStop ):
                        return False;

                    print( "\nINF: abcdk.camera.changeExposureMode: changing gain/expo: %d, %d" % (nActualGain, nActualExpo) );
                    avd.setParam( self.kCameraGainID, nActualGain );
                    avd.setParam( self.kCameraExposureID, nActualExpo );
                    time.sleep( 0.4 );
                    im = self.getImage();
                    rLum = image.getImageLuminosity( im, 1 );
                    print( "\nINF: abcdk.camera.changeExposureMode: current luminosity: %f (after setting test exposure)" % rLum );
                    if( abs( rLum - nTargetLuminosity ) < rLumMargin ):
                        break; # this is a good settings
                    if( rLum > nTargetLuminosity ):
                        nRange2 = nActualGain;
                    else:
                        nRange1 = nActualGain;
                    if( nRange1 == nRange2 ):
                        print( "ERR: abcdk.camera.changeExposureMode: can't achieve good gain (weird)" );
                        return False;
                    nActualGain = ( nRange1 + nRange2 + 1 ) / 2;
                # while - set expo
                # while - end

        self.nManualExposure_nMode = nMode;
        self.nManualExposure_nExposure = nActualExpo;
        self.nManualExposure_nGain = nActualGain;

        print( "INF: abcdk.camera.changeExposureMode: finished time taken: %5.3fs" % (time.time() - timeBegin ) );
        return True;
    # changeExposureMode - end

    def changeExposureMode_abort(self):
        """
        Exit a potentially changeExposureMode method (leaving it in an unknown state)
        """
        print( "INF: abcdk.camera.changeExposureMode_abort: launching a stop signal..." );
        self.bManualExposure_bMustStop = True;
    # changeExposureMode_abort - end

    def updateGain( self, nTargetLuminosity = 127 ):
        """
        take a random picture and change a bit the gain, so what the luminosity is keeped.
        It's intended to be called from time to time
        return 0: nothing done, 1: changed, -1: impossible to change gain
        """
        import image
        import naoqitools # prevent cycling import

        im = self.getImage();
        rLum = image.getImageLuminosity( im, 1 );
        if( abs( rLum - nTargetLuminosity ) > 20 ):
            if( rLum > nTargetLuminosity ):
                nChange = -10;
            else:
                nChange = +10;
            avd = naoqitools.myGetProxy( "ALVideoDevice" );
            nValGain = avd.getParam( self.kCameraGainID );
            nValGain += nChange;
            # TODO Here: if mode sport, then we should change expo
            if( nValGain < 0 or nValGain > self.nMaxGain ):
                print( "WRN: abcdk.camera.updateGain: can't achieve good gain (current lum: %f, nWantedGain: %d) => changing a bit of exposure" % (rLum, nValGain ) );
                nValExpo = avd.getParam( self.kCameraExposureID );
                nValExpo += nChange;
                if( nValExpo < 0 or nValExpo > self.nMaxExposure ):
                    print( "ERR: abcdk.camera.updateGain: can't achieve good expo (current lum: %f, nWantedExpo: %d)" % (rLum, nValExpo ) );
                    return -1;
                print( "INF: abcdk.camera.updateGain: changing current exposure (current lum: %f, nWantedExpo: %d, change: %d)" % (rLum, nValExpo, nChange ) );
                avd.setParam( self.kCameraExposureID, nValExpo );
                avd.setParam( self.kCameraGainID, nValGain-nChange ); # set another gain
            else:
                print( "INF: abcdk.camera.updateGain: changing current gain (current lum: %f, nWantedGain: %d, change: %d)" % (rLum, nValGain, nChange ) );
                #~ avd.setParam( self.kCameraExposureID, avd.getParam( self.kCameraExposureID ) ); # reset it (not usefull)
                avd.setParam( self.kCameraGainID, nValGain );
            return 1;
        return 0;
    # updateGain - end

    def getLastImageTimeStamp(self, strClientNameKey):
        return self.dictImageLastTimeStamp[strClientNameKey]

    def getImage( self, nImageResolution = 1, nCamera = -1, bUseMultiStreamModule = False ):
        """
        take an image from the camera
        WRN: not optimal (it's at python level)
        - nCamera:
            -1: use current selected,
            +0: use top camera,
            +1: use bottom camera
        return:
            - None on error
            - an OpenCV image "image"
            - or an array of two opencv image: [image1, image2] if multistream
        """

        import naoqitools # prevent cycling import

        avd = naoqitools.myGetProxy( "ALVideoDevice" );
        strMyClientName = "abcdk.camera";

        #~ print( "DBG: abcdk.camera.getImage: subscribing: before..." );
        timeBegin = time.time();
        if( not bUseMultiStreamModule ):
            strMyClientName = avd.subscribe( strMyClientName, nImageResolution, self.kBGR, 5 );
            nUsedResolution = avd.getGVMResolution( strMyClientName );
        else:
            strMyClientName = avd.subscribeCameras( strMyClientName, [0,1], [nImageResolution]*2, [self.kBGR]*2, 5 );
            nUsedResolution, nDumb = avd.getResolutions( strMyClientName );
        #avd.setResolution( strMyClientName, 2);

        #~ print( "DBG: abcdk.camera.getImage: subscribing: after, nUsedResolution: %d (takes: %5.3fs)" % ( nUsedResolution, ( time.time() - timeBegin ) ) );

        nSizeX, nSizeY = avd.resolutionToSizes( nUsedResolution );
        #~ print( "DBG: abcdk.camera.getImage: GVM has Image properties: %dx%d" % (nSizeX,nSizeY) );
        bufferImageToDraw = cv.CreateImage( (nSizeX, nSizeY), cv.IPL_DEPTH_8U, 3 );
        if( bUseMultiStreamModule ):
            bufferImageToDraw2 = cv.CreateImage( (nSizeX, nSizeY), cv.IPL_DEPTH_8U, 3 );
        try:
            if( not bUseMultiStreamModule ):
                dataImage = avd.getImageRemote( strMyClientName );
            else:
                #~ print( "getImagesRemote: avant" );
                dataImage = avd.getImagesRemote( strMyClientName );
                #~ print( "getImagesRemote: apres" );

            avd.unsubscribe( strMyClientName );

            if( dataImage == None ):
                print( "ERR: abcdk.camera.getImage: dataImage is none!" );
                return None;
            if( not bUseMultiStreamModule ):
                nSizeX = dataImage[0];
                nSizeY = dataImage[1];
                #~ print( "Image get: %dx%d" % (nSizeX,nSizeY) );
                #~ print( "Image prop: layer: %d, format: %d" % (dataImage[2],dataImage[3]) );
                image = dataImage[6];
                #~ print( "first char: '%s','%s','%s'" % ( image[0+960],image[1],image[2] )  );
                #~ print( "first char orded: %s,%s,%s" % ( ord( image[0] ), ord( image[1] ), ord( image[2] )  ) );
                # bufferImageToDraw.data = image;
            else:
                #~ print("image len: %d" % len(dataImage) );
                nSizeX = dataImage[0][0]; # read only properties of image 1
                nSizeY = dataImage[0][1];
                image = dataImage[2][nSizeX*nSizeY*3:];
                image2 = dataImage[2];
            # converted locally in NAO's  head
            cv.SetData( bufferImageToDraw, image );
            if( bUseMultiStreamModule ):
                cv.SetData( bufferImageToDraw2, image2 );
                return [bufferImageToDraw, bufferImageToDraw2];
            return bufferImageToDraw;
        except BaseException, err:
            print( "ERR: abcdk.camera.getImage: catching error: %s! (%s)" % (err, traceback.format_exc()) );
        return None;
    # getImage - end

    #def unsubscribeCamera(self, nCamera=0):
    #    """
    #    """
    #    return getImageCV2_releaseImage( nCamera=nCamera );

    def getClientNameFromProperties( self, nImageResolution = 2, nCamera = 0 , colorSpace = 13 ):
        return "abcdk.camera_client_" + str(nCamera) + "_" + str(nImageResolution) + "_" + str(colorSpace);


    def getALImage(self,  nImageResolution = 2, nCamera = 0 , colorSpace = 13, fps = 5, bNoUnsubscribe=False, bVerbose = False, bEnsureImageIsDifferent=True ):
        """
        """
        #bEnsureImageIsDifferent = None
        def _getImage(avd, strMyClientName, bUseLocalProxy=True):
            #print("Avd is %s, strMyClientName is %s, bUseLocalProxy is %s" % (avd, strMyClientName, bUseLocalProxy))
            aImage = ALImage()
            if bUseLocalProxy:
                #print("INF: abcdk.getALImage using getImageLocal")
                nMemoryPointer = avd.getImageLocal2( strMyClientName );
                aImage.loadFromMemory(nMemoryPointer)
                aCopyImage = aImage.getDataOwnedCopy() # we update ownedDataCopy (== unlink from memory, so we can release the image)
                #print("the array is %s, with flags %s" % (aCopyImage, aCopyImage.flags))
                avd.releaseImage(strMyClientName)  # we released the camera right now
            else:
                #print("INF: abcdk.getALImage using getImageRemote")

                ## SECTION CRITIQUE ###
                aALValueList = avd.getImageRemote( strMyClientName );
                ## END SECTION CRITIQUE ###
                #print aALValueList[0]
                if aALValueList is None:
                    print( "ERR: abcdk.camera.getALImage: dataImage is none!") # (duration: %5.3fs)" % (time.time()-timeBegin) );
                    debug.raiseCameraFailure();
                aImage.loadFromALMemory(aALValueList)

            if( aImage.ownedDataCopy == None ):
                print( "ERR: abcdk.camera.getALImage: dataImage is none!") # (duration: %5.3fs)" % (time.time()-timeBegin) );
                debug.raiseCameraFailure();
                #if( bNoUnsubscribe ):
                    #avd.unsubscribe( self.dictOpenedSubscriber[strMyClientNameKey] );
                #    self.dictOpenedSubscriber[strMyClientNameKey] = None;
                time.sleep(0.1)
                return None;

            return aImage

        import naoqitools
        avd = naoqitools.myGetProxy( "ALVideoDevice" );
        strMyClientNameKey = self.getClientNameFromProperties( nImageResolution = nImageResolution, nCamera = nCamera, colorSpace = colorSpace );
        #~ print( "DBG: abcdk.camera.getImage: subscribing: before..." );
        if( strMyClientNameKey not in self.dictOpenedSubscriber.keys() or self.dictOpenedSubscriber[strMyClientNameKey] == None ):
            print("%s DBG: abcdk.camera.getALImage: subscribing  with name '%s'..." % (time.time(),strMyClientNameKey) );
            self.dictOpenedSubscriber[strMyClientNameKey] = avd.subscribeCamera( strMyClientNameKey, nCamera , nImageResolution, colorSpace, fps );
            self.dictImageLastTimeStamp[strMyClientNameKey] = None
            #self.dictTimestampLastGetImageCall[strMyClientNameKey] = None
        strMyClientName  = self.dictOpenedSubscriber[strMyClientNameKey]


        bUseLocalProxy = self.bUseLocalProxy  # on l'attache a l'objet camera

        ## Section Critique
        self.aSubsribersInUse.add(strMyClientName)
        aImage = _getImage(avd, strMyClientName, bUseLocalProxy=bUseLocalProxy)
        self.aSubsribersInUse.remove(strMyClientName)
        # end section critique

        if bEnsureImageIsDifferent:
            #print("time is %s:%s return %s" % (dataImage[4], dataImage[5], rCurrentTimeStamp))
            rLastImageTimeStamp = self.dictImageLastTimeStamp[strMyClientNameKey]
            #print("rLastImageTimeStamp %s, %s" % (rCurrentTimeStamp, rLastImageTimeStamp))
            if rLastImageTimeStamp == None:
                rLatency = None
            else:
                rLatency = rLastImageTimeStamp - aImage.rTimeStamp
            while rLatency == 0:
                #print("waiting rLatency is %s" % rLatency)
                aImage = _getImage(avd, strMyClientName, bUseLocalProxy=bUseLocalProxy)
                rLatency = rLastImageTimeStamp - aImage.rTimeStamp
            #    print("getting new image timestamp")
                #rCurrentTimeStamp = dataImage[4] + dataImage[5]/(1000.0*1000.0)
                #rLatency = rLastImageTimeStamp - rCurrentTimeStamp
                #time.sleep(0.2/fps) # we wait a bit
#                   self.dictTimestampLastGetImageCall[strMyClientNameKey]
#                   time.sleep(1.0/fps - rTimeElapseSincePreviousCall)
#                   rTimeElapseSincePreviousCall = time.time() - self.dictTimestampLastGetImageCall[strMyClientNameKey]
#                   rTimeToSleep = max(0, 1.0/fps - (rTimeElapseSincePreviousCall))
#                   time.sleep(rTimeToSleep)
#               self.dictTimestampLastGetImageCall[strMyClientNameKey] = time.time()
            self.dictImageLastTimeStamp[strMyClientNameKey] = aImage.rTimeStamp
        if not(bNoUnsubscribe):
            print("%s DBG: abcdk.camera.getImageCV2: unsubscribing..." % time.time())
           # avd.unsubscribe( strMyClientName );
            self.getImageCV2_unsubscribeCamera(nImageResolution=nImageResolution, nCamera=nCamera, colorSpace=colorSpace)  # unsubscribe

        return aImage


    ### BUG .. si on dit camera 1.. bah c'est camera0 qui est utilisé..
    def getImageCV2( self, nImageResolution = 2, nCamera = 0 , colorSpace = 13, fps = 5, bNoUnsubscribe=False, bVerbose = False, bEnsureImageIsDifferent=True ):
        """
        take an image from the camera
        Args :
        nImageResolution :
            AL::kQQQVGA 7       Image of 80*60px
            AL::kQQVGA  0       Image of 160*120px
            AL::kQVGA   1       Image of 320*240px
            AL::kVGA    2       Image of 640*480px
            AL::k4VGA   3       Image of 1280*960px
        - nCamera:
            0: use top camera,
            1: use bottom camera
        - colorSpace:
            0 = kYuvColorSpace,
            13 = kBGRColorSpace
        return:
            - None on error
            - an OpenCV2/numpy image
        """
        if( self.mutexGetImageCV2.testandset() == False ):
            print( "WRN: abcdk.camera.getImageCV2: already acquiring an image, returning None..." );
            return None;
        #ALimage = self.getALImage(*args, **kwArgs)
        #try:
        timeBegin = time.time();
        alimage = self.getALImage(nImageResolution = nImageResolution, nCamera = nCamera , colorSpace = colorSpace, fps = fps, bNoUnsubscribe=bNoUnsubscribe, bVerbose = bVerbose, bEnsureImageIsDifferent=bEnsureImageIsDifferent)
        image = alimage.ownedDataCopy
        if( bVerbose ):
            if( image.shape[2] == 1 ):
                strPixels = "first grey data: 0x%02x,0x%02x,0x%02x,0x%02x" % ( image[0,0],image[0,1], image[0,2], image[0,3] );
                strLum = str( np.mean( image ) );
            else:
                strPixels = "first colored data: ";
                for i in range(4):
                    strPixels += "(0x%02x,0x%02x,0x%02x)," % (image[0,i][0],image[0,i][1],image[0,i][2]);
                strLum = str( np.mean( image ) );
            print( "DBG: abcdk.camera.getImageCV2: get a new image, " + strPixels + ", lum: " + strLum + (" (duration: %5.3fs)"%(time.time()-timeBegin)) );
            if( True ):
                strOut = self.strDebugPath + filetools.getFilenameFromTime() + ".jpg";
                print( "DBG: abcdk.camera.getImageCV2: image saved to '%s'" % strOut );
                cv2.imwrite( strOut, image, [cv2.IMWRITE_JPEG_QUALITY, 100] );

        self.mutexGetImageCV2.unlock();
        return image;

        #except BaseException, err:
        #    print( "ERR: abcdk.camera.getImageCV2: catching error: %s!" % traceback.format_exc() );
        #return None;
    # getImageCV2 - end

    def autotest_speedCamera(self):
        import time

        def _testSpeedCamera(nColorSpace, nImageResolution):
            import naoqitools # prevent cycling import
            rStartTime = time.time()
            rElapsedTime = time.time() - rStartTime
            nFps = 30
            nCamera = 0
            nImages = 0
            while rElapsedTime <= 10:
                a = self.getImageCV2(nImageResolution = nImageResolution, nCamera = nCamera , colorSpace = nColorSpace, fps = nFps, bNoUnsubscribe=True, bVerbose = False )
                if a!= None:
                    nImages += 1
                rElapsedTime = time.time() - rStartTime
            print("%s images have been acquired in %s , which means %s image/sec" % (nImages, rElapsedTime, nImages/rElapsedTime))
            self.getImageCV2_unsubscribeCamera(nImageResolution=nImageResolution, nCamera=nCamera, colorSpace=nColorSpace)  # unsubscribe
            return (nImages/rElapsedTime)


        res = []
        for nColorSpace in [0, 13]:
            for nImageResolution in [7, 0, 1, 2, 3]:
                #print("nColorSpace (%s), nImageResolution (%s), results:" % (nColorSpace, nImageResolution))
                rImagePerSec = _testSpeedCamera(nColorSpace, nImageResolution)
                res.append([nColorSpace, nImageResolution, rImagePerSec])
        print res
        ## ON ROMEO we get : [[0, 7, 14.09150438615292], [0, 0, 14.676634559724544], [0, 1, 14.671493053486659], [0, 2, 13.980443539369695], [0, 3, 6.256661365433674], [13, 7, 14.033450665372754], [13, 0, 14.673578627617513], [13, 1, 14.675853777091424], [13, 2, 6.998751362408521], [13, 3, 1.7358447410316877]]
        # ON NAO : [[0, 7, 29.233307029810536], [0, 0, 28.06853192861368], [0, 1, 28.07255059611683], [0, 2, 21.303238803833022], [0, 3, 6.478833021008139], [13, 7, 27.830928694666117], [13, 0, 27.450729054560316], [13, 1, 27.553239091277234], [13, 2, 8.7797696866663], [13, 3, 1.7813247539973027]]

        #assert(np.all(np.array(res)[:,2] > 25))  # minimum 25 fps
        #print("Still subscribed are: %s" % (self.dictOpenedSubscriber))


    def getImageCV2_unsubscribeCamera( self, nImageResolution = 2, nCamera = 0, colorSpace = 13 , bForce=False):
        """
        when you using getImageCV2 with the option bNoUnsubscribe, you must call this at the end
        """
        strMyClientNameKey = self.getClientNameFromProperties( nImageResolution = nImageResolution, nCamera = nCamera, colorSpace = colorSpace)
        strMyClientName = self.dictOpenedSubscriber[strMyClientNameKey]
        if strMyClientName is not None:
            self.unsubscribeCamera(strMyClientName)

    def unsubscribeCamera(self, strMyClientName, bForce=False):
        print("INF: trying to unsubscribe %s" % strMyClientName)
        import naoqitools
        if strMyClientName in self.dictOpenedSubscriber.values():
            avd = naoqitools.myGetProxy( "ALVideoDevice" );
            if not(bForce):
                while(strMyClientName in self.aSubsribersInUse):
                    print("abcdk.camera.Camera.getImageCV2_unsubscribeCamera: %s is currently in used, wait until image is released" % strMyClientName)
                    time.sleep(0.1)
            avd.unsubscribe( strMyClientName );
            aKeyToPop = [key for key in self.dictOpenedSubscriber.keys() if self.dictOpenedSubscriber[key] == strMyClientName]
            #assert(len(aKeyToPop) == 1)
            for key in aKeyToPop:
                self.dictOpenedSubscriber.pop(key)
            print("abcdk.camera.getImageCV2_unsubscribeCamera (%s): done" %  strMyClientName)
    # getImageCV2_unsubscribeCamera - end

    def getImageCV2_unsubscribeAllCameras( self, bForce=False ):
        """
        """
        import naoqitools
        for k,v in self.dictOpenedSubscriber.iteritems():
            avd = naoqitools.myGetProxy( "ALVideoDevice" );
            self.unsubscribeCamera(v, bForce=bForce)
            #avd.unsubscribe( v );
        #self.dictOpenedSubscriber = dict(); # reset it



    def setFullAuto(self, camNum=0, nExpositionAlgorithm=0): #, exposureTime=100, gain=120, whiteBalance = 0):
        """
        Set automatic exposition and wb

        Args:
            cameraNum: the number of camera in /dev/video
            nExpositionAlgorithm: 0: , 2 : hightlight .. # TODO
        Returns:
            True if Success, False if error occured

        """
       # import v4l2
       # import fcntl
        import naoqitools
        mod = naoqitools.myGetProxy("ALVideoDevice")
        mod.setParameter(camNum, self.kCameraAutoExpositionID, 1) #  auto exposition
        mod.setParameter(camNum, self.kCameraAutoWhiteBalanceID, 1) # auto wb
        mod.setParameter(camNum, self.kCameraAecAlgorithmID, nExpositionAlgorithm) # exposition algorithm : hightlight
        #mod.setParameter(camNum, 17, exposureTime)
        #mod.setParameter(camNum, 6, gain)
            ## white balance not used for now.. cause it's buggy in vision
            #mod.setParameter(camNum, 33, 0)
    #    vd = open('/dev/video' + str(cameraNum), 'rw')
    #    cp = v4l2.v4l2_capability()
    #    fcntl.ioctl(vd, v4l2.VIDIOC_QUERYCAP, cp)
    #    print("Using camera %s" % (cp.bus_info))
    #    cp = v4l2.v4l2_control()  # creation of control structure id + value


            #CID_SATURATION   , 128
            #CID_HUE: 0
            #CID_SHARPNESS -7
            #CID_EXPOSURE_AUTO, 0  # disable auto exposure adjustement of gain/exposure
            # CID_GAIN, 32  # 32 = 1x gain
            # CID_EXPOSURE, 0
            #CID_AUTO_WHITE_BALANCE, 0 # disable
            # CID_BACKLIGHT_COMPENSATION, 0  ???
            # V4L2_MT9M114_FADE_TO_BLACK (V4L2_CID_PRIVATE_BASE):
            #cp.id, cp.value = (v4l2.V4L2_CID_AUTO_WHITE_BALANCE, 0)
            #fcntl.ioctl(vd, v4l2.VIDIOC_S_CTRL, cp)

            #cp.id, cp.value = (v4l2.V4L2_CID_EXPOSURE_AUTO, 0)
            #fcntl.ioctl(vd, v4l2.VIDIOC_S_CTRL, cp)

            #cp.id, cp.value = (v4l2.V4L2_CID_EXPOSURE, 80)
            #fcntl.ioctl(vd, v4l2.VIDIOC_S_CTRL, cp)

            #cp.id, cp.value = (v4l2.V4L2_CID_GAIN, 64)
            #fcntl.ioctl(vd, v4l2.VIDIOC_S_CTRL, cp)

            #cp.id, cp.value = (v4l2.V4L2_CID_DO_WHITE_BALANCE, -85)
            #fcntl.ioctl(vd, v4l2.VIDIOC_S_CTRL, cp)
        return True

# Camera - end
camera = Camera(); # singleton

class VideoMaker(object):
    """
    A simple object to start/stop a video recording and saving image to a filepath
    """
    def __init__(self, nImageResolution=0, aCameras=[0,1], nColorSpace=0, nFps=30, strImagesPath='/tmp/', strExtension='jpg', nImageCompression=10):
        self.nImageResolution = nImageResolution
        self.aCameras = aCameras  # list of cameras to use
        self.nColorSpace = nColorSpace
        self.nFps = nFps
        self.strImagesPath = strImagesPath
        self.bMustStop = False;
        self.bDisableImWrite = False
        self.strExtension = strExtension
        self.nImageCompression = nImageCompression

    def stop(self):
        if( not self.bMustStop ):
            self.bMustStop = True
            print( "INF: abcdk.camera.videoMaker: stopping..." )
            print("List of subscribed camera %s" % camera.dictOpenedSubscriber)
            time.sleep(0.5) # we wait for current image to be processed
            for nCamera in self.aCameras:
                camera.getImageCV2_unsubscribeCamera(nImageResolution=self.nImageResolution, nCamera=nCamera, colorSpace=self.nColorSpace)  # unsubscribe

    def start(self, bDebug=True):
        """
        save a bunch of image using a timestamp
        """
        import time
        print("Using Local Image %s" % camera.bUseLocalProxy)
        self.bMustStop = False
        self.nImageSaved = 0

        for nCamera in self.aCameras:
            image = camera.getImageCV2(nImageResolution=self.nImageResolution, nCamera=nCamera, colorSpace=self.nColorSpace, fps=self.nFps, bNoUnsubscribe=True, bVerbose=False)

        rStartTime = time.time()
        while not(self.bMustStop):
            for nCamera in self.aCameras:
                rStartTime_getImage = time.time()
                image = camera.getImageCV2(nImageResolution=self.nImageResolution, nCamera=nCamera, colorSpace=self.nColorSpace, fps=self.nFps, bNoUnsubscribe=True, bVerbose=False)
                rDuration_getImage = time.time() - rStartTime_getImage
                    #print("Using timestamp %s" % timestamp)
                if not(self.bDisableImWrite):
                    strMyClientNameKey = camera.getClientNameFromProperties( nImageResolution = self.nImageResolution, nCamera = nCamera, colorSpace = self.nColorSpace);
                    timestamp = camera.getLastImageTimeStamp(strMyClientNameKey)
                    rStartTime_timestampManagement = time.time()
                    strFileOut = self.strImagesPath + str(nCamera) + "_" + filetools.getFilenameFromTime(timestamp=timestamp) + "." + self.strExtension
                    rDuration_timestampManagement = time.time() - rStartTime_timestampManagement
#               #print( "DBG: abcdk.camera.videoMaker: writing image to '%s'" % strFileOut );
                    rStartTime_imwrite = time.time()
                    #print("writting %s" % strFileOut)
                    cv2.imwrite( strFileOut, image, [cv2.IMWRITE_JPEG_QUALITY, self.nImageCompression] );
                    rDuration_imwrite = time.time() - rStartTime_imwrite
                    rFullDuration = time.time() - rStartTime_getImage
                    if rFullDuration > 0.2:
                        print("WARNING: SLOW (full is %s): Saving image took %ssec, getImageCv2 took %s sec, timestamp management took %s" % (rFullDuration, rDuration_imwrite, rDuration_getImage, rDuration_timestampManagement))

            self.rElapsedTime = time.time() - rStartTime

            self.nImageSaved += 1
        return(self.rElapsedTime, self.nImageSaved, self.nImageSaved/self.rElapsedTime)
   # with black and white ( 2 cameras, 10seconds, in /tmp/, using   self.videoMaker.nImageCompression = 60) : (9.730589866638184, 285, 29.28907742552554)
   # with color ( 2 cameras, 10seconds, in /tmp/, using  self.videoMaker.nImageCompression=60) :  (9.742464065551758, 130, 13.343646856206037)  (9.690371036529541, 152, 15.685673894942674)

    def test_speed(self):
        import time
        rStartTime = time.time()
        rElapsedTime = time.time() - rStartTime
        nImageSaved = 0
        nCamera = 0
        while rElapsedTime < 10:
            rElapsedTime = time.time() - rStartTime
            image = camera.getImageCV2(nImageResolution=3, nCamera=nCamera, colorSpace=0, fps=30, bNoUnsubscribe=True, bVerbose=False)
            rElapsedTime = time.time() - rStartTime
            if image != None:
                nImageSaved += 1
        return(rElapsedTime, nImageSaved, nImageSaved/rElapsedTime)

# End - videoMaker



#def hackToGetVideoDeviceDirectly():
#    # with NNNN = pid de naoqi
#    #lsof -p NNNN | awk '{print $9}' | grep '\.so'  | grep videoDevice -> on a alors le path de la lib ALVideoDevice chargé
#
## to list available symbol on a specific library use objdump .. but yeah.. objdump is not available on the robot (do it on your computer)
##objdump  -T /usr/lib/naoqi/libalvideodevice.so
#
## for instance we have :
##00000000000687c0 g    DF .text  00000000000001b5  Base        _ZN2AL13ALVideoDevice23getDirectRawImagesLocalERKSs
##00000000000685b0 g    DF .text  0000000000000069  Base        _ZN2AL13ALVideoDevice13getImageLocalERKSs
##0000000000068980 g    DF .text  00000000000001b5  Base        _ZN2AL13ALVideoDevice14getImagesLocalERKSs
##00000000000686f0 g    DF .text  0000000000000069  Base        _ZN2AL13ALVideoDevice22getDirectRawImageLocalERKSs
#    #so we can call dll._ZN2AL13ALVideoDevice13getImageLocalERKSs()
#    # in the .h files we see the signature: void* getImageLocal(const std::string& Name);
#    # with name the registred camera..
#
#
#    import naoqitools# prevent cycling import
#
#    #avd = naoqitools.myGetProxy( "ALVideoDevice" );
#    import naoqi
#    avd = naoqi.ALProxy("ALVideoDevice", "127.0.0.1", 9559)
#    strMyClientName = "abcdk.cameraRAW";
#
#    #~ print( "DBG: abcdk.camera.getImage: subscribing: before..." );
#    nImageResolution = 0
#    nColorSpace = 0
#    strMyClientName = avd.subscribe( strMyClientName, nImageResolution, nColorSpace, 5 );
#    nUsedResolution = avd.getGVMResolution( strMyClientName );
#
#    import ctypes
#    dll = ctypes.cdll.LoadLibrary('/usr/lib/naoqi/libalvideodevice.so')
#    ## ah mais oui il nous faut un proxy !! un vrai..
#
#    ### /usr/lib/libqiproject.so << avec un truc comme ça..
#    #aStr = ctypes.create_string_buffer(strMyClientName)
#    #ref= ctypes.c_char_p(ctypes.addressof(aStr))
#    #pointer = dll._ZN2AL13ALVideoDevice13getImageLocalERKSs(ctypes.byref(ref))
#    ## JE n'arrive pas a passer un std::string.. ça fait planter meme avec un types.c_char_p(ctypes.addressof(ctypes.create_string_buffer(strMyClientName))) etc..
#
#
#    #On va donc essayer de taper directement libqimessaging pour avoir un pointeur vers le proxy actuel
#    #000ba506 g     F .text  0000047b              qi::Session::Session()
#
##000ba506 g     F .text  0000047b              _ZN2qi7SessionC2Ev
##000ba506 g     F .text  0000047b              _ZN2qi7SessionC1Ev
##000ba506 g    DF .text  0000047b  Base        _ZN2qi7SessionC2Ev
##000ba506 g    DF .text  0000047b  Base        _ZN2qi7SessionC1Ev
##
#
#    dll = ctypes.cdll.LoadLibrary('/usr/lib/libqimessaging.so')
##    objdump -tT /home/lgeorge/media/nao/toolchain/linux64-nao-atom-cross-toolchain-1.22.3.10_2013-12-23_pub/sysroot/usr/lib/libqi.so | grep Base | grep C1Ev | grep Version
### Base pour avoir un truc callable ?
### C1Ev car C2Ev -> segfault ?..
### Il faudrait trouver la doc quelque part pour comprendre comment c
#
#    # on peut aussi utiliser naoqi1 et faire un ALProxy
#
#    ## En fait plus simple: ALVideoDeviceProxy('127.0.0.1
#
#    ## ON va utiliser alvideodeviceproxy ->     ALVideoDeviceProxy(const std::string &ip, int port=9559);
### donc on
##objdump -tTC /home/lgeorge/versionGateMaster/sdk/libnaoqi/build-1.22.2.52-release/sdk/lib/libalproxies.so | grep ALVideoDeviceProxy
#
##    0012ba3c g    DF .text  00000232  Base        AL::ALVideoDeviceProxy::ALVideoDeviceProxy()
##0012ba3c g    DF .text  00000232  Base        _ZN2AL18ALVideoDeviceProxyC1Ev
#
## en fait nous on veut la version qui prend une string et un int  (si)
##0012b656 g     F .text  000001d9              _ZN2AL18ALVideoDeviceProxyC1ERKSsi
##0012b656 g     F .text  000001d9              _ZN2AL18ALVideoDeviceProxyC2ERKSsi
##0012b656 g    DF .text  000001d9  Base        _ZN2AL18ALVideoDeviceProxyC1ERKSsi
##0012b656 g    DF .text  000001d9  Base        _ZN2AL18ALVideoDeviceProxyC2ERKSsi
#
###import ctypes
###dll = ctypes.cdll.LoadLibrary('/usr/lib/libalproxies.so')
###_createFunct = dll._ZN2AL18ALVideoDeviceProxyC1ERKSsi
###_createFunct.argtypes = [ctypes.c_char_p, ctypes.c_int]
###_createFunct.argtypes = [ctypes.c_void_p, ctypes.c_int]  # on passe par reference
###_createFunct.restype = ctypes.c_void_p
###strin = ctypes.create_string_buffer("127.0.0.1")
###_int_p = ctypes.POINTER(ctypes.c_int)
###_char_p_p = ctypes.POINTER(ctypes.c_char_p)
###addr = ctypes.create_string_buffer("127.0.0.1")
###
##### on feinte.. on utilise libstdc++ pour convertir un char* en std::string const&
###std = ctypes.cdll.LoadLibrary('libstdc++.so')
###p = std._ZNSsC2EPKcRKSaIcE(ctypes.addressof(strin))
###std_string_p = ctypes.c_void_p(p)
###ip = ctypes.c_int(9559)
###_createFunct(ctypes.byref(std_string_p), ip)  # ca segfault car les std::string ne sont pas supporte avec ctypes..
###
###    _createFunct(
###### [W] 4838 alcommon.alproxy: ALProxy(ModuleName, IP, Port) is DEPRECATED. Create a broker yourself and ask it for a proxy.
###### rahhh.. et apres segfault
### CA NE MARCHERA PAS.. ctypes c'est bien pour le c.. pour le c++ (les objets etc.. ca ne marchera pas)
##p = avd.getImageLocal2("subscriberName")
#
##a = np.ctypeslib.as_array((ctypes.c_int8 * 120* 160).from_address(p))  <<-- ca marche certainement depuis
#
#
## il faudrait un magic pour etre certain qu'on est dans le meme espace memoire
#
## avec un
## v.eval("ctypes.c_ubyte.from_address(0x5e4cf0c8)") <<-- avec v un python bridge dans le meme espace memoire que alVideoDevice
###
#pythonB.eval("a=np.ctypeslib.as_array((ctypes.c_int8*arr.fHeight*arr.fWidth).from_address(1186803720)) ")



def autoTest():
    import test
    test.activateAutoTestOption();
    #~ camera.changeExposureMode();
    #~ camera.changeExposureMode( nMode = 1 );
    #~ camera.changeExposureMode( nMode = 2 );
    for i in range( 20 ):
        print( "updateGain: %d" % camera.updateGain() );

# autoTest

if __name__ == "__main__":
    pass
    #autoTest()
    #autoTest();
