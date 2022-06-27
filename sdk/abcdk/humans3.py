# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# User knowledge tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""User knowledge tools"""
print( "importing abcdk.humans3" );

import datetime
import os
import shutil
import time

def assert_equal(a, b):
    if a != b:
        print( "ERR: assert failed: %s != %s " % (str(a),str(b) ) )
        assert 0
        
def getTodayString():
    """
    return the today string value like: "1974_08_19"
    (from abcdk.stringtools, to avoid including it)
    """
    datetimeObject = datetime.datetime.now()
    strTimeStamp = datetimeObject.strftime( "%Y_%m_%d")
    return strTimeStamp

class Human:
    """
    This class handle users knowledge about humans (name, last seen, country origin, facts and likes...)
    user are recognised by their ID
    
    Liking management example:
    - humanManager.updateLike( "spinash", 0. ) => if there's an active human, it will be recorded (or update) he dislikes "spinash"
    - humanManager.getLike( "spinash" ) => if the active human is the previous one, will return 0. None if it's another one (with unknown 'spinash' liking knowledge)
    - humanManager.getLikes() => will return a dictionnary of all known liking
    
    - HumanManager.generateTextFromLike( attribute, value ) => built an english text describing a liking
    - generateTextFromLikes(a dict - like the one from getLikes) => built an english text describing all liking of a person
    
    """

    def __init__( self, nHumanId, strLastName = "Unknown", strChristianName = "Unknown", strCountry = "fr", dictPronounciation = {} ):
        self.nHumanId = nHumanId;
        self.strLastName = strLastName;
        self.strChristianName = strChristianName;
        self.strCountry = strCountry;
        self.aLanguages = [strCountry]
        self.dictPronounciation = dictPronounciation; # for each lang, the pronounciation of name and christian name, each element could be set to None
        self.bIsWoman = False; # sadly default is male.
        self.timeLastSeen = None; # default is never
        self.nCptTimeSeen = 0; # nbr time we saw that human
        self.nDayWithoutSeeing = None;  # the nbr of day from today without having seen him (will be reseted tomorrow)
        self.nStateToday = 0; # the state of the knowledge of the human: what is next ?. 0: hello to exchange; 1: healing question; 2: curious question; 3: passe moi le sel / nothing
        self.aMemoInfo = []; # a list of memo to tell from someone, a memo is a field: [id_creator,date_creation,message], None: this person has never got memo, []: perhaps some memo, but no one their
        self.nCptSeenWithGlasses = 0;
        self.bLastSeenWithGlasses = False;
        self.timeLastSeenWithGlasses = None;
        
        # about knowledge # all keys in lower case !!!
        self.facts = {} # for each attribute, its value, -- eg: "birth place":  "London"
        self.likes = {} # for each attribute, the human liking. --  eg: "green beans": 1. 1: like very much, 0.: dislike, 0.5: average
        
        self.strTodayFactsDate = "" # the date of the today facts (if none for today, or the day has just change, then it's something else than "2019_10_22"
        self.todayFacts = {} # for each attribute, its value,  "already spoke of menu ?": True
        
    # __init__ - end
    
    def setIdentity( self, strLastName, strFirstName ):
        """
        add real identity afterward
        """
        self.strLastName = strLastName;
        self.strChristianName = strFirstName;

    #~ def __getattr__(self, name):
        #~ if name in self:
            #~ return self[name]
        #~ return None

    #~ def __setattr__(self, name, value):
        #~ self[name] = value

    def __str__( self ):
        strOut = "\n";
        strOut += "- nHumanId: %s\n" % self.nHumanId;
        strOut += "- strLastName: %s\n" % self.strLastName;
        strOut += "- strChristianName: %s\n" % self.strChristianName;
        strOut += "- strCountry: %s\n" % self.strCountry;
        strOut += "- aLanguages: %s\n" % self.aLanguages;
        strOut += "- is woman: %s\n" % self.bIsWoman;
        strOut += "- last seen: %s\n" % self.timeLastSeen;
        strOut += "- nCptTimeSeen: %s\n" % self.nCptTimeSeen;
        strOut += "- nDayWithoutSeeing: %s\n" % self.nDayWithoutSeeing;
        strOut += "- nStateToday: %s\n" % self.nStateToday;
        strOut += "- aMemoInfo: %s\n" % self.aMemoInfo;
        strOut += "- nCptSeenWithGlasses: %s\n" % self.nCptSeenWithGlasses;
        strOut += "- bLastSeenWithGlasses: %s\n" % self.bLastSeenWithGlasses;        
        strOut += "- timeLastSeenWithGlasses: %s\n" % self.timeLastSeenWithGlasses;
        strOut += "- facts: %s\n" % self.facts;
        strOut += "- likes: %s\n" % self.likes;
        strOut += "- strTodayFactsDate: %s\n" % self.strTodayFactsDate;
        strOut += "- todayFacts: %s\n" % self.todayFacts;
        return strOut;
    # __str__ - end
    
    def __repr__( self ):
        strOut = ""
        strOut += "%d," % self.nHumanId
        strOut += "'%s'," % self.strLastName
        strOut += "'%s'," % self.strChristianName
        strOut += "'%s'," % self.strCountry
        strOut += "%s," % self.aLanguages.__repr__()
        strOut += "%s," % self.bIsWoman
        strOut += "%s," % self.timeLastSeen
        strOut += "%s," % self.nCptTimeSeen
        strOut += "%s," % self.nDayWithoutSeeing
        strOut += "%s," % self.nStateToday
        strOut += "%s," % self.nDayWithoutSeeing
        strOut += "%s," % self.aMemoInfo
        strOut += "%s," % self.nCptSeenWithGlasses
        strOut += "%s," % self.bLastSeenWithGlasses
        strOut += "%s," % self.timeLastSeenWithGlasses
        strOut += "%s," % self.facts
        strOut += "%s," % self.likes
        strOut += "'%s'," % self.strTodayFactsDate
        strOut += "%s," % self.todayFacts        
        return strOut
        
    def initFromTuple( self, tupleWithData ):
        
        self.nHumanId, self.strLastName, self.strChristianName, self.strCountry, self.aLanguages, self.bIsWoman, self.timeLastSeen, self.nCptTimeSeen, \
            self.nDayWithoutSeeing, self.nStateToday, self.nDayWithoutSeeing, self.aMemoInfo, self.nCptSeenWithGlasses, self.bLastSeenWithGlasses, \
            self.timeLastSeenWithGlasses, self.facts, self.likes, self.strTodayFactsDate, self.todayFacts = tupleWithData
    
    def updateLike(  self, strAttribute, value ):
        """
        return True if ok, or False if nothing is changed
        """
        strDebugPrevLike = self.getLike(strAttribute)
        if strDebugPrevLike == value:
            return False        
        print( "Human.updateLike: %s: %s => %s" % (strAttribute,strDebugPrevLike,value) )
        self.likes[strAttribute.lower()] = value
        return True
        
    def getLike(  self, strAttribute ):
        """
        return None if no like or no active human
        """
        try:
            return self.likes[strAttribute.lower()]
        except KeyError as err:
            return None
        
    def getLikes( self ):
        """
        return a dictionnary of liking or {} if no known liking
        """
        return self.likes
        
    def _updatePotentialNewDay( self ):
        """
        """
        # old piece of code what:        
        #~ nDeltaDay = datetime.timedelta( seconds = (time.time()- self.timeLastSeen) ).days;
        #~ print( "INF: HumanManager.updateSeen: nDeltaDay: %d" % nDeltaDay );
        #~ if( nDeltaDay > 0 ):
            #~ some code
        
        strToday = getTodayString()
        if self.strTodayFactsDate == strToday:
            return
        # reset today facts
        self.todayFacts = dict()
        self.strTodayFactsDate = strToday
        nDeltaDay = datetime.timedelta( seconds = (time.time()- self.timeLastSeen) ).days;
        self.nDayWithoutSeeing = nDeltaDay;
        self.nStateToday = 0;        
        
    def setTodayFact( self, strFactName, value ):
        """
        Return True if set is effective, false if already set at the same value
        """
        self._updatePotentialNewDay()
        try:
            if self.todayFacts[strFactName] == value:
                return False # won't go there if variable not known or is different
        except KeyError: pass        
        self.todayFacts[strFactName] = value
        return True
        
    def getTodayFact( self, strFactName, defaultValue = None ):
        self._updatePotentialNewDay()
        try:
                return self.todayFacts[strFactName]
        except KeyError: pass
        return defaultValue      
        
    def updateSeen( self ):
        if( self.timeLastSeen == None or time.time() - self.timeLastSeen > 5*60 ): # pas vu depuis plus de 5 minutes !
            self.nCptTimeSeen += 1;

        if( self.timeLastSeen != None ):
            self._updatePotentialNewDay()
        self.timeLastSeen = time.time();
        #~ if( bWasWearingGlasses ):
            #~ self.nCptSeenWithGlasses += 1;
            #~ self.timeLastSeenWithGlasses = time.time();
        #~ self.bLastSeenWithGlasses = bWasWearingGlasses;        
        
    def isKnown( self ):
        return self.nCptTimeSeen > 1
        
    def getTextToSay( self ):
        
        #when calling this method, you need some extra "naoqi layers" library
        import system
        import translate
        
        bIsKnown = self.isKnown()
        strChristianName = ""
        strName = ""
        bGlassesStateChange = False
        
        nLimitToFirstState = 2

        nStateToSay = self.nStateToday
        nDayWithoutSeeing = self.nDayWithoutSeeing
        strNaming = "" # getNaming( speech.getSpeakLangAbbrev() );
        print( "INF: abcdk.getTextToSay: nStateToSay: %s" % str(nStateToSay ))
        print( "INF: abcdk.getTextToSay: nDayWithoutSeeing: %s" % str(nDayWithoutSeeing ))
        print( "INF: abcdk.getTextToSay: strNaming: %s" % str(strNaming ))
        try:
            strHello = translate.getSalutation( int( time.strftime( "%H", time.localtime() ) ) );
            strToSay = ""
            if( nStateToSay == 0 ):
                strToSay = strHello + " " + strNaming + ". ";                
                if( not bIsKnown ):
                    #~ if( self.bIsWoman ):
                        #~ strToSay += translate.chooseFromDictRandom( {'en': "I've never seen you in real life!", 'fr': "Oh je ne t'avais jamais vu en vrai, tu es beaucoup plus pulpeuse!/Je ne te connaissais pas personnellement, tu es charmante madeuhmoiselleselle.", 'jp': "hajimei mashite", 'ch':"renshi ni wo hen gaoxin"} );
                    #~ else:
                        #~ strToSay += translate.chooseFromDictRandom( {'en': "I've never seen you in real life!", 'fr': "Oh je ne t'avais jamais vu en vrai, tu es plus grand qu'en photo!/Je ne te connaissais pas personnellement, mais on m'a dit que tu étais cool!", 'jp': "hajimei mashite", 'ch':"renshi ni wo hen gaoxin"} );
                    strHello = "Nice to meet you, my name is %s" % (system.getNickName())
                    strToSay = strHello + " " + strChristianName + " " + strName;
                elif( nDayWithoutSeeing == 1 ):
                    strToSay += translate.chooseFromDictRandom( {'en': "Long time no see.", 'fr': "Je ne t'ai pas vu hier!/T'étais ou hier?", 'jp': "hisashiburi", 'ch':"hen jiu mei jian le" } ); # TODO: translate from french!
                elif( nDayWithoutSeeing == 2 or nDayWithoutSeeing == 3 ):
                    strToSay += translate.chooseFromDictRandom( {'en': "Long time no see.", 'fr': "T'étais en week end ?/Tu faisais quoi ces derniers temps?", 'jp': "hisashiburi", 'ch':"hen jiu mei jian le" } ); # TODO: translate from french!
                elif( nDayWithoutSeeing < 21 ):
                    strToSay += translate.chooseFromDictRandom( {'en': "Long time no see.", 'fr': "T'étais en vacances ou quoi?/Ca fait longtemps que je t'avais pas vu!", 'jp': "hisashiburi", 'ch':"hen jiu mei jian le" } ); # TODO: translate from french!
                else:
                    strToSay += translate.chooseFromDict( {'en': "Long time no see.", 'fr': "Ca fait vraiment trai longtemps que je ne t'avais pas vu!", 'jp': "hisashiburi", 'ch':"hen jiu mei jian le" } );
            elif( nStateToSay == 1 and nStateToSay < nLimitToFirstState ):
                nNumMonth = datetime.datetime.now().month # TODO: put in a tools library
                nNumDay = datetime.datetime.now().day
                if( nNumMonth == 1 and nStateToSay < nLimitToFirstState and ( timeLastSeen==None or (timeLastSeen > 60*60*24*(nNumDay-1) ) ) ): # this is so rough TODO: real computation !!!
                    print( "INF: abcdk.getTextToSay: # Happy new year! " );
                    strToSay += translate.chooseFromDictRandom( {'en': "By the way, Happy new year %s!", 'fr': "Au faite, Bonne annee %s !" } ) % strNaming;
                else:
                    strToSay += translate.chooseFromDictRandom( {'en': "How are you %s?", 'fr': "Au faite, ca va bien %s ?/Comment vas tu %s ?/Tu as bien dormi %s?" } ) % strNaming;
            elif( ( nStateToSay == 2 and nStateToSay < nLimitToFirstState ) or bGlassesStateChange ):
                if( bGlassesStateChange ):
                    if( isActualHumanWearGlasses() ):
                        strToSay += translate.chooseFromDictRandom( {'en': "Wow nice glasses %s!", 'fr': " %s, j'aime tes lunettes!/Oh, Tu as mis tes belles lunettes, %s!" } ) % strNaming;
                    else:
                        strToSay += translate.chooseFromDictRandom( {'en': "You've remove your glasses %s?", 'fr': "Tu as raison %s, faisons une pause!/Ne viens pas te plaindre que tu as mal a la taite, %s, si tu enlaives aussi souvent tes lunettes!/Oh, tu as enlevai tes lunettes, %s?" } ) % strNaming;

                elif( self.bIsWoman ):
                    strToSay += translate.chooseFromDictRandom( {'en': "How are you %s?", 'fr': " %s, tu es drolement en beauté aujourd'hui !/On dirais que tu as encore maigri %s!/Il est chouette ton petit top %s!/%s, tu as une super coiffure aujourd'hui!/%s, mh, tu sens bon!" } ) % strNaming; # TODO: translate from french!
                else:
                    strToSay += translate.chooseFromDictRandom( {'en': "How are you %s?", 'fr': "Tu t'es pas rasé %s, ce matin ?/%s, tu as fait de la muscu récemment ?/%s, j'aime ton afteur shaive!/%s, tu devrais prendre une petite douche, de temps en temps, quand même!/%s, tu as l'air bien frais ce matin!/%s, tu n'as pas l'air trai frais ce matin!" } ) % strNaming; # TODO: translate from french!
            else:
                strMemo = humanManager.getMemo(strID,strCountry);
                if( strMemo != "" ):
                    print( "INF: abcdk.getTextToSay: strMemo is: %s" % str( strMemo ) );
                    strToSay += strMemo;
                elif( time.time() - timeLastSeen > 10*60 ):
                    strToSay += translate.chooseFromDictRandom( {'en': "Hey, %s?", 'fr': "Hey, %s!/Yo %s!/Coucou %s!/%s?/Je peux t'aider %s?/Tu as l'air content %s!/Prend la vie du bon coté %s/%s: souris a la vie, et elle te sourira!/%s, si tu as un problème prend donc un mantosse!/%s, quand je te vois bouger, je me dis que les robots ne sont pas si nuls que sa!/Je suis d'accord avec toi %s!/%s, tu es un exemple pour moi." } ) % strNaming;
                # debug, repete le prénom
                self.rMinRepeatTime = 2.;
            # if( nStateToSay == 0 ) - end
        except BaseException, err:
            print( "INF: abcdk.getTextToSay: problem with some text for people '%s' nStateToSay: %s, nDayWithoutSeeing: %s; err: %s"% ( str(self.nHumanId), str(nStateToSay),str(nDayWithoutSeeing), str(err) ) );

        strToSay = str(strToSay);
            
        self.nStateToday += 1        
        return strToSay
            
    

