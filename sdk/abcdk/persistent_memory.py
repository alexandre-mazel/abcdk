# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Persistent memory: a class to store data to a shared memory, in a persistent mode (even if restarting naoqi, nao, ...)
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Persistent memory: a class to store data to a shared memory, in a persistent mode (even if restarting naoqi, nao, ...)"

print( "importing abcdk.persistent_memory" );

import mutex
import os
import struct
import time

import debug
import filetools
import naoqitools
import pathtools

unknownValue = -4242.42; # how access to module level ?


class PersistentMemoryData:
    def __init__(self, strName = None ):
        self.mutex = mutex.mutex();        
        self.strName = strName;
        self.allValue = [];  # a big array of triple [time, type, value] but because type is self explained => [time, value]  # from older to newer
        # precomputed value:
        self.lastValue = None; 
        if( strName != None ):
            self.readFromFile();
        self.timeLastSave = time.time(); # for autosaving
    # __init__ - end
    
    def __del__(self):
        print( "INF: PersistentMemoryData.__del__ called" );
        self.writeToFile();
    # __del__ - end
    
    def updateData( self, value ):
#        print( "INF: PersistentMemoryData.updateData: %s set to '%s'" % ( self.strName, str( value ) ) );
        while( self.mutex.testandset() == False ):
            print( "PersistentMemoryData(%s).updateData: locked" % self.strName );
            time.sleep( 0.1 ); 
#        self.allValue.append( [ time.time(), typeToString( value ), value ] );
        self.allValue.append( [ time.time(), value ] );
        if( len( self.allValue ) > 200 ):
            print( "INF: %s: PersistentMemoryData(%s).updateData: reducing history" % ( debug.getHumanTimeStamp(), self.strName ) ); # permet aussi de voir si il n'y a pas des valeurs dans lesquels on poste un peu trop souvent
            self.allValue = self.allValue[-100:]; # ne garde que les 100 derniers !
        self.lastValue = value;
        self.mutex.unlock();
        # locking would be done in the write method
        if( time.time() - self.timeLastSave > 60 ): # save each variables every 60 seconds
            print( "INF: PersistentMemoryData(%s).updateData: autosaving data..." % self.strName );
            self.writeToFile();
    # updateData - end
    
    def getData( self, defaultValue = -4242.42 ):
        "return last value"
#        print( "INF: PersistentMemoryData.getData of %s return '%s'" % ( self.strName, str( self.lastValue ) ) );
        if( len( self.allValue ) != 0 ):
            return self.lastValue;
        debug.debug( "WRN: PersistentMemoryData.getData not found: '%s' returning default" % ( self.strName ), bIgnoreDuplicateMessage = True );
        return defaultValue;
    # getData - end
    
    def getDataAndTime( self, defaultValue = -4242.42 ):
        "return last value and time of value"
