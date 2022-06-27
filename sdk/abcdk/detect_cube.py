import copy
import cv2
import math
import numpy as np
import time

def dist2D( x1, y1, x2, y2 ):
    dx = x1-x2
    dy = y1-y2
    return math.sqrt( dx*dx+dy*dy)
    
def dist2D_squared( x1, y1, x2, y2 ):
    dx = x1-x2
    dy = y1-y2
    return dx*dx+dy*dy



def mergeSimilarZone( aaZone, im_rgb_debug = None ):
    """
    analyse zone, merge near one who are smaller than others
    cf orderZone for aaZone description
    return modified aaZone
    """
    bVerbose = 1
    # first compute average size:
    rSum = 0
    nNbr = 0
    for zones_per_color in aaZone:
        for zone in zones_per_color:
            x,y,a,p = zone
            rSum += a
            nNbr += 1
    if( nNbr < 1 ):
        return aaZone;
        
    rAreaAvg = rSum / nNbr
    rApproxAvgDiam = int(math.sqrt(rAreaAvg)/math.pi) * 2
    
    # now look for smaller one
    for aZonePerColor in aaZone:
        nNumZone = 0
        while nNumZone < len(aZonePerColor):
            x,y,a,p = aZonePerColor[nNumZone]
            if( a < 0.8*rAreaAvg):
                # find a zone next to this one (previous where already handled)
                nNumOtherZone = nNumZone + 1
                while nNumOtherZone < len(aZonePerColor):
                    xo, yo, ao, po = aZonePerColor[nNumOtherZone]
                    rDist = dist2D( x, y, xo, yo );
                    if( rDist < rApproxAvgDiam+1 ):
                        # fusion zone
                        print( "fusion x: %d,y: %d with x: %d,y: %d, dist: %f, avgdiam: %f" % (x,y,xo,yo,rDist,rApproxAvgDiam) )
                        aZonePerColor[nNumZone] = ( (x+xo)/2, (y+yo)/2, a+ao, (p+po)/1.5 ) # p is roughly approximated
                        del aZonePerColor[nNumOtherZone]
                    else:
                        nNumOtherZone += 1
                
                if( bVerbose and im_rgb_debug != None ):
                    x,y,a,p = aZonePerColor[nNumZone]
                    nApproxRadius = int(math.sqrt(a)/math.pi)
                    print nApproxRadius
                    cv2.circle( im_rgb_debug, (int(x),int(y)), nApproxRadius,  (255, 255, 0), 5 )
            # if smaller!
            if( bVerbose and im_rgb_debug != None ):
                # render a circle with approx avg diam around each zone
                x,y,a,p = aZonePerColor[nNumZone]
                cv2.circle( im_rgb_debug, (int(x),int(y)), rApproxAvgDiam,  (0, 255, 255), 1 )
            
            nNumZone += 1
            
    return aaZone
# mergeSimilarZone - end

def findNearestZone( aaZone, xp, yp ):
    """
    find the nearest zone of a position (but not the current point)
    cf orderZone for aaZone description
    return: the distance in pixels
    """
    rDistMin = 10e6
    for aZonePerColor in aaZone:
        nNumZone = 0
        for zone in aZonePerColor:
            x,y,a,p = zone
            if( xp != x and yp != y ):
                rDist = dist2D_squared( xp, yp, x, y )
                if( rDist < rDistMin ):
                    rDistMin = rDist
                    
    return math.sqrt(rDistMin);
            
    
    
def removeIsolatedZone( aaZone ):
    """
    if a zone is far from the nearest, remove it
    cf orderZone for aaZone description
    """
    nNumColor = 0;
    while nNumColor < len(aaZone):
        nNumZone = 0
        while nNumZone < len(aaZone[nNumColor]):
            x,y,a,p = aaZone[nNumColor][nNumZone]
            rDist = findNearestZone(aaZone, x, y )
            #~ print( "removeIsolatedZone: min dist to zone: %s" % rDist )
            if( rDist > 70 ):
                print( "removeIsolatedZone: removing isolated zone at dist: %s" % rDist )
                del aaZone[nNumColor][nNumZone]
            else:
                nNumZone += 1
        # while each zone - end
        nNumColor += 1
    # while each color - end
    return aaZone
