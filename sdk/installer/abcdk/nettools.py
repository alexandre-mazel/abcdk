# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# String tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################


"""Tools to work with net, web, caching web page, ftp, ping..."""

print( "importing abcdk.nettools" );

import time

import debug
import naoqitools
import pathtools
import filetools
import random
import system
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

def getHostFolderAndFile( strWebAddress ):
    "separate host, directory and filename from a web address"
    "ie: 'http://mangedisque.com/Alma/index.html' => ['http://mangedisque.com', 'Alma', 'index.html'];"

    strHostname = "";
    strFoldersName = "";
    strFileName = "";

    strRemaining = strWebAddress;
    nIndex = strRemaining.find( '//' );
    if( nIndex != -1 ):
        strHostname = strRemaining[:nIndex+2];
        strRemaining = strRemaining[nIndex+2:];
    else:
        strHostname = "http://";

    nIndex = strRemaining.find( '/' );
    if( nIndex != -1 ):
         strHostname += strRemaining[:nIndex];
         strRemaining = strRemaining[nIndex:];
    else:
        strHostname += strRemaining;
        strRemaining = "";

    nIndex = strRemaining.rfind( '/');
    if( nIndex != -1 ):
         strFoldersName = strRemaining[:nIndex+1];
         strFileName = strRemaining[nIndex+1:];
    else:
        strFileName = "index.php";

    if( strHostname[0] in ['"', "'"] ):
        strHostname = strHostname[1:];

    if( strFileName[-1] in ['"', "'"] ):
        strFileName = strFileName[:-1];

    return [ strHostname, strFoldersName, strFileName ];
# getHostFolderAndFile - end
#print( "%s" % getHostFolderAndFile( 'http://mangedisque.com/Alma/index.html' ) ); # pass
# print( "%s" % getHostFolderAndFile( 'http://google.com/index.html' ) ); # pass

def webCache_getPath():
    return pathtools.getCachePath() +  "WebCache" + pathtools.getDirectorySeparator();
# webCache_getPath - end

def webCache_getFilename( strHtmlAdress ):
    "return a filename relative to a web request"
    strHtmlAdress = strHtmlAdress.replace( "?", "_PARAMS_" );
    strHtmlAdress = strHtmlAdress.replace( "&", "_AND_" );
    strHtmlAdress = strHtmlAdress.replace( ".", "__" );
    strHtmlAdress = strHtmlAdress.replace( "/", "_I_" );
    strHtmlAdress = strHtmlAdress.replace( "\\", "_I_" );
    strHtmlAdress = strHtmlAdress.replace( "=", "_EQ_" );
    strHtmlAdress = strHtmlAdress.replace( ":", "_SEP_" );
    return webCache_getPath() + strHtmlAdress + ".dat";
# webCache_getFilename - end

def webCache_write( strHtmlAdress, strPageContents ):
    "Add web results to cache, so that it's possible to get them faster, or if internet is not present at that moment"
    strFilename = webCache_getFilename( strHtmlAdress );
    filetools.makedirsQuiet( webCache_getPath() );
    file = open( strFilename, "wb" );
    file.write( strPageContents );
    file.close();
# webCache_write - end

def webCache_get( strHtmlAdress ):
    "get previously cached or False if no info"
    strFilename = webCache_getFilename( strHtmlAdress );
    if( not filetools.isFileExists( strFilename ) ):
        return False;
    print( "WRN: nettools.webCache_get: cache hit for '%s', returning previously cached results." % strHtmlAdress );
    return filetools.getFileContents( strFilename );
# webCache_get - end

def webCache_getAgeOfFile( strHtmlAdress ):
    "get cache time stamp (from filename)"
    strFilename = webCache_getFilename( strHtmlAdress );
    return filetools.getAgeOfFile( strFilename );
# webCache_getAgeOfFile - end

def webCache_touch( strHtmlAdress ):
    "set cache time stamp to NOW"
    strFilename = webCache_getFilename( strHtmlAdress );
    filetools.touch( strFilename );
# webCache_touch - end

