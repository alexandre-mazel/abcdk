# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Face Recognition Tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
#
# copy faces to robot for further learning:
# scp -pw nao -r C:\work\studio_mirror\imageuploader\uploads\face* nao@10.0.:/home/nao/
#
###########################################################

#
# results
#
# Current result on test_faces from all learned from EOS600D
#
#
# Pepper 2.5.5.5
# 
# on /home/nao/test_faces/:
# - good: 412 (43%) (avg conf:  0.44)
# - bad: 219 (22%)
# - ndet: 327 (34%)
# - total image tested: 958
# total duration: 28.08s (avg: 0.03s)

"Face Recognition Tools"
print( "importing abcdk.facerecognition" );

import datetime
import numpy
import os
import sys

import extractortools
import filetools
import image
import leds.leds
import naoqitools
import pathtools
import stringtools
import test
import time

import shutil

def findMostProbable( listWithProba ):
    """
    receive a list of id, proba, name, and find which is the more probable.
    eg: [['00098__MAZEL_alexandre', 0.5360000133514404 ], ['00098__MAZEL_alexandre', 0.5910000205039978], ['00098__MAZEL_alexandre', 0.5910000205039978, ], ['00087__HERVIER_thibault', 0.527999997138977], ['00087__HERVIER_thibault', 0.527999997138977], ['00087__HERVIER_thibault', 0.51500004529953 ]]
    Return "" if improbable or the name of the most probable
    """
    if( len(listWithProba) < 1 ):
        return "";
    aList = sorted( listWithProba, key=lambda tup:tup[1], reverse=True );
    print aList
    strFaceName = aList[0][0];
    rSum = aList[0][1];
    nNbrInSum = 1;
    i = 0; # make it happy, when not entering the loop
    for i in range(1,len(aList)):
        if( aList[i][0] != strFaceName ):
            break;
        rSum += aList[i][1];
        nNbrInSum += 1;
    rAvg = rSum/nNbrInSum;
    print( "rSum: %s, i: %s, rAvg: %s, len(aList): %s" % (rSum, i, rAvg,len(aList)) );
    if( i >= len(aList)/2 and (rAvg + nNbrInSum *0.2) > 0.6 and nNbrInSum > 1 ):  # nNbrInSum give a bonus, even if ratio is low, the fact to have a lot increase the probability
        return strFaceName;
    return "";
    # name
    #~ if( len( self.listReco ) > 0 ):
        #~ bAllSame = True;
        #~ print( "self.listReco: %s" % self.listReco );
        #~ strFaceName = self.listReco[0][2];
        #~ for rec in self.listReco[1:]:
            #~ print( "rec: %s" % rec );
            #~ if( strFaceName != rec[2] ):
                #~ bAllSame = False;
        #~ if( bAllSame ):
# findMostProbable - end
#~ print( findMostProbable( [['00098__MAZEL_alexandre', 0.5360000133514404 ], ['00098__MAZEL_alexandre', 0.5910000205039978], ['00098__MAZEL_alexandre', 0.5910000205039978, ], ['00087__HERVIER_thibault', 0.527999997138977], ['00087__HERVIER_thibault', 0.527999997138977], ['00087__HERVIER_thibault', 0.51500004529953 ]] ) );
#~ exit(1)

def isFilenameOfImage( strFilename ):
    """
    return true if this filename looks like a good image for the facerecognition
    """
    strBlackhole, strFileExtension = os.path.splitext( strFilename );
    return strFileExtension.lower() in [".jpg", ".jpeg", ".png"];
# isFilenameOfImage - end

def renameImage( strPath, bReallyDoIt = False, nHumanID = -1 ):
    """
    Rename all image in a folder, to the normalised image name.
    at the end, they should have a name like: 
        "00005__2012_12_05-13h22m48s084ms__MT_4020.jpg"
        or
        "00xxx__2012_12_05-13h22m48s084ms.jpg"
    return number of file renamed
    - strPath where are the file to be renammed
    - bReallyDoIt: by default, it just print the renamming to do
    - nHumanID: if specified, it will rename the prefix with the good number
    """
    bUseExif = True;
    
    if( not bReallyDoIt ):
        print( "WRN: facerecognition.renameImage: this is just a simulation..." );
       
    strPrefixHumanID  = "00xxx";
    if( nHumanID != -1 ):
        strPrefixHumanID = "%05d" % nHumanID;
    strPrefixHumanID += "__";
        
    files = sorted(os.listdir( strPath));
    nCptImage = 0;
    for strFile in files:
        nCptImage += 1;
        if( not isFilenameOfImage( strFile ) or strFile[0] == '0' ): # don't rename image file beginning by 0 as they should be already renammed!
            continue;
        strTimeStamp = filetools.getFileTimePrintable( strPath+strFile );
        strCameraType = "";
        if( bUseExif ):
            strCameraTypeExif, strDateTimeExif = image.getExifInfo( strPath+strFile, ["Model", "DateTime"] );
            if( strCameraTypeExif != None ):
                strCameraTypeExif = strCameraTypeExif.replace( "Canon", "" );
                strCameraTypeExif = strCameraTypeExif.replace( " ", "" );
                strCameraType = "__" + strCameraTypeExif;
            if( strDateTimeExif != None ):
                # exif format is: '2013:02:23 09:48:24'
                strDateTimeExif = strDateTimeExif.replace( ":", "_", 2 );
                strDateTimeExif = strDateTimeExif.replace( " ", "-" );
                strDateTimeExif = strDateTimeExif.replace( ":", "h", 1 );
                strDateTimeExif = strDateTimeExif.replace( ":", "m", 1 );
                strTimeStamp = strDateTimeExif + "s" + ("%03dms" % (nCptImage%1000)); # create a new ms for every file
        if( ',' in strFile and "ms" in strFile ):
            # the name could be a stamp "1421232698,496ms.jpg", so use it
            timeInFilename = float( strFile.split("ms")[0].replace(',','.' ) );
            dt = datetime.datetime.fromtimestamp( timeInFilename );
            strTimeStamp = dt.strftime( "%Y_%m_%d-%Hh%Mm%Ss%fms" ).replace("000ms", "ms");
            
        strOld = strPath + strFile;
        strBlackhole, strFileExtension = os.path.splitext( strFile );
        strNew = strPath + strPrefixHumanID + strTimeStamp + strCameraType + strFileExtension.lower();        
        if( strOld != strNew ):
            print( "INF: facerecognition.renameImage: '%s' = > '%s'" % ( strOld, strNew ) );
            if( os.path.exists( strNew ) ):
                print( "WRN: facerecognition.renameImage: destination exists, skipping..." );
            else:
                if( bReallyDoIt ):
                    shutil.move( strOld , strNew );
# renameImage - end
#~ renameImage( "/home/likewise-open/ALDEBARAN/amazel/photo_new/", bReallyDoIt = True );
#~ renameImage( "d:/faces_new/", bReallyDoIt = False );
#~ renameImage( "c:/tmp/img/", bReallyDoIt = True );
#~ renameImage( "c:/tmp/rec_faces/william/", bReallyDoIt = True, nHumanID = 301 );

def correctFormat( strTotalFile ):
    """
    Rename a file so the filename match the intended one
    handles this error:
    - 4 to 3 digits in the ms: "2012_01_01_00h00m00s0016ms" => "2012_01_01_00h00m00s016ms"
    - only one _ to delimit first field: "00121_2013_02_07-10h55m07s014ms__EOS650D__Expressive" => "00121__2013_02_07-10h55m07s014ms__EOS650D__Expressive"
    """
    bMustCorrect = False;
    strPath,  strFilename = os.path.split( strTotalFile );
    strFilename, strExt = os.path.splitext( strFilename );
    if( strFilename[6] != '_' ):
        print( "INF: abcdk.facerecognition:correctFormat: file: %s use only one delimiter after id." % strFilename );        
        strFilename = strFilename[:6] + '_' + strFilename[6:];
        bMustCorrect = True;
    listInfo = strFilename.split("__");
    #~ print( "listInfo: %s" % listInfo );
    stamp = listInfo[1];
    if( stamp[-6] != 's' and stamp[-7] == 's' ):
        print( "INF: abcdk.facerecognition:correctFormat: file: %s use old microsecond format on 4 digits." % strFilename );
        listInfo[1] = stamp[:-6] + listInfo[1][-5:];
        bMustCorrect = True;
    if( bMustCorrect ):
        strFilename = "__".join(listInfo) + strExt;
        print( "INF: abcdk.facerecognition:correctFormat: renaming to '%s'" % strFilename );
        os.rename( strTotalFile, strPath + os.sep + strFilename );
        return 1;
    return 0;
# correctFormat - end
#correctFormat( "00121_2013_02_07-10h55m07s014ms__EOS650D__Expressive" );

def correctFormatInFolder( strPath ):
    """
    Apply correctFormat to a bunch of file
    """
    #~ print( "INF: abcdk.facerecognition:correctFormatInFolder: processing path: %s" % strPath );
    files = sorted(os.listdir( strPath));
    nNbrRenamed = 0;
    for file in files:
        strAbsName = strPath+os.sep+file;
        if os.path.isdir(strAbsName):
            nNbrRenamed += correctFormatInFolder( strAbsName )
        else:
            nNbrRenamed += correctFormat(strAbsName);
    if( nNbrRenamed > 0 ):
        print( "INF: abcdk.facerecognition:correctFormatInFolder: processing path: %d renammed file(s) in %s" % (nNbrRenamed,strPath) );
    return nNbrRenamed;
# correctFormat - end
#~ correctFormatInFolder( "C:/work/studio_mirror/imageuploader/faces/" );
#~ correctFormatInFolder( "C:/work/studio_mirror/imageuploader/faces/00255__FONTA_rose/Validated/" );
#~ correctFormatInFolder( "C:/work/studio_mirror/imageuploader/faces/00098__MAZEL_Alexandre/Validated/" );


