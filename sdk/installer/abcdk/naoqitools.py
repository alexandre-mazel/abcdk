
# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Naoqi tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

# this module should be called naoqi, but risk of masking with the official naoqi.py from Naoqi.

"""Naoqi specific tools"""
print( "importing abcdk.naoqitools" );

import os
import sys
import time
import datetime

import arraytools
import cache
import config
import debug
import evaltools
# import filetools # cycling include, don't include this here
# import path # non on ne peut pas inclure path, car ca fait une boucle d'inclusion
# import system # de meme
import test

try:
    import qi
except BaseException, err:
    print( "ERR: naoqitools: can't import qi" );


"we cut/paste this method here to not having to import the full module (cycle)"

def getFileContents( szFilename, bQuiet = False ):
    "read a file and return it's contents, or '' if not found, empty, ..."
    aBuf = "";
    try:
        file = open( szFilename );
    except BaseException, err:
        if( not bQuiet ):
            debug.debug( "ERR: naoqitools.getFileContents open failure: %s" % err );
        return "";

    try:
        aBuf = file.read();
    except BaseException, err:
        if( not bQuiet ):
            debug.debug( "ERR: filetools.getFileContents read failure: %s" % err );
        file.close();
        return "";

    try:
        file.close();
    except BaseException, err:
        if( not bQuiet ):
            debug.debug( "ERR: filetools.getFileContents close failure: %s" % err );
        pass
    return aBuf;
# getFileContents - end

def isOnNao():
    """Are we on THE real Nao ?"""
    szCpuInfo = "/proc/cpuinfo";
#  if not isFileExists( szCpuInfo ): # already done by the getFileContents
#    return False;
    szAllFile =  getFileContents( szCpuInfo, bQuiet = True );
    if( szAllFile.find( "Geode" ) == -1 and szAllFile.find( "Intel(R) Atom(TM)" ) == -1 ):
        return False;
    return True;
# isOnNao - end

"we cut/paste this method here to not having to import the full module (cycle)"
def getNaoqiPath():
    "get the naoqi path"
    "we cut/paste this method here to not having to import the full module (cycle)"
    s = os.environ.get( 'AL_DIR' );
    if( s == None ):
        if( isOnNao() ):
            s = '/opt/naoqi/';
        else:
            s = '';
    return s;
# getNaoqiPath - end


# import naoqi lib
strPath = getNaoqiPath();
home = `os.environ.get("HOME")`
# hard path:
# strPath = "C:/Python27/Lib/site-packages";
if strPath == "None":
  print "the environnement variable AL_DIR is not set, aborting..."
  sys.exit(1)
else:
  #alPath = strPath + "/extern/python/aldebaran"
  strPath = strPath.replace("~", home)
  strPath = strPath.replace("'", "")
  print( "INF: Using naoqi from path '%s'" % strPath );
  if( not strPath in sys.path ):
    sys.path.append(strPath);
  strPath = strPath + os.sep + "lib" + os.sep
  if( not strPath in sys.path ):
    sys.path.append(strPath);
  try:
      import naoqi
      from naoqi import ALBroker
      from naoqi import ALModule
      from naoqi import ALProxy
      bNaoqiInitialised = True;
  except BaseException, err:
      print( "ERR: abcdk.naoqitools: Can't load naoqi python module !?!, err: %s" % str( err ) );
      class ALModule:
          def __init__(self):
            self.name = "DUMB MODULE CLASS JUST TO HELP CLARIFY FURTHER INITIALISATION"
      bNaoqiInitialised = False;
#import inaoqi_d
#from naoqi_d import * # fait crasher sous windows, ca commence bien...

# import naoqi object - end




global_getNaoqiStartupTime = time.time();
def getNaoqiStartupTime():
    "return the time in seconds epoch of naoqi start (actually last altools loading)"
    global global_getNaoqiStartupTime;
    return global_getNaoqiStartupTime;
# getNaoqiStartupTime - end

