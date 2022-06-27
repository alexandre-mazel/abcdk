# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# System tools
# Author: A. Mazel
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Aldebaran Behavior Complementary Development Kit: A module for system tools."""
print( "importing abcdk.system" );

import math
import os
import signal
import sys
import threading
import time

import config
import debug
import filetools
import naoqitools
import pathtools
import stringtools # for findNumber
import test
import typetools

#print( debug.dump( signal ) ); # loof for cont and stop numbers...

global_isOnRobot_Cache = None; # optim to prevent opening one file each time
def isOnRobot( bForceRecompute = False ):
    """Are we on an Aldebaran Robot ?"""
    global global_isOnRobot_Cache;
    if( global_isOnRobot_Cache != None and not bForceRecompute ):
        return global_isOnRobot_Cache;    
    szCpuInfo = "/proc/cpuinfo";
#  if not isFileExists( szCpuInfo ): # already done by the getFileContents
#    return False;
    szAllFile =  filetools.getFileContents( szCpuInfo, bQuiet = True );
    if( szAllFile.find( "Geode" ) == -1 and szAllFile.find( "Intel(R) Atom(TM)" ) == -1 ):
        global_isOnRobot_Cache = False;
        return False;
    global_isOnRobot_Cache = True;
    return True;
# isOnRobot - end

global_isOnNao_Cache = None; # small optim...
def isOnNao( bForceRecompute = False ):
    """Are we on an Aldebaran Robot, and this is NAO ?"""
    global global_isOnNao_Cache;
    if( global_isOnNao_Cache != None and not bForceRecompute ):
        return global_isOnNao_Cache;
    if( not isOnRobot() ):
        global_isOnNao_Cache = False;
        return global_isOnNao_Cache;
    mem = naoqitools.myGetProxy( "ALMemory" );
    try:
        try:
            value = mem.getData( "HAL/Robot/Type" );
        except BaseException, err:
            print( "INF: system.isOnNao: while accessing HAL/Robot/Type: %s (version <1.14?)" % str( err ) );
            value = "nao"; # forcing to be on nao, because version  prior to 1.14 are all just for nao (and we've already check we're on a robot)
        if( value.lower() == "nao" ):
            global_isOnNao_Cache = True;
            return global_isOnNao_Cache;
    except BaseException, err:
        print( "INF: system.isOnNao: err: " + str( err ) );
    global_isOnNao_Cache = False;
    return global_isOnNao_Cache;
# isOnNao - end

global_isOnRomeo = None;
def isOnRomeo( bForceRecompute = False ):
    """Are we on an Aldebaran Robot, and this is Romeo ?"""
    global global_isOnRomeo;
    if( global_isOnRomeo != None and not bForceRecompute ):
        return global_isOnRomeo;
    mem = naoqitools.myGetProxy( "ALMemory" );
    try:
        value = mem.getData( "HAL/Robot/Type" );
    except BaseException, err:
        if( mem != None ):
            print( "INF: system.isOnRomeo: while accessing HAL/Robot/Type: %s (version <1.14? or a Romeo not well configurated?) (using hostname)" % str( err ) );
        value = getNickName(); # we wish to have romeo in the hostname of any of our beta romeo
    print( "abcdk.system.isOnRomeo: %s" % value );
    bRet = "romeo" in value.lower();
    global_isOnRomeo = bRet;
    return bRet;
# isOnRomeo - end

global_isOnPepper = None;
def isOnPepper( bForceRecompute = False ):
    """Are we on an Aldebaran Robot, and this is Pepper/Juliette ?"""
    global global_isOnPepper;
    if( global_isOnPepper != None and not bForceRecompute ):
        return global_isOnPepper;
    mem = naoqitools.myGetProxy( "ALMemory" );
    try:
        value = mem.getData( "HAL/Robot/Type" );
    except BaseException, err:
        if( mem != None ):
            print( "INF: system.isOnPepper: while accessing HAL/Robot/Type: %s (version <1.14? or a Romeo not well configurated?) (using hostname)" % str( err ) );
        value = getNickName(); # we wish to have romeo in the hostname of any of our beta romeo
    print( "INF: abcdk.system.isOnPepper: %s" % value );
    bRet = "juliette" in value.lower();
    global_isOnPepper = bRet;
    return bRet;
# isOnPepper - end

def reloadSystemPrecalcGlobal():
    """
    After changing default ip of targeted robot, some global has to be reloaded
    """
    isOnNao(bForceRecompute=True);
    isOnPepper(bForceRecompute=True);
    isOnRomeo(bForceRecompute=True);
    isOnRobot(bForceRecompute=True);

def isOnOtherRobotThanNao():
    """Are we on an Aldebaran Robot, but this is not NAO ?"""
    return isOnRobot() and not isOnNao();
# isOnOtherRobotThanNao - end

def isOnWin32():
    "Are we on a ms windows system?"
    # return not isOnNao() and os.name != 'posix';
    return os.name != 'posix';
# isOnWin32 - end

def getNaoIP():
  "get the nao ip address (eth>wifi)"
  if( not isOnRobot() ):
    return "";

  try:    
      import socket # under windows, we doesn't have this module
      import fcntl
      import struct
  except:
      return "";
  def get_ip_address( strInterfaceName ):
    "get the ip associated to a linux network interface"
    "WARNING: it assumes that device are eth0 and wlan0 (known bugs on some 1.12.xx)"
    "return '' on no ip"
    try:
      sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
#      print( "sock: '%s'" % str( sock ) );
#      print( "strInterfaceName: " + str( strInterfaceName ) );
      strInterfaceName = strInterfaceName[:15];
#      print( "strInterfaceName: " + str( strInterfaceName ) );
      packedInterfaceName = struct.pack( '256s', strInterfaceName );
#      print( "packedInterfaceName: " + str( packedInterfaceName ) );
      ret = fcntl.ioctl(
          sock.fileno(),
          0x8915,  # SIOCGIFADDR
          packedInterfaceName
      );
#      print( "ret: '%s'" % ret );
      ret = ret[20:24];
#      print( "ret: '%s'" % ret );
      return socket.inet_ntoa( ret );
    except:
      return '';
  # get_ip_address - end

  debug.debug( "getNaoIP: getting ethernet" );
  # romeo case
  strIP = get_ip_address( 'eth1' );
  if( strIP != '' ):
    return strIP;
  strIP = get_ip_address( 'eth0' );
  if( strIP != '' ):
    return strIP;
  #~ strIP = get_ip_address( 'eth1' ); # handle other interface (bug on 1.12.46)
  #~ if( strIP != '' ):
    #~ return strIP;
  #~ strIP = get_ip_address( 'eth2' );
  #~ if( strIP != '' ):
    #~ return strIP;    
  debug.debug( "getNaoIP: getting wifi" );
  return get_ip_address( 'wlan0' );
# getNaoIP - end

# print "getNaoIP(): '%s'" % str( getNaoIP() );

def getNaoIPs():
  "get the nao ips address: [eth,wifi]"
  if( not isOnRobot() ):
    return [];

  try:    
      import socket # under windows, we doesn't have this module
      import fcntl
      import struct
  except:
      return "";
  def get_ip_address( strInterfaceName ):
    "get the ip associated to a linux network interface"
    try:
      sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
#      print( "sock: '%s'" % str( sock ) );
#      print( "strInterfaceName: " + str( strInterfaceName ) );
      strInterfaceName = strInterfaceName[:15];
#      print( "strInterfaceName: " + str( strInterfaceName ) );
      packedInterfaceName = struct.pack( '256s', strInterfaceName );
#      print( "packedInterfaceName: " + str( packedInterfaceName ) );
      ret = fcntl.ioctl(
          sock.fileno(),
          0x8915,  # SIOCGIFADDR
          packedInterfaceName
      );
#      print( "ret: '%s'" % ret );
      ret = ret[20:24];
#      print( "ret: '%s'" % ret );
      return socket.inet_ntoa( ret );
    except:
      return '';
  # get_ip_address - end

  return [get_ip_address( 'eth0' ), get_ip_address( 'wlan0' )];
# getNaoIPs - end

import subprocess


class ASyncSystemCallThread( threading.Thread ):
    def __init__(self, strCommandAndArgs, bStoppable = False ):
        threading.Thread.__init__( self );
        self.strCommandAndArgs = strCommandAndArgs;
        self.newProcess = False;
        self.bStoppable = bStoppable;
    # init - end

    def run ( self ):
        debug.debug( "system.asyncSystemCallThread calling '%s'" % self.strCommandAndArgs );
        # mySystemCall( self.strCommandAndArgs );
        if( self.bStoppable and isOnWin32() ):
            self.newProcess = subprocess.Popen( self.strCommandAndArgs );  # sous windows, il ne faut oas mettre shell a true si on veut pouvoir arreter une tache (genre lancer choregraphe)
        else:
            self.newProcess = subprocess.Popen( self.strCommandAndArgs, shell=True ); # , stdin=subprocess.PIPE
        try:
            sts = os.waitpid( self.newProcess.pid, 0 );
        except:
            pass # pid already finished or some erros occurs or under windows ?
        debug.debug( "system.asyncSystemCallThread calling '%s' - end" % self.strCommandAndArgs );
    # run - end

    def stop( self, rTimeOut = 2.0 ):
        "stop the process"
        "return -1 if it hasn't been really stopped"
        if( self.newProcess == False ):
            return -1; # the process hasn't been launch yet !

        if( not self.isFinished() ):
        #~ if(   os.name != 'posix' ):
            #~ # Kill the process using pywin32
            #~ import win32api # install from pywin32-214.win32-py2.6.exe
            #~ print dump( win32api );
            #~ win32api.TerminateProcess( int( self.newProcess._handle ), -1)
            #~ win32api.CloseHandle(self.newProcess._handle);
            #~ import ctypes
            #~ ctypes.windll.kernel32.TerminateProcess(int(self.newProcess._handle), -1)
        #~ else:
            try:
                self.newProcess.terminate(); # warning: require python2.6 or higher # fonctionne mais shell doit etre a true dans le Popen
            except:
                print( "WRN: testAll: ASyncSystemCallThread.stop: terminate failed" );
        self.join( rTimeOut ); #wait with a timeout of n sec
        if( not self.isFinished() ):
            time.sleep( rTimeOut / 4.0 ); # time for things to be resfreshed (join/poll or ...) (longer)
        if( not self.isFinished() ):
            return -1;
        return self.newProcess.returncode;
    # stop - end

    def isFinished( self ):
        "is the process finished ?"
        time.sleep( 0.05 ); # time for things to be resfreshed (join/poll or ...)
#       return self.isAlive();
        if( self.newProcess == False ):
            return False; # the process hasn't been launch yet !
            
        if( isOnWin32() ):
            self.newProcess.poll();
            return ( self.newProcess.returncode != None );
        # on new gentoo, it works better with that:
        return not self.is_alive();
    # isFinished - end
    
    def pause( self ):
        # os.kill( self.newProcess.pid, signal.SIG_STOP ); # SIG_STOP: don't exists...
        mySystemCall( "kill -STOP %d" % self.newProcess.pid );
        
    def resume( self ):
        # os.kill( self.newProcess.pid, signal.SIG_CONT );
        mySystemCall( "kill -CONT %d" % self.newProcess.pid );

# ASyncSystemCallThread - end

def asyncSystemCall( strCommandAndArgs, bStoppable = False ):
  "launch a system call, without waiting the end of the system call"
  "return the thread object"
  async = ASyncSystemCallThread( strCommandAndArgs, bStoppable );
  async.start();
  return async;
# asyncSystemCall - end


def mySystemCall( strCommandAndArgs, bWaitEnd = True, bStoppable = False, bQuiet = False ):
    "make a system call, and choose to wait till the end or to thread"
    "return the process status or an object of type ASyncSystemCallThread, if it's an asynccall"
    if( not bQuiet ):
        debug.debug( "altools: mySystemCall( '%s', bWaitEnd=%d, bStoppable=%d)" % ( strCommandAndArgs, bWaitEnd, bStoppable ) );
    obj = False;
    if( config.bTryToReplacePopenByRemoteShellCall ):
        try:
            ur = naoqitools.myGetProxy( "UsageRemoteTools", True );
            if( ur == None ):
                if( not bQuiet ):
                    print( "WRN: mySystemCall: UsageRemoteTools not found, doing a standard call..." );
            else:
                naoqiTask = None;
                if( bWaitEnd ):
                    ur.systemCall( strCommandAndArgs );
                else:
                    id = ur.post.systemCall( strCommandAndArgs );
                    naoqiTask = naoqitools.naoqiTask( id, "UsageRemoteTools" );
                if( not bQuiet ):
                    debug.debug( "system.mySystemCall( '%s', bWaitEnd=%d ) - remote call - end" % ( strCommandAndArgs, bWaitEnd ) );
                return naoqiTask;
        except BaseException, err:
            if( not bQuiet ):
                print( "WRN: system.mySystemCall: UsageRemoteTools error, doing a standard call - err: %s" %  err );
            pass # in case of bug, we will use normal call (next lines)
    
    # else cas normal
    if( bWaitEnd ):
        try:
            newProcess = subprocess.Popen( strCommandAndArgs, shell=True ); # not blocking !
        except AttributeError, err:
            debug.debug( "WRN: bug in subprocess.Popen: doing a shell system, err: %s" % str( err ) );
            newProcess = os.system( strCommandAndArgs );
        try:
            sts = os.waitpid( newProcess.pid, 0 );
            obj = sts[1]; # waitpid return (pid, exitstatus)
        except:
            pass # pid already finished or some erros occurs or under windows ?
    else:
        obj = asyncSystemCall( strCommandAndArgs, bStoppable );
    if( not bQuiet ):
        debug.debug( "altools: mySystemCall( '%s', bWaitEnd=%d) - end" % (strCommandAndArgs, bWaitEnd ) );
    return obj;
# mySystemCall - end

class ASyncEvalThread( threading.Thread ):
    def __init__(self, strPythonCode, globaldico = None, localdico = None, bStoppable = False ):
        """
        strPythonCode: a string to execute or an array of string to launch in sequence, unless it has been stopped
        """
        threading.Thread.__init__( self );
        self.strPythonCode = ( strPythonCode );
        self.globaldico = globaldico;
        self.localdico = localdico;
        self.bStoppable = bStoppable;
        self.bMustStop = False;
    # init - end

    def run( self ):
        import choregraphetools # to avoid cyclic import
        debug.debug( "altools: ASyncEvalThread evaluating '%s'" % self.strPythonCode );
        self.bMustStop = False;
        sys.settrace( self.globaltrace ); # permit to kill thread, WRN: it's a debug purpose functionnality not existing or all platform and ...
        #~ self.strPythonCode = """
