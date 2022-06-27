# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Memory Tools
# Author A. Mazel
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Memorise small thing, object state and ..."

print( "importing abcdk.memory" );

import mutex
import time


class ObjectEvents:
    
    kEventTypeAppear = 1 # static to class ObjectEvents
    kEventTypeDisappear = 2
    
    def __init__( self, nEventType, name, infos = None ):
        self.name = name
        self.nEventType = nEventType
        self.infos = infos
        self.time = time.time()
        
    def eventToTxt( self ):
        strOut = ""
        strOut += ""
        return strOut
        
class ObjectMemory:
    """
    Memorize information about the object seen in the scene. An object is described by an unique name (cat1, cat2, ...)
    """
    def __init__( self, rAnchoringDuration = 0.5, nIdxNameInObject = 0 ):
        """
        - rAnchoringDuration: what is the minimal time for decide an event is really occuring (no alternating between two state)
        """
        self.rAnchoringDuration = rAnchoringDuration
        self.nIdxNameInObject = nIdxNameInObject
        self.dEvents = dict() # name => ObjectEvents
        self.mutex = mutex.mutex()
        
    def _addEvent( self, nEventType, o ):
        name = o[self.nIdxNameInObject]
        if name in self.dEvents.keys():
            # an event exists for this object
            if time.time() - self.dEvents[name].time < self.rAnchoringDuration and self.dEvents[name].nEventType != nEventType:
                # do nothing: this event erase previous contrary one
                print( "DBG: ObjectMemory._addEvent: for object '%s', this new event %d (%s), erase previous one: %d (%s)" % (name, nEventType, o, self.dEvents[name].nEventType, self.dEvents[name].infos ) )
                del self.dEvents[name]
                return
        name = o[self.nIdxNameInObject]
        #if name in self.dEvents.keys():
        oe = ObjectEvents( nEventType, name, o )
        self.dEvents[name] = oe

    def appear( self, o ):
        """
        add an event about an object. object is a list with the name often in first position
        """
        while self.mutex.testandset() == False:
            print( "INF: ObjectMemory: already in, waiting..." )
            time.sleep( 0.001 )

        self._addEvent( ObjectEvents.kEventTypeAppear, o )
        
        self.mutex.unlock()
            
        
    def disappear( self, o ):
        while self.mutex.testandset() == False:
            print( "INF: ObjectMemory: already in, waiting..." )
            time.sleep( 0.001 )
        
        self._addEvent( ObjectEvents.kEventTypeDisappear, o )
        
        self.mutex.unlock()
        
    def appear_list( self, list_o ):
        """
        as appear and disappear, but from list of objects
        """
        for o in list_o:
            self.appear(o)
            
    def disappear_list( self, list_o ):
        for o in list_o:
            self.disappear(o)
        
        
    def _getEvents( self ):
        """
        """
        timeNow = time.time()
        added = []
        removed = []
        for k,e in self.dEvents.iteritems():
            if timeNow - e.time > self.rAnchoringDuration:
                if e.nEventType == ObjectEvents.kEventTypeAppear:
                    added.append( e.infos )
                else:
                    removed.append( e.infos )
        return (added,removed)        
    
    def getEvents( self ):
        """
        return a pair of list of object with associated events ([added], [removed]
        eg: ([object info added], [] )
        """
        while self.mutex.testandset() == False:
            print( "INF: ObjectMemory: already in, waiting..." )
            time.sleep( 0.001 )      
        ret = self._getEvents()
        self.mutex.unlock()
        return ret
        
    def getEventsAsTxt( self ):
        while self.mutex.testandset() == False:
            print( "INF: ObjectMemory: already in, waiting..." )
            time.sleep( 0.001 )        
        listA,listD = self._getEvents()
        strOut = ""
                
        if len(listD) > 0:
            strOut += "you remove " + listD[0][self.nIdxNameInObject]
            for e in listD[1:]:
                strOut += " and " +  e[self.nIdxNameInObject]
                
        if len(listA) > 0:
            if len(listD) > 0:
                strOut += " and "
            strOut += "you add " + listA[0][self.nIdxNameInObject]
            for e in listA[1:]:
                strOut += " and " +  e[self.nIdxNameInObject]

        if len(strOut) > 0:
            strOut += "."
        self.mutex.unlock()            
        return strOut
    # getEventsAsTxt - end
        
    def clearEvents( self ):
        """
        erase all pending events (events that would be return by getEvents*
        """
        while self.mutex.testandset() == False:
            print( "INF: ObjectMemory: already in, waiting..." )
            time.sleep( 0.001 )        
        timeNow = time.time()
        lisKeyToRemove = []
        for k,e in self.dEvents.iteritems():
            if timeNow - e.time > self.rAnchoringDuration:
                lisKeyToRemove.append(k)
                
        for k in lisKeyToRemove:
            del self.dEvents[k]
        self.mutex.unlock()
        
# class ObjectMemory - end
    


def autoTest():
    import test
    test.activateAutoTestOption();
    om = ObjectMemory()
    test.assert_check( om.getEvents(), ([],[]) )
    objectInfo1 = ["bag", 0.1, 0.3, -0.4 ]
    om.appear( objectInfo1 )
    om.appear( objectInfo1 )
    time.sleep(1.)
    test.assert_check( om.getEvents(), ([ ['bag', 0.1, 0.3, -0.4] ],[]) )
    test.assert_check( om.getEventsAsTxt(), "you add bag." )
    
    om.clearEvents()
    test.assert_check( om.getEvents(), ([],[]) )
    test.assert_check( om.getEventsAsTxt(), "" )

    objectInfo2 = ["cat", 0.2, 0.3, -0.4 ]
    objectInfo2b = ["cat", 0.4, 0.6, -0.9 ]    
    om.appear( objectInfo2 )
    time.sleep(0.1)
    test.assert_check( om.getEvents(), ([],[]) )

    time.sleep(0.1)    
    om.disappear( objectInfo2b )
    test.assert_check( om.getEvents(), ([],[]) )
    
    
    om.disappear( objectInfo1 )
    time.sleep(0.1)    
    test.assert_check( om.getEvents(), ([],[]) )
    time.sleep(0.45)
    test.assert_check( om.getEvents(), ( [], [ ['bag', 0.1, 0.3, -0.4]]) )
    test.assert_check( om.getEventsAsTxt(), "you remove bag." )

    #~ om.clearEvents()    # change nothing
    om.appear_list( [objectInfo1, objectInfo2] )
    time.sleep(0.55)
    test.assert_check( om.getEventsAsTxt(), "you add bag and cat." )
    
# autoTest - end

if( __name__ == "__main__" ):
    autoTest();