class FaceRecognition(object):
    """
    An objet to manipulate face recognition from file or camera
    """
    def __init__(self):
        object.__init__(self)
        #~ self.fr = naoqi.ALProxy( "ALFaceRecognition", "localhost", 9559 );
        self.fr = naoqitools.myGetProxy( "ALFaceDetection" );
        self.faces = None;
        if( self.fr != None ):
            self.faces = self.listKnownFaces()
        else:
            print( "WRN: abcdk.FaceRecognition: the 'ALFaceDetection' module wasn't reachable..." );
        if self.faces is None:
            self.faces = []
        #self.fr = naoqitools.myGetProxy("ALFaceRecognition")
        #self.strLogPath = "/home/nao/abcdk_debug/facereco/";
        #~ filetools.makedirsQuiet( self.strLogPath );
        self.strLearnedCachePath = pathtools.getCachePath() + "facereco/";
        self.strFaceRecognitionModuleBasePath = "/home/nao/.local/share/vision/facerecognition/";
        filetools.makedirsQuiet( self.strLearnedCachePath );
        self.reset();        
        
    def reset( self ):
        """
        call this method before face recognised stuffs as an extractor
        """
        print( "WRN: abcdk.FaceRecognition: resetting..." );
        self.aDictEvaluateBadRecognised = {}; # a dict to store bad recognized: "reference_name" => {bad_name1=>[confidence1, confidence2],bad_name2 =>[confidence2] }
        if( self.fr != None ):
            self.fr.setTrackingEnabled( True );
        
    def changeBase( self, strFilename ):
        print( "WRN: abcdk.changeBase: switching to base '%s'" % strFilename );
        filetools.makedirsQuiet( self.strLearnedCachePath + strFilename );
        try:
            self.fr.useDatabase( self.strFaceRecognitionModuleBasePath + strFilename );
        except BaseException, err:
            print( "WRN: abcdk.FaceRecognition.changeBase: error while switching database, perhaps not handled by your version. err: %s" % err );
    # changeBase - end
    
    def getCurrentBaseName(self):
        try:
            strName =  self.fr.getUsedDatabase().replace(self.strFaceRecognitionModuleBasePath,"");
        except BaseException, err:
            print( "WRN: abcdk.FaceRecognition.getCurrentBaseName: switching database is perhaps not handled by your version. err: %s" % err );
            strName = "default"
        return strName

    def recognizeFromFile(self, imgPath):
        """
        Recognizes a face from an image file.

        Returns: List of names and associated scores (example: [[“Paul”, 0.98236], [“Ringo”, 0.12675]]),
        or None if face is not recognized face or no face is present.
        """
        retval = self.fr.recognizeFromFile(imgPath, False)
        print "INF: recognizeFromFile: ", retval
        if retval == [] or retval[0][0] == '':
            print "INF: recognizeFromFile: unknown people", retval
            retval = None
        return retval

    def listKnownFaces(self):
        """
        Returns the list of all names present in the database.
        Return: List of names (example: [“Paul”, “Ringo”]).
        """
        #~ if "1.17" in self.fr.version():
            #~ return self.fr.listKnownFaces()
        #~ else:  # >1.20
            #~ return self.fr.getKnownFaces()
        return self.fr.getLearnedFacesList();

    def split_info(self, format_fir_key):
        """
        split a well format string to fir number, name, firstname
        example : 00000__NAME_Firstname OR x_FirstName_NAME
        return: [0,NAME, Firstname] or [-1,"", ""] on error
        """
        fid = -1;
        try:
            fid, whole = format_fir_key.split("__")
            name, firstname = whole.split("_")
            return [int(fid), name, firstname]
        except BaseException, err:
            print( "DBG: abcdk.facerecognition.split_info: while decoding '%s', err: %s" % ( format_fir_key, str( err ) ) );
            return [int(fid), "", ""]

    def getInfo(self, strFilename):
        """
        return [nID, "Name", "Christian Name"] or [-1, "", ""] in case of error
        We except one of these input :
        if it's FIR :
        00000__NAME_firstname.fir
        else
        00000__NAME_firstname/Validated/00005__2012_12_05-13h22m48s084ms__MT_4020.jpg
        or
        00000__NAME_firstname/00005__2012_12_05-13h22m48s084ms__MT_4020.jpg
        or 
        00005__2012_12_05-13h22m48s084ms__MT_4020.jpg
        or 
        00005__2012_12_05-13h22m48s084ms__MT_4020        
        """
        if type(strFilename) is str:
            if ".fir" in strFilename:
                return self.split_info(strFilename)
            else:
                parts = strFilename.split("/")
                dir_name = ""
                if( len(parts)<2):
                    # just a filename
                    return self.split_info(strFilename);
                if len(parts) > 2:
                    if "Validated" in parts[-2]:
                        dir_name = parts[-3]
                    else:
                        dir_name = parts[-2]
                elif len(parts) > 1:
                    dir_name = parts[-2]
                return self.split_info(dir_name)

        return [-1, "", ""]
        
    def getInfoFromImage( self, strImageFilename ):
        """
        get [nIx, strDate, strTime, strCameraType, strExpression] from an image name from the data base.
        eg: 00098__2013_01_11-00h00m12s003ms__EOS600D__Happy.JPG => [98, "2013_01_11", "00h00m003ms", "EOS600D", "Happy"]
        eg: 00098__2013_01_11-00h00m12s003ms__EOS600D__G.JPG => [98, "2013_01_11", "00h00m003ms", "EOS600D", "", True]
        an empty field will be set with ""
        if error, all fields will be set to "", and integer to -1
        optionnaly a last parameter could be added: True or False, if the human has glasses or not!
        """
        strImageFilename = strImageFilename.split(".")[0];
        fields = strImageFilename.split( "__" );
        try:
            nIdx = int( fields[0] );
        except BaseException, err:
            print( "WRN: abcdk.facerecognition.getInfoFromImage: in '%s', index error : %s" % (strImageFilename, str( err ) ) );
            nIdx = -1;
        try:
            strDate, strTime = fields[1].split("-");
        except BaseException, err:
            # try with old format 2012_01_01_00h00m00s0016ms
            try:
                aDecoded = fields[1].split( "_" );
                strDate = "_".join( aDecoded[:3] );
                strTime = aDecoded[3];
            except BaseException, err:
                print( "WRN: abcdk.facerecognition.getInfoFromImage: in '%s', date-time error : %s" % (strImageFilename, str( err ) ) );
                strDate = "";
                strTime = "";
        if( strDate != "" and len(strDate) != 10 ):
            print( "WRN: abcdk.facerecognition.getInfoFromImage: in '%s', date seems bad formated: '%s'" % ( strImageFilename,strDate ) );
        if( strTime != "" and len(strTime) != 14 ):
            print( "WRN: abcdk.facerecognition.getInfoFromImage: in '%s', date seems bad formated: '%s'" % ( strImageFilename , strTime ) );
            
        bHasGlasses = False;
        if( fields[-1] == "G" ):
            bHasGlasses = True;
            fields.pop();
        if( len( fields ) > 2 ):
            strCameraType = fields[2];
            if( "_" in strCameraType ):
                print( "WRN: abcdk.facerecognition.getInfoFromImage: in '%s', camera type seems bad formated: '%s'" % ( strImageFilename , strCameraType ) );
        else:
            strCameraType = "Unknown";
        if( len( fields ) > 3 ):
            strExpression = fields[3];
            if( "_" in strExpression ):
                print( "WRN: abcdk.facerecognition.getInfoFromImage: in '%s', expression seems bad formated: '%s'" % ( strImageFilename , strExpression ) );
        else:
            strExpression = "";
            
        return [nIdx, strDate, strTime, strCameraType, strExpression,bHasGlasses];
    # getInfoFromImage - end 

    def getID(self, strFilename):
        import humans
        if strFilename != "": 
            humans.setActualHumanWearGlasses( strFilename[-1] == "2" )
        return self.getInfo(strFilename)[0];

    def getName(self, strFilename):
        return self.getInfo(strFilename)[1:]

    #def isCorrectImage(self, strFilename, rCenterRatio = 1. ):
    #    pass

    #def treatTempCapture(self, source_dir, results_dir):
    #    """
    #        take haarextractor output or basic nao image output
    #        apply the facerecon on
    #        and sort images in the good directory

    #        source_dir = temp directory of nao (tmp/ ?)
    #        results_dir = directory output for results
    #    """
    #    pass

    def knownFace(self, fir_name):
        """
            test if the module known this fir id
            fir_name = 00000__NAME_firstname
        """
        if fir_name in self.faces:
            return True
        return False
        
    def learnHumanFromFiles( self, strHumanName, listFiles ):
        """
        Learn a new human from a set of files
        """
        print( "INF: abcdk.facerecognition.learnHumanFromFiles: learning %s from %s" % ( str(strHumanName),listFiles) );
        listFiles=sorted(listFiles);
        if( strHumanName in self.fr.getLearnedFacesList() ): # this check could takes a bit of time... blaaah
            self.fr.forgetPerson( strHumanName );
        bFirst = True;
        for strFilename in listFiles:
            #if( strCameraType != "Unknown" and True ): # TODO: move this part in learnHumanFromFiles
            if( True ):
                # big image from apn, needs to be resized to prevent some out of memory in the learning process.
                image.reduceBigger( strFilename, strFilename, 2048, 2592 ); # we change the image directly on the nao !!! (it shouldn't be done on the original data base!)            
            self.fr.learnFaceFromFile( strHumanName, strFilename, not bFirst );
            bFirst = False;
    # learnHumanFromFiles - end

    def learn( self, strImageDirectory, nBeginAt = 0, nLimitNumber = 0, bOverwrite=False, strRestrictToCameraType = "", strRestrictToExpression = "", bDuplicateWithGlasses = False ):
        """
            learn all images sorted in directory
            like that's describe here :
            http://sirius2/mediawiki/index.php/FACERECO

            strImageDirectory:            directory containing humans pictures
            nBeginAt:                        first human to learn
            nLimitNumber:                  maximum number to learn
            bOverwrite:                     even if fir is present and learned with same image, relearn it!
            strRestrictToCameraType:  learn using only information from a type of camera (tagged in the image filename)
            strRestrictToExpression:    using only some type of human expression (tagged in the image filename)
            bDuplicateWithGlasses:      when set, the learning will separate with or without glasses
            
            return the duration of the operation in seconds (float)

        """
        print( "INF: abcdk.facerecognition: learn( '%s', %d, %d, %s, '%s', '%s' ) - beginning..." % (strImageDirectory, nBeginAt, nLimitNumber, str( bOverwrite ), strRestrictToCameraType, strRestrictToExpression ) );
        beginat = time.time()
        humans = sorted(os.listdir(strImageDirectory))
        nCurrentLearning = 0;
        if( bOverwrite ):
            self.fr.clearDatabase();
        for human in humans:
            if os.path.isdir(strImageDirectory+human) is True:
                # validated ...
                validated = strImageDirectory+human+"/Validated/"
                # compose the fir file name
                nId, name, firstname = self.getInfo(validated+"fake.jpg");
                face_name = ("%05d" % nId) + "__" + name + "_" + firstname
                #~ if self.knownFace(face_name) == True and not bOverwrite: # old test: when list of used learned image weren't memorized
                    #~ continue;
                if not os.path.isdir(validated):
                    continue;
                if( int(nId) < nBeginAt ):
                    # skip image before that number
                    continue;
                images = sorted(os.listdir(validated))
                list_list_images = [[],[]] # for every human, we can make separate learning
                for strImage in images:
                    nIx, strDate, strTime, strCameraType, strExpression, bHasGlasses = self.getInfoFromImage( strImage );
                    if( strRestrictToCameraType != "" or strRestrictToExpression != "" ):
                        if( strRestrictToCameraType != None and not strRestrictToCameraType in strCameraType ):
                            continue;
                        if( strRestrictToExpression != None and not strRestrictToExpression in strExpression ):
                            continue;
                    if( not bDuplicateWithGlasses ):                    
                        list_list_images[0].append(validated+strImage);
                    else:
                        if( bHasGlasses ):
                            list_list_images[1].append(validated+strImage);
                        else:
                            list_list_images[0].append(validated+strImage);
                            
                for nNumList, list_images in enumerate(list_list_images):
                    if( len(list_images) < 1 ):
                        continue;
                    if( nNumList > 0 ):
                        face_name += "2";
                    strLearnedCachePath = self.strLearnedCachePath + self.getCurrentBaseName() + os.sep
                    strLearnedCachePathFilename = strLearnedCachePath + face_name + ".log";
                    if( self.knownFace(face_name) and os.path.exists( strLearnedCachePathFilename ) ):
                        file = open( strLearnedCachePathFilename );
                        aLastComputed = file.read();
                        file.close();
                        aLastComputed = eval( aLastComputed );
                        if( aLastComputed == list_images and not bOverwrite ):
                            print( "\nWRN: abcdk.facerecognition: Learning %s: data already computed for this set of images (%d images were used)" % (face_name, len(list_images) ) );
                            continue;
                        print( "\nWRN: abcdk.facerecognition: ReLearning %s: car difference entre:\n%s\net:\n%s\n" % (face_name,aLastComputed,list_images) );
                    print( "\nINF: abcdk.facerecognition: Learning %s, please wait... (%d images)" % (face_name, len(list_images) ) );
                    self.learnHumanFromFiles(face_name, list_images)
                    if( True ):
                        # add a small trace of which file where used for this learning
                        filetools.makedirsQuiet( strLearnedCachePath )
                        file = open( strLearnedCachePathFilename, "wt" );
                        file.write( str( list_images ) );
                        file.close();
                nCurrentLearning += 1
                if nLimitNumber is not 0:
                    if nCurrentLearning >= nLimitNumber:
                        break

        return time.time() - beginat

    def flat_fr_result(self, aRet):
        """
            take a result of face recognized
            and flat it in a string
            separate fid id and trust score by "_"
            and each one by "__"
        """
        if aRet is not None:
            if len(aRet) > 0:
                one_dim = [(fir+"_"+str(trust)) for (fir, trust) in aRet]
                return "__".join(one_dim)
        return ""
        
    def normaliseConfidence( self, aReco ):
        """
        - aReco: a pair  ['gilbert', 0.9]
        Return normalised confidence: eg: ['gilbert', 0.65]
        """
        rNewConf = aReco[1]
        if( "00300" in aReco[0] ):
            rNewConf = aReco[1]*0.4
            #~ print( "normaliseConfidence: oneReco: %s changed from %6.3f to %6.3f" % (aReco[0],aReco[1],rNewConf) )
        return [aReco[0],rNewConf]
    # normaliseConfidence - end
    
    def select_recognised( self, recolist ):
        """
        receive a list of recognition [['alexandre', 0.65], ['laurent', 0.2]]    or [], in that case, we send back []
        Return the best one, eg: ['alexandre', 0.65]
            (often the first one, but we can optimize or change coef or blacklist some or ...)
        """
        #~ print( "DBG: select_recognised: %s" % recolist )
        if( recolist == [] ):
            return []
        
        if len(recolist) > 0 and ( not isinstance( recolist[0], list ) or len(recolist[0]) != 2 ):
            print( "ERR: facerecognition.select_recognised: receiving: recolist: '%s': bad format !" % recolist );        
            return ["format error", 0.9];
        # apply modification        
        if( len(recolist) < 1 ):
            return self.normaliseConfidence(recolist)
            
        for i in range(len(recolist) ):
            recolist[i] = self.normaliseConfidence(recolist[i])
            
        return recolist[0];
    # select_recognised - end
    
    def findBestForOneName( self, recolist, strName ):
        """
        receive a list of recognition [['alexandre', 0.65], ['laurent', 0.2]]
        Return the best one for a specific name or [] if none
            (we can optimize or change coef or blacklist some or ...)
        """
        newlist = [];
        rBest = -1;
        for reco in recolist:
            if( reco[0] == strName and reco[1] > rBest ):
                rBest = reco[1];
                if( len(newlist) == 0 ):
                    newlist.append( [strName, rBest] );
                else:
                    newlist[0][1] = rBest;
        return newlist;
    # findBestForOneName - end
        
    def evaluateOnLearned( self, nLimitNumber=-1 ):
        """
        Launch an evaluation to see the score of the learned origin pictures
        """
        strPath = "/home/nao/Users/All/Caches/facereco/";
        learned = sorted(os.listdir(strPath));
        nCpt = 0;
        self.fr.setTrackingEnabled( False );
        for strFileName in learned:
            file = open( strPath+strFileName, "rt" );
            listImg = eval(file.read());
            file.close();
            nCptFailed = 0;
            nCptSuccess = 0;
            rSumSuccess = 0.;
            for img in listImg:
                faceInfos = self.fr.recognizeFromFile( img, False );
                decodedData = extractortools.FaceDetectionNew_decodeInfos(faceInfos);
                #~ print( "decodedData: %s" % decodedData );
                strThisHumanPath, strThisHumanFilename = os.path.split( img );
                if( len( decodedData.objects ) > 0 ):
                    #reco = decodedData.objects[0].recognised
                    object = extractortools.FaceDetectionNew_select_face(decodedData,-1).objects[0];
                    reco = self.select_recognised( object.recognised );
                    nCptSuccess += 1;
                    if( reco[0][:5] != strThisHumanFilename[:5] ):
                        print( "WRN: evaluateOnLearned: FAKE POSITIF !!!\n\n\n" );
                        rSumSuccess -= reco[1];
                    else:
                        rSumSuccess += reco[1];

                else:
                    reco = ["",0.];
                    nCptFailed += 1;
                #~ print( "DBG: evaluateOnLearned: %s => %s" % (strThisHumanFilename, reco) );
                #~ assert( reco[0] == -1 or reco[2][:5] == strThisHumanFilename[:5] );                
                nCpt += 1;
                if( nLimitNumber != -1 and nCpt >= nLimitNumber ):
                    break;
            # for each img of one human - end
            if( nCptSuccess > 0 ):
                rAvgSuccess = rSumSuccess/nCptSuccess;
            else:
                rAvgSuccess = 0.;
            print( "INF: evaluateOnLearned STATS: %s, failed: %s, success: %s, sum: %5.2f, avg: %5.2f\n" % (strFileName,nCptFailed, nCptSuccess,rSumSuccess,rAvgSuccess) );
            
            if( nLimitNumber != -1 and nCpt >= nLimitNumber ):
                break;
        # for each human - end
    # evaluateOnLearned - end
        

    def evaluate(self, strImageToTestDirectory, strOutputDirectory, nLimitNumber = 0, rConfidenceLimit = 0.3 ):
        """
        evaluate image from a test dir
        and put result in the output directory
        - nLimitNumber: 0: no limit
        
        return the number of [image tested, nbr_tested_that_must_be_good, good detection, bad detection, and not detected, avg_confidence]
        """
        filetools.makedirsQuiet( strOutputDirectory );
        files = sorted( os.listdir(strImageToTestDirectory) );
        nNbrGood = 0;
        nNbrMustBeGood = 0;
        nNbrBad = 0;
        nNbrNotDetected = 0;
        nNbrTested = 0;

        beginat = time.time();
        self.fr.setTrackingEnabled( False );
        rSumConfidenceGood = 0.;        
        for strImageFile in files:
            if os.path.isdir(strImageFile) is False:
                if( isFilenameOfImage( strImageFile ) ):
                    print( "INF: testing picture %d/%d: '%s'... " % ( nNbrTested, len(files), strImageFile ) );
                    filename = strImageToTestDirectory + strImageFile
                    #~ aRet = self.recognizeFromFile(filename);
                    #~ print( "aRet: %s" % str( aRet ) );
                    aReferenceDecodedInfo = self.getInfoFromImage( strImageFile );
                    nReferenceIdx = aReferenceDecodedInfo[0];
                    if( nReferenceIdx < 9000 and nReferenceIdx != -1 ):
                        nNbrMustBeGood += 1;
                    
                    faceInfos = self.fr.recognizeFromFile( filename, False );
                    decodedData = extractortools.FaceDetectionNew_decodeInfos(faceInfos);
                    
                    strNameDestResult = "___" + strImageFile;
                    reco = None;
                    rConfidence = -1.;
                    if( len(decodedData.objects) > 0 ):
                        object = extractortools.FaceDetectionNew_select_face(decodedData,-1).objects[0];
                        #~ strNameDestResult = self.flat_fr_result(aRet) + strNameDestResult;
                        #~ rConfidence = aRet[0][1];
                        reco = self.select_recognised( object.recognised );
                        rConfidence = reco[1];
                        if( rConfidence < rConfidenceLimit ):
                            print("INF: Not enough confidence %5.2f < %5.2f" % (rConfidence , rConfidenceLimit) );
                            reco = None;
                    if( reco != None ):
                        nFoundIdx = int(self.getInfo( reco[0] )[0]);
                        if( nReferenceIdx == nFoundIdx ):
                            nNbrGood += 1;
                            rSumConfidenceGood += reco[1];
                            print( "INF: GOOD, conf:%5.2f" % rConfidence );
                            strNameDestResult = "GOOD_" + strNameDestResult;
                        else:
                            nNbrBad += 1;
                            print( "INF: BAD ( %d instead of %d ) (%s) (conf:%5.2f)" % ( nFoundIdx, nReferenceIdx, reco[0], rConfidence ) );
                            strNameDestResult = "BAD_" + strNameDestResult;
                            if( not nReferenceIdx in self.aDictEvaluateBadRecognised.keys() ):
                                self.aDictEvaluateBadRecognised[nReferenceIdx] = {};
                            if( not nFoundIdx in self.aDictEvaluateBadRecognised[nReferenceIdx] ):
                                self.aDictEvaluateBadRecognised[nReferenceIdx][nFoundIdx] = [];
                            self.aDictEvaluateBadRecognised[nReferenceIdx][nFoundIdx].append( rConfidence );
                    else:
                        if( nReferenceIdx < 9000 and nReferenceIdx != -1 ):
                            nNbrNotDetected += 1;
                            print( "INF: NOT FOUND, conf:%5.2f" % rConfidence );
                            strNameDestResult = "BAD_NOT_FOUND_" + strNameDestResult;
                        else:
                            nNbrGood += 1; # here true negative, it shouldn't be noted as good!!! (it will fake the recall ratio) "ERROR134"
                            print( "INF: GOOD: none detected, and there was no one on it!, conf: %5.2f" % rConfidence );
                            strNameDestResult = "GOOD_NOT_FOUND_" + strNameDestResult;
                    strBlackhole, strFileExtension = os.path.splitext( strImageFile );
                    shutil.copy(filename, strOutputDirectory + strNameDestResult + strFileExtension );
                    nNbrTested += 1;
                    if( nLimitNumber > 0 and nNbrTested >= nLimitNumber ):
                        break;
        # for each file - end
        rAvgGoodConfidence = 0.;
        if( nNbrGood > 0 ):
            rAvgGoodConfidence = rSumConfidenceGood/nNbrGood;
        if( nNbrTested < 1 ):
            print( "WRN: No test images found !" )
        else:
            print( "INF: abcdk.facerecognition.evaluate on %s: aBadRecognised: %s" % (strImageToTestDirectory,self.aDictEvaluateBadRecognised) );
            print( "INF: abcdk.facerecognition.evaluate\n#on %s:\n# - good: %d (%d%%) (avg conf: %5.2f)\n# - bad: %d (%d%%)\n# - ndet: %d (%d%%)\n# - total image tested: %d\n# total duration: %5.2fs (avg:%5.2fs)" % (strImageToTestDirectory, nNbrGood, (nNbrGood*100)/nNbrTested, rAvgGoodConfidence, nNbrBad, (nNbrBad*100)/nNbrTested, nNbrNotDetected, (nNbrNotDetected*100)/nNbrTested,nNbrTested, (time.time() - beginat), (time.time() - beginat)/float(nNbrTested) ) );
        return [nNbrTested,nNbrMustBeGood,nNbrGood, nNbrBad, nNbrNotDetected,rAvgGoodConfidence];
    # evaluate - end
    
    def getDictEvaluateBadRecognised( self ):
        """
        see reset for the format of the dict
        """
        return self.aDictEvaluateBadRecognised;
    # getDictEvaluateBadRecognised - end
    
    def computeStatOnBad( self, aDictBad ):
        """
        return a string explaining the bad recognition
        """
        strOut = "";
        for nRef, dictData in aDictBad.iteritems():
            strOut += "%5d: %d different bad(s)" % (nRef, len(dictData));
            nNbrTotal = 0;
            for nBad, data in dictData.iteritems():
                nNbr = len(data);
                nNbrTotal += nNbr;
                rSum = sum(data);
                rMin = min(data);
                rMax = max(data);
                strOut += "%5d: %5.2f/%5.2f/%5.2f (nbr: %d)," % (nBad, rMin, rSum/nNbr, rMax, nNbr);
            strOut += " total bad(s): %s\n" % nNbrTotal;
        return strOut;
    # computeStatOnBad - end
    
    def evaluate_total( self, bFull = True, rConfidenceLimit = 0.4, bNoRelearn = False, bOnlyNoDuplicateWithGlasses = True ):
        """
        Launch a total evaluation
        - bFull: if false, launch just a quick test (no relearn and 10 image for each folder)
        - bOnlyNoDuplicateWithGlasses: when you want to compare two software version or ... => just one database: mixed glasses and not...
        """
        listFolderToEvaluate = [
            "00098_alexandre",
            "00313_laurent",
            "00156_steev",
            "00162_guillaume",
            "00301_william",
            "00304_simon",
            "00306_pierre",
            "00309_blaise",
            "00310_vincent",
            "00313_laurent",
            "viviane",
        ];

        resTotal = [];
        dictBad = [];
        aTimeTaken = [];
        
        nNbrPass = 2;
        nLimitNumber = 0;
        if( not bFull ):
            nNbrPass = 2;
            nLimitNumber = 10;
            
        if( bOnlyNoDuplicateWithGlasses ):
            nNbrPass = 1;
            
        for numPass in range(nNbrPass):
            print( "INF: evaluate_total: pass: %d" % numPass );
            self.reset();
            resTotal.append([]);
            
            #if( bFull ):
            if( not bNoRelearn ):
                # first pass: apprentissage, sans duplicate glass
                if( numPass == 0 ):
                    strBaseName = "glass_duplication_off";
                    bDuplicateWithGlasses = False;
                else:
                    strBaseName = "glass_duplication_on";
                    bDuplicateWithGlasses = True;
                
                self.changeBase( strBaseName );
                rTimeToLearn = self.learn( "/home/nao/.local/faces/", nBeginAt = 0, nLimitNumber=0, bOverwrite = False, strRestrictToCameraType = "EOS600D", strRestrictToExpression = "", bDuplicateWithGlasses = bDuplicateWithGlasses );
                print( "INF: evaluate_total: rTimeToLearn: %f" % rTimeToLearn );

            timeBegin = time.time();
            for idx, folder in enumerate(listFolderToEvaluate):
                print( "INF: evaluate_total: evaluate: pass %d, folder: %d/%d: %s" % (numPass, idx+1,len(listFolderToEvaluate), folder ) );
                res = self.evaluate( "/home/nao/.local/test_faces2/" + folder + "/", "/home/nao/results_test/", nLimitNumber=nLimitNumber,rConfidenceLimit=rConfidenceLimit);
                resTotal[numPass].append( res );
            aTimeTaken.append( time.time() - timeBegin );
            dictBad.append( self.getDictEvaluateBadRecognised() );                
        # for - end
        print( "INF: evaluate_total: resTotal: %s" % resTotal );

        strFullTxt = "";
        for numPass in range(len(resTotal)):
            resSum = numpy.array([0,0,0,0,0,0.]);
            for res in resTotal[numPass]:
                #print( "add res: %s" % res );
                resSum += res;
            avgSum = resSum / len(resTotal[numPass]);

            # precision is the number of found good / number of selected ie (good+bad)
            # recall is the number of found good / all goods ie intended to be good
            rPrecision = 0.;
            rRecall = 0.;
            rSelected = resSum[2]+resSum[3];
            if( rSelected > 0. ):
                rPrecision = resSum[2] / rSelected;
            if( resSum[1] > 0. ):
                rRecall = resSum[2] / resSum[1]; # here it's a bit fake as true negative has been counted as good "ERROR134"
            
            strResSum = "[";
            for elem in resSum:
                strResSum += "%10.2f, " % elem;
            strResSum += "]";
            
            strAvgSum = "[";            
            for elem in avgSum:
                strAvgSum += "%10.2f, " % elem;
            strAvgSum += "]";            
            
            strFullTxt += "\n\nconf limit: %5.2f, time taken: %5.2fs\npass %d (img tested, must be good, good detect, bad detect, not detected, avg_confidence) :\nres sum: %s\navg sum: %s\n%%tage good: %5.1f%%, precision: %5.1f%%, recall: %5.1f%%\n\n" % ( rConfidenceLimit,aTimeTaken[numPass],numPass, strResSum,strAvgSum,avgSum[2]*100/float(avgSum[0]),rPrecision*100,rRecall*100 );
            #self.log( "dictBad: %s" % dictBad[numPass] );
            strTxtDictBad = self.computeStatOnBad(dictBad[numPass]);
            strFullTxt += "dictBad stat:\n%s" % strTxtDictBad;
        # for - end
        
        print strFullTxt;
        return strFullTxt;
    # class evaluate_total - end
    
    def evaluate_total_with_various_confidence( self, arConfidenceLimit ):
        pass
    # evaluate_total_with_various_confidence - end
        
    
