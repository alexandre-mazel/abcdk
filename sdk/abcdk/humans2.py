# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Humans profile tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""User profile tools"""
print( "importing abcdk.humans2" );


import time
import datetime
import os
import random
import time
import json

#import Levenshtein # Levenshtein.distance: nbr of letters inserted, ratio: a number (doesn't work on my nao)

#~ import facerecognition
import filetools
import metaphone # taken from https://github.com/dracos/double-metaphone/blob/master/metaphone.py, thanks to Andrew Collins and ...
import pathtools
import pronounciation
import speech
import typetools
import translate

# TODO: add a flag: "write me!".


class Human(dict):
    """
    This class handle users knowledge about humans (name, face recognition, last seen, country origin, ...)
    user are recognised by their ID, usually "Firstname_Lastname" (or "Firstname_L"
    """

    def __init__( self, strID, strLastName = "Unknown", strChristianName = "Unknown", strCountry = "fr", dictPronounciation = {} ):
        dict.__init__(self)
        self.strID = strID;
        self.strLastName = strLastName;
        self.strChristianName = strChristianName;
        self.strCountry = strCountry;
        self.aLanguages = strCountry
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
    # __init__ - end
    
    def setIdentity( self, strLastName, strFirstName ):
        """
        add real identity afterward
        """
        self.strLastName = strLastName;
        self.strChristianName = strFirstName;

    def __getattr__(self, name):
        if name in self:
            return self[name]
        return None

    def __setattr__(self, name, value):
        self[name] = value

    def __str__( self ):
        strOut = "\n";
        strOut += "- strID: %s\n" % self.strID;
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
        return strOut;
    # __str__ - end

    def remove_accents(self, data):
        import unicodedata
        import string
        if(type(data) == str):
            data = unicode(data.encode("utf-8"))
        return ''.join(x for x in unicodedata.normalize('NFKD', data) if x in string.ascii_letters).lower()

    def getPronounciation( self, strLangAbbrev ):
        """
        Get name and firstname pronounciation for a specific language, or real name if no specific pronounciation
        return [strLastName, strChristianName]
        """
        try:
            return pronounciation.instance.get(
                    [self.strLastName, self.strChristianName],
                    strLangAbbrev)
        except BaseException, err:
            print( "DBG: Human.getPronounciation: err is %s (should just means there's no specific pronunciation for this lang: '%s')" % ( err, strLangAbbrev ) );
        return [self.strLastName, self.strChristianName];
    # getPronounciation - end

    def getNaming( self, strLangAbbrev = "en" ):
        """
        Return for a specific lang the way to call someone (related to intimacy or country).
        for the moment, french people are  nammed by their firstname, jp with a san
        """
        strOut = "";
        listToPronounce = self.getPronounciation( strLangAbbrev );
        if( self.strCountry == "fr" or self.nCptTimeSeen > 2 ):
            strOut += listToPronounce[1];
        elif( self.strCountry == "jp" ):
            strOut += listToPronounce[0] + "san";
        else:
            strOut += listToPronounce[1] + " " + listToPronounce[0];
        return strOut;
    # getNaming - end

    def _getSomethingToSayState( self ):
        """
        Compute something to say to human related to the knowledge on this people
        Return: an array [state, extra info], with:
            state: 0: hello, 1: how are you, 2: say something silly, 3: ignore
            extra info: number of day without seeing him, or none if never seen
        """
        nStateToday = self.nStateToday;
        self.nStateToday += 1;
        return [nStateToday,self.nDayWithoutSeeing];
    # _getSomethingToSayState - end

# class Human - end

