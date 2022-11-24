# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Arraytools tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Array tools"

# renammed from array to arraytools, to be more explicit.

print( "importing abcdk.arraytools" );

import random

import typetools


def dup( value ):
    """
    duplicate an array.
    The array won't be a copy of any other source value.
    No sub array will share data, it's different than copy.deepcopy ! (see below)
    """

    if typetools.isArray( value ):
        # in case of an array, we need to recreate a new one, and not a pointer on origin.
        newArray = [];
        for v in value:
            newArray.append( dup(v) );
        return newArray;
    
    if typetools.isDict( value ):
        newD = {};
        for k,v in value.iteritems():
            newD[k] = dup(v);
        return newD;
    
    # end of recursivity
    # print( "value is not an array: %s" % str( value ) );
    return value;
                
# dup - end

def testDup():
    val = [[[0,1,2],3,4],{"a": 1, "b":2},6];
    val2 = dup( val );
    val[0][0][0] = 153;
    val[2] = 154;
    val[1]["b"]=4
    print( "test dup: %s => %s" % ( str( val ), str( val2 ) ) );
    assert( val2[0][0][0] == 0 )    
    assert( val2[2] == 6 )
    assert( val2[1]["b"] == 2 )

    import copy
    aCorner = copy.deepcopy( [[0]*2]*4 );
    aCorner[0][1] = 3;
    #~ print aCorner; # bad: 3 are copied in the four sub array! ouin!
    assert( aCorner[1][1] == 3 )

    aCorner2 = dup( [[0]*2]*4 );
    aCorner2[0][1] = 3;
    #~ print aCorner2; # good: 3 are copied only in the first array! yes!
    assert( aCorner2[1][1] == 0 )
    
    
    


def arrayCreate( nNewSize, value = 0 ):
    "create an array of size nNewSize by inserting some value (default 0)"
    "The array won't be a copy of any other source value"
    newArray = [];
    for i in range( nNewSize ):
        newArray.append( dup( value ) );
    return newArray;
# arrayCreate - end

#~ val = [[1,2,3],4,5];
#~ val2 =arrayCreate( 3, val );
#~ val[0][0] = 153;
#~ val[2] = 154;
#~ print( "test arrayCreate: %s => %s" % ( str( val ), str( val2 ) ) );

def convertToArray( value ):
    "convert any type of value to array"
    "eg: convertToArray( (0,1,3,(0,1,2)) ) => [0,1,3,[0,1,2] ]"
    newValue = [];
    for v in value:
        if( typetools.isIterable( v ) ): # will work even with exotic type <type 'numpy.ndarray'>
            newValue.append( convertToArray( v ) );
        else:
            newValue.append( v );
    return newValue;
# convertToArray - end

#~ val = (0,1,2,(3,4,(5,6,7)));
#~ val2 = convertToArray( val );
#~ print( "%s => %s" % ( str( val ), str( val2 ) ) );

def arraySum( anArray ):
    "compute the sum of an array"
    "assume all element of the array could be added each others"
    sum = 0;
    for val in anArray:
        sum += val;
    return sum;
# arraySum - end


def chooseOneElem( aList ):
    "Pick randomly an element in a list "
    "each list contains elements, and optionnal probability ratio (default is 1)"
    "exemple of valid list:"
    "     'hello' (a non list with only one element)"
    "     ['hello', 'goodbye']"
    "     ['sometimes', ['often',10] ] often will appears 10x more often than sometimes (statistically)"
    
    # simple case
    if( not typetools.isArray( aList ) ):
        return aList;
        
    # generate statistic repartition
    listProba = [];
    nSum = 0;
    for elem in aList:
        if( typetools.isArray( elem ) and len( elem ) > 1 ):
            nVal = elem[1];        
        else:
            nVal = 1; # default value        
        listProba.append( nVal );
        nSum += nVal;
    nChoosen = random.randint( 0, nSum - 1 );
#    logToChoregraphe( "nChoosen: %d / total: %d / total different: %d (list:%s)" % ( nChoosen, nSum, len( aList ) , aList ) );
    nSum = 0;
    nIdx = 0;
    for val in listProba:
        nSum += val;
        if( nSum > nChoosen ):
            elem = aList[nIdx];
            if( typetools.isArray( elem ) ):
                return elem[0];
            return elem;
        nIdx += 1;
        
    return "not found or error";
# chooseOneElem - end

