# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# File tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

# this module should be called file, but risk of masking with the class file.

"""File Tools"""
print( "importing abcdk.filetools" );

import os
import time
import datetime
#~ import mutex
import threading
import shutil
import time

import debug
import pathtools


def isFileExists( strPathFilename ):
#  strPathFilename = strPathFilename.replace( "/", getDirectorySeparator() );
#  strPathFilename = strPathFilename.replace( "\\", getDirectorySeparator() );
#  strPathFilename = strPathFilename.replace( getDirectorySeparator() + getDirectorySeparator(), getDirectorySeparator() );
#  print( "isFileExists( '%s' ) =>" % strPathFilename );

  #~ try:
    #~ file = open( strPathFilename, 'r' );
    #~ if( file ):
      #~ file.close();
      #~ return True;
  #~ except (IOError, os.error), err:
#~ #    print( "err: " + str( err ) );
    #~ pass
  #~ return False;
  return os.path.exists( strPathFilename );
# isFileExists - end


def copyFile( strPathFilenameSrc, strPathFilenameDst, bVerbose = False ):
    "copy one file to another one"
    "return true if ok"
    if( bVerbose ):
        print( "INF: copyFile: %s => %s" % ( strPathFilenameSrc, strPathFilenameDst ) );
    bError = False;
    try:
        file = open( strPathFilenameSrc, "rb" );
    except BaseException as err:
        print( "ERR: filetools.copyFile failed at source opening: %s" % err );
        return False;
        
    try:
        strBuf = file.read();
    except BaseException as err:
        print( "ERR: filetools.copyFile failed at dest opening: %s" % err );
        bError = True;
    file.close();        
    if( bError ):
        return False;

    try:
        file = open( strPathFilenameDst, "wb" );
        file.write( strBuf );
    except (IOError, os.error) as err:
        print( "ERR: filetools.copyFile failed: %s" % err );
        bError = True;
    file.close();
    return not bError;
# copyFile - end

def moveFile( strPathFilenameSrc, strPathFilenameDst, bVerbose = True ):
    "move one file to another one"
    "return true if ok"
    if( bVerbose ):
        print( "INF: moveFile: %s => %s" % ( strPathFilenameSrc, strPathFilenameDst ) );
    bRet = copyFile( strPathFilenameSrc, strPathFilenameDst, bVerbose  );
    if( bRet ):
        unlink( strPathFilenameSrc );
    else:
        print( "ERR: filetools.moveFile, %s => %s: copy failure, leaving original." % ( strPathFilenameSrc, strPathFilenameDst ) );
    return bRet;
# moveFile - end

def compareFile( strFile1, strFile2, bCountDifference = False, bVerbose = False ):
    """
    Compare two files.
    Return 0 if same, or > 0 if differences found. Return -1 on error (file not found...)
    - bCountDifference: when set, it will compare file and return precise number of different bytes, even if the size are different. 
       (a different size means each missing bytes are different)
    """
    try:
        nFileSize1 = os.path.getsize( strFile1 );
        nFileSize2 = os.path.getsize( strFile2 );
    except BaseException as err:
        print( "DBG: abcdk.filetools.compareFile: %s" % str( err ) );
        return -1;
    if( not bCountDifference and nFileSize1 != nFileSize2 ):
        if( bVerbose ):
            print( "INF: filetools.compareFile: file '%s' and '%s' has DIFFERENT SIZE: %d and %d" % ( strFile1, strFile2, nFileSize1, nFileSize2 ) );
        return abs(nFileSize1-nFileSize2);
    nFileSizeMin = min( nFileSize1, nFileSize2 );        
    file1 = open( strFile1, "rb" );
    file2 = open( strFile2, "rb" );
    buf1 = file1.read();
    buf2 = file2.read();
    file1.close();
    file2.close();
    nDiff = 0;
    n = 0;
    while( n != nFileSizeMin ):
        if( buf1[n] != buf2[n] ):
            if( bVerbose ):
                nMaxDiffToPrint = 30;
                if( nDiff < nMaxDiffToPrint ):
                    print( "INF: filetools.compareFile: file '%s' and '%s': DIFFERENCE at offset %d: data: %d (%x) and %d (%x)" % ( strFile1, strFile2, n, ord(buf1[n]), ord(buf1[n]), ord(buf2[n]), ord(buf2[n]) ) );
                elif( nDiff == nMaxDiffToPrint ):
                    print( "INF: filetools.compareFile: file '%s' and '%s': others difference found (stopping printing)" % ( strFile1, strFile2 ) );
            nDiff += 1;
        n += 1;
    nDiff = nDiff + abs(nFileSize1-nFileSize2);
    if( bVerbose ):
        print( "INF: filetools.compareFile: file '%s' and '%s': TOTAL DIFFERENCE: %d" % ( strFile1, strFile2, nDiff ) );
    return nDiff;