# class Human - end










class HumanManager:
    """
    """
    def __init__( self, strSavePath = "~/" ):
        self.strSavePath = os.path.expanduser(strSavePath)
        self.reset()
        self.load()
    # __init__ - end

    def __del__( self ):
        self.save()
    # __del__ - end

    def __str__( self ):
        strOut = "Active Human: %d\n" % self.nActiveHumanId;
        for k, human in self.dictHumans.items():
            strOut += "%d: %s" %( k, str( human ) )
        return strOut;
    # __str__ - end

    def reset( self ):
        self.dictHumans = {}; # for each ID, the human associated
        self.nActiveHumanId = -1
        self.bMustSave = False
    # reset - end
    
    def load( self ):
        strSaveFileName = self.strSavePath + "humans.dat"
        self.reset()
        try:
            file = open( strSaveFileName, "rt" )
        except IOError as err:
            print( "WRN: HumanManager.load: error: %s" % str(err) )
            return False
        while True:
            bufLine = file.readline()
            if len(bufLine) < 3:
                break
            tupleData = eval(bufLine)
            id = tupleData[0]
            h = Human(id)
            h.initFromTuple( tupleData[1:] )
            self.dictHumans[id] = h
        file.close()
        return True
        
    def save( self ):   
        if not self.bMustSave:
            return
        self.bMustSave = False
        strSaveFileName = self.strSavePath + "humans.dat"
        try:
            shutil.copyfile( strSaveFileName, "/tmp/save_humans_"+str(time.time())+".bak" )
        except IOError: pass # original file not existing
        
        file = open( strSaveFileName, "wt" )
        for k,h in self.dictHumans.items():
            file.write( "%d, %s\n" % ( k,repr(h) ) )
        file.close()
        

    def getNbrHuman( self ):
        return len( self.dictHumans )
    # getNbrHuman - end
    
    def setActiveHumanIndex( self, nHumanId ):
        if nHumanId == self.nActiveHumanId:
            return
        if not nHumanId in self.dictHumans.keys() and nHumanId != -1:
            print( "INF: HumanManager.setActiveHumanIndex: creating user %d" % (nHumanId) )
            self.dictHumans[nHumanId] = Human(nHumanId)
            self.bMustSave = True
        print( "INF: HumanManager.setActiveHumanIndex: activating user %d" % (nHumanId) )
        self.nActiveHumanId = nHumanId
        if nHumanId != -1:
            self.dictHumans[nHumanId].updateSeen()
            self.save()
    
    def getActiveHumanIndex( self ):
        return self.nActiveHumanId
        
    def isActiveHuman( self ):
        return self.getActiveHumanIndex() != -1
        
    def getActiveHuman( self ):
        """
        return the human object or None if no current active human
        """
        if not self.isActiveHuman():
            return None
        return self.dictHumans[self.getActiveHumanIndex()]
        
    def updateLike(  self, strAttribute, value ):
        """
        """
        if not self.isActiveHuman():
            return False
        bModified = self.getActiveHuman().updateLike( strAttribute, value )
        self.bMustSave = bModified
        return True
        
    def getLike(  self, strAttribute ):
        """
        return None if no like or no active human
        """
        if not self.isActiveHuman():
            print( "WRN: HumanManager.getLike: no active human !!!" )
            return None
        return self.getActiveHuman().getLike( strAttribute )
        
    def getLikes( self ):
        """
        return a dictionnary of liking or {} if no known liking or None if no active human
        """
        if not self.isActiveHuman():
            print( "WRN: HumanManager.getLikes: no active human !!!" )
            return None
        return self.getActiveHuman().getLikes()
        
    def setTodayFact( self, strFactName, value ):
        if not self.isActiveHuman():
            print( "WRN: HumanManager.setTodayFact: no active human !!!" )
            return False
        
        bModified = self.getActiveHuman().setTodayFact(strFactName,value)     
        self.bMustSave = bModified
        self.save()
        return bModified
        
    def getTodayFact( self, strFactName, defaultvalue = None ):
        if not self.isActiveHuman():
            print( "WRN: HumanManager.getTodayFact: no active human !!!" )
            return defaultvalue
        return self.getActiveHuman().getTodayFact(strFactName, defaultvalue)
        
    #########################
    # Text Generation
    
    @staticmethod
    def generateTextFromLike( attribute, value ):
        strOut = ""
        if value < 0.5:
            strOut += "you don't like %s" % attribute
            if value < 0.2:
                strOut += " at all"
        else:
            strOut += "you like %s" % attribute
            if value > 0.9:
                strOut += " very much"
        return strOut
        
    @staticmethod
    def generateTextFromLikes( likes ):
        strOut = ""
        for i in range( len(likes.keys()) ):
            k = likes.keys()[i]
            v = likes[k]
            strOut += HumanManager.generateTextFromLike( k,v)
            if i < len(likes.keys())-2:
                strOut += ", "
            elif i < len(likes.keys())-1:
                strOut += " and "
        return strOut
        
    def getTextToSay( self ):
        """
        get something to say to current human.
            
        Return [txt, alternate info]
            - txt: txt to say or "" is already said or ...
        """    
        
        if not self.isActiveHuman():
            print( "WRN: HumanManager.getLikes: no active human !!!" )
            return None
        return self.getActiveHuman().getTextToSay()        