# removeIsolatedZone - end
    
    
def orderZone( aaZone ):
    """
    take a list of list of zone and order them in space
        - aaZone: [t1,t2,...] with t1: [a1, a2, ....] with a1: [xcenter, y center, area, perimeter]
    return:
        the zone ordered in left-right top-bottom:
            [[nt1,a1], [nt2,a2], ...] with nt1 the number of the type [0..n-1] (ie from which list number was it taken) and a1 the zone from input (but a1 is not the same one a1 then the one from input)
    """
    # work on copy
    aaZoneCpy = copy.deepcopy(aaZone)
    aaZone = aaZoneCpy;
    
    aaOut = []
    #we'll use a sort method with a bigger weight on the X
    nNbrFaceFound = 0
    while 1:
        rDistMin = 10e6
        nNumColor = 0
        nNumColorMin = -1
        nNumZoneMin = -1
        while nNumColor < len(aaZone):
            nNumZone = 0
            while nNumZone < len(aaZone[nNumColor]):
                x,y,a,p = aaZone[nNumColor][nNumZone]
                if (nNbrFaceFound%3) == 0:
                    # first of the line
                    rDistToCorner = x+y*1 # so y cost more; # 2.5 is a nice value!
                    rDist = rDistToCorner
                else:
                    #rDistToCorner = x+y*2.5 # so y cost more # 2.5 is a nice value!
                    xFirst = aaOut[nNbrFaceFound-1][1][0]
                    yFirst = aaOut[nNbrFaceFound-1][1][1]
                    rDistToFirstOfLine = abs(xFirst-x)+abs(yFirst-y)*1.355 # for 0078, *1.5 => *1.355
                    rDist = rDistToFirstOfLine
                    if( x < xFirst ):
                        rDist += 5000 # the ugly way to do aleft right ordering !!!
                if( rDist < rDistMin ):
                    rDistMin = rDist;
                    nNumColorMin = nNumColor
                    nNumZoneMin = nNumZone
                nNumZone += 1
            # while each zone - end
            nNumColor += 1    
        # while each color - end
        if( nNumColorMin == -1 ):
            break # finiched!
        
        aaOut.append( [ nNumColorMin,aaZone[nNumColorMin][nNumZoneMin] ] )
        del aaZone[nNumColorMin][nNumZoneMin]
        nNbrFaceFound += 1
    # while - end
    return aaOut;
# orderZone - end    

def isWellOrdered( aOrdered ):
    """
    check the 9 faces are well ordered (each center is roughly at center and ...)
    aOrdered: an ordered list of pair, as the one outputted by orderZone
    """
    rThreshold = 25
    for i in range(3):
        # check each line has a center roughly around middle of the line
        f1 = aOrdered[i*3+0][1]
        f2 = aOrdered[i*3+1][1]
        f3 = aOrdered[i*3+2][1]
        xc = (f1[0]+f3[0])/2
        yc = (f1[1]+f3[1])/2
        rDiff = dist2D( xc,yc, f2[0], f2[1] )
        print( "rDiff: %s" % rDiff )
        if( rDiff > rThreshold ):
            return False
            
    for i in range(3):
        # check each line has a center roughly around middle of the line
        f1 = aOrdered[0*3+i][1]
        f2 = aOrdered[1*3+i][1]
        f3 = aOrdered[2*3+i][1]
        xc = (f1[0]+f3[0])/2
        yc = (f1[1]+f3[1])/2
        rDiff = dist2D( xc,yc, f2[0], f2[1] )
        print( "rDiff: %s" % rDiff )
        if( rDiff > rThreshold ):
            return False
            
    return True
# isWellOrdered - end



