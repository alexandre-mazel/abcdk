# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Display tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################


"""Tools to display image on tablet, picoproj..."""


print( "importing abcdk.display" );

import filetools
try: import minttu.minttu_manager
except: print( "WRN: abcdk.display: minttu not found..." )
import naoqitools
import os
import time


class Display():
    """
    For the tablet, we need to have a tmp directory with some web access, so you should do sth like:
        sudo mount / -o remount,rw
        mkdir /tmp/www
        su -c "ln -s /tmp/www /var/www/tmp"
        su -c "ln -s /home/nao/.local/lib/python2.7/site-packages/abcdk/data /var/www/abcdk_data"
    

        j'ai ajoute aussi a nginx.conf, avant "location /libs"
        su -c "nano /etc/nginx/nginx.conf"
            location /tmp {
            root /var/www;
        }
        et ne pas oublier de relancer le serveur:
        su -c "/etc/init.d/nginx restart"
        # en 2.5: 
        su -c "systemctl restart nginx"
        
    """
    def __init__( self ):
        self.tabletService = None;
        self.strWebLocalPath = "/var/www/tmp/";
        try:
            os.makedirs( "/tmp/www" ); # because /tmp is erased after each restart
        except:
            pass
        self.bDeactivate = False;
        import system
        if( not system.isOnPepper() ):
            self.bDeactivate = True;
    # __init__ - end

    def prepare( self ):
        """
        Do the real init, the one that takes time, requires hardware...
        """        
        if( self.tabletService == None ):
            self.tabletService = naoqitools.myGetProxy( "ALTabletService" );

            if( self.tabletService == None ):
                print( "WRN: can't connect to ALTabletService: you won't seen image on your tablet..." );            
                self.strWebRemotePath = None
            else:
                self.strWebRemotePath = "http://%s/tmp/" % self.tabletService.robotIp();
                
    def hideImage( self ):
        """
        Do the real init, the one that takes time, requires hardware...
        """        
        self.prepare()
        if( self.tabletService != None ):
            self.tabletService.hideImage()
    
    def showImage( self, strPathAndFilename, bDeleteFileJustAfter = False, bVerbose = False ):
        """
        Return False on error
        """
        if( self.bDeactivate ):
            return;
        dummy, strExt = os.path.splitext(strPathAndFilename)
        if( not strExt.lower() in ["jpg", "png", "gif"] ):
            # convert on the fly
            import cv2
            img = cv2.imread( strPathAndFilename )
            strDest = "/tmp/temp.jpg"
            cv2.imwrite( strDest, img )
            strPathAndFilename = strDest
            if( bDeleteFileJustAfter ):
                os.unlink( strPathAndFilename );
            
        bCheckSize = 1
        if( bCheckSize ):
            nRequiredW = 800
            nRequiredH = 480
            img = cv2.imread( strPathAndFilename )
            h,w,p = img.shape
            if( h > nRequiredH or w > nRequiredW ):
                while( h > nRequiredH or w > nRequiredW ):
                    small_image = cv2.resize( img, dsize=(0,0), fx=0.5, fy=0.5 );
                    img = small_image
                    h,w,p = img.shape
                print( "INF: abcdk.display.showImage: image resized to %dx%d" % (w,h) )                    
                strDest = "/tmp/temp.jpg"
                cv2.imwrite( strDest, img )
                strPathAndFilename = strDest
                if( bDeleteFileJustAfter ):
                    os.unlink( strPathAndFilename );
                
                
        self.prepare();
        if( self.tabletService == None ):
            return;
        strHttp = "http://";
        bUrl = False;
        if( strPathAndFilename[:len(strHttp)] != strHttp ):
            # local filename
            strLocalWebTmp = "/tmp/www/";
            bCopiedToTmp = False;
            strFilename = os.path.basename( strPathAndFilename );
            if( strPathAndFilename[:len(strLocalWebTmp)] != strLocalWebTmp ):
                if bVerbose: print( "INF: abcdk.display.showImage: copying file to %s" % strLocalWebTmp );                
                bRet = filetools.copyFile( strPathAndFilename, self.strWebLocalPath + strFilename );
                if( not bRet ):
                    return False;
                strRemoteFile = self.strWebRemotePath + strFilename;
                bCopiedToTmp = True;
            else:
                strRemoteFile = self.strWebRemotePath + strPathAndFilename.replace( strLocalWebTmp, "" );
        else:
            # url
            strRemoteFile = strPathAndFilename;
            bUrl = True;
        if bVerbose: print( "DBG: abcdk.display.show: showing '%s'" % strRemoteFile );

        self.tabletService.preLoadImage( strRemoteFile );
        self.tabletService.showImageNoCache( strRemoteFile ); # showImage => showImageNoCache
        if( bDeleteFileJustAfter and not bUrl ):
            time.sleep( 0.2 );
            if bVerbose: print( "INF: abcdk.display.showImage: unlinking: %s" % strPathAndFilename );
            os.unlink( strPathAndFilename );
            if( bCopiedToTmp ):
                strFileNameToUnlink = self.strWebLocalPath + strFilename;
                if bVerbose: print( "INF: abcdk.display.showImage: unlinking-2: %s" % strFileNameToUnlink );
                os.unlink( strFileNameToUnlink );
        return True;
    # showImage - end

    def hide(self):
        self.prepare();
        if( self.tabletService == None ):
            return;
        self.tabletService.hide();