# class HumanManager - end

humanManager = HumanManager() # default singleton

def autoTest():
    hm = HumanManager( "/tmp/" )
    hm.reset() # erase previous knowledge from /tmp
    hm.setActiveHumanIndex( 1 )
    retVal = hm.updateLike( "apple", 1. )
    retVal = hm.updateLike( "spinash", 0. )
    retVal = hm.getLike( "apple" )
    assert(retVal == 1.)
        
    retVal = hm.getLikes()
    assert(retVal == {"apple": 1., "spinash": 0.} )
    
    for i in range(5):    
        retVal = hm.getTextToSay()
        print( "getTextToSay (%d): '%s'" % (i, retVal) )
    print( "\n" )
    
    hm.setActiveHumanIndex( -1 )    
    retVal = hm.getLike( "apple" )
    assert(retVal == None)
    
    
    hm.setActiveHumanIndex( 2 )
    retVal = hm.updateLike( "pear", 1. )
    print( "HumanManager: contents: \n" + str(hm) )
    hm.save()
    
    print( "HumanManager: contents: \n" + str(hm) )
    hm.reset()
    hm.load()
    print( "HumanManager: contents: \n" + str(hm) )
    hm.setActiveHumanIndex( 1 )
    retVal = hm.getLikes()
    assert_equal(retVal, {"apple": 1., "spinash": 0.} )
    
    retVal = hm.updateLike( "onions", 0.5 )
    retVal = HumanManager.generateTextFromLikes( hm.getLikes() )
    print( "generateTextFromLikes: %s" % (retVal) )
    
    # Today Facts
    hm.setActiveHumanIndex( 1 )
    retVal = hm.getTodayFact( "interact_on_food", False )
    assert_equal(retVal, False )
    
    retVal = hm.setTodayFact( "interact_on_food", True )
    assert_equal(retVal, True )
    retVal = hm.setTodayFact( "interact_on_food", True )
    assert_equal(retVal, False )    
    
    retVal = hm.getTodayFact( "interact_on_food", False )
    assert_equal(retVal, True )
    
    hm.save()
    
    hm.reset()
    hm.load() 
    hm.setActiveHumanIndex( 1 )
    print( "HumanManager: contents: \n" + str(hm) )    
    retVal = hm.getTodayFact( "interact_on_food", False )
    assert_equal(retVal, True )
    
# autoTest - end

if __name__ == "__main__":
    autoTest();