class HumanManager:
    DataUrl = "http://studio.aldebaran-robotics.com/humans/humans.json?reload_bugging_proxy_AR_random=27"
    """
    This class handling human knowledge, it will merge absolute data from the web
    and local knowledge related to the robot where it is running.
    """
    def __init__( self ):
        self.reset();
    # __init__ - end

    def __del__( self ):
        self.saveInfoFromLocal();
    # __del__ - end

    def __str__( self ):
        strOut = "";
        for human in self.dictHumans:
            strOut += str( human );
        return strOut;
    # __str__ - end

    def reset( self ):
        self.dictHumans = {}; # for each ID, the human associated
    # reset - end

    def getNbrHuman( self ):
        return len( self.dictHumans );
    # getNbrHuman - end


    def addInfoFromLocal( self, strFilename = pathtools.getCachePath() + "human_local.txt" ):
        """
        Add local to NAO information. Data format:
        {
            0: [last_seen_time, nCptTimeSeen, nDayWithoutSeeing, nStateToday,memos],
            1: [last_seen_time, ...],
            ...
        }
        """
        print( "INF: HumanManager.addInfoFromLocal - begin - read is from '%s'" % strFilename );
        data = filetools.getFileContents( strFilename );
        if( len(data) < 2 ):
            print( "INF: HumanManager.addInfoFromLocal - end (no data)" );
            return 0;
        dictRead = eval( data );
        for k,v in dictRead.iteritems():
            if( k not in self.dictHumans.keys() ):
                print( "ERR: HumanManager.addInfoFromLocal: human with ID: %d is unknown in the global base!" % k );
            else:
                    self.dictHumans[k].timeLastSeen = v[0];
                    if( len(v) > 1 ): # handle old save case
                        self.dictHumans[k].nCptTimeSeen = v[1];
                    if( len(v) > 2 ): # handle old save case
                        self.dictHumans[k].nDayWithoutSeeing = v[2];
                    if( len(v) > 3 ): # handle old save case
                        self.dictHumans[k].nStateToday = v[3];
                    if( len(v) > 4 ):
                        self.dictHumans[k].aMemoInfo = v[4];
                    if( len(v) > 5 ):
                        self.dictHumans[k].nCptSeenWithGlasses = v[5];
                    if( len(v) > 6 ):
                        self.dictHumans[k].bLastSeenWithGlasses = v[6];                        
                    if( len(v) > 7 ):
                        self.dictHumans[k].timeLastSeenWithGlasses = v[7];
        # for - end
        print( "INF: HumanManager.addInfoFromLocal: %d human(s) local info read" % len(dictRead) );
        print( "INF: HumanManager.addInfoFromLocal - end" );
    # addInfoFromLocal - end

    def saveInfoFromLocal( self, strFilename = pathtools.getCachePath() + "human_local.txt" ):
        """
        Save local Info. Data format: (see addInfoFromLocal)
        Return True if ok
        """
        print( "INF: HumanManager.saveInfoFromLocal - begin" );
        # construct dictionnary to save
        localDict = {};
        if( len( self.dictHumans ) < 2 ):
            print( "INF: HumanManager.saveInfoFromLocal - end (not enough human)" );
            return True;
        for k,v in self.dictHumans.iteritems():
            if( v.timeLastSeen != None or v.aMemoInfo != None ):
                localDict[k] = [v.timeLastSeen,v.nCptTimeSeen,v.nDayWithoutSeeing,v.nStateToday, v.aMemoInfo, v.nCptSeenWithGlasses, v.bLastSeenWithGlasses, v.timeLastSeenWithGlasses];
        # end - for
        file = open( strFilename, "wt" );
        file.write( str( localDict ) );
        file.close();
        print( "INF: HumanManager.saveInfoFromLocal: %d human(s) local info saved" % len(localDict) );
        print( "INF: HumanManager.saveInfoFromLocal - end" );
        return True;
    # addInfoFromLocal - end
    
    def enforceHumanExists( self, strID ):
        """
        create a new human on the fly, or do nothing if he already exists
        strID is "firstname_lastname"
        """
        print( "INF: enforceHumanExists: receiving: '%s'" % strID )
        
        if strID in self.dictHumans.keys():
            return
                
        strChristianName, strName = strID.split("_")
        print( "WRN: HumanManager.enforceHumanExists(%s) => creating a new human on the fly (name: %s, surname: %s)" % (strID,strName, strChristianName) );
        self.dictHumans[strID] = Human(strID)
        self.dictHumans[strID].strLastName = strName
        self.dictHumans[strID].strChristianName =  strChristianName
    # enforceHumanExists - end

    def getHumanInfo( self, strID ):
        """
        get information about a specific human
        return information in the same order than in the Human Class or None if unknown
        """
        try:
            return self.dictHumans[strID]
        except KeyError, err:
            print( "WRN: HumanManager.getHumanInfo(%s): key err: %s" % ( str(strID), err ) );
            #~ self.enforceHumanExists(strID)
            #~ return self.dictHumans[strID]
        return None;
    # getHumanInfo - end
    
    def getNameAndFirstName(self, strID):
        info = self.getHumanInfo(strID)
        return info.strLastName,info.strChristianName


    def find( self, strName = "", strChristianName = "", bApproximate = False ):
        """
        find a human in the list.
        return the index or -1 if not found
        """
        if( bApproximate ):
            dmName = metaphone.dm(unicode(strName));
            dmChristianName = metaphone.dm(unicode(strChristianName));
        for k,v in self.dictHumans.iteritems():
            if( not bApproximate ):
                if ( v.strLastName == strName or strName == "" ) and ( v.strChristianName == strChristianName or strChristianName == "" ):
                    return k;
            else:
                #~ rDist = 0;
                #~ if( strName != "" ):
                    #~ rDist += Levenshtein.ratio( v.strLastName, strName );
                #~ if( strChristianName != "" ):
                    #~ rDist += Levenshtein.ratio( v.strChristianName, strChristianName );
                #~ print( "rDist between %s,%s and %s,%s: %f " % ( strName, strChristianName, v.strLastName, v.strChristianName, rDist ) );
                #~ if( rDist > 0.9 ):
                    #~ return i;
                if ( metaphone.dm(unicode(v.strLastName)) ==  dmName or strName == "" ) and ( metaphone.dm(unicode(v.strChristianName)) ==  dmChristianName or strChristianName == "" ):
                    return k;

        return -1;
    # find - end

    def setLangAndGetInfo( self, strID, bDontSwitchLang = False ):
        """
        switch to the nearest language related to human (even if human unknown)
        """
        print( "INF: HumanManager.setLangAndGetInfo: param: %s" % str( strID ) );
        # default settings
        bIsKnown = False;
        strCountry = "fr";
        timeLastSeen = None;
        nCptTimeSeen = 0;

        #~ try:
        if 1:
            strName, strChristianName = self.getNameAndFirstName(strID)            

            humanInfo = self.getHumanInfo( strID );
            try:
                print( "INF: HumanManager.setLangAndGetInfo: humanInfo: %s" % str( humanInfo ) );
            except BaseException, err:
                print( "ERR: HumanManager.setLangAndGetInfo: strID: %s =>, err: %s" % (str( strID ),str(err)) );
                
            if( humanInfo != None ):
                bIsKnown = True;
                strCountry = humanInfo.strCountry;
                pronounce = humanInfo.getPronounciation( strCountry );
                timeLastSeen = humanInfo.timeLastSeen;
                nCptTimeSeen = humanInfo.nCptTimeSeen;
            else:
                pronounce = [strName,strChristianName];

            nLang = speech.fromLangAbbrev( strCountry );
            print( "INF: HumanManager.setLangAndGetInfo: Lang to use is %d" % nLang );
            if( not bDontSwitchLang ):
                if( speech.isLangPresent( nLang ) ):
                    print( "INF: HumanManager.setLangAndGetInfo: Switching to lang %s" % strCountry );
                    if( speech.getSpeakLanguage() != nLang ):
                        speech.setSpeakLanguage( nLang );
                else:
                    strCountry = "en";
                    nLang = speech.fromLangAbbrev( strCountry );
                    print( "Switching to default lang %s" % strCountry );
                    speech.setSpeakLanguage( nLang );
            pronounce = humanInfo.getPronounciation( strCountry );

            return [bIsKnown, pronounce[0], pronounce[1], strCountry, timeLastSeen, nCptTimeSeen];
        #~ except BaseException, err:
                #~ print( "ERR: HumanManager.setLangAndGetInfo (2): strID: %s =>, err: %s" % (str( strID ),str(err)) );
                
        return [False, "error", "error", "fr", None, 0];
    # setLangAndGetInfo - end

    def setSeenHuman( self, strID, bWasWearingGlasses = False ):
        """
        Update info about this human
        return True if ok
        """
        try:
            if( self.dictHumans[strID].timeLastSeen == None or time.time() - self.dictHumans[strID].timeLastSeen > 5*60 ): # pas vu depuis plus de 5 minutes !
                self.dictHumans[strID].nCptTimeSeen += 1;

            if( self.dictHumans[strID].timeLastSeen != None ):
                nDeltaDay = datetime.timedelta( seconds = (time.time()- self.dictHumans[strID].timeLastSeen) ).days;
                print( "INF: HumanManager.setSeenHuman: nDeltaDay: %d" % nDeltaDay );
                if( nDeltaDay > 0 ):
                    self.dictHumans[strID].nDayWithoutSeeing = nDeltaDay;
                    self.dictHumans[strID].nStateToday = 0;
            self.dictHumans[strID].timeLastSeen = time.time();
            if( bWasWearingGlasses ):
                self.dictHumans[strID].nCptSeenWithGlasses += 1;
                self.dictHumans[strID].timeLastSeenWithGlasses = time.time();
            self.dictHumans[strID].bLastSeenWithGlasses = bWasWearingGlasses;
                
            return True;
        except BaseException, err:
            print( "WRN: HumanManager.setSeenHuman(%s): err: %s" % ( strID, err ) );
        return False;
    # setSeenHuman - end
    
    def resetSeenHuman( self, strID ):
        """
        Forget this human!
        strID: see setLangAndGetInfo
        return True if ok
        """
        try:
            print( "INF: HumanManager.resetSeenHuman(%s)!" % strID );
            self.dictHumans[strID].timeLastSeen = None;
            self.dictHumans[strID].nCptTimeSeen = 0;
            self.dictHumans[strID].nDayWithoutSeeing = None;
            self.dictHumans[strID].nStateToday = 0;
            self.dictHumans[strID].nCptSeenWithGlasses = 0;
            self.dictHumans[strID].bWasWearingGlasses = False;            
            self.dictHumans[strID].timeLastSeenWithGlasses = None;
            return True;
        except BaseException, err:
            print( "WRN: HumanManager.resetSeenHuman(%d): err: %s" % ( strID, err ) );
        return False;            
    # resetSeenHuman - end
    
    def getMemo( self, strID, strLangAbbrev = None ):
        """
        return a memo to tell to this human, "" if none
        """
        nHumanID = strID
        infos = self.dictHumans[nHumanID].aMemoInfo;
        if( infos ==None or len(infos) < 1 ):
            return "";
        info = infos.pop();
        try:
            self.dictHumans[info[0]]
        except KeyError, err:
            print( "WRN: HumanManager.getMemo(%s): key err: %s" % ( str(info[0]), err ) );
            self.enforceHumanExists( info[0] )
        
        strName = self.dictHumans[info[0]].getNaming(strLangAbbrev); # self.dictHumans[nHumanID].strCountry
        bIsWoman = self.dictHumans[info[0]].bIsWoman;
        strMessage = info[2];
        #~ moment = datetime.datetime.now() - datetime.timedelta( seconds = time.time() - info[1] );
        #~ strDate = moment.strftime( '%Y/%m/%d' );
        #~ strHour = moment.strftime( '%H:%M:%S' );
        #~ strMoment = speech.transcriptDateTime( strDate, strHour, bSmart = True );
        strMoment = speech.transcriptDuration(  time.time() - info[1], bSmart = True, nSmartLevel = 1 );
        nVct = 90;
        if( not bIsWoman ):
            nVct -= 12; # speak manly
        aSentence = { 'en': "by the way %s, %s ago, %s told me to say to you: \\RSPD=85\\ \\VCT=%d\\ %s", 'fr':"au faite %s, il y a %s, %s m'a dit de te dire: \\RSPD=85\\ \\VCT=%d\\ %s" };
        try:
            strTxt = aSentence[strLangAbbrev] + " \\VCT=100\\ ";
        except BaseException, err:
            print( "WRN: HumanManager.getMemo(): while acceding aSentence: err: %s" % str(err) );
            strTxt = aSentence["en"];
        strMe = self.dictHumans[nHumanID].getPronounciation(strLangAbbrev)[1];
        return  strTxt % (strMe, strMoment, strName, nVct, strMessage );
    # getMemo - end

    def addMemo( self, nTargetID,  nCreatorID,  strMessage ):
        nDate = time.time();
        if( self.dictHumans[nTargetID].aMemoInfo == None ):
            self.dictHumans[nTargetID].aMemoInfo = [];
        self.dictHumans[nTargetID].aMemoInfo.append( [nCreatorID, nDate, strMessage] );
    # addMemo - end

    def getAllPossibleNameForReco( self, strLangAbbrev = None ):
        """
        return all name/christian name and all combinations possible
        """
        bAddToName = True; # add conjonction "a Alexandre";
        try:
            strToName = { 'fr': "a", 'en': "to" }[strLangAbbrev];
        except BaseException, err:
            strToName = "to";
        strAllPossibleCombi = "";
        for k,v in self.dictHumans.iteritems():
            strAllPossibleCombi += "%s;%s;" % ( v.strLastName, v.strChristianName );
            strAllPossibleCombi += "%s %s;" % ( v.strLastName, v.strChristianName );
            strAllPossibleCombi += "%s %s;" % ( v.strChristianName, v.strLastName );
            if( bAddToName ):
                strAllPossibleCombi += "%s %s;%s;" % ( strToName, v.strLastName, v.strChristianName );
                strAllPossibleCombi += "%s %s %s;" % ( strToName, v.strLastName, v.strChristianName );
                strAllPossibleCombi += "%s %s %s;" % ( strToName, v.strChristianName, v.strLastName );
        return strAllPossibleCombi.encode("utf-8")
    # getAllPossibleNameForReco - end

