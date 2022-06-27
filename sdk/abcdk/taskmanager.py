# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Taskmanager tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Tasklist tools"""
print( "importing abcdk.taskmanager" );

import time
import datetime
import random

import filetools
import pathtools
import speech

def getDateTime( strDate, strTime ):
    "convert strings in datetime, using today+now as an implicit reference"
    "strDate: YYYY/MM/DD or MM/DD or DD or empty (for "
    "strTime: HH:MM:SS with HH in [0,23[ or HH:MM or HH"    
    "return a filled datetime structure"
    dt = datetime.datetime.now();
    
    dt = dt.replace( microsecond = 0 ); # we want to be at 0 microsecond
    
    # decode date
    datedecoded = strDate.split( "/" );
    if( len( datedecoded ) > 2 ):
        # dt.day = int( datedecoded[2] );
        dt = dt.replace( day = int( datedecoded[2] ) );
    if( len( datedecoded ) > 1 ):
        # dt.month = int( datedecoded[1] );
        dt = dt.replace( month = int( datedecoded[1] ) );
    if( len( datedecoded ) > 0 and len( datedecoded[0] ) > 0 ):
        # dt.year = int( datedecoded[0] );
        dt = dt.replace( year = int( datedecoded[0] ) );
        
    # decode time
    timedecoded = strTime.split( ":" );
    if( len( timedecoded ) > 2 ):
        # dt.second = int( timedecoded[2] );
        dt = dt.replace( second = int( timedecoded[2] ) );
    else:
        dt = dt.replace( second = 0 ); # default is 0 second
    if( len( timedecoded ) > 1 ):
        # dt.minute = int( timedecoded[1] );
        dt = dt.replace( minute = int( timedecoded[1] ) );
    else:
        # default is in 10 minutes
        dt = dt.replace( minute = 10 );
    if( len( timedecoded ) > 0 and len( timedecoded[0] ) > 0 ):
        # dt.hour = int( timedecoded[0] );
        dt = dt.replace( hour = int( timedecoded[0] ) );        
        
#    print( "%s,%s => %s" % ( strDate, strTime , str( dt ) ) );
    
    return dt;
# getDateTime - end


class Task:
    
    eRepeatNone = 0;
    eRepeatDaily = 1;
    eRepeatWeekly = 2;
    eRepeatMonthly = 3;
    eRepeatYearly = 4;
    
    def __init__( self ):
        "create a new task"
    # __ init__
    
    def set( self, strName, strDate, strTime, nRepeatType = eRepeatNone ):
        "set a new task from external program"
        "strDate: YYYY/MM/DD or MM/DD or DD or empty (for "
        "strTime: HH:MM:SS with HH in [0,23[ or HH:MM or HH"
        self.strName = strName; # name of the task
        self.datetime = getDateTime( strDate, strTime ); # WARNING: month is [1,12]
        self.nRepeatType = nRepeatType;
        self.lastExecuted = False; # False or some datetime object (to check if we must bother user for this task)
    # set - end
    
    def read( self, strFilename ):
        "read known task from disk"
        try:
            file = open( strFilename, "r" );
        except:
            file = False;
        if( not file ):
            print( "WRN: Task.read no task info in '%s'" % ( strFilename ) );
            return False;
        self.strName, self.datetime, self.nRepeatType, self.lastExecuted = eval( file.read() );
        file.close();
        print( "INF: Task.read: '%s': date: %s, repeat: %d, last: %s" % ( self.strName, str( self.datetime ), self.nRepeatType, str( self.lastExecuted ) ) );
        return True;
    # read - end
    
    def write( self, strFilename ):
#        print( "INF: User.write" );
        file = open( strFilename , "w" );
        file.write( str( [self.strName, self.datetime, self.nRepeatType, self.lastExecuted ] ) );
        file.close();
#        print( "INF: User.write - end" );
        return True;
    # write - end
    
    def _incrementTaskDueToPeriodicity( self ):
        if( self.nRepeatType == Task.eRepeatYearly ):
            self.datetime.year += 1;
            
        elif( self.nRepeatType == Task.eRepeatMonthly ):
            self.datetime.month += 1;
            if( self.datetime.month > 12 ):
                self.datetime.month = 1;
                self.datetime.year += 1;
                
        elif( self.nRepeatType == Task.eRepeatWeekly ):
            # self.datetime.day += 7;
            self.datetime += datetime.timedelta( 7 );
            
        elif( self.nRepeatType == Task.eRepeatDaily ):
            # self.datetime.day += 1;
            self.datetime += datetime.timedelta( 1 );
    # _incrementTaskDueToPeriodicity - end
    
        
# class Task - end

