# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Color tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Color tools"
print( "importing abcdk.color" );

import numeric


def colorCompToHexa( rR, rG, rB ):
    "take 3 floats R,G,B [0.0,1.0] and create an hexa value from them"
    nColor = ( int(rR * 255.) << 16 ) | ( int(rG * 255.) << 8 ) | int( rB * 255. );
#    debug( "colorCompToHexa: r:%f, g:%f, b:%f => 0x%x" % ( rR, rG, rB, nColor ) );
    return nColor;
# colorCompToHexa - end

def colorHexaToComp( nColor ):
    "take an rgb int (24bits) and return [b,g,r]"
    rB = ( ( nColor & 0xFF ) ) / 255.;
    rG = ( ( nColor & 0xFF00 ) >> 8  ) / 255.;
    rR = ( ( nColor & 0xFF0000 ) >> 16  ) / 255.;
    aRet = [rB, rG, rR];
#    debug( "colorHexaToComp: 0x%x => %s" % ( nColor, str( aRet ) ) );
    return aRet ;
# colorHexaToComp - end

def ensureBrightOrDark( nColor, bBright = True ):
    """
    take a color, and ensure it's the bright version if bright is needed or dark if dark is needed
    eg: 
        ensureBrightOrDark( 0x0000FF, True ) => 0x8080FF
        ensureBrightOrDark( 0x0000FF, False ) => 0x0000FF
        ensureBrightOrDark( 0xFFFFFF, True ) => 0xFFFFFF
        ensureBrightOrDark( 0xFFFFFF, False ) => 0x606060        
    """
    #~ print( "ensureBrightOrDark: nColor: 0x%x, bBright: %s" % (nColor, bBright) );    
    rB = ( ( nColor & 0xFF ) );
    rG = ( ( nColor & 0xFF00 ) >> 8  );
    rR = ( ( nColor & 0xFF0000 ) >> 16  );
    
    #~ print( "ensureBrightOrDark: comp: r=%s, g=%s, b=%s" % (rR, rG, rB) );

    nMed = 0x7F+0xFF;
    if( bBright ):
        if( rB + rG + rR < nMed ):
            nColor = interpolateColor( nColor, 0xFFFFFF, 0.4 );
    else:
        if( rB + rG + rR >= nMed ):
            nColor = interpolateColor( nColor, 0x000000, 0.4 );
    #~ print( "ensureBrightOrDark: => nColor: 0x%x" % (nColor) );
    return nColor;
# ensureBrightOrDark - end
    
    
    
def darkenColor( nColor, rLuminosity ):
    "darken one color"
    "when rLuminosity is set to 0.0 => black; 1.0 => no change"
    if( rLuminosity > 1. ):
        rLuminosity = 1.;
    elif( rLuminosity < 0. ):
        rLuminosity = 0.;
    rB,  rG, rR = colorHexaToComp( nColor );
    rB *= rLuminosity;
    rG *= rLuminosity;
    rR *= rLuminosity;
    return colorCompToHexa( rR, rG, rB );
# darkenColor - end


def interpolateColor( nColorFrom, nColorTo, rRatio ):
    "interpolate a rgb color from nColorFrom to nColorTo"
    "when rRatio tend to 0.0 it will be a color equals to nColorFrom"
    "if it tends to 1.0 it will be nColorTo"
    rFromB,  rFromG, rFromR = colorHexaToComp( nColorFrom );
    rToB,  rToG, rToR = colorHexaToComp( nColorTo );
    rInvRatio = 1. - rRatio;
#    debug( "rRatio: %f, rinv: %f, rFromB: %f, rToB: %f" % (rRatio,rInvRatio, rFromB, rToB) );
    rToB = rFromB * rInvRatio + rToB * rRatio;
    rToG = rFromG * rInvRatio + rToG * rRatio;
    rToR = rFromR * rInvRatio + rToR * rRatio;

    return colorCompToHexa( rToR, rToG, rToB );
