# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Blog module
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""An object to generate a blog"""
print( "importing abcdk.blog" );

import mutex
import datetime
import os
import time

import config
#config.bInChoregraphe = False;
#config.strDefaultIP = "10.0.252.179";
import filetools
import naoqitools
import pathtools
import system

class Blog:
    """ a class to update a blog"""
    def __init__(self):
        if( system.isOnNao() ):
            self.strFileName = "/home/nao/www/blog/index.html";
        elif( system.isOnWin32() ):
            self.strFileName = "D:/ApacheRootWebSite2/htdocs/naoblog/index.html";
        else:
            self.strFileName = "/www/blog";
            
        self.strImgFolderAbs = os.path.dirname( self.strFileName ) + "/img/";
        self.strImgFolderLocal = "img/";        
        self.strEmoFolderAbs = os.path.dirname( self.strFileName ) + "/emo/";
        self.strEmoFolderLocal = "emo/";
        
        self.logMutex = mutex.mutex();
        self.logLastTime = None;
        
        # constants:
        self.none = 0;
        self.happy = 1;
        self.sad = 2;
        self.proud = 3;
        self.excitement = 4;
        self.fear = 5;
        self.anger = 6;
        self.neutral = 7;
        self.hot= 8;
        
    # __init__ - end
    
    def __del__(self):
        pass
    # __del__ - end
    
    def xCreateBlog( self ):
        try:
            if( not os.path.isfile( self.strFileName ) ):
                try:
                    os.makedirs( os.path.dirname( self.strFileName ) );
                    os.makedirs( self.strImgFolderAbs );
                    os.makedirs( self.strEmoFolderAbs );
                except BaseException, err:
                    print( "ERR: Blog.xCreateBlog: err: %s (1)" % ( str( err ) ) );                    
                    pass # nope
                file = open( self.strFileName, "wt" );                
                file.write( "<html><head><title>MyLife</title><meta http-equiv='refresh' content='10'></head><body><img src='/media/buddy.icon'><br><br><font size=+2>My Life<br><br></font>\n" ); # pour simplifier l'implementation, on ne fermera jamais la balise body ni html
                file.write( "<table cellpadding=5 cellspacing=2 valign=middle border=0>" );
                file.close();
                filetools.copyDirectory( pathtools.getABCDK_Path() + "data/emo/", self.strEmoFolderAbs );
        except BaseException, err:
            print( "ERR: Blog.xCreateBlog: err: %s (2)" % ( str( err ) ) );
    # createBlog - end
    
    def updateBlog( self, strMessage ):
        "add a sentence to the blog"
        strNow = str( datetime.datetime.now() );
        strDate = strNow[0:len(strNow)-7]; # enleve les micro secondes! et les milli!
        
        while( self.logMutex.testandset() == False ):
            print( "INF: Blog.updateBlog: locked" );
            time.sleep( 0.02 );
            
        self.xCreateBlog();
        
        file = False;
        try:        
            file = open( self.strFileName, "at" );
            # file.seek( os.SEEK_SET, 0 ); // ca serait sympa de pouvoir inserer au debut, mais bon c'est pas facile (et puis y a le header et tout, beurk bof...) # de toutes facons ca marche pas en 'at' on ne peut pas modifier le debut du fichier!
            if( self.logLastTime == None or self.logLastTime.strftime( "%d%m%y" ) != datetime.datetime.now().strftime( "%d%m%y" ) ):
                # output date
                self.logLastTime = datetime.datetime.now();
                strDate = self.logLastTime.strftime( "%A %d %B" );
                strTxt = "<tr><td width=80>""</td><td width=480><b><hr size=1 width=80%><center>" + strDate + "</center></b></td><tr>\n";
                file.write( strTxt );
            
            strDate = datetime.datetime.now().strftime( "%H:%M:%S" );
            strTxt = "<tr><td><font color=#808080 size=-1>" + strDate + "</font></td><td><font face='Verdana'>" + strMessage + "</font></td><tr>\n";
            file.write( strTxt );
            

        finally:
            if( file ):
                file.close();
                
        self.logMutex.unlock();
    # updateblog - end
    
    def updateImg( self, strMessage, strFilenameImg = None, strLegend = None ):
        "add an image and a sentence to a blog"
        "strFilenameImg: if None, take a picture using camera"
        "strLegend: if different of None or strLegend, add a legend below the image"
        
        if( strFilenameImg == None ):
            print( "INF: Blog.updateImg: Taking picture...\n" );
            camToolBox = naoqitools.myGetProxy( "ALVisionToolbox" );
            camToolBox.halfPress();
            strFilenameImg = "/home/nao/" + filetools.getFilenameFromTime();
            camToolBox.post.takePictureRegularly( 5.0, strFilenameImg, True, "jpg", 2 ); # 2=> VGA
            time.sleep( 2.2 ); # 1 second is not sufficient !
            camToolBox.stopTPR( strFilenameImg, "jpg" );
            strFilenameImg = strFilenameImg + '.jpg'; # coz takePictureRegularly add '.jpg' automatically
            print( "INF: Blog.updateImg: Taking picture, file goes to '%s'\n" % strFilenameImg );
        strExt = os.path.basename( strFilenameImg );
        strExt = strExt.split( '.' );
        strExt = strExt.pop();
        strFilename = filetools.getFilenameFromTime() + '.' + strExt;
        strDest = self.strImgFolderAbs + strFilename;
        filetools.copyFile( strFilenameImg, strDest );
        strTxt = "<table cellpadding=2><tr><td>%s<br></td></tr><tr><td><IMG SRC='%s' HEIGHT=192></td></tr>" % ( strMessage, self.strImgFolderLocal + strFilename );
        if( strLegend != None and strLegend != "" ):
            strTxt += "<tr><td><font size=-2><center>- %s -</center></font></td></tr>" % strLegend;
        strTxt += "</table>";
        self.updateBlog( strTxt );
    # updateImg - end
    
    def updateEmo( self, strMessage, nEmoNumber = 1 ):
        "add a text with an emoticon"
        astrFilename = [ 
            "happy",
            "sad",            
            "proud",
            "excitement",
            "fear",
            "anger",
            "neutral",
            "hot",
        ];
        
        if( nEmoNumber == 0 ):
            return self.updateBlog( strMessage ); # no emotion
        strImgFile = "emo/nao_" + astrFilename[nEmoNumber-1] + '.png';
        strTxt = "<table cellpadding=2><tr><td>%s</td><td><IMG SRC='%s' HEIGHT=22></td></tr></table>" %  ( strMessage, strImgFile );
        self.updateBlog( strTxt );
    # updateImg - end    
    
# class Blog

blog = Blog();

def autoTest():
    blog.updateBlog( "coucou" );
    blog.updateBlog( "o_O &nbsp;je vais bien !" );
    blog.updateEmo( "Je suis bien content !", blog.happy );
    blog.updateEmo( "J'ai faim!", blog.sad );
    blog.updateEmo( "J'ai chaud!", blog.hot );
    blog.updateImg( "J'ai vu ca:", "d:\\graph\\2009-03-13_16m06m29.771616_alexandre.png", "humain en train de réfléchir" );
    blog.updateImg( "et ca:", "d:\\graph\\2009-03-13_16m06m29.771616_alexandre.png" );
    blog.updateImg( "et puis ca aussi, ca ressemble carrément un peu non, tu ne trouves pas?:", "d:\\graph\\2009-03-13_16m06m29.771616_alexandre.png" );
    blog.updateImg( "et la je vois ca, t'imagines ?" );
# autoTest - end

#autoTest();