# compareFile - end

def copyDirectory( strPathSrc, strPathDst, strExcludeSkul = None ):
    "copy an entire directory to another place"
    "strExcludeSkul: if a file or directory contain this string, it will be excluded"
    "return true if ok"
    print( "INF: copyDirectory: %s => %s" % ( strPathSrc, strPathDst ) );
    bOk = True;
    bAtLeastOneFile = False;
    try:
        os.makedirs( strPathDst );
    except BaseException as err:
        print( "WRN: filetools.copyDirectory: while creating destination: " + str( err ) );
    if( not os.path.exists( strPathSrc ) ):
        return False;
    for elem in os.listdir( strPathSrc ):
        bAtLeastOneFile = True;
        sFullPath = os.path.join( strPathSrc, elem );
        if( strExcludeSkul != None and strExcludeSkul in elem ):
            continue;
        if os.path.isdir(sFullPath) and not os.path.islink(sFullPath):
            bOk &= copyDirectory( sFullPath, strPathDst + '/' + elem, strExcludeSkul );
        else:
            bOk &= copyFile( sFullPath, strPathDst + '/' + elem );
    return bOk and bAtLeastOneFile;
# copyDirectory - end


def getFileContents( szFilename, bQuiet = False ):
    "read a file and return it's contents, or '' if not found, empty, ..."
    aBuf = "";
    try:
        file = open( szFilename );
    except BaseException as err:
        if( not bQuiet ):
            debug.debug( "ERR: filetools.getFileContents open failure: %s" % err );
        return "";
        
    try:
        aBuf = file.read();
    except BaseException as err:
        if( not bQuiet ):
            debug.debug( "ERR: filetools.getFileContents read failure: %s" % err );
        file.close();
        return "";
        
    try:
        file.close();
    except BaseException as err:
        if( not bQuiet ):
            debug.debug( "ERR: filetools.getFileContents close failure: %s" % err );
        pass
    return aBuf;
# getFileContents - end


def getLine( strText, nNumLine ):
    "extract a specific line in a multiline text, return '' if line not found, text empty or ..."
    "parameter nNumLine should be in [0,nbrline-1]"
    # trim EOL and ...
    if( len( strText ) < 1 or nNumLine < 0 ):
        return "";

    aByLine = strText.split( '\n' );

    if( nNumLine >= len( aByLine ) ):
        return "";
    return aByLine[nNumLine];
 # getLine - end

def getFileFirstLine( szFilename, bQuiet = False ):
  "read a file and return it's first line, or '' if not found, empty, ..."
  strBufferRead = getFileContents( szFilename, bQuiet = bQuiet );
  return getLine( strBufferRead, 0 );
# getFileFirstLine - end


def getFilenameFromTime(timestamp=None):
  """
  get a string usable as a filename relative to the current datetime stamp.
  eg: "2012_12_18-11h44m49s049ms"
  
  timestamp : time.time()
  """
  # old method:
  #~ strTimeStamp = str( datetime.datetime.now() );
  #~ strTimeStamp = strTimeStamp.replace( " ", "_" );
  #~ strTimeStamp = strTimeStamp.replace( ".", "_" );
  #~ strTimeStamp = strTimeStamp.replace( ":", "m" );
  if timestamp is None:
      datetimeObject = datetime.datetime.now()
  elif isinstance(timestamp, datetime.datetime):
      datetimeObject = timestamp
  else:
      datetimeObject = datetime.datetime.fromtimestamp(timestamp)
  strTimeStamp = datetimeObject.strftime( "%Y_%m_%d-%Hh%Mm%Ss%fms" );
  strTimeStamp = strTimeStamp.replace( "000ms", "ms" ); # because there's no flags for milliseconds
  return strTimeStamp;