# interpolateColor - end

def interpolateColor3( nColorFrom, nColorMedian, nColorTo, rRatio ):
    "interpolateColor3: interpolate a rgb color from nColorFrom to nColorTo"
    "(passing by nColorMedian at ratio of 0.5)"
    if( rRatio < 0.5 ):
        nColor = interpolateColor( nColorFrom, nColorMedian, rRatio * 2. );
    else:
        nColor = interpolateColor( nColorMedian, nColorTo, ( rRatio - 0.5 ) * 2. );        
    return nColor;
# interpolateColor3 - end

def yuvToRgb( yuv ):
    "take an yuv array [y,u,v] (0..255) and return it in [r,g,b] (0..255)"
    "Attended value:"
    "red: [255,0,0] => [0°=>0,255,255]"
    y, u, v = yuv;
    r = numeric.limitRange( int( 1.164*(y - 16) + 1.596*(v-128) ), 0, 255 );
    g = numeric.limitRange( int( 1.164*(y - 16) - 0.813*(u-128) - 0.391*(v-128) ), 0, 255 );
    b = numeric.limitRange( int(1.164*(y - 16) + 2.018*(u-128) ), 0, 255 );
    return [ r, g, b];
# yuvToRgb - end

# from http://www.righto.com/java/ColorSelector.java
"""
	public void fromRGB(int vals[])  # RGB to HSV
    {
		float v;
		int max=(int)max(max(vals[RED],vals[GRN]),vals[BLU]);
		int min=(int)min(min(vals[RED],vals[GRN]),vals[BLU]);
		vals[VAL] = max;
		if (max==0) {
			vals[SAT]=0;
		} else {
			vals[SAT] = (int)((max-min)*255/(float)max);
		}
		if (vals[SAT]==0) {
			vals[HUE]=0;
		} else {
			float rc,gc,bc;
			rc = (max-vals[RED])/(float)(max-min);
			gc = (max-vals[GRN])/(float)(max-min);
			bc = (max-vals[BLU])/(float)(max-min);
			float h;
			if (vals[RED]==max) {
				h = bc-gc;
			} else if (vals[GRN]==max) {
				h=2+rc-bc;
			} else {
				h=4+gc-rc;
			}
			if (h<0) {
				h += 6;
			}
			vals[HUE] = (int)(h/6.*255);
"""

def rgbToHsv( rgb ):
    "take an rgb array [r,g,b] (0..255) and return it in [h,s,v] (0..255)"
    "Attended value:"
    "red: [255,0,0] => [0°=>0,255,255]"
    "green: [0,255,0] => [120°=>85,255,255]"
    "blue: [0,0,255] => [240°=>170,255,255]"
    "light blue: [40,128,255] => [215°=>152, 84.3% => 214.96 , 255]"
    "grey: [128,128,128] => [0, 0, 128]"
    "light orange [255,180,80] => [34° => 24, 68.6% => 174.9, 255]"
    "light green [120,255,80] => [106° => 75, 68.6% => 174.9, 255]"
    "white [255,255,255] => [0, 0, 255]"
    "purple/magenta [255,0,255] => [-60° => 212.5, 255, 255]"
    "cyan [0,255,255] => [180° => 128, 255, 255]"
    "yellow [255,255,0] => [60° => 42.5, 255, 255]"    
    "army green [50,125,100] => [160° => 113, 153, 125]" # this one is wrong (113 instead of 98) [ca dépend des sources] !!!
    "dark green (seen as red [63,64,65] => [210° => 149, 7, 63]" # this one is slightly wrong (149 instead of 164)
    "dark grey [19,11,0] => [33° => 24, 255, 19]" # this one is wrong (1 instead of 24)

    """
    V = max(R,G,B)
    S = (V-min(R,G,B))/V if V<>0, 0 otherwise 
    H =

        (G - B)/6/S, if V=R; 
        1/2+(B - R)/6/S, if V=G; # en fait ca marche mieux ca avec 1/3 qu'avec 1/2, pfff...
        2/3+(R - G)/6/S, if V=B. 
    """

    r,g,b = rgb;
    
    v = max(r,g,b);
    nMinVal = min(r,g,b);
    if( v == 0 ):
        s = 0;
    else:
        s = ( v - nMinVal ) * 255 / v;

    if( s == 0 ):        
        h = 0;
    else:
        # first methods (bug 199,11,0 => 1, 255, 19)
        #~ if( v == r ):
            #~ h = (g - b)*42/s; # c'est plus drole de mettre des 42!
        #~ elif( v == g ):
