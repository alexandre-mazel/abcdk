# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# NaoLibrary tools
# @author The usage team - Living Labs
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

# v0.82: removing all altools: use abcdk instead

"""NaoLibrary Tools: an attempt to have Link box: some big box are not duplicate, but used from scratch from the Nao. 
See ...\git\appu_shared\library\naolibrary\all_boxes_links.crg for reference link box"""

print( "importing abcdk.naolibrary" );

import os
import time
import datetime
import mutex
import shutil
import random

import debug
import naoqitools
import pathtools

def getVersion():
    return 0.82;
# getVersion - end

def getStandardBehaviorPath():
    "return the path containing standard behavior"
    return "/home/nao/behaviors/";
# getStandardBehaviorPath - end

def getNaoLibraryPath():
    return '../naolibrary/';
# getNaoLibraryPath - end

def getLibraryName( strBehaviorName ):
    return getNaoLibraryPath() + strBehaviorName;
# getNaoLibraryPath - end

def getTotalName( strBehaviorName ):
    return getStandardBehaviorPath() + getNaoLibraryPath() + strBehaviorName;
# getNaoLibraryPath - end

def runBehavior( strBehavior, nTimeOut = 60 ):
    print( "ERROR " * 10 );
    print( "ERR: runBehavior is deprecated, use the updated box NaoLibrary-Launcher or the XarLoader class" );
    print( "ERR: you ask to load '%s'" % strBehavior );
    print( "ERROR " * 10 );
# runBehavior

def runBehavior_BM( strBehavior, nTimeOut = 60 ):
    "launch a behavior on Nao, return "" if loading failed, or the 'naoqi' name of the behavior"
    "nTimeOut: temps maximum a attendre en secondes, -1 => pas d'attente (don't wait end)"
    abm = naoqitools.myGetProxy( "ALBehaviorManager" );
    strBeName = getLibraryName( strBehavior );
    
    # comme on ne peut le charger qu'une fois, on doit toujours le stopper avant (ca stoppera un précédent)
    try:
        print( "naolibrary.runBehavior: stopping previously running (%s)" % strBehavior );
        abm.stopBehavior( strBeName );
    except:
        pass # not previously running ... not a big deal
    try:
        print( "naolibrary.runBehavior: unloading previously loaded (%s)" % strBehavior );
        abm.unloadBehavior( self.strBehaviorName );
    except:
        pass # not previously running ... not a big deal
    
    try:
        print( "naolibrary.runBehavior: loading (%s)" % strBehavior );
        abm.loadBehavior( strBeName );
    except:
        print( "naolibrary.runBehavior: can't preload behavior, version >= 1.4.32 (%s) ?" % strBehavior );
    try:
        print( "naolibrary.runBehavior: running (%s)" % strBehavior );
        abm.runBehavior( strBeName );
        rStep = 0.2;
        rTotal = 0;
        while( abm.isBehaviorRunning( strBeName ) or rTotal > nTimeOut ):
            print( "naolibrary.runBehavior: waiting '%s'... %f..." % ( strBehavior, rStep ) );
            time.sleep( rStep );
            rTotal += rStep;
    except BaseException, err:
        debug.logToChoregraphe( "naolibrary.runBehavior: error occurs: " + str( err ) );
        strBeName = "";
    print( "naolibrary.runBehavior: exiting '%s'" % ( strBehavior ) );
    return strBeName;
# runBehavior - end

def waitBehaviorEnd_BM( strBehavior, nTimeOut = 60 ):
    "Wait until the end of a previously launched behavior"
    "return False if not finished, True if finished"
    "nTimeOut: temps maximum a attendre en secondes, -1 => pas d'attente (don't wait end)" 
    
    abm = naoqitools.myGetProxy( "ALBehaviorManager" );
    rStep = 0.2;
    rTotal = 0;
    while( abm.isBehaviorRunning( strBeName ) or rTotal > nTimeOut ):
        time.sleep( rStep );
        rTotal += rStep;
    return nTotal <= nTimeOut;
# waitBehaviorEnd - end

def stopBehavior_BM( strBehavior ):
    "stop a Behavior"
    abm = naoqitools.myGetProxy( "ALBehaviorManager" );
    abm.stopBehavior( strBehavior );
# stopBehavior - end

