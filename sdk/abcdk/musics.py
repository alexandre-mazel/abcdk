# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Musics tools
# v0.6
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Musics tools"

print( "importing abcdk.musics" );

import naoqitools
import system
import typetools

import mutex
import os
import random
import time

import json

def loadMetadata(strMetadataFilename):
    """
    return a dict with metadata info
    keys: examplse:
     "time_signature": 4,
 "analysis_url": "http://echonest-analysis.s3.amazonaws.com/TR/5xUCRwCcnVh0MWmoZxhfP0jDMzM5a9qgsLi9QARtKJq-2JSaXypefVXZI8oy62yB6_KUGu9oKlsc0ZtU8%3D/3/full.json?AWSAccessKeyId=AKIAJRDFEY23UEVW42BQ&Expires=1391699350&Signature=tmZKm2GHvNpc35sEIpw7fxonmBY%3D",
 "energy": 0.549781,
 "liveness": 0.232914,
 "tempo": 108.363,
 "speechiness": 0.054486,
 "acousticness": 0.745132,
 "mode": 0,
 "key": 10,
 "duration": 243.09288,
 "loudness": -12.981,
 "audio_md5": "b00d12b8c85491a9451aa32ac26de815",
 "valence": 0.248917,
 "danceability": 0.628939

    :param strMetadataFilename:
    :return:
    """
    with open(strMetadataFilename) as f:
        aDict = json.load(f)
    return aDict


class Songv2(object):
    """
    New representation of a song file (not compatible with previous) # Laurent.

    # NDEV:
    draft for demo
    """
    def __init__(self, strMp3Filename):
        self.strFilename = strMp3Filename
        self.metadataDict = loadMetadata(os.path.splitext(os.path.basename(self.strFilename))[0])
        if self.metadataDict.haskey('tempo'):
            self.bpm = self.metadataDict['tempo']
        else:
            self.bpm = 100
        if self.bpm < 100:
            self.strStyle = 'Singer'
        else:
            self.strStyle = 'Rock'
        self.strArtist = self.metadataDict['artist']