# class Display - end

display = Display();

global_lastDisplayedMessageFullScreen = None
def writeMessageFullScreen( strMessage, color = (255,255,255), bDeleteFileJustAfter = True, nOffsetY = 0, strBackgroundImage = None ):
    """
    Write a message on the tablet - for debug or demo or ...
    - bDeleteFileJustAfter: did we delete the file from the disk after drawing it ?
    - nOffsetY: permits to change the height of the text
    """
    nTabletX = 800
    nTabletY = 480
    global global_lastDisplayedMessageFullScreen
    if( global_lastDisplayedMessageFullScreen == strMessage ):
        return;
    global_lastDisplayedMessageFullScreen = strMessage
        
    import numpy as np
    import cv2
    
    img = np.zeros( (nTabletY,nTabletX,3 ), np.uint8 );
    if( strBackgroundImage != None ):
        imgFile = cv2.imread( strBackgroundImage, cv2.CV_LOAD_IMAGE_COLOR );
        img = cv2.resize( imgFile, (nTabletX, nTabletY) );

    import image
    
    
    aLines = strMessage.split('\n')
    nDy = 40
    if( 1 ):
        nY = (nTabletY/2+nDy) - nDy*len(aLines);
        for strTxt in aLines:            
            if( len( strTxt ) < 1 ):
                continue
            # TODO: a better stuffs: using a getTextSize...
            rAutoTextSize = 32./len(strTxt); 
            if( rAutoTextSize > 4 ):
                rAutoTextSize = 4;        
            if( rAutoTextSize < 0.5 ):
                rAutoTextSize = 0.5;
            image.addTextAboveLocation( img, strTxt, pt = [nTabletX/2,nY+nOffsetY], color = color, rTextSize = rAutoTextSize );
            nY += rAutoTextSize*nDy
        
    import random
    import filetools
    strfilename = "/tmp/%s_tablet.jpg" % filetools.getFilenameFromTime();
    cv2.imwrite( strfilename, img );
    display.showImage( strfilename, bDeleteFileJustAfter = bDeleteFileJustAfter );
# writeMessageFullScreen - end

