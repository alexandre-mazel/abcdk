# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Debug tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Debug tools"""
print( "importing abcdk.debug" );

import sys
import mutex
import time
import datetime

import config


global_debug_dictAlreadyOutputted = dict();
def debug( args, bIgnoreDuplicateMessage = False ):
  "output a debug message to the user"
  "bIgnoreDuplicateMessage: when set to true, won't output message if the same has been outputted"
  if( config.bDebugMode ):
    if( bIgnoreDuplicateMessage ):
        global global_debug_dictAlreadyOutputted;
        if( str( args ) in global_debug_dictAlreadyOutputted.keys() ):
            return;
        global_debug_dictAlreadyOutputted[str(args)] = True; # add it!
    print args;
# debug - end

def setDebugMode( bNewVal ):
  print( "altools.setDebugMode: changed from %s to %s" % ( config.bDebugMode, bNewVal ) );
  config.bDebugMode = bNewVal;
# setDebugMode - end

def dump( obj, bShowPrivate = True ):
  "dump the contents of an object into a string"
  s = "";
  for attrName in dir( obj ):
    if( not bShowPrivate and attrName[0] == '_' ):
      continue;
    s += "%s: '%s'\n" % ( attrName, str( getattr( obj, attrName ) ) );
  return s;
# dump - end

def dumpHexaArray( anArray, nNbrByte = 1, bSigned = False ):
    """
    Dump an array
    """
    strTemp = "";
    for val in anArray:
        if( nNbrByte > 1 ):
            #for i in range( nNbrByte-1, -1, -1 ):
            for i in range( nNbrByte ):
                val8 = ( val >> (i*8) ) & 0xFF;
                strTemp += chr( val8 );
        else:
            strTemp += chr( val );
    return dumpHexa( strTemp );
# dumpHexaArray - end    

def dumpHexa( anArray ):
    """
    dump a string variable, even if containing binary
    return a string formated as an hexa editor panel with the hexa on left and text on right
    """
    # some cheap equivalent is: print repr(data)
    if( anArray == None ):
        return "WRN: debug.dumpHexa: Value is None!";
    #~ if( isinstance( anArray, np.ndarray ) ): # but requires to use np, pfff
        #~ anArray=anArray.tolist();
    strTxt = "dumpHexa data len: %d\n" % len( anArray );
    i = 0;
    strAsciiLine = "";
    strTxt += "%03d: " % i;
    while( i < len( anArray ) ):        
        strTxt += "%02x " % ord( anArray[i] );
        if( ord( anArray[i] ) >= 32 and ord( anArray[i] ) <= 127 ):
            strAsciiLine += "%s" % anArray[i];
        else:
            strAsciiLine += "_";
        i += 1;
        if( i % 8 == 0 ):
            strTxt += "  ";
        if( i % 16 == 0 ):
            strTxt += "  " + strAsciiLine + "\n";
            strTxt += "%03d: " % i;
            strAsciiLine = "";
    # while - end
    #~ print (i%16)
    if( (i%16) < 8):
        strTxt += "__ "*(8-(i%16)); # end of line
        strTxt += "  ";
        i = 8;
    strTxt += "__ "*(16-((i)%16)); # end of line
    if( i != 15 ):
        strTxt=strTxt[:-1]; # eat the last space!
    return strTxt + "     " + strAsciiLine + "\n";
# dumpHexa - end
#print( dumpHexa( "\t3213 Alexandre Mazel, happy happy man!\nYo!" ) );
#~ print( dumpHexa( "Alexandre"*1 ) );

  
def getFileAndLinePosition( nCallStackUp = 0 ):
    "this method return the position of caller in a string (idem __FILE__ __LINE__)"
    "purpose: debug, trace..."
    "nCallStackUp: you can ask for your caller, by adding extra higher level in the call stack"
    "0: this method"
    "1: the method that calls this method"
    "2: ..."
    co = sys._getframe(nCallStackUp+1).f_code; # return one more, call we are in a method !
    return "%s (%s @ %3d)" % (co.co_name, co.co_filename, co.co_firstlineno);
# getFileAndLinePosition - end

#~ print getFileAndLinePosition();

