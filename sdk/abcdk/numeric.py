# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Numeric tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Numeric tools"

print( "importing abcdk.numeric" );
## NOTE: some methods use np.dot which is slow if numpy is not compiled with blas/atlas (wich is the case on the robot) -> the expected improvement is about a reduction of time computation by 10.

import arraytools # for dup (better than deepcopy)
import math

bUseAlMath = True # True #False #True
#bUseAlMath = False

try:
    import numpy as np
except:
    print("ERR: abcdk.numeric: no numpy available here")

def limitRange( rVal, rMin, rMax ):
    "ensure that a value is in the range rMin, rMax"
    "WARNING: if rMin is less than rMax, there could be some strange behaviour"
    if( rVal < rMin ):
        rVal = rMin;
    elif( rVal > rMax ):
        rVal = rMax;
    return rVal;
# limitRange - end

def inRange( rVal, rMin = 0, rMax = 1 ):
    return rVal >= rMin and rVal <= rMax;

def inRange01( rVal ):
    return rVal >= 0 and rVal <= 1;

def sign( val ):
    "sign in c++: return { -1; 0; +1 } "
    "(as in the roulette)"
    if( val > 0 ):
        return 1;
    elif( val < 0 ):
        return -1;
    return 0;
# sign - end

def sign2( val ):
    "sign as in math: 0 is considered as positive value => return 1 or -1"
    if( val < 0 ):
        return -1;
    return 1;
# sign - end

def norm2D( v ):
    return math.sqrt( v[0] * v[0] + v[1] * v[1] );
# norm2D - end


def norm2D_squared( v ):
    return ( v[0] * v[0] + v[1] * v[1] );
# norm2D - end

def dist2D_squared( v1, v2 ):
    dx = v1[0] - v2[0];
    dy = v1[1] - v2[1];
    return dx*dx+dy*dy;
# dist2D_squared - end

def dist2D( v1, v2 ):
    return math.sqrt( dist2D_squared( v1,v2 ) );
# dist2D - end

def dist3D_squared( v1, v2 ):
    dx = v1[0] - v2[0];
    dy = v1[1] - v2[1];
    dz = v1[2] - v2[2];
    return dx*dx+dy*dy+dz*dz;
# dist2D_squared - end

def dist3D( v1, v2 ):
    return math.sqrt( dist3D_squared( v1,v2 ) );
# dist3D - end

def distManhattan2D(v1, v2):
    return abs(v1[0] - v2[0]) + abs(v1[1] - v2[1])
    
def normalise2D( v ):
    rNorme = math.sqrt( v[0]*v[0]+v[1]*v[1] );
    if( rNorme > 0.0001 ):
        return [v[0]/rNorme,v[1]/rNorme];
    return [0.,0.];
# normalise2D - end    

def normalise3D( v ):
    rNorme = math.sqrt( v[0]*v[0]+v[1]*v[1]+v[2]*v[2] );
    if( rNorme > 0.0001 ):
        return [v[0]/rNorme,v[1]/rNorme,v[2]/rNorme];
    return [0.,0.,0.];
# normalise3D - end

def anorm2(a):
    """
    as anorm, but squared
    return (a*a).sum(-1)
    """
    return (a*a).sum(-1)
# anorm2 - end
def anorm(a):
    """
    compute squared norm of a multi dimension scalar.
    (numpy style)
    - a: eg: [
                    [-365 -148]
                    [-428  -87]
                    [-434  -35]
                    [-368  -59]
                    [-437 -142]
                    [-416 -140]
                    [-434  -90]
                ]
    """
    return np.sqrt( anorm2(a) )
# anorm - end

import random

class Choice:
    "a list of value to be choosen"
    "it could be an ensemble or a min max"


    def __init__( self, aValues, nType = 0 ):
        """
        - aValues could be:
          - [min, max] (max included)
          - an int max: so it becomes a choice between [0,max-1]
          - [value1, value2, value3, ...]
        - nType:
           0: int list
          1: int min and max
        """
        self.aInitValues = aValues;
        self.nType = nType;
        self.reset();
    # __init__ - end

    def reset( self ):
        if( isinstance( self.aInitValues, int ) ):
            self.aValues = [0,self.aInitValues-1];
            self.nType = 1;
        else:
            self.aValues = self.aInitValues;
        if( self.nType == 1 ):
            assert( len( self.aValues ) == 2 );
    # reset - end

    def pickValue( self, bRemoveAfterChoose = False ):
        """
        return a value or None if all were returned.
        """
        if( len( self.aValues ) < 1 ):
            return None;

        if self.nType == 0:
            # random.choice( self.aValues ); # good, but can't delete efficiently
            # print( "list: %s" % str( self.aValues ) );
            nIdx = random.randint( 0, len(self.aValues)-1);
            nVal = self.aValues[nIdx];
            if( bRemoveAfterChoose ):
                del self.aValues[nIdx];
            return nVal;
        if self.nType == 1:
            nVal = random.randint( self.aValues[0],  self.aValues[1] );
            if( bRemoveAfterChoose ):
                # not very efficient !
                self.aValues = range(self.aValues[0], nVal) + range(nVal+1, self.aValues[1]+1 );
                self.nType = 0;
            return nVal;

    # pickValue - end

    @staticmethod
    def autoTest():
        aChoice = Choice( [1,2,3] );
        aChoiceRange = Choice( [1,1000], 1 );
        aChoiceRangeSmall = Choice( [1,4], 1 );
        aChoiceRangeAuto = Choice(2);
        print( "Choice.autoTest: pickValue: %s" % str( aChoice.pickValue(True) ) );
        print( "Choice.autoTest: pickValue: %s" % str( aChoice.pickValue(True) ) );
        print( "Choice.autoTest: pickValue: %s" % str( aChoice.pickValue(True) ) );
        print( "Choice.autoTest: pickValue: %s" % str( aChoiceRange.pickValue() ) );
        print( "Choice.autoTest: pickValue: %s" % str( aChoiceRange.pickValue(True) ) );
        print( "Choice.autoTest: pickValue: %s" % str( aChoiceRangeSmall.pickValue(True) ) );
        print( "Choice.autoTest: pickValue: %s" % str( aChoiceRangeSmall.pickValue(True) ) );
        print( "Choice.autoTest: pickValue: %s" % str( aChoiceRangeSmall.pickValue(True) ) );
        print( "Choice.autoTest: pickValue: %s" % str( aChoiceRangeSmall.pickValue(True) ) );
        print( "Choice.autoTest: pickValue: %s" % str( aChoiceRangeAuto.pickValue(True) ) );
        print( "Choice.autoTest: pickValue: %s" % str( aChoiceRangeAuto.pickValue(True) ) );
        assert( aChoiceRangeAuto.pickValue(True) == None );
        print( "Choice.autoTest: pickValue (must be None): %s" % str( aChoiceRangeAuto.pickValue(True) ) );

    # autoTest - end

# class Choice - end

# Two direct accessor to Choice
class ChoiceRange(Choice):
    def __init__( self, aValues ):
        Choice.__init__( self, aValues, 1 );
    # __init__ - end

class ChoiceList(Choice):
    def __init__( self, aValues ):
        Choice.__init__( self, aValues, 0 );
    # __init__ - end

global_listLastRandom = {}; # a list of last returned value for each max (so each one will be different)
def randomDifferent( min, maxIncluded ):
    """
    Return a random, always different !
    The syntaxe is the same as the classic random.randint(min,max included)
    """
    if( maxIncluded < min ):
        print( "WRN: randomDifferent: called with a max inferior to min, returning min! (min: %d, maxIncluded: %d)" % ( min,maxIncluded) )
        return min; # patch, we should also raise an exception, but...        
    global global_listLastRandom;
    try:
        nLast = global_listLastRandom[maxIncluded];
    except BaseException as err:
        print( "INF: randomDifferent: first access to a random with max %d" % maxIncluded );
        nLast = min-1; # impossible value
    if( min == maxIncluded ):
        return min
    nValue = random.randint( min, maxIncluded );
    while( nValue == nLast ):
        nValue = random.randint( min, maxIncluded );
    global_listLastRandom[maxIncluded] = nValue;
    return nValue;