#~ #            h = 127 + ((b - r)/6)/s; # la il y a un truc de faux!
#~ #            h = h * 255 / 360;
            #~ h = 85 + ((b - r)*42)/s;
        #~ else:
            #~ h = 170 + ((r - g)*42)/s;
    #~ if( h < 0 ):
        #~ h += 255;
        
        rc = (v - r) / (float)( v - nMinVal) ;
        gc = (v - g) / (float)(v - nMinVal );
        bc = (v - b) / (float)( v - nMinVal );
        if( r == v):
            h = bc-gc;
        elif ( g == v ):
            h=2+rc-bc;
        else:
            h=4+gc-rc;
        if( h<0 ):
            h += 6;
        h = (int)(h*255/6);
    return [h,s,v];
# def rgbToHsv - end

def getColorNameFromHSV( hsv, nIndexLang = 0, bHueIsOn360 = False ):
    "take a hue value [h,s,v](0..255)"
    "return [color, rDist, color described], with:"
    " - color           : the name of the nearest color (multilang)"
    " - dist            : distance to the plain color [0,1]"
    " - color described : the name of the nearest color (multilang), with an idea of the distance (eg: blancheatre, greeny)."
    aHueReferences256 = [
        [217, 14],      # 'Red'        
        [14, 29],       # 'Orange'
        [29, 49],       # 'Yellow'
        [49, 120],      # 'Green'
        [120, 177],     # 'Blue'
        [177, 217],     # 'Purple
    ];    
    
    aHueReferences360 = [
        [305, 20],      # 'Red'        
        [20, 41],       # 'Orange'
        [41, 69],       # 'Yellow'
        [69, 169],      # 'Green'
        [169, 249],     # 'Blue'
        [249, 305],     # 'Purple
    ];    
    
    
    aColorList = [
        [ 'Red' , 'Rouge' ],
        [ 'Orange' , 'Orange' ],
        [ 'Yellow' , 'Jaune' ],
        [ 'Green' , 'Vert' ],
        [ 'Blue', 'Bleu' ],
        [ 'Purple' , 'Violet' ],
    ];
    
    nDefaultColor = 0; # if not found => red
    
    nColorValMax = 255;
    if( bHueIsOn360 ):
        aHueReferences = aHueReferences360;
        nColorValMax = 359;
    else:
        aHueReferences = aHueReferences256;
    
    
    # handle "no color" color
    
    nSatu = hsv[1];
    nValue = hsv[2];    
    if( nSatu < 60 or nValue < 50 ): # Alma: add a threshold on nValue, so that too dark color will be seen as dark
        aGreyLevel = [
            [ 'Black',  'Noir' ],
            [ 'Dark Grey',  'Gris foncé' ],
            [ 'Grey',  'Gris' ],
            [ 'Light Grey',  'Gris clair' ],
            [ 'White',  'Blanc' ],
        ];
        
        nRange = (255) / (len( aGreyLevel ) - 0);
        nIndex = nValue / nRange;
        if( nIndex >= len( aGreyLevel ) ):
            nIndex = len( aGreyLevel ) - 1;
            
        # On border area, confidence is the distance from the border. On inner area it's the difference with the median value
        if( nIndex == 0 ):
            rConfidence = nValue / float( nRange );
        elif( nIndex == len( aGreyLevel ) - 1 ):
            rConfidence = (255-nValue) / float( nRange );
        else:
            rConfidence = abs( (nValue - (nIndex*nRange) - nRange/2 ) / float( nRange ) ) * 2;
            
        strColorName = aGreyLevel[nIndex][nIndexLang];
        nHue = -1; # for debugging only
    # nSatu < 40
    else:    
        strColorName = None
        rConfidence = None
        nHue = hsv[0];
        # Then look up into the reference hue colors
        for i in range( len( aHueReferences ) ):
          v = aHueReferences[i];
          if v[0] <= nHue < v[1]:
              strColorName = aColorList[i][nIndexLang];
              center = float(v[0]+v[1])/2.0
              rConfidence = abs(nHue - center) / (v[1] - center)
              break;

        # If no color found here, then it's Red, since nHue is around zero
        if strColorName == None:
    #        print( "strColorName: none!!! (red?)" );
            strColorName = aColorList[nDefaultColor][nIndexLang];
            v = aHueReferences[nDefaultColor];
            if nHue >= v[0]:
                nHue -= nColorValMax;
            v = [v[0]-nColorValMax, v[1]]        
            center = float(v[0]+v[1])/2.0
            rConfidence = abs(nHue - center) / (v[1] - center)
    # nSatu < 40 - else end
    
    # add presque, nearly, atre, ...
    strColorNameConfidenceDescribed = strColorName;
    if( rConfidence > 0.5 ):
        if( nIndexLang == 1 ):
            # french
            #strColor = "presque " + strColor;
            if( strColorName[-1] == 'c' ):
                strColorNameConfidenceDescribed = strColorName + "hatre";
            elif( strColorName[-3:] == 'air' or strColorName[-1] == 't'):
                strColorNameConfidenceDescribed = "presque " + strColorName;
            else:
                strColorNameConfidenceDescribed = strColorName + "atre";        
        else:
            # english ?
            strColorNameConfidenceDescribed = strColorName + "-ish";

    print("color.getColorNameFromHSV: Hue: %d, Color: %s, variance: %s, colordesc: %s" % (nHue, strColorName, str(rConfidence), strColorNameConfidenceDescribed))
    return [strColorName, rConfidence, strColorNameConfidenceDescribed ];