#~ import signal
#~ print( 'installing handler...' );
#~ def handler(signum, frame):
    #~ print 'Signal handler called with signal', signum;
    #~ exit( 42 );
#~ signal.signal(signal.SIGTERM, handler)
#~ """ + self.strPythonCode; => ERROR signal only works in main thread
        if( config.bDebugMode ):
            choregraphetools.logToChoregraphe( "self.strPythonCode: '%s'" % self.strPythonCode );
        if( typetools.isArray( self.strPythonCode ) ):            
            debug.debug( "altools: ASyncEvalThread evaluating this sequence: %s" % self.strPythonCode );    
            if( not self.bMustStop ):
                for s in self.strPythonCode:
                    debug.debug( "altools: ASyncEvalThread evaluating this piece of sequence: '%s'" % s );
                    exec( s, self.globaldico, self.localdico );
                    if( self.bMustStop ):
                        break;             
        else:
            exec( self.strPythonCode, self.globaldico, self.localdico ); # TODO: here: do something to test bMustStop is not Set to True, if so exit
        debug.debug( "altools: ASyncEvalThread evaluating '%s' - end" % ( self.strPythonCode ));
    # run - end

    def stop( self, rTimeOut = 3.0 ):
        "stop the process"
        #   if( not self.isFinished() ): # doesnt return a correct value!
        debug.debug( "ASyncEvalThread.stop(): stopping..." );
        self.bMustStop = True;
        return self.join( rTimeOut ); #wait with a timeout of n sec # attention au bout de n sec, il ne kill pas le join mais juste il rend la main...
    # stop - end

    def isFinished( self ):
        "is the process finished ?"
        bAlive = self.isAlive();
        debug.debug( "ASyncEvalThread.isFinished() => %s" % str( not bAlive ) );
        return not bAlive;
    # isFinished - end

    def globaltrace(self, frame, why, arg):
