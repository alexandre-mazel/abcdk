# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Config file
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Configure you preferences"""
print( "importing abcdk.config" );

import constants

#
# global settings
#

# choose here the default language of Nao
#nNumLang = LANG_EN; 
nStrLoc = constants.LOC_CHI;
nSpeakVolume = 140;
nSpeakPitch 	= 100;
nSpeakSpeed 	= 100;
nSpeakSpeedUI 	= 90;

nFavoriteEyesColor = 0x000020;

bPrecomputeText = True;     # activate it to precompute text in LocalizedText and various speech
bRemoveDirectPlay = False;  # activate it to remove all direct play that directly call aplay, mpg321 with shell command

# Debug mode add extra print in various modules
bDebugMode = True;

# This option change the creation of the proxy, move it to False to cut/paste code from choregraphe box directly in a python shell
bInChoregraphe = True; # default True
#bInChoregraphe = False; # default True
# Defaut adress when bInChoregraphe is False (to test it from outside choregraphe)
#strDefaultIP = "10.0.254.117"
strDefaultIP = "127.0.0.1"

nDefaultPort = 9559;

# Various debug
bTryToReplacePopenByRemoteShellCall = True


# to debug directly from some python IDE (Scite?) from your computer, connected to some real NAO
#bInChoregraphe = False;
#strDefaultIP = "NaoAlex16.local"; # set here your specific configuration

bAutoTestEnabled = False; # enable it to have autotest

def setDebug( bNewState ):
    bNewState = bool(bNewState);
    print( "abcdk.config.setDebug: set debug mode to %s" % str( bNewState ) );
    bDebugMode = bNewState;
# setDebug - end

def setInChoregraphe( bNewVal ):
    global bInChoregraphe;
    bNewVal = bool(bNewVal);
    print( "INF: abcdk.config.setInChoregraphe: changing from %s to %s" % (bInChoregraphe, bNewVal) );
    bInChoregraphe = bNewVal;

def setDefaultIP( strNewDefaultIP, bSetNotInChoregraphe = False ):
    global strDefaultIP;
    print( "INF: abcdk.config.setDefaultIP: changing from %s to %s" % (strDefaultIP, strNewDefaultIP) );
    strDefaultIP = strNewDefaultIP;
    if( bSetNotInChoregraphe ):
        setInChoregraphe( False );
    import system
    system.reloadSystemPrecalcGlobal();