class TaskManager:
    
    def __init__( self ):
        "create a new task manager"
        strDir = pathtools.getCachePath() + "task/";
        filetools.makedirsQuiet( strDir );
        self.strFilenameTemplate = strDir + "%05d.dat";
        self.listTask = [];
        self.read();
    # __init__ - end
    
    def __del__( self ):
        self.write();
    # __del__ - end
    
    def read( self ):
        "read task from disk"

        self.listTask = []; # reset();
        
        bEnd = False;
        nNumTask = 1;

        while( not bEnd ):
            newTask = Task();
            if( not newTask.read( self.strFilenameTemplate % nNumTask ) ):
                bEnd = True;
            else:
                self.listTask.append( newTask );
            nNumTask += 1;            
        print( "INF: TaskManager.read: %d task(s) loaded." % len( self.listTask ) );
    # read - end
    
    def write( self ):
        "write user to disk"

        print( "INF TaskManager.write: writing %d task(s)." % len( self.listTask ) );

        bEnd = False;
        nNumTask = 1;

        for i in range( len( self.listTask ) ):
            self.listTask[i].write( self.strFilenameTemplate % nNumTask );
            nNumTask += 1;            
    # write - end
    
    def addTask( self, strName, strDate, strTime, nRepeatType = Task.eRepeatNone ):
        "add some task"
        newTask = Task();
        newTask.set( strName, strDate, strTime, nRepeatType );
        
        # TODO: check duplicate !!!
        
        
        diffTime = newTask.datetime - datetime.datetime.now();
        diffSec = (diffTime.microseconds + (diffTime.seconds + diffTime.days * 24 * 3600) * 10**6) / 10**6;
        if( diffSec < 0 and newTask.nRepeatType != Task.eRepeatNone ):
            # task is in the past, we increment the task
            print( "WRN: TaskManager.addTask: task '%s' is in the past, incrementing task using to peridocity" % newTask.strName );
            newTask._incrementTaskDueToPeriodicity();
        
        self.listTask.append( newTask );
        
        # check results
        newTask = self.listTask[-1];
        print( "INF: TaskManager.addTask: added task: '%s', '%s', repeat: %d" % ( newTask.strName, str( newTask.datetime ), newTask.nRepeatType ) );
        
        self.sort(); # we should sort there !
        self.write();
    # addTask - end
    
    def getNextTasks( self, nIntervalInSec = -1, bKeepOld = True,  bKeepDone = False ):
        "get next task"
        "nIntervalInSec: interval containing task (-1: unlimited/all)"
        "bKeepOld: when set, output even if older than 10 min ago"
        "bKeepDone: when set, output even if the task has been made"
        "return an array of couple [idx_task, sentence to say]"
        
        listOut = [];
        timeCurrent = datetime.datetime.now();
        for i in range( len( self.listTask ) ):
            diffTime = self.listTask[i].datetime - timeCurrent;
            # diffSec = diffTime.total_seconds(); # New in version 2.7.
            diffSec = (diffTime.microseconds + (diffTime.seconds + diffTime.days * 24 * 3600) * 10**6) / 10**6;
            # print( "diffTime: '%s': %s (%d sec)" % ( self.listTask[i].strName, str( diffTime ),  diffSec ) );
            
            if( diffSec < -10*60 and not  bKeepOld ):
                continue;
                
            if( diffSec > nIntervalInSec and not nIntervalInSec == -1 ):
                continue;
                
            if( not bKeepDone ):
                if( self.listTask[i].lastExecuted != False ):
                    continue;
            strOut = self.listTask[i].strName + ": " + speech.transcriptDateTimeObj( self.listTask[i].datetime, bSmart = True );
            listOut.append( [i,strOut] );
        # for each task- end
                
        return listOut;
    # getNextTask - end
    
    def setTaskDone( self, nIdxTask ):
        "return '' on error or the name of the task"
        if( nIdxTask < 0 or nIdxTask >= len( self.listTask ) ):
            print( "ERR: TaskManager.setTaskDone: wrong idx: %d" % nIdxTask );
            return "";
            
        print( "INF: TaskManager.setTaskDone: closing '%s'" % self.listTask[nIdxTask].strName );
        
        strName = self.listTask[nIdxTask].strName;

        # handle repetition:
        if( self.listTask[nIdxTask].nRepeatType == Task.eRepeatNone ):
            # no repeat => task done
            self.listTask[nIdxTask].lastExecuted = datetime.datetime.now();            
        else:
            self.listTask[nIdxTask]._incrementTaskDueToPeriodicity();
        self.sort();
        self.write();
        return strName;
    # setTaskDone - end
    
    def sort( self ):
        # sort all tasks
        self.listTask.sort(key=lambda sometask: sometask.datetime );
        
    # sort - end
# class TaskManager - end

taskManager = TaskManager(); # the singleton


def autoTest():
    if( False ):
        taskManager.addTask( "testdaily", "", "12:00",  Task.eRepeatDaily );
        taskManager.addTask( "test1", "", "" );
    listNextTasks = taskManager.getNextTasks();
    print( "getNextTask: " + str( listNextTasks ) );
    taskManager.setTaskDone( listNextTasks[0][0] );
# autoTest - end

# autoTest();