# getFilenameFromTime - end
#~ print( getFilenameFromTime() );

def getFileTime( strFilename ):
    """
    get the date/time of the last modify date of a file.
    return a number: seconds since epoch, or 0 if file not found
    """
    try:
        nTime = os.path.getmtime( strFilename );
    except os.error as err:
        nTime = 0;
#    print( "getFileTime( '%s' ): %d" % ( strFilename, nTime ) );
    return nTime;
# getFileTime - end

def getFileTimePrintable( strFilename ):
    """
    get the date/time of the last modify date of a file, as a printable string.
    return "2012_12_18-11h44m49s049ms" or "" if file not found
    """
    try:
        nTime = os.path.getmtime( strFilename );
    except os.error as err:
        return "";
    #~ print( "getFileTimePrintable( '%s' ): %d" % ( strFilename, nTime ) );
    strTimeStamp = datetime.datetime.fromtimestamp(nTime).strftime( "%Y_%m_%d-%Hh%Mm%Ss%fms" );
    strTimeStamp = strTimeStamp.replace( "000ms", "ms" ); # because there's no flags for milliseconds    
    #~ print( "getFileTimePrintable( '%s' ): '%s'" % ( strFilename, strTimeStamp ) );
    return strTimeStamp;
# getFileTimePrintable - end
#~ getFileTimePrintable( "C:/public/photos_apn/IMG_0604.JPG" );


def getAgeOfFile( strFilename ):
    "return the number of seconds between timestamp of file and now"
    "or a long long time if the file doesn't exists"
    try:
        nTime = time.time() - getFileTime( strFilename );
        return nTime;
    except BaseException as err:
        print( "DBG: filetools.getAgeOfFile: err: %s" % str( err ) );
        return time.time() - 10000000; 
# getAgeOfFile - end

def touch( strFilename ):
    """
    Set the time stamp of a file to now.
    return True if ok, False if file doesn't exists...
    """
    try:    
        os.utime( strFilename, None );
        return True;
    except BaseException as err:
        print( "DBG: filetools.touch: err: %s" % str( err ) );
    return False;
# touch - end



def makedirsQuiet( strPath, bPrintError = False ):
    try:
        os.makedirs( strPath );
    except BaseException as err:
        if( bPrintError ):
            print( "WRN: filetools.makedirsQuiet: err: %s" + str( err ) );
        pass # quiet!
# makedirsQuiet - end


def removeDirsQuiet( strPath, bPrintError = False ):
    try:
        shutil.rmtree( strPath );
    except BaseException as err:
        if( bPrintError ):
            print( "WRN: filetools.removeDirsQuiet: err: %s" + str( err ) );
        pass # quiet!
# removeDirsQuiet - end