# class HumanManager - end

global_variantLastInteractingHuman = None;
def setLastInteractingHuman( variantLastInteractingPeople ):
    global global_variantLastInteractingHuman;
    global_variantLastInteractingHuman = variantLastInteractingPeople;    
# setLastInteractingHuman - end

def getLastInteractingHuman():
    global global_variantLastInteractingHuman;
    return global_variantLastInteractingHuman
# getLastInteractingHuman - end

global_isWearingGlasses = False;
def setActualHumanWearGlasses( bValue ):
    global global_isWearingGlasses;
    print( "INF: abcdk.humans.setActualHumanWearGlasses: %s => %s" % (global_isWearingGlasses,bValue) );
    global_isWearingGlasses = bValue;

def isActualHumanWearGlasses():
    global global_isWearingGlasses;
    print( "INF: abcdk.humans.isActualHumanWearGlasses: returning %s" % (global_isWearingGlasses) );
    return global_isWearingGlasses;

#
# global loading and init of the module
#
humanManager = HumanManager();
if( 0 ): # 13-11-15 Alma: commenting those autoloading as it takes time when generating documentation...  (because there's a bug (at least on windows))
    humanManager.getInfoFromWeb();
    humanManager.addInfoFromLocal();


class Likes():
    """
    store what humans likes.
    - temporary: to be made more clean on of those days
    """
    def __init__(self):
        self.aDict = {} # for each human, an array of he likes
        self.read();
        
    def __del__(self):
        self.write();
        
    def read(self):
        """
        Return true if read ok, else does nothing (and return false)
        """
        try:
            file = open( pathtools.getCachePath() + "human_likes.txt", "rt" );
            buf = file.read();
            self.aDict = eval(buf);
            file.close();
        except BaseException, err:
            print( "WRN: humans.Likes.read, err: %s" % err );
            self.aDict = {};
            return False
        return True;
        
    def write( self ):
        """
        Return true if write ok
        """
        try:
            file = open( pathtools.getCachePath() + "human_likes.txt", "wt" );
            buf = file.write(str(self.aDict));
            file.close();
        except BaseException, err:
            print( "WRN: humans.Likes.write, err: %s" % err );
            return False
        return True;
        
    def get( self, strName, default = [] ):
        """
        return [L1,L2,L3]: a list of likes of a human
        """
        try:
            val = self.aDict[strName];
            print( "INF: humans.Likes.get: retrieve '%s' for '%s'" % (val,strName) );
            return val;            
        except BaseException, err:
            print( "WRN: humans.Likes.get, err: %s" % err );
        return default;
        
    def getAsString( self, strName, default = "" ):
        """
        return same as get, but as a string
        """
        
        aTxt = self.get( strName );
        if( aTxt == "" ):
            return aTxt;
        strTxt = "";
        for i in range(len(aTxt)):
            strTxt += aTxt[i];
            if( i == len(aTxt)-2 ):
                strTxt += " et "; #  TODO: localise
            elif( i != len(aTxt)-1 ):
                strTxt += ", ";
        return strTxt;
        
    def store( self, strName, strLike ):
        """
        store a new likes for a human
        return True if ok
        """
        print( "INF: humans.Likes.store: storing '%s' for '%s'" % (strLike,strName) );
        try:
            self.aDict[strName] = self.get( strName, [] );
            self.aDict[strName].append( strLike );
            return True;
        except BaseException, err:
            print( "WRN: humans.Likes.store, err: %s" % err );
        return False;
        