#        logToChoregraphe( "globaltrace( frame='%s', why='%s', arg='%s' )" % (frame, why, arg) );
        if why == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, why, arg):
#        logToChoregraphe( "localtrace( frame='%s', why='%s', arg='%s' )" % (frame, why, arg) );
        if self.bMustStop:
            if why == 'line':
                raise sys.exit( -9 );
        return self.localtrace;

# ASyncEvalThread - end

def asyncEval( strPythonCode, globaldico =globals(), localdico = locals() ):
  "launch an evaluation in another python thread, a tricky specific manner"
  evaluationThreadObj = ASyncEvalThread( strPythonCode, globaldico, localdico );
  evaluationThreadObj.start();
  return evaluationThreadObj;
# asyncEval


def getNaoChestName():
    "get the nao name as stored in the rom chest"
    stm = naoqitools.myGetProxy( "ALMemory" );
    strNum = stm.getData( "Device/DeviceList/ChestBoard/BodyNickName" );
    if( strNum == 'Nao336' and getNaoNickName() == 'Astroboy' ):
        strNum = 'Nao332';    
    return strNum;
# getNaoChestName - end

def getBodyID():
    """
    get the body ID
    Return a string with the ID or "" if no body ID
    """
    try:
        stm = naoqitools.myGetProxy( "ALMemory" );
        strBodyID = stm.getData( "Device/DeviceList/ChestBoard/BodyId" );
        strBodyID = str(strBodyID);
    except BaseException, err:
        print( "WRN: abcdk.system.getBodyID: err: %s" % err );
        return "";
    return strBodyID;

