# -*- coding: utf-8 -*-
###########################################################
# Aldebaran Behavior Complementary Development Kit
# Store any attribute forever on pepper
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

import os
import shutil
import time

def assert_equal( x, y ):
    if x != y:
        print( "%s != %s" % ( str(x), str(y) ) )
        assert(0)
        
class LongTermMemory:
    """
    a long term memory, just set or get values, and they will be there, forever.
    """
    
    def __init__( self, strOptionnalSavePath = "~/" ):
        strOptionnalSavePath = os.path.expanduser(strOptionnalSavePath)
        self.strSaveFileName = strOptionnalSavePath + "long_term_memory.dat"
        self.reset()
        self.load()
        
    def reset( self ):
        self.bMustSave = False
        self.values = dict()
        
    def load( self ):
        timeBegin = time.time()
        try:
            file = open(self.strSaveFileName, "rt" )
        except: return
        
        print( "INF: LongTermMemory.load: starting..." )
        self.reset()        
        while True:
            line = file.readline()
            if len(line) < 3:
                break
            #~ print( "DBG:line: %s" % line )
            lineval = eval(line)
            #~ print( "DBG:lineval: %s" % str(lineval) )
            name = lineval[0]
            self.values[name] = lineval[1]
        self.bMustSave = False            
        print( "INF: LongTermMemory.load: end (loaded variables nbr: %d)(takes: %5.2fs)" % (len(self.values),(time.time()-timeBegin)) )
        
    def save( self ):
        timeBegin = time.time()
        if not self.bMustSave:
            return
        #~ print( "INF: LongTermMemory.save: starting..." )
        
        try:
            shutil.copyfile( self.strSaveFileName, "/tmp/long_term_memory_"+str(time.time())+".bak")
        except IOError: pass
        
        file = open(self.strSaveFileName, "wt" )
        for name, datas in self.values.items():
            file.write('"%s", ' % name )
            file.write('%s\n' % repr(datas) )
        file.close()
        self.bMustSave = False
        #~ print( "INF: LongTermMemory.save: end (takes: %5.2fs)" %(time.time()-timeBegin) )
        
    def set( self, attribute_name, value ):
        """
        return True if modified, False if value were the same.
        """
        try:
            if self.values[attribute_name] == value:
                return False # won't go there if variable not known or is different
        except KeyError: pass
        
        self.values[attribute_name] = value
        self.bMustSave = True        
        self.save()
        return True
        
    def inc( self, attribute_name, value, default_value = 0 ):
        """
        incremente a variable and return its new value
        """
        value_orig = self.get( attribute_name, default_value )
        value_orig += value
        self.set( attribute_name, value_orig )
        return value_orig
        
    def get( self, attribute_name, defaultValue = None ):
        try:
                return self.values[attribute_name]
        except KeyError: pass
        return defaultValue
        
    def gets( self ):
        return self.values    
# class LongTermMemory - end

ltm = LongTermMemory()

def autoTest():
    ltm = LongTermMemory("/tmp/")
    ltm.reset()
    retVal = ltm.get( "tototutu", 142 )
    assert_equal(retVal, 142)    
    
    retVal = ltm.set("test", 1 )
    assert_equal(retVal, True)
    
    retVal = ltm.set("test", 1 )
    assert_equal(retVal, False)
    
    retVal = ltm.inc("count", 1 )
    assert_equal(retVal, 1)

    retVal = ltm.inc("count", 1 )
    assert_equal(retVal, 2)

    retVal = ltm.inc("count", -3, 0 )
    assert_equal(retVal, -1)
    ltm.reset()
    ltm.load()
    retVal = ltm.get("count" )
    assert_equal(retVal, -1)
    
if __name__ == "__main__":
        autoTest()