# class FaceRecognition - end

faceRecognition = FaceRecognition();


class MemorizeUsers:
    """
        sometimes we have face recognized, sometime just a gender and an age.
        let's have a descriptor for dialog to differentiate every of the
    """
    def __init__(self):
        self.dInfos = [] # a dict of some "highlevel_user_id" => [last_time_updated, lastTrackID, nNbrUpdated, 
                                #                                                             strRecognized, nSumRecoOk, 
                                #                                                             rSumGenderProrated, rSumGenderConf, 
                                #                                                             rSumAgeProrated, rSumAgeConf, 
                                #                                                             rHeadSize, posInImage, headAngle]        
        self.nThresholdRecoStore = 3
        
    
    def updateAllUsers( self, rTime, allDecodedDatas ):
        for o in allDecodedDatas.objects:
            reco = faceRecognition.select_recognised( o.recognised );
            strRecognized = ""
            rRecoConf = 0.
            if reco != []:
                strRecognized, rRecoConf = reco
            self.updateUser( rTime, o.faceInfo.id, strRecognized, rRecoConf, o.gender, o.age )
            
    def getHighID_fromTrackID( self, nTrackID ):
        for i, v in enumerate( self.dInfos ):
            if v[1] == nTrackID:
                return i
        return -1
        
    def getTimeLastSeen( self, nHighID ):
        return self.dInfos[nHighID][0]
        
    def getInfos( self, nHighID ):
        """
        return accumulated infos about a user:
        [last time updated, last track id, nbr_updated, recognized_if_sure or "", gender_estimation(str), avg_age_if_sure (or -1)]
        """
        v = self.dInfos[nHighID][:] # copy
        print v
        
        if v[4] < self.nThresholdRecoStore:
            v[3] = ""
        v[5] = v[5]/v[6]
        v[7] = v[7]/v[8]
        
        if v[6] < 0.8: # means less than 0.2x4 or 0.4x2
            v[5] = -1
            
        if v[8] < 0.8:
            v[7] = -1
        
        
        del v[8]
        del v[6]
        del v[4]
        print v
        return v
        
    
    def updateUser( self, rTime, nTrackID, strRecognized = "", rRecoConf = 0., arGenderAndConf = [0,0.], arAgeAndConf=[1,0.], rHeadSize = 0.2, posInImage = None, headAngle = None ):
        """
        update data for each people on screen.
        - gender is between -1 and 1
        return an "highlevel_user_id"
        """
        
        rTimeShouldBeANewUser = 20. # after 20 sec, an unknow man coming shouldn't be the same than before
        
        if strRecognized != "" and rRecoConf < 0.55:
            strRecognized=""
            
        recoIdx = -1
        
        # search same track id
        for i, v in enumerate( self.dInfos ):
            if v[1] == nTrackID:
                recoIdx = i
            
        if recoIdx == -1 or rRecoConf > 0.70:
            # reco sur name
            for i, v in enumerate( self.dInfos ):
                if strRecognized == v[3] and (rRecoConf > 0.55 or (v[2] > 3. and rRecoConf > 0.70) ): # if same, or recognize a previous tracked user
                    if nTrackID != v[1]:
                        print( "INF: abcdk.facerecognition.MemorizeUsers.updateUser: using reco name: track id: %s => high ID %s (prev trackid: %s)" % (nTrackID, i, v[1]) )
                        if recoIdx != -1:
                            print( "WRN: abcdk.facerecognition.MemorizeUsers.updateUser: previously unrecognized, we should output some apologise to this user" )
                        
                        self.dInfos[i][1] = nTrackID
                    recoIdx = i
                    break

        if recoIdx == -1 and arAgeAndConf[1] > 0.4:
            # reco on age
            for i, v in enumerate( self.dInfos ):
                # we want: 40,0.5 + 
                if v[8] > 0:
                    rAvgAge = v[7]/v[8]
                else:
                    rAvgAge = -1
                if v[6] > 0:
                    rAvgGender = v[5]/v[6]
                else:
                    rAvgGender = -1
                print( "DBG: abcdk.facerecognition.MemorizeUsers.updateUser: trying reco on age: high id: %d, avg age: %s, avg gender: %s" % (i,rAvgAge,rAvgGender) )
                if abs(rAvgAge - arAgeAndConf[0]) < 6. and (abs(rAvgGender - arGenderAndConf[0]) < 0.3 or arGenderAndConf[1] < 0.4) and rTime-v[0] < rTimeShouldBeANewUser:
                    print( "INF: abcdk.facerecognition.MemorizeUsers.updateUser: using age: track id: %s => high ID %s (prev trackid: %s)" % (nTrackID, i, v[1]) )
                    self.dInfos[i][1] = nTrackID
                    recoIdx = i
                    break
                    
        if recoIdx == -1:
            recoIdx = len(self.dInfos)
            print( "INF: abcdk.facerecognition.MemorizeUsers.updateUser: new high level user %d: track id: %s" % (recoIdx,nTrackID) )
            emptyUserData = [rTime, nTrackID, 0,
                                    "", 0,
                                    0,0.,
                                    0,0.,
                                    0., [0.,0.], 0. ]
                                    
            self.dInfos.append( emptyUserData )
            
        # update infos
        self.dInfos[recoIdx][0] = rTime
        self.dInfos[recoIdx][2] += 1
        if strRecognized != "":
            if strRecognized == self.dInfos[recoIdx][3]:
                self.dInfos[recoIdx][4] += 1
                #~ print( "DBG: abcdk.facerecognition.MemorizeUsers.updateUser: increasing sureness of facereco for user %d to %d ('%s')" % (recoIdx,self.dInfos[recoIdx][4],strRecognized) )
            else:
                if self.dInfos[recoIdx][4] <self.nThresholdRecoStore:
                    print( "DBG: abcdk.facerecognition.MemorizeUsers.updateUser: WRN: changing facereco name for user %d from '%s' to '%s'" % (recoIdx,self.dInfos[recoIdx][3], strRecognized ) )
                    self.dInfos[recoIdx][3] = strRecognized
                    self.dInfos[recoIdx][4] = 1
        self.dInfos[recoIdx][5] += arGenderAndConf[0]*arGenderAndConf[1]
        self.dInfos[recoIdx][6] += arGenderAndConf[1]                    
        self.dInfos[recoIdx][7] += arAgeAndConf[0]*arAgeAndConf[1]
        self.dInfos[recoIdx][8] += arAgeAndConf[1]
        
        return recoIdx
                
    def innerTest(self):        
        test.assert_check(self.updateUser( 1., 12, "Alex", 0.62, [1., 0.8], [40, 0.5] ), 0 )
        test.assert_check(self.updateUser( 1.1, 12, "Toto", 0.1, [1., 0.], [12, 0.1] ), 0 ) # same track id: easy
        test.assert_check(self.updateUser( 1.1, 14, "Blaise", 0.1, [1., 0.4], [30, 0.1] ), 1 )
        test.assert_check(self.updateUser( 1.1, 14, "Blaise", 0.1, [1., 0.7], [30, 0.5] ), 1 )
        test.assert_check(self.updateUser( 1.2, 15, "Alex", 0.62, [1., 0.], [43, 0.5] ), 0 ) # reco sur name => convert id
        test.assert_check(self.updateUser( 1.5, 15, "Toto", 0.1, [1., 0.], [12, 0.1] ), 0 )
        test.assert_check(self.updateUser( 2.1, 17, "", 0.1, [1., 0.], [30, 0.5] ), 1 ) # unknow people (blaise, based on age)
        test.assert_check(self.updateUser( 2.4, 18, "", 0.1, [1., 0.], [40, 0.41] ), 0 ) # alex based on age
        test.assert_check(self.updateUser( 3.4, 19, "", 0.1, [-1., 0.5], [40, 0.41] ), 2 ) # a girl
        test.assert_check(self.updateUser( 41., 20, "Jim", 0.1, [1., 0.8], [40, 0.5] ), 3 ) # later should'nt rely on age!
        test.assert_check(self.updateUser( 45., 30, "Alex", 0.62, [1., 0.8], [40, 0.5] ), 0 ) # later, should rely on name
        test.assert_check(self.updateUser( 81., 32, "Alex", 0.1, [1., 0.8], [40, 0.5] ), 4 ) # later => user not recognised
        # Q: si j'ai deja dit bonjour a Alexandre ce matin, si je vois un gars venir, je lui dit bonjour et lui propose de l'aide,
        # que faire si après je me rend compte que c'est Alexandre ? switch back to previous ? oui!
        test.assert_check(self.updateUser( 82., 32, "Alex", 0.82, [1., 0.8], [40, 0.5] ), 0 ) # use new user or switch to old one ?
        