#        print( "INF: PersistentMemoryData.getDataAndTime of %s return '%s'" % ( self.strName, str( self.lastValue ) ) );
        if( len( self.allValue ) != 0 ):
            return self.allValue[-1];
        debug.debug( "WRN: PersistentMemoryData.getDataAndTime not found: '%s' returning default" % ( self.strName ), bIgnoreDuplicateMessage = True );
        return [defaultValue,0];
    # getDataAndTime - end    
    
    def eraseData( self ):
        "destroy this data, history and all disk files"
        debug.debug( "INF: PersistentMemoryData.eraseData: erasing %d value(s) for '%s'" % ( len( self.allValue ), self.strName ) );
        while( self.mutex.testandset() == False ):
            print( "PersistentMemoryData(%s).eraseData: locked" % self.strName );
            time.sleep( 0.1 );
            
        self.allValue = [];  # a big array of triple [time, type, value] but because type is self explained => [time, value] 
        self.lastValue = None; 
        cleanedName = str.replace( self.strName, "/", "__" );
        filename = self.__getVarPath_Inner__() + cleanedName + '.dat';
        try:
            os.unlink( filename );
        except BaseException, err:
            # debug.debug( "INF: PersistentMemoryData.eraseData(%s): normal error if no previous save: '%s'" % ( self.strName, err ) );
            pass
        self.mutex.unlock();
    # eraseData - end
    
    def getDataHist( self, nNbrValue = 3 ):
        if( len( self.allValue ) < 1 ):
            return [];
        elif( len( self.allValue ) < nNbrValue ):
            nNbrValue = len( self.allValue );
        return self.allValue[-nNbrValue:];
    # getDataHist - end
    
    def getDataHistLength( self ):
        return len( self.allValue );
    # getDataHistLength - end
    
    
    @staticmethod 
    def getVarPath():
        return pathtools.getCachePath() + 'mem' + pathtools.getDirectorySeparator();
    # getVarPath - end
    
    # je ne sais pas pourquoi dans cette classe il veut pas que j'appelle PersistentMemoryData.getVarPath() (depuis une méthode non statique) (c'est nul ca!!!)
    def __getVarPath_Inner__( self ):
        import pathtools # module already unloaded when called from __del__
        return pathtools.getCachePath() + "mem" + pathtools.getDirectorySeparator();
    # getVarPath - end
    
    def readFromFile( self ):
        print( "INF: PersistentMemoryData.readFromFile: reading previous value for '%s'" % self.strName );
        while( self.mutex.testandset() == False ):
            print( "PersistentMemoryData(%s).readFromFile: locked" % self.strName );
            time.sleep( 0.1 );         
        cleanedName = str.replace( self.strName, "/", "__" );
        filename = self.__getVarPath_Inner__() + cleanedName + '.dat';
        try:
            file = open( filename, 'rb' );
            if( file ):
                buf = file.read();
                file.close();
                self.allValue = eval( buf );
                if( len( self.allValue ) > 0 ):
                    self.lastValue = self.allValue[len(self.allValue)-1][1]; # 1 is the index of the value
                    print( "INF: PersistentMemoryData.readFromFile: lastValue: %s (%d value(s))"% ( str( self.lastValue ),  len( self.allValue ) ) );
        except BaseException, err:
            debug.debug( "WRN: PersistentMemoryData.readFromFile(%s)\nWRN: error: '%s'\nWRN: => no value readed" % ( filename, err) );
        self.mutex.unlock();
    # readFromFile - end
    
    def writeToFile( self ):
        print( "INF: PersistentMemoryData.writeToFile: storing value for '%s' (%d value(s))" % ( self.strName, len( self.allValue ) ) );
        while( self.mutex.testandset() == False ):
            print( "PersistentMemoryData(%s).writeToFile: locked" % self.strName );
            time.sleep( 0.1 );
            
        if( len( self.allValue ) == 0 ):
            import debug # module already unloaded when called from __del__
            debug.debug( "WRN: PersistentMemoryData.writeToFile(%s): no write because no value in the object" % self.strName );
            # don't save empty object
            self.mutex.unlock();
            return;
        try:            
#           print( "allValue: %s"% str( self.allValue ) );
            cleanedName = str.replace( self.strName, "/", "__" );
            filename = self.__getVarPath_Inner__() + cleanedName + '.dat';
        except BaseException, err:
            print( "ERR: PersistentMemoryData.writeToFile(%s) error: '%s'" % ( self.strName, err ) );
            pass
            
        try:
            file = open( filename, 'wb' );
            if( file ):
                buf = str( self.allValue );
                
                #~ buf = "[";
                #~ for value in self.allValue:
                    #~ buf += "[%s,%s,%s]" % ( value[0], typeToString, str( value[2] ) );                    
                #~ buf += "]";
                
                file.write( buf );
                file.close();
                
        except BaseException, err:
            print( "WRN: PersistentMemoryData.writeToFile(%s), filename: '%s' error: '%s'" % ( self.strName, filename, err ) );
        self.timeLastSave = time.time();
        self.mutex.unlock();
    # writeToFile - end
    
    def exportToALMemory( self ):
        "write all value of this variable to the ALMemory"
        mem = naoqitools.myGetProxy( "ALMemory" );
        while( self.mutex.testandset() == False ):
            print( "PersistentMemoryData(%s).exportToALMemory: locked" % self.strName );
            time.sleep( 0.1 );        
        strKeyname = "behaviordata/" + self.strName;