class XarLoader:
    """ a class to load bunches of xar"""
    """ usage: """
    def __init__(self):
        self.aLoadedXar = []; # a list of [hostname, name, framemanager_id, bRunning] malheureusement la gestion du bRunning est encore insuffisante a ce niveau => un autre test doit etre ajouté dans la boite chorégraphe appellante
        self.unknown_value = -424242;
        self.logMutex = mutex.mutex();
        self.logLastTime = time.time();       
    # __init__ - end
    
    def __del__(self):
        "delete all loaded behaviors!"
        self.unloadAll();
    # __del__ - end
    
    def log( self, strMessage ):
        timeNow = time.time();
        rDurationSec = timeNow - self.logLastTime;
        self.logLastTime = timeNow;
        strTimeStamp = debug.getHumanTimeStamp();
        print( "INF: %s: Xarloader: %s" % ( strTimeStamp,  str( strMessage ) ) );
        while( self.logMutex.testandset() == False ):
            print( "INF: XarLoader: log: locked" );
            time.sleep( 0.02 );
        
        strFilename = pathtools.getCachePath() + "XarLoader.log";
        try:
            os.makedirs( pathtools.getCachePath() );
        except BaseException, err:
            print( "WRN: normal error: err: " + str( err ) );
            
        file = open( strFilename, "at" );
        file.write( "%s (%5.2fs): %s\n" % ( strTimeStamp, rDurationSec, strMessage ) );
        file.close();
        self.logMutex.unlock();
    # log - end        
    
    def unloadAll( self ):
        "unload all previously loaded behavior (gain ram, or update of behavior or ...)"
        for behav in self.aLoadedXar:
            self.log( "INF: unloadAll: erasing %s:%s" % ( behav[0], behav[1] ) );
            try: 
                fm = naoqitools.myGetProxy( "ALFrameManager", strHostName = behav[0] );
                fm.exitBehavior( behav[2] );
            except BaseException, err:
                self.log( "ERR: unloadAll: %s!" % ( err ) );
        self.aLoadedXar = []; # weird: without this line, the framemanager_id, stay valid and can be used and it works => exitBehavior ne fait rien ? (vu sur 1.7.42)
    # unloadAll - end
        
    
    def find( self, strPathAndFilenameXar, strHostName = 'localhost' ):
        "return the index in the list of loaded xar"
        "-1 if not found"
        for i in range( len(self.aLoadedXar) ):
            if( self.aLoadedXar[i][0] == strHostName and self.aLoadedXar[i][1] == strPathAndFilenameXar ):
                return i;
        return -1;
    # find - end
    
    def prepare( self, strPathAndFilenameXar, strHostName = 'localhost' ):
        "reset soft cancel and all about this behaviors"
        "usefull to do before loading or launching, because choregraphe box could be stopped while starting so flags needs to be positionned at the first moment"
        self.log( "INF: prepare: ***** %s:%s" % ( strHostName, strPathAndFilenameXar ) );
        mem = naoqitools.myGetProxy( "ALMemory", strHostName = strHostName );
        mem.raiseMicroEvent( self.getVarName_SoftCancel( strPathAndFilenameXar ), False );
    # prepare - end
    
    def load( self, strPathAndFilenameXar, strHostName = 'localhost', bForceLoading = False ):
        "load a behavior and return the framemanager id"
        "return -1 if error"
        "ATTENTION: strHostName: PAS TROP ENCORE GERE / TESTE"
        "ATTENTION: bForceLoading: PAS TROP ENCORE GERE / TESTE"
        if( not bForceLoading ):
            nNumLoadedXar = self.find( strPathAndFilenameXar, strHostName );
            if( nNumLoadedXar != -1 ):
                self.log( "INF: load: reusing previously loaded behavior %s:%s" % ( strHostName, strPathAndFilenameXar ) );
                return self.aLoadedXar[nNumLoadedXar][2];
        # already loaded - end
        try:
            fm = naoqitools.myGetProxy( "ALFrameManager", strHostName = strHostName );
        except BaseException, err:
            self.log( "ERR: load: host '%s' unreachable (%s)!" % ( strHostName, err ) );
            return -1;
        timeBegin = time.time();
        try:
            self.log( "INF: load: Loading '%s'" % strPathAndFilenameXar );
            idNew = fm.newBehaviorFromFile( strPathAndFilenameXar + "/behavior.xar", "" );
        except BaseException, err:
            self.log( "ERR: load: newBehaviorFromFile: loading '%s' failure (%s)" % ( strPathAndFilenameXar, err ) );
            raise Exception( "ERR: NaoLibrary.XarLoader: Behavior '%s' not found on your Robot (or naoqi)" % strPathAndFilenameXar );
            # return -1;

        duration = time.time() - timeBegin;
        self.log( "INF: load: %s: loading time: %fs" % ( strPathAndFilenameXar, duration ) );

        if( not bForceLoading ):
            # add it:
            self.aLoadedXar.append( [strHostName, strPathAndFilenameXar, idNew, False] );
        return idNew;
    # load - end
    
    def invalidate( self, strPathAndFilenameXar, strHostName ):
        "This behavior seems not working anymore, erasing information about it"
        "Return False if this behaviors doesn't exists"
        nNumLoadedXar = self.find( strPathAndFilenameXar, strHostName );
        if( nNumLoadedXar != -1 ):
            self.log( "INF: invalidate: invalidateing previously loaded behavior %s:%s" % ( strHostName, strPathAndFilenameXar ) );
            del self.aLoadedXar[nNumLoadedXar];
            return True;
        self.log( "ERR: invalidate: can't invalidate behavior %s:%s: not found!" % ( strHostName, strPathAndFilenameXar ) );
        return False;
    # invalidate - end
    
    def launch( self, strPathAndFilenameXar, bWaitEnd = True, strHostName = 'localhost', bForceLoading = False, rTimeOutInSec = 60*60*24*7 ):
        "launch a behavior and return the framemanager id"
        "return [id, return_value]"
        "the id has no use if bWaitEnd is true"
        "the return_value is not set if not bWaitEnd"
        "rTimeOutInSec: on pourrait peut etre mettre un temps plus court par défaut, ca serait mieux pour les tests"
        nSimulatedThreadID = random.randint( 1,10000 );
        self.log( "INF: launch: Launching %s:%s, rTimeOutInSec=%5.3f (thread:%d)" % ( strHostName, strPathAndFilenameXar, rTimeOutInSec, nSimulatedThreadID ) );
        mem = naoqitools.myGetProxy( "ALMemory", strHostName = strHostName );