global_getNaoqiStartupTimeStamp = str( datetime.datetime.now() );
global_getNaoqiStartupTimeStamp = global_getNaoqiStartupTimeStamp[0:len(global_getNaoqiStartupTimeStamp)-3]; # enleve les micro secondes!
global_getNaoqiStartupTimeStamp = global_getNaoqiStartupTimeStamp.replace( " ", "_" );
global_getNaoqiStartupTimeStamp = global_getNaoqiStartupTimeStamp.replace( ":", "m" );

def getNaoqiStartupTimeStamp():
    "return the time stamp of naoqi start (actually last altools loading) - human readable, printable, usable as a filename"
    global global_getNaoqiStartupTimeStamp;
    return global_getNaoqiStartupTimeStamp;
# getNaoqiStartupTimeStamp - end


def myGetProxy( strProxyName, bUseAnotherProxy = False, strHostName = None, bQuiet = False ):
  "redefinition of the basic getproxy, si it can work from choregraphe or from a python script"
  "bUseAnotherProxy: this proxy is used to unlock another proxy, with the same name"
  "strHostName: use another hostname, WRN: using this option will recreate a new proxy at each CALL => TODO"

  if( not config.bInChoregraphe and strHostName == None ):
      strHostName = config.strDefaultIP;
  if( bUseAnotherProxy ):
      return myGetProxyNoAddr( strProxyName, True, bQuiet = bQuiet );
  if( strHostName != None ):
      return myGetProxyWithAddr( strProxyName, strIP = strHostName, bQuiet = bQuiet );
  obj = cache.getInCache( strProxyName, ALProxy );
  if( obj != None ):
    return obj;
  obj = myGetProxyNoAddr( strProxyName, bQuiet = bQuiet );
  if( obj != None ):
    cache.storeInCache( strProxyName, obj );
  return obj;
# myGetProxy - end

def myGetProxyNoAddr( strProxyName, bUseAnotherProxy = False, bQuiet = False ):
    if( strProxyName != 'UsageRemoteTools' and not bQuiet ): # because it's a standard error!
        debug.debug( "MyGetProxyNoAddr: connecting to '%s'" % (strProxyName) );
    if( config.bInChoregraphe ):
        try:
            obj = ALProxy( strProxyName, bUseAnotherProxy );
            if( not obj or obj == None ):
                if(  not bQuiet ):
                    debug.debug( "ERR: MyGetProxyNoAddr: couldn't connect to '%s" % (strProxyName) );
                return None;
            if( strProxyName != "ALTabletService" ): # why don't we have a ping in those modules ?
                obj.ping(); # to validate the right construction
            debug.debug( "INF: MyGetProxyNoAddr: connected to '%s'" % (strProxyName) );
            return obj;
        except RuntimeError, err:
            if( strProxyName != 'UsageRemoteTools' and not bQuiet ): # because it's a standard error!
                debug.debug(  "ERR: MyGetProxyNoAddr(%s): Exception catched: %s" % ( strProxyName, err ) );
            return None;
    else:
        # print  "MyGetProxyNoAddr: method disabled";
        # return None;
        return myGetProxyWithAddr( strProxyName );
# myGetProxyNoAddr - end

def myGetProxyWithAddr( strProxyName,  strIP = None, nPort = config.nDefaultPort, bQuiet = False ):
  #debug.debug( "MyGetProxyWithAddr: connecting to '%s@%s:%d'" % (strProxyName,strIP,nPort) );
  if( strIP == None ):
      strIP = config.strDefaultIP;
  try:
    obj = cache.getInCache( strProxyName + strIP + str( nPort ), ALProxy );
    if( obj != None ):
        return obj;
    obj = ALProxy( strProxyName, strIP, nPort );
    if( strProxyName != "ALTabletService" ): # why don't we have a ping in those modules ?    
        obj.ping(); # to validate the right construction
    if( not obj or obj == None ):
      debug.debug( "ERR: MyGetProxyWithAddr: couldn't connect to '%s@%s:%d' (1)" % (strProxyName,strIP,nPort) );
      return None;
    debug.debug( "INF: MyGetProxyWithAddr: connected to '%s@%s:%d' (1)" % (strProxyName,strIP,nPort) );
    cache.storeInCache( strProxyName + strIP + str( nPort ), obj );
    return obj;
  except BaseException, err:    
    debug.debug( "ERR: MyGetProxyWithAddr(%s): Exception catched: %s" % (strProxyName,err ) );
    return None;