def getNaoNickName():
    "get the nao name as given by user"
    return getNickName();
# getNaoNickName - end

def getNickName():
    "get the robot name as given by user"
    # return executeAndGrabOutput( "hostname", True );
    try:
        strRet = filetools.getFileFirstLine( '/etc/hostname', bQuiet = True );
        if( strRet != "" ):
            return strRet;
    except BaseException, err:
        print( "WRN: system.getNickName: err: %s" % str(err) );
    return "computer"; # error case
# getNickName - end


def getNaoMagic( bCanonics =True ):
    "compute a magic relative to THIS NAO"
    "it should differs from one NAO to another, but..."
    "bCanonics, if set, the collision between two NAO would be very rare"
    "           when set to false, the magic is just a number between 0 and 255"
    stm = naoqitools.myGetProxy( "ALMemory" );
    strHead = stm.getData( "RobotConfig/Head/HeadId" );
    if( bCanonics ):
        strBody = stm.getData( "Device/DeviceList/ChestBoard/BodyId" );
        nNumBody = stringtools.findNumber( strBody, bFindLast = True );
        nMagic = int( strHead ) + 10000*nNumBody; # we could have two nao with same number, cross every 10000 NAOs
    else:
        nMagic = int( strHead ) % 256;
    return nMagic;
# getNaoMagic - end