# randomDifferent - end

def findBoundingBox( listPoint ):
    """
    from a list of points, find bouding box
    return them [xleft, ytop, xright, ybottom]
    """
    x1 = x2 = listPoint[0][0];
    y1 = y2 = listPoint[0][1];
    for point in listPoint[1:]:
        if( x1 > point[0] ):
            x1 = point[0];
        if( x2 < point[0] ):
            x2 = point[0];
        if( y1 > point[1] ):
            y1 = point[1];
        if( y2 < point[1] ):
            y2 = point[1];
    return [x1,y1,x2,y2];
# findBoundingBox - end


def findCorner( listPointParam, nFindCornerMethod = 0 ):
    """
    from a list of points, find corner (it's not bounding box, because point are real point, not translated one )
    return them [topleft, topright, bottomleft, bottomright] with for each point: [x,y]
    listPoint: a list of 2D point [ [x1,y1], [x2,y2], ... ]
    nFindCornerMethod: (NDEV!!!) what to do when there's no point at the corner. 0: use the point the nearest of the bouding box. 1: maximize width, 2: maximize height
    """
    print( "DBG: findCorner: listPoint: %s" % str(listPointParam) );
    listPoint = listPointParam[:];
    x1 = x2 = listPoint[0][0];
    y1 = y2 = listPoint[0][1];
    for point in listPoint[1:]:
        if( x1 > point[0] ):
            x1 = point[0];
        if( x2 < point[0] ):
            x2 = point[0];
        if( y1 > point[1] ):
            y1 = point[1];
        if( y2 < point[1] ):
            y2 = point[1];

    aWanted = [ [x1,y1], [x2,y1],[x1,y2],[x2,y2] ];
    print( "DBG: findCorner: aWanted: %s" % aWanted );
    # find nearest point of bounding box
    aCorner = arraytools.dup( [[0]*2]*4 );
    for j in range(4): # for each corner    
        # find nearest point
        rMin = 1000000;
        iMin = -1;        
        for i in range(len(listPoint)):
            dx = aWanted[j][0]-listPoint[i].x;
            dy = aWanted[j][1]-listPoint[i].y;
            rDist = dx*dx+dy*dy;
            if( rDist < rMin ):
                print( "best i: pt: %s => corner %d (prev dist:%f, new: %f)" % (listPoint[i], j, rMin,rDist ) );
                rMin = rDist;
                iMin = i;
        # store
        print( "final best idx %d => corner : %d (rMin: %f)" % (iMin,j, rMin) );
        aCorner[j][0] = listPoint[iMin][0];
        aCorner[j][1] = listPoint[iMin][1];
        listPoint[iMin].x = 10000000; # "remove it"
        
    print( "DBG: findCorner: returning: %s" % aCorner );
    return aCorner;
# findCorner - end

def isRectangleInto( r1, r2 ):
    """
    is rectangle r1 in rectangle r2 ?  NOT TESTED !
    - r1: [x1,y1,x2,y2]
    """
    return (
                r1[0] >= r2[0] and r1[0] <= r2[2]
        and  r1[1] >= r2[1] and r1[1] <= r2[3]
        and  r1[2] >= r2[0] and r1[2] <= r2[2]
        and  r1[3] >= r2[1] and r1[3] <= r2[3]
        );
# isRectangleInto - end

def isRectangleIntersect( r1, r2 ):
    """
    is rectangle r1 intersect with r2 ? (r1 could be in r2) NOT TESTED !
    - r1: [x1,y1,x2,y2]
    """
    return (
                # test extrem corner
                ( r1[0] >= r2[0] and r1[0] <= r2[2]  and r1[1] >= r2[1] and r1[1] <= r2[3] )
        or     ( r1[2] >= r2[0] and r1[2] <= r2[2]  and r1[3] >= r2[1] and r1[3] <= r2[3] )
                # two other corner
        or     ( r1[2] >= r2[0] and r1[2] <= r2[2]  and r1[1] >= r2[1] and r1[1] <= r2[3] )
        or     ( r1[0] >= r2[0] and r1[0] <= r2[2]  and r1[3] >= r2[1] and r1[3] <= r2[3] )
    );
# isRectangleIntersect - end

def getEnclosingRect( r1, r2 ):
    """
    found bouding box of two rectangle
    - r1: [x1,y1,x2,y2]
    """
    constructedList = [];
    for r in [r1,r2]:
        constructedList.append( [ r[0], r[1] ] );
        constructedList.append( [ r[0], r[3] ] );
        constructedList.append( [ r[2], r[1] ] );
        constructedList.append( [ r[2], r[3] ] );
    return findBoundingBox( constructedList );
# getEnclosingRect - end

def getRectangleAverageDistance( r1, r2 ):
    """
    Return an average distance of the empty space between two rectangle
    - r1: [x1,y1,x2,y2]
    """
    if( isRectangleIntersect( r1, r2 ) ):
        return 0;
    pt1Center = [(r1[0]+r1[2])/2, (r1[1]+r1[3])/2];
    pt2Center = [(r2[0]+r2[2])/2, (r2[1]+r2[3])/2];
    rCenterDist = dist2D( pt1Center, pt2Center   );
    rAvgDist_If_touching = dist2D( pt1Center, ( r1[0], r1[1] ) ) + dist2D( pt2Center, ( r2[0], r2[1] ) );
    return max( 0, rCenterDist - rAvgDist_If_touching );
# getRectangleAverageDistance - end

def simplifyRectangleList( listRectParams ):
    """
    take a list of rect [x1,y1,x2,y2] and remove duplicate, group closer one, and remove enclosed one
    return the simplified list
    """
    listRect = [];
    listRect.extend( listRectParams );
    #~ print( "DBG: abcdk.numeric.simplifyRectangleList: input: %s" % listRect );

    listRectOut = [];
    i = 0;
    while( i < len( listRect ) ):
        j = i + 1;
        if( listRect[i] != None ):
            rc = [];
            rc.extend( listRect[i] );
            while( j < len( listRect ) ):
                if( listRect[j] != None ):
                    if( isRectangleInto( rc, listRect[j] ) ):
                        #~ print( "DBG: abcdk.numeric.simplifyRectangleList: %d %s in %d %s -> destroy i" % ( i, rc, j, listRect[j] ) );
                        # already in another one
                        rc = None;
                        break;
                    if( isRectangleInto( listRect[j], rc ) ):
                        #~ print( "DBG: abcdk.numeric.simplifyRectangleList: %d %s in %d %s -> destroy j %d %s" % ( j, listRect[j], i, rc, j, listRect[j], ) );
                        listRect[j] = None; # remove the other
                    else:
                        rDist = getRectangleAverageDistance( rc, listRect[j] );
                        #~ print( "DBG: abcdk.numeric.simplifyRectangleList: rDist: %f" % rDist );
                        if( rDist < 2 ):
                            # group closer
                            rc = getEnclosingRect( rc, listRect[j] );
                            #~ print( "DBG: abcdk.numeric.simplifyRectangleList: close: summing %d and %d %s => %s (destroying j)" % (i, j, listRect[j], rc ) );
                            listRect[j] = None; # remove the other
                        else:
                            # difference, let's do nothing more
                            pass
                j += 1;
            # while j - end
            if( rc != None ):
                #~ print( "DBG: abcdk.numeric.simplifyRectangleList: %d: adding %s" % (i, rc ) );
                #~ print( "DBG: abcdk.numeric.simplifyRectangleList: remaining list: %s" % ( listRect ) );
                listRectOut.append( rc );
        i += 1;
    #~ print( "DBG: abcdk.numeric.simplifyRectangleList: simplifyRectangleList: listRectOut: %s" % listRectOut );
    return listRectOut;