# myGetProxyWithAddr - end

# various tools

def launchCall( *listArgs ):
  "launch a naoqi call with a various list of argument"
  try:
    print "LaunchCall:", listArgs;
    args = listArgs[0];
    proxy = myGetProxy( args[0] );
    strFuncName = args[1];
    params = args[2];
    print( "LaunchCall: " + strFuncName + " params: " );
    print( params );
    proxy.callPython( strFuncName, *params );
    thread.exit(); # exit thread
  except BaseException, err:
    debug.debug( "MyPCall: Exception catched: %s" % err );
# launchCall - end

def myPCall( proxy, strFuncName, args ):
  try:
    listArgs = [ proxy, strFuncName, args ];
    thread.start_new_thread( LaunchCall, (listArgs,) );
    return;
  except BaseException, err:
    debug.debug( "MyPCall: Exception catched: %s" % err );
# myPCall - end

def postQueueOrders( aListOrder, nDelayBetweenOrderInSec = 0. ):
    """launch a list of naoqi command contiguously"""
    """eg: ["ALLeds = ALProxy( 'ALLeds')", "ALLeds.setIntensity( 'FaceLeds', 0.0 )","ALLeds.fadeRGB( 'FaceLeds', 0x0, 2.0 )" ] """
    def implode(strString,strElem):
        if( nDelayBetweenOrderInSec > 0. ):
            return "%s;time.sleep( %f ); %s " % ( strString, nDelayBetweenOrderInSec, strElem );
        return strString + ";" + strElem;
    strConstructedCommand = reduce( implode, aListOrder )
#    print( "strConstructedCommand: %s" % strConstructedCommand );
    evaltools.asyncEval( strConstructedCommand );
# postQueueOrders - end

class naoqiTask:
    "an interface to a naoqi task (created with pcall)"

    def __init__(self, id, strProxyName ):
        self.id = id;                                       # the naoqi ID
        self.strProxyName = strProxyName;       # the proxy that handle this task
    # __init__ - end

    def isFinished( self ):
        "is the process finished ?"
#        time.sleep( 0.05 ); # time for things to be resfreshed (join/poll or ...) # the time to create the proxy is sufficient
        proxy = myGetProxy( self.strProxyName );
        try:
            #~ proxy.wait( self.id, 1 ); # wait a minimal time
            #~ return True;
            return not proxy.isRunning( self.id );
        except:
            pass  # error => task finished
        return False;
    # isFinished - end

    def stop( self ):
        "stop the process"
        "return -1 if it hasn't been really stopped"
        proxy = myGetProxy( self.strProxyName );
        try:
            proxy.stop( self.id ); # wait a minimal time
            return isFinished();
        except:
            pass  # error => task finished or ...
        return True;
    # isFinished - end

# class naoqiTask - end


def getNaoqiVersion():
    "get the naoqi version"
    mem = myGetProxy( 'ALMemory' );
    return mem.version();
# getNaoqiPath - end

