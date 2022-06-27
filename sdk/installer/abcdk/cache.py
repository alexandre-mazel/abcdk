# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Cache tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Tools to manipulate objects in cache."""
print( "importing abcdk.cache" );

import stringtools
import typetools

global_dictCacheObj = dict();
def getInCache( strName, typeType ):
  "get an objet from a list of cached object, return None if object not in cache"
#  debug( "altools.getInCache( %s )" % strName );
  if( typetools.isString( typeType ) ):
    strGeneratedName = strName + str( type( typeType ) );
  else:
    strGeneratedName = strName + str( typeType ); # => return the type
#  print( "altools.getInCache: strGeneratedName: '%s'" % strGeneratedName );
  global global_dictCacheObj;
  if( strGeneratedName in global_dictCacheObj ):
#    debug( "altools.getInCache: obj %s as %s caching success" % ( strName , strGeneratedName ) );
    return global_dictCacheObj[strGeneratedName];
#  debug( "altools.getInCache: obj %s as %s not in cache" % ( strName , strGeneratedName ) );
  return None;
# getInCache - end

def storeInCache( strName, obj ):
  "store an objet in a list of cached object"
  strGeneratedName = strName + str( type( obj ) );
#  print( "altools.storeInCache: strGeneratedName: '%s'" % strGeneratedName );
  global global_dictCacheObj;
  global_dictCacheObj[strGeneratedName] = obj;
#  debug( "altools.storeInCache: storing %s as %s" % ( strName , strGeneratedName ) );
# storeInCache - end

def removeFromCache( strName, typeType ):
    "remove an object from the cache, return False if the object isn't present in the cache"
    if( typetools.isString( typeType ) ):
        strGeneratedName = strName + str( type( typeType ) );
    else:
        strGeneratedName = strName + str( typeType ); # => return the type    
#    print( "altools.removeFromCache: strGeneratedName: '%s'" % strGeneratedName );        
    global global_dictCacheObj;
    try:
        del global_dictCacheObj[strGeneratedName];
        return True;
    except:
        pass
    return False;
# removeFromCache - end

def printCache():
    "print the cache contents"
    global global_dictCacheObj;
    print( "*** Cache contents ***" );
    print stringtools.dictionnaryToString( global_dictCacheObj );
    print( "*** Cache contents - end ***" );
# removeFromCache - end