# getColorNameFromHSV - end

def freenectRgbToDist( rgb ):
    "take a [r,g,b] in pseudocolor from the depth camera, and turn it to a distance"
    "return a distance value between 0 and 5*256+254 (to be further calibrated)"
    "Attended value:"
    "white  : [ff,ff,ff] => 0"
    "red    : [ff,00,00] => 255"
    "yellow : [ff,ff,00] => 256*1+255"
    "green  : [00,ff,00] => 256*2+255"
    "cyan   : [00,ff,ff] => 256*3+255"
    "blue   : [00,00,ff] => 256*4+255"
    "black from blue   : [00,00,1] => 5*256+254"
    "WARNING: NOT FULLY TESTED !!!"
    r, g, b = rgb;
    if( r == 0xff ):
        if( g == b ):
            return 0xff-g;
        return g+0x100*1;
    if( g == 0xff ):
        if( b == 0 ):
            return (0xff-r) + 0x100*2;
        return b + 0x100*3;
    if( g != 0 ):
        return (0xff-g) + 0x100*4;
    return (0xff-b) + 0x100*5;
# freenectRgbToDist - end

def getColorValueFromName( strName ):
    """
    return rgb color from the (english) name of a color (cf translate for every country to english)
    """
    dictColor = {
        "blue": 0x0000FF,
        "red": 0xFF0000,
        "green": 0x00FF00,
        "yellow": 0xFFFF00,
        "purple": 0x801187,
        "pink": 0xff00ff,
        "orange": 0xff9e00,
        "brown": 0x733300,
        "black": 0x000000,
        "grey": 0x7F7F7F,        
        "white": 0xFFFFFF,
    };
    try:
        nColor = dictColor[strName.lower()];
        return nColor;
    except:
        pass
    print( "WRN: abcdk.color.getColorValueFromName: don't know color '%s'" % strName );
    return -1;
