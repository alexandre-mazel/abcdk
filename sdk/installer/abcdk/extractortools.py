# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Extractor tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Small convenient method to help debug and decode information from extractors"""

print( "importing abcdk.extractortools" );
import arraytools
import image_info
import filetools

class DatamatrixInfo(object):
    """
    Info of one seen datamatrix mark.
    """
    def __init__( self, data_for_one ):
        self.reset();
        self.strName = data_for_one[0][0]; # mark Name
        self.aPosXY = data_for_one[1][1];  # center X,Y
        self.aSizeWH = data_for_one[1][2]; # width/height
        self.aCornersAngle = data_for_one[2][1:5];  # the 4 corners of datamatrix in camera angle (-0.5, 0.5)
        self.rAngleX = data_for_one[2][5]  # rotation angle of datamatrix
        self.aCornersPixels= data_for_one[3][0:4] # corners of datamatrix in pixels
        self.aCornersRefinedPixels = data_for_one[4][0:6] #[topLeft,  bottomLeft,  middleOfBottomTimingPattern,
                                                # rightBottomCrossOfDotLines,  rightMidleTimingPattern,  rightTopCorner]
        med = [0,0];
        for pt in self.aCornersAngle:
            med[0] += pt[0];
            med[1] += pt[1];
        med[0] /= 4;
        med[1] /= 4;
        self.aCenterAngle = med;

    def reset( self ):
        self.strName = "";
        self.aPosXY = []; # center of bounding box (image relative [-0.5..0.5])
        self.aSizeWH = []; # size (exprimed in image relative [0..1])
        self.aCornersAngle = [] # corner trapezeAngle are position exprimed in camera angle
        self.aCenterAngle = []; # average center of corners exprimed in camera angle
        self.rAngleX = None; # rotated angle of the datamatrix (the wheel of fortune)
        self.aCornersPixels =[]; # corner trapeze in pixel
        self.aCornersRefinedPixels = [] # follows points :#[topLeft,  bottomLeft,  middleOfBottomTimingPattern,
                                                # rightBottomCrossOfDotLines,  rightMidleTimingPattern,  rightTopCorner]
    # reset - end

    def __str__( self ):
        strOut = "";
        strOut += "strName: '%s'\n" % self.strName;
        strOut += "Bounding box pos: %s\n" % ( self.aPosXY );
        strOut += "Bounding box size (width = %s, height = %s)\n" % (self.aSizeWH[0], self.aSizeWH[1]);
        strOut += "Corners In camera angle: %s\n" % ( self.aCornersAngle );
        strOut += "CenterAngle: %s\n" % ( self.aCenterAngle);
        strOut += "rAngleX: %s\n" % ( self.rAngleX );
        strOut += "Corner in pixel: %s\n" % ( self.aCornersPixels );
        strOut += "Corner refined :%s \n" % (self.aCornersRefinedPixels)
        return strOut;
        
# class DatamatrixInfo - end        
                
class DatamatrixInfos:
    """
    Info of one round of datamatrix detection (it contains info about a bunch of datamatrix)
    """        
    def __init__( self, data ):
        bEmpty = (data == [] or data == None);
        self.imageInfo = image_info.ImageInfo();
        if( not bEmpty ):
            self.imageInfo.nTimeStamp = data[0][0] + data[0][1]/1000000.0 # meme format que time.time()
            self.imageInfo.cameraPosInNaoSpace = data[1]
            self.imageInfo.cameraPosInWorldSpace = data[2]
            self.imageInfo.cameraPosInFrameTorso = data[3]
            self.imageInfo.nCameraName = data[4]
            self.imageInfo.nResolution = data[5]
            self.imageInfo.headAngles = data[6]
            #self.imageInfo.headAngles = data[7]
        self.marks = [];
        if( not bEmpty ):
            for mark in data[7]:
                #print mark
                self.marks.append( DatamatrixInfo( mark ) );
                
    def __str__( self ):
        strOut = "";
        strOut += "imageInfo:\n%s" % self.imageInfo;
        strOut += "detected: %d mark(s):\n" % len( self.marks );
        for mark in self.marks:
            strOut += str( mark );
        return strOut;
# class DatamatrixInfos - end

def datamatrix_decodeInfo( data ):
    """
    Take "THE" big array and return a created object containing nammed fields
    return a DatamatrixInfos object
    - data: data from extractors
    """
    return DatamatrixInfos( data );
# datamatrix_decodeInfo - end

def datamatrix_getLookAt( data, strName = "" ):
    """
    return the absolute position to set the head to look at the center of datamatrix seen at this analyse (using head pos when taking picture)
        or None if no information
    - strName: filter on only some marks
    """
    decoded = datamatrix_decodeInfo( data );
    headPos = None;
    #print( "abcdk.extractortools.datamatrix_getLookAt( %s, '%s' )" % (str(decoded), strName ) )
    for mark in decoded.marks:
        if( strName in mark.strName ):
            #~ headPos = [mark.pos[0]*0.4, mark.pos[1]*0.4];            
    #        oldPos = [decoded.cameraPosInNaoSpace[5] + mark.pos[0], decoded.cameraPosInNaoSpace[4] + mark.pos[1]];
            headPos = [decoded.imageInfo.cameraPosInFrameTorso[5] + mark.centerAngle[0], decoded.imageInfo.cameraPosInFrameTorso[4] + mark.centerAngle[1]];

            break;
    print( "abcdk.extractortools.datamatrix_getLookAt => headPos: %s" % (str(headPos ) ) );
    #print( "abcdk.extractortools.datamatrix_getLookAt => oldPos: %s" % (str(oldPos ) ) );
    return headPos;
# datamatrix_lookAt - end

def getMark(dataDecoded, strName):
    """
    return the first mark in data that have the specified name
    
    if no mark with this name is found, None is returned
    """
    l = [mark for mark in dataDecoded.marks if mark.strName == strName]
    if l != []:
        return l[0]


#def datamatrix_getNormal(data, rRealSize, strName = ""):
#    """
#    return the normal vector of datamatrix compared to nao torso 
#    """
#    fovD = 1.267109036947883  # 72.6 deg 
#    fovH = 60.97 * math.pi / 180.0  
#
#    decoded = datamatrix_decodeInfo( data );
#    for mark in decoded.marks:
#        if (strName in mark.strName):
#            strLabel, rRealSize, trapeze = mark.strName, rRealSize, mark.trapeze
#            med = [0,0];
#            for pt in trapeze:
#                med[0] += pt[0];
#                med[1] += pt[1];
#            med[0] /= 4;
#            med[1] /= 4;
#
#            rSize = 0;
#            for pt in trapeze:            
#                rSize += numeric.dist2D( pt, med );
#            rSize /= 2; # size de la diagonal
#            
#            # we assume that mark are allways L en haut a gauche
#
#            # we compute the average of bottom and top delta
#            rdy1 = trapeze[3][1] - trapeze[0][1];
#            rdx1 = trapeze[3][0] - trapeze[0][0];
#            rdy2 = trapeze[2][1] - trapeze[1][1];
#            rdx2 = trapeze[2][0] - trapeze[1][0];
#            rZ1 = math.atan2( rdy1, -rdx1 );
#            rZ2 = math.atan2( rdy2, -rdx2 );
#            rAngleZ = (rZ1 - rZ2) / 2;
#            rAngleZ *= 8; # 8 is the magic corresponding to the field of view of our camera
#
#            rDist = (rRealSize * (1.41 / 2.0) / (math.tan(self.fovD / 2.0)))  / rSize
#            #rDist *= math.cos(rHeadYawAngle)
#            theta = rHeadYawAngle
#
#            coord_datamatrix = topology._polarToCartesian(rDist, theta)
#            vect_normal = - np.array(topology._polarToCartesian(1, rAngleZ))
#            self.addPointToLocal(self.nCurLocalVs, strLabel, coord_datamatrix, vect_normal)
#            angleZ = 