def addFolderToZip( zipFile, strFolderPath, bStoreFullPath = True, strFileTemplateToMatch = "", strSpecificDstPath = "", strFileTemplateToIgnore = "", astrFolderToIgnore = [], _strRootPath = None ):
    """
    add an entire path to a ZipFile object previously open
    - bStoreFullPath: disable it to have all file stored in the root of your archive
    - strSpecificDstPath: when bStoreFullPath, permits to change the location in the zip file (Seems to not work so good)
    - strFileTemplateToMatch: add only file that contains that part of word, eg '.png'
    - strFileTemplateToIgnore: don't add only file that contains that part of word, eg '.png'
    - astrFolderToIgnore: list of path to ignore (use / for folder separator)
    - _strRootPath: (internal use) 1) permits to know when call from outside (=None), 2) store the absolute path of the archive root directory
    return the number of file added
    """
    assert( isinstance( bStoreFullPath, bool ) ); # when we add the option bStoreFullPath, we need to check that no one use _strRootPath from outside this method
    print( "INF: filetools.addFolderToZip( '%s', '%s' )" % ( strFolderPath, _strRootPath ) );
    nNbrFile = 0;
    for elem in os.listdir( strFolderPath ):
        sFullPath = os.path.join( strFolderPath, elem );
        sFullPath = sFullPath.replace( '\\', '/' ); # use allways '/' for file matching/exclude
        if os.path.isdir(sFullPath) and not os.path.islink(sFullPath) and not sFullPath in astrFolderToIgnore:
            if( _strRootPath == None ):
                strRootPathChild = strFolderPath;
            else:
                strRootPathChild = _strRootPath;
            nNbrFile += addFolderToZip( zipFile, sFullPath, bStoreFullPath = bStoreFullPath, strFileTemplateToMatch = strFileTemplateToMatch, strSpecificDstPath = strSpecificDstPath, strFileTemplateToIgnore = strFileTemplateToIgnore, astrFolderToIgnore = astrFolderToIgnore, _strRootPath = strRootPathChild );
        else:
            if( strFileTemplateToMatch not in elem ):
                #~ print( "INF: skipping file '%s' (not matching)" % elem );
                continue;
            if( strFileTemplateToIgnore != "" and strFileTemplateToIgnore in elem ):
                #~ print( "INF: skipping file '%s' (matching to ignore)" % elem );
                continue;
            strOrigFile = sFullPath;
            #~ if( _strRootPath != None ):
                #~ strArcFile = sFullPath[len(_strRootPath):];
            #~ else:
            if( bStoreFullPath ):
                strArcFile = sFullPath;
            else:
                strLocalPath = "";
                if( _strRootPath != None ):
                    strLocalPath = strFolderPath.replace( _strRootPath, "", 1 ) + "/";
                strArcFile = strSpecificDstPath + strLocalPath + elem;
            print( "%s => %s" % ( strOrigFile, strArcFile ) );
            zipFile.write( strOrigFile, strArcFile );
            nNbrFile += 1;
    if( _strRootPath == None ):
        print( "INF: filetools.addFolderToZip: %d file(s) added to zip" % nNbrFile );
    return nNbrFile;
# addFolderToZip - end

def extractFolderFromZip( zipFile, aTableListPath ):
    "extract some folders from a zip file"
    "aTableListPath: a dictionnary with folder_in_archives => destination_on_disk"
    "eg: [ 'behaviors' ] = '/home/nao/Applications/autonomous/life2/'"
    "return number of extracted files"
    "WARNING: handle only first folder name"
    print( "filetools.extractFolderFromZip, table path:" );
    for k, v in aTableListPath.iteritems():
        print( "\t '%s' => '%s'" % ( k, v ) );
    listFile = zipFile.infolist();
    nNbrExtracted = 0;
    nCount = 0;
    for info in listFile:
        strFilename = info.filename;
        strFirstFolder = strFilename[:strFilename.find('/')];
#        print( "file: '%s' => first folder: '%s'\n" % ( strFilename, strFirstFolder ) );
        if( strFirstFolder in aTableListPath.keys() ):
            print( "%4d/%4d: '%s' exploded to '%s'" % ( nCount, len( listFile ), strFilename, aTableListPath[strFirstFolder] ) );
            try:
                zipFile.extract( strFilename, aTableListPath[strFirstFolder] );
                nNbrExtracted += 1;
            except BaseException as err:
                print( "ERR: life_data.installPackage: extract %s to %s, err: %s" % ( strFilename, aTableListPath[strFirstFolder], str( err ) ) );
                # on continue la ou pas ?            
        nCount += 1;
    print( "INF: filetools.extractFolderFromZip: %d file(s) extracted" % nNbrExtracted );
    return nNbrExtracted;
# extractFolderFromZip - end
    

def replaceInFile( strStringToFind, strStringNew, strFilenameSrc, strFilenameDst = None ):
    "replace the string <strStringToFind> by <strStringNew> in a file <strFilenameSrc>"
    "strFilenameDst: if unspecified, the source will be changed"
    "return True if ok"
    
    debug.debug( "INF: filetools.replaceInFile: file '%s' => '%s', replacing '%s' by '%s'\n" % (strFilenameSrc, strFilenameDst, strStringToFind, strStringNew )  );
    
    strContents = getFileContents( strFilenameSrc );
    
