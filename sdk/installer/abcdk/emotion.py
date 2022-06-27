# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Emotion tools
# Author A. Mazel
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Emotion tools: a bunch of small tools, demo and research around emotion"

print( "importing abcdk.emotion" );

import arraytools
import color
import debug
import test


def getListColorEmotion():
    "return a list of 6 eyes leds configurations" 
    import emotion_list_eyes;
    listEmo = [];
    listEmo.extend( emotion_list_eyes.listEmotionEyes ); # listEmo = list_emotion_eyes.listEmotionEyes ne ferait qu'un pointeur sur l'objet, et donc quand on append la neutralpose, ca ajoute a la liste du module, beurk.
    
    # the file can contains one light (the eyes has a plain color) or 8 lights
    # so we expand it:
#    print( "listEmo: %d" % len( listEmo ) );
    for i in range( len( listEmo ) ):
        if( len( listEmo[i] ) == 1 ):
            listEmo[i] = arraytools.arrayCreate( 8, listEmo[i][0] );
#    print( "listEmo: %d" % len( listEmo ) );
    return listEmo;
# getListColorEmotion - end


def interpolateColorEmotion( arListRatioParams, rNeutral = 0. ):
    "create a color for each eyes mixed from 6 emotions colors and a neutral"
    "arListRatio: the ratio of each emotions: [Proud, Happy, Excitement, Fear, Sadness, Anger]"
    "             if sum is greater than 1, it would be normalised"
    "             if sum is lower than 1, a neutral position would be added"
    "rNeutral:    to force an addition of a proportion of the neutral pose"
    "return a RGB hexa code describing the left eyes (use mirror for right eye)"
    
    debug.debug( "interpolateColorEmotion( %s, %f )" % ( str( arListRatioParams ), rNeutral ) );
    
    arListRatio = arraytools.dup( arListRatioParams );
    # preparation of the ratio
    rSum = arraytools.arraySum( arListRatio );
    rEpsilon = 0.001;
    
    if( rNeutral < rEpsilon and rSum < 1. ):
        rNeutral = 1. - rSum;
    rSumTotal = rSum + rNeutral;
    
    if( rSumTotal > 1. ):
        # normalisation
        for i in range( len( arListRatio ) ):
            arListRatio[i] /= rSumTotal;
        rNeutral /= rSumTotal;

    # push zeroes for others emotions:
    for i in range( len( arListRatio ), 6 ):
        arListRatio.append( 0. );
        
    anColorNeutral = arraytools.arrayCreate( 8, 0x0000FF );

    listColorEmotion = getListColorEmotion();

    if( rNeutral > 0.001 ):
        listColorEmotion.append( anColorNeutral );
        arListRatio.append( rNeutral );

    

    anColor = arraytools.arrayCreate( 8, [0.,0.,0.] );

    #~ print( "arListRatio: %s" % str( arListRatio ) );
    #~ print( "listColorEmotion: %s" % str( listColorEmotion ) );
    #~ print( "anColorNeutral: %s" % str( anColorNeutral ) );    
    #~ print( "anColor: %s" % str( anColor ) );
    
    # hexa to comp rgb
    arListColorEmotionRGB = [];
    for nNumEmotion in range( len( listColorEmotion ) ):
        arListColorEmotionRGB.append( [] );
        for led in listColorEmotion[nNumEmotion]:
            arListColorEmotionRGB[nNumEmotion].append( color.colorHexaToComp( led ) );
    
    # interpolation stuff    
    for nNumEmotion in range( len( arListColorEmotionRGB ) ):
        for nNumLed in range( len( anColor ) ):
            for nNumComposanteRGB in range( 3 ):
                anColor[nNumLed][nNumComposanteRGB] += arListRatio[nNumEmotion] * arListColorEmotionRGB[nNumEmotion][nNumLed][nNumComposanteRGB];

#    print( "anColor2: %s" % str( anColor ) );
    
    # median and rgb to hexa
    for nNumLed in range( len( anColor ) ):
        # we haven't to divide in rgb space !
        #~ for nNumComposanteRGB in range( 3 ):
            #~ anColor[nNumLed][nNumComposanteRGB] = anColor[nNumLed][nNumComposanteRGB]  / len( arListColorEmotionRGB );
        anColor[nNumLed] = color.colorCompToHexa( anColor[nNumLed][2], anColor[nNumLed][1], anColor[nNumLed][0] );
        
    return anColor;
# interpolateColorEmotion - end

def autoTest():
    if( not test.isAutoTest() and False ):
        return;
    test.activateAutoTestOption();
    print( "emotion.autotest..." );
    anColor = interpolateColorEmotion( [1, 0, 0, 0, 0, 0] );
    print( "anColor: " + str( anColor ) );
   
# autoTest - end

# autoTest();