# class Likes - end

def autoTest_likes():
    l = Likes();
    aThing = l.get( "Alexandre", "les pierres" );
    print( "aThing: %s" % aThing );
# autoTest_likes - end
#~ autoTest_likes();
#~ exit();

likes = Likes();

    
    
def enforceHumanExists( strID ):
    global humanManager
    return humanManager.enforceHumanExists(strID)

def getTextToSay( strID, nLimitToFirstState = 100, bDontSwitchLang = False, bOutputAtLeastFirstName = False ):
    """
    get something to say to someone.
        - nLimitToFirstState: limit txt to say to this state, eg if nLimitToFirstState == 2, we'll just say (0) hello and (1)how are you
        - bOutputAtLeastFirstName: when nothing to say, just say the firstname
        
        
    Return [txt, alternate info]
        - txt: txt to say or "" is already said or ...
    """    
    setLastInteractingHuman( strID ); # NEW: we done it automatically directly from this method
    
    info = humanManager.setLangAndGetInfo( strID, bDontSwitchLang = bDontSwitchLang );
    print( "INF: abcdk.getTextToSay: setLangAndGetInfo return: %s" % str( info ) );
    bIsKnown, strName, strChristianName, strCountry, timeLastSeen, nCptTimeSeen = info;

    # We make the test before updating datas!
    humanInfo = humanManager.getHumanInfo( strID )
    bGlassesStateChange = humanInfo != None and (isActualHumanWearGlasses() != humanInfo.bLastSeenWithGlasses)
    humanManager.setSeenHuman( strID, isActualHumanWearGlasses() );

    strToSay = "";

    if( not bIsKnown ):
        strHello = translate.getSalutation( int( time.strftime( "%H", time.localtime() ) ) );
        strToSay = strHello + " " + strChristianName + " " + strName;
    else:
        nStateToSay, nDayWithout = humanManager.getHumanInfo( strID )._getSomethingToSayState();
        strNaming = humanManager.getHumanInfo( strID ).getNaming( speech.getSpeakLangAbbrev() );
        print( "INF: abcdk.getTextToSay: nStateToSay: %s" % str(nStateToSay ))
        print( "INF: abcdk.getTextToSay: nDayWithout: %s" % str(nDayWithout ))
        print( "INF: abcdk.getTextToSay: strNaming: %s" % str(strNaming ))
        try:
            if( nStateToSay == 0 ):
                strHello = translate.getSalutation( int( time.strftime( "%H", time.localtime() ) ) );
                strToSay = strHello + " " + strNaming + ". ";

                if( nDayWithout == None ):
                    if( humanManager.getHumanInfo( strID ).bIsWoman ):
                        strToSay += translate.chooseFromDictRandom( {'en': "I've never seen you in real life!", 'fr': "Oh je ne t'avais jamais vu en vrai, tu es beaucoup plus pulpeuse!/Je ne te connaissais pas personnellement, tu es charmante madeuhmoiselleselle.", 'jp': "hajimei mashite", 'ch':"renshi ni wo hen gaoxin"} );
                    else:
                        strToSay += translate.chooseFromDictRandom( {'en': "I've never seen you in real life!", 'fr': "Oh je ne t'avais jamais vu en vrai, tu es plus grand qu'en photo!/Je ne te connaissais pas personnellement, mais on m'a dit que tu étais cool!", 'jp': "hajimei mashite", 'ch':"renshi ni wo hen gaoxin"} );
                elif( nDayWithout == 1 ):
                    strToSay += translate.chooseFromDictRandom( {'en': "Long time no see.", 'fr': "Je ne t'ai pas vu hier!/T'étais ou hier?", 'jp': "hisashiburi", 'ch':"hen jiu mei jian le" } ); # TODO: translate from french!
                elif( nDayWithout == 2 or nDayWithout == 3 ):
                    strToSay += translate.chooseFromDictRandom( {'en': "Long time no see.", 'fr': "T'étais en week end ?/Tu faisais quoi ces derniers temps?", 'jp': "hisashiburi", 'ch':"hen jiu mei jian le" } ); # TODO: translate from french!
                elif( nDayWithout < 21 ):
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

                elif( humanManager.getHumanInfo( strID ).bIsWoman ):
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
            print( "INF: abcdk.getTextToSay: problem with some text for people '%s' nStateToSay: %s, nDayWithout: %s; err: %s"% ( str(strID), str(nStateToSay),str(nDayWithout), str(err) ) );

    strToSay = str(strToSay);
    
    if( bOutputAtLeastFirstName ):
        if( strToSay == "" ):
            strToSay = str( strNaming );
        
    return [strToSay,0];