# class MemorizeUsers - end

memorizeUsers = MemorizeUsers()

def testMemorizeUsers():
    memorizeUsers.innerTest()
    exit(1)
#~ testMemorizeUsers()

class FaceMemory:
    """
    Memorize last seen people to filter stuff
    """
    def __init__(self):
        self.lastTimeSeen = time.time();
        self.nCurrentID = -1; # the current face id
        self.nLastRecoId = -1; # the current face id
        # accumulation of recent data for current seen user
        self.listAge = []
        self.listGender = []
        self.listReco = [] # list of potential ressemblant human
        
        self.nbrSampling = 5; # number of analyse to get an average (an analyse takes roughly 10ms) (but no in fact it's 300ms with tracking enabled and ...)
        self.nbrSamplingAge = 3;
        
        self.rTimeForSomeoneToBeSeenAsLeft = 3. # when we don't see someone for this time, it's like he has left
        self.bWasLedLighten = False;
        
        self.strLockedName = "";
        self.timeLockedName = time.time();
        
        self.lastFaceInfo = None; # last info of a face analysed or recognised
        self.lastFacePos = [];
        self.timeLastFaceInfo = 0;
        
        self.interesting_info = None; # this store info, that could be less sure, but sometimes usefull
        self.interesting_time = time.time()-1000;
        
        # proeminent: often someone more proeminent needs to be handled
        self.proeminent_timeFirstSeen = time.time()-1000;
        self.proeminent_nID = -1;
        
        #~ self.dictFacRecoTrackID = dict()
        
        self.mem = naoqitools.myGetProxy( "ALMemory" );
        self.lastUserChange = None
        
        self.bDebugMode = False
        
        try:
            self.ledsDcm = leds.leds.ledsDcm
        except:
            print( "ERR: leds module stk problems" )
            self.ledsDcm = None # $$$$ leds module doesn't works anymore
        
        
    def getLastFaceInfo( self ):
        """
        """
        retVal = [self.timeLastFaceInfo,self.lastFaceInfo,self.lastFacePos];
        print( "INF: abcdk.facerecognition.faceMemory.getLastFaceInfo: returning: %s" % retVal );
        return retVal;
        
    def getLastFaceInterestingInfo( self ):
        """
        get information about last recognised or analysed face and associated time
        return [time seen, info about face and last know pos]
        """
        lastInfos = self.getLastFaceInfo();
        info = lastInfos[1];
        time_info = lastInfos[0];
        if( info == None and self.interesting_info != None ):
            info = self.interesting_info[:];
            time_info = self.interesting_time;
        retVal = [time_info,info,lastInfos[2]]; # pos could be false or related to someone else!
        print( "INF: abcdk.facerecognition.faceMemory.getLastFaceInterestingInfo: returning: %s" % retVal );
        return retVal;
        
    def setNammingOfLastHuman( self, strName ):
        """
        Set a default namming, if noone was seen or test or debug or ...
        """
        print( "INF: abcdk.FaceMemory.setNammingOfLastHuman: setting: '%s'" % strName );
        self.interesting_time = time.time();
        self.interesting_info = [None,strName,None];
        
        
    def getNammingOfLastHuman( self, bJustFirstName = False, bForceGender = False ):
        """
        return a descriptor for the last seen human (name, or mister or madam)
        or "" if no or too much time
        - bJustFirstName: just return the firstname instead of 0_Alexandre_Mazel
        """
        import humans
        import translate
        infos = self.getLastFaceInterestingInfo();
        lastTime = infos[0];
        if( time.time() - lastTime > 50 ):
            return "";
        infos = infos[1];
        strFaceName = infos[1];
        if( strFaceName != "" and strFaceName != None  and not bForceGender ):
            print( "DBG: getNammingOfLastHuman: strFaceName: %s" % strFaceName );
            if( bJustFirstName ):
                splitted = strFaceName.split("_" ) # was x_FirstName_NAME
                if( len(splitted) == 3 ):
                    return splitted[1]
            
            id=faceRecognition.getID(strFaceName);
            print( "DBG: getNammingOfLastHuman: after get id: %s (facename:%s)" % (id,strFaceName) );
            if( id == -1 or humans.humanManager.getHumanInfo( id ) == None ):
                strName = strFaceName;
            else:
                try:
                    humans.humanManager.enforceHumanExists( strFaceName, id )
                    strName = humans.humanManager.getHumanInfo( id ).getNaming();
                except:
                    strName = strFaceName.split("_")[-1] #  00098__MAZEL_alexandre => alexandre
                    print( "DBG: getNammingOfLastHuman: error occurs, strFaceName: %s => get name on the fly: %s" % (strFaceName,strName) );
                print( "DBG: getNammingOfLastHuman: after getNaming, strName: %s" % strName );
                
        else:
            rAge = infos[2];
            rGender = infos[3];
            strName = translate.getTitle( rAge, rGender );
            print( "DBG: getNammingOfLastHuman: after getTitle, strName: %s" % strName );
        return str(strName);            
    # getNammingOfLastHuman  - end
    
    def getGenderOfLastHuman( self ):
        """
        return 1 if man or 2 if woman (as in secu). 
        0 if unknown.
        """
        
        infos = self.getLastFaceInterestingInfo();
        lastTime = infos[0];
        if( time.time() - lastTime > 10 ):
            return 0;
            
        infos = infos[1];
                
        rGender = infos[3];
        if( abs(rGender) < 0.4 ):
            return 0
        if( rGender > 0 ):
            return 1
        return 2
    # getGenderOfLastHuman - end
    
    def recordUserChange( self, nNewTrackID, nPrevTrackID ):
        """
        record that a new user get the focus
        """
        
        nNewHighLevelFocusID = memorizeUsers.getHighID_fromTrackID(nNewTrackID)
        nPrevHighLevelFocus = memorizeUsers.getHighID_fromTrackID(nPrevTrackID) 
        rTime = memorizeUsers.getTimeLastSeen(nPrevHighLevelFocus)
        bPrevGone = time.time() - rTime > self.rTimeForSomeoneToBeSeenAsLeft

        eventInfo = [nNewHighLevelFocusID, nPrevHighLevelFocus, bPrevGone]
        if self.mem: self.mem.raiseMicroEvent( "FaceRecognition/UserChange", eventInfo )
        self.lastUserChange = eventInfo
        
    def getLastUserChange( self ):
        return self.lastUserChange
        
        
    def updateSeen( self, faceInfos ):
        """
        take the face infos, and memorize info for further use
        - faceInfos: information directly from the ALMemory FaceDetection/FaceDetected containing a bunch of recognized face
        Return:
            - None: no one seen
            - [face_id, face_x,face_y, face_h, face_pitch, face_yaw, face_roll]: someone with not enough information, face_x and face_y:  the face position in [-0.5,+0.5]; face_h: height in [0..1]
            - [face_id, recognized_id, avg_age, avg_gender,face_x,face_y, face_h, face_pitch, face_yaw, face_roll ]: 
                #~ - bNewcomers: true every some seconds
                - face_id: the human id from the face detection, valid only for a few second (8s?)
                - recognized_id: the unique id of a recognized people or ""
                - avg_age: a median of the found age, or -10
                - avg_gender: a median of the gender, or -10
                
        Raise also info in:
                - FaceRecognition/NbrManyFaces: everytime more than two faces are seen, trigger a value
                - FaceRecognition/UserChange: [id, prevId, bPrevGone] everytime a user change, output its id, second parameter is previous one. The new one could be -1 if someone leaves with noone replacing him
        """
        
        decodedData = extractortools.FaceDetectionNew_decodeInfos(faceInfos);
        if self.bDebugMode: print( "DBG: abcdk.facerecognition.updateSeen: full debug:\n%s" % str(decodedData))
        
        # memorize and track id conversion
        memorizeUsers.updateAllUsers( time.time(), decodedData )
        
        if( len(decodedData.objects) < 1 ):
            if( self.bWasLedLighten ):
                if self.ledsDcm: self.ledsDcm.setEyesOneLed( 0, 0.9, 0x00 );
                if self.ledsDcm: self.ledsDcm.setEyesOneLed( 1, 0.9, 0x00 );
                self.bWasLedLighten = False;
            return None;

        if( len(decodedData.objects) > 1 ): # was 2
            if self.mem: self.mem.raiseMicroEvent( "FaceRecognition/NbrManyFaces", len(decodedData.objects) )
        # default value in case of vertices error or ???
        face_x = face_y = 0.
        face_h = 0.5
        face_pitch = face_yaw = face_roll = 0.
        
                    
        if self.ledsDcm: self.ledsDcm.setEyesOneLed( 0, 0.05, 0x00FF00 );
        self.bWasLedLighten = True;

        objectBest = extractortools.FaceDetectionNew_select_face(decodedData).objects[0];
        object = extractortools.FaceDetectionNew_select_face(decodedData,self.nCurrentID).objects[0];
        # bForceSwitch = True # why ?
        bForceSwitch = False
        if( object.faceInfo.id != objectBest.faceInfo.id ):
            print( "INF: abcdk.facerecognition.updateSeen: current tracking id: %d, isn't the most proeminent: %s" % (object.faceInfo.id, objectBest.faceInfo.id) )
            if( self.proeminent_nID != objectBest.faceInfo.id ):
                self.proeminent_nID = objectBest.faceInfo.id
                self.proeminent_timeFirstSeen = time.time()
            elif time.time() - self.proeminent_timeFirstSeen > 4.:
                print( "INF: abcdk.facerecognition.updateSeen: forcing a switch to a more proeminent" )
                object = objectBest

        vertices = object.faceInfo.vertices;
        if( abs( vertices[0][0] ) < 2000 or abs( vertices[2][1] ) < 2000 ):
            x = (vertices[0][0]+vertices[3][0] )/ 2;
            y = (vertices[0][1]+vertices[3][1] )/ 2;
            face_x = (x - 160)/320.; # will output a [-0.5,+05]
            face_y = (y - 120)/240.; # will output a [-0.5,+05]
            face_h = ( vertices[3][1] - vertices[0][1] ) / 240.;
            face_pitch, face_yaw, face_roll = object.faceDirection.rPitch,object.faceDirection.rYaw,object.faceDirection.rRoll;
            
        if( object.faceInfo.id != self.nCurrentID ):
            bSameHuman_ProvedByFaceReco = False;
            if( len(self.listReco) > 0 ):
                aList = sorted( self.listReco, key=lambda tup:tup[1], reverse=True );
                strPrevName = aList[0][0];
                rPrevConf = aList[0][1];
                print( "DBG: abcdk.facerecognition.updateSeen: new people seems like prev? prev: %s, %s" % (strPrevName,rPrevConf) );   
                if( rPrevConf > 0.4 ):
                    aListReco = faceRecognition.findBestForOneName( object.recognised, strPrevName );
                    if( len(aListReco) > 0 ):
                        reco = aListReco[0];
                        print( "DBG: abcdk.facerecognition.updateSeen: new people seems like prev? new: %s" % reco );
                        if( reco != None and reco != [] and reco[1] > 0.4 ):
                            if( reco[0][-1] == "2" ):
                                reco[0] = reco[0][:-1];
                            if( reco[0] == strPrevName ):
                                # it's the same guy
                                print( "DBG: abcdk.facerecognition.updateSeen: new people? no it looks like it's the same" );
                                bSameHuman_ProvedByFaceReco = True;
            if( not bSameHuman_ProvedByFaceReco ):
                if( time.time() - self.interesting_time < self.rTimeForSomeoneToBeSeenAsLeft and not bForceSwitch ):
                    print( "DBG: we loose our target %d, but let's wait a bit to be sure it's lost for a long time..." % self.nCurrentID )
                    return None;
                print( "DBG: abcdk.facerecognition.updateSeen: human has changed, resetting memory!, current id: %d, new: %d" % (self.nCurrentID,object.faceInfo.id));                
                self.recordUserChange(  object.faceInfo.id, self.nCurrentID ) # [object.faceInfo.id,-1]
                self.nCurrentID = object.faceInfo.id;
                self.listAge = [];
                self.listGender = [];
                self.listReco = [];
                if( time.time() - self.timeLockedName > self.rTimeForSomeoneToBeSeenAsLeft ): # you must lose someone more than x sec to forget it
                    self.strLockedName = "";
            else:
                self.recordUserChange( object.faceInfo.id, self.nCurrentID  ) # [object.faceInfo.id,self.nCurrentID]
                self.nCurrentID = object.faceInfo.id; # adding this line, here, is it a good id ?
            
        if( object.age[1] > 0.2 ):
            self.listAge.append( object.age );
        
        if( object.gender[1] > 0.2 ):            
            if( object.gender[0] == 0 ):
                object.gender[0] = -1;            
            self.listGender.append( object.gender );
            
        reco = faceRecognition.select_recognised( object.recognised );
        print( "DBG: abcdk.facerecognition.updateSeen: recognized: %s" % reco );                        
        if( reco != None and reco != [] and reco[1] > 0.4 ):
            if( reco[0][-1] == "2" ):
                reco[0] = reco[0][:-1];
            print( "DBG: abcdk.facerecognition.updateSeen: recognized SURE: %s" % reco );
            self.listReco.append( reco );
          
        # store quick info:
        if( 1 ):
            strReco = "";
            if( reco != [] and reco[1] > 0.55 ):
                strReco = reco[0];
                humans.humanManager.enforceHumanExists( strReco )
            else:
                if( self.interesting_info != None and time.time() - self.interesting_time < 10 and object.faceInfo.id == self.interesting_info[0] ):
                    # keep it!
                    strReco = self.interesting_info[1];
            self.interesting_info = [self.nCurrentID, strReco, object.age, object.gender[0]*object.gender[1]*2, face_x, face_y,face_h,face_pitch, face_yaw, face_roll]; # *2: because the confidence is low on gender
            self.interesting_time = time.time();
            
            
        bResetArray = False;
        
        # summarize
        bNoFaceRecoButAges = ( len( self.listAge ) > self.nbrSamplingAge and len(self.listReco) < 1 );
        bFaceRecoButALotAges = len( self.listAge ) > self.nbrSamplingAge*3;
        bEnoughFaceSure = len(self.listReco) > self.nbrSampling;
        print( "DBG: abcdk.facerecognition.updateSeen: bNoFaceRecoButAges: %d, bFaceRecoButALotAges: %d, bEnoughFaceSure: %d, len(listReco): %d" % (bNoFaceRecoButAges,bFaceRecoButALotAges,bEnoughFaceSure,len(self.listReco)) );
        if( bNoFaceRecoButAges or bEnoughFaceSure or bFaceRecoButALotAges ):
            bResetArray = True;
            strFaceName = findMostProbable( self.listReco );
            if( self.strLockedName != "" and strFaceName == self.strLockedName ):
                self.timeLockedName = time.time(); # after two equal anlse, even if we lost this face or change face id, we will continue to memorize it for some seconds
            if( self.strLockedName != "" and self.strLockedName != strFaceName ):
                print( "WRN: abcdk.facerecognition.updateSeen: reusing locked name: '%s' instead of '%s'" % (self.strLockedName, strFaceName) );
                strFaceName = self.strLockedName;
                
            if( strFaceName != "" ):
                self.strLockedName = strFaceName;
                if self.ledsDcm: self.ledsDcm.setEyesOneLed( 1, 0.05, 0x0000FF );
                print( "INF: abcdk.facerecognition.updateSeen: face name: '%s'" % strFaceName );
            else:
                if self.ledsDcm: self.ledsDcm.setEyesOneLed( 1, 0.9, 0x00 );
                
                
            if( not bEnoughFaceSure or strFaceName != "" ):
                #
                # we output a full answer only if human recognized or no reco sure and enough ages
                #
                
                # age
                rSumAge = 0.;
                rSumCoef = 0.;
                for i in range(len(self.listAge)):
                    rSumAge += (self.listAge[i][0]*self.listAge[i][1]);
                    rSumCoef += self.listAge[i][1];
                if( rSumCoef > 0.1 ):
                    rAvgAge = rSumAge/rSumCoef;
                else:
                    rAvgAge = -10;
                # gender
                rSumGender = 0.;
                rSumCoef = 0.;
                for i in range(len(self.listGender)):
                    rSumGender += (self.listGender[i][0]*self.listGender[i][1]);
                    rSumCoef += self.listGender[i][1];
                if( rSumCoef > 0.1 ):
                    rAvgGender = rSumGender/rSumCoef;
                else:
                    rAvgGender = -10.;
                aOutput = [self.nCurrentID, strFaceName, rAvgAge, rAvgGender, face_x, face_y,face_h,face_pitch, face_yaw, face_roll];
                print( "INF: abcdk.facerecognition.updateSeen: outputting total info: %s" % aOutput );
                if strFaceName != "":
                    import humans
                    humans.humanManager.enforceHumanExists( strFaceName )

                # reset for next time
                self.listAge = [];
                self.listGender = [];
                self.listReco = [];
                
                self.timeLastFaceInfo = time.time();
                self.lastFaceInfo = aOutput;
                
                # update info in memory
                strNamming = self.getNammingOfLastHuman()
                if self.mem: self.mem.insertData( "human_name", strNamming )
                if self.mem: 
                    # else, we're not on a robot or ...
                    import actors
                    if strFaceName != "":
                        actors.actorsManager.setCurrentActor( strFaceName.split("_")[0] )
                    else:
                        actors.actorsManager.setCurrentActor( -1 )
                    #~ else:
                        #~ import actors
                        #~ actors.actorsManager.setCurrentActor( self.getNammingOfLastHuman())
                return aOutput;

        if( bResetArray ):
            # reset for next time
            self.listAge = [];
            self.listGender = [];
            self.listReco = [];
            
        self.lastFacePos = [face_x, face_y,face_h,face_pitch, face_yaw, face_roll];
        return [self.nCurrentID,face_x, face_y,face_h,face_pitch, face_yaw, face_roll];
    # updateSeen - end
    
    def getLastSeen( bMustBeSure = True ):
        """
        get information about last seen human
        - bMustBeSure: output only info if sure
        return [timestamp, rConfidence, info] 
            - with confidence: a joint confidence giving an idea of sure it is
            - with info: [self.nCurrentID, strFaceName, rAvgAge, rAvgGender, face_x, face_y,face_h]
            - with "" if not recognized
        """
        pass
        # use getLastFaceInfo instead
        
        
    def renderDebugOnImage( self, strSrcFilename, resFromFaceDetection ):
        """
        render debug using current analyse and current memory of users
        """
        print( "FaceMemory.renderDebugOnImage: opening '%s'..." % strSrcFilename )
        import cv2
        im = cv2.imread( strSrcFilename )
        decodedData = extractortools.FaceDetectionNew_decodeInfos(resFromFaceDetection);        
        
        # recompute id=>high id table
        # ugly !
        extraInfo = []