class Song():
    "The representation of a song file"
    def __init__(self, strFilename = "", strLocalPath = "", strStyle = "", strArtist = "", strTitle = "", strAlbumName = "", strExtra = "" ):
        strLocalPath = strLocalPath.replace( "\\", "/" );
        strFilename = strFilename.replace( "\\", "/" );
        if( strLocalPath == "" ):
            # the strFilename is in fact the absolute path
            nIndexSlash = strFilename.rfind( '/' ) + 1;
            # print( "strFilename: %s nIndexSlash: %d" % (strFilename, nIndexSlash) );
            strFilenameOnly = strFilename[nIndexSlash:];
            strLocalPath = strFilename[:-len( strFilenameOnly )];
            strFilename = strFilenameOnly;
          
        self.strFilename = strFilename;
        self.strLocalPath = strLocalPath; # local path in the library, without filename eg: rock/metal/
        self.strStyle = strStyle;
        self.strArtist = strArtist;
        self.strTitle = strTitle;
        self.strAlbumName = strAlbumName;
        self.strExtra = strExtra; # some extra information ("featuring Alex" / "radio mix" / "acapella version") ...
        # optionnal field:
        self.rUserNotation = -1;
        self.rGlobalNotation = -1;

        # extract info from song name
        if( strArtist == "" and strTitle == "" ):
            aField = strFilename.split( "_-_" );
            if( len( aField ) > 1 ):
                # format is "artist_-_song_title"
                self.strArtist = Song.cleanField( aField[0] );
                self.strTitle = Song.cleanField( aField[1] );
                aFieldExt = aField[1].split( "__" );
                if( len( aFieldExt ) > 1 ):
                    if( self.strExtra == "" ):
                        self.strExtra = Song.cleanField( aFieldExt[1] );
                    self.strTitle = Song.cleanField( aFieldExt[0] );
            else:
                # analyse folder name (could be overriden while analysing song name)
                nIndexSlash = self.strLocalPath.rfind( '/', 0, -1 );
                # print( "strFolderOnly: %s nIndexSlash: %d" % (self.strLocalPath, nIndexSlash) );
                strFolderOnly = self.strLocalPath[nIndexSlash:-1];
                
                aField = strFolderOnly.split( " - " );
                if( len( aField ) > 1 ):
                    # folder is on style artist - album name
                    self.strAlbumName = aField[1];

                aField = strFilename.split( " - " );
                if( len( aField ) > 3 ):
                    # format is "artist - album name - track number - song title"
                    if( len( aField ) > 1 ):
                        self.strArtist = Song.cleanField( aField[0] );
                        self.strAlbumName = Song.cleanField( aField[1] );
                    if( len( aField ) == 4 ):
                        self.strTitle = Song.cleanField( aField[3] );
                    else:
                        self.strTitle = "";
                        for i in range( 3, len( aField ) ):
                            if( not typetools.isIntInString( aField[i] ) ):
                                self.strTitle += Song.cleanField( aField[i] );
                                if( i < len( aField ) - 1 ):
                                    self.strTitle += ' - ';
                else:
                    # format is "artist - track number - song title"
                    if( len( aField ) > 2 ):
                        self.strArtist = Song.cleanField( aField[0] );
                        self.strTitle = Song.cleanField( aField[2] );

                

    @staticmethod
    def cleanField( strFieldContents ):
        """clean a field extracted from a file name eg: "_" => " " and ... """
        strFieldContents = strFieldContents.replace( "_", " " );
        strFieldContents = strFieldContents.replace( ".mp3", "" );
        strFieldContents = strFieldContents.replace( ".wav", "" );
        return strFieldContents;

    def toString( self, bFull = True ):
        "convert the value in a clean string, ready to print"
        if( bFull ):
            strOutput = "\n";
            strOutput += "---------------------\n";
            strOutput += "Filename: '" + self.strFilename + "'\n";
            strOutput += "LocalPath: '" + self.strLocalPath+ "'\n";
            if( self.strStyle != "" ):
                strOutput += "Style: " + self.strStyle + "\n";
            strOutput += "Artist: " + self.strArtist + "\n";
            if( self.strTitle != "" ):
                strOutput += "Title: " + self.strTitle+ "\n";
            if( self.strAlbumName != "" ):
                strOutput += "Album Name: " + self.strAlbumName + "\n";
            if( self.strExtra != "" ):
                strOutput += "Extra Info: " + self.strExtra + "\n";
            if( self.rUserNotation != -1 ):
                strOutput += "User Notation: " + str( self.rUserNotation ) + "\n";
            if( self.rGlobalNotation != -1 ):
                strOutput += "Global Notation: " + str( self.rGlobalNotation ) + "\n";
            strOutput += "---------------------\n";
        else:
            strOutput = "%s - '%s' (from '%s')" % ( self.strArtist, self.strTitle, self.strAlbumName );
        return strOutput;
    # toString - end
  
    @staticmethod
    def sortSongByFilename(song1, song2):
        "This private method is a tool for some language processing functions."
        "BAD: can't succeed in calling from Musics, even when public => using lambda"
        return song1.strFilename < song2.strFilename;

# class Song - end