global_listNaoOwner = {
    '316': ['Valentin','Nanimator'],
    '327': ['Alex','NaoAlex'],
    '598': ['Alex','NaoAlex'],
    '425': ['Accueil','NaoLife'],
    '302': ['Flora','NaoFlop'],
    '471': ['Céline','Lestate'],
    '488': ['Jérome','NaoIntissar'],
    '492': ['Julien','Nao2Jams'],
    
    '340': ['JmPomies','Tifouite'],
    '337': ['Jerome Laplace',''],
    '329': ['Locki','Noah'],
    '340': ['Troopa',''],
    '351': ['Mlecyloj',''],
    '317': ['Scoobi','Nao'],
    '379': ['Ksan','Timmy'],
    '387': ['Richard Seltrecht','Isaac'],
    '341': ['Zelig','Sonny'],
    '339': ['Rodriguez','Andrew'],
    '305': ['Tibot','Zoé'],
    '314': ['Laurent','Nao'],
    '409': ['Drack','Igor'],
    '319': ['Oxman','R2'],
    '342': ['Jfiger',''],
    '321': ['Bothari','Tchoggi'],
    '307': ['Alexan','Cybot'],
    '407': ['Olleke','Domo'],
    '412': ['Hadrien',''],
    '312': ['Bilbo','Nao'],
    '334': ['Nameluas','Nao'],
    '338': ['DavidRPT','Nao'],
    '332': ['Clayde','AstroBoy'],  # 332 renamed in 336
    '336': ['Harkanork','Tao'],
    '330': ['Antoine','Naodadi'],
    '367': ['Mataweh','Junior'],
    '358': ['Lexa','Zirup'],
    '306': ['Gwjsan','Naomi'],
};

def getUserNameFromChestBody():
    "get the user name from the chest number"
    "WRN: valid only for appu, and beta30!"
    global global_listNaoOwner;
    strNum = getNaoChestName(); 
    strNum = strNum[3:];
    try:
        strName = global_listNaoOwner[strNum][0];
    except:
        strName = "unknown";
    return strName;
# getUserNameFromChestBody - end

def executeAndGrabOutput( strCommand, bLimitToFirstLine = False, bIncludeErrorOutput = False, bQuiet = False ):
  "execute a command in system shell and return grabbed output"
  "WARNING: it's a 'not efficient' function!"
  strTimeStamp = filetools.getFilenameFromTime();
  strOutputFilename = pathtools.getVolatilePath() + "grab_output_" + strTimeStamp+ ".tmp"; # generate a different file each call for multithreading capabilities
  strTotalCommand = strCommand + " >" + strOutputFilename;
  if( bIncludeErrorOutput ):
        strTotalCommand += " 2>&1";  # 2>&1: redirect error in standard output    
  mySystemCall( strTotalCommand, bQuiet = bQuiet );
  if( isOnWin32() ):
    time.sleep( 1.5 );
  if( bLimitToFirstLine ):
    strBufferRead = filetools.getFileFirstLine( strOutputFilename );
  else:
    strBufferRead = filetools.getFileContents( strOutputFilename );
  try:
    os.unlink( strOutputFilename );
  except:
    pass
  if( not bQuiet ):
    debug.debug( "executeAndGrabOutput: '%s'" % strBufferRead );
  return strBufferRead;
# executeAndGrabOutput - end


def getCpuLoad():
    "get the current cpu load/usage (as an integer percent) (the second value from uptime)"
    "in fact the first value is better: it represents 1min, so it's more interesting"
    # strRet = executeAndGrabOutput( "uptime | cut -dg -f2 | cut -d: -f2" );
    #~ try:
        #~ strText = executeAndGrabOutput( "uptime" );
        #~ aAnalysed = strText.split( 'load average:' );
        #~ aAnalysed = aAnalysed[1].split( ',' );
        #~ return int(float( aAnalysed[1] ) * 100);
    #~ except:
        #~ return 0;
  
    try:
        szCpuLoad = "/proc/loadavg";
        strAllFile = filetools.getFileContents( szCpuLoad );
        listVar = strAllFile.split( ' ' );
        if( len( listVar ) > 1 ):
            return int( float( listVar[0] ) * 100 ); # change listVar[1] to [0] to have the time on 1 min
    except BaseException, err:
        debug.debug( "ERR: altools.getCpuLoad: %s" % str( err ) );
    return 0;
# getCpuLoad - end


def getHeadTemperature():
    "return the temperature of the silicium in degrees, or -42 if no temperature found"
    for strFilename in ["/sys/class/i2c-adapter/i2c-1/1-004c/temp2_input","/var/run/alfand/cputemp", "/sys/devices/virtual/thermal/thermal_zone0/temp"]:
        try:
            file = open( strFilename, "rt" );
        except IOError, err:
            #print( "DBG: getHeadTemperature: IOError: %s" % err );
            continue
        
        if( file ):
            break;
    else:
        return -42; # no file found, let's return a dummy value
        
    try:
        strTemp = file.read();    
        nTemp = int( strTemp ) / 1000;
    finally:
        file.close();
    return nTemp;
# getHeadTemperature - end

def getBodyVersion():
    "return the body version as a string"
    "return: '3.2', '3.3', ..."
    try:
        stm = naoqitools.myGetProxy( "ALMemory" );
        strText = stm.getData( "RobotConfig/Body/BaseVersion" );
        return strText[1:];
    except BaseException, err:
        print( "abcdk.system.getBodyVersion(): error: %s" % str( err ) );
        return 'unknown body version';
# getBodyVersion - end
    
def getHeadVersion():
    "return the body version as a string"
    "return: '3.2', '3.3', ..."
    try:
        stm = naoqitools.myGetProxy( "ALMemory" );
        strText = stm.getData( "RobotConfig/Head/BaseVersion" );
        return strText[1:];
    except BaseException, err:
        print( "abcdk.system.getHeadVersion(): error: %s" % str( err ) );
        return 'unknown head version';