def getLibraryNameForVersion( strLibraryName, strVersion ):
    """
    "usage.so", "1.12" will return "usage_1_12_.so"
    """
    if( "1.12" in strVersion ):
        strLibraryNameNew = strLibraryName.replace( ".so", "_1_12.so" );
    elif( "1.14" in strVersion ):
        strLibraryNameNew = strLibraryName.replace( ".so", "_1_14.so" );
    elif( "1.16" in strVersion ):
        strLibraryNameNew = strLibraryName.replace( ".so", "_1_16.so" );
    elif( "1.17" in strVersion ):
        strLibraryNameNew = strLibraryName.replace( ".so", "_1_17.so" );
    elif( "1.18" in strVersion ):
        strLibraryNameNew = strLibraryName.replace( ".so", "_1_18.so" );
    elif( "1.20" in strVersion ):
        strLibraryNameNew = strLibraryName.replace( ".so", "_1_20.so" );
    elif( "1.21" in strVersion ):
        strLibraryNameNew = strLibraryName.replace( ".so", "_1_21.so" );
    elif( "1.22.4" in strVersion ):
        strLibraryNameNew = strLibraryName.replace( ".so", "_1_22_4.so" );
    elif( "1.22.3" in strVersion ):
        strLibraryNameNew = strLibraryName.replace( ".so", "_1_22_3.so" );
    elif( "1.22.2" in strVersion ):
        strLibraryNameNew = strLibraryName.replace( ".so", "_1_22_2.so" );
    elif( "1.22.1" in strVersion ):
        strLibraryNameNew = strLibraryName.replace( ".so", "_1_22_1.so" );
    elif( "1.22" in strVersion ):
        strLibraryNameNew = strLibraryName.replace( ".so", "_1_22.so" );
    elif( "2.0.3" in strVersion ):
        strLibraryNameNew = strLibraryName.replace( ".so", "_2_0_3.so" );
    elif( "2.0.2" in strVersion ):
        strLibraryNameNew = strLibraryName.replace( ".so", "_2_0_2.so" );
    elif( "2.0" in strVersion ):
        strLibraryNameNew = strLibraryName.replace( ".so", "_2_0.so" );
    elif( "2.2" in strVersion ):
        strLibraryNameNew = strLibraryName.replace( ".so", "_2_2.so" );        
    elif( "2.1" in strVersion ):
        strLibraryNameNew = strLibraryName.replace( ".so", "_2_1.so" );
    else:
        strLibraryNameNew = strLibraryName;
    return strLibraryNameNew;
# getLibraryNameForVersion - end

def findLibraryNameForVersion( strLibraryName, strVersion, astrPossiblePath = ["./"] ):
    """
    find in a path the good library for some version, is one library isn't present, it will take older one.
    return the total path and filename or "" if noone is found
    - astrPossiblePath: possible path to look for by preference WRN: before it was just a string and not an array so you should change your call to enclosed your script with brackets (sorry)
    """
    print( "INF: naoqitools.findLibraryNameForVersion( '%s', '%s', '%s' )" % ( strLibraryName, strVersion,  astrPossiblePath ) );
    if( "1.14" in strVersion ): # 1.22, 1.22.1 and 1.22.2 have different linkage... shame on us...
        strVersion = strVersion[:4]; # so 1.14.5 => 1.14
    aListVersion = ["1.10", "1.12", "1.14", "1.17", "1.18", "1.20","1.21", "1.22", "1.22.1", "1.22.2", "1.22.3", "1.22.4", "2.0", "2.0.2", "2.0.3", "2.0.4","2.1", "2.1.0", "2.1.1", "2.2"]; # we skip 1.16 because it's too different from 1.17 and 1.14
    strPrevVersion = strVersion;
    while( True ):
        for strPath in astrPossiblePath:
            strPathAndLibraryName = strPath + strLibraryName;
            strLibraryNameNew = getLibraryNameForVersion( strPathAndLibraryName, strPrevVersion );
            print( "DBG: naoqitools.findLibraryNameForVersion: trying: %s" % strLibraryNameNew );
            if( os.path.exists( strLibraryNameNew ) ):
                print( "INF: naoqitools.findLibraryNameForVersion: You ask for %s, and we will use version %s found there: '%s'" % (strVersion, strPrevVersion, strLibraryNameNew ) );
                return strLibraryNameNew;
        try:
            nIdxVersion = aListVersion.index( strPrevVersion );
            print( "nIdxVersion: %d" % nIdxVersion );
        except IndexError, err:
            print( "DBG: launch: %s"  % err );
            nIdxVersion = -1;
        if( nIdxVersion > 0 ):
            strPrevVersion = aListVersion[nIdxVersion-1];
            print( "INF: naoqitools.findLibraryNameForVersion: downgrading: trying with version: '%s'" % strPrevVersion );
        else:
            return "";
        # while - end
    strLibraryNameNew = astrPossiblePath[0] + strLibraryName;
    print( "INF: naoqitools.findLibraryNameForVersion: No version lib found for '%s', returning default name: '%s'" % (strVersion, strLibraryNameNew ) );
    return strLibraryNameNew;