#        mem.raiseMicroEvent( self.getVarName_SoftCancel( strPathAndFilenameXar ), False ); # on ne le fait pas ici, car des fois on a un stoppe, avant de rentrer dans cette méthode, donc autant le lire ici... par contre on le reinitialisera apres le comportement !         
        if( not bWaitEnd ):
            mem.raiseMicroEvent( self.getVarName_SoftCancel( strPathAndFilenameXar ), False ); # cependant dans ce cas, vu qu'on ne sera pas mis au courant de la fin de ce behavior, on ne pourra pas le remettre a False a la fin, donc il faut le mettre la
        try:
            if( mem.getData( self.getVarName_SoftCancel( strPathAndFilenameXar ) ) == True ):
                self.log( "INF: launch: Launching %s:%s - end (soft canceled before loading)(thread:%d)" % ( strHostName, strPathAndFilenameXar, nSimulatedThreadID ) );
                mem.raiseMicroEvent( self.getVarName_SoftCancel( strPathAndFilenameXar ), False ); # on le réinit pour le prochain lancement
                return [None, None];
        except:
            pass # oui cette variable peut ne pas encore exister!
        nXarID = self.load( strPathAndFilenameXar, strHostName, bForceLoading );
        if( nXarID == -1 ):
            self.log( "ERR: launch: '%s:%s' load failure" % ( strHostName, strPathAndFilenameXar, nSimulatedThreadID ) );
            return -1;
        nNumLoadedXar = self.find( strPathAndFilenameXar, strHostName );
        if( self.aLoadedXar[nNumLoadedXar][3] == True ):
            self.log( "WNG: launch: already launched: '%s:%s' => waiting a little (thread:%d)" % ( strHostName, strPathAndFilenameXar, nSimulatedThreadID ) );
            time.sleep( 1.0 ); # attend une seconde et reteste
            nNumLoadedXar = self.find( strPathAndFilenameXar, strHostName ); # refresh nNumLoadedXar
            if( self.aLoadedXar[nNumLoadedXar][3] == True ):
                self.log( "ERR: launch: already launched: '%s:%s' => skipped (thread:%d)" % ( strHostName, strPathAndFilenameXar, nSimulatedThreadID ) );
                return -1;
        self.aLoadedXar[nNumLoadedXar][3] = True;            
        mem.insertData( self.getVarName_Results( strPathAndFilenameXar ), self.unknown_value );
        mem.insertData( self.getVarName_Cancel( strPathAndFilenameXar ), False );
        try:
            if( mem.getData( self.getVarName_SoftCancel( strPathAndFilenameXar ) ) == True ):
                # on a été interrompu pendant le chargement ou  la connection d'un machin!
                self.log( "INF: launch: Launching %s:%s - end (soft canceled before launching) (thread:%d)" % ( strHostName, strPathAndFilenameXar, nSimulatedThreadID ) );
                mem.raiseMicroEvent( self.getVarName_SoftCancel( strPathAndFilenameXar ), False ); # on le réinit pour le prochain lancement
                self.aLoadedXar[nNumLoadedXar][3] = False;
                return [None, None];
        except:
            pass # oui cette variable peut ne pas encore exister!
            
            
        fm = naoqitools.myGetProxy( "ALFrameManager", strHostName = strHostName );
        try:
            self.log( "DBG: launch: before fm.playBehavior(%s) (thread:%d)" % ( str( nXarID ), nSimulatedThreadID ) );
            fm.playBehavior( nXarID );
            self.log( "DBG: launch: after fm.playBehavior(%s) (thread:%d)" % ( str( nXarID ), nSimulatedThreadID ) );
        except BaseException, err:
            self.log( "ERR: launch: while launching playBehavior on '%s': %s (thread:%d)" % ( strPathAndFilenameXar, err, nSimulatedThreadID ) );
            # self.aLoadedXar[nNumLoadedXar][3] = False; # pas la peine: on va carrément l'invalider!            
            # erasing it for next one!
            self.invalidate( strPathAndFilenameXar, strHostName );
            return [None, None];

        timeBegin = time.time();
        
        # "ATTENTION: strHostName: PAS TROP ENCORE GERE / TESTE"
        # "ATTENTION: bForceLoading: PAS TROP ENCORE GERE / TESTE"
        
        if( not bWaitEnd ):
            self.log( "INF: launch: Launching %s:%s - end (no wait end)(2) (thread:%d)" % ( strHostName, strPathAndFilenameXar, nSimulatedThreadID ) );
            return [nXarID, None];
        timeBegin = time.time();
        while( not self.isFinished( strPathAndFilenameXar, strHostName ) ):
            timeFromBegin = time.time() - timeBegin;
            print( "INF: launch: %s: waiting finish... (timeFromBegin: %5.2f, timeout: %5.2f) (thread:%d)" % ( strPathAndFilenameXar, timeFromBegin, rTimeOutInSec, nSimulatedThreadID ) );
            if( timeFromBegin > rTimeOutInSec ):
                self.log( "WNG: launch: '%s:%s': timeout (elapsed: %5.3ss) (thread:%d)" % ( strHostName, strPathAndFilenameXar, timeFromBegin, nSimulatedThreadID ) );
                break;
            time.sleep( 0.1 );

        duration = time.time() - timeBegin;
        self.log( "INF: launch: %s: executing time: %fs (thread:%d)" % ( strPathAndFilenameXar, duration, nSimulatedThreadID ) );

        # the behavior is finished
        mem.raiseMicroEvent( self.getVarName_SoftCancel( strPathAndFilenameXar ), False ); # on le réinit pour le prochain lancement
        
        returnValue = None;
        try:
            returnValue = mem.getData( self.getVarName_Results( strPathAndFilenameXar ) );
        except BaseException, err:
            debug.debug( "WNG: XarLoader.launch: return value not found for '%s:%s' (%s) (thread:%d)" % ( strHostName, strPathAndFilenameXar, err, nSimulatedThreadID ) );
        nNumLoadedXar = self.find( strPathAndFilenameXar, strHostName );
        self.aLoadedXar[nNumLoadedXar][3] = False;            
        self.log( "INF: launch: Launching %s:%s - end (return value: %s) (thread:%d)" % ( strHostName, strPathAndFilenameXar, str(returnValue), nSimulatedThreadID ) );
        return [None, returnValue];
    # launch - end
    
    def stop( self, strPathAndFilenameXar, strHostName = 'localhost' ):
        "stop a running behavior"
        "return true if the behavior was really running"
        self.log( "INF: stop: Stopping %s:%s" % ( strHostName, strPathAndFilenameXar ) );
        nNumLoadedXar = self.find( strPathAndFilenameXar, strHostName );
        if( nNumLoadedXar == -1 ):
            self.log( "WNG: stop: xar '%s:%s' is not running (perhaps currently loading - in this case, it will be stopped at the end of the loading)" % ( strHostName, strPathAndFilenameXar) );  
            # don't return there !
        try:
            mem = naoqitools.myGetProxy( "ALMemory", strHostName = strHostName );
            mem.raiseMicroEvent( self.getVarName_SoftCancel( strPathAndFilenameXar ), True );
            # pour etre sur on stoppe aussi le comportement (ca rajoute un peu plus de brutalité dans un monde de bug)
            fm = naoqitools.myGetProxy( "ALFrameManager", strHostName = strHostName );
            fm.exitBehavior( self.aLoadedXar[nNumLoadedXar][2] ); # will send a stop # mettre ici deleteBehavior si on veut liberer de la memoire (l'exit est fait dedans)            
        except BaseException, err:
            self.log( "ERR: stop: deleting '%s:%s' failure (already stopped?): err: %s" % ( strHostName, strPathAndFilenameXar, str(err) ) );
            return False;
        self.log( "INF: stop: Stopping %s:%s - STOPPED!" % ( strHostName, strPathAndFilenameXar ) );            
        return True;
    # stop - end
    

    
    def isFinished( self, strPathAndFilenameXar, strHostName = 'localhost' ):
        mem = naoqitools.myGetProxy( "ALMemory", strHostName = strHostName );
        try:
            valueResults = mem.getData( self.getVarName_Results( strPathAndFilenameXar ) );
            valueCancel = mem.getData( self.getVarName_SoftCancel( strPathAndFilenameXar ) ); # des fois le comportement appellé ne recoit pas que le softcancel a été raisé, donc on n'ajoute ici un test.
        except BaseException, err:
            debug.debug( "WNG: XarLoader.isFinished: return value not found for '%s:%s' (%s) => true" % ( strHostName, strPathAndFilenameXar, err ) );
            return True;
        bFinished = ( valueResults != self.unknown_value ) or valueCancel;
        debug.debug( "INF: XarLoader.isFinished(%s:%s): %s (current results is: %s)" % ( strHostName, strPathAndFilenameXar, str( bFinished ), str( valueResults ) ) );
        return bFinished;
    # isFinished - end

    def getVarName_Params( self, strPathAndFilenameXar ):