# simplifyRectangleList - end

def simplifyAreaList( listArea ):
    """
    as simplifyRectangleList but rectangle are xcenter, ycenter, w, h
    """
    listRect = [];
    for area in listArea:
        listRect.append( [area[0]-area[2]/2, area[1]-area[3]/2, area[0]+area[2]/2,area[1]+area[3]/2] );
    #~ print( "DBG: abcdk.numeric.simplifyAreaList:\narea: %s\nrects: %s" % (str(listArea), str(listRect) ) );
    listRectOut = simplifyRectangleList( listRect );
    areaOut = [];
    for rect in listRectOut:
        w = rect[2]-rect[0];
        h = rect[3]-rect[1];
        areaOut.append( [rect[0]+w/2, rect[1]+h/2, w, h] );
    return areaOut;
# simplifyAreaList - end

def simplifyBoundingBoxList( listArea ):
    """
    as simplifyRectangleList but rectangle are xleft, ytop, w, h
    """
    listRect = [];
    for area in listArea:
        listRect.append( [area[0], area[1], area[0]+area[2],area[1]+area[3]] );
    #~ print( "DBG: abcdk.numeric.simplifyBoundingBoxList:\nbbs: %s\nrects: %s" % (str(listArea), str(listRect) ) );
    listRectOut = simplifyRectangleList( listRect );
    bbsOut = [];
    for rect in listRectOut:
        w = rect[2]-rect[0];
        h = rect[3]-rect[1];
        bbsOut.append( [rect[0], rect[1], w, h] );
    return bbsOut;
# simplifyAreaList - end

def isShapeRoughlyInto( s1, s2 ):
    """
    is all point of a shape roughly into another one ?
    (it could be some point, where some point of the small shape could be out of the big)

    ---------
    |           \
    |       --- \-/    <-- this point is out (but it's not a big deal)
    |      |      X
    |       --- / \
    |                \
    --------------


    - s1: [[x1,y1],[x2,y2], [x3,y3], ...]
    - s2: same format
    """

    s = findBoundingBox( s1 ); # small
    b = findBoundingBox( s2 ); # big

    return isRectangleInto( s, b );
# isShapeRoughlyInto - end

def getShapeDifference( s1, s2 ):
    """
    Compute the sum of each difference for each point compared 2 by 2
    - s1: an array of point (each point is a pair (2D) or a tuple (3D))
    - s2: same as s1
    return a value expriming the difference
    """
    kDiffPerMissingElement = 100;
    nTotalDiff = 0;
    if( len(s1) != len(s2) ):
        nTotalDiff += kDiffPerMissingElement * abs( len(s1) -len(s2) );
    nMinLen = min( len(s1), len(s2) );
    for i in range( nMinLen ):
        nDiff = 0;
        for j in range( len(s1[i]) ):
            nDiff += abs( s1[i][j] - s2[i][j] );
        nTotalDiff += nDiff;
    return nTotalDiff;
# getShapeDifference - end

def isRhombus( listPoint ):
    """
    Is a list of 4 point describing a rhombus (losange) ?
      - listPoint: an array or tuple of pair x,y: [topleft, topright, bottomleft, bottomright]
    return True or False
    """
    #~ print( "INF: abcdk.numeric.isRhombus(%s)" % str( listPoint ) );

    # just a simple test:  is the middle of  each diagonal quite equal and is not a flat losange (the middle is different than each corner)
    xc1 = ( listPoint[0][0] + listPoint[3][0] ) / 2;
    yc1 = ( listPoint[0][1] + listPoint[3][1] ) / 2;

    xc2 = ( listPoint[1][0] + listPoint[2][0] ) / 2;
    yc2 = ( listPoint[1][1] + listPoint[2][1] ) / 2;

    #~ print( "INF: abcdk.numeric.isRhombus: xc1: %d, yc1: %d" % ( xc1, yc1 ) );
    #~ print( "INF: abcdk.numeric.isRhombus: xc2: %d, yc2: %d" % ( xc2, yc2 ) );


    nSum = abs( xc1 - xc2 ) + abs( yc1 - yc2 );
    nSumFlat1 = abs( xc1 - listPoint[0][0] ) + abs( yc1 - listPoint[0][1] );
    nSumFlat2 = abs( xc2 - listPoint[1][0] ) + abs( yc2 - listPoint[1][1] );
    nSumFlat = nSumFlat1 + nSumFlat2;

    #~ print( "INF: abcdk.numeric.isRhombus: nSum: %d, nSumFlat1: %d, nSumFlat2: %d" % ( nSum, nSumFlat1, nSumFlat2 ) );

    nAvgSize = abs( listPoint[0][0] - listPoint[3][0] ) + abs( listPoint[0][1] - listPoint[3][1] )  + abs( listPoint[1][0] - listPoint[2][0] ) + abs( listPoint[1][1] - listPoint[2][1] );

    #~ print( "INF: abcdk.numeric.isRhombus: nAvgSize: %d" % ( nAvgSize ) );

    kEquality = 4;
    if( nSum > nAvgSize/20 or nSumFlat < kEquality ):
        return False;

    return True;
# isRhombus - end

def polarToCartesian(r, theta):
    """ convert polar coordinate to cartesian coordinate """
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    return x, y

def cartesianToPolar(x,y):
    """ convert 2D  cartesian coordinate to polar coordinate """
    r = math.sqrt(x * x + y* y)
    theta = math.atan2(y, x)
    return r, theta

def MinAngle(angle):
    angle = angle % (2*math.pi)
    if (angle) > math.pi:
        return (angle - 2*math.pi)

    if (angle) < -math.pi:
        return (angle + 2*math.pi)

    return angle

def OrientedAngle(A,B,C):
    """ return orriented angle
    >>> [A,B,C] = [2,1], [1,1], [1,2]
    >>> OrientedAngle(A,B,C)
    1.5707963267948966
    >>> OrientedAngle(C,B,A)
    -1.5707963267948966
    >>> OrientedAngle(B,A,C)
    -0.78539816339744839
    >>> OrientedAngle(C,A,B)
    0.78539816339744839
    """
    A = np.array(A)
    B = np.array(B)
    C = np.array(C)

    return - computeVectAngle(C-B, A-B)  #< bug here ?
    #return  computeVectAngle(C-B, B-A)

def computeVectAngle(vect1, vect2):
    """ return the orriented angle between vect1 and vect2.
    >>> computeVectAngle([1,0], [1,0])
    0.0
    >>> computeVectAngle([1,0], [0,1]) # math.pi/2
    1.5707963267948966
    >>> computeVectAngle([1,0], [1,1]) # math.pi/4
    0.78539816339744839
    >>> computeVectAngle([1,1], [1,0]) # math.pi/4
    -0.78539816339744839
    """
    #>>> computeVectAngle([0,0], [1,0]) # math.pi/4
    #nan
    return computeAngleBetween(vect1, vect2)
    sign = math.copysign(1, vect1[0] * vect2[1] - vect2[0] * vect1[1])
    try:
        num = (np.dot(np.array(vect1),(np.array(vect2))))
        denum = ( dist2D(vect1, [0,0]) * dist2D(vect2, (0,0)) )
        val =  num/denum
        theta = sign * math.acos(val)

    except ValueError as err:
        print("ERR: abcdk.numeric.computeVectANGLE v1 = %s, v2 = %s, error %s" % (str(vect1), str(vect2), str(err)))
        theta = 0
    return MinAngle(theta)


def norm(vector):
    """ Returns the norm (length) of the vector."""
    # note: this is a very hot function, hence the odd optimization
    # Unoptimized it is: return np.sqrt(np.sum(np.square(vector)))
    return np.sqrt(np.dot(vector, vector))

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    if norm(vector) == 0:
        return vector * 0
    return vector / norm(vector)