def constructFromNamedArray(obj, aNamedArray ):
    "construct a python object from an array of couple [attr_name,attr_value]"
    "reverse of stringtools.dictionnaryToString ???"
    for attr_name, attr_value in aNamedArray:
        try:
            attr = getattr( obj, attr_name );
            if( attr != None ):
                # eval( "obj." + attr_name + " = '" + attr_value + "'" );
                setattr( obj, attr_name, attr_value );
        except BaseException as err:
            print( "WRN: constructFromNamedArray: ??? (err:%s)" % ( str( err ) ) );
            pass
  # for
#   print( dump( obj ) );
    return obj;
# constructFromNamedArray - end

def dictToArray( dico, bSort = False ):
    """
    Convert a dictionnary to an array [ [k1,value1], [k2,value2]... ]
    bSort: when set: sort the array by their value: bigger first
    v0.6
    """
    retVal = [];
    if( len( dico ) > 0 ):
        for k,v in dico.iteritems():
            if( typetools.isDict( v ) ):
                retVal.append( [k,dictToArray(v)] );
            else:
                retVal.append( [k,v] ) # modif laurent
                retVal.append( [k,v] ); 
        if( bSort ):
            retVal.sort(key=lambda a:a[1], reverse=True );
    return retVal;
# dictToArray - end

def arrayToDict( elements, bTreatsEmptyArrayAsDict = False ):
    """
    Convert a dictionnary to an array [ [k1,value1], [k2,value2]... ]
    - bTreatsEmptyArrayAsDict: when set [['a', []]] => {'a': {}} else it would be {'a': []}
    WARNING: it won't reconstruct original array on every case!
    """
    retVal = dict();
    for k, v in elements:
        #~ print( "k:%s, v: %s" % (k,v) );
        if( 
                        typetools.isArray( v ) 
                and  (
                            bTreatsEmptyArrayAsDict 
                            or 
                            ( 
                                    (len(v) > 0 ) 
                                and (
                                                typetools.isString( v[0] )  # first check it could be a key
                                            or typetools.isArray( v[0] )   # or if it's not a key, so it's a sub array
                                        )  
                            )
                        ) 
        ):
            #~ print( "v is array to dictable: %s" % str( v ) );
            v = arrayToDict( v );
            retVal[k] = v;
        else:
            if( not typetools.isString( k ) ):
                # in fact we're not in an array, aborting, and returning elements as before
                return elements;
            retVal[k] = v;
    return retVal;
# arrayToDict - end

#~ print dictToArray( { "a": 123 } );
#~ print arrayToDict( dictToArray( { "a": 123 } ) );
# print arrayToDict( ['a', 'b', 'c'] ); # will raise an error
#~ print dictToArray({"a":{}})

def simplifyArray( a ):
    """
    remove nested solitary element in an array and subarray
    - a: an array
    return a simplied array.
    eg: [[[178, 901]], [[177, 902]], [[177, 904]]] => [[178, 901], [177, 902], [177, 904]]
    """
    out = [];
    for elem in a:
        if( len(elem) == 1 and typetools.isArray(elem[0]) ):
            out.append( elem[0] );
        else:
            out.append( elem );
    return out;
# simplifyArray - end

#~ print( simplifyArray(  [[[178, 901]], [[177, 902]], [[177, 904]]] ) );

def listPointToTuple( listPoints ):
    """
    todo: clean and comment and test!
    """
    listOut = [];
    for i in range( 0, len( listPoints ), 2 ):
        ptx = listPoints[i];
        pty = listPoints[i+1];
        if( ptx != 0. or pty != 0. ):        
            listOut.append( (ptx, pty) );
    return listOut;
    
    
def convertTupleListAngleToImagePixels( listTupleAngles, w, h ):
    """
    todo: clean and comment and test!
    """
    
    listOut = [];
    for pt in listTupleAngles:
        listOut.append( ( (-int(pt[0]*w)+w/2),int(pt[1]*h)+h/2 ) );
    return listOut;

def convertAngleToImagePixels( x, y, w, h ):
    return ( (-int(x*w)+w/2),int(y*h)+h/2 );
    
def convertSizeToImagePixels( sx, sy, w, h ):
    return ( (int(sx*w)),int(sy*h) );
    