class MinttuSimpleDisplay:
    """
    Just a simple display based on Mintu:
    an image in full screen and an optionnal text, somewhere
    
    # stop/reset the tablet:
    qicli call ALTabletService._stopApk com.mbusy.minttu 
    qicli call ALTabletService.resetTablet
    fuser 3000/udp => affiche l'id qui utilise le port => kill it
    fuser 3001/tcp
    """
    def __init__( self ):        
        self.mm = None
        self.bBackgroundFlipFlop = False
        
    def __del__( self ):
        self.hide()
        
    def show( self ):
        if self.mm != None:
            return        
        print( "INF: MinttuSimpleDisplay.show: entering..." )        
        #~ try:
        if 1:
            import minttu.minttu_values as minttu_values
            self.mm = minttu.minttu_manager.MinttuManager()
            self.mm.launchApp()
            #self.mm.generateViewFromXml()        
            self.generalLayout = self.mm.createGeneralLayout()
            self.viewImg = self.mm.createImageView("Background", "")
            self.viewImg.setLayoutParams( minttu_values.MATCH_PARENT, minttu_values.MATCH_PARENT )
            self.viewImg.setLayoutGravity( minttu_values.CENTER )
            self.generalLayout.addImageView( self.viewImg )
            print(dir(self.viewImg))
            #self.viewImg
            self.viewTxt = self.mm.createTextView("MainText")
            self.viewTxt.setText( "(empty text)" )
            self.viewTxt.setLayoutParams( minttu_values.WRAP_CONTENT, minttu_values.WRAP_CONTENT )
            self.viewTxt.setLayoutGravity( minttu_values.CENTER )
            self.viewTxt.setTextSize( 50 )
            self.generalLayout.addTextView( self.viewTxt )
            self.mm.postLayout(self.generalLayout) # will launch the app
        #~ except BaseException, err:
            #~ print( "ERR: MinttuSimpleDisplay: %s" % str(err) )
            #~ self.hide()
        print( "INF: MinttuSimpleDisplay.show: end" )
        
        
    def hide( self ):
        if self.mm == None:
            return
        print( "INF: MinttuSimpleDisplay.hide: entering..." )
        self.mm.hide()
        self.mm.clear()
        self.mm.flushImages()
        self.mm.closeConnection()
        self.mm = None
        print( "INF: MinttuSimpleDisplay.hide: end" )

    def writeCentered( self, strTxt, nY = -1 ):
        """
        Write a text on the tablet
        nY: when set to -1: the text is printed vertical centered NDEV
        """
        self.show()
        self.mm.editElementText( "MainText", strTxt )
        
    def changeTextSize( self, nSize ):
        #self.viewTxt.setTextSize( nSize )
        #~ self.mm.minttuCommunicator.post({'editElementText':'MainText', 'textSize':nSize})
        #~ self.mm.minttuCommunicator.post({'editElementText':'MainText', 'newTextSize':nSize})
        pass # NDEV
        
    def setTextLayoutGravityBottom( self ):
        #~ import minttu.minttu_values as minttu_values
        #~ self.viewTxt.setLayoutGravity( minttu_values.BOTTOM )        
        pass # NDEV
        
    def changeBackgroundImage( self, strAbsoluteFilename ):
        """
        change the background ok
        return true when ok
        """
        
        print strAbsoluteFilename
        if not os.path.exists( strAbsoluteFilename ):
            return False
        
        self.show()
        
        self.bBackgroundFlipFlop = not self.bBackgroundFlipFlop
        if self.bBackgroundFlipFlop:
            strRessourceDesc = "background_1"
        else:
            strRessourceDesc = "background_2"
        
        print strRessourceDesc            
        self.mm.uploadImage( strRessourceDesc, strAbsoluteFilename )    
        time.sleep( 1.0 ) # 0.5 is not enough
        self.mm.editElementImage( "Background", strRessourceDesc )
        #~ self.generalLayout.setBackgroundImage( strRessourceDesc )
        return True
        
# class MinttuSimpleDisplay - end
        
minttuSimpleDisplay = MinttuSimpleDisplay()

def autoTest():
    pass

if( __name__ == "__main__" ):
    autoTest();


if( 0 ):
    strPathAndFilename = "http://perso.ovh.net/~mangedisf/mangedisque/images/bologo.gif";
    strHttp = "http://";
    bDiff = ( strPathAndFilename[:len(strHttp)] != strHttp );
    print( ":%s" % strPathAndFilename[:len(strHttp)]  );
    print( "bDiff: %s" % bDiff );