class Musics:
    "A catalog of music, play album, manage playlist, ..."
    
    def __init__( self, strBasePath ):
        self.strBasePath = strBasePath;
        self.songList = [];
        self.currentPlayList = []; # list of current song to play
        self.nPlaylistIdx = 0; # current index in the playlist
        self.bPlaying = False;
        self.idPlay = -1; # Naoqi play task id
        self.songPlaying = None;
        self.mutex = mutex.mutex();
        self.scan();
        self.lastAlbumChoice = ["",""];
    # __init__ - end
    
    def __del__( self ):
        self.stop();
    # __del__ - end
    
    def __scandir__( self, strDir ):
        print( "INF: abcdk.musics.scanning: '%s'" % strDir );
        for elem in os.listdir( strDir ):
            sFullPath = os.path.join( strDir, elem );
            #~ print( "fullpath: " + sFullPath );
            if os.path.isdir(sFullPath) and not os.path.islink(sFullPath):
                if( elem[0] != '.' ):
                    self.__scandir__( sFullPath );
            if os.path.isfile( sFullPath ):
                if( elem.find( ".mp3" ) != -1 or elem.find( ".wav" ) != -1 ):
                    s = Song( sFullPath );
                    self.songList.append( s );
        print( "INF: abcdk.musics.scanning: found %d song(s)" % len(self.songList) );                    
    # __scandir__ - end
                    
    def scan( self ):
        "(re)scan base path to find music"
        self.songList = [];
        self.__scandir__( self.strBasePath );        
        # self.songList.sort(Song::sortSongByFilename)
        self.songList.sort(key=lambda somesong: somesong.strFilename );
        
    # scan - end
    
    def toString( self, bFull = False ):
        "return the image of the library in a string"
        s = "";
        for song in self.songList:
          #~ if( bFull ):
            #~ s += song.toString( bFull );
          #~ else:
            #~ s += "%s: %s - %s (%s)\n" % ( song.strStyle, song.strArtist, song.strTitle , song.strFilename);
            s += song.toString( bFull ) + "\n";
        s += "%d songs" % len( self.songList );
        return s;
    # toString - end
    
    def toAbsolutePath( self, song ):
        "return the absolute path file name of a song object in the current library"
        # return self.strBasePath + song.strLocalPath + song.strFilename;
        return song.strLocalPath + song.strFilename;
    # toAbsolutePath - end
    
    def generatePlayListFromAlbum( self, strArtist, strAlbumName ):
        "generate a playlist relative to an album"
        "return the list of all song object"
        playList = [];
        # bad method
        strSkul = "%s - %s" % ( strArtist, strAlbumName );
        for song in self.songList:
            if( ( song.strLocalPath == "" and strSkul in song.strFilename ) or ( strArtist == song.strArtist and strAlbumName == song.strAlbumName ) ):
                playList.append( song );
        self.lastAlbumChoice =  [strArtist, strAlbumName];
        return playList;
    # generatePlayListFromAlbum - end
    
    def chooseRandomAlbum( self ):
        "generate a couple [artist,name] that permits to generate a non empty list of corresponding song "
        "calling twice won't never give the same results"
        "return [], if no album or only one, and called twice"
        nCpt = 0;
        lastAlbumChoice = self.lastAlbumChoice; # would be lost when calling generatePlayListFromAlbum
        while( nCpt < 20 ):
            nCpt += 1;
            song = self.songList[ int( ( random.random() ) * len( self.songList ) ) ];
            print( "song: %s" % song.toString() );
            strArtist = song.strArtist;
            strAlbumName = song.strAlbumName;
            someChoice = [ strArtist, strAlbumName ];
            print( "INF: Musics.generatePlayListFromRandomAlbum, trying: %s" % str( someChoice ) );
            aList = self.generatePlayListFromAlbum( strArtist, strAlbumName );
            if( someChoice != lastAlbumChoice and len( aList ) > 0 and not "YMCA" in strAlbumName ): # for demo purpose, we skip YMCA from the random
                return someChoice;
        
        print( "WRN: Musics.generatePlayListFromRandomAlbum, returning NONE" );
        return [];
    # chooseRandomAlbum - end
    
    def generateRandomPlayList(self):
        """
        Generate a random playlist of current known song
        return a list of song to send further to enqueue
        """
        playList = [];
        anIdx = range(0, len(self.songList) );
        random.shuffle( anIdx );
        for idx in anIdx:
            playList.append( self.songList[idx] );
        return playList;
    # generateRandomPlayList - end
    
    def enqueue( self, listToPlay ):
        while( not self.mutex.testandset() ):
            time.sleep( 0.1 );
            print( "INF: Musics.enqueue: lock..." );
        
        self.currentPlayList.extend( listToPlay );
        print( "INF: Musics.enqueue: Current playlist has now %d title(s)" % len( self.currentPlayList ) );
        self.printCurrentPlaylist();
        self.__play();
        self.mutex.unlock();
    # enqueue - end
    
    def clearPlaylist( self ):
        self.currentPlayList = [];
        self.nPlaylistIdx = 0;
    # clearPlaylist - end    
    
    def __play( self ):
        if( self.bPlaying ):
            print( "INF: Musics.play: already playing..." );
            return;
        if( len( self.currentPlayList ) - self.nPlaylistIdx < 1 ):
            print( "INF: Musics.play: nothing to play..." );
            return;
            
        try:
            print( "Musics.play: playing '%s', remaining in queue: %d song(s)" % ( self.currentPlayList[self.nPlaylistIdx].strFilename, len( self.currentPlayList ) - self.nPlaylistIdx - 1 ) );
            self.printCurrentPlaylist();

            ap = naoqitools.myGetProxy( "ALAudioPlayer" );
            if( ap != None ):
                self.idPlay = ap.post.playFile( self.toAbsolutePath( self.currentPlayList[self.nPlaylistIdx] ) );
            else:
                # play from a computer !
                strCommand = "start winamp \"%s\"" % self.toAbsolutePath( self.currentPlayList[self.nPlaylistIdx] );
                print( "INF: abcdk.musics.__play: Launching command: '%s'" % strCommand );
                os.system( strCommand );
                self.idPlay = -1; # TODO: something !
            self.songPlaying = self.currentPlayList[self.nPlaylistIdx];
            self.bPlaying = True;
        except BaseException, err:
            print( "ERR: Musics.play: %s" % str( err ) );
    # __play - end
    
    def play( self ):
        while( not self.mutex.testandset() ):
            time.sleep( 0.1 );
            print( "INF: Musics.play: lock..." );
        self.__play();
        self.mutex.unlock();        
    # play - end    
    
    def __stop( self ):
        try:
            if( self.bPlaying ):
                if( self.idPlay != -1 ):
                    try:
                        ap = naoqitools.myGetProxy( "ALAudioPlayer" );
                        ap.stop( self.idPlay );
                    except BaseException, err:
                        print( "WRN: Musics.stop: normal error?: %s" % str( err ) );
                    self.songPlaying = None;
                self.bPlaying = False;
        except BaseException, err:
            print( "ERR: Musics.stop: %s" % str( err ) );
    # __stop - end
    
    def stop( self ):
        while( not self.mutex.testandset() ):
            time.sleep( 0.1 );
            print( "INF: Musics.stop: lock..." );
        self.__stop();
        self.mutex.unlock();
    # stop - end
    
    def __updateState( self ):
        "see 'updateState' for documentation"
        nRet = 0;
        if( self.bPlaying ):
            nRet = 1;
            try:
                ap = naoqitools.myGetProxy( "ALAudioPlayer" );
                self.bPlaying = ap.isRunning( self.idPlay );
                # play next song
                if( not self.bPlaying and self.nPlaylistIdx < len( self.currentPlayList ) - 1 ):
                    self.nPlaylistIdx += 1;
                    self.__play();
                    nRet = 2;
            except BaseException, err:
                self.bPlaying = False;
                print( "WRN: Musics.__updateState: normal error?: %s" % str( err ) );
        return nRet;
    # __updateState - end    
    
    def updateState( self ):
        "this method should be called regularly"        
        "return 1 if a song is playing"
        "return 2 if song has changed"
        "return 0 elsewhere"
        
        while( not self.mutex.testandset() ):
            time.sleep( 0.1 );
            print( "INF: Musics.updateState: lock..." );
            
        nRet = self.__updateState();
                
        self.mutex.unlock(); 
        
        return nRet;
    # updateState - end
    
    def isPlaying( self ):
        self.updateState();
        return self.bPlaying;
    # isPlaying - end
    
    def printCurrentPlaylist( self ):
        nCpt = 0;        
        for song in self.currentPlayList:
            strOptText = "";
            if( self.nPlaylistIdx == nCpt ):
                strOptText = "<-- current song";
            print( "%s %s\n" % ( song.strFilename, strOptText ));
            nCpt += 1; 
    # printCurrentPlaylist - end
    
    def getCurrentSong( self ):        
        "return None if no song is playing"
        while( not self.mutex.testandset() ):
            time.sleep( 0.1 );
            print( "INF: Musics.getCurrentSong: lock..." );
        self.__updateState();
        if( not self.bPlaying or self.nPlaylistIdx >= len( self.currentPlayList ) or self.nPlaylistIdx < 0 ):
            self.mutex.unlock();
            return None;
        song = self.currentPlayList[self.nPlaylistIdx];
        self.mutex.unlock();
        return song;
    # getCurrentSong - end
    
    def getCurrentSongName( self ):
        "return a string describing current song playing"
        "return '' if no song is playing"
        song = self.getCurrentSong();
        if( song == None ):
            return "";
        strTitle = song.strTitle;
        if( strTitle == '' ):
            strTitle = song.strFilename.replace( ".mp3", "");
        return strTitle;
    # getCurrentSongName - end
    
    def next( self ):
        "return False if there's no song at the asked position"
        while( not self.mutex.testandset() ):
            time.sleep( 0.1 );
            print( "INF: Musics.next: lock..." );
        
        if( self.nPlaylistIdx >= len( self.currentPlayList ) - 1 ):
            self.mutex.unlock();
            return False;
        self.__stop();
        self.nPlaylistIdx += 1;        
        self.__play();
        self.mutex.unlock();
        return True;
    # next - end
    
    def prev( self ):
        "return False if there's no song at the asked position"
        while( not self.mutex.testandset() ):
            time.sleep( 0.1 );
            print( "INF: Musics.prev: lock..." );
        
        if( self.nPlaylistIdx < 1 ):
            self.mutex.unlock();
            return False;
        self.__stop();
        self.nPlaylistIdx -= 1;
        self.__play();
        self.mutex.unlock();
        return True;
    # next - end
    
    def pause( self ):
        "pause or resume the playing"
        # TODO
        pass
    # pause - end
    