#        print( "INF: PersistentMemoryData.exportToALMemory: exporting value for '%s' (%d value(s))" % ( self.strName, len( self.allValue ) ) );
        if( mem != None ):
            mem.insertData( strKeyname, self.allValue );
        self.mutex.unlock();
    # exportToALMemory - end
    
    def importFromALMemory( self, strName, strSpecificIP = "localhost" ):
        "read a value from a distant ALMemory on a robot"
        mem = naoqitools.myGetProxy( "ALMemory", strSpecificIP );        
        while( self.mutex.testandset() == False ):
            print( "PersistentMemoryData(%s).importFromALMemory: locked" % self.strName );
            time.sleep( 0.1 );                
        self.strName = strName;
        strKeyname = "behaviordata/" + self.strName;
        self.allValue = mem.getData( strKeyname );
        self.mutex.unlock();
        print( "self.allValue: " + str( self.allValue ) );
    # importFromALMemory - end
    
    def generateGraph( self ):
        import matplotlib
        import pylab
        while( self.mutex.testandset() == False ):
            print( "PersistentMemoryData(%s).generateGraph: locked" % self.strName );
            time.sleep( 0.1 );        
        valueToGraph = [];
        listLibelle = [];
        bHasLibelle = False;
        bHasValue = False;
        for i in range( len( self.allValue ) ):
            val = self.allValue[i][1];
            if( typetools.isString( val ) ):
                valueToGraph.append( None );
                listLibelle.append( val );
                bHasLibelle = True;
            else:
                valueToGraph.append( val );
                listLibelle.append( '' );
                bHasValue = True;
#        valueToGraph = [ 0, 3, 2, 0, 5, 7 ];
        pylab.plot(valueToGraph);
        pylab.grid( True );
        pylab.title( self.strName );
        if( bHasLibelle ):
            if( not bHasValue ):
                pylab.axis([0,len( self.allValue ),-3,3] );
#            pylab.legend( listLibelle ); # non en fait c'est des etiquettes que je veux et pas une légende !
            for i in range( len( listLibelle ) ):
                pylab.text( i, ((i+2)%5)-2, listLibelle[i] );
            pass
        self.mutex.unlock();
    # generateGraph - end
    
    
    def drawGraph( self, nPosX = 0, nPosY = 0, nSizeX = 320, nSizeY = 200 ):
        "draw a graph on screen showing all values of this data"
        import matplotlib
        import pylab
        
        self.generateGraph();
        
        matplotlib.pyplot.show()
        matplotlib.pyplot.close();
    # drawGraph - end    
        
    
    def saveGraph( self, strFilename = "" ):
        "save a png file showing all values into a graph"
        import matplotlib
        import pylab
        
        try:
            if( len( self.allValue ) < 1 ):
                return False;
            strGraphPath = self.__getVarPath_Inner__() + "graph/";
            if( strFilename == "" ):
                try:
                    os.makedirs( strGraphPath );
                except:
                    pass
                strFilename =  strGraphPath + str.replace( self.strName, "/", "__" ) + ".png";
            print( "INF: PersistentMemoryData.saveGraph: saving graph of variable to file '%s'" % ( strFilename ) );
            self.generateGraph();
            matplotlib.pyplot.savefig( strFilename, format="png", transparent=True); # dpi=50 => 400x300 au lieu de 800x600
            matplotlib.pyplot.close()
        except BaseException, err:
            debug.debug( "WRN: PersistentMemoryData.saveGraph(%s) error: '%s'" % ( self.strName, err ) );
            return False;
        return True;
    # saveGraph - end
    
    
# class PersistentMemoryData - end