#        debug.debug( "getVarName_Params(%s): " % strPathAndFilenameXar );
        return strPathAndFilenameXar + "__params";
    # getVarName_Params - end

    def getVarName_InputData( self, strPathAndFilenameXar ):
#        debug.debug( "getVarName_InputData(%s): " % strPathAndFilenameXar );
        return strPathAndFilenameXar + "__input_data";
    # getVarName_InputData - end

    def getVarName_Intermediary( self, strPathAndFilenameXar ):
        return strPathAndFilenameXar + "__intermediary";
    # getVarName_Intermediary - end

    def getVarName_Results( self, strPathAndFilenameXar ):
#        debug.debug( "getVarName_Results(%s): " % strPathAndFilenameXar );
        return strPathAndFilenameXar + "__results";
    # getVarName_Results - end

    def getVarName_Cancel( self, strPathAndFilenameXar ):
        return strPathAndFilenameXar + "__cancel";
    # getVarName_Cancel - end

    def getVarName_SoftCancel( self, strPathAndFilenameXar ):
        return strPathAndFilenameXar + "__soft_cancel";
    # getVarName_SoftCancel - end
    
# class XarLoader - end

xarLoader = XarLoader(); # the XarLoader singleton


# small launcher (not very usefull)
    
def standing( bEnsureMaxStiffness = False, bEnableSecurity = True ):
    return runBehavior( getTotalName() + 'Standing' );
# standing - end