#        extraInfo = [ [-1, "test", (34,34,255)] ]
        for o in decodedData.objects:                
            high_id = memorizeUsers.getHighID_fromTrackID( o.faceInfo.id )
            extraInfo.append( [o.faceInfo.id,"hID: %d" % high_id, (180,0,0) ] )
            info = memorizeUsers.getInfos( high_id )
            strGenderAndAge = ""
            if info[4] != -1:
                if info[4] > 0.5: strGenderAndAge += "male"
                elif info[4] < -0.5: strGenderAndAge += "female"
                else: strGenderAndAge += "human"
                strGenderAndAge += " "
            if info[5] != -1:
                strGenderAndAge += "(%d)"% info[5]
            extraInfo.append( [o.faceInfo.id,"%s" % strGenderAndAge, (180,0,0) ] )
            extraInfo.append( [o.faceInfo.id,"%s" % info[3].split("_")[-1], (180,0,0) ] )
        
        extractortools.FaceDetectionNew_drawResultsOnOpenedImage( decodedData, im, astrExtraTextAndColor = extraInfo )
        return im
            
# class FaceMemory - end

faceMemory = FaceMemory();


def getIDFromFilename(strFilename):
    f = FaceRecognition()
    return f.getID(strFilename)

def getNameFromFilename(strFilename):
    f = FaceRecognition()
    return f.getName(strFilename);
    
    