# findLibraryNameForVersion - end

def launch( strModuleName, strLibraryName = "", bHandleMultiVersion = False, strCustomPath = "", strLauncherName = "ALLauncher" ):
    """"
    Ensure a proxy is running, or launch it if not running.
    Return False if not loaded and loading fail
    - strCustomPath: user specific path (choregraphe project content...)
    """
    strLibraryPathDefault = "/usr/lib/naoqi/";
    strUserPathDefault = "/home/nao/.local/lib/";
    try:
        launcher = myGetProxy( strLauncherName );
    except BaseException, err:
        print( "WRN: naoqitools.launch: can't connect to ALLauncher: '%s', trying ALLauncher_cogito..." % err );
        launcher = myGetProxy( "ALLauncher_cogito" );
    if( not launcher.isModulePresent( strModuleName ) ):
        if( bHandleMultiVersion ):
            strVersion = getNaoqiVersion();
            strLibraryName = findLibraryNameForVersion( strLibraryName, strVersion, [strCustomPath, strUserPathDefault, strLibraryPathDefault] ); # we wish there are the same on local and where to launch them (romeo)
        print( "INF: naoqitools.launch: Loading '%s'" % strLibraryName );
        if( not os.path.exists( strLibraryName ) ):
            strLibraryName = strLibraryPathDefault + strLibraryName;
        print( "INF: launching: library '%s'" % strLibraryName );
        aModuleList = launcher.launchLocal( strLibraryName );
        print( "INF: naoqitools.launch: new module loaded: " + str( aModuleList ) );

        # seems to failt on last version ... should be test.. but not now
        #if( not launcher.isModulePresent( strModuleName ) ):
        #    print("MODULE NOT PRESENT>..")
        #    # raise RuntimeError( "ERROR: The loading of '%s' has failed" % strLibraryName );
        #    return False;
    return True;
# launch - end

def isMethodExist( strProxyName, strMethodName ):
    """
    Return true if the method exists in that module
    """
    try:
        p = myGetProxy( strProxyName );
        p.getMethodHelp( strMethodName ); # we could make a if in getMethodList, but what if the method is hidden ?
        return True;
    except:
        pass
    return False;
# isMethodExist - end

def getMemoryData( strName, defaultValue = None ):
    """
    return a data from ALMemory with some specific default value when not found
    """
    try:
        mem = myGetProxy( "ALMemory" );    
        return mem.getData( strName );
    except BaseException, err:
        print( "WRN: abcdk.naoqitools.getMemoryData: access to data '%s' return default: %s (err:%s)" % (strName, str(defaultValue), err ) );
    return defaultValue;
# getMemoryData - end