#    print( "strContents: " + strContents );

    strContents = strContents.replace( strStringToFind, strStringNew );
    if( strFilenameDst == None ):
        strFilenameDst = strFilenameSrc;
        
    try:
        file = open( strFilenameDst, "w" );
    except BaseException as err:
        debug.debug( "ERR: filetools.replaceInFile open failure: %s" % err );        
        return False;
        
    try:
        file.write( strContents );
    except BaseException as err:
        debug.debug( "ERR: filetools.replaceInFile write failure: %s" % err );
        file.close();
        return False;
        
    try:
        file.close();
    except BaseException as err:
        debug.debug( "ERR: filetools.replaceInFile close failure: %s" % err );
        return False;
        
    return True;
# replaceInFile - end

# TODO: rewrite in a beautiful object
global_strAltools_LogToFile = None;
#~ global_mutex_LogToFile = mutex.mutex();
global_mutex_LogToFile = threading.Lock()
global_timeLogToFile_lastLog = time.time();
def logToFile( strMessage, strSpecificFileName = "" ):
    "add a message to the current debug log file"
    global global_strAltools_LogToFile;
    global global_mutex_LogToFile;
    global global_timeLogToFile_lastLog;
    timeNow = time.time();
    rDurationSec = timeNow - global_timeLogToFile_lastLog;
    global_timeLogToFile_lastLog = timeNow;
    while( global_mutex_LogToFile.testandset() == False ):
        time.sleep( 0.02 );
    if( global_strAltools_LogToFile == None ):
        try:
            os.makedirs( pathtools.getCachePath() );
        except:
            pass # often the cases!
        global_strAltools_LogToFile = pathtools.getCachePath() + getFilenameFromTime() + ".log";
        print( "altools.logToFile: logging to '%s'" % global_strAltools_LogToFile );
        
    if( strSpecificFileName == '' ):
        strFileName = global_strAltools_LogToFile;
    else:
        import naoqitools # pourquoi ici on met tout le temps du naoqi meme si pas sur un robot ?
        strFileName = pathtools.getCachePath() + strSpecificFileName + '_' + naoqitools.getNaoqiStartupTimeStamp() + ".log";
#    print( "logToFile: logging to %s" % strFileName );
    try:
        file = open( strFileName, "at" );
        file.write( "%s (%5.2fs): %s\n" % ( debug.getHumanTimeStamp(), rDurationSec, strMessage ) );
    finally:
        if( file ):
            file.close();
    global_mutex_LogToFile.unlock();
# logToFile - end

# serializer for map
def dictTofile( file, aDict ):
    "transform a dict to text formated, and ouput it on an already opened file" # alex: note pour plus tard consider using the python method 'repr'
    "return true if ok"
    strOut = "dict({\n";
    for k, v in aDict.iteritems():
      strOut += "  '%s': %s,\n" % ( k, str(v) );
    strOut += "})\n";
    file.write( strOut );
    return True;
# dictTofile - end
    
def fileToDict( file ):
    "extract a dict from an already opened file"
    "return the dict or False on error"
    aDict = dict();
    bufLines = "";
    oneLine = file.readline(); # read dict(
    while( oneLine != ");" and oneLine != '' ):
#        print( "DBG: fileToDict: oneLine: '%s'" % oneLine );
        bufLines += oneLine; 
        oneLine = file.readline();
    bufLines += oneLine; 
#    print( "DBG: fileToDict: bufLines: '%s'" % bufLines );
    aDict = eval( bufLines );
    return aDict;
# fileToDict - end

def waitForFile( strPathFilename, nTimeout = 30. ):
    "wait a file is created"
    "return False on timeout"
    timeBegin = time.time();
    while( not os.path.exists( strPathFilename ) ):
        if( time.time() - timeBegin >= nTimeout ):
            return False;
        time.sleep( 0.3 );
    return True;
# waitForFile - end