class TimeMethod:
    "measure the time taken by a method"
    "Use: define an object TimeMethod in your method, and that's all!"
    def __init__(self, strOptionnalLibelle = "" ):
        "Create the object"
        self.reset( strOptionnalLibelle );
    # __init__ - end
    
    def reset( self, strOptionnalLibelle = "" ):
        "reset the object"
        self.strCaller = getFileAndLinePosition( 2 ); # callstack: reset, __init__, caller
        if( strOptionnalLibelle != "" ):
            strOptionnalLibelle = "( " + strOptionnalLibelle + " )";
        self.strOptionnalLibelle = strOptionnalLibelle;
        self.timeBegin = time.time();            
        self.intermediate = []; # optionnal pair of [time, message]
        self.bStopped = False;
    # reset - end
    
    def setIntermediate( self, strOptionnalMessageNamingFollowingPart = "" ):
        "store intermediate time and continue, the optionnal name is the name of the following part"
        if( strOptionnalMessageNamingFollowingPart != "" ):
            strOptionnalMessageNamingFollowingPart = "( " + strOptionnalMessageNamingFollowingPart + " )";
        totalTime = time.time() - self.timeBegin;
        self.intermediate.append( [ totalTime, strOptionnalMessageNamingFollowingPart ] );
        timePrev = 0;
        if( len( self.intermediate ) > 1 ):
            timePrev = self.intermediate[-2][0];
        print( "timer: %40s: intermediate time: %6.3f %s %s\n" % ( self.strCaller, totalTime-timePrev, self.strOptionnalLibelle, strOptionnalMessageNamingFollowingPart ) );
    # setIntermediate - end
    
    def getCurrentTotalTime( self ):
        return time.time() - self.timeBegin;
    # getCurrentTotalTime - end
        
    def stopAndPrint( self ):
        "stop the timer, print info, and return a string containing a printable string"
        strOut = "";
        if( self.bStopped ):
            return strOut;
        self.bStopped = True;
        totalTime = time.time() - self.timeBegin;
        if( len( self.intermediate ) < 1 ):
            strOut += "timer: %40s: executing time: %6.3f %s" % ( self.strCaller, totalTime, self.strOptionnalLibelle );
        else:
            strOut += "timer: %40s: total time: %6.3f %s\n" % ( self.strCaller, totalTime, self.strOptionnalLibelle );
            nPrev = 0.;
            for someTime in self.intermediate:
                strOut += " %57s + %6.3f %s\n" % ( "", someTime[0] - nPrev, someTime[1] );
                nPrev = someTime[0];
            strOut += " %57s + %6.3f %s" % ( "", totalTime - nPrev, "( til the end )" );
        print( strOut );
        return strOut;
    # stopAndPrint - end
    
    def __del__( self ):
        self.stopAndPrint();
    # __del__ - end
    
# class TimeMethod - end


def logToChoregraphe( strText ):
    "print logs in the choregraphe debug print (like box.log)"
    import naoqitools
    debug( "logToChoregraphe: '%s'" % strText );
    try:
        chor = naoqitools.myGetProxy( "ALChoregraphe" );
        chor.onPythonPrint( str( strText ) );
    except:
        pass
# logToChoregraphe - end

global_getNaoqiStartupTimeStamp = str( datetime.datetime.now() );
global_getNaoqiStartupTimeStamp = global_getNaoqiStartupTimeStamp[0:len(global_getNaoqiStartupTimeStamp)-3]; # enleve les micro secondes!
global_getNaoqiStartupTimeStamp = global_getNaoqiStartupTimeStamp.replace( " ", "_" );
global_getNaoqiStartupTimeStamp = global_getNaoqiStartupTimeStamp.replace( ":", "m" );
  
def getNaoqiStartupTimeStamp():
    "return the time stamp of naoqi start (actually last altools loading) - human readable, printable, usable as a filename"
    global global_getNaoqiStartupTimeStamp;
    return global_getNaoqiStartupTimeStamp;
# getNaoqiStartupTimeStamp - end

def getHumanTimeStamp():
  "get a printable timestamp than a user (even french) could understand"
  strNow = str( datetime.datetime.now() );
  strTimeStamp = strNow[0:len(strNow)-3]; # enleve les micro secondes!
  return strTimeStamp;
# getHumanTimeStamp - end



global_strAltools_LogToFile = None;
global_mutex_LogToFile = mutex.mutex();
global_timeLogToFile_lastLog = time.time();
def logToFile( strMessage, strSpecificFileName = "" ):
    "add a message to the current debug log file"
    import filetools
    import pathtools
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
            pass
        global_strAltools_LogToFile = pathtools.getCachePath() + filetools.getFilenameFromTime() + ".log";
        print( "altools.logToFile: logging to '%s'" % global_strAltools_LogToFile );
        
    if( strSpecificFileName == '' ):
        strFileName = global_strAltools_LogToFile;
    else:
        strFileName = pathtools.getCachePath() + strSpecificFileName + '_' + getNaoqiStartupTimeStamp() + ".log";
#    print( "logToFile: logging to %s" % strFileName );
    try:
        file = open( strFileName, "at" );
        file.write( "%s (%5.2fs): %s\n" % ( getHumanTimeStamp(), rDurationSec, strMessage ) );
    finally:
        if( file ):
            file.close();
    global_mutex_LogToFile.unlock();
# logToFile - end

#logToFile( "toto" );


#~ timer = TimeMethod( "coucou" );
#~ time.sleep( 1 );
#~ timer.setIntermediate( "compute" );
#~ time.sleep( 4 );
#~ timer.setIntermediate( "draw" );
#~ time.sleep( 3 );
#~ timer.stopAndPrint();

def getFileAndLinePosition( nCallStackUp = 0 ):
    "this method return the position of caller in a string (idem __FILE__ __LINE__)"
    "purpose: debug, trace..."
    "nCallStackUp: you can ask for your caller, by adding extra higher level in the call stack"
    "0: this method"
    "1: the method that calls this method"
    "2: ..."
    co = sys._getframe(nCallStackUp+1).f_code; # return one more, call we are in a method !
    return "%s (%s @ %3d)" % (co.co_name, co.co_filename, co.co_firstlineno);
# getFileAndLinePosition - end

#~ print getFileAndLinePosition();

def raiseCameraFailure():
    return bipError();
# raiseCameraFailure - end

def bipError():
    import sound
    sound.playSound( "bip_error.wav" );
# bipError - end
    



def autoTest():
    import test
    if( test.isAutoTest() ):
        test.activateAutoTestOption();
        debug( "Hello World" );
        logToChoregraphe( "Hello Mr Choregraphe from abcdk.debug" );
        print( "getFileAndLinePosition: " + str( getFileAndLinePosition( 0 ) ) );
        
# autoTest - end
    
if( __name__ == "__main__" ):
    autoTest();