def getHtmlPage( strHtmlAdress, bWaitAnswer = True, rTimeOutForAnswerInSec = 30.0, strSaveAs = None, bTryToUseCpp = True, bUseCache = False, bUpdateCache = False, _bForceCacheUpdateInternalUseOnly = False, strUser = None, strPassword = None ):
    "return a web page, or "" on error (async or sync method, with optionnal timeout)"
    "Warning: don't put '&' in the html adress !"
    "rTimeOutForAnswerInSec: set to 0 for infinite"
    "strSaveAs: instead of returning a string, just save to a file and return True"
    "bUseCache: when set, all request will be cached, so no more internet is used, it could then be retrieved, even if internet is not present"
    "bUpdateCache: try to connect to the web, even if cache present, then update cache on success"
    "strUser: optionnal user to use for accessing file"
    "strPassword: optionnal password to use for accessing file"
    "_bForceCacheUpdateInternalUseOnly: used for recursivity only"

# this method is ok but doesn't work on adress that doesn't finished with an extension (.ext)
#  req = urllib2.Request( strHtmlAdress );
#  print req.get_full_url();
# handle = urllib2.urlopen( req );
#  res = handle.read();
#  return res;

    # seems not to work when called from python/getWebPage
    strUser = None;
    strPassword = None;

    if( bUseCache and not _bForceCacheUpdateInternalUseOnly ):
        if( webCache_getAgeOfFile( strHtmlAdress ) > 8*60*60 ): # 8 hours
            # the cache is a bit older, try refresh it!
            print( "INF: getHtmlPage('%s'): cache is old (or not cached), updating it..." % strHtmlAdress );
            bUpdateCache = True;

    if( bUpdateCache ):
        # launch a get without caching, then we will return the cached value, that has been created (or nothing if no value, or old one, if new get has failed)
        # print( "DBG: getHtmlPage: Updating cache...\n" );
        getHtmlPage( strHtmlAdress, bWaitAnswer = True, rTimeOutForAnswerInSec = rTimeOutForAnswerInSec, bTryToUseCpp = bTryToUseCpp, bUseCache = True, bUpdateCache = False, _bForceCacheUpdateInternalUseOnly = True, strUser = strUser, strPassword = strPassword );
        # print( "DBG: getHtmlPage: Updating cache - end: new value to be returned is:\n" + str( dataDebug ) );
        # touch the cache file, so that, even if web not found, we won't retry until some times
        webCache_touch( strHtmlAdress );


    if( ( bUseCache and not _bForceCacheUpdateInternalUseOnly ) and strSaveAs == None ):
        strPageContents = webCache_get( strHtmlAdress );
        if( strPageContents != False ):
            # if( len(strPageContents) > 2 or random.random() > 0.3 ): # from time to time, when cache data are small, we retest it (it permits to get updated info in case of "at one moment, there was no info) Better: use cache time !
                return strPageContents;

    # use cpp !
    if( bTryToUseCpp ):
        try:
            usage = naoqitools.myGetProxy( 'UsageTools' );
            if( usage == None ):
                print( "WRN: getHtmlPage: UsageTools not found" );
            else:
                # separate hostname and directories
                strHost, strFolder, strPageName = getHostFolderAndFile( strHtmlAdress );
        #        print( "altools.getHtmlPage: L'ADRESSE DU SITE: -%s-%s-%s-:" % (strHost, strFolder, strPageName) );
        #        strHost = strHost[len('http://'):]; # remove http: older version doesn't like it !
                if( strSaveAs != None ):
                    if( bWaitAnswer ):
                        bRet = usage.getWebFile( strHost, strFolder + strPageName, strSaveAs, rTimeOutForAnswerInSec );
                        return bRet;
                    else:
                        bRet = usage.post.getWebFile( strHost, strFolder + strPageName, strSaveAs, rTimeOutForAnswerInSec );
                        return "";
                strPageContents = usage.getWebPage( strHost, strFolder + strPageName, rTimeOutForAnswerInSec );
                if( strPageContents != "error" or ( rTimeOutForAnswerInSec > 0. and rTimeOutForAnswerInSec < 10.0 ) ): # if we put a short timeout, that's possible to have an empty response!
                    if( bUseCache and strPageContents != "" ):
                        webCache_write( strHtmlAdress, strPageContents );
                    return strPageContents; # else, we will use the normal method
                else:
                    print( "WRN: getHtmlPage: CPP method error: return empty, trying other method" );
        except BaseException, err:
            print( "WRN: getHtmlPage: CPP method error: %s" % str( err ) );
            pass # use oldies version

    print( "WRN: nettools.getHtmlPage: using old one using fork and shell!" );

    # not very efficient: should store it in var/volatile (but less os independent)
    debug.debug( "INF: ***** getHtmlPage( %s, bWaitAnswer = %d, rTimeOutForAnswerInSec = %d, bUseCache = %d )" % ( strHtmlAdress, bWaitAnswer, rTimeOutForAnswerInSec, bUseCache ) );
    strRandomFilename = pathtools.getVolatilePath() + "getHtmlPage_%s.html" % filetools.getFilenameFromTime();
    # sous windows wget peut geler, donc on va l'appeller avec un timeout (qui ne fonctionne pas, c'est drole...)