class MemorySubscriber(ALModule):
    """
    Use this object to get call back from the ALMemory of the naoqi world.
    Your callback needs to be a method with two parameter (variable name, value).

    """

    def __init__( self, strModuleName ):
        #~ print( "DBG: abcdk.MemorySubscriber.__init__: strModuleName: %s" % str(strModuleName) );
        try:
            ALModule.__init__(self, strModuleName );
        except BaseException, err:
            print( "ERR: abcdk.MemorySubscriber: init error (1): %s" % str(err) );
            
        try:            
            self.BIND_PYTHON( self.getName(),"callback" );
            self.mem = myGetProxy( "ALMemory" );
            self.pb = myGetProxy( "ALPythonBridge" );
        except BaseException, err:
            print( "ERR: abcdk.MemorySubscriber: init error (2): %s" % str(err) );
        self.dictRegister = list(); # a list of [strMemoryKeyname, strMethodToCall, in a naoqi or not?] # TODO: multi register to same variable
        #~ print( "DBG: abcdk.MemorySubscriber.__init__: self.mem: %s" % str(self.mem) );

    # __init__ - end
    def __del__( self ):
        print( "INF: abcdk.MemorySubscriber.__del__: cleaning everything" );
        ALModule.__del__(self)
        tempList = arraytools.dup( self.dictRegister );
        for registered in tempList:
            self.unregister( registered[0], registered[1] );
        print( "INF: abcdk.MemorySubscriber.__del__: cleaning everything - end" );

    def register( self, strMemoryKeyname, strMethodToCall ):
        """
        register to an event
        """
        print( "INF: abcdk.MemorySubscriber.register: change on '%s' will call '%s'" % ( strMemoryKeyname, strMethodToCall ) );
        # first of it, we create the data, so that, it won't throw an error
        if( hasattr( self, "mem" ) and self.mem != None ):
            self.mem.raiseMicroEvent( strMemoryKeyname, None );
            self.mem.subscribeToMicroEvent( strMemoryKeyname, self.getName(), strMethodToCall, "callback" );
            self.dictRegister.append( [strMemoryKeyname, strMethodToCall] );
        else:
            print( "ERR: abcdk.MemorySubscriber.register: can't register: no mem proxy! ( '%s' => '%s')" % ( strMemoryKeyname, strMethodToCall ) );
    # register - end

    def unregister( self, strMemoryKeyname, strMethodToCall ):
        """
        stop hearing for that event
        """
        print( "INF: abcdk.MemorySubscriber.unregister: change on '%s' won't call '%s' anymore" % (strMemoryKeyname, strMethodToCall ) );
        self.mem.unsubscribeToMicroEvent( strMemoryKeyname, self.getName() ); # bad: when subscribing twice to the same variable, removing one is removing the other one (TODO: just cut the link)

        try:
            idx = self.dictRegister.index( [strMemoryKeyname, strMethodToCall] );
            del self.dictRegister[idx];
        except ValueError, err:
            print( "DBG: abcdk.MemorySubscriber.unregister: find error for (%s,%s)" % ( strMemoryKeyname, strMethodToCall ) );

    # unregister - end

    def callback(self, pDataName, pValue, pObjectToCallback ):
        #print( "callback: %s, %s, %s" % ( pDataName, pValue, pObjectToCallback ) );
        if( '.' in pObjectToCallback ):
            listObject = pObjectToCallback.split( "." );
            strObjectName = listObject[len(listObject)-2];
            strCall = "global %s;\n%s('%s',%s)" % ( strObjectName, pObjectToCallback, pDataName, str(pValue) );
        else:
            strCall = "global %s;\n%s('%s',%s)" % ( pObjectToCallback, pObjectToCallback, pDataName, str(pValue) );
        #~ print( "evaluating this: '%s'" % strCall );
        #~ eval( strCall, globals(), locals() );
        try:
            self.pb.eval( strCall );
        except BaseException, err:
            print( "ERR: abcdk.MemorySubscriber: while callbacking '%s': err: %s" % (strCall, str(err) ) );
    # callback - end
    
    def __str__( self ):
        strOut = "MemorySubscriber: dictRegister:\n" + str(self.dictRegister)
        return strOut
        
# MemorySubscriber - end

# JBE : a small patch to avoid create a module
# if we don't have a broker !
if( os.name == 'posix' ): # permits to deactivate those lines for quick testing when on my windows computer
    try:
        memorySubscriber = MemorySubscriber( "memorySubscriber" ); # make it global to the python wolrd
        # make it really global to every body from naoqi world
        # __builtins__["memorySubscriber"] = memorySubscriber; # doesn't work
        # global memorySubscriber;
        if( bNaoqiInitialised ):
            tempPythonBridge = myGetProxy( "ALPythonBridge" );
            tempPythonBridge.eval( "from abcdk.naoqitools import memorySubscriber" );
    except RuntimeError, err:
        print( "WRN: abcdk.naoqitools: no broker found or new error, err: %s" % str( err ) );
        #~ memorySubscriber = None;
    except AttributeError, err:
        print( "WRN: abcdk.naoqitools: errors occurs, err: %s" % str( err ) );

