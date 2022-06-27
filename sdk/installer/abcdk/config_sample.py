# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Config file
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Configure you preferences"""

import constants

#
# global settings
#

# choose here the default language of Nao
#nNumLang = LANG_EN; 
nStrLoc = constants.LOC_CHI;
nSpeakVolume = 140;
nSpeakPitch 	= 100;
nSpeakSpeed 	= 85;
nSpeakSpeedUI 	= 160;

bPrecomputeText = True;     # activate it to precompute text in LocalizedText and various speech
bRemoveDirectPlay = False;  # activate it to remove all direct play that directly call aplay, mpg321 with shell command

# Debug mode add extra print in various modules
bDebugMode = False;

# This option change the creation of the proxy, move it to False to cut/paste code from choregraphe box directly in a python shell
bInChoregraphe = True; # default True

# Defaut adress when bInChoregraphe is False (to test it from outside choregraphe)
strDefaultIP = "localhost";
nDefaultPort = 9559;

# Various debug
bTryToReplacePopenByRemoteShellCall = False