#    threadWGet = system.mySystemCall( "wget %s --output-document=%s --tries=16 --timeout=60 --cache=off -q" % ( strHtmlAdress, strRandomFilename ), False, True ); # commenter cette ligne pour avoir toujours le meme fichier
    # en fait plein d'options n'existe pas sur Nao, donc on ne laisse que celle ci:
    if( strSaveAs != None ):
        strRandomFilename = strSaveAs;
    strCommandToLaunch = "wget \"%s\" --output-document=%s" % ( strHtmlAdress, strRandomFilename ); # -q
    if( strUser != None ):
        strCommandToLaunch += " --user=%s" % strUser;    # or --http-user
    if( strPassword != None ):
        strCommandToLaunch += " --password=%s" % strPassword; # or --http-password

    threadWGet = system.mySystemCall( strCommandToLaunch, bWaitEnd = False, bStoppable = True ); # commenter cette ligne pour avoir toujours le meme fichier

    if( not bWaitAnswer ):
        debug.debug( "getHtmlPage( %s, %d ) - direct return" % ( strHtmlAdress, bWaitAnswer ) );
        return "";

    timeBegin = time.time();
    timeElapsed = 0.;

    time.sleep( 0.5 ); # time for the process to be created ! # 2012-04-27: try with 0.5 instead of 1.0 to gain some reactiveness...

    if( isinstance( threadWGet, int ) ):
        # on est ici dans un post d'un systemCall threaded sur un UsageRemoteTools
        try:
            usage = naoqitools.myGetProxy( 'UsageRemoteTools', True );
            usage.wait( threadWGet, rTimeOutForAnswerInSec*1000 ); # On a trés souvent cette erreur la: "'Function wait exists but parameters are wrong'" la tache est peut etre deja fini ?
        except BaseException, err:
            print( "WRN: getHtmlPage: wait for end failed, err: " + str( err ) );
        debug.debug( "getHtmlPage: at the end: thread is finished (naoqi id: %d)" % threadWGet );
    else:
        # system call classique
        while( 1 ):
            debug.debug( "getHtmlPage: thread is finished: %d" % threadWGet.isFinished()  );
            if( threadWGet.isFinished() ):
                debug.debug( "getHtmlPage: isFinished !!!" );
                break;

            timeElapsed = time.time() - timeBegin;
            if( timeElapsed > rTimeOutForAnswerInSec ):
                debug.debug( "getHtmlPage: %f > %f => timeout" % (timeElapsed, rTimeOutForAnswerInSec) );
                threadWGet.stop();
                break;
            time.sleep( 0.2 );
        # while - end
        debug.debug( "getHtmlPage: at the end: thread is finished: %d" % threadWGet.isFinished()  );