class PersistentMemory:
    """ store data with history"""
    def __init__(self):
        debug.debug( "INF: PersistentMemoryDataManager.__init__ called" );
        self.allData = {};
        self.mutexListData = mutex.mutex();
        try:
            os.makedirs( PersistentMemoryData.getVarPath() );
        except:
            pass # le dossier existe deja !
    # __init__ - end
    
    def __del__(self):
        import debug # module already unloaded when called from __del__
        debug.debug( "INF: PersistentMemoryDataManager.__del__ called" );
        self.exportToALMemory(); # before that we export one time to the ALMemory, it doesn't cost a lot and can help users later (debug or...)
        self.allData = {};
    # __del__ - end

    def updateData( self, strName, value ):
        while( self.mutexListData.testandset() == False ):
            print( "PersistentMemoryDataManager.updateData(%s): locked" % strName );
            time.sleep( 0.1 ); 
        if( not strName in self.allData ):
            self.allData[strName] = PersistentMemoryData( strName );
        self.mutexListData.unlock();
        self.allData[strName].updateData( value ); # on ne mutex pas l'update (ca sera fait dans la methode)
    # updateData - end
    
    def getData( self, strName, defautValue = unknownValue ):
        "return the value of some data"
        if( not strName in self.allData ):
            # we create it (or reading it from disk)
            self.allData[strName] = PersistentMemoryData( strName );
        return self.allData[strName].getData( defautValue );
    # getData - end
    
    def getDataAndtime( self, strName, defautValue = unknownValue ):
        "return the [value, time_of_this_value] of some data"
        if( not strName in self.allData ):
            # we create it (or reading it from disk)
            self.allData[strName] = PersistentMemoryData( strName );
        return self.allData[strName].getDataAndTime( defautValue );
    # getDataAndtime - end    
    
    def removeData( self, strName, defautValue = unknownValue ):
        if( not strName in self.allData ):            
            # nothing to do!
            print( "WRN: PersistentMemoryDataManager.removeData(%s): data not found" % strName );
            return;
        self.allData[strName].eraseData();
        del self.allData[strName]; # erase the object (no backup would be made, since we erase the data)
    # getData - end    
    
    def loadAll( self ):
        "load all variables present on disk in the normal path"
        "That's usefull before calling saveGraphs"
        print( "INF: PersistentMemoryDataManager.loadAll called" );
        while( self.mutexListData.testandset() == False ):
            print( "PersistentMemoryDataManager.loadAll: locked" );
            time.sleep( 0.1 );         
        strPath = PersistentMemoryData.getVarPath();
        allFiles = filetools.findFile( strPath,  ".dat", False );
        for file in allFiles:
            strVarName = str.replace( file, strPath, "" );
#            strVarName = str.replace( strVarName, "extracted_data__", "" );
            strVarName = str.replace( strVarName, ".dat", "" );
