# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit - server side
# knowledge engine (no need for web access)
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""
knowledge
When deploying you need to launch that command:

cd /var/www/knowledge

rm data_fr/*
rm data_en/*


mkdir -p data_fr
echo >data_fr/knowledge.log
echo >data_fr/knowledge.dat
echo >data_fr/lock
mkdir -p data_en
echo >data_en/knowledge.log
echo >data_en/knowledge.dat
echo >data_en/lock
chown -R amazel:www-data *
chmod -R 770 *
cat data_fr/knowledge.log


"""


print( "importing web.knowledge" );

import metaphone
try: import httptools
except: pass # no web acces

import datetime
import os
import mutex
try: import stringtools # for levenshtein
except: pass
import random
import time

def thismodulecurrentdir():
    try:
        strLocalPath = os.path.dirname( __file__ ); # when launched from another module
        if( strLocalPath == "" ):
            strLocalPath = ".";
    except:
        strLocalPath = ".";
    print( "thismodulecurrentdir: '%s'" % strLocalPath );
    return strLocalPath + os.sep; # when launched from local

class KnowledgeEngine:
    """
    A class to store the knowledge about... ... everything
    """
    
    def __init__( self, dataPath ):
        """
        dataPath: path to store data!
        """
        self.nID = int(time.time()*100)%10000; # a specific value to help understanding multithreading and many problems
        self.lock = None;
        self.bMultiProcess = True; # does we have multiple process, and so multiple object at the same time ?
        self.mutex = mutex.mutex();
        self.modulePath = thismodulecurrentdir();
        self.dataPath = self.modulePath + dataPath + os.sep;
        try:
            os.makedirs( self.dataPath );
        except BaseException, err:
            #~ print( "DBG: should be a normal error: %s" % str( err ) );
            pass        
        self.log( "\n" ); # clear the output!
        self.log( "INF: module path: '%s'" % self.modulePath );
        self.log( "INF: using data from '%s'" % self.dataPath );
        self.strDefaultFilename = "knowledge.dat";        
        self.data = {}; # for each question, a list of possible answer (a dictionnary {"answer" => [confidence, [list of nao thar ear that answers]] })
        self.bModified = False;
        self.load();
        self.nCptSave = 0; # count nbr of learn, then make a small backup save
    # __init__ - end
    
    def __del__( self ):
        self.log( "DBG: destroying Knowledge object!" );
        self.save();
        
    def __str__( self ):
        while( self.mutex.testandset() == False ):
            self.log( "INF: knowledge.__str__: locked..." );
            time.sleep( 0.1 );        
        strOut = "ID: %04d\n" % self.nID;
        strOut += "Nbr records: %d\n" % len( self.data );
        nCpt = 0;
        for k,v in self.data.iteritems():
            nCpt += 1;
            strOut += "%d: '%s':\n" % (nCpt, k);
            for k2,v2 in v.iteritems():
                strOut += "  '%s': %5.2f - %s\n" % ( k2, v2[0], v2[1] );
        self.mutex.unlock();
        return strOut;
    # __str__ - end
    
    def lockSession( self, bLock ):
        """
        It seems like it could be exists many object in the world in parallel.
        It's a mutex global for different process
        Trying to lock them thru a file !
        bLock: lock or unlock ?
        mutexed from local concurrency access from outwhere.
        
        The idea is: each time you wan't to modify the database, you need to create a new session of load/modify/save
        """
        if( not self.bMultiProcess ):
            return;
        if( bLock ):
            if( self.lock == None ):
                self.log( "INF: Locking disk access" );
                while( True ):
                    try:
                        self.lock = open( self.dataPath + "lock", "wb" );
                        break;
                    except BaseException, err:
                        self.log( "INF: locked... (should be normal err: %s)" % str( err ) );
                        time.sleep( 0.1 );
        else:
            if( self.lock == None ):
                self.log( "ERR: Unlocking without locking is weird !" );
            else:
                self.log( "INF: Unlocking disk access" );
                self.lock.close();
                self.lock = None;
    # lockSession - end
            
    def log( self, strMessage ):
        #~ strLogPath = self.modulePath + "logs" + "/"; # don't use os.sep, because os seems to be already unloaded when called from __del__
        file = open( self.dataPath + "knowledge.log", "at" ); # NB: on the server you need to create it manually first and give him owner right amazel:www-data
        strMsg =  "%04d: %s: %s" % ( self.nID, time.time(), strMessage );
        print( "LOG: %s" % strMsg );
        file.write( strMsg + "\n" );
        file.close();
        
    def _load( self ):
        try:
            file = open( self.dataPath + self.strDefaultFilename, "rt" );
            buf = file.read();
            file.close();
            self.bModified = False;
            if( len( buf ) > 2 ):
                self.data = eval( buf );
            else:
                self.data = {};
        except BaseException, err:
            self.log( "INF: knowledge.load: while loading: %s" % str( err ) );
            return False;
        self.log( "INF: knowledge: %d records loaded" % len( self.data.keys() ) );
        return True;
    # _load - end        
        
    def load( self ):
        while( self.mutex.testandset() == False ):
            self.log( "INF: knowledge.load: locked..." );
            time.sleep( 0.1 );     
        bRet = self._load();
        self.mutex.unlock();
        return bRet;
    # load - end

    def _force_reload( self ):
        """
        Because some other people could have updated the file on disk (not optimal to do that at every time, but...)
        """
        # TODO: we could check if datetime of the file on disk have really changed...
        if( True ):
            self._save();
            self._load();
    # force_reload - end
    
    def force_reload( self ):
        """
        Because some other people could have updated the file on disk (not optimal to do that at every time, but...)
        """
        while( self.mutex.testandset() == False ):
            self.log( "INF: knowledge.force_reload: locked..." );
            time.sleep( 0.1 );
            
        self.lockSession(True);
        
        self._force_reload();
       
        self.lockSession(False);
        self.mutex.unlock();
    # force_reload - end    
    
    def _save( self ):
        if( not self.bModified ):
            return False;
                
        try:
            os.makedirs( self.dataPath );
        except BaseException, err:
            #~ print( "DBG: should be a normal error: %s" % str(err) );
            pass
        file = open( self.dataPath + self.strDefaultFilename, "wt" );
        file.write( str( self.data ) );
        file.close();
        self.bModified = False;
        self.log( "INF: _save: wroten %d records" % len( self.data.keys() ) );
        if( True ):
            # make periodic backup
            self.nCptSave += 1;
            if( self.nCptSave > 50 ):
                strTimeStamp = datetime.datetime.now().strftime( "%Y_%m_%d-%Hh%Mm%Ss%fms" );
                strTimeStamp = strTimeStamp.replace( "000ms", "ms" ); # because there's no flags for milliseconds                
                self.log( "INF: _save: making a small backup. '%s'" % strTimeStamp );
                self.nCptSave = 0;                
                file = open( self.dataPath + self.strDefaultFilename + strTimeStamp, "wt" ); # I bet it won't work, because python hasn't rights to create file !!!
                file.write( str( self.data ) );
                file.close();                    
        return True;
    # _save - end
        
    def save( self ):
        """
        Save the modified database
        Return True if the base has really been saved!
        """
        while( self.mutex.testandset() == False ):
            self.log( "INF: knowledge.save: locked..." );
            time.sleep( 0.1 );
            
        bRet = self._save();
        self.mutex.unlock();
        return bRet;
    # save - end
    
    def formatQuery( self, strQuery ):
        """
        convert query to a less changing one
        strQuery: a question, like "  Qui est barack obama ?"
        return sth like "qui est barack obama"
        """
        strRet = strQuery.lower();
        strRet = strRet.strip( "?:,_" );
        return strRet;
        
    def _learn( self, strQuery, strAnswer, strSource = None ):
        rDefaultNote = 0.2;
        self.bModified = True;
        found = self._search( strQuery );
        if( found[1] == "" ):
            # new one
            self.log( "INF: learn: adding a new question: '%s' => '%s'" % ( strQuery, strAnswer ) );
            self.data[strQuery] = {strAnswer: [rDefaultNote, [strSource] ]};
        else:
            strQuery = found[1]; # sometimes a nearly query has been found
            if( not strAnswer in self.data[strQuery].keys() ):
                # add answer
                self.log( "INF: learn: adding a new answer: '%s' => '%s'" % ( strQuery, strAnswer ) );
                self.data[strQuery][strAnswer] = [rDefaultNote, [strSource] ];
            else:
                # update note
                self.log( "INF: learn: updating a new answer: '%s' => '%s'" % ( strQuery, strAnswer ) );
                self._note( strQuery, strAnswer, 1, strSource );
    # _learn - end
    
    def learn( self, strQuery, strAnswer, strSource = "" ):
        """
        Learn something
        - strQuery, 
        - strAnswer
        - strSource: optional: add an info about the source giving that answer
        Armored method !
        """
        try:
            self.log( "INF: learn for '%s': '%s' (src: '%s')" % (strQuery, strAnswer, strSource ) );
            while( self.mutex.testandset() == False ):
                self.log( "INF: knowledge.learn: locked..." );
                time.sleep( 0.1 );
                
            self.lockSession(True);
            self._force_reload();
            strQuery = httptools.html_decode( strQuery );
            strQuery = httptools.phonetiseFrenchAccent( strQuery );
            strAnswer = httptools.html_decode( strAnswer );
            strSource = httptools.html_decode( strSource );

            strQuery = self.formatQuery( strQuery );
            
            self.log( "INF: learn: after string decode: '%s': '%s' (src: '%s')" % (strQuery, strAnswer, strSource ) );
            
            self._learn( strQuery, strAnswer, strSource );
            self._save();
            self.lockSession(False);
            self.mutex.unlock();
        except BaseException, err:
            self.log( "ERR: EXCEPTION CATCHED: learn error: %s" % str(err) );
            self.lockSession(False);
            self.mutex.unlock();            
        return True;
    # learn - end
    
    def randomInfo( self ):
        """
        look for a random piece of information
        """
        self.log( "INF: randomInfo: entering" );
        while( self.mutex.testandset() == False ):
            self.log( "INF: knowledge.randomInfo: locked..." );
            time.sleep( 0.1 );        
        #~ k = random.choice(d.keys()); # choice seems to not exists...        
        #~ retVal = [k, _search(k)[0]];
        n = random.randint( 0, len( self.data ) - 1 );
        nCpt = 0;
        retVal = ["", []];
        for k,v in self.data.iteritems():
            if( nCpt == n ):
                retVal = [k,v];
                break;
            nCpt += 1;
        self.mutex.unlock();
        self.log( "INF: randomInfo: '%s'" % (retVal ) );
        return retVal;
    # randomInfo - end
    
    def _note( self, strQuery, strAnswer, nModifier = 1, strSource = "" ):
        """
        (internal method)
        """
        rStep = 0.1;
        self._updateAnswer( strQuery, strAnswer, rStep * nModifier, strSource );
        return True;
    
    def note( self, strQuery, strAnswer, nModifier = 1, strSource = "" ):
        """
        Modify the confidence of an answer
        Armored method !
        - nModifier: 1 add a good step, -1: add a bad step, you can put more to change "more"
        """
        try:        
            self.log( "INF: Changing note for '%s': '%s' (mod:%d)..." % (strQuery, strAnswer, nModifier ) );
            while( self.mutex.testandset() == False ):
                self.log( "INF: knowledge.note: locked..." );
                time.sleep( 0.1 );
            self.lockSession(True);
            self._force_reload();
            strQuery = httptools.html_decode( strQuery );
            strQuery = httptools.phonetiseFrenchAccent( strQuery );
            strQuery = self.formatQuery( strQuery );
            strAnswer = httptools.html_decode( strAnswer );
            strSource = httptools.html_decode( strSource );        
            bRet = self._note( strQuery, strAnswer, nModifier, strSource );
            self._save();
            self.lockSession(False);
            self.mutex.unlock();
            return bRet;
        except BaseException, err:
            self.log( "ERR: EXCEPTION CATCHED: note error: %s" % str(err) );
            self.lockSession(False);
            self.mutex.unlock();            
        return True;
        
    def _updateAnswer( self, strQuery, strAnswer, rMod, strSource ):
        self.log( "INF: _updateAnswer: updating a new answer: '%s' => '%s' - change: %5.1f" % ( strQuery, strAnswer, rMod ) );        
        self.bModified = True;
        try:
            self.data[strQuery][strAnswer][0] += rMod;
            if( not strSource in self.data[strQuery][strAnswer][1] ):
                self.data[strQuery][strAnswer][1].append( strSource );
        except BaseException, err:
            # we should never go there
            self.log( "INF: _updateAnswer: update for an inexistant answer is weird !!! (err: %s)" % str(err) );
            if( rMod >= 0. ):
                # we store only when it's good !
                self._learn( strQuery, strAnswer, strSource );
                self.data[strQuery][strAnswer][0] += rMod;
    # _updateAnswer - end
        
        
    def _search( self, strQuery, bApproximativeSearch = False ):
        """
        internal unarmored search (and not statisticated)        
        - bApproximativeSearch: can we search for approximative search (you shouldn't at learn stage!!!)
        """
        try:
            ans = self.data[strQuery];
            return [ans, strQuery];
        except BaseException, err:
            print( "DBG:_search: possible error: key '%s' not found" % str(err) );
            rBest = 421;
            kBest = "";
            if( True ):
                # metaphone search
                self.log( "   DBG: methaphone search..." );
                metaQuery = metaphone.dm(unicode( strQuery ) );
                for k,v in self.data.iteritems():
                    metaK = metaphone.dm(unicode(k));
                    self.log( "   DBG: %s (%s) comp to %s (%s)" % (metaQuery,strQuery, metaK, k) );
                    if( metaK == metaQuery ):
                        self.log( "   INF: found in metaphone: %s ~= %s" % ( strQuery, k ) );
                        return [v,k];
                    if( bApproximativeSearch ):
                        # compute distance
                        rMidLen = ( len(metaK[0]) + len( metaQuery[0] ) ) / 2.;
                        rDist = stringtools.levenshtein( metaK[0], metaQuery[0] ) / rMidLen;
                        if( rDist < rBest ): # and nDist + 2 < min( len(metaK[0]), len( metaQuery[0] ) ) ): # si on a autant de difference que la longueur de la chaine, c'est pourri
                            self.log( "   INF: new best nearest: %s ~= %s (dist:%5.3f)" % ( strQuery, k, rDist ) );
                            rBest = rDist;
                            kBest = k;
            if( rBest < 0.5 ):
                return [self.data[kBest],kBest]; # TODO: divide confidence related to rBest distance + donner un bonus si c'est ce robot qui l'a appris ? (non ca on le fera dans le comportement haut niveau)
            return [{},""];
    # _search - end
        
    def search( self, strQuery ):
        """
        Search an answer in the database.
        Return a list of sorted answer and the key associated to the search. or [{},""] if not found
        eg: search( "ou est alexandre?" ) => [{"au toilettes":[0.6, ["NaoAlex16"], "a la piscine": [0.2,[] ] }, "ouais alexandre?"]
        Armored method !
        """
        try:
            self.log( "INF: Searching for '%s'..." % strQuery );
            while( self.mutex.testandset() == False ):
                self.log( "INF: knowledge.search: locked..." );
                time.sleep( 0.1 ); 
            # we won't change the file, so no need to lock it
            # But Do we need to ensure the file is not currently being wroten ? (TODO?)
            self.lockSession(True);
            self._force_reload(); # this line force us to lock !
            self.lockSession(False);
            strQuery = httptools.html_decode( strQuery );
            strQuery = httptools.phonetiseFrenchAccent( strQuery );
            strQueryF = self.formatQuery( strQuery );
            out = self._search( strQueryF, bApproximativeSearch = True );
            self.log( "INF: Searching for '%s' (fmt: '%s') => %s" % (strQuery,strQueryF,str(out)) );
            self.mutex.unlock();
            return out;
        except BaseException, err:
            self.log( "ERR: EXCEPTION CATCHED: search error: %s" % str(err) );
            self.mutex.unlock();
            return [{},""];
    # search - end
# class KnowledgeEngine - end



def autoTest():
    know = KnowledgeEngine( "autotest" );
    print "search: " + str( know.search( "not foundable" ) );
    print "search: " + str( know.search( "qui est tu ?" ) );
    print "learn: " + str( know.learn( "qui est tu ?", "nao", "NaoAlex16" ) );
    print "learn: " + str( know.learn( "qui est tu ?", "gros connard" ) );
    print "learn: " + str( know.learn( "qui est tu ?", "un rigolo" ) );
    print "learn: " + str( know.learn( "est tu content?", "oui" ) );
    print "learn: " + str( know.learn( "est tu content?", "oui" ) );
    print "learn: " + str( know.learn( "est tu content?", "des fois" ) );
    print "learn: " + str( know.learn( "Qui est barack obama?", "Le président des états unis" ) );
    print "learn: " + str( know.learn( "Qui est le président des états unis?", "barack obama!" ) );
    print "search: " + str( know.search( "qui est tu ?" ) );
    print "search: " + str( know.search( "Qui est barack obama" ) );
    print "search: " + str( know.search( "Mais c'est qui barack obama" ) );
    print "search: " + str( know.search( "Mais c'est qui les états unis?" ) );
    print "random: " + str( know.randomInfo() );
# autoTest - end

def autoTest_no_web():
    know = KnowledgeEngine( "autotest" );
    print "search: " + str( know._search( "not foundable" ) );
    print "search: " + str( know._search( "qui est tu ?" ) );
    print "learn: " + str( know._learn( "qui est tu ?", "nao", "NaoAlex16" ) );
    print "learn: " + str( know._learn( "qui est tu ?", "gros connard" ) );
    print "learn: " + str( know._learn( "qui est tu ?", "un rigolo" ) );
    print "learn: " + str( know._learn( "est tu content?", "oui" ) );
    print "learn: " + str( know._learn( "est tu content?", "oui" ) );
    print "learn: " + str( know._learn( "est tu content?", "des fois" ) );
    print "learn: " + str( know._learn( "Qui est barack obama?", "Le president des etats unis" ) );
    print "learn: " + str( know._learn( "Qui est le president des etats unis?", "barack obama!" ) );
    print "search: " + str( know._search( "qui est tu ?" ) );
    print "search: " + str( know._search( "Qui est barack obama" ) );
    print "search: " + str( know._search( "Mais c'est qui barack obama" ) );
    print "search: " + str( know._search( "Mais c'est qui les etats unis?" ) );
    print "random: " + str( know.randomInfo() );
# autoTest - end


if __name__ == "__main__":
    autoTest_no_web();
    pass
    exit();
    
if 0:
    # standard process
    know = dict();
    know["fr"] = KnowledgeEngine( "data_fr" );
    know["en"] = KnowledgeEngine( "data_en" );