def subscribe( strMemoryKeyname, strMethodToCall ):
    """
    Subscribe a callback to ALMemory from outside naoqi world (but just in python).
    - strMethodToCall: the method to call, it should be a two parameter (variable name, value).
        eg: def onBumper( self, strVariableName, rVal ):
        see bodytalk.py or obstacles.py for use case
    """
    memorySubscriber.register( strMemoryKeyname, strMethodToCall );
# subscribe - end

def unsubscribe( strMemoryKeyname, strMethodToCall ):
    """
    cf subscribe
    """
    memorySubscriber.unregister( strMemoryKeyname, strMethodToCall );
# subscribe - end

def getALMemoryPlugClassDescription( strMemoryName ):
    strCode = """pass
import naoqi
class ALMemoryPlug(naoqi.ALModule):
    "Use this object to create an ALMemory plug for compatibility usage"

    def __init__( self, strModuleName ):
        try:
            naoqi.ALModule.__init__(self, strModuleName );
            memExt = naoqi.ALProxy( "MEMORY_NAME" );
            listMethods = memExt.getMethodList();
            for strMethod in listMethods:
                print( "ERR: abcdk.naoqitools.ALMemoryPlug: adding the method '%s'" % strMethod );
                self.BIND_PYTHON( self.getName(), strMethod );
                setAttr( self, strMethod, "bouchon" );
        except BaseException, err:
            print( "ERR: abcdk.naoqitools.ALMemoryPlug: loading error: %s" % str(err) );

    # __init__ - end
    def __del__( self ):
        print( "INF: abcdk.naoqitools.ALMemoryPlug.__del__: cleaning everything" );

    # those two methods doesn't works as method_missing is already done in parent caller...
    def __getattr__(self, name):
            def _missing(*args, **kwargs):
                print "A missing method was called."
                print "The object was %r, the method was %r. " % (self, name)
                print "It was called with %r and %r as arguments" % (args, kwargs)

            return _missing;

    def method_missing( self, *args, **kwargs ):
        print( "ma method missing" );

    def bouchon( self, *args, **kwarg ):
        print( "%r, and %r " % ( args, kwargs ) );
        #~ return memExt.name truc truc

# class FakeALLeds - end
    """;
    strCode = strCode.replace( "MEMORY_NAME", strMemoryName );
    return strCode;
# getALMemoryPlugClassDescription - end

def installALMemoryPlug():
    """
    on Romeo, for instance, sometimes we don't have any ALMemory module.
    So we create this one sending all the command to another ALMemory

    Return: True if installed or False if already install or no need to have

    To test from a python interactive session:
import abcdk.config
abcdk.config.bInChoregraphe=False
import abcdk.naoqitools
abcdk.naoqitools.installALMemoryPlug()
mem = abcdk.naoqitools.myGetProxy( "ALMemory", "localhost", 9559 )
pb = abcdk.naoqitools.myGetProxy( "ALPythonBridge_audio", "localhost", 9559 )

or manually (sur audio):

import abcdk.naoqitools
reload( abcdk.naoqitools )
strCode = abcdk.naoqitools.getALMemoryPlugClassDescription( "ALMemory_audio" );
exec strCode
ALMemory = ALMemoryPlug( "ALMemory" ) # could not create a module, as there is no current broker in Python's world.



    """
    print( "INF: abcdk.naoqitools.installALMemoryPlug: starting..." );
    mem = myGetProxy( "ALMemory" );
    if( mem != None ):
        #~ return False;
        pass

    print( "INF: abcdk.naoqitools.installALMemoryPlug: looking for existing ALMemory..." );
    listPossibleName = [ "ALMemory_audio", "ALMemory_video", "ALMemory_motion" ];
    #~ listPossibleName = ["ALLauncher", ""];
    for strMemoryName in listPossibleName:
        memExt = myGetProxy( strMemoryName );
        if( memExt != None ):
            break;
    else:
        print( "ERR: abcdk.naoqitools.installALMemoryPlug: no ALMemory_xxx found" );
        return False;



    print( "INF: abcdk.naoqitools.installALMemoryPlug: Translating to '%s'" % strMemoryName );
    strPostFix = strMemoryName[strMemoryName.find("_")+1:];
    print( "INF: abcdk.naoqitools.installALMemoryPlug: Current Method in '%s': %s" % (strMemoryName, memExt.getMethodList() ) );

    strCode = getALMemoryPlugClassDescription( strMemoryName );
    pb = myGetProxy( "ALPythonBridge_" + strPostFix );
    print( "INF: abcdk.naoqitools.installALMemoryPlug: Installing code in the PythonBridge..." );
    retEval = pb.eval( strCode );
    print( "DBG: abcdk.naoqitools.installALMemoryPlug: ret eval: %s" % retEval );
    pb.eval( "ALMemory = ALMemoryPlug( 'ALMemory' )" );
    print( "INF: abcdk.naoqitools.installALMemoryPlug: done..." );