def autoTest_dataMatrix():
    # New API:
    dataMatrixFMTOnImage = [[0, 0], [], [], [], 's_1368715299451276', 3, [], [[['FRI'], [0, [0.25397202372550964, 0.12455330789089203], [0.06307802349328995, 0.07784582674503326]], [9, [0.253296822309494, 0.13075721263885498], [0.2520856559276581, 0.20306813716888428], [0.1896490454673767, 0.19507881999015808], [0.1896490454673767, 0.12495400756597519], 4.729842185974121], [[334.81353759765625, 631.1724853515625], [336.2727966308594, 714.7734375], [411.5, 705.5367431640625], [411.5, 624.4632568359375]]]]]
    decoded = datamatrix_decodeInfo(dataMatrixFMTOnImage)
    print( "decoded:\n%s" % decoded );
    assert( len(decoded.marks) == 1 );
    assert( decoded.marks[0].strName == "FRI" );
    assert( len( decoded.marks[0].aCornersAngle) == 4 );


    dataMatrixFMTOnCamera = [[1253152980, 876669], [0.05168341100215912, -0.005454219877719879, 0.4350603520870209, 0.024001266807317734, -0.3751111328601837, 0.017715394496917725], [5.284880638122559, 7.125033378601074, 0.4350603520870209, 0.02400125004351139, -0.3751111626625061, 2.3846797943115234], [0.0271149892359972, 0.0007061260985210538, 0.20872646570205688, -9.313225746154785e-10, -0.40555036067962646, 0.02603602595627308], 'CameraTop', 3, [0.02603602409362793, -0.42649388313293457], [[['230'], [0, [-0.005809792783111334, -0.046707503497600555], [0.27721133828163147, 0.2958141565322876]], [9, [-0.27894389629364014, 0.24564769864082336], [-0.2837458550930023, -0.04104948416352272], [-0.011059122160077095, -0.0460098497569561], [-0.006090942304581404, 0.25061115622520447], 1.5533430576324463], [[976.0875244140625, 764.0009765625], [981.8731689453125, 432.5414123535156], [653.3246459960938, 426.80657958984375], [647.3387451171875, 769.7393798828125]]]]]
    decoded = datamatrix_decodeInfo(dataMatrixFMTOnCamera)
    print( "decoded:\n%s" % decoded );
    assert( len(decoded.marks) == 1 );
    assert( decoded.marks[0].strName == "230" );
    assert( len( decoded.marks[0].aCornersAngle) == 4 );
    print decoded  # todo coriger la premiere partie / écrire autotest/assert..

#    newDatamatrixFmt = [[1334415318, 707285], [[[0, [0.001659954315982759, 0.05362715199589729], [0.13611572980880737, 0.1349327713251114]], ['P02'], [9, [0.06307800859212875, -0.013839269988238811], [0.06971783190965652, 0.11417387425899506], [-0.053118348121643066, 0.1210934966802597], [-0.06639792025089264, -0.013839269988238811]]]], [0.07232627272605896, -0.02259776182472706, 0.5057775378227234, -0.00015980497119016945, -0.03767629340291023, -0.12897777557373047], [0.3167612850666046, 0.032817292958498, 0.5057775378227234, -0.00015980470925569534, -0.03767629340291023, 0.01741587556898594], 'CameraTop'];
#    decoded = datamatrix_decodeInfo( newDatamatrixFmt );
#
#    decoded = datamatrix_decodeInfo( [] );
#    print( "decoded:\n%s" % decoded );
#    assert( decoded.imageInfo.nTimeStamp == 0 );
#    assert( len(decoded.marks) == 0 );
#
#    newDatamatrixFmtAndAngle = [[1334504770, 432107], [[[0, [-0.021579312160611153, -0.005189717281609774], [0.11619636416435242, 0.1210935115814209]], ['P06'], [9, [0.03651886805891991, -0.055357031524181366], [0.028219128027558327, 0.055357031524181366], [-0.07967749238014221, 0.04497759789228439], [-0.0680578425526619, -0.06573648750782013], 4.782202243804932]], [[0, [0.18093432486057281, -0.03719300776720047], [0.10955656319856644, 0.11244398355484009]], ['P05'], [9, [0.2307327687740326, -0.09341500699520111], [0.23571263253688812, 0.015569175593554974], [0.13113588094711304, 0.019028987735509872], [0.1261560618877411, -0.09168510138988495], 4.66002893447876]]], [0.07759957015514374, -0.01012600027024746, 0.42497560381889343, 0.010077138431370258, -0.126565620303154, -0.09078516066074371], [0.0771368145942688, -0.01191205345094204, 0.42497560381889343, 0.010077139362692833, -0.126565620303154, -0.09522870928049088], 'CameraTop', [0.042124245315790176, -0.0038247262127697468, 0.20205019414424896, 0.0, -0.2138005644083023, -0.09054803848266602]]
#    decoded = datamatrix_decodeInfo( newDatamatrixFmtAndAngle );
#    print( "decoded:\n%s" % decoded );
#    assert( len(decoded.marks) == 2 );
#    assert( decoded.marks[0].strName == "P06" );
#    assert( decoded.marks[0].rAngleX == 4.7822022438049316 );
#    assert( len( decoded.marks[0].trapeze ) == 4 );
#
#
#    newDatamatrixFmtAndAngleAndYawtorso = [[1366623551, 609390], [[[0, [-0.16931471228599548, 0.2508365511894226], [0.10291676968336105, 0.10725425183773041]], ['C00'], [9, [-0.1195162683725357, 0.1972094476222992], [-0.11785628646612167, 0.3010038733482361], [-0.22077307105064392, 0.3044636845588684], [-0.21745316684246063, 0.1972094476222992], 4.6949357986450195]], [[0, [0.0904671773314476, 0.27592021226882935], [0.11121651530265808, 0.11244398355484009]], ['P07'], [9, [0.13777567446231842, 0.2196982502937317], [0.14607541263103485, 0.32868239283561707], [0.039838746190071106, 0.3321422040462494], [0.03485891595482826, 0.22142812609672546], 4.642575740814209]]], [0.02870846726000309, -0.015019143931567669, 0.5298012495040894, 0.015923738479614258, -0.15698716044425964, -0.043140046298503876], [0.03807978332042694, -0.010408011265099049, 0.5298012495040894, 0.015923738479614258, -0.15698717534542084, -0.034713078290224075], 'CameraTop', [0.047929633408784866, -0.00176739483140409, 0.19858703017234802, 0.0, -0.13710033893585205, -0.03685808181762695], 3]
#    decoded = datamatrix_decodeInfo( newDatamatrixFmtAndAngleAndYawtorso )
#    print( "decoded:\n%s" % decoded );
#
#    datamatrix_getLookAt( newDatamatrixFmtAndAngleAndYawtorso )
#    assert( len(decoded.marks) == 2 );
#    assert( decoded.marks[0].strName == "C00" );
#    assert( decoded.marks[0].rAngleX == 4.6949357986450195 );
#    assert( len( decoded.marks[0].trapeze ) == 4 );
#
#
#    visionRecoData =  [];
#    decoded = visionRecognition_decodeInfo( visionRecoData );
#    print( "decoded:\n%s" % decoded );
#    assert( len(decoded.objects) == 0 );
#
#    visionRecoData =  [[1377526293, 549855], [[['Front', 'TeeShirtRobocup2013'], 58, 0.3717, [[0.26685482263565063, -0.2260037660598755], [-0.2222311943769455, -0.26034167408943176], [-0.25553804636001587, 0.30428823828697205], [0.2924065887928009, 0.2379956692457199]]]]];
#    decoded = visionRecognition_decodeInfo( visionRecoData );
#    print( "decoded:\n%s" % decoded );
#    assert( len(decoded.objects) == 1 );
#    assert( decoded.objects[0].strName == 'TeeShirtRobocup2013' );
#    assert( decoded.objects[0].strSide == 'Front' );
#    assert( decoded.objects[0].rConfidence == 0.3717 );
#    assert( decoded.objects[0].nNbrPoints == 58 );