# getHeadVersion - end

def getCameraType():
    strHeadVersion = getHeadVersion();
    if( isOnNao ):
        if( "3." in strHeadVersion ):
            return "OV7670";
        return "MT9M114";
    return "OV5640"; # 2
# getCameraType - end
    
def getNaoqiVersion():
    "return the naoqi version as a string"
    "return: '3.2', '3.3', ..."
    try:
        stm = naoqitools.myGetProxy( "ALMemory" );
        return stm.version();
    except BaseException, err:
        print( "abcdk.system.getNaoqiVersion(): error: %s" % str( err ) );
        return 'unknown naoqi version';
# getNaoqiVersion - end

def isPlugged( bVerbose = False ):
    """
    Is battery plugged ?
    """
    mem = naoqitools.myGetProxy( "ALMemory" );
    status = mem.getData( "Device/SubDeviceList/Battery/Charge/Sensor/Status" );
    if( bVerbose ):
        print( "INF: abcdk.system.isPlugged: battery status signed: %s" % status );
    if( not math.isnan( status  ) ):
        if( status < 0 ):
            status = status + 0x10000;
        status = int( status );
        if( bVerbose ):
            print( "INF: abcdk.system.isPlugged: battery status unsigned: 0x%x" % status );
        bEmptyBattery = (status&0x1)>0;
        bNearlyEmptyBattery = (status&0x2)>0;
        bDischargingFlag = (status&0x20)>0;    
        bCharging = (status&0x80)>0;
        bPlugged = (status&0x8000)>0;
        if( bVerbose ):
            print( "INF: abcdk.system.isPlugged: bEmptyBattery: %s, bNearlyEmptyBattery: %s, bCharging: %s, bDischargingFlag: %d, bPlugged: %s" % (bEmptyBattery, bNearlyEmptyBattery, bCharging, bDischargingFlag, bPlugged) );    
        # plugged est en fait buggé et retourne toujours True (du moins en 1.22.1 avec les nouvelles batteries), donc on décide de ne jamais l'utiliser!
        if( not bCharging ):
            rCurrentConsomation = mem.getData( "Device/SubDeviceList/Battery/Current/Sensor/Value" );
            #~ print( "INF: abcdk.system.isPlugged: rCurrentConsomation: %s" % rCurrentConsomation );
            if( rCurrentConsomation > -0.5 ):
                bCharging = True;        
        return bCharging;
        
    #patch 1.22 or ...
    if( bVerbose ):
        print( "WRN: abcdk.system.isPlugged: battery status is nan (=%s)" % status );
    rConso = mem.getData( "Device/SubDeviceList/Battery/Current/Sensor/Value" );
    bPlugged = rConso > -0.5;
    if( bVerbose ):
        print( "INF: abcdk.system.isPlugged: rConso: %f => plugged: %s" % ( rConso, bPlugged ) );
    # NB: will work only if the battery is not full charged, nor too hot, and the robot is not stiffness and moving.
    return bPlugged;
# isPlugged - end

def getBatteryLevel():
    """
    return current battery level [0..1]
    """
    mem = naoqitools.myGetProxy( "ALMemory" );
    rValue = mem.getData( "Device/SubDeviceList/Battery/Charge/Sensor/Value" );
    return rValue;
# getBatteryLevel - end
    
    

global_FindPort_listPort = {};
def findExternalPort( strFilter = "" ):
    # return usb or BT port present (tested on NAO NextGen v1.12.5)
    # strFilter : filter on some word contains in the port, eg ttyU will return only /dev/ttyUSB0, /dev/ttyUSB1, ...
    # return [listPort, listNew]
    # listPort: all present port (including new) eg ["/dev/ttyUSB0"]
    # listNew: all port created since last call
    global global_listFindPort;
    listPort = [];
    listNew = [];    
    strPath = "/dev/";
    for file in os.listdir( strPath ):
        if( "ttyA" in file or "rfcomm" in file or "ttyUSB" in file ): #ttyA is for Usb Arduino, rfcomm for BT Arduino, and ttyUSB* for Romeo Brain
            if( strFilter == "" or strFilter in file ):
                try:
                    nTimeCreation = os.path.getmtime( strPath + file );
                    if( not file in global_FindPort_listPort.keys() or global_FindPort_listPort[file] < nTimeCreation ):
                        print( "INF: system.findExternalPort: Found a new created port: %s (showing only '*%s*')" % ( file, strFilter ) );
                        global_FindPort_listPort[file] = time.time();
                        listNew.append( strPath + file );
                    listPort.append( strPath + file );                
                except BaseException, err:
                    print( "WRN: system.findExternalPort: port %s disappeard just now? (err: %s)" % ( file, str( err ) ) );
    return [listPort, listNew];
# findExternalPort - end

def mount( strDevice = "", strLocation = "" ):
    # mount a device, implicit device or location is possible using /etc/fstab current option
    # return -2: no rights, -1: not in the fstab or mtab, 0: drive not present, 1: ok, 2: already mounted
    buf = executeAndGrabOutput( "mount %s %s" % ( strDevice, strLocation ), bIncludeErrorOutput = True );