def findNiceFace( strPath, strHumanName ):
    """
    look for a nice picture of someone (centred, facing objectiv, nice, ...)
    - strPath: a path with some cropped face: current filenaming is: "1462363975,278ms__cropped_face__0_Alexandre_MAZEL__072.jpg" (last figures is confidence)
    - strHumanName: the name of the human    
    return:
        the name of the best file or None if no best file
    """
    rBestScore = 0.
    strBestFile = None
    strHumanName =strHumanName.upper()
    for file in sorted( os.listdir( strPath) ):
        if strHumanName in file.upper():
            strTotalFilename = strPath + file
            rScoreSize = os.path.getsize(strTotalFilename)/(float)(20*1024)            
            rConfScore = int(file[-7:-4]) / 100.
            rCenteredScore = 0.5 #NDEV            
            rScore = rScoreSize * rConfScore * rCenteredScore
            print( "DBG: findNiceFace: file: '%s', rScoreSize: %s, rConfScore: %s, rCenteredScore: %s, rScore: %s" % ( file, rScoreSize, rConfScore, rCenteredScore, rScore ) )
            if( rScore > rBestScore ):
                rBestScore = rScore
                strBestFile = strPath + file
    print( "DBG: findNiceFace: returning: file: '%s'" % ( strBestFile ) )
    return strBestFile