# autoTest_dataMatrix - end    



class VisionRecognitionInfo:
    """
    Info about one seen object.
    a good validation test: using rMinConf a 0.32:  if( o.rConfidence >= rMinConf or o.nNbrPoints >= rMinConf * 140 ):
    """
    def __init__( self, data_for_one ):
        self.reset();
        self.strName = data_for_one[0][1];
        self.strSide = data_for_one[0][0];
        self.rConfidence = data_for_one[2];
        self.nNbrPoints = data_for_one[1];
        self.boundaries = data_for_one[3];
        assert( len(self.boundaries) == 4 );
            
    def reset( self ):
        self.strName = "???";
        self.strSide = "";
        self.rConfidence = 0.; # [0..1]
        self.nNbrPoints = 0; # nbr points recognized
        self.boundaries = []; # BoundaryPoint is a list of points coordinates in angle values (radian) representing the reprojection in the current image of the boundaries selected during the learning stage.
    # reset - end

    def __str__( self ):
        strOut = "";
        strOut += "strName: '%s'\n" % self.strName;
        strOut += "strSide: '%s'\n" % str( self.strSide );
        strOut += "rConfidence: %5.3f\n" % self.rConfidence;
        strOut += "nNbrPoints: %d\n" % self.nNbrPoints;
        strOut += "boundaries: %s\n" % str( self.boundaries );
        return strOut;
        
# class DatamatrixInfo - end        

class VisionRecognitionInfos:
    """
    Info of one round of visionreco detection (it contains info about a bunch of datamatrix)
    """        
    def __init__( self, data ):
        self.reset();
        if( len(data) < 2 ):
            return;
        self.timestamp, objs = data;
        for o in objs:
            self.objects.append( VisionRecognitionInfo( o ) );
        
    def reset( self ):
        self.timestamp = [0,0];
        self.objects = [];        
        
                
    def __str__( self ):
        strOut = "";
        strOut += "VisionRecognitionInfo:\n";
        strOut += "TimeStamp:%s\n" % self.timestamp;
        strOut += "detected: %d object(s):\n" % len( self.objects );
        for object in self.objects:
            strOut += str( object );
        return strOut;
# class VisionRecognitionInfos - end

def visionRecognition_decodeInfo( data ):
    """
    Take "THE" big array and return a created object containing nammed fields
    return a visionInfos object
    - data: data from extractors
    """
    return VisionRecognitionInfos( data );
# visionRecognition_decodeInfo - end

class ExtraInfo:
    """
    Info about detail of a face (eyes position, ...)
    """
    def __init__( self, data ):
        self.reset();
        print( "FaceDetectionInfo: constructing from %s" % str( data ) );
        self.nFaceID = data[0];
        self.rScoreReco = data[1];
        self.strFaceLabel = data[2];
        self.aLeftEyePoints = data[3];
        self.aRightEyePoints = data[4];
        self.aLeftEyebrowPoints = data[5];
        self.aRightEyebrowPoints = data[6];
        self.aNosePoints = data[7];
        self.aMouthPoints = data[8];
            
    def reset( self ):
        self.nFaceID = -1;
        self.rScoreReco = -1;
        self.strFaceLabel = "";
        self.aLeftEyePoints = [];
        self.aRightEyePoints = [];
        self.aLeftEyebrowPoints = [];
        self.aRightEyebrowPoints = [];
        self.aNosePoints = [];
        self.aMouthPoints = [];
    # reset - end

    def __str__( self ):
        strOut = "";
        strOut += "  nFaceID: '%s'\n" % self.nFaceID;
        strOut += "  rScoreReco: %s\n" % self.rScoreReco;
        strOut += "  strFaceLabel: '%s'\n" % self.strFaceLabel;
        strOut += "  aLeftEyePoints: %s\n" % self.aLeftEyePoints;
        strOut += "  aRightEyePoints: %s\n" % self.aRightEyePoints;
        strOut += "  aLeftEyebrowPoints: %s\n" % self.aLeftEyebrowPoints;
        strOut += "  aLeftEyebrowPoints: %s\n" % self.aLeftEyebrowPoints;
        strOut += "  aNosePoints: %s\n" % self.aNosePoints;
        strOut += "  aMouthPoints: %s\n" % self.aMouthPoints;
        return strOut;
# class ExtraInfo - end    

class FaceDetectionInfo:
    """
    Info about one seen face
    """
    def __init__( self, data ):
        self.reset();
        #~ print( "FaceDetectionInfo: constructing from %s" % str( data ) );
        self.aShapeInfo = data[0];
        self.aExtraInfos = ExtraInfo(data[1]);
            
    def reset( self ):
        self.faceInfo = [];
    # reset - end

    def __str__( self ):
        strOut = "";
        strOut += " aShapeInfo: %s\n" % self.aShapeInfo;
        strOut += " aExtraInfos:\n%s\n" % self.aExtraInfos;
        return strOut;
# class FaceDetectionInfo - end        

class FaceDetectionInfos:
    """
    Info of one round of visionreco detection (it contains info about a bunch of faces)
    """        
    def __init__( self, data ):
        self.reset();
        
        if( data == None or len(data) < 2 ):
            return;
        self.timestamp, objs, self.aCameraPose_InTorsoFrame, self.aCameraPose_InRobotFrame, self.nCamera_Id = data;
        #~ print( "objs: %s" % str( objs ) );
        for o in objs[:-1]:
            #~ print( "o: %s" % str( o ) );
            self.objects.append( FaceDetectionInfo( o ) );
        self.aTime_Filtered_Reco_Info = objs[-1];
        
    def reset( self ):
        self.timestamp = [0,0];
        self.objects = [];
        self.aTime_Filtered_Reco_Info = [];
        self.aCameraPose_InTorsoFrame = [0,0,0];
        self.aCameraPose_InRobotFrame = [0,0,0];
        self.nCamera_Id = -1;        
                
    def __str__( self ):
        strOut = "";
        strOut += "FaceDetectionInfos:\n";
        strOut += "TimeStamp: %s\n" % self.timestamp;
        strOut += "detected: %d object(s):\n" % len( self.objects );
        for object in self.objects:
            strOut += str( object );
        strOut += "aCameraPose_InTorsoFrame: %s\n" % self.aCameraPose_InTorsoFrame;
        strOut += "aCameraPose_InRobotFrame: %s\n" % self.aCameraPose_InRobotFrame;
        strOut += "nCamera_Id: %s\n" % self.nCamera_Id;

        return strOut;
# class FaceDetectionInfos - end

def FaceDetection_decodeInfos( data ):
    """
    Take "THE" big array and return a created object containing nammed fields
    return a visionInfos object
    - data: data from extractors
    """
    return FaceDetectionInfos( data );
# FaceDetection_decodeInfos - end
    
def drawPoints( img, listPoints, aColor = (255,0,0) ):
    """
    add a list of point to the image (listPoints: a list as [pt1x, pt1y, pt2x, pt2y, ...])
    """
    import cv2    
    w = img.shape[1];
    h = img.shape[0];
    for i in range( 0, len( listPoints ), 2 ):
        ptx = listPoints[i];
        pty = listPoints[i+1];
        if( ptx != 0. or pty != 0. ):
            cv2.circle( img, arraytools.convertAngleToImagePixels(ptx, pty, w,h), 1, aColor );    
    # drawPoints - end