#    print( "mount buf:'%s'" % buf );
    if( "already mounted" in buf ):
        return 2;
    if( "only root can" in buf ):
        return -2;        
    if( "can't find" in buf ):
        return -1;        
    if( "does not exist" in buf ):
        return 0;
    return 1;
# mount - end

def unmount( strDeviceOrLocation ):
    # unmount a device
    # return -2: no rights, -1: busy, 0: is not mounted, 1: ok, 
    buf = executeAndGrabOutput( "umount %s" % ( strDeviceOrLocation ), bIncludeErrorOutput = True );
    print( "unmount buf:'%s'" % buf );
    if( "is not mounted" in buf ):
        return 0;
    if( "busy" in buf ):
        return -1;
    if( "only root can" in buf ):
        return -2;
    return 1;
# unmount - end
    

def testDetectAlive():
    myThread = mySystemCall( "sleep 5", bWaitEnd = False, bStoppable = True );
    timeBegin = time.time();
    while( time.time() - timeBegin < 10 ):
        print( "thread is finished?: %s; poll: %s, isAlive: %s; active_count: %d; enumerate: %s" % ( str( myThread.isFinished()  ), str( myThread.newProcess.poll() ), str( myThread.isAlive() ), threading.active_count(), str( threading.enumerate() ) ) );
        time.sleep( 1 );
    #    myThread.stop();
# testDetectAlive - end

def getBoardList( bOnlyMotor = False ):
    """
    Git all board in current robot.
    TODO: test all configuration
    """
    aList = [];
    aList.append( "RightFootBoard" );
    aList.append( "LeftFootBoard" );
    aList.append( "LeftShinBoard" );
    aList.append( "LeftThighBoard" );
    aList.append( "LeftHipBoard" );
    aList.append( "RightShinBoard" );
    aList.append( "RightThighBoard" );
    aList.append( "RightHipBoard" );
    aList.append( "RightHandBoard" );
    aList.append( "RightArmBoard" );
    aList.append( "RightShoulderBoard" );
    
    aList.append( "LeftHandBoard" );
    aList.append( "LeftArmBoard" );
    aList.append( "LeftShoulderBoard" );
    aList.append( "HeadBoard" );
    if( not bOnlyMotor ):
        aList.append( "TouchBoard" );    
        aList.append( "ChestBoard" );
        aList.append( "USBoard" );
        aList.append( "FaceBoard" );
    return aList;
# getBoardList - end
#~ print( getBoardList() );

