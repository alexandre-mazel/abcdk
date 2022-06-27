# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Type tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

# this module should be called Type, but risk of masking with the keyword type.

"""Tools to know the type of a variable."""
print( "importing abcdk.typetools" );

def isInt( nVariable ):
    "has the variable the numeric type ?"
    return isinstance( nVariable, int );
# isInt - end

def isIntInString( strVariable ):
    "does this string contains an int ?"
    bRet = False;
    try:
        nDummy = int( strVariable );
        bRet = True;
    except:
        pass
    return bRet;
# isIntInString - end

def isIterable( aVariable ):
    "return True even with exotic type <type 'numpy.ndarray'>"
    try:
        len( aVariable );
    except BaseException, err:
        return False;
    return True;
# isIterable - end

def isDict( aVariable ):
    "has the variable the dict type ?"
    return isinstance( aVariable, dict );
# isDict - end    

def isArray( aVariable ):
    "has the variable the array type ?"
    #~ try:
        #~ aVariable[0];
    #~ except BaseException, err:
        #~ return False;
    #~ return not isString( aVariable ); #car les strings aussi ont la méthode crochet
    bRet = isinstance( aVariable, list );
    # print( "isArray( '%s' ) => %d" % ( str( aVariable ), bRet ) );
    return bRet;
# isArray - end


def isTuple( aVariable ):
    "has the variable the tuple type ?"
    bRet = isinstance( aVariable, tuple );
    # print( "isTuple( '%s' ) => %d" % ( str( aVariable ), bRet ) );
    return bRet;
# isTuple - end    


def isString( strVariable ):
  "has the variable the string type ? (bytes or unicode)"
  try:
    # if( type( strVariable ) == type( "some string") ):
    if isinstance( strVariable, basestring ): # True for both Unicode and byte strings
      return True;
  except BaseException, err:
    pass
  return False;
# isString - end

def isString_Bytes( strVariable ):
  "has the variable the string type bytes ?"
  try:
    if isinstance( strVariable, str ):
      return True;
  except BaseException, err:
    pass
  return False;
# isString_Bytes - end

def isString_Unicode( strVariable ):
  "has the variable the string type unicode ?"
  return isString( strVariable ) and not isString_Bytes( strVariable );
# isString_Unicode - end


def autoTest():
    assert( isInt( 0 ) );
    assert( isInt( 2 ) );
    assert( not isInt( 2.3 ) );
    assert( not isInt( 2.0 ) );
    assert( not isInt( "0" ) );

    assert( isString( "2" ) );
    assert( isString( "-2" ) );
    assert( not isString( -3 ) );
    
    assert( isDict( dict() ) );
    assert( not isDict( -3 ) );
    
    assert( isArray( list() ) );
    assert( isArray( [] ) );
    assert( isArray( [3,4] ) );
    assert( isArray( [[3,1,2],[4,3,6]] ) );
    assert( not isArray( dict() ) );
    
    assert( isIntInString( "0" ) );
    assert( isIntInString( "-3" ) );
    assert( isIntInString( "08" ) );
    assert( not isIntInString( "" ) );
    assert( not isIntInString( "3.5" ) );
    assert( not isIntInString( "int13" ) );
# autoTest - end    
    
# autoTest();

#~ print (time.time()