# getTextToSay - end

global_TextToSayToUnknown_nLastAge = -10.;
global_TextToSayToUnknown_rLastGender = -10.;
global_TextToSayToUnknown_lastTime = time.time()-1000;

def getTextToSayToUnknown( analysedInfo, bShortMessage = False ):
    """
    Compute a text to say to an unknown people
    - humanInfo: information from the tracker Tracking/FaceRecognised
    - bShortMessage: output only a short message hello mister / hello madam.
    Return [strTxt, bSeemsSame]:
        - strTxt: txt to say
        - bSeemsSame: set to true if it's the same human than recently
        
    """
    nAge = int(analysedInfo[2]+0.5);
    rGender = analysedInfo[3];
    
    global global_TextToSayToUnknown_nLastAge
    global global_TextToSayToUnknown_rLastGender    
    global global_TextToSayToUnknown_lastTime
    bSeemsSame = False;
    if( (time.time() - global_TextToSayToUnknown_lastTime) < 60*3 and abs( nAge - global_TextToSayToUnknown_nLastAge ) < 8 and abs( global_TextToSayToUnknown_rLastGender - rGender ) < 0.2 ):
        bSeemsSame = True;
    else:
        global_TextToSayToUnknown_nLastAge = nAge;
        global_TextToSayToUnknown_rLastGender = rGender;
        global_TextToSayToUnknown_lastTime = time.time();
    
    strOut = translate.getTitle(nAge,rGender);
    
    nSpeed = 90;
    if( nAge < 6 or nAge > 50 ):
        nSpeed = 80;
    if( nAge > 65 ):
        nSpeed = 70;

        
    #~ strLeLa = "le";
    #~ if( rGender < 0. ):
        #~ strLeLa = "la";

    #~ listTxtVous = {
        #~ "fr": "Je pense que vous avez %d ans./vous avez %d ans./Heumme, Je vous donnerais %d ans./A mon avis vous avez %d ans./ohoho, \\PAU=500\\ euh, c'est difficile, \\PAU=600\\ Je dirais %d ans.",
        #~ "en": "I think you are %d years old.",
        #~ };
    #~ listTxtTu = {
        #~ "fr": "Je crois que tu as %d ans./Tu as %d ans./Tu n'aurais pas autour de %d ans, par hasard?",
        #~ "en": "May I suggest youare %d years old?",
        #~ };
    #~ if( nAge < 20 ):
        #~ strAgePhrase = translate.chooseFromDictRandom( listTxtTu );
    #~ else:
        #~ strAgePhrase = translate.chooseFromDictRandom( listTxtVous );
        
    astrPolite = {
        "fr": "Je suis content de vous rencontrer/Enchanté/Je suis fier de vous rencontrer/Je suis content de vous voir",
        "en": "Nice to meet you/Pleased to meet you/I'm glad you're here/Happy to meet you"
        };
        
    astrPoliteTu = {
        "fr": "Je suis content de te rencontrer/Je suis fier de te rencontrer/Je suis content de te voir",
        };
        
    astrPoliteYoung = {
        "fr": "C'est cool que tu sois la/C'est trop chouette de te rencontrer enfin/Trop Trop la classe que tu sois la!",
        "en": "Too cool, you're here/Nice to see you/Yo, what's up?",
        };        
        
    if( nAge < 13 ):
        astrPolite["fr"] = astrPoliteTu["fr"];
        
    if( nAge > 12 and nAge < 18 ):
        # teenagers
        nSpeed = 110;   
        astrPolite = astrPoliteYoung;
        
        
    strOut = ( "\\RSPD=%d\\ " % nSpeed ) + translate.getSalutation() + " " + strOut
    if( not bShortMessage ):
        strOut += ", " + translate.chooseFromDictRandom(astrPolite) + "."
    outValue = [strOut,bSeemsSame]
    print( "INF: abcdk.humans.getTextToSayToUnknown(%s,%s)=>%s" % ( nAge,rGender,outValue ) );
    return outValue;
