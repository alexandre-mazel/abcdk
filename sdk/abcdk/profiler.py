# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Profiler tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Profiler tools"""
print( "importing abcdk.profiler" );

import time

import debug
import naoqitools


def profile_this(fn):
    """ 
    just a profile command to use as a decorator 
    from profiler import profile_this
    @profile_this
    def MaFunction()
    """
    import time
    import cProfile
    def profiled_fn(*args, **kwargs):
        strCurTime = time.strftime("%Y%m%d-%Hh%M")
        fpath = fn.__name__ + strCurTime + ".profile"
        prof = cProfile.Profile()
        ret = prof.runcall(fn, *args, **kwargs)
        prof.dump_stats(fpath)
        return ret
    return profiled_fn


def getBoxConstantName( strPathBoxName ):
    "extract from a long choregraphe name, a short name"
    "eg: ALFrameManager__0xad95c6c0__root__TestBattery_4  => TestBattery_4"
    strPick = "__root";
    nPos = strPathBoxName.find( strPick );
    return "Box_" + strPathBoxName[nPos+len(strPick)-4:];
# getBoxConstantName - end

#~ print( getBoxConstantName( "ALFrameManager__0xad95c6c0__root" ) );
#~ print( getBoxConstantName( "ALFrameManager__0xad95c6c0__root__TestBattery_4" ) );

def startBox( strBoxName ):
    up = naoqitools.myGetProxy( "UsageProfiler" );
    up.startMeasure ( getBoxConstantName( strBoxName ), "", "", 0 );
# startBox - end
    
def stopBox( strBoxName ):
    up = naoqitools.myGetProxy( "UsageProfiler" );
    up.stopMeasure( getBoxConstantName( strBoxName ), "", "", 0 );
# startBox - end

class UsageProfilerHelper:
    "A small helper to use UsageProfiler"
    "just create it in some methods"
    def __init__( self, pstrModuleName, pstrFunctionName = "",  pstrTaskName = "" ):
        self.up = naoqitools.myGetProxy( "UsageProfiler" );
        self.strModuleName = pstrModuleName;
        self.strFunctionName = pstrFunctionName;
        self.strTaskName = pstrTaskName;
        self.up.startMeasure( pstrModuleName, pstrFunctionName, pstrTaskName, -1 );
    # __init__ - end
    
    def __del__( self ):
        self.up.stopMeasure( self.strModuleName, self.strFunctionName, self.strTaskName );
    # __del__ - end
    
    #~ def idle( self ):
        #~ "fait croire au systme que l'objet est utilisé est donc qu'il ne faut pas le garbager tout de suite"
        #~ if( self.up == 421 ): # impossible...
            #~ self.strModuleName = "pipi";
    #~ # idle - end        
    
# class UsageProfilerHelper - end

def UsageProfilerHelperBox( strBoxName ):
    "use UsageProfilerHelper in a choregraphe box"
    return UsageProfilerHelper( getBoxConstantName( strBoxName ) );
# startBox - end

class TimeMethod:
    "mesure the time taken by a method - another implementation of a profiler, in pure python"
    "Use: define an object TimeMethod in your method, and that's all!"
    def __init__(self, strOptionnalLibelle = "" ):
        "Create the object"
        self.reset( strOptionnalLibelle );
    # __init__ - end
    
    def reset( self, strOptionnalLibelle = "" ):
        "reset the object"
        self.strCaller = debug.getFileAndLinePosition( 2 ); # callstack: reset, __init__, caller
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

class Fps:
    "mesure the frequency of an event"
    "Use: define an object Fps in your method, and that's all!"
    def __init__(self ):
        "Create the object"
        self.reset();
    # __init__ - end
    
    def reset( self ):
        "reset the object"
        self.nCount = 0;
        self.begintime = time.time();
    # reset - end
    
    def newFrame( self ):
        "add a new frame to count"
        self.nCount += 1;
    # newFrame - end
    
    def getCurrent( self ):
        return self.nCount / (time.time() - self.begintime);
    # getCurrent - end

    def printAndReset( self ):
        print( "fps: %5.2f" % self.getCurrent() );
        self.reset();
    # getCurrent - end
    
    def update( self ):
        "call it each frame, and it will do everything: from time to time: auto print and reset"
        self.newFrame();
        if( self.nCount > 0 and time.time() - self.begintime > 3 ):
            self.printAndReset();
    # update - end
# class Fps - end