# installALMemoryPlug - end


def registerObjectAsService(strServiceName="ABCDK_NONE_SERVICE", theObject=None, bForce=False):
    """
    Create a service using naoqi2 stuff

    :param: bForce unsubscribe to service if allready present
    """
    strMinQiVersion = '2.0.0.14'
    if not(hasattr(qi, '__version__')) or qi.__version__ < strMinQiVersion:
        if hasattr(qi, '__version__'):
            strCurrentVersion = qi.__version__
        else:
            strCurrentVersion = "Unknowned"
        print("abcdk.naoqitools.registerObjectAsService: this functionnality is available only in naoqi-sdk > %s, your version is %s" % (strMinQiVersion, strCurrentVersion))
        return
    #app = qi.Application()
    session = qi.Session()
    import config
    strUri = "".join(["tcp://", config.strDefaultIP, ":", str(config.nDefaultPort)])
    try:
        session.connect(strUri)
    except:
        print("failed to connect to %s" % strUri)
        return
    if bForce:
        aListServices = session.services()
        aServicesToStop = [service for service in aListServices if service['name'] == strServiceName]  # it's a dict only in last naoqi version qi > 2.0.0.14
        for service in aServicesToStop:
            print("Unregistering services %s (id: %s)" % (service['name'], service['id']))
            session.unregisterService(service['id'])
    session.registerService(strServiceName, theObject)
    print("abcdk.naoqitools.registerObjectAsService: service is registered as %s" % strServiceName)
    #qi.async(app.run) # we run it in background using async
    print("has been run in background")
    time.sleep(2)
    print("fin du time sleep")
    return session

def test_registerObjectAsService():
    import config
    config.bInChoregraphe = False
    config.strDefaultIP = "10.2.1.75"
    class Test(object):
        def plop(self):
            print self
    a =  Test()
    registerObjectAsService(strServiceName="ALTEST", theObject=a)
    registerObjectAsService(strServiceName="ALTEST", theObject=a, bForce=True)
    registerObjectAsService(strServiceName="ALTEST", theObject=a, bForce=True)


######## callback test
def callbackTest( value ):
    print( "callbackTest: %s" % str( value ) );
######## callback test - end

def isVariableInMemory( strVariableName, strSpecificProxyName = "ALMemory" ):
    try:
        mem = myGetProxy( strSpecificProxyName );
        d = mem.getType( strVariableName );
        return True;
    except BaseException, err:
        pass
    return False
# isVariableInMemory - end

def autoTest():
    if( test.isAutoTest() ):
        test.activateAutoTestOption();
        postQueueOrders( ["import naoqitools", "ALLeds = naoqitools.myGetProxy( 'ALLeds')", "ALLeds.setIntensity( 'FaceLeds', 1.0 )","ALLeds.fadeRGB( 'FaceLeds', 0xFF, 2.0 )" ] );
        subscribe( "FrontTactilTouched", "naoqitools.callbackTest" );
# autoTest - end

if( __name__ == "__main__" ):
    autoTest();

print( "importing abcdk.naoqitools - end" );