# class Musics - end

def playRandomFromFlatDirectory( strDirectoryName ):
    jukebox = Musics( strDirectoryName );
    playList = jukebox.generateRandomPlayList();
    print( "INF: playlist is now: %s" % str(playList) );
    jukebox.enqueue( playList );
    return jukebox;
# playRandomFromFlatDirectory - end

def playRandomFromFlatDirectoryTest():
    strPath = "/home/nao/music_ambient_selection/";
    if( not system.isOnRobot() ):
        strPath = "c:/work/music_ambient_selection/";
    jukebox = playRandomFromFlatDirectory( strPath );
    return jukebox;
# playRandomFromFlatDirectoryTest - end



def autoTest():
    if( system.isOnRobot() ):
        jukebox = Musics( "/home/nao/jukebox/" );
    else:
        jukebox = Musics( "d:/jukebox/" );
    print( jukebox.toString() );
    listToPlay = jukebox.generatePlayListFromAlbum( "Rob Thomas", "...Something To Be" );
    print( "listToPlay1: %s\n" % str( listToPlay ) );
    listToPlay = jukebox.generatePlayListFromAlbum( "Youri", "Covers Collection" );
    print( "listToPlay2: %s\n" % str( listToPlay ) );    
    choice = jukebox.chooseRandomAlbum();
    choice = jukebox.chooseRandomAlbum();
    listToPlay = jukebox.generatePlayListFromAlbum( choice[0], choice[1] );
    print( "abs path: " + jukebox.toAbsolutePath( listToPlay[0] ) );    
    jukebox.enqueue( listToPlay );
# autoTest - end

if( __name__ == "__main__" ):
    #autoTest();
    playRandomFromFlatDirectoryTest();
    
    