# getColorValueFromName - end
            

def autoTest():
    nMed = interpolateColor( 0x0080E0, 0xE04020, 0.5 );
    print( "nMed: 0x%x" % nMed );
    assert( nMed == 0x706080 );
    
    nMed = darkenColor( 0xE08044, 0.25 );
    print( "nMed: 0x%x" % nMed );
    assert( nMed == 0x382011 );


    hsv = rgbToHsv( [255,0,0] );
    print str( hsv )
    assert( [0,255,255] == hsv );
    
    hsv = rgbToHsv( [40,128,255] );
    print str( hsv )
    assert( [152,215,255] == hsv );

    hsv = rgbToHsv( [255,0,255] );
    print str( hsv )
    assert( [212,255,255] == hsv );

    hsv = rgbToHsv( [50,125,100] );
    print str( hsv )
    assert( [113, 153, 125] == hsv );
    
    colorInfo = getColorNameFromHSV( [359,200,200], 0, True );    
    assert( "Red" == colorInfo[0] );
    colorInfo = getColorNameFromHSV( [180,200,200], 1, True );    
    assert( "Bleu" == colorInfo[0] );    
    colorInfo = getColorNameFromHSV( [127,200,200] );
    print( str( colorInfo ) );
    assert( "Blue" == colorInfo[0] );
    assert( "Blue-ish" == colorInfo[2] );
    colorInfo = getColorNameFromHSV( [127,200,200] );
    assert( "Blue" == colorInfo[0] );
    
    
    # My black shirt:
    # uvmedian: [23, 120, 135]
    # rgb: [19, 11, 0]; hsv: [1, 255, 19]
    # col: 'Rouge', dist: 0.500000 
    # but must be Black !!! [ok]
    
    rgb = yuvToRgb( [23,120,135] );
    print str( rgb )
    assert( [19,11,0] == rgb );
    hsv = rgbToHsv( rgb );
    print str( hsv )
    assert( [24,255,19] == hsv ); #should be h 24/235 !!!
    colorInfo = getColorNameFromHSV( hsv );
    assert( "Black" == colorInfo[0] );

    # my bleu marine "esprit" top
    # => red-ish ! 
    # instead of brown "Wood Bark"
    hsv = rgbToHsv( [42,30,27] );
    print str( hsv )
    assert( [8, 91, 42] == hsv );
    colorInfo = getColorNameFromHSV( hsv );
    assert( "Black" == colorInfo[0] );
    
    # my black shirt
    # => red-ish ! 
    # instead of brown "Cowboy"
    hsv = rgbToHsv( [69,57,54] );
    print str( hsv )
    assert( [8, 55, 69] == hsv );
    colorInfo = getColorNameFromHSV( hsv );
    assert( "Dark Grey" == colorInfo[0] );    
    
    
    hsv = [15,51,55];
    colorInfo = getColorNameFromHSV( hsv, 1 );
    #assert( "Orange" == colorInfo[0] );
    #assert( "Orangeatre" == colorInfo[2] );
    assert( "Gris foncé" == colorInfo[0] );
    assert( "Gris foncéatre" == colorInfo[2] );
    
    
    assert( freenectRgbToDist( [0x00,0x00,0xff] ) == 0x100*5 );
    assert( freenectRgbToDist( [0xff,0x00,0x00] ) == 0xff );
    assert( freenectRgbToDist( [0xff,0xff,0x00] ) == 0x100*1+0xff );
    assert( freenectRgbToDist( [0xff,0xff,0xff] ) == 0 );
    assert( freenectRgbToDist( [0xff,0x20,0x20] ) == 0xff-0x20 );
    assert( freenectRgbToDist( [0x00,0x00,0x01] ) == 0x100*5+0xfe );
       
# autoTest- end

# autoTest();