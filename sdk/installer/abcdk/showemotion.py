# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Show Emotion tools
# Author A. Mazel
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Emotion tools: a bunch of small tools, demo and research around emotion"

print( "importing abcdk.showemotion" );

# Change AL_DIR stuffs on the fly
#~ import os
#~ os.environ["AL_DIR"] = r"C:\Program Files\Aldebaran\naoqi-sdk-1.12-win32-vs2008"; # "caca";
#~ print( "aldir pas changed to : " + os.environ["AL_DIR"] );

import arraytools
import color
import constants
import debug
import emotion
import leds
import naoqitools
import poselibrary
import random
import speech
import test

import time


def showEmotionFull( arListRatio, rNeutral = 0., nTxtLang = -1, strSpecificTextToSay = "" ):
    "Mix a movement, a color eyes and a speech reflecting an emotion"
    "arListRatio: the ratio of each emotions: [Proud, Happy, Excitement, Fear, Sadness, Anger]"
    "             if sum is greater than 1, it would be normalised"
    "             if sum is lower than 1, a neutral position would be added"
    "rNeutral:    to force an addition of a proportion of the neutral pose"
    "nTxtLang:    lang to use, -1 => no text. currently handled: fr, en"
    print( "showEmotionFull: using emotions ratio: %s and neutral ratio: %5.2f, lang: %d and text: '%s'" % ( str( arListRatio ), rNeutral, nTxtLang, strSpecificTextToSay ) );
    
    aListFr = [ "Youpi!", "Super!", "Chouette!", "C'est trop cool!", "Oui, c'est ça!", "Bravo!", "Je suis bien, bien content."];
    aListEn = [ "Great!", "Cool!", "I'm happy!"];
    if( nTxtLang == -1 ):
        strSpecificTextToSay = "";
    else:
        if( strSpecificTextToSay == "" ):
            strSpecificTextToSay = speech.getEmoText( arListRatio, rNeutral );
    
    rTime = max( 1., len(strSpecificTextToSay)*0.2 );
    rTime = min( 2., rTime );
    print( "showEmotionFull: using time: %f" % rTime );
    
    anColor = emotion.interpolateColorEmotion( arListRatio, rNeutral );    
    leds.setColorToEyes( anColor, rTime, 0x3 );
    
    thePose1 = poselibrary.PoseLibrary.interpolateEmotion( arListRatio, rNeutral );
    rNeutralComplement = 1. - sum(arListRatio);
    #print( "rNeutralComplement: %f (list:%s)" % ( rNeutralComplement, arListRatio ) );
    rNeutralAlternate = rNeutralComplement * 1.2;
    #print( "rNeutralAlternate2: %f" % rNeutralAlternate );
    if( rNeutralAlternate < 0.01 ):
        rNeutralAlternate = 0.15;
        
    thePose2 = poselibrary.PoseLibrary.interpolateEmotion( arListRatio, rNeutralAlternate );
    thePoseNeutral = poselibrary.PoseLibrary.interpolateEmotion( [0.]*6, 1. );
    tts = naoqitools.myGetProxy( "ALTextToSpeech" );
    nMotionID = poselibrary.PoseLibrary.setPosition( thePose1, rTime, False );
    time.sleep( 0.2 ); # let a bit of time for the emotion to be launched
    if( strSpecificTextToSay != "" ):
        nTtsID = tts.post.say( strSpecificTextToSay );    
    bFlipFlop = False;
    while( tts.isRunning( nTtsID ) ):
        rTimeRespiration = 0.8;
        print( "showEmotionFull: Sending a new pose..." );
        if( bFlipFlop ):
            nMotionID = poselibrary.PoseLibrary.setPosition( thePose1, rTimeRespiration, True );
        else:
            nMotionID = poselibrary.PoseLibrary.setPosition( thePose2, rTimeRespiration, True );
        bFlipFlop = not bFlipFlop;            
    rTimeReturn = 1.6; # or else he will fall
    nMotionID = poselibrary.PoseLibrary.setPosition( thePoseNeutral, rTimeReturn, False );    
    
# showEmotionFull - end

def autoTest():
    if( not test.isAutoTest() and False ):
        return;
    test.activateAutoTestOption();
    print( "emotion.autotest..." );
    
    showEmotionFull( [0, 1, 0, 0, 0, 0], 0., nTxtLang = constants.LANG_FR );
    # showemotion.showEmotionFull( [0, 1, 0, 0, 0, 0], 0., nTxtLang = constants.LANG_FR, strSpecificTextToSay = "blablablabla blablablabla blablabalblablablalblallablalblablbalblablbalbalbalbalbal" );
    
# autoTest - end

# autoTest();