def FaceDetection_drawResultsOnImage( faceDetectionInfo, strFilenameImageSrc, strFilenameImageDst = None ):
    """
    take data from face detection info and output detected point in the image. Final image is stored to strFilenameImageDst.
    - faceDetectionInfo: info from detection
    - strFilenameImageSrc: image source from detection
    - strFilenameImageDst: alternate filename to store results (optionnal)
    return true on success
    """
    if( strFilenameImageDst == None ):
        strFilenameImageDst = strFilenameImageSrc;
    import cv2
    img = cv2.imread( strFilenameImageSrc );
    if( img == None ):
        print( "ERR: FaceDetection_drawResultsOnImage: can't open src image file: '%s'" % strFilenameImageSrc );
        return False;
    w = img.shape[1];
    h = img.shape[0];
    print( "w: %s" % w );
    print( "h: %s" % h );
    #~ nThickness = 2;
    #~ font = cv2.initFont( cv2.CV_FONT_HERSHEY_SIMPLEX, 0.5, 0.5, 0, nThickness, 8 );            
    for object in faceDetectionInfo.objects:
        shape = object.aShapeInfo[1:];
        print( "shape: %s" % shape );
        center = arraytools.convertAngleToImagePixels(shape[0],shape[1],w,h)
        print( "center: %s" % str(center) );
        size = arraytools.convertSizeToImagePixels(shape[2],shape[3],w,h)
        print( "size: %s" % str(size) );
        pt1 = ( center[0]-size[0]/2, center[1]-size[1] ); # tuple(map(lambda x, y: x + y, pt1, size))
        pt2 = ( center[0]+size[0]/2, center[1]+size[1] );
        cv2.rectangle( img, pt1,pt2, (255,0,0) );        
        if( len(object.aExtraInfos.strFaceLabel) > 0 ):
            strText = object.aExtraInfos.strFaceLabel.split("__")[0];
            strText += "%6.2f" % object.aExtraInfos.rScoreReco;
            textSize = cv2.getTextSize( strText, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1 );
            print( str( textSize ) );
            colorText = (255,255,0);
            if( object.aExtraInfos.rScoreReco < 0.30):
                colorText = (80,80,0);
            if( object.aExtraInfos.rScoreReco < 0.20):
                colorText = (40,40,40);                
            cv2.putText( img, strText, ((pt1[0]+pt2[0])/2-(textSize[0][0]/2), pt2[1]-4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colorText );
        
        drawPoints( img, object.aExtraInfos.aLeftEyePoints, (255,0,0) );
        drawPoints( img, object.aExtraInfos.aRightEyePoints, (255,128,0) );
        drawPoints( img, object.aExtraInfos.aNosePoints, (0,255,0) );
        drawPoints( img, object.aExtraInfos.aMouthPoints, (0,0,255) );
    bRet = cv2.imwrite( strFilenameImageDst, img );
    if( not bRet ):
        print( "ERR: FaceDetection_drawResultsOnImage: can't open dest image file: '%s'" % strFilenameImageDst );        
        return False;
    return True;    
# FaceDetection_drawResultsOnImage - end
    

def autoTest_FaceDetection():
    dataIn = [[1275896248, 349847], [[[0, 0.2489922046661377, 0.13493278622627258, 0.3585487902164459, 0.37365996837615967], [-1, 0.0, '', [0.2821911573410034, 0.08303557336330414, 0.2821911573410034, 0.08303557336330414, 0.3187100291252136, 0.08649538457393646, 0.2987906336784363, 0.07265608757734299, 0.2987906336784363, 0.08303557336330414, 0.31207022070884705, 0.07265608757734299, 0.2921508550643921, 0.07265608757734299], [0.18923406302928925, 0.09341500699520111, 0.21579323709011078, 0.09341500699520111, 0.165994793176651, 0.09687481820583344, 0.19255398213863373, 0.07957576215267181, 0.19255398213863373, 0.09687481820583344, 0.2058335393667221, 0.07957576215267181, 0.18259428441524506, 0.07957576215267181], [0.2821911573410034, 0.055357031524181366, 0.30875033140182495, 0.04843740910291672, 0.5345032811164856, -0.41863757371902466], [0.21911315619945526, 0.07265608757734299, 0.18923406302928925, 0.06919627636671066, 0.5345032811164856, -0.41863757371902466], [0.2456722855567932, 0.14877203106880188, 0.27223145961761475, 0.14877203106880188, 0.21579323709011078, 0.14877203106880188], [0.2821911573410034, 0.20066925883293152, 0.2124733328819275, 0.20066925883293152, 0.2489922046661377, 0.17645053565502167, 0.2489922046661377, 0.24564684927463531, 0.26559168100357056, 0.179910346865654, 0.22907280921936035, 0.17645053565502167, 0.22907280921936035, 0.23180755972862244, 0.26559168100357056, 0.23180755972862244]]], []], [], [], 0];
    data = FaceDetection_decodeInfos(dataIn);
    print data;
    
    dataIn = [[0, -1], [[[0, 0.05978844314813614, 0.010384699329733849, 0.17438293993473053, 0.1817324161529541], [1, 0.40300002694129944, 'romain_duris__1974', [0.08802185207605362, -0.017307857051491737, 0.07307475060224533, -0.013846290297806263, 0.10296899080276489, -0.013846290297806263, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.014947103336453438, -0.017307857051491737, 0.029894206672906876, -0.013846290297806263, -0.0, -0.015577074140310287, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0523148775100708, 0.025961773470044136, 0.06809239089488983, 0.025961773470044136, 0.03653739020228386, 0.025961773470044136], [0.08137869834899902, 0.06750062108039856, 0.019929490983486176, 0.06750062108039856, 0.051484495401382446, 0.04673117399215698, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]], []], [], [], -1]
    data1 = FaceDetection_decodeInfos(dataIn);
    print data1;
    FaceDetection_drawResultsOnImage( data1, "c:\\pic\\0_0003478s988.jpg", "c:\\tempo\\debug1.jpg" );
    
    dataIn = [[0, -1], [[[0, -0.07473554462194443, 0.06750062108039856, 0.0996473953127861, 0.10384709388017654], [2, 0.40300002694129944, 'romain_duris__1974', [-0.04982369765639305, 0.05365435406565666, -0.05812764912843704, 0.05538511276245117, -0.03985898196697235, 0.05365435406565666, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [-0.0946650356054306, 0.05192354694008827, -0.08470026403665543, 0.05538511276245117, -0.10629057884216309, 0.05365435406565666, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [-0.06975319236516953, 0.08307769149541855, -0.05978841334581375, 0.08307769149541855, -0.07971790432929993, 0.08307769149541855], [-0.05314528942108154, 0.10730866342782974, -0.09134344756603241, 0.10730866342782974, -0.06975319236516953, 0.09692396223545074, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]], []], [], [], -1]
    data2 = FaceDetection_decodeInfos(dataIn);
    print data2;
    FaceDetection_drawResultsOnImage( data2, "c:\\pic\\0_0003666s390.jpg", "c:\\tempo\\debug2.jpg" );


    dataIn = [[0, -1], [[[0, 0.009964745491743088, -0.041538845747709274, 0.2972813844680786, 0.30981048941612244], [1, 1.0, 'romain_duris__1974', [0.07639634609222412, -0.07096219062805176, 0.051484495401382446, -0.06750062108039856, 0.0996473953127861, -0.06923140585422516, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [-0.03653739020228386, -0.08307766914367676, -0.011625542305409908, -0.07615453749895096, -0.05978841334581375, -0.08653923869132996, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.012455924414098263, 0.0017308080568909645, 0.04151974618434906, 0.005192374344915152, -0.016607899218797684, -0.0017307832604274154], [0.06975319236516953, 0.038077279925346375, -0.05314528942108154, 0.024230966344475746, 0.008303949609398842, 0.031154148280620575, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]], []], [], [], -1]
    #~ dataIn = [[0, -1], [[[0, 0.006239546462893486, -0.028994278982281685, 0.32445672154426575, 0.33504506945610046], [188, 1.0, 'romain_duris__1974', [0.06863506883382797, -0.06604254245758057, 0.04679664224386215, -0.06282095611095428, 0.09047349542379379, -0.06443174928426743, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [-0.03275762498378754, -0.07731808722019196, -0.012479092925786972, -0.07087491452693939, -0.05459608510136604, -0.08053966611623764, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.010919228196144104, 0.004026968497782946, 0.03587741404771805, 0.00644316803663969, -0.01403901632875204, 0.0016108150593936443], [0.057715870440006256, 0.041880637407302856, -0.04367685690522194, 0.030605072155594826, 0.0077994405291974545, 0.03221588581800461, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]], []], [], [], -1]
    # offline on the robot wo learning:
    #~ dataIn = [[0, -1], [[[0, 0.009359334595501423, -0.03865905478596687, 0.27921995520591736, 0.2883320450782776], [1, 0.0, '', [0.07175485789775848, -0.06604254245758057, 0.04835653677582741, -0.06282095611095428, 0.0935932844877243, -0.06443174928426743, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [-0.03431754931807518, -0.07731808722019196, -0.010919228196144104, -0.07087491452693939, -0.05615594983100891, -0.08053966611623764, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.011699160560965538, 0.0016108150593936443, 0.03899720311164856, 0.0048323990777134895, -0.015598881058394909, -0.0016107920091599226], [0.06551530957221985, 0.03543746843934059, -0.049916431307792664, 0.02255108766257763, 0.0077994405291974545, 0.028994301334023476, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]], []], [], [], -1]
    # online on the robot with learning
    #~ dataIn = [[0, -1], [[[0, 0.009359334595501423, -0.03865905478596687, 0.27921995520591736, 0.2883320450782776], [1, 1.0, 'romain_duris__1974', [0.07175485789775848, -0.06604254245758057, 0.04835653677582741, -0.06282095611095428, 0.0935932844877243, -0.06443174928426743, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [-0.03431754931807518, -0.07731808722019196, -0.010919228196144104, -0.07087491452693939, -0.05615594983100891, -0.08053966611623764, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.011699160560965538, 0.0016108150593936443, 0.03899720311164856, 0.0048323990777134895, -0.015598881058394909, -0.0016107920091599226], [0.06551530957221985, 0.03543746843934059, -0.049916431307792664, 0.02255108766257763, 0.0077994405291974545, 0.028994301334023476, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]], [2, ['romain_duris__1974']]], [], [], -1]
    # online on the robot with learning alt
    #~ dataIn = [[0, -1], [[[0, 0.009359334595501423, -0.03865905478596687, 0.2698606252670288, 0.27866730093955994], [1, 1.0, 'romain_duris__1974', [0.07019496709108353, -0.06604254245758057, 0.04679664224386215, -0.06443174928426743, 0.09203339368104935, -0.06443174928426743, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [-0.03431754931807518, -0.0789288803935051, -0.012479092925786972, -0.07087491452693939, -0.057715870440006256, -0.08215045928955078, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.010919228196144104, 0.003221584018319845, 0.037437308579683304, 0.00644316803663969, -0.015598881058394909, 0.0], [0.062395524233579636, 0.03704823926091194, -0.049916431307792664, 0.02416190318763256, 0.0077994405291974545, 0.030605072155594826, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]], []], [], [], -1]    
    dataIn = [[0, -1], [[[0, 0.014038987457752228, -0.043491430580616, 0.2620611786842346, 0.27061331272125244], [1, 1.0, 'romain_duris__1974', [0.07019496709108353, -0.06443174928426743, 0.04679664224386215, -0.06282095611095428, 0.0935932844877243, -0.06282095611095428, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [-0.03587741404771805, -0.07731808722019196, -0.01403901632875204, -0.06926412880420685, -0.059275735169649124, -0.08053966611623764, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.010139266960322857, 0.004026968497782946, 0.037437308579683304, 0.00644316803663969, -0.017158744856715202, 0.0016108150593936443], [0.06395541876554489, 0.03704823926091194, -0.053036220371723175, 0.02416190318763256, 0.0077994405291974545, 0.03221588581800461, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]], []], [], [], -1]
    data3 = FaceDetection_decodeInfos(dataIn);
    print data3;
    FaceDetection_drawResultsOnImage( data3, "C:\\work\\Dev\\git\\appu_data\\faces\\famous\\640x480\\romain_duris__1974.jpg", "c:\\tempo\\debug3.jpg" );
    
    if( 0 ):
        import image_morphing
        
        strHumanFilename = "c:\\pic\\0_0003478s988.jpg";
        strRefFilename = "C:\\work\\Dev\\git\\appu_data\\faces\\famous\\640x480\\romain_duris__1974.jpg";
        object = data1.objects[0];
        aFacePosHuman = object.aShapeInfo[1:];
        aListPointHuman = [];
        aListPointHuman.extend( arraytools.listPointToTuple( object.aExtraInfos.aLeftEyePoints ) );
        aListPointHuman.extend( arraytools.listPointToTuple( object.aExtraInfos.aRightEyePoints ) );                    
        aListPointHuman.extend( arraytools.listPointToTuple( object.aExtraInfos.aNosePoints ) );                    
        aListPointHuman.extend( arraytools.listPointToTuple( object.aExtraInfos.aMouthPoints ) );                                        
        object = data3.objects[0];
        aFacePosRef = object.aShapeInfo[1:];        
        aListPointRef = [];        
        aListPointRef.extend( arraytools.listPointToTuple( object.aExtraInfos.aLeftEyePoints ) );
        aListPointRef.extend( arraytools.listPointToTuple( object.aExtraInfos.aRightEyePoints ) );                    
        aListPointRef.extend( arraytools.listPointToTuple( object.aExtraInfos.aNosePoints ) );                    
        aListPointRef.extend( arraytools.listPointToTuple( object.aExtraInfos.aMouthPoints ) );                                                
        image_morphing.generateMorphData( strHumanFilename, aFacePosHuman, aListPointHuman, strRefFilename, aFacePosRef, aListPointRef );        
# autoTest_FaceDetection - end


class FaceDetectionNewInfo:
    """
    Info about one seen face
    """
    
    class FaceInfo:
        def __init__(self, rawData=None):
            self.reset();
            if( rawData != None ):
                self.id = rawData[0];
                self.vertices = rawData[1:5];
                self.rPose =  rawData[5];
                self.rConfidence =  rawData[6];
                
        def reset(self):
            self.id = -1;
            self.vertices = [];
            self.rPose = 0.;
            self.rConfidence = 0.;
            
        def __str__( self ):
            strOut = "";
            strOut += "  id: %s\n" % self.id;
            strOut += "  vertices:%s\n" % self.vertices;
            strOut += "  rPose:%s\n" % self.rPose;
            strOut += "  rConfidence:%s\n" % self.rConfidence;
            return strOut;
    # class FaceInfo - end
    
    class FaceDirection:
        def __init__(self,rawData=None):
            if( rawData != None ):
                self.rPitch, self.rYaw, self.rRoll =  rawData;
            
        def __str__( self ):
            strOut = "";
            strOut += "  pitch:%s\n" % self.rPitch;
            strOut += "  yaw:%s\n" % self.rYaw;
            strOut += "  roll:%s\n" % self.rRoll;
            return strOut;
    # class FaceDirection - end



    def __init__( self, data ):
        self.reset();
        #~ print( "FaceDetectionNewInfo: constructing from %s" % str( data ) );
        faceInfo = data[0];
        self.faceInfo = self.FaceInfo(faceInfo);
        
        #  facialParts: Pour chaque point du visage : [[x, y], confidence] où x, y  sont les coordonnées dans l'image et confidence est la confiance entre 0 et 1
            #~ POINT_LEFT_EYE,            /* Left Eye Center    */
            #~ POINT_RIGHT_EYE,               /* Right Eye Center   */
            #~ POINT_MOUTH,                   /* Mouth Center       */
            #~ POINT_LEFT_EYE_IN,             /* Left Eye In        */
            #~ POINT_LEFT_EYE_OUT,            /* Left Eye Out       */
            #~ POINT_RIGHT_EYE_IN,            /* Right Eye In       */
            #~ POINT_RIGHT_EYE_OUT,           /* Right Eye Out      */
            #~ POINT_MOUTH_LEFT,              /* Mouth Left         */
            #~ POINT_MOUTH_RIGHT,             /* Mouth Right        */
            #~ POINT_NOSE_LEFT,               /* Nose Left          */
            #~ POINT_NOSE_RIGHT,              /* Nose Right         */
            #~ POINT_MOUTH_UP,                /* Mouth Up           */
        
        self.facialParts = data[1];
        self.faceDirection = self.FaceDirection( data[2] );
        self.age = data[3][0]; # age (int), entre 0 et 75 et confidence
        self.gender = data[3][1]; # gender (0 => male, 1 => female) et confidence
        self.smile = data[4]; # degré de sourire entre 0 (pas de smile) et 1 (big smile) suivi de confidence entre 0 et 1
        if( len(data)> 5 and data[5] != None ):
            # handle old and new format: recognised could be a [name, confidence] or a  [[name1, confidence1], [name2, confidence2] , [name3, confidence3]  ] NDEV
            #~ print( "DBG: old and new format: data[5]: '%s'" % data[5] );
            self.recognised = data[5];
        else:
            #self.recognised = [-1,"",0.]
            self.recognised = []
            
            
    def reset( self ):
        self.faceInfo = [];
    # reset - end

    def __str__( self ):
        strOut = "";
        strOut += " FaceInfo:\n%s\n" % self.faceInfo;
        strOut += " FacialParts:%s\n" % self.facialParts;
        strOut += " FaceDirection:\n%s\n" % self.faceDirection;
        strOut += " Age: %s\n" % self.age;
        strOut += " Gender: %s\n" % self.gender;
        strOut += " Smile: %s\n" % self.smile;
        strOut += " Recognised: %s\n" % self.recognised;
        return strOut;
# class FaceDetectionNewInfo - end        

class FaceDetectionNewInfos:
    """
    Info of one round of face reco detection (it contains info about a bunch of faces)
    """        
    def __init__( self, data = None ):
        self.reset();
        if( data == None ):
            return;
        for o in data:
            #~ print( "o: %s" % str( o ) );
            self.objects.append( FaceDetectionNewInfo( o ) );
        
    def reset( self ):
        self.objects = [];
      
                
    def __str__( self ):
        strOut = "";
        strOut += "FaceDetectionNewInfos (%d objects):\n" % len(self.objects);
        for object in self.objects:
            strOut += str( object );
        return strOut;
# class FaceDetectionNewInfos - end

def FaceDetectionNew_decodeInfos( data ):
    """
    Take "THE" big array and return a created object containing nammed fields
    return a visionInfos object
    - data: data from extractors
    """
    return FaceDetectionNewInfos( data );
# FaceDetectionNew_decodeInfos - end

def FaceDetectionNew_select_face( faceDetectionNewInfos, nTryFocusOnID = -1 ):
    """
    sort face so the most interesting is in first (the biggest and more at the center)
    - nTryFocusOnID: if provided: it should be the previous selected, so we keep focus on this one
    """
    import numeric
    w = 320;
    h = 240
    nMaxScore = -1024*1024*1024; # INT_MIN
    nIdxBest = -1;
    for i in range(len( faceDetectionNewInfos.objects ) ):
        if( nTryFocusOnID != -1 and faceDetectionNewInfos.objects[i].faceInfo.id == nTryFocusOnID ):
            print( "INF: FaceDetectionNew_select_face, continue to focus on %s" % nTryFocusOnID );
            nIdxBest = i;
            break;
        xt, yt, xb, yb = numeric.findBoundingBox( faceDetectionNewInfos.objects[i].faceInfo.vertices );
        facew = xb-xt;
        faceh = yb-yt;        
        nScore = 0; # all distances are compared in square
        nScore += facew*faceh*8; # *8: it's a parameter to make the size weight "more quite the same" compared to the distance
        dx = ( w / 2 ) - ( xt + (facew/2) );
        dy = ( h / 2 ) - ( yt + (faceh/2) );
        nScore -= dx*dx+dy*dy;
        if( nScore > nMaxScore ):
            nMaxScore = nScore;
            nIdxBest = i;
            
    # now the best is in idx...
    out = FaceDetectionNewInfos();
    if( nIdxBest != -1 ):
        print( "INF: FaceDetectionNew_select_face, selected face %d, id: %s" % (nIdxBest, faceDetectionNewInfos.objects[nIdxBest].faceInfo.id) );
        out.objects.append( faceDetectionNewInfos.objects[nIdxBest] );
    return out;    
# FaceDetectionNew_select_face - end


global_graphResults = dict();  # a dictionnary of nFaceID => graph Figure
def FaceDetectionNew_drawResultsOnOpenedImage( faceDetectionNewInfos, img, rTime = None, rScale = 1., bGraph = False ):
    """
    - rTime: time used from information
    """
    import cv2.cv as cv
    import cv2    
    w = img.shape[1];
    h = img.shape[0];
    #~ print( "w: %s" % w );
    #~ print( "h: %s" % h );
    nFontThickness = 2;
    nFontScale = 0.8;
    font = cv.InitFont( cv.CV_FONT_HERSHEY_SIMPLEX, nFontScale, nFontScale, 0, nFontThickness, 8 );
    
    if( bGraph ):
        import figure
        global global_graphResults;
    #global_graphResults[0].saveToFile("/tmp/0.png");
    
    if( rTime == None ):
        rTime = time.time();
    
    
                
    bPlotted = False;
    
    for object in faceDetectionNewInfos.objects:
        colorRect = ( 128, 128, 128 );
        
        facialParts = object.facialParts;

        
                
        if( bGraph ):
            if( object.faceInfo.id not in global_graphResults.keys() ):
                global_graphResults[object.faceInfo.id] = figure.Plotter();
                global_graphResults[object.faceInfo.id].setAxisRange( [0,3], [-1,1] )
        rFaceCenterX = int( ( object.faceInfo.vertices[0][0] + object.faceInfo.vertices[1][0] ) / 2*rScale );
        rFaceTop = int(object.faceInfo.vertices[1][1]*rScale );
        rFaceBottom = int(object.faceInfo.vertices[3][1]*rScale );
        #~ print( "rFaceCenterX: %s, rFaceBottom: %s" % (rFaceCenterX, rFaceBottom ) );

        strTextAge = "id_" + str(object.faceInfo.id);            
        strTextGender = None;
        
        
        if( 1 ):
            # mouth:
            # 0 mil oeil a gauche, 1 mil oeil droite, 2 centre bas bouche, 5 interieur oeil droite, 6 ext oeil droite, 7 coin gauche bouche, 8 coin droit bouche, 9 narine gauche, 10 narine droite, 11 haut de la bouche
            if( facialParts[2][1] > 0.8 ):
                colorMouthLow = img[facialParts[2][0][1], facialParts[2][0][0] ];
                colorMouthHigh = img[facialParts[11][0][1], facialParts[11][0][0] ];
                colorMouthLeft = img[facialParts[7][0][1], facialParts[7][0][0] ];
                colorMouthRight = img[facialParts[8][0][1], facialParts[8][0][0] ];
                print( "colorMouthLow: %s - %s" % (colorMouthLow, colorMouthLow[2]*2-colorMouthLow[1]-colorMouthLow[0]) );
                print( "colorMouthHigh: %s - %s" % (colorMouthHigh, colorMouthHigh[2]*2-colorMouthHigh[1]-colorMouthHigh[0]) );
                print( "colorMouthLeft: %s" % (colorMouthLeft ) );
                print( "colorMouthRight: %s" % (colorMouthRight ) );
                rRatioColorMouthLow = colorMouthLow[2]*2-colorMouthLow[1]-colorMouthLow[0];
                if( rRatioColorMouthLow < 94 and colorMouthLow[0] > 20 and colorMouthLow[1] > 20 ):
                    strTextGender =   "(Speaking)"
        
        if( abs( rFaceCenterX ) < 2000 ):
            aColor = [(0,255,0)]*4;
            if( object.age[1] > 0.4 ):
                nGreyConfidence = int(128*object.age[1]/(1.-0.4))+127;
                aColor[1] = (0,nGreyConfidence,0);
                strTextAge += " age: %s " % object.age[0];
                #global_graphResults[object.faceInfo.id].updateValue( object.age[0] );
            else:
                strTextAge += "";
            if( object.gender[1] > 0.1 or 1 ):
                rGenderAndConfidence = object.gender[0]*object.gender[1];
                nGreyConfidence = int(128*object.gender[1]/(1.-0.2))+127;
                aColor[2] = (0,nGreyConfidence,0);
                if( 0 ):
                    if( object.gender[0] == 1 ):
                        strTextGender = "(male)";
                    else:
                        strTextGender = "(female)";
                if( bGraph ):
                    global_graphResults[object.faceInfo.id].updateValue( rGenderAndConfidence, rTime=rTime, bVerbose = True );
                    bPlotted = True;

                rGenderAndConfidence *= 20;
                rGenderAndConfidence *= -1; # bug sur Julie
                rGreyLevel = 255*(0.5-(abs(rGenderAndConfidence)/2));
                rColorLevel = 255*(abs(rGenderAndConfidence)/2)+128;
                print( "rGenderAndConfidence: %s, rGreyLevel: %s, rColorLevel: %s" % (rGenderAndConfidence,rGreyLevel,rColorLevel) );
                if( rGenderAndConfidence > 0. ):
                    # male
                    colorRect = (rColorLevel, rGreyLevel, rGreyLevel );
                else:
                    # female
                    colorRect = (rColorLevel, rGreyLevel, rColorLevel );
                
            strTextSmile = "Smile: %5.2f" % object.smile[0];
            nGreyConfidence = int(128*object.smile[1]/(1.))+127;
            aColor[3] = (0,nGreyConfidence,0);
            
            
            nDecay = 1;        
            for nIdx, strText in enumerate([strTextAge, strTextGender, strTextSmile]):
                if( strText != None ):
                    textSize = cv.GetTextSize( strText, font );
                    pt = (rFaceCenterX, rFaceBottom);
                    cv2.putText( img, strText, ((pt[0])-(textSize[0][0]/2), pt[1]+28*nDecay), cv2.FONT_HERSHEY_SIMPLEX, nFontScale, aColor[nIdx], nFontThickness );
                    nDecay += 1;
                    
            if( 1 ):
                # trucage, affichage "woman"
                if( rTime >= 1429873947.52 ):
                    strText = "WOMAN";
                    textSize = cv.GetTextSize( strText, font );
                    pt = (rFaceCenterX, rFaceTop);
                    cv2.putText( img, strText, ((pt[0])-(textSize[0][0]/2), pt[1]-6), cv2.FONT_HERSHEY_SIMPLEX, nFontScale, (255,0,255), nFontThickness );
                    
                
        # render rectangle and facial parts
        for i in range(4):
            i1 = i;
            i2 = (i+1)%4;
            if( i1 == 1 ):
                i1 = 1;
                i2 = 3;                
            elif( i1 == 3 ):
                i1 = 2;
                i2 = 0;
            
            pt1 = object.faceInfo.vertices[i1];
            pt2 = object.faceInfo.vertices[i2];
            if( abs( pt1[0] ) > 2000 or abs( pt2[0] ) > 2000 ): # a stange bug: once the vertices were :[[-540508416, 1825055232], [-1352820352, 1592128512], [-307581664, 1012743168], [-1119893632, 779816448]]
                continue;
            pt1 = (int(pt1[0]*rScale),int(pt1[1]*rScale));
            pt2 = (int(pt2[0]*rScale),int(pt2[1]*rScale));
            #~ print( "pt1: %s, pt2: %s" % (pt1, pt2 ) );
            cv2.line( img, pt1, pt2, colorRect, 2 );
            
        for part in facialParts:
            cv2.circle( img, (int(part[0][0]*rScale),int(part[0][1]*rScale)), 1, (255,255,255) );    
                            
                
    # for - end
    if( bGraph and bPlotted ):
        nLayer = 0;
        nX = 0;
        nY = 0;
        strTempFile = "/tmp/temp.png";
        for k, v in sorted(global_graphResults.iteritems()):
            # discard old graph
            if( rTime - v.getAbsoluteLastTime() > 5. ):
                print( "DBG: graph is too old: k: %s, rTime: %s, lastTime: %s" % (k, rTime,v.getAbsoluteLastTime() ) );
                continue;
            # add graph in the image
            bRet = v.saveToFile( strTempFile );
            if( bRet ):
                fig = cv2.imread( strTempFile );
                #~ dst_roi = img(nX, nY, fig.shape[1], fig.shape[0]);
                #~ figure.copyTo(dst_roi);
                resized_fig = cv2.resize(fig, (0, 0), fx=0.25, fy=0.25 ) #cv2.resize(fig, (100, 50)) 
                img[nY:nY+resized_fig.shape[0],nX:nX+resized_fig.shape[1]] = resized_fig
                nY += resized_fig.shape[0];
                if( nY+resized_fig.shape[0] >= img.shape[0] ):
                    nY = 0;
                    nX += resized_fig.shape[1];
                    if( nX+resized_fig.shape[1] >= img.shape[1] ):
                        # will overlay a bit, dirty but ...
                        nLayer += 1;
                        nX = 20*nLayer;
                        nY = 20*nLayer; 
    
                
# FaceDetectionNew_drawResultsOnOpenedImage - end
    
def FaceDetectionNew_drawResultsOnImage( faceDetectionNewInfos, strFilenameImageSrc, strFilenameImageDst = None, rScale = 1., bGraph = False ):
    """
    take data from face detection info and output detected point in the image. Final image is stored to strFilenameImageDst.
    - faceDetectionNewInfo: info from detection
    - strFilenameImageSrc: image source from detection
    - strFilenameImageDst: alternate filename to store results (optionnal)
    return true on success
    """
    if( strFilenameImageDst == None ):
        strFilenameImageDst = strFilenameImageSrc;
    import cv2
    img = cv2.imread( strFilenameImageSrc );
    if( img == None ):
        print( "ERR: FaceDetectionNew_drawResultsOnImage: can't open src image file: '%s'" % strFilenameImageSrc );
        return False;
        
    rTimeFromImage = strFilenameImageSrc.split(".")[0].split("_")[-2:];
    rTimeFromImage = int(rTimeFromImage[0]) + int(rTimeFromImage[1])/100.;
    #~ print( "rTimeFromImage: %s" % rTimeFromImage );
    
    FaceDetectionNew_drawResultsOnOpenedImage( faceDetectionNewInfos, img, rTime = rTimeFromImage, rScale = rScale, bGraph = bGraph );
            
    bRet = cv2.imwrite( strFilenameImageDst, img );
    if( not bRet ):
        print( "ERR: FaceDetectionNew_drawResultsOnImage: can't open dest image file: '%s'" % strFilenameImageDst );        
        return False;
    return True;    
# FaceDetectionNew_drawResultsOnImage - end

def FaceDetectionNew_drawResultsOnImageFromPrecalc( listFileAndResults, strOrigPath, strDestPath ):
    """
    take a list of pair of filename and results and generate image
    - listFileAndResults = [pair1, pair2, ...] with pair a [filename, rawInfo]
    """
    nCpt = 0;
    for p in listFileAndResults[120:]:
        strFilenameOrig, infos = p
        infos = FaceDetectionNew_decodeInfos( infos );
        print( "%d/%d: filename: '%s', res: %s" % (nCpt,len(listFileAndResults),strFilenameOrig, infos) );
        FaceDetectionNew_drawResultsOnImage( infos, strOrigPath + strFilenameOrig, strDestPath + strFilenameOrig, bGraph = False );
        nCpt+=1
        if( nCpt > 80 ):
            pass
            #~ return;
        
# FaceDetectionNew_drawResultsOnImageFromPrecalc - end

def FaceDetectionNew_drawResultsOnImageFromPrecalcFromFile(strFileContainingResults,strOrigPath, strDestPath):
    """
    idem FaceDetectionNew_drawResultsOnImageFromPrecalc, but takes info from a file
    """
    f = open( strFileContainingResults, "rt" );
    buf = f.read();
    f.close();
    listFileAndResults = eval(buf);
    FaceDetectionNew_drawResultsOnImageFromPrecalc( listFileAndResults, strOrigPath, strDestPath );
# FaceDetectionNew_drawResultsOnImageFromPrecalcFromFile - end

def renderForEars():
    strPath = "C:/MontageVideo6/ears/img/";
    FaceDetectionNew_drawResultsOnImageFromPrecalcFromFile( strPath+"info_images.txt", strPath + "short/", strPath + "framed/" ); 
        

def FaceDetectionNew_saveInterestingFaces( faceDetectionNewInfos, img, strDestPath, rScale = 1. ):
    """
    save all faces found in an image in dedicated face
    """
    import cv2
    import numeric
    print( "FaceDetectionNew_saveInterestingFaces: %s" % faceDetectionNewInfos );
    for object in faceDetectionNewInfos.objects:
        vertices = object.faceInfo.vertices;
        if( abs( vertices[0][0] ) > 2000 or abs( vertices[2][1] ) > 2000 ): # a stange bug: once the vertices were :[[-540508416, 1825055232], [-1352820352, 1592128512], [-307581664, 1012743168], [-1119893632, 779816448]]
            continue;
        if( object.smile[1] > 0.05 or True ):
            # if the smile in unsure then the face is blurred or ...
            if( object.smile[0] < 0.5 ):
                # we want only neutral face
                xt, yt, xb, yb = numeric.findBoundingBox( vertices );
                rSurroundingBonusX = 0.03*(xb-xt);
                rSurroundingBonusY = 0.30*(yb-yt);
                xt = int(xt-rSurroundingBonusX)*rScale;
                yt = int(yt-rSurroundingBonusY*0.75)*rScale;
                xb = int(xb+rSurroundingBonusX)*rScale;
                yb = int(yb+rSurroundingBonusY*0.25)*rScale;
                print( "bb: %s, %s, %s, %s" % (xt, yt, xb, yb ));
                cropped = img[yt:yb, xt:xb];
                strFilenameImageDst = strDestPath + ("%05d" % object.faceInfo.id) + "_" + filetools.getFilenameFromTime() + ".jpg";
                print( "INF: FaceDetectionNew_saveInterestingFaces: saving face to %s" % strFilenameImageDst );
                bRet = cv2.imwrite( strFilenameImageDst, cropped, [int(cv2.IMWRITE_JPEG_QUALITY), 100] );
        
        
    
    

def autoTest_FaceDetectionNew():
    if( 0 ):
        dataIn = [[[2, [101, 112], [171, 112], [101, 182], [171, 182], 0.0, 0.6100000143051147], [[[123, 136], 0.7410000562667847], [[149, 136], 0.9800000190734863], [[138, 167], 0.9890000224113464], [[129, 138], 0.7410000562667847], [[117, 137], 0.7410000562667847], [[144, 138], 0.9800000190734863], [[155, 137], 0.9800000190734863], [[124, 166], 0.9890000224113464], [[150, 166], 0.9890000224113464], [[131, 154], 0.1080000028014183], [[144, 154], 0.1080000028014183], [[138, 161], 0.9890000224113464]], [0.12217304855585098, 0.13962633907794952, 0.0], [[39, 0.20000000298023224], [1, 0.8100000619888306]], [0.47999998927116394, 0.7430000305175781]]]
        data1 = FaceDetectionNew_decodeInfos(dataIn);
        print data1;
        FaceDetectionNew_drawResultsOnImage( data1, "c:\\tmp\\2014_09_12-12h26m56s404284ms.jpg", "c:\\tempo\\debug1.jpg", rScale=2. );
    if( 1 ):
        dataIn = [[[15, [51, 143], [107, 143], [51, 199], [107, 199], 0.0, 0.6970000267028809], [[[69, 161], 1.0], [[90, 160], 0.9920000433921814], [[80, 186], 0.999000072479248], [[74, 162], 1.0], [[65, 161], 1.0], [[86, 162], 0.9920000433921814], [[94, 160], 0.9920000433921814], [[73, 185], 0.999000072479248], [[89, 185], 0.999000072479248], [[75, 176], 0.706000030040741], [[84, 176], 0.706000030040741], [[80, 183], 0.999000072479248]], [-0.12217304855585098, -0.13962633907794952, -0.05235987901687622], [[40, 0.25], [1, 0.30800002813339233]], [0.03999999910593033, 0.3920000195503235]], [[16, [248, 122], [290, 122], [248, 164], [290, 164], 0.0, 0.7670000195503235], [[[261, 140], 1.0], [[279, 139], 1.0], [[270, 157], 1.0], [[264, 140], 1.0], [[257, 140], 1.0], [[276, 140], 1.0], [[283, 139], 1.0], [[263, 158], 1.0], [[277, 157], 1.0], [[266, 150], 0.9970000386238098], [[274, 149], 0.9970000386238098], [[270, 154], 1.0]], [0.19198621809482574, -0.01745329238474369, -0.01745329238474369], [[2, 1.0], [0, 0.2720000147819519]], [0.009999999776482582, 0.35500001907348633], [["alexandre", 0.65],["laurent", 0.20]] ] ];
        data1 = FaceDetectionNew_decodeInfos(dataIn);
        print data1;
        assert( data1.objects[1].recognised[1] == ["laurent", 0.20] );
        print( "FaceDetectionNew_select_face: " );
        dataselect = FaceDetectionNew_select_face( data1 );
        print dataselect;
        print( "FaceDetectionNew_select_face(focus): " );
        dataselect = FaceDetectionNew_select_face( data1, 16 );
        print dataselect;
    

def autoTest():
    #~ autoTest_FaceDetection();
    autoTest_FaceDetectionNew();
    #~ autoTest_dataMatrix(); # btw: ne fonctionne plus au 28-2-2014
# autoTest - end    
    
if __name__ == "__main__":
    #autoTest();
    renderForEars();