def detectCube( im, strImgNameDebug = "tmpCube.jpg", bVerbose=False ):
    """
    detect a rubics cube.
    return:
        []: if no cube
        [col_conf1, col_conf2, ...]
        with: col_confx:
            a pair of color letter capitalised [White, Yellow, Green, Blue, Orange, Red] and a confidence [0..1] 
    """
    im_rgb_debug = None # when no debug, this is set to None
    
    im = cv2.bilateralFilter(im,9,75,75)  # beautifuler, but not more results
    #im = cv2.fastNlMeansDenoisingColored(im,None,10,10,7,24) # takes 12sec on my computer

    
    im_hsv = cv2.cvtColor(im,  cv2.COLOR_BGR2HSV)
    #~ im_h = im_hsv[:,:,0]
    #~ print im_h
    if( 0 ):
        mask = im_hsv[:,:,1] < 80
        im_hsv[mask,0] = 0
        
    
    aListColor = ['W', 'Y', 'G', 'B', 'O', 'R'];
    
    # for debuging classic color to draw them
    aListColorBGR_Std = [
                        [ 255,255,255],
                        [0, 255,255],
                        [0,255,0],
                        [255,0,0],
                        [0,128,255],
                        [0,0,255],
    ]
    
    # those are color from photoshop: 0..360 and 0..100
    # seems like ps and cv hasn't the same convert algo...
    #~ aListHue = [
                        #~ [180, 10], 
                        #~ [50, 94], 
                        #~ [132,82],
                        #~ ];

    # by hand values [H min, H Max], [S min, S, Max]
    
    # my old small corto cube "unofficial"
    """
    aListHue = [                        
                        [[-1,190], [-1,95]],  # Hm=40 was enough but for 042 => 0
                        [[20,50], [130,256]],
                        [[60,83], [140,256]],
                        [[90,110], [180,256]],
                        [[4,20], [180,256]],
                        [[-1,5], [180,256]],
    ];
    """    
    
    aListHue = [                        
                        [[0,190], [0,40]],  # Hm=40 was enough but for 042 => 0
                        [[20,50], [130,256]],
                        [[70,85], [180,256]],
                        [[100,120], [180,256]],
                        [[0,10], [180,256]],
                        [[-1,5], [180,256]],
    ];

    im_bw = cv2.cvtColor(im_hsv, cv2.COLOR_BGR2GRAY)                                
    #~ im_bw[:]=0;    
    if( bVerbose ):
        # debug chan per chan
        im_rgb_debug = cv2.cvtColor(im_bw, cv2.COLOR_GRAY2BGR)
        im_rgb_debug[::] = 0;
    
    h = im.shape[0]
    w = im.shape[1]
    xCenter = w/2;
    yCenter = h/2;
    
    
    aListArea = []; # a list of area per color [x,y,area, perimeter]
    
    if( bVerbose ): cv2.imwrite( "/tmp/%s" % strImgNameDebug.replace( ".", ("_hsv.")), im_hsv );
    
    for i in range(len(aListHue)):        
        
        if( bVerbose ): print( "\ncolor %d: %s" % (i, aListColor[i]) )
            
        aListArea.append([])
        im_bw[:] = 0
        aH,aS = aListHue[i]
        #~ aH,aS = aListHue[1] # to visualize only one channel
        
        maskH = ( im_hsv[:,:,0] >= aH[0] ) & ( im_hsv[:,:,0] < aH[1] )
        maskS = ( im_hsv[:,:,1] >= aS[0] ) & ( im_hsv[:,:,1] < aS[1] )
        mask = maskH & maskS
        
        if( i == 0 ):
            maskV = ( im_hsv[:,:,2] > 200 ) # prevent the 001-002 to work (needs whity > 110 of lum to work)
            mask = mask & maskV

        if( i == 4 ):
            maskV = ( im_hsv[:,:,2] > 220 )
            mask = mask & maskV

        if( i == 5 ):
            maskV = ( im_hsv[:,:,2] < 170 )
            mask = mask & maskV
            
        
        if( 1 ):
            # cropping for a specific positionning
            mask[0:140,0:w] = 0
            mask[h-40:h,0:w] = 0
            mask[0:h,0:150] = 0
            mask[0:h,w-150:w] = 0
                        
        #~ im_hsv[:,:,0] = 0        
        #~ im_hsv[:,:,1] = 0
        #~ im_hsv[:,:,2] = 0
        im_bw[mask] = 255
        
        if( i == 5 ):
            # alternate mask (h: 177, s:194)
            maskH = ( im_hsv[:,:,0] >= 170 ) & ( im_hsv[:,:,0] < 190 )
            maskS = ( im_hsv[:,:,1] >= 200 ) & ( im_hsv[:,:,1] < 256 )
            mask = maskH & maskS
            im_bw[mask] = 255
            
        
        if( bVerbose ): cv2.imwrite( "/tmp/%s" % strImgNameDebug.replace( ".", ("_mask_%d." % i)), im_bw );
        
        element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        for nErosion in range(1):
            im_bw = cv2.erode(im_bw, element,iterations=2)
            if i != 0: # white melt with background
                im_bw = cv2.dilate(im_bw, element,iterations=1)
                
        if( bVerbose ): cv2.imwrite( "/tmp/%s" % strImgNameDebug.replace( ".", ("_mask_%d_logic." % i)), im_bw );

        im_bwtemp = np.copy(im_bw)
        contours, hierarchy = cv2.findContours(im_bwtemp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #~ cv2.drawContours(im_bw, contours, -1, (250), 2)
        for cnt in contours:
            m = cv2.moments(cnt)
            rArea          = m['m00']
            rPerimeter     = cv2.arcLength(cnt,True)
            (x, y), radius = cv2.minEnclosingCircle(cnt)
            
            if( bVerbose ): print( "x: %s, y: %s, Area: %s, perimeter: %s, radius: %s" % (x,y,rArea, rPerimeter,radius) );
            
            rMinArea = 600;
            if i == 5:
                rMinArea = 100;
            if rArea < rMinArea or rArea > 2800: # 500-2500 for im 2 is enough...
                continue
                
            #~ if( rArea*0.6 < rPerimeter ):
                #~ # too thin contour
                #~ continue
                
            if( radius > 38 ): # the big thin white stuffs in 001 has a radius of 39
                continue
                
                
            rDistToCenterSquared = (x-xCenter)*(x-xCenter)+(y-yCenter)*(y-yCenter)
            
            #~ if( bVerbose ): print( "rDistToCenterSquared: %s" % rDistToCenterSquared );
            
            #~ if ( rArea < 100 or rArea > 1000) and rDistToCenterSquared > 10000:
                #~ continue
                
            #~ if rDistToCenterSquared > 13000:
                #~ continue
            #~ if( abs(x-320)>100 ):
                #~ continue
            
            #~ (x, y), radius = cv2.minEnclosingCircle(contour)            
            #~ if( m['m00'] > 0.01 ):
                #~ Centroid      = ( m['m10']/m['m00'],m['m01']/m['m00'] )
            #~ else:
                #~ Centroid      = ( x, y )                    
            #~ pt = _LedPt(Centroid[0], Centroid[1])
            #~ pt.area = Area
            #~ pt.perimeter = Perimeter
            #~ pt.val = image[pt.y, pt.x]
            #~ if( bVerbose ):
                #~ print( "x,y: %s, %s, val:%s, Centroid: %s" % (x, y, pt.val,Centroid) );
            #~ pt.score = pt.area / (math.pi * radius ** 2)
            #~ res.append(pt)
    
            if( bVerbose ): print( "keeped" );
            aListArea[i].append([x,y,rArea, rPerimeter])
            if( bVerbose ):
                #color = np.random.randint(0,255,(3)).tolist() # Select a random color
                color = aListColorBGR_Std[i]
                cv2.drawContours(im_rgb_debug,[cnt],0,color,2)
        # for each cnt - end
    # for each color - end

    # now we've got every area, and we need to sort them in space
    if( bVerbose ): print( "DBG: aListArea: %s" % aListArea )
    aListArea = removeIsolatedZone( aListArea )
    aListArea = mergeSimilarZone( aListArea, im_rgb_debug );
    orderedFaceZone = orderZone( aListArea );
        
    if( bVerbose ):
        if( orderedFaceZone != None ):
            nNumFace = 1
            for f in orderedFaceZone:
                nColor,area = f
                x,y,a,p = area
                cv2.putText( im_rgb_debug, str(nNumFace) + ": " + aListColor[nColor], (int(x)-8, int(y)+4), cv2.FONT_HERSHEY_SIMPLEX, 0.35, aListColorBGR_Std[nColor] );
                nNumFace += 1
            strImgNameDebugFilename = strImgNameDebug.replace( ".png", ".jpg" )
            strImgNameDebugFilename = strImgNameDebugFilename.replace( ".jpg", "_contours.jpg" )
            cv2.imwrite( "/tmp/%s" % strImgNameDebugFilename, im_rgb_debug );
        
    if( bVerbose ): cv2.imwrite( "/tmp/%s" % strImgNameDebug.replace( ".jpg", "_h.jpg" ), im_bw );

    if( len(orderedFaceZone) < 9 ):
        return []
        
    orderedFaceZone = orderedFaceZone[:9]
    # check well ordered:
    if( not isWellOrdered( orderedFaceZone ) ):
        print( "WRN: bad ordered: skipping!" );
        return[]

    # convert zone to face letter
    orderedFace = []
    for f in orderedFaceZone:
        nColor,area = f
        orderedFace.append( [aListColor[nColor], 0.5] );
        
    return orderedFace;
# detectCube - end

def convertColorToFacePos( strColor ):
    """
    convert a face color "Yellow/Red/White ..." to a face name "Back/Front/Right/Up ..."
    only the first letter is taken / outputed
    """
    
    # my not official cube:
    aDictColorToFace =  { 
        # corto broken cube
        #~ "W": "F",
        #~ "Y": "D",
        #~ "G": "L",
        #~ "B": "B",
        #~ "O": "U",
        #~ "R": "R",
        "W": "F",
        "Y": "L",
        "G": "R",
        "B": "B",
        "O": "U",
        "R": "D",
        };
    strOut = aDictColorToFace[strColor[0]]
    return strOut
# convertColorToFacePos - end

def getColorToIndices(strColor):
    aDictColorToIndex =  { 
        "W": 0,
        "Y": 1,
        "G": 2,
        "B": 3,
        "O": 4,
        "R": 5,
        };
        
    return aDictColorToIndex[strColor[0]]

def convertListFaceToCubeConfiguration( aListFace ):
    """
    take a list of 6 lists of 9 colors and return face configuration in cube ordering (aretes then corners)
    the order shown is always: front right back left up down
    the configuration is a list of 12 aretes then 8 corners
    """
    aConfiguration = "";
    
    # up aretes
    aConfiguration += aListFace[4][7]
    aConfiguration += aListFace[0][1]
    aConfiguration += " "
    
    aConfiguration += aListFace[4][5]
    aConfiguration += aListFace[1][1]
    aConfiguration += " "
    
    aConfiguration += aListFace[4][1]
    aConfiguration += aListFace[2][1]
    aConfiguration += " "
    
    aConfiguration += aListFace[4][3]
    aConfiguration += aListFace[3][1]
    aConfiguration += " "
    
    
    # down aretes
    aConfiguration += aListFace[5][1]
    aConfiguration += aListFace[0][7]
    aConfiguration += " "
    
    aConfiguration += aListFace[5][5]
    aConfiguration += aListFace[1][7]
    aConfiguration += " "
    
    aConfiguration += aListFace[5][7]
    aConfiguration += aListFace[2][7]
    aConfiguration += " "
    
    aConfiguration += aListFace[5][3]
    aConfiguration += aListFace[3][7]
    aConfiguration += " "
    
    # middle aretes
    aConfiguration += aListFace[0][5]
    aConfiguration += aListFace[1][3]
    aConfiguration += " "
    
    aConfiguration += aListFace[0][3]
    aConfiguration += aListFace[3][5]
    aConfiguration += " "
    
    aConfiguration += aListFace[2][3]
    aConfiguration += aListFace[1][5]
    aConfiguration += " "
    
    aConfiguration += aListFace[2][5]
    aConfiguration += aListFace[3][3]
    aConfiguration += " "
    
    # corners top
    aConfiguration += aListFace[4][8]
    aConfiguration += aListFace[0][2]
    aConfiguration += aListFace[1][0]
    aConfiguration += " "
    
    aConfiguration += aListFace[4][2]
    aConfiguration += aListFace[1][2]
    aConfiguration += aListFace[2][0]
    aConfiguration += " "
    
    aConfiguration += aListFace[4][0]
    aConfiguration += aListFace[2][2]
    aConfiguration += aListFace[3][0]
    aConfiguration += " "
    
    aConfiguration += aListFace[4][6]
    aConfiguration += aListFace[3][2]
    aConfiguration += aListFace[0][0]
    aConfiguration += " "
    
    # corners bottom
    aConfiguration += aListFace[5][2]
    aConfiguration += aListFace[1][6]
    aConfiguration += aListFace[0][8]
    aConfiguration += " "
    
    aConfiguration += aListFace[5][0]
    aConfiguration += aListFace[0][6]
    aConfiguration += aListFace[3][8]
    aConfiguration += " "    

    aConfiguration += aListFace[5][6]
    aConfiguration += aListFace[3][6]
    aConfiguration += aListFace[2][8]
    aConfiguration += " "    

    aConfiguration += aListFace[5][8]
    aConfiguration += aListFace[2][6]
    aConfiguration += aListFace[1][8]

    # convert color name to face name
    aConfigInFaceName = ""
    for c in aConfiguration:
        if( c == " " ):
            aConfigInFaceName += " "
        else:
            aConfigInFaceName += convertColorToFacePos(c)
        
    return aConfigInFaceName
    
# convertListFaceToCubeConfiguration - end

def test_convertListFaceToCubeConfiguration():
    aFaces = [ ["W"]*9, ["R"]*9, ["B"]*9, ["G"]*9, ["O"]*9, ["Y"]*9 ]
    print aFaces
    cubeConf = convertListFaceToCubeConfiguration( aFaces )
    print cubeConf
    cubeConfTheoric = "UF UR UB UL DF DR DB DL FR FL BR BL UFR URB UBL ULF DRF DFL DLB DBR"
    assert( cubeConf == cubeConfTheoric)
#test_convertListFaceToCubeConfiguration - end

def resolve(aCubeConfiguration):
    """
    resolve a configuration.
    - aCubeConfiguration: a string of face configuration, eg: "FF BL FR UU RD BR LU UB RD LF LU DB FDU URB BLR UFR DRF FLD DBR DLB"
    from thistlethwaite.py
    """
    global aRecipes
    aRecipes = ""
    T=[]
    S=[0]*20,'QTRXadbhEIFJUVZYeijf',0
    I='FBRLUD'

    G=[(~i%8,i/8-4)for i in map(ord,'ouf|/[bPcU`Dkqbx-Y:(+=P4cyrh=I;-(:R6')]
    R=range

    def M(o,s,p):
     z=~p/2%-3;k=1
     for i,j in G[p::6]:i*=k;j*=k;o[i],o[j]=o[j]-z,o[i]+z;s[i],s[j]=s[j],s[i];k=-k

    N=lambda p:sum([i<<i for i in R(4)for j in R(i)if p[j]<p[i]])

    def H(i,t,s,n=0,d=()):
     if i>4:n=N(s[2-i::2]+s[7+i::2])*84+N(s[i&1::2])*6+divmod(N(s[8:]),24)[i&1]
     elif i>3:
      for j in s:l='UZifVYje'.find(j);t[l]=i;d+=(l-4,)[l<4:];n-=~i<<i;i+=l<4
      n+=N([t[j]^t[d[3]]for j in d])
     elif i>1:
      for j in s:n+=n+[j<'K',j in'QRab'][i&1]
     for j in t[13*i:][:11]:n+=j%(2+i)-n*~i
     return n

    def P(i,m,t,s,l=''):
     global aRecipes
     for j in~-i,i:
      if T[j][H(j,t,s)]<m:return
     if~m<0:aRecipes += l + "\n";return t,s
     for p in R(6):
      u=t[:];v=s[:]
      for n in 1,2,3:
       M(u,v,p);r=p<n%2*i or P(i,m+1,u,v,l+I[p]+`n`)
       if r>1:return r

    s=aCubeConfiguration.split()
    print( "s: '%s'" % s )
    o=[-(p[-1]in'UD')or p[0]in'RL'or p[1]in'UD'for p in s]
    s=[chr(64+sum(1<<I.find(a)for a in x))for x in s]

    try:
        for i in R(7):
         m=0;C={};T+=C,;x=[S]
         for j,k,d in x:
          h=H(i,j,k)
          for p in R(C.get(h,6)):
           C[h]=d;u=j[:];v=list(k)
           for n in i,0,i:M(u,v,p);x+=[(u[:],v[:],d-1)]*(p|1>n)
         if~i&1:
          while[]>d:d=P(i,m,o,s);m-=1
          o,s=d    
    except KeyError, err:
        print( "ERR: resolve: %s => can't resolve" % err )
        return None
    return aRecipes
# resolve - end

def checkNbrFaces(aColoredFaces):
    """
    Ensure there's not more than 9 faces of the same color!    
    """
    aCptPerColor = [0]*6
    for face in aColoredFaces:
        for col in face:
            aCptPerColor[getColorToIndices(col)] += 1;
    
    for i in range(len(aCptPerColor)):
        n = aCptPerColor[i]
        if( n != 9 ):
            print( "index %d: sum: %d" % (i,n) )
            return False
    return True
            

def test_resolve():
    init_state = "UF UR UB UL DF DR DB DL FR FL BR BL UFR URB UBL ULF DRF DFL DLB DBR"
    recipe_empty = resolve( init_state )
    print( "recipe_empty: '%s'" %  recipe_empty )
    assert( recipe_empty == "\n"*4 )
    
    #~ aConfig = "BD UR FL UL DF DR FU DL FR UB BR BL UFR URB UBL DLB DBR DFL ULF DRF"
    #~ recipe0 = resolve( aConfig )
    #~ print( "recipe0: '%s'" %  recipe0 )
    # U1B3L3B1\nF2R1U1D2R3D2R1\nU3F2R2U1\nU2L2U2R2U2B2L2U2B2U2B2\n"

    
    #aColoredFaces = [['W', 'Y', 'R', 'G', 'W', 'R', 'G', 'Y', 'W'], ['O', 'G', 'R', 'Y', 'R', 'O', 'R', 'R', 'B'], ['B', 'R', 'G', 'G', 'B', 'Y', 'G', 'O', 'R'], ['O', 'W', 'G', 'B', 'G', 'W', 'B', 'B', 'Y'], ['B', 'W', 'O', 'O', 'O', 'B', 'O', 'W', 'W'], ['W', 'G', 'Y', 'O', 'Y', 'B', 'Y', 'R', 'Y']]    
    aColoredFaces = [['G', 'G', 'W', 'O', 'W', 'O', 'O', 'G', 'R'], ['O', 'G', 'B', 'B', 'G', 'W', 'B', 'G', 'G'], ['Y', 'R', 'R', 'Y', 'B', 'W', 'B', 'R', 'R'], ['W', 'B', 'O', 'O', 'Y', 'Y', 'W', 'Y', 'W'], ['Y', 'Y', 'O', 'R', 'O', 'O', 'B', 'W', 'Y'], ['G', 'R', 'Y', 'B', 'R', 'B', 'G', 'W', 'R']]

    bCheck = checkNbrFaces(aColoredFaces)
    if( bCheck ):
        cubeConf = convertListFaceToCubeConfiguration( aColoredFaces )
        print( "cubeConf: %s" % cubeConf )
        print( "cubeConf str: %s" % str(cubeConf).replace("'", "").replace(",", " ") )
        timeBegin = time.time()
        recipe1 = resolve( cubeConf )
        rDuration = time.time()-timeBegin
        print( "time resolve: %ss" % rDuration )        
        print( "recipe1: %s" % recipe1 )
    
    
def autotest():
    #~ test_convertListFaceToCubeConfiguration()
    test_resolve()
    

def minitest():
    strCompleteName = "/work/Dev/git/appu_data/images_to_analyse/cube/cube_small/"
    strFilename = "205.png"
    #~ strFilename = "002_s.jpg"    
    strCompleteName += strFilename
    im = cv2.imread( strCompleteName );
    timeBegin = time.time()
    res = detectCube(im, strFilename, bVerbose=True);
    rDuration = time.time()-timeBegin
    print( "time detect: %ss" % rDuration )            
    print( "%s => %s" % (strFilename, res ) )
        
if __name__=="__main__":
    #~ minitest()
    autotest()