# findNiceFace - end
#~ print( findNiceFace( "/tmp/rec_faces_cropped/", "MAZEL" ) )
#~ print( findNiceFace( "/tmp/rec_faces_cropped/", "CANIOT" ) )
#~ exit(1)

def tuneTrackingTwoUsers( strFile ):
    timeBase = 1479465700.
    taggedEvents = [
        # time in image of event begin, time in image of event ends (or should be detected at max), new high level id, prev high level id, is prev left?, comments
        [20.37, 22.55, 0, -1, False, "user1 arrives",],
#        [23.81, "user2 arrives",], # generate no event
        [26.26, 26.26+2.5, 1, 0, True, "user1 leaves (switch to 2)",], # he leaves at 26.26, but in fact, we should wait a bit before forgetting it
#        [31.31, 31.31+1.0, 0, -1, False, "user1 came back",], # generate no event
        [34.88, 34.88+2.5, 0, 1, True, "user2 leaves",], 
#        [37.14, 37.14+2.5, 0, -1, False, "user2 came back",], # generate no event
#        [45.01, 45.61, 0, -1, False, "users switch sides",], # generate no event (should)
        [49.77, 0, -1, False, "users switch sides again",],
        [55.08, 0, -1, False, "user2 leaves",],
        [57.26, 0, -1, False, "user2 came back",],
        [58.32, 0, -1, False, "user1 leaves",],
        [61.54, 0, -1, False, "user1 came back",],
        [61.93, 0, -1, False, "user2 leaves",],
        [63.34, 0, -1, False, "user1 leaves",],        
    ]
    nNumNextTaggedEvent = 0
    f = open("../../../datas/%s" % strFile, "rt" )
    datatxt = f.read()
    f.close()
    datas = eval(datatxt)
    rOriginalDelay = 0.0435 # 1005 images from 20.08 over 63.86 => 43.78s
    rOriginalDelay = 0.05
    #~ rOriginalDelay = 0.0001
    prevuc = None
    #~ datas = datas[150:160] # moment with two peoples
    #~ datas = datas[120:150] # moment with two peoples alex come back
    for idx, resana in enumerate(datas):
        print( "\n"+"*" * 40 )        
        name,res = resana
        print name
        
        if 1:
            relative_time = name.replace("camera_viewer_0__14794657","")
            relative_time = int(relative_time.split("_")[0]) + int(relative_time.split("_")[1]) / 100.
            print relative_time
            time.sleep(rOriginalDelay)
            faceMemory.updateSeen(res)
            uc = faceMemory.getLastUserChange()
            if uc != prevuc and 0:
                prevuc = uc
                print( "!"*40 + " new uc: %s" % uc )
                print( "current tag theorical: %s" % taggedEvents[nNumNextTaggedEvent] )
                tag_reltime_begin, tag_reltime_end, newid, previd, hasgone, desc = taggedEvents[nNumNextTaggedEvent]
                uc_newid, uc_previd, uc_gone = uc
                assert( relative_time > tag_reltime_begin and relative_time < tag_reltime_end)
                assert( newid == uc_newid )
                assert( previd == uc_previd )
                assert( hasgone == uc_gone )
                print( "OK: event tag seems ok: at:%s (ref:%s): %s" % (relative_time, tag_reltime_begin, desc ) )
                nNumNextTaggedEvent += 1

        if 1:
            # write debug
            filename = resana[0]
            strPathSrc = "/home/likewise-open/ALDEBARAN/amazel/dev/git/protolab_group/datas/ears_scenario_2_recorded_images_for_tracking/"
            strPathDst = "/tmp/"
            imgDebug = faceMemory.renderDebugOnImage( strPathSrc + filename, res )

            import cv2
            try:
                filename = "%08d.jpg" % idx # for ffmpeg # ffmpeg -framerate 23 -i /tmp/%08d.jpg -c:v libx264 -r 30 -pix_fmt yuv420p /tmp/out.mp4
                cv2.imwrite( strPathDst + filename, imgDebug )
            except BaseException, err: print( "Exception: err: %s" % err )
            #~ return
            