#  bOnWindows = ( os.name != 'posix' );
#  if( bOnWindows ):
#      time.sleep( 8.0 ); # temps de l'appel car sur certaines plateformes (windows) le os.waitpid semble ne pas bien fonctionner ou alors c'est le wget...

    if( strSaveAs == None ):
        strBuf = "";

        file = False;
        try:
            file = open( strRandomFilename, 'r' );
            strBuf = file.read();
        except:
            print( "getHtmlPage: WRN: file '%s' is empty or not finished to be aquire... (timeElapsed: %f)" % ( strRandomFilename, timeElapsed ) );
        finally:
            if( file ):
                file.close();

        try:
            if( file ):
                os.unlink( strRandomFilename );
        except:
            print( "getHtmlPage: WRN: unlink of file '%s' failed..." % strRandomFilename );

    #    debug.debug( "getHtmlPage( %s, %d ) - return '%s'" % ( strHtmlAdress, bWaitAnswer, strBuf ) );
        debug.debug( "getHtmlPage( %s, %d ) - return a page of length: '%d'" % ( strHtmlAdress, bWaitAnswer, len( strBuf ) ) );
    else:
        debug.debug( "getHtmlPage( %s, %d ) - return, data saved to '%s'" % ( strHtmlAdress, bWaitAnswer, strSaveAs ) );
        strBuf = True; # a bit burk
    if( bUseCache and strBuf != "" ):
        # print( "INF: getHtmlPage: updating cache for '%s' with:\n%s" % (strHtmlAdress, strBuf) );
        webCache_write( strHtmlAdress, strBuf );
    return strBuf;
# getHtmlPage - end

def ping( strAddr, bPleaseBeSure = False ):
    "ping an adress 'google.com' or an ip '127.0.0.1'"
    "bPleaseBeSure: ask for a surest test"
    "return true if ok"
    # should use the ping from UsageTools.pingTest, but it's not working by now
    nTimeout = 1;
    if( bPleaseBeSure ):
        nTimeout = 4;
    strCommand = "ping -w %d " % nTimeout;
    if( system.isOnWin32() ):
        strCommand = "ping -n 1 -w %d "  % nTimeout;
    strRet = system.executeAndGrabOutput( strCommand + strAddr, bQuiet = True );
    # strRet = system.executeAndGrabOutput( "sleep 3", bLimitToFirstLine = False ); # executeAndGrabOutput n'attend plus la fin sous windows ?!? Arghhhh
#    print( "DBG: ping: strRet:" + strRet );
    if( ( " 0% packet loss" in strRet ) or ( "perte 0%" in strRet ) ):
        return True;
    return False;
# ping - end

def isWebConnected():
    "return true if connected to the web"
    return ping( "209.85.148.99", bPleaseBeSure = True ); # hard coding of google address, so it doesn't need to use DNS
# isWebConnected - end

def isInternetPresent():
    """
    Alternate method
    """
    import urllib2
    try:
        response=urllib2.urlopen('http://85.239.127.112',timeout=1)
        return True
    except urllib2.URLError as err: pass
    return False    
# isInternet - end

def _retrieveGoogleImage(strSearchString, strFileFormat='.jpg', strImgType=None, nNumberOfImage=8, strImgsz='small|medium|large', strSafeMode='moderate', strLanguage='fr'):
    """
    use google image api to find image related to a string

    strFileFormat: '.jpg', or .png, or .bmp, or .gif

    strImgType could be :

    imgtype=face restricts results to images of faces.
    imgtype=photo restricts results to photographic images.
    imgtype=clipart restricts results to clipart images.
    imgtype=lineart restricts results to line drawing images.
    or None

    strImgsz : small|medium|large|xlarge , xxlarge , icon, huge,  you can use | for or
    strSafeMode :   safe=active enables the highest level of safe search filtering.
                safe=moderate enables moderate safe search filtering (default).
                safe=off disables safe search filtering.


    return : list of image url
    """
    import urllib2
    import simplejson
    print('searching for %s on google image' % strSearchString)

    if nNumberOfImage > 8:
        logger.error("For now only 8 images max are handled..")
        nNumberOfImage = 8

    url = ('https://ajax.googleapis.com/ajax/services/search/images?' +
        'v=1.0&q=%s&as_filetype=%s&rsz=%s&imgsz=%s&safe=%s&hl=%s' % (urllib2.quote(strSearchString), strFileFormat, str(nNumberOfImage), strImgsz, strSafeMode, strLanguage))
    if strImgType != None:
        url = ''.join([url, "&imgtype=%s" % strImgType])

    bUseCache = False
    if bUseCache:
        response = getHtmlPage(url, bUseCache=True)
        results = simplejson.loads(response)
    else:
        request = urllib2.Request(url, None)
        response = urllib2.urlopen(request)
        results = simplejson.load(response)


    # Process the JSON string.
    #results = simplejson.load(response)
    # now have some fun with the results...
    #aImagesUrl = [result['url'] for result in results['responseData']['results']]
    aImagesUnescapedUrl = [result['unescapedUrl'] for result in results['responseData']['results']]
    return aImagesUnescapedUrl