def saveToFile( a, strFilename ):
    """
    save an array or a dict to a file, return true if ok
    the array can contain any type of data, having the repr method
    """
    if isinstance( a, dict ):
        return False # TODO
    file = open( strFilename, "wt" )
    if( not file ):
        return False
    if( 0 ):
        file.write( "[" )
        for e in a:
            s = repr(e)
            file.write(s)
            file.write(",")
        file.write( "]" )
    else:
        import json
        json.dump( a, file )
    file.close()
    return True
# saveToFile - end

def readFromFile( strFilename ):
    """
    read an array or a dict to a file, return the constructed object or None in case of error
    """
    file = open( strFilename, "rt" )
    if( not file ):
        return None
    if( 0 ):
        buf = file.read()
        file.close()
        a = eval(buf) # lazy but can generate security issue in your program. if buf contain for instance: __builtins__.__import__("os").unlink("/tmp/data")
    else:
        import json
        a = json.load( file )
    return a
# saveToFile - end
#~ readFromFile( "/tmp/risk" )

def dist( a, b, anRowToSkip  = [] ):
    """
    find the distance, between to array by comparing each respective element.
    eg: 
        [1,2,3] and [1, 2, 4] => 1
        [1,2,3] and [1, 0, 3] => 2
        [1,2,3] and [1,2] => 3 (all missing data are considered as 0)
        - anRowToSkip: a list of column to skip, beginning at 0.
          eg: [1,2,3] and [1, 0, 3],  with anRowToSkip = [1] => 0
    """
    n = max(len(a),len(b))
    rDist = 0
    for i in range(n):
        if( i not in anRowToSkip ):
            if i < len(a):
                aVal = a[i]
            else:
                aVal = 0
            if i < len(b):
                bVal = b[i]
            else:
                bVal = 0
            if( isinstance( aVal, basestring ) or isinstance( bVal, basestring )  ):
                if( aVal != bVal ):
                    rDist += 1 # different string => 1
                # else 0
            else:
                rDist += abs(bVal - aVal)
    return rDist
# dist - end

def findNearest( a, l, anRowToSkip  = [] ):
    """
    in a list of list: find the nearest element to l
    return a pair: index in [a, dist] or None if empty list
    - anRowToSkip: cf dist method
    """
    if len(a) == 0:
        return None
    rDistMin = 1e9
    nIdxMin = -1
    for i in range(len(a)):
        rDist = dist( a[i], l, anRowToSkip=anRowToSkip )
        if rDist < rDistMin:
            rDistMin = rDist
            nIdxMin = i
    return [nIdxMin, rDistMin]
    
def findInterestingResultsFromClassConfidencePair( listOfResults, listOfInterest = [], rConfidenceThreshold = 0.8, nConfidenceIndex = 1, bInputListIsSortedByConfidence = True ):
    """
    take list of pairs (or more) [ ["human", 3.1, "toto"], ["dog", 0.9, 1,2,3], ["toothbrush", 0.3, "a", "b", "c"] ]
    and filter all object not interesting
    - listOfResults: list of class, results.
    - listOfInterest: list of class of interest. eg: ["human, "toothbrush"] if empty: all
    - rConfidenceThreshold: threshold: filter, all that is below this point
    - nConfidenceIndex: by default the confidence index is the 2nd value (just after class name). You can change it.
    - bInputListIsSortedByConfidence: if not, high confidence could be anywhere in the list
    return the list filtered and sorted by confidence
    """
    listOut = []
    for res in listOfResults:
        rConf = res[nConfidenceIndex]
        if bInputListIsSortedByConfidence and rConf < rConfidenceThreshold:
            break
        if rConf < rConfidenceThreshold:
            continue            
        if listOfInterest != [] and res[0] not in listOfInterest:
            continue

        listOut.append( res )
    if not bInputListIsSortedByConfidence:
        listOut.sort(key=lambda a:a[nConfidenceIndex], reverse=True )
    return listOut
# findInterestingResultsFromClassConfidencePair - end

def findDifferenceFromClassConfidencePair( listOfResultsOld, listOfResultsNew, nKeyIndex = 0 ):
    """
    compare two lists, and return a pair (added, removed) based only on first element.
    eg: [ ["dog", 1, 2, 3], ["mouse", 1., 2, 3]] and [ ["dog", 3, 4, 5], ["cat", 1., 2, 3]] will return: ([["cat", 1., 2, 3]], [["mouse", 1., 2, 3]])
    ASSUME: no duplicate
    """
    dOld = dict()
    dNew = dict()
    for v in listOfResultsOld:
        dOld[v[nKeyIndex]] = v
    for v in listOfResultsNew:
        dNew[v[nKeyIndex]] = v
        
    dOld_keys = set(dOld.keys())
    dNew_keys = set(dNew.keys())
        
    addedKey = dNew_keys - dOld_keys
    removedKey = dOld_keys - dNew_keys
    
    added = []
    for k in addedKey:
        added.append(dNew[k] )
    
    removed = []    
    for k in removedKey:
        removed.append(dOld[k] )    
        
    return (added, removed)
        