class BatteryRomeo:
    """
    Handle Battery for Romeo.
    classic use:
        battery.checkOnce();
        while( 1 ):
            battery.checkPeriodically();
            time.sleep( 2 );
    """
    def __init__( self ):
        self.mem = None;
        
    def create(self):
        """
        Create all the variable (should be done directly from init, but we don't want to create it at singleton creation)
        Do that once!
        """
        if( not isOnRomeo() ):
            return;
            
        self.mem = naoqitools.myGetProxy( "ALMemory" );
        
        self.listData = [ 
            "Device/SubDeviceList/Battery/Charge/Sensor/Value",
            "Device/subdeviceList/Battery/Charge/Sensor/CyclesCount",
            "Device/SubDeviceList/Battery/TotalVoltage",
            "Device/SubDeviceList/Battery/Charge/Sensor/Charging",            
        ];
        
        for i in range( 4 ):
            self.listData.append( "Device/SubDeviceList/Battery/TemperatureSensor%d/Sensor/Value" % (i+1) );
            
        self.bIsCharging = None;
    # create - end
            
    def checkOnce( self ):
        """
        Check that everything seems ok
        return 0 or a negative value in case of error
        """
        if( self.mem == None ):
            self.create();
            
        strBatteryVersion = self.mem.getData( "Device/DeviceList/Battery/FirmwareVersion" );
        if( strBatteryVersion != "4.3c" ):
            print( "WRN: abcdk.BatteryRomeo.checkOnce: strBatteryVersion: '%s'" % strBatteryVersion );
            return -1;
        return 0;
    # checkOnce - end
    
    def isCharging( self ):
        return self.bIsCharging;
            
    def checkPeriodically( self ):
        """
        Check that everything seems ok
        return 0 or a negative value in case of error, a positive value in case of information
        """
        aListVal = self.mem.getListData( self.listData );
        print( "DBG: abcdk.BatteryRomeo.checkPeriodically: data: %s" % aListVal );
        
        nFirstIdxTemperature = 4;
        nFirstIdxCell = 8;
        rChargeValue = aListVal[0];
        strCycleCount = aListVal[1];
        rTotalVoltage = aListVal[2];
        bInCharge = aListVal[3];
        
        if( rChargeValue < 0.05 ):
            return -100; 
        if( rChargeValue < 0.1 ):
            return -10;
            
        if( strCycleCount != None ):
            nCycleCount = int( strCycleCount );
            if( nCycleCount < 0 or nCycleCount > 2000 ):
                print( "ERR: abcdk.BatteryRomeo.checkPeriodically: nCycleCount: %d" % nCycleCount );
                return -5;
                
        if( rTotalVoltage != None ):
            if( rTotalVoltage < 48. ):
                print( "ERR: abcdk.BatteryRomeo.checkPeriodically: rTotalVoltage: %f" % rTotalVoltage );
                return -110;
            if( rTotalVoltage > 55. ):
                print( "ERR: abcdk.BatteryRomeo.checkPeriodically: rTotalVoltage: %f" % rTotalVoltage );
                return -111;
                
        for i in range( 4 ):
            rVal = aListVal[nFirstIdxTemperature+i];
            if( rVal > 58. ):
                print( "ERR: abcdk.BatteryRomeo.checkPeriodically: %d: temperature: %f" % (i, rVal) );
                return -120;
            if( rVal < -18. ):
                print( "ERR: abcdk.BatteryRomeo.checkPeriodically: %d: temperature: %f" % (i, rVal) );
                return -121;             
                
        # information
        if( bInCharge != self.bIsCharging ):
            self.bIsCharging = bInCharge;
            print( "INF: abcdk.BatteryRomeo.checkPeriodically: charging change, now it's: %f" % self.bIsCharging );
            if( self.bIsCharging ):
                return 2;
            return 1;
                
            
        return 0;
    # checkPeriodically - end    
        
    def getErrorDesc( self, nNumber ):
        dictError = {
            1: {
                    "en": "I'm unplugged.",
                    "fr": "Je suis débranché.",
                },
            2: {
                    "en": "I'm charging.",
                    "fr": "Je me charge.",
                },                
            -1: {
                    "en": "Warning: The battery version is not the one expected.",
                    "fr": "Attention: La version de la batterie ne semble pas bonne.",
                },
            -5: {
                    "en": "Warning: error with battery cycle number",
                    "fr": "Attention: Erreur de nombre de cycle sur la batterie",
                },                
            -10: {
                    "en": "Warning: The battery is low.",
                    "fr": "Attention: La batterie est basse.",
                },
            -20: {
                    "en": "Warning: Check the battery's balancing.",
                    "fr": "Attention: Verifier l'equilibrage de la batterie.",
                },
            -30: {
                    "en": "Warning: I am going to walk with my charger connected.",
                    "fr": "Attention: Tu me demandes de marcher alors que mon chargeur est connecté.",
                },                
            -100: {
                    "en": "The battery is very low.",
                    "fr": "La batterie est très basse.",
                },
            -110: {
                    "en": "The battery has too low voltage.",
                    "fr": "La tension de la batterie est trop basse.",
                },
            -111: {
                    "en": "The battery has too high voltage.",
                    "fr": "La tension de la batterie est trop haute.",
                },                
            -120: {
                    "en": "The battery is too hot.",
                    "fr": "La batterie est trop chaude.",
                },
            -121: {
                    "en": "The battery is too low.",
                    "fr": "La batterie est trop basse.",
                },                
        };
        import translate
        return translate.chooseFromDict( dictError[nNumber] );
    # getErrorDesc - end
# class BatteryRomeo - end
    
battery = BatteryRomeo();
    

def autoTest():
    if( test.isAutoTest() or True ):
        test.activateAutoTestOption();
        print( "isOnRobot(): '%s'" % str( isOnRobot() ) );
        print( "isOnNao(): '%s'" % str( isOnNao() ) );
        print( "isOnWin32(): '%s'" % str( isOnWin32() ) );
        print( "getNaoIP(): '%s'" % str( getNaoIP() ) );
        print( "getNaoIPs(): '%s'" % str( getNaoIPs() ) );
        print( "getNaoqiVersion(): '%s'" % str( getNaoqiVersion() ) );
        print( "getHeadVersion(): '%s'" % str( getHeadVersion() ) );
        print( "getCameraType(): '%s'" % str( getCameraType() ) );
        
        backgroundTask = mySystemCall( "echo waiting 5s;sleep 5;echo end of waiting 5s", bWaitEnd = False );
        mySystemCall( "echo ; echo CECI EST UNE TRACE DE TEST; echo" );
        print( "backgroundTask_wait_5s isFinished: %s" % str( backgroundTask.isFinished() ) );
        time.sleep( 5 );
        print( "backgroundTask_wait_5s isFinished: %s" % str( backgroundTask.isFinished() ) );
        backgroundTask2 = mySystemCall( "echo waiting 5s (2);sleep 5;echo end of waiting 5s (2)", bWaitEnd = False );
        print( "killing task2 - before" );
        backgroundTask2.stop();
        print( "killing task2 - after" );
        time.sleep( 1 );
        print( "finished (after that, there should be no more trace...)" );
        
        
# autoTest - end
    
#~ autoTest();
# testDetectAlive();

print( "importing abcdk.system - end" );

#nMagic = abcdk.system.getNaoMagic();kol
if( 0 ):
    nMagic = 26033508
    nMagic = 47974546
    nSpeedMod = (nMagic%17)-8;
    nVctMod = (nMagic%11)-5;            
    print( "nMagic: %d, nSpeedMod: %d, nVctMod: %d" % ( nMagic, nSpeedMod, nVctMod ) );