def computeAngleBetween(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::
   #         >>> angle_between((1, 0, 0), (0, 1, 0))
   #         1.5707963267948966
   #         >>> angle_between((1, 0, 0), (1, 0, 0))
   #         0.0
   #         >>> angle_between((1, 0, 0), (-1, 0, 0))
   #         3.141592653589793
    """
    sign = math.copysign(1, v1[0] * v2[1] - v2[0] * v1[1])
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    angle = np.arccos(np.dot(v1_u, v2_u))
    if np.isnan(angle):
        if (v1_u == v2_u).all():
            return 0.0
        if np.isnan(v1_u[0]) or np.isnan(v2_u[0]):
            return np.nan
        return np.pi * sign
    return angle * sign

def inversePose(aP6D):
    """
    return the inverse of the pos
    :param aP6D:
    :return:
    """
    import almath
    aP6DAlmathFormat = almath.Position6D(np.array(aP6D, dtype=np.float))
    aP6DInverseAlmathFormat = almath.transformFromPosition6D(aP6DAlmathFormat).inverse()
    aTransform = almath.position6DFromTransform(aP6DInverseAlmathFormat)
    aP6Dret = np.array( aTransform.toVector(), dtype=np.float)
    return aP6Dret

def test_inversePose():
    np.testing.assert_almost_equal(inversePose(np.array([1,1,1,0,0,0])), np.array([-1,-1,-1,0,0,0]))
    np.testing.assert_almost_equal(inversePose(np.array([0,0,0,1,0,0])), np.array([0,0,0,-1,0,0]))

def convertPoseWorldToFrameRobot( p6DObjectRtWorld, p6DRobotRtWorld):
    """
    """
    import almath
    # pWorld In robot frame:

    #print("INF: abcdk.numeric: using almath")

    p6DRobotRtWorld = almath.Position6D(np.array(p6DRobotRtWorld, dtype=np.float))
    t6DRobotRtWorld = almath.transformFromPosition6D(p6DRobotRtWorld)
    p6DWorldRtRobot = almath.position6DFromTransform(t6DRobotRtWorld.inverse()).toVector()  #on repasse en pose6D

    return changeReference(p6DObjectRtWorld, p6DWorldRtRobot)


def convertPoseWorldToTorso( p6DObjectRtWorld, p6DRobotRtWorld):
    """
    TODO/NDEV: rename into getObjectPoseRelativeToRobot(p6DObject, p6DRobot)

    For a pose (`p6DObjectRtWorld`) expressed in the world coordinate and the robot pose6D (`p6DRobotRtWorld`) in this world, compute the corresponding pose6D in frameRobot
    This metod is similar to chgRepereT  ## arevoir
    """
    ### on devrait pouvoir utiliser directement changeReference.. mais bon, le code ne semble pas bon, faire un redmine :D
    ### almath.changeReferencePosition6D(tRobotRtWorld, p6DObjectRtWorld, p6DToTest )  #// <<< ne semble pas fonctionner... attention
    ## ap6DObjectRtRobotTest = np.array(p6DToTest.toVector())

    # Rt = relative to
    global bUseAlMath
    p6DRobotRtWorld = np.array(p6DRobotRtWorld, dtype=np.float)
    p6DObjectRtWorld = np.array(p6DObjectRtWorld, dtype=np.float)
    #bUseAlMath = False
    if bUseAlMath:
        import almath
        # pWorld In robot frame:

        #print("INF: abcdk.numeric: using almath")

        p6DRobotRtWorld = almath.Position6D(np.array(p6DRobotRtWorld, dtype=np.float))
        t6DRobotRtWorld = almath.transformFromPosition6D(p6DRobotRtWorld)
        p6DWorldRtRobot = almath.position6DFromTransform(t6DRobotRtWorld.inverse()).toVector()  #on repasse en pose6D

        return changeReference(p6DObjectRtWorld, p6DWorldRtRobot)
    else:
        p6DObjectRtWorld = np.array(p6DObjectRtWorld)
        p6DRobotRtWorld = np.array(p6DRobotRtWorld)
        ap6DObjectRtRobot = np.zeros(6)
        ap6DObjectRtRobot[:3] = p6DObjectRtWorld[:3] - p6DRobotRtWorld[:3]

        dWX, dWY, dWZ = - p6DRobotRtWorld[3:]
        coords = ap6DObjectRtRobot[:3]

        rotMatX = np.array([[1.0,0.0,0.0],[0.0,np.cos(dWX), -np.sin(dWX)], [0.0, np.sin(dWX), np.cos(dWX)]])
        newCoords = rotMatX.dot(coords)

        # rotation autour de y
        rotMatY = np.array([[np.cos(dWY), 0.0, np.sin(dWY)], [0.0, 1.0, 0.0], [-np.sin(dWY), 0.0, np.cos(dWY)]])
        newCoords = rotMatY.dot(newCoords)

        # rotation autour de z
        rotMatZ = np.array([[np.cos(dWZ), -np.sin(dWZ), 0.0], [np.sin(dWZ), np.cos(dWZ), 0.0], [0.0, 0.0, 1.0]])
        newCoords = rotMatZ.dot(newCoords)

        ap6DObjectRtRobot[:3] = newCoords[:3]
        ap6DObjectRtRobot[3:] = p6DObjectRtWorld[3:] - p6DRobotRtWorld[3:]
#        print("avec les transform %s, avec changeRepereAlmath %s, avec abcdk %s" % (ap6DObjectRtRobotAlMath, ap6DObjectRtRobotTest, ap6DObjectRtRobot))
        return ap6DObjectRtRobot

def convertPoseTorsoToWorld( p6DObjectRtRobot, p6DRobotRtWorld):
    """
    Inverse of convertPoseWorldToTorso

    p6DObjectRtRobot: pose 6D of the object in the reper centered at robot
    p6DRobotRtWorld: pose6D of the robot in a world
    """
    p6DObjectRtRobot = np.array(p6DObjectRtRobot, dtype=np.float)
    p6DRobotRtWorld = np.array(p6DRobotRtWorld, dtype=np.float)
    global bUseAlMath
    if bUseAlMath:
        ## NDEV utiliser le changeReference ici !
        return changeReference(p6DObjectRtRobot, p6DRobotRtWorld)

        # transform pour passer de l'origine du robot à l'origine de l'objet
        #tObjectRtRobot = almath.transformFromPosition6D(almath.Position6D(p6DObjectRtRobot))
        ##tRobotRtObject = tObjectRtRobot.inverse()
        ## transform pour passer de l'origine du monde à l'origine du robot
        #tRobotRtWorld = almath.transformFromPosition6D(almath.Position6D(p6DRobotRtWorld))
        ## transform poru passer de l'origine du robot à l'origine du monde
        ##tWorldRtRobot = tRobotRtWorld.inverse()
        ## transform pour passer de l'origine du monde à l'origine de l'object
        #tObjectRtWorld =  tObjectRtRobot * tRobotRtWorld
        #ap6DObjectRtWolrd = np.array(almath.position6DFromTransform(tObjectRtWorld).toVector())
        #return ap6DObjectRtWolrd
    else:

        p6DObjectRtRobot = np.array(p6DObjectRtRobot)
        p6DRobotRtWorld = np.array(p6DRobotRtWorld)
        newPose6D = np.zeros(6)
        coords = p6DObjectRtRobot[:3]
        dWX, dWY, dWZ = p6DRobotRtWorld[3:]

        rotMatX = np.array([[1.0,0.0,0.0],[0.0,np.cos(dWX), -np.sin(dWX)], [0.0, np.sin(dWX), np.cos(dWX)]])
        newCoords = rotMatX.dot(coords)

        # rotation autour de y
        rotMatY = np.array([[np.cos(dWY), 0.0, np.sin(dWY)], [0.0, 1.0, 0.0], [-np.sin(dWY), 0.0, np.cos(dWY)]])
        newCoords = rotMatY.dot(newCoords)

        # rotation autour de z
        rotMatZ = np.array([[np.cos(dWZ), -np.sin(dWZ), 0.0], [np.sin(dWZ), np.cos(dWZ), 0.0], [0.0, 0.0, 1.0]])
        newCoords = rotMatZ.dot(newCoords)

        return np.array([newCoords[0] + p6DRobotRtWorld[0], newCoords[1] + p6DRobotRtWorld[1], newCoords[2] + p6DRobotRtWorld[2], dWX + p6DObjectRtRobot[3], dWY+p6DObjectRtRobot[4], dWZ + p6DObjectRtRobot[5] ])



def computeRotationMatrix(theta, R = None):
    """ return 3D rotation matrix (efficiently)
    source: http://osdir.com/ml/python-numeric-general/2009-03/msg00103.html
    RX, then RY, then RZ
    """
    if R == None:
        R = np.zeros((4, 4))
    cx, cy, cz = np.cos(theta)
    sx, sy, sz = np.sin(theta)
    R.flat = ( cy*cz, cz*sx*sy-cx*sz, cx*cz*sy + sx*sz, 0, cy*sz, cx*cz+sx*sy*sz, -cz*sx+cx*sy*sz, 0, -sy, cy*sx, cx*cy, 0, 0, 0, 0, 1)
    # z then y then x:
    #R.flat = ( cy*cz, -cy*sz, sy, 0, cx*sz+sx*sy*cz, cx*cz-sx*sy*sz, -sx*cy, 0, sx*sz-cx*sy*cz, sx*cz+cx*sy*sz, cx*cy, 0, 0, 0, 0, 1)
    return R


def chgRepere(x,y,z, dX, dY, dZ, dWX, dWY, dWZ, bUseOldMethod=False):
    """ Return the new coordinate after change of reper in a 3D vector space.
    dX,DY,DZ,DWX, DWY, DWZ are the difference

    #>>> chgRepere(1,0, 0, 0, 0, 0, 0, 0, math.pi/2)
    array([  6.12323400e-17,   1.00000000e+00,   0.00000000e+00])
    """
    ## return x',y',z'
    global bUseAlMath
    if bUseAlMath:
        #print("INF: abcdk.numeric: using almath")
        import almath
        tObjectRtCamera = almath.transformFromPosition3D(almath.Position3D([x,y,z]))
        tCameraRtRobot = almath.transformFromPosition6D(almath.Position6D([dX, dY, dZ, dWX, dWY, dWZ]))
        #tObjectRtRobot = tObjectRtCamera * tCameraRtRobot  #>.. ca ne passe pas
        tObjectRtRobot = tCameraRtRobot * tObjectRtCamera
        #tObjectRtRobot = tObjectRtCamera* tCameraRtRobot
        aPose6D = np.array(almath.position6DFromTransform(tObjectRtRobot).toVector())
        return aPose6D[:3]
    else:

        if not(bUseOldMethod):
            coords = np.array([x, y, z, 0])  # dans le repere camera.. on fais les rotation autour du point camera donc pas besoin d'ajouter le rotation_point dans les rotMat
            rotMat = computeRotationMatrix([dWX, dWY, dWZ])
            newCoords = rotMat.dot(coords)[:3]
        else:
            coords = np.array([x, y, z])  # dans le repere camera.. on fais les rotation autour du point camera donc pas besoin d'ajouter le rotation_point dans les rotMat
            # rotation autour de x
            rotMatX = np.array([[1.0,0.0,0.0],[0.0,np.cos(dWX), -np.sin(dWX)], [0.0, np.sin(dWX), np.cos(dWX)]])
            newCoords = rotMatX.dot(coords)

            # rotation autour de y
            rotMatY = np.array([[np.cos(dWY), 0.0, np.sin(dWY)], [0.0, 1.0, 0.0], [-np.sin(dWY), 0.0, np.cos(dWY)]])
            newCoords = rotMatY.dot(newCoords)

            # rotation autour de z
            rotMatZ = np.array([[np.cos(dWZ), -np.sin(dWZ), 0.0], [np.sin(dWZ), np.cos(dWZ), 0.0], [0.0, 0.0, 1.0]])
            newCoords = rotMatZ.dot(newCoords)

            # translation

            #print("coord apres rotations.. %s and la translation a ajouter %s" % (str(newCoords), str(translationVector)) )
        translationVector = np.array([dX, dY, dZ])
        newCoords = newCoords + translationVector
        return newCoords

def test_chgReperePerf():
    import time
    rStart = time.time()
    for i in range(1000):
        chgRepere(1,1,1, 10, 10, 10, math.pi/2, math.pi/2, math.pi/2)
    rDuration  = time.time() - rStart
    assert ( rDuration < 0.05)


## TODO : virer cette methode ! utiliser seulement chgRepere partout dans le code !
## Cette methode est utilisé pour le pod.. il faudrait la virer/la mettre a jour en utilisant almath:NDEV, je ne fais pas ça maintenant car alex bosse sur le pod
def chgRepereCorrected(x,y,z, dX, dY, dZ, dWX, dWY, dWZ):
    """ Return the new coordinate after change of reper in a 3D vector space.
    The rotation is done arround 0,0,0

    Args:
        x,y,z : coordinate of the point that need to be moved
        dx,dy,dz : translation vector
        dwX, dWY, dWZ: rotation angle arround each axis
    """
    ## return x',y',z'
    coords = np.array([x, y, z])  # dans le repere camera.. on fais les rotation autour du point camera donc pas besoin d'ajouter le rotation_point dans les rotMat

    # rotation autour de x
    rotMatX = np.array([[1,0,0],[0,np.cos(dWX), -np.sin(dWX)], [0, np.sin(dWX), np.cos(dWX)]])
    newCoords = rotMatX.dot(coords)


    # rotation autour de y
    rotMatY = np.array([[np.cos(dWY), 0, np.sin(dWY)], [0, 1, 0], [-np.sin(dWY), 0, np.cos(dWY)]])
    newCoords = rotMatY.dot(newCoords)

    # rotation autour de z
    rotMatZ = np.array([[np.cos(dWZ), -np.sin(dWZ), 0], [np.sin(dWZ), np.cos(dWZ), 0], [0, 0, 1]])
    newCoords = rotMatZ.dot(newCoords)

    # translation
    translationVector = np.array([dX, dY, dZ])
    newCoords = newCoords - translationVector
    return newCoords

def test_changeReference():


 #   N = 100
 #   for i in range(N):
 #       aP6DObjectInRefA = np.array([np.random.rand() , np.random.rand() , 0.0, 0, 0, np.random.rand()])
 #       aP6DRefAInRefB = np.random.rand(6)
 #       aRes = changeReference(aP6DObjectInRefA, aP6DRefAInRefB)

 #       np.testing.assert_allclose(aP6DRefAInRefB[3], aRes[3], atol=0.1)  # on ne doit pas changer l'orientation de y
 #       np.testing.assert_allclose(aP6DRefAInRefB[4], aRes[4], atol=0.1)  # on ne doit pas changer l'orientation de z  .. en fait si ça doit.. demonstration alex

    aP6DObjectInRefA = np.array([1.0 , 1.0 , 2.0, 0, 0, 0])
    aP6DRefAInRefB = np.array([10, 10, 10, 0, 0, math.pi/2.0])
    aRes = changeReference(aP6DObjectInRefA, aP6DRefAInRefB)
    np.testing.assert_almost_equal(aRes, np.array([9, 11, 12, 0, 0, math.pi/2.0]), decimal=3)


    aP6DObjectInRefA = np.array([-1.0 , -1.0 , 0.0, 0, 0, 0])
    aP6DRefAInRefB = np.array([1, 1, 0, 0.0, 0.0, 0.0])
    aRes = changeReference(aP6DObjectInRefA, aP6DRefAInRefB)
    np.testing.assert_almost_equal(aRes, np.zeros(6))


    aP6DObjectInRefA = np.array([-1.0 , -1.0 , 0.0, 0, 0, 0])
    aP6DRefAInRefB = np.array([1, 1, 0, 0.0, 0.0, 0.0])
    aRes = changeReference(aP6DObjectInRefA, aP6DRefAInRefB)
    np.testing.assert_almost_equal(aRes, np.zeros(6))


def changeReference(p6DobjectInRefA, p6DRefAInRefB):
    """
    Compute the pose of an object relative to a specific reference (refB) by knowing the pose of this object in refA and the pose of refA in refB.

    This method use almath

    @param p6DobjectInRefA: (numpy array dtype = float)
    @param p6DRefAInRefB (numpy array dtype = float)
    @return: p6DObjectInRefB (numpy array dtype = float)
    """
    import almath
    # we convert to almath pose6D
    p6DobjectInRefA = almath.Position6D(np.array(p6DobjectInRefA, dtype=np.float))
    p6DRefAInRefB = almath.Position6D(np.array(p6DRefAInRefB, dtype=np.float))
    # we convert into almath matrix transform  (t for transform) - i.e on passe en coordonnee homogene/matrix plus simple pour faire des transformations
    tRefAToObject = almath.transformFromPosition6D(p6DobjectInRefA)  # matrice pour passer de p6DRefA à p6DObject
    tRefBToRefA = almath.transformFromPosition6D(p6DRefAInRefB)  # matrice pour passer de RefB à RefA
    t6DRefBToObject = tRefBToRefA * tRefAToObject  # on compose les deux transformations (juste une simple multiplication de matrice :D)
    # NDEV il y a deja un changeReference dans almath, le tester et utiliser le code ici ?
    p6DObjectInRefB = almath.position6DFromTransform(t6DRefBToObject).toVector()  #on repasse en pose6D
    return np.array(p6DObjectInRefB, dtype=np.float)


# NDEV: renommer cette fonction
def chgRepereT(aOrientation, aTranslation, rDx, rDy, rDz, rDwx, rDwy, rDwz):
    """
    Change origin point of view.
    @param aOrientation: object orientation relative to camera
    @param aTranslation: object translation relative to camera
    @param rDx: camera x position in world
    @param rDy: camera y position in world
    @param rDz: camera z position in world
    @param rDwx: camera x orientation
    @param rDwy: camera y orientation
    @param rDwz: camera z orientation
    @return: object orientation, object translation in the world
    """
    global bUseAlMath
    if bUseAlMath:
        #print("INF: abcdk.numeric: using almath")
        import almath
        tCameraToObject = almath.transformFromPosition6D(almath.Position6D([aTranslation[0], aTranslation[1], aTranslation[2], aOrientation[0], aOrientation[1], aOrientation[2]]))
        tRobotToCamera= almath.transformFromPosition6D(almath.Position6D([rDx, rDy, rDz, rDwx, rDwy, rDwz]))
        tRobotToObject = tRobotToCamera * tCameraToObject
        aPose6D = np.array(almath.position6DFromTransform(tRobotToObject).toVector())
        return aPose6D[3:], aPose6D[:3]
    else:
        newTranslation = chgRepere(aTranslation[0], aTranslation[1], aTranslation[2], rDx, rDy, rDz, rDwx, rDwy, rDwz)
        newOrientation = (aOrientation + np.array([rDwx, rDwy, rDwz]))
        return newOrientation, newTranslation

def getAbsMin(a, b):
    """
    return the min of abs(a), abs(b), and add the sign of a.
    """
    return np.sign(a) * np.min([abs(a), abs(b)])


def testMaison():
    import pylab
    poseRobot = np.array([10, 15, 0, 0, 0, math.pi/3])

    vecDir = polarToCartesian(1, poseRobot[5])
    pylab.quiver(poseRobot[0], poseRobot[1], vecDir[0], vecDir[1])

    destPose = np.array([25, 40, 0, 0, 0, 0])
    res = convertPoseWorldToTorso(destPose, poseRobot)
    dx = res[0]
    dy = res[1]
    dwz = res[5]
    #print( res )
    #vecDir = polarToCartesian(1, res[5])
    #pylab.quiver( res[0], res[1], vecDir[0], vecDir[1], color='r')

    #dest
    #dx = 4
    #dy = 2

    poseRobotAfterMove = convertPoseTorsoToWorld(np.array([dx, dy, 0, 0, 0, dwz]), poseRobot)

    vecDir = polarToCartesian(1, poseRobotAfterMove[5])
    pylab.quiver( poseRobotAfterMove[0], poseRobotAfterMove[1], vecDir[0], vecDir[1], color='g')
    #print poseRobotAfterMove[0], poseRobotAfterMove[1]
    pylab.axis('equal')

    pylab.show()

def testconvertPoseWorldToTorso():
    """
    autotest
    """
    val = convertPoseWorldToTorso([0, 0, 0, 0, 0, 0],  [0, 0, 0, 0, 0, 0])
    np.testing.assert_almost_equal(val, np.array([0., 0., 0., 0., 0., 0.]))

    val = convertPoseWorldToTorso([1, 1, 0, 0, 0, 0],  [0, 0, 0, 0, 0, 0])
    np.testing.assert_almost_equal(val, np.array([1., 1., 0., 0., 0., 0.]))


    val = convertPoseWorldToTorso([0, 0, 0, 0, 0, 0],  [1, 1, 0, 0, 0, 0])
    np.testing.assert_almost_equal(val, np.array([-1., -1., 0., 0., 0., 0.]))

    ## NDEV le test suivant ne passe pas avec almath..
    val = convertPoseWorldToTorso([1, 2, 0, 0, 0, 0],  [0, 0, 0, 0, 0, math.pi/2.0])
    np.testing.assert_almost_equal(val, np.array([2., -1., 0., 0., 0., -math.pi/2.]))
    ##print val
    val = convertPoseWorldToTorso([1, 2, 0, 0, 0, 0],  [0, 0, 0, 0, math.pi/2, math.pi/2.0])
    #val = convertPoseWorldToTorso([1, 2, 0, 0, 0, 0],  [0, 0, 0, 0, 0, math.pi/2.0])

    #tPInFrameRobot = numeric.convertPoseWorldToTorso(aTargetP6D, aRobot )

    p6DObjectRtWorld = np.zeros(6)
    p6DRobotRtWorld  = np.array([1 , 1, 0, 0.0, 0.0, math.pi/2.0])
    val = convertPoseWorldToTorso(p6DObjectRtWorld, p6DRobotRtWorld)
    print( val )
    np.testing.assert_almost_equal(val, np.array([-1, 1, 0, 0, 0, -math.pi/2.0]))



def intersectionPlaneSegment(planePt, planeNormalVector, segmentPtA, segmentPtB ):
    """
    Return the 3D interesection point of a 2D plane and a segment if it exists.
    If the segments is in the plane, then [segmentPtA, segmentPtB] is return.

    planePt: point in the plane
    planeNormalVector: normal vector that define the plane
    segmentPtA: First point of the segment
    segmentPtB: First point of the segment

    return:
    - case interesection exists, and it's a point in the segment: return interesectionPt
    - case interesection exists it's the segment: return [segmentPtA, segmentPtB]
    - caes no interesection: return None

    """
    segmentVector = (segmentPtB - segmentPtA)
    rDenominator = np.dot(segmentVector, planeNormalVector)
    rNumerator = np.dot((planePt - segmentPtA), planeNormalVector)
    if rDenominator == 0: # vector are orthogonal
        if rNumerator != 0: # segment not in plane
            return None   # no interesection
        else: # the whole segment is in the plane
            return [segmentPtA, segmentPtB]
    else: # vector are not orthogonal
        rDistanceFromPtA = float(rNumerator) / float(rDenominator)
        #print( rDistanceFromPtA )
        if (rDistanceFromPtA<0) or  (rDistanceFromPtA > abs(dist3D(segmentPtA, segmentPtB))):
            return None  # interesection outside of segment
        else:
            ptIntersection = rDistanceFromPtA * segmentVector + segmentPtA
            return ptIntersection

def test_intersectionPlaneSegment():

    planePt = np.array([0,0,0])
    planeNormalVector = np.array([0, 0 , 1])  # plan origine
    segmentPtA = np.array([0,0,10])
    segmentPtB = np.array([1,0,10])

    # there should be no interesection
    ptIntersection = intersectionPlaneSegment(planePt, planeNormalVector, segmentPtA, segmentPtB)
    assert( ptIntersection == None )

    planePt = np.array([0,0,0])
    planeNormalVector = np.array([0, 0 , 1])  # plan origine
    segmentPtA = np.array([0,0,10])
    segmentPtB = np.array([0,0,-10])
    # there should be an interesection in 0,0,0
    ptIntersection = intersectionPlaneSegment(planePt, planeNormalVector, segmentPtA, segmentPtB)
    np.testing.assert_almost_equal(ptIntersection, np.array([0,0,0]))

    planePt = np.array([0,0,0])
    planeNormalVector = np.array([0, 0 , 1])  # plan origine
    segmentPtA = np.array([0,0,0])
    segmentPtB = np.array([100,100,0])
    # whole segment is in the plane..
    aIntersection = intersectionPlaneSegment(planePt, planeNormalVector, segmentPtA, segmentPtB)
    assert( aIntersection == [segmentPtA, segmentPtB] )


    planePt = np.array([0,0,0])
    planeNormalVector = np.array([0, 0 , 1])  # plan origine
    segmentPtA = np.array([1, -1,-0.2])
    segmentPtB = np.array([1, -1, -1])
    aIntersection = intersectionPlaneSegment(planePt, planeNormalVector, segmentPtA, segmentPtB)

    assert( aIntersection == None )


    rCumElapsedTime = 0
    import time
    for i in range(1000):
        segmentPtA = np.random.rand(3)
        segmentPtB = np.random.rand(3)
        planePt = np.random.rand(3)
        planeNormalVector = np.random.rand(3)

        rStartTime = time.time()
        intersectionPlaneSegment(planePt, planeNormalVector, segmentPtA, segmentPtB)

        rElapsedTime = time.time() - rStartTime
        rCumElapsedTime += rElapsedTime

    print("Cum elpased time for 1000 interesection computation is %s" % rCumElapsedTime) # Lgeorge 29 mai 2014: 0.0111587047577sec on coreI7
    assert(rCumElapsedTime < 1)  #  moins 'dune seconde

def _intersectionPlaneCuboid(planePt, planeNormalVector, aListOfCuboidVertex):
    """
    return the list of point that are in the interesection of a cuboid and a plane

    if you need a polygon, just run a convexHullDetection on this list of points

    aListOfCuboidVertex: vertex of the cuboid (it's a list of tuple of point3d)
    """
    aPtsInIntersection = []
    for aVertex in aListOfCuboidVertex: ## TODO : mettre un iterateur icii.. aller plus vite

        intersection = intersectionPlaneSegment(planePt, planeNormalVector, aVertex[0], aVertex[1])
        if intersection != None:
            if type(intersection) is list:
                aPtsInIntersection.append(intersection[0])
                aPtsInIntersection.append(intersection[1])
            else:
                aPtsInIntersection.append(intersection)

    return aPtsInIntersection


def test_intersectionPlaneCuboid():
    planePt = np.array([0,0,0])
    planeNormalVector = np.array([0, 0 , 1])  # plan origine
    aVertex = []
    aZ = [-1,1]
    for z in aZ :
        aPts = []
        x,y = 1,1
        aPts.append([x,y])
        x,y = -1,1
        aPts.append([x,y])
        x,y = -1,-1
        aPts.append([x,y])
        x,y = 1, -1
        aPts.append([x,y])

        for _ptA in aPts:
            for _ptB in aPts[1:] + [aPts[0]]:
                ptA = _ptA + [z]
                ptB = _ptB + [z]
                ptAinv = _ptA + [aZ[0]]
                aVertex.append([np.array(ptA), np.array(ptB)])
                aVertex.append([np.array(ptA), np.array(ptAinv)])

    print( aVertex )
    import time
    rTimeStart = time.time()
    aIntersection = _intersectionPlaneCuboid(planePt, planeNormalVector, aVertex)
    rTimeElapsed = time.time() - rTimeStart
    print("rTimeElapsed %s" % rTimeElapsed)
    import pylab

    for pt in aIntersection:
        pylab.scatter(pt[0], pt[1])
    pylab.show()
    assert( rTimeElapsed < 0.01)


def getCoordinateRectangle(aPose2DOrigin, rDx, rDy):
    x_0, y_0 = np.array([rDx/2.0, -rDy/2.0])
    x_1, y_1 = np.array([rDx/2.0, rDy/2.0])
    x_2, y_2 = np.array([-rDx/2.0, rDy/2.0])
    x_3, y_3 = np.array([-rDx/2.0, -rDy/2.0])

def getCoordinateCuboid(aPose3DOrigin, rDx, rDy, rDz):

    x_0, y_0 = np.array([rDx/2.0, -rDy/2.0])
    x_1, y_1 = np.array([rDx/2.0, rDy/2.0])
    x_2, y_2 = np.array([-rDx/2.0, rDy/2.0])
    x_3, y_3 = np.array([-rDx/2.0, -rDy/2.0])

def getVertexCuboid(aPose6D, rDx, rDy, rDz):
    aListPoints = []
    aVertex = []
    for nFace in [-1,1]:
        x_0, y_0 = [rDx/2.0, -rDy/2.0]
        aListPoints.append(np.array([x_0, y_0, nFace * rDz/2.0]))
        x_1, y_1 = [rDx/2.0, rDy/2.0]
        aListPoints.append(np.array([x_1, y_1, nFace * rDz/2.0]))
        x_2, y_2 = [-rDx/2.0, rDy/2.0]
        aListPoints.append(np.array([x_2, y_2, nFace * rDz/2.0]))
        x_3, y_3 = [-rDx/2.0, -rDy/2.0]
        aListPoints.append(np.array([x_3, y_3, nFace * rDz/2.0]))

    ## TODO: ici faire la transfoormee
    aListPoints_ = []
    for point in aListPoints:
        newPoint =  chgRepere(point[0], point[1], point[2], *aPose6D)

        aListPoints_.append(newPoint)
    aListPoints = aListPoints_
    aVertex.extend(zip(aListPoints[:], aListPoints[1:] + [aListPoints[0]]))
    aVertex.extend(zip(aListPoints[0:4], aListPoints[4:])) # les vertex entre les deux faces
    return aVertex

def segmentIntersectedAtOnePoint(a,b,c,d):
    """
    return the intersection point of segment [a,b] and [c,d] if it exists and is unique
    return None otherwise


    Il ne s'agit pas la de la methode optimal.. on fait une inversion de matrix.. il y a  peut etre plus simple:
        ## TODO : now : http://softsurfer.com/Archive/algorithm_0104/algorithm_0104B.htm
        ## comprendre le code python avec perp : http://stackoverflow.com/questions/3252194/numpy-and-line-intersections
        ## essayer de faire le code avec les determinants et cramer.. c'est plus algebrique mais ca devrait etre bien aussi

    """
    #print("intersection inputs are %s %s %s %s" % (a,b,c,d))

    xa,ya = a
    xb,yb = b
    xc,yc = c
    xd,yd = d
    # le systeme d'equation est : A x = b, avec (on l'obtient en pausant les equation de chaque droite, et en mettant les inconnus du meme cote
    A = np.matrix([[1,0,xa-xb,0],[0,1,ya-yb,0],[1,0,0,xc-xd],[0,1,0,yc-yd]])
    b = np.matrix([[xa],[ya],[xc],[yc]])

    if np.linalg.det(A) == 0:
        #print("no unique solution A is %s" % A)
        return None # pas de solution unique

    x = np.linalg.inv(A) * b
    if  not(0<=x[2]<=1) or not(0<=x[3]<=1):  ## l'intersection est dans le segment
        #print("not in segment %s" % x)
        return None
    aIntersection = x[0:2] # intersection
    return np.squeeze(np.asarray(aIntersection))  # we convert it to numpy array flat

def computeBarycenter(aListOf3DPoints):
    aBarycenter = np.mean(aListOf3DPoints, axis=0)
    return aBarycenter

def test_computeBarycenter():
    a = np.array([2,4,6])
    b = np.array([0,0,0])

    aBarycenter = computeBarycenter([a,b])
    np.testing.assert_allclose(aBarycenter, np.array([1,2,3]))
 #       np.testing.assert_allclose(aP6DRefAInRefB[3], aRes[3], atol=0.1)  # on ne doit pas changer l'orientation de y


def computeOrientationAngles(aPose3DA, aPose3DB):
    """
    return dwX, dwY, dwZ that corresonpd to orrientation of vector (aPose3DB-aPose3DA)
    """
    #TODO # TODO
    pass


def get2DPolygonProjection(planePt, planeNormalVector, aListOfCuboidVertex):
    import cv2
    aPoints3D = np.array(_intersectionPlaneCuboid(planePt, planeNormalVector, aListOfCuboidVertex))
    if aPoints3D.shape[0] == 0:
        print('no interesection')
        return None
    ## TODO: better projection..
    aPoints2D = aPoints3D[:, 0:2] # TODO better projection
    #aPolygon2DPoints = cv2.convexHull(np.array([a,b,c,d,e], dtype=np.float32))
    aPoints = np.array(aPoints2D, dtype=np.float32)

    aPolygon2DPoints = cv2.convexHull(aPoints)

    return aPolygon2DPoints.reshape(aPolygon2DPoints.shape[0], aPolygon2DPoints.shape[-1])

def computePlaneBaseVectors(planePt, planeNormalVector):
    ## TODO : a revoir.. on va dire qu'on travail en permanence dans le plan (1,0,0), (0,1,0), (0,0,1) pour la navigation pour l'instant..
    """
    return an orthornormal basis of the plane

    the return orthornormal basis is the projected of the canonical basis of the 3D EV.


    The case of a planeNormalVector with z coordinate=0 is not handled (return None)
    """

    rXn, rYn, rZn = planeNormalVector
    if rZn == 0:
        print("WARNING computePlaneBaseVectors: no basis returned because normal vector z coordinate==0")
        ## TODO
        #bv1 = np.array([0,0,1])
        #bv2 =
        return
    bv1 = np.array([1, 0, float(rYn)/rZn])  *  math.sqrt(1 + (rYn / rZn)**2 )
    bv2 = np.array([0, 1, float(rYn)/rZn])  *  math.sqrt(1 + (rXn / rZn)**2 )
    return bv1, bv2

def test_computePlaneBaseVectors():
    planePt = np.array([0,0,0])
    planeNormalVector = np.array([0,0,1])
    e1, e2 = computePlaneBaseVectors(planePt, planeNormalVector)
    np.testing.assert_almost_equal(e1, np.array([1,0,0]))
    np.testing.assert_almost_equal(e2, np.array([0,1,0]))


    # np.cross([1,0,0], [0,1,0]) = [0,0,1])

def boundingRect(a2DPoints):
    """ return the bounding rect of points
    a2DPoints: list of 2D tuple, or np.array

    return: a rectangle tuple(X,Y, width, height)
    >>> boundingRect([[1,0],[2,3]])
    (1, 0, 2, 4)
    >>> boundingRect(np.array([[1,0],[2,3]]))
    (1, 0, 2, 4)
    """
    a2DPoints = np.array([a2DPoints], dtype=np.float32)
    from cv2 import boundingRect as cv2BoundingRect
    return cv2BoundingRect(a2DPoints)
    
    

def rotate( pts, rAngle ):
    """
    rotate a list of pts [x1,y1,x2,y2,...] around 0,0
    - rAngle: angle in radians
    return a rotated list
    """
    input_type = type(pts)
    #if len(pts) > 10:
    # using numpy for optim
    mat_rot = np.array([[math.cos(rAngle), -math.sin(rAngle)], [math.sin(rAngle), math.cos(
        rAngle)]])
    pts = np.array(pts, dtype=np.float)
    pts.shape = (pts.size/2, 2)  # we reshape
    out = np.dot(pts, mat_rot.T)
    if (input_type == np.ndarray):
        return out
    else:
        return out.flatten().tolist()
    #else:
    #    out = [];
    #    c = math.cos(rAngle)
    #    s = math.sin(rAngle)
    #    for i in xrange( 0, len(pts), 2 ):
    #        x = pts[i];
    #        y = pts[i+1];

    #        x2 = x*c - y*s
    #        y2 = x*s + y*c
    #        out.append( x2 );
    #        out.append( y2 );
    #    return out


# rotate - end


def translate( pts, aOffset ):
    """
    translate a list of pts [x1,y1,x2,y2,...] by adding an offset
    aOffset: [offset_x1,offset_y1]
    return the translated list
    """
    out = [];
    for i in range( 0, len(pts), 2 ):
        x = pts[i];
        y = pts[i+1];        
        x2 = x + aOffset[0];
        y2 = y + aOffset[1];
        out.append( x2 );
        out.append( y2 );
    return out;
# translate - end


def autotest():
    test_computeBarycenter()
    assert( limitRange( 0,0,0) == 0 );
    assert( limitRange( 10,0,5) == 5 );
    assert( limitRange( -5,0.,5) == 0. );
    assert( limitRange( 500,1000,10) == 1000 ); # sounds like a bug, but it's a known limitation :)
    assert( dist2D_squared( [1,2],[3,4] ) == 8 );
    Choice.autoTest();
    print( "classic random:" );
    for _ in xrange( 10 ):
        print( random.randint( 0, 3 ) )

    print( "different random:" );
    for _ in xrange( 10 ):
        print( randomDifferent( 0, 3 ) )

    listRect = [ [0,0,10,10], [-5,5,20,-20], [0,0,6,6] ];
    listRectOut = simplifyRectangleList( listRect );
    #print( listRectOut );
    assert( listRectOut == [[-5, -20, 20, 10]] );
    listRectOut = simplifyRectangleList( listRect[::-1] );
    #print( listRectOut );
    assert( listRectOut == [[-5, -20, 20, 10]] );

    listRect = [ [0,0,10,10], [5,7,6,9] ];
    listRectOut = simplifyRectangleList( listRect );
#    print( listRectOut );
    assert( listRectOut == [[0,0,10,10]] );
    listRectOut = simplifyRectangleList( listRect[::-1] );
    #print( listRectOut );
    assert( listRectOut == [[0,0,10,10]] );

    assert( inRange01( 0 ) );
    assert( inRange01( 0.5 ) );
    assert( inRange01( 1 ) );
    assert( not inRange01( -1 ) );

    testconvertPoseWorldToTorso()
    test_inversePose()

    test_intersectionPlaneSegment()
    test_intersectionPlaneCuboid()
    test_computePlaneBaseVectors()

# autotest - end

if( __name__ == "__main__" ):
    autotest();
    import doctest
    doctest.testmod()
    #testconvertPoseWorldToTorso()
    #testMaison()