# findDifferenceFromClassConfidencePair - end    


def autoTest():
    import test
    a = arrayCreate( 8, 2 );
    test.assert_check( arraySum( a ), 16 );    

    d = {"a": 123, "b": [1,2,3], "c": {"pomme": 2, "caca": 3}, "d": 12.3, "embedded2": {"train": {"nuage": 6, "soleil": 2} } };
    print( d );
    a = dictToArray( d );
    print( a );
    d2 = arrayToDict( a );
    print( d2 );
    assert( d2 == d );    
    
    assert( {} == arrayToDict(dictToArray({}) ) );

    d = {"a":{}};
    print( d );
    a = dictToArray( d );
    print( a );
    d2 = arrayToDict( a, bTreatsEmptyArrayAsDict = True );
    print( d2 );
    assert( d2 == d );    
    d2 = arrayToDict( a, bTreatsEmptyArrayAsDict = False );
    print( d2 );
    assert( d2 == {'a': []} );
    
    d = {1: {'P07': [[0.3211357075700192, 0.08681054247451304], [-0.9747738710942114, 0.22319475852269827]]}};
    print( d );
    a = dictToArray( d );
    print( a );
    d2 = arrayToDict( a );
    print( d2 );
    assert( d2 == d );
    
    a = [["Jean pierre", 1, 3, 5.6],  ["Francois", 4, 2, 6.9]]
    test.assert_check( saveToFile( a, "/tmp/testarraytools.txt" ) )
    test.assert_check( readFromFile( "/tmp/testarraytools.txt" ), a )
    
    a = []
    test.assert_check( saveToFile( a, "/tmp/testarraytools2.txt" ) )
    test.assert_check( readFromFile( "/tmp/testarraytools2.txt" ), a )
    
    a = ["françois"]
    test.assert_check( saveToFile( a, "/tmp/testarraytools.txt" ) )
    test.assert_check( readFromFile( "/tmp/testarraytools.txt" ), [u"fran\xe7ois"] ) # DOESN'T WORKS with ascii "as it": we need to decode them!
    
    test.assert_check( dist([1,2,3],[1,2,3]), 0 )
    test.assert_check( dist([1,2,3],[1,3]), 4 )
    test.assert_check( dist([1,2,3],[10,20,30]), 54 )
    test.assert_check( dist([1,2,3],[10,20,30],[0,2]), 18 )
    
    test.assert_check( findNearest([[1,2,3],[10,20,30]],[6,10,14]), [0,24] )
    test.assert_check( findNearest([["jean",2,3],["francois",10,20]],[8,10,15]), [1,6] )
    
    test.assert_check( findInterestingResultsFromClassConfidencePair( [["human", 3.1, "toto"], ["dog", 3.9, 1,2,3], ["toothbrush", 0.3, "a", "b", "c"]], ["human","dog"], bInputListIsSortedByConfidence = False ), [['dog', 3.9, 1, 2, 3], ['human', 3.1, 'toto']] )
    test.assert_check( findDifferenceFromClassConfidencePair( [ ["dog", 1, 2, 3], ["mouse", 1., 2, 3]],  [ ["dog", 3, 4, 5], ["cat", 1., 5, 1321]] ), ([['cat', 1.0, 5, 1321]], [['mouse', 1.0, 2, 3]]) )
    test.assert_check( findDifferenceFromClassConfidencePair( [ ["papa", 1, 2, 3] ],[] ), ([], [ ["papa", 1, 2, 3] ]) )
    test.assert_check( findDifferenceFromClassConfidencePair( [],[ ["cat", 1, 2, 3] ] ), ([ ["cat", 1, 2, 3] ], [] ) )
    test.assert_check( findDifferenceFromClassConfidencePair( [],[] ), ([],[]) )
    
    
    
    
    print( "autoTest: ok" );
# autoTest - end

if( __name__ == "__main__" ):
    autoTest();
