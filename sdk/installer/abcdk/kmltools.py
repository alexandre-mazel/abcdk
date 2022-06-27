# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Kml tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################


"""Tools to work with google localisation tools 'kml file'."""

print( "importing abcdk.kmltools" );

import filetools
import pathtools
import nettools
import naoqitools
import system

class KmlManager:
    """ a small class to create constant preventing to changing the value of an existant one"""
    """ to create a new constants, just type const.toto = 3;"""
    """ the many of the info are not usefull, because the exact processing is redone to the server side"""
    def __init__(self):
        self.aListPos = {}; # a dictionnary of chestName => [[position2D, (altitude)],desc]
        self.strServerAdress = "http://10.0.252.143/naoworld/";
        self.strServerAdress = "http://www.mangedisque.com/Alma/naoworld/";
        self.strServerAdress = "http://perso.ovh.net/~mangedisf/mangedisque/Alma/naoworld/";
      
        self.loadFromDisk();
    # __init__ - end

    def __del__(self):
       self.saveToDisk();
    # __init__ - end
    
    def reset(self):
       self.aListPos = {};
    # __init__ - end    
    
    def addPosition( self, strName, aPosition, strDesc = None ):
        # add a known position: aPosition is an array [longitude, latitude, (altitude)]
        print( "KmlManager.addPosition: adding '%s' at %s" % ( strName, str( aPosition ) ) );
        val = [aPosition];
        if( strDesc != None ):
            val.append( strDesc );
        self.aListPos[strName] = val;
        # each time we export to local KML, just for fun ?
#        self.exportToKML();
        
        if( True ): # send to server
            if( len( aPosition ) > 2 ):
                paramAlt = "&alt=" + str(aPosition[2] );
            else:
                paramAlt = "";
            if( strDesc != None ):
                paramDesc = "&desc=" + strDesc;
            else:
                paramDesc = "";
            strNaoqiVer = naoqitools.getNaoqiVersion();
            strOwner = system.getUserNameFromChestBody();
            strRequest = "?name=%s&long=%s&lat=%s%s%s&naoqi=%s&owner=%s" % ( strName, aPosition[0], aPosition[1], paramAlt, paramDesc, strNaoqiVer, strOwner );
            strRet = nettools.getHtmlPage( self.strServerAdress + "add_positions.php" + strRequest );
            print( "INF: KmlManager.loadFromDisk: sended addPosition to the web, ret: '%s'" % (strRet) );
    # addPosition - end
    
    def loadFromDisk( self ):
        print( "INF: KmlManager.loadFromDisk: begin" );
        try:
            file = open( pathtools.getCachePath() + "KmlManager.dat", "rb" );        
            if( file ):
                self.aListPos = filetools.fileToDict( file );
                print( "INF: KmlManager.loadFromDisk: position known: %d" %  len( self.aListPos ) );
                file.close();
        except BaseException, err:
            print( "INF: KmlManager.loadFromDisk: no previous data found ? (err:%s)" % ( err ) );        
            self.aListPos = {}; # reset it
            return;
        print( "INF: KmlManager.loadFromDisk: end" );            
    # loadFromDisk - end
    
    def saveToDisk( self ):
        try:
            timer = altools.TimeMethod();    
        except:
            pass
        print( "INF: KmlManager.saveToDisk: begining..." );
        file = open( pathtools.getCachePath() + "KmlManager.dat", "wb" );
        filetools.dictTofile( file, self.aListPos );
        file.close();
        print( "INF: KmlManager.saveToDisk: end" );
    # saveToDisk - end

    def toString( self ):
        strOut = "KmlManager, known pos: %d\n" % len( self.aListPos );
        strOut += str( self.aListPos );
        return strOut;
    # toString - end        

    def exportToKML( self, strFilename = None ):
        if( strFilename == None ):
            strFilename = pathtools.getVolatilePath()  + 'pos.kml';
        strOut = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Folder>""";
        for k, v in self.aListPos.iteritems():
            pos = v[0];
            rLon = pos[0];
            rLat = pos[1];
            rAlt = 0;
            if( len( pos ) > 2 ):
                rAlt = pos[2];
                
            strDesc = "";
            if( len( v ) > 1 ):
                strDesc = "<description>%s</description>" % v[1];
                
            strOut += """
            <Placemark>
                <name>%s</name>
                %s
                <Point>
                    <coordinates>%f,%f,%f</coordinates>
                </Point>
            </Placemark>""" % ( k, strDesc, rLon, rLat, rAlt );
  
  
        strOut += "\n  </Folder>\n</kml>";
        
        file = open( strFilename, "wt" );
        file.write( strOut );
        file.close();
        
        print( "INF: exportToKML: exported to '%s': %d position(s)" % (strFilename, len( self.aListPos ) ) );
        
    # exportToKML - end        
    
# class KmlManager - end

def autoTest():
    km = KmlManager();
    km.reset();
    km.addPosition( "Maison", [ 2.34527108441, 48.8037763095], "La maison de ou que j'habite" );
    km.addPosition( "Aldebaran Robotics", [ 2.309744, 48.829494] );    
    print( km.toString() );
    km.exportToKML();
# autoTest  - end
    

# test zone
#autoTest();