#tuneTrackingTwoUsers - end
    
    
def autoTest():
    f = FaceRecognition();    
    aDecoded = f.getInfoFromImage( "00098__2013_01_11-00h00m00s003ms__EOS600D__Happy.JPG" );
    print( "aDecoded image info: %s" % str( aDecoded ) );
    assert( aDecoded == [98,"2013_01_11", "00h00m00s003ms", "EOS600D", "Happy", False] );

    aDecoded = f.getInfoFromImage( "00098__2013_01_11-00h00m00s003ms__EOS600D__Happy__G.JPG" );
    print( "aDecoded image info: %s" % str( aDecoded ) );
    assert( aDecoded == [98,"2013_01_11", "00h00m00s003ms", "EOS600D", "Happy", True] );

    aDecoded = f.getInfoFromImage( "00198__2013_01_11-00h00m00s003ms__EOS600D.JPG" );
    print( "aDecoded image info: %s" % str( aDecoded ) );
    assert( aDecoded == [198,"2013_01_11", "00h00m00s003ms", "EOS600D", "", False] );
    
    aDecoded = f.getInfoFromImage( "00198__2013_01_11-00h00m00s003ms__EOS600D__G.JPG" );
    print( "aDecoded image info: %s" % str( aDecoded ) );
    assert( aDecoded == [198,"2013_01_11", "00h00m00s003ms", "EOS600D", "", True] );
    

    aDecoded = f.getInfoFromImage( "00070__2012_11_03-20h33m12s607ms__Unknown.jpg" );
    print( "aDecoded image info: %s" % str( aDecoded ) );
    assert( aDecoded == [70,"2012_11_03", "20h33m12s607ms", "Unknown", "", False] );

    aDecoded = f.getInfoFromImage( "00070__2012_11_03-20h33m12s607ms__Unknown__G.jpg" );
    print( "aDecoded image info: %s" % str( aDecoded ) );
    assert( aDecoded == [70,"2012_11_03", "20h33m12s607ms", "Unknown", "", True] );

    
    aDecoded = f.getInfoFromImage( "00100__2012_11_03-20h33m12s607ms.jpg" );
    print( "aDecoded image info: %s" % str( aDecoded ) );
    assert( aDecoded == [100,"2012_11_03", "20h33m12s607ms", "Unknown", "", False] );    

    aDecoded = f.getInfoFromImage( "00101__2012_11_03-20h33m12s607ms__G.jpg" );
    print( "aDecoded image info: %s" % str( aDecoded ) );
    assert( aDecoded == [101,"2012_11_03", "20h33m12s607ms", "Unknown", "", True] );   
    

    aDecoded = f.getInfoFromImage( "00002__2012_01_01-00h00m00s001ms.JPG" );
    print( "aDecoded image info: %s" % str( aDecoded ) );
    assert( aDecoded == [2,"2012_01_01", "00h00m00s001ms", "Unknown", "", False] );

    aDecoded = f.getInfoFromImage( "00200__2012_01_01-00h00m00s001ms__G.JPG" );
    print( "aDecoded image info: %s" % str( aDecoded ) );
    assert( aDecoded == [200,"2012_01_01", "00h00m00s001ms", "Unknown", "", True] );
    
    aDecoded = f.getInfoFromImage( "00042__2012_01_01_00h00m00s001ms.JPG" );
    print( "aDecoded image info: %s" % str( aDecoded ) );
    assert( aDecoded == [42,"2012_01_01", "00h00m00s001ms", "Unknown", "", False] );

    aDecoded = f.getInfoFromImage( "None_038.jpg" ); # this line could generate warnings !
    print( "aDecoded image info: %s" % str( aDecoded ) );
    assert( aDecoded == [-1,"", "", "Unknown", "", False] );
    
    #~ f.learn("/home/nao/.local/faces/", bOverwrite=True)
    #~ f.evaluate("/home/nao/alex/", "/home/nao/results/")    
    
    mu = MemorizeUsers()
    mu.innerTest()
    
# autoTest - end

if __name__ == "__main__":
    #autoTest();
    tuneTrackingTwoUsers("resfacedetect.txt")    
    
    pass