# getTextToSayToUnknown - end    
        
        

def autoTest():
    # strPath = r"D:\Dev\git\appu_applications\facevacs\learned";
    #~ strPath = "/home/likewise-open/ALDEBARAN/amazel/dev/git/appu_applications/facevacs/learned";
    #~ humanManager._parseLearnedDirectoryAndGeneratedTextList(strPath);
    print( "humanManager.getNbrHuman: %s" % humanManager.getNbrHuman() )
    strID = "alexandre_m"
    humanManager.enforceHumanExists( strID )
    print( "humanManager.getNbrHuman: %s" % humanManager.getNbrHuman() )

    print( humanManager.getHumanInfo( strID ) );
    humanManager.getHumanInfo( strID ).setIdentity( "Mazel", "Alexandre" )
    humanManager.setSeenHuman( strID );
    print( "human naming: " + humanManager.getHumanInfo( strID ).getNaming("fr") );
    print( "human pronouncing: " + str( humanManager.getHumanInfo( strID ).getPronounciation("fr") ) );
    print( "human things to say state: " + str( humanManager.getHumanInfo( strID )._getSomethingToSayState() ) );
    print( "*** human things to say text 1: " + str( getTextToSay(strID) ) );
    print( "*** human things to say text 2: " + str( getTextToSay(strID) ) );
    print( "*** human things to say text 3: " + str( getTextToSay(strID) ) );
    print( "*** human things to say text 4: " + str( getTextToSay(strID) ) );
    
    

    if 1:
        # memo testing
        strID2 = "Rodolphe_g"
        humanManager.enforceHumanExists( strID2 )
        humanManager.addMemo( strID2, strID, "Coucou Rodolphe!" );
        ret = humanManager.getMemo(strID2);
        print( "current memo 1: %s" % ret );
        assert( ret != "" );
        ret = humanManager.getMemo(strID2);
        print( "current memo 2: %s" % ret );
        assert( ret == "" ); # this could be wrong if some older test doesn't finished or this human have already others memo

    if 1:
        # metaphone lookup
        strFindId = humanManager.find( "masele", bApproximate = True );
        print( "find id 1: %s" % strFindId );
        assert( strFindId != None )
        assert( humanManager.getHumanInfo( strFindId ).strLastName.lower() == "mazel" );
        if( strFindId != -1 ):
            print( humanManager.getHumanInfo( strFindId ) );
        strFindId = humanManager.find( strChristianName = "alexandre", bApproximate = True );
        print( "find id 2: %s" % strFindId );
        assert( humanManager.getHumanInfo( strFindId ).strChristianName == "Alexandre" );
        if( strFindId != -1 ):
            print( humanManager.getHumanInfo( strFindId ) );

    print( humanManager.getAllPossibleNameForReco() );
    assert( len(humanManager.getAllPossibleNameForReco().split(";")) == humanManager.getNbrHuman()*8+1 ); # +1 because of the last  char finished by a ';' so it creates an empty last element

    if 0:
        # test pronunciation
        h = humanManager.getHumanInfo( 12 )
        print h.getPronounciation("fr")
        assert( h.getPronounciation("fr")[1] == "yo-ko" );

        h = humanManager.getHumanInfo( 70 )
        print "fir name : ", h.getFIRName()

# autoTest - end

if __name__ == "__main__":
    autoTest();