def loadCsv( strFilename, strSeparator = ",", bSkipHeader = False ):
    """
    load a csv, 
    return:
        - an array (one per line) of array (one per column)
        - False, if file not found,
    - strSeparator: you can specify your own separator
    bSkipHeader: is the first line a format/comments line ?
    """
    try:
        file = open( strFilename, "rt" );
    except BaseException as err:
        print( "WRN: abcdk.filetools.loadCsv: file '%s' not found?: err: %s" % (strFilename, str(err) ) );
        return False;
    buf = file.read();
    #~ print( "buf: '%s'" % buf );
    lines = buf.split( "\n" );
    datas = [];
    nNumFirstLine = 0;
    if( bSkipHeader ):
        nNumFirstLine = 1;
    for line in lines[nNumFirstLine:]: # skip headers ?
        # a csv is separated by ',' so when a string contains a ',' it is enclosed by '"', so just spliting on ',' is not enough.
        # when user want a ", it's outputted as a ""
        items = line.split(",");        
        i = 0;
        nLen = len(line);
        nPosLastBracket = -1; # set to last position or -1 if not into a '"' area
        items = [];
        strCurrentItem = "";
        bPreviousIsFirstBracket = False; # detect pair of bracket
        bIntoBracket = False;
        while( i < nLen ):
            if( line[i] == '"' ):
                if( not bIntoBracket ):
                    if( bPreviousIsFirstBracket ):
                        strCurrentItem += '"';
                        bPreviousIsFirstBracket = False;
                    else:
                        bPreviousIsFirstBracket = True;
                    bIntoBracket = True;
                else:
                    if( bPreviousIsFirstBracket ):
                        strCurrentItem += '"';
                        bPreviousIsFirstBracket = False;
                    else:
                        bPreviousIsFirstBracket = True;
                    bIntoBracket = False;
            else:
                if( line[i] == strSeparator and not bIntoBracket ):
                    items.append( strCurrentItem );
                    strCurrentItem = "";
                else:
                    strCurrentItem += line[i];
                bPreviousIsFirstBracket = False;
            i += 1;
        items.append( strCurrentItem );
        datas.append( items );
    return datas;
# loadCsv - end        
#~ strPath = "C:/Documents and Settings/amazel/Mes documents/Downloads/";
#~ datas = loadCsv( strPath + "Knowledge_Validated - FR.csv" );
#~ print( datas );

def patchBinary( strFilenameSrc, strStringOrigin, strStringNew, nOffsetMin = 0, nOffsetMax = -1, nNbrReplaceMax = -1, strAfterThisString = None, strFilenameDst = None, nChangeAfterTheXth = -1 ):
    """
    Patch a binary file, changing strStringOrigin occurence by strStringNew
    - strFilenameSrc: name of the source file
    - strStringOrigin: string to change (it could be binary?)(TODO)
    - strStringNew: new string
    - nOffsetMin: offset from where change is possible (included)
    - nOffsetMax: offset max to change (excluded)
    - nNbrReplaceMax: nbr of replace maximum
    - strFilenameDst: if set, destination file
    - nChangeAfterTheXth: count x before changing (eg if set to 3, the fourth one will be changed)
    return the number of changes or -1 on error
    """
    if( strFilenameDst == None ):
        strFilenameDst = strFilenameSrc;
        
    # loading
    file = open( strFilenameSrc, "rb" );
    data = file.read();
    file.close();
    if( nOffsetMax != -1 ):
        data = data[:nOffsetMax];
    if( strAfterThisString != None ):
        nIdx = data.find( strAfterThisString );
        if( nIdx == -1 ):
            return -1;
        nOffsetMin = nIdx + len(strAfterThisString);
    if( nChangeAfterTheXth != -1 ):
        nCount = 0;
        while( nCount < nChangeAfterTheXth ):
            nFound = data[nOffsetMin:].find( strStringOrigin );
            if( nFound == -1 ):
                return -1;
            nOffsetMin += nFound + len(strStringOrigin); # add relatif offset to begin of research
            print( "nOffsetMin: %d" % nOffsetMin );                
            nCount += 1;
    data = data[:nOffsetMin] + data[nOffsetMin:].replace( strStringOrigin, strStringNew, nNbrReplaceMax );
    nNbrChange = 0;
    file = open( strFilenameDst, "wb" );
    file.write( data );
    file.close();
    
    print( "abcdk.filetools.patchBinary: %s => %s (%d change(s))" % (strFilenameSrc, strFilenameDst, nNbrChange) );
    
    return nNbrChange;
    