def testFps():    
    "test fps class"
    fps = Fps();
    for i in range( 3 ):
        fps.newFrame();
        time.sleep( 0.2 );
    print( fps.getCurrent() ); # should be something like 5 fps
    fps.printAndReset();
    fps.newFrame();
    time.sleep( 0.5 );
    fps.printAndReset(); # should print 2    
    for i in range( 2 ):
        fps.update();
        time.sleep( 0.2 );    
    assert fps.getCurrent() > 4.8 and fps.getCurrent() < 5.2;
# testFps - end

class PeriodManager:
    "compute statistics about some events"
    def __init__(self ):
        "Create the object"
        self.reset();
    # __init__ - end
    
    def reset( self ):
        "reset the object"
        self.dictPeriod = dict(); # all handled statistics, for each stats name, a total time, a number of occurence, a min time, a max time, and a last time occurs (for event)
    # reset - end
    
    def addStat( self, strName, rTimeSec ):
        "call it after for each measured period"
        if( not strName in self.dictPeriod.keys() ):
            self.dictPeriod[strName] = [0.,0,10000.,0., False];
        prev = self.dictPeriod[strName];
        if( prev[2] > rTimeSec ):
            prev[2] = rTimeSec;
        if( prev[3] < rTimeSec ):
            prev[3] = rTimeSec;
        prev[1] += 1;
        prev[0] += rTimeSec;
        self.dictPeriod[strName] = prev;
    # addStat - end

    def addStatEvent( self, strName, rCurrentTime ):
        "call it each time an event occurs"        
        if( not strName in self.dictPeriod.keys() ):
            self.dictPeriod[strName] = [0.,0,10000.,0., False];
        # measure elapsed        
        prev = self.dictPeriod[strName];
        if( prev[4] != False ):
            rElapsed = rCurrentTime - prev[4];
            self.addStat( strName, rElapsed );
        self.dictPeriod[strName][4] = rCurrentTime;
    # addStatEvent - end        
    
    def __str__( self ):
        strOut = "";
        for k,v in sorted(self.dictPeriod.iteritems()):
            nNbrTimes = v[1];
            if( nNbrTimes > 1 ):
                strPlural = "s";
            else:
                strPlural = " ";
            strOut += "%-40s - %d call%s:  med: %.3fs,  min: %.3fs,  max: %.3fs,   total: %.3fs\n" % ( k, nNbrTimes, strPlural, v[0]/nNbrTimes, v[2], v[3], v[0] );
        return strOut;
    # __str__ - end
    
# class PeriodManager - end

periodManager = PeriodManager();
    
class PeriodInner:
    "mesure the period of a method"
    "Use: define an object Period in your method, and that's all!"
    "This object is the auto-object to use in your code"
    "To draw statistic on it, call print periodManager"
    def __init__( self, strName ):
        "Create the object"
        self.strName = strName;
        self.reset();
    # __init__ - end
    
    
    def reset( self ):
        "reset the object"
        #~ self.nCount = 0;
        self.begintime = time.time();
        self.bStopped = False;
    # reset - end
    
    def __del__(self ):
        "Create the object"
        self.end();
    # __del__ - end    
    
    def end( self ):
        if( self.bStopped ):
            return;
        self.bStopped = True;
        rElapsed = time.time() - self.begintime;
        periodManager.addStat( self.strName, rElapsed );
    # end - end    
# class PeriodInner - end

class PeriodEvent:
    "mesure the period of a frequent event"
    "Use: define an object Period in your method, and that's all!"
    "This object is the auto-object to use in your code"
    "To draw statistic on it, call print PeriodManager"
    def __init__( self, strName ):
        "Create the object"
        self.strName = strName;
        periodManager.addStatEvent( self.strName, time.time() );
    # __init__ - end
# class PeriodEvent - end

def testPeriodInner():
    p1 = PeriodInner("p1");
    time.sleep( 1. );
    p2 = PeriodInner("p2");
    time.sleep( 2. );
    p3 = PeriodInner("p2");
    time.sleep( 0.5 );
    event1 = PeriodEvent( "ev1" );
    event2 = PeriodEvent( "ev1" );
    event3 = PeriodEvent( "ev2" );
# testPeriodInner - end
    
def testPeriod():
    event1 = PeriodEvent( "ev2" );    
    testPeriodInner();
    print( "PeriodManager: state:\n" + str( periodManager ) );
# testPeriod - end    

#~ timer = TimeMethod( "coucou" );
#~ time.sleep( 1 );
#~ timer.setIntermediate( "compute" );
#~ time.sleep( 4 );
#~ timer.setIntermediate( "draw" );
#~ time.sleep( 3 );
#~ timer.stopAndPrint();

# testFps();
# testPeriod();