def getGoogleImagesCV2Format(strSearchString, strImgType=None, nNumberOfImage=8, strImgsz='small|medium|large'):
    """
    use google image api to find image related to a string

    file format is limited to jpg for opencv support
    return : list of cv2 image (numpy array)

    "example call:

    nettools.getGoogleImagesCV2Format('Steve Jobs', '/tmp/', strImgType='face')

    """
    import urllib2
    import cv2
    import numpy as np
    aImagesUnescapedUrl = _retrieveGoogleImage(strSearchString, strFileFormat='.jpg', strImgType=strImgType, nNumberOfImage=nNumberOfImage, strImgsz=strImgsz)
    aListOfCv2Image = []
    for nNum, strUrl in enumerate(aImagesUnescapedUrl):
        try:
            req = urllib2.urlopen(strUrl)
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            img = cv2.imdecode(arr,-1) # 'load it as it is'
            aListOfCv2Image.append(img)
        except:
            logger.error("Execpiton occurs during conversion of image %s %s" % (nNum, strUrl))
    return aListOfCv2Image

def downloadGoogleImages(strSearchString, strDestPath='/tmp/', strFileFormat='.jpg', strImgType=None, nNumberOfImage=8, strImgsz='small|medium|large'):
    """
    Args:
        strSearchString: string to search for on google image
        strDestPath : path to save images
    return:
        List of imagesSaved on disk (full path)

    nettools.downloadGoogleImages('train', '/tmp/', strImgType='photo')
    nettools.downloadGoogleImages('robot', '/tmp/', strImgType='photo')
    nettools.downloadGoogleImages('pepper', '/tmp/', strImgType='photo')
    """
    import filetools
    import urllib
    import os
    aImagesUnescapedUrl = _retrieveGoogleImage(strSearchString,strFileFormat=strFileFormat, strImgType=strImgType, nNumberOfImage=nNumberOfImage, strImgsz=strImgsz)
    aSavedImage = []
    for strUrl in aImagesUnescapedUrl:
        strFilename = os.path.join(strDestPath, filetools.getFilenameFromTime() + strFileFormat)
        try:
            bUseCache = False
            if bUseCache:
                aPage = getHtmlPage(strUrl, bUseCache=True)
                with open(strFilename, 'w') as f:
                    print('writing image')
                    f.write(aPage)
            else:
                urllib.urlretrieve(strUrl, strFilename)
        except:
            logger.error("Exception occurs during urlretrieve of image %s" % (strUrl))

        aSavedImage.append(strFilename)
    print aSavedImage
    return aSavedImage
    
    
def connectToWifi( strSSID, strPasswd = None ):
    """
    Connect to a (new) wifi, or reconnect to an already known
    Using ALConnectionManager
    Return True if ok
    """
    
# connectToWifi - end    

def autoTest():
    assert( ping( "127.0.0.1" ) );
    assert( not ping( "124.0.0.1" ) );
    getHtmlPage( "http://www.google.fr/index.html" );
    strMedicPage = "http://candiweb.factorycity.com/ObjectKnowledge/search.py?name=Doliprane";
    retMedic1 = getHtmlPage( strMedicPage );
    retMedic2 = getHtmlPage( strMedicPage, bUseCache = True );
    retMedic3 = getHtmlPage( strMedicPage, bUseCache = True );
    print( "medic1: '%s'" % retMedic1 );
    print( "medic2: '%s'" % retMedic2 );
    print( "medic3: '%s'" % retMedic3 );
    assert( retMedic1 == retMedic2 );
    assert( retMedic1 == retMedic3 );
# autoTest  - end


# test zone
# autoTest();


#downloadGoogleImages('pape', '/tmp/')
#getGoogleImages('Coeur')
#getGoogleImages('laurent george')

#downloadGoogleImages('rire', '/tmp/', strImgType='photo')
#downloadGoogleImages('macdos', '/tmp/', strImgType='photo')
#downloadGoogleImages('nous', '/tmp/', strImgType='photo')

#aImagesUnescapedUrl = _retrieveGoogleImage('pepper',strFileFormat='.jpg')
#print aImagesUnescapedUrl