# patchBinary - end

def autoTest_patchBinary():
    #src = "c:\\tempo\\libdcm_hal.so";
    #~ src = "c:\\tempo\\libusage_1_22_3.so";
    src = "c:\\tempo\\libaudiodevice.so";
    #~ src = "c:\\tempo\\libspeechrecognition.so";
    
    dst = src.replace( ".so", "a.so" );
    bRet = patchBinary( src,  "ALModularity", "ALModularita", strFilenameDst = dst, nNbrReplaceMax = -1, nChangeAfterTheXth=-1 );
    #~ bRet = patchBinary( src,  "UsageProfiler", "UsageProfileA", strFilenameDst = dst, nNbrReplaceMax = -1, nChangeAfterTheXth=-1 );
    print( "patchBinary return: %s" % bRet );
    compareFile( src, dst, bVerbose = True );    
    
    
def find_last_file( strPath, nNbrFileToReturn = 1 ):
    """    
    find the last alphabetical file in a folder
    - nNbrFileToReturn: return more than one file [...,penultimate, ultimate]
    return a list of filename, even if only one file is asked
    """    
    listFile = sorted(os.listdir(strPath) )
    # remove folder and concat name
    listFileOut = []
    for i in range(len(listFile)):
        strFullPath = strPath + "/" + listFile[i]
        if os.path.isfile(strFullPath) and not os.path.islink(strFullPath):
            listFileOut.append( strFullPath )
    return listFileOut[-nNbrFileToReturn:]
# find_last_file - end
#~ print find_last_file( "/tmp", 4 )
#~ exit()

def isFileOpenForWrite( strFilename ):
    """
    Is this file already open by the system, for write ?
    (so it's not "finished" / full)
    """
    #~ for pid in os.listdir( '/proc/'):
        #~ if pid.isdigit() and pid != os.getpid():
            #~ try:
                #~ for fd in os.listdir('/proc/%s/fd' % pid): 
                        #~ print os.path.samefile( strFilename, '/proc/%s/fd/%s' % (pid, fd) )
            #~ except BaseException as err:
                #~ print( "DBG: isFileOpenForWrite: err: %s" % err )
    #~ return False # TODO !
    file = open( strFilename, "ab" )
    if( file ):
        file.close()
        return False
    return True
# isFileOpenForWrite - end    

def loadSrtFile( strFilename ):
    """
    load a subtitle file
    return a list of event [ev1,ev2,...]
    with ev: [startTimeMs,stopTimeMs,txt]
    
    srt file are this type (minus the tabs):
    1
    00:00:00,440 --> 00:00:01,120
    Hello guys!

    2
    00:00:02,740 --> 00:00:03,250
    """
    import stringtools
    out = []
    file = open(strFilename, "rt" )
    lines = file.read().split("\n")
    nNumLine = 0
    while nNumLine+3<len(lines):
        nNumLine += 1 # skip event number
        startTimeMs = stringtools.srtStyleToTimeMs( lines[nNumLine][0:12] )
        stopTimeMs = stringtools.srtStyleToTimeMs( lines[nNumLine][12+5:12+5+12] )
        nNumLine += 1
        txt = lines[nNumLine]
        nNumLine += 1
        nNumLine += 1
        out.append( [startTimeMs,stopTimeMs,txt] )
    return out
        
        

def autoTest():
    import config
    config.bDebugMode = True;
    print( "getAgeOfFile: %s"  % str( getAgeOfFile( "filetools.py" ) ) );
    #print( "replace in File:" + str( replaceInFile( "abcdk.", "toto.", "test.txt", "test2.txt" ) ) );
    logToFile( "coucou", "autotest" );
    
    #~ autoTest_patchBinary();


if __name__=="__main__":
    autoTest();

print( "importing abcdk.filetools - end" );