#            print( strVarName );
            if( not strVarName in self.allData ):
                self.allData[strVarName] = PersistentMemoryData( strVarName );
        self.mutexListData.unlock();
        print( "loadAll: %d variable(s) loaded" % len( allFiles ) );
    # loadAll - end
    
    def storeAll( self ):
        "store all variable"
        while( self.mutexListData.testandset() == False ):
            print( "PersistentMemoryDataManager.storeAll: locked" );
            time.sleep( 0.1 );        
        print( "INF: PersistentMemoryDataManager.storeAll: storing %d variable(s)" % len( self.allData ) );
        for k, v in self.allData.iteritems():
            v.writeToFile();
        self.mutexListData.unlock();
    # storeAll - end
    
    def saveGraphs( self ):
        "store all variable"
        while( self.mutexListData.testandset() == False ):
            print( "PersistentMemoryDataManager.saveGraphs: locked" );
            time.sleep( 0.1 );        
        print( "INF: PersistentMemoryDataManager.saveGraphs: graphing %d variable(s)" % len( self.allData ) );
        for k, v in self.allData.iteritems():
            v.saveGraph();
        self.mutexListData.unlock();
    # saveGraphs - end
    
    def exportToALMemory( self ):
        "copy all variable to ALMemory"
        if( len( self.allData ) == 0 ):
            return;
        print( "INF: PersistentMemoryDataManager.exportToALMemory: exporting %d variable(s)" % len( self.allData ) );
        import naoqitools # module already unloaded when called from __del__
        mem = naoqitools.myGetProxy( "ALMemory" );
        if( mem == None ):
            print( "WRN: PersistentMemoryDataManager.exportToALMemory: can't connect to ALMemory" );
            return;
        while( self.mutexListData.testandset() == False ):
            print( "PersistentMemoryDataManager.exportToALMemory: locked" );
            time.sleep( 0.1 );            
        allVarName = [];
        mem = naoqitools.myGetProxy( "ALMemory" );
        for k, v in self.allData.iteritems():
            allVarName.append( v.strName );
            v.exportToALMemory();
        mem.insertData( "PersistentMemoryDataManager_all_vars", allVarName );
        self.mutexListData.unlock();
    # exportToALMemory - end
    
    def importFromALMemory( self, strSpecificIP = "localhost" ):
        "import all variables from a (remote) ALMemory"
        try:
            mem = naoqitools.myGetProxy( "ALMemory", strSpecificIP );
            allVarName = mem.getData( "PersistentMemoryDataManager_all_vars" );
        except BaseException, err:
            debug.debug( "WRN: importFromALMemory: %s" % str( err ) );
            return;
        while( self.mutexListData.testandset() == False ):
            print( "PersistentMemoryDataManager.importFromALMemory: locked" );
            time.sleep( 0.1 );            
        self.allData = {};
        for strVarName in allVarName:
            someData = PersistentMemoryData();
            someData.importFromALMemory( strVarName, strSpecificIP );
            self.allData[strVarName] = someData;
        self.mutexListData.unlock();
        print( "importFromALMemory: %d variable(s) loaded" % len( self.allData ) );
    # exportToALMemory - end
    
    def dumpAll( self ):
        "dump to print all the outputted extracted data"
        print( "INF: PersistentMemoryDataManager.dumpAll at %d - humantime: %s" % ( int( time.time() ), debug.getHumanTimeStamp() ) );
        print( "*" * 30 );
        while( self.mutexListData.testandset() == False ):
            print( "PersistentMemoryDataManager.dumpAll: locked" );
            time.sleep( 0.1 );            
        for k, v in self.allData.iteritems():
            strOut = "%s " % ( k );
            strOut += "(%d val): " % v.getDataHistLength();
            aLastValue = v.getDataHist( 3 );
            for val in aLastValue:
                strOut += "%s: %s; " % ( timeToHuman( val[0] ), str( val[1] ) );
            print( strOut );
        print( "*" * 30 );
        self.mutexListData.unlock();        
    # dumpAll - end
    
    def getHist( self, strDataName, nNbrValue = 3 ):
        if( not strDataName in self.allData ):
            return [];
        return self.allData[strDataName].getDataHist( nNbrValue );
    # getHist - end
        
            
        
# class PersistentMemory - end    

    
    

persistentMemory = PersistentMemory(); # the singleton


def autoTest():
    timeTest_get_first = persistentMemory.getData( "timeTest", 421 );
    print( "*** timeTest_get_first: %s" % str( timeTest_get_first ) );
    timeTest = time.time();
    persistentMemory.updateData( "timeTest", timeTest );
    timeTest_get = persistentMemory.getData( "timeTest", 421 );
    print( "*** timeTest_get: %s" % str( timeTest_get ) );
    print( "*** timeTest_get hist: %s" % str( persistentMemory.getHist( "timeTest", 20 ) ) );
    persistentMemory.removeData( "timeTest" );
    timeTest_get = persistentMemory.getData( "timeTest", 421 );
    print( "*** timeTest_get(after erase): %s" % str( timeTest_get ) );
    print( "*** timeTest_get hist(after erase): %s" % str( persistentMemory.getHist( "timeTest", 20 ) ) );
    
# autoTest - end
    
# autoTest();