# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Knowledge database access
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Aldebaran Behavior Complementary Development Kit: A module for system tools."""
print( "importing abcdk.knowledge" );

import arraytools
import filetools
import nettools
import stringtools
import system
import time
import translate
import typetools


def getMedicamentInfo( strObjectName ):
    """
    Connect to the medicament database to retrieve info.
    return a dictionnary containing some of that field:    
    - name: name of the object
    - pronunciation: a dict by lang code: the right way to pronounce its name.
    - usage: a dict by lang code: indication of use
    - posology: a dict by lang code: posology
    - isbn: the global bar code ean13
    return None if not found
    """
    
    # strWebserver = "http://10.0.252.216/ObjectKnowledge/";
    #~ strWebserver = "http://candiweb.factorycity.com/ObjectKnowledge/"; # redirection 301 not working in our cpp modules 
    # strWebserver = "http://82.237.225.247:70/ObjectKnowledge/"; # but :70 won't work either with or cpp => removing our cpp part
    #~ strWebserver = "http://studio.aldebaran-robotics.com/amazel/ObjectKnowledge/";
    strWebserver = "http://knowledge.factorycity.com/ObjectKnowledge/"; # redirection 301 not working in our cpp modules 
    if( strObjectName[-1] == ' ' ):
        strObjectName = strObjectName[:-1];
    strQuery = strWebserver + "search.py?name=%s&type=%d" % ( (strObjectName.replace( " ", "_SPACE_" ) ), 10 ); # 10 is the medicine type
    strData = nettools.getHtmlPage( strQuery, bTryToUseCpp = False, bUseCache = True );
    print( "nettools.getHtmlPage: return '%s'" % strData );
    if( strData == '' ):
        print( "nettools.getHtmlPage: returning empty, auto retry in 0.5sec" );
        time.sleep( 0.5 );
        strData = nettools.getHtmlPage( strQuery, bTryToUseCpp = False, bUseCache = True );
        print( "nettools.getHtmlPage: return '%s'" % strData );                
    if( len( strData ) > 0 ):
        listData = eval(strData);
        if( len( listData ) > 0 ):
            # return first medicine object
            # listData contain: '[{'strMiscID': '', 'nType': 10, 'strISBN': '7640107850806', 'strName': 'Audibaby', 'optionnal': '["Hygi\\xc3\\xa8ne de l\'oreille.", \'Hygiene of the ear.\'],[\'Utiliser un flacon pour nettoyer chaque oreille. A faire une fois par semaine, pendant un mois.\', \'Use a bottle to clean each ear. To do once a week for one month.\']'},]'
            data = listData[0];
            ret = {};
            ret["name"] = data["strName"];
            ret["isbn"] = data["strISBN"];
            if( "optionnal" in data.keys() ):
                opt = eval( data["optionnal"] );
                ret["usage"] = {};
                ret["usage"]["fr"] = opt[0][0];
                ret["usage"]["en"] = opt[0][1];
                ret["posology"] = {};
                ret["posology"]["fr"] = opt[1][0];
                ret["posology"]["en"] = opt[1][1];
            return ret;
    return None;
# getMedicamentInfo - end

def autoTest_MedicamentInfo():
    print "medic: " + str( getMedicamentInfo( "Audibaby" ) );
    print "medic: " + str( getMedicamentInfo( "Dynamisan" ) );    
    
    
    
    
global_UniverseKnowledge_WebServer = "http://studio.aldebaran-robotics.com/knowledge/"
def UniverseKnowledge_setWebServer( strNewWebServerAddress ):
    global global_UniverseKnowledge_WebServer
    global_UniverseKnowledge_WebServer = strNewWebServerAddress
    
def UniverseKnowledge_search( strQuestion ):
    """
    Search for a question in the web K database.    
    Return: 
        - a list of sorted answer and the key associated to the search, eg: [{"au toilettes":[0.6, "NaoAlex16"], "a la piscine": [0.2, ""] }, "ouais alexandre?"]
        - [{},""] if not found
        - None on error (web error or script error)
    - strQuestion: question to ask
    """
    global global_UniverseKnowledge_WebServer
    print( "UniverseKnowledge_search: '%s'" % (strQuestion) );    
    strCountry = translate.getLangAbbrev();
    strQuestion = stringtools.html_encode(strQuestion);
    print( "UniverseKnowledge_search: converted: '%s'" % (strQuestion) );
    buf = nettools.getHtmlPage( "%ssearch.py?q=%s&l=%s" % (global_UniverseKnowledge_WebServer,strQuestion, strCountry ) );
    print( "UniverseKnowledge_search: ret: '%s'" % buf );
    if( len(buf) < 2 ):
        return None;
        
    retVal = eval(buf);
    if( not typetools.isArray( retVal ) ):
        return None;
    if( retVal == [] ):
        retVal = [{},""]; # for compatibility reason
    return retVal;
# UniverseKnowledge_search - end

def UniverseKnowledge_analyseAnswer( answers ):
    """
    analyse answer from UniverseKnowledge_search
    return:
     - [[best_global, rConfidence, True]] 
     - [[best_perso, rConfidence, False]], if my perso is far better than the global
     - [[best_global, rConfidence, False], [best_perso, rConfidence, True]] if some perso is existing
     - [] if no answers
     - None on error
     params:
    - answers could be:
      - standard form: [ {"au toilettes":[0.6, "NaoAlex16"], "a la piscine": [0.2, ""] }, "ouais alexandre?"]
      - flattened form: [ ["au toilettes", [0.6, "NaoAlex16"]], ["a la piscine": [0.2, ""]] ]
     
    """
    if( answers == None ):
        return answers;
    if( answers == [{},""] or answers == [[],""] or answers == [] ):
        return [];
    strMe = system.getNaoNickName();
    print( "INF: UniverseKnowledge_analyseAnswer: My name is '%s', answers are: '%s'" % (strMe,str(answers)) );
    rBestGlobal = rBestPerso = -1.;
    strBestGlobal = strBestPerso = "";
    if( isinstance( answers[0], dict ) ):
        # standard form, convert to array:
        answers = arraytools.dictToArray( answers[0] );
    elif not isinstance( answers[-1], dict ):
        answers = answers[0]
    for k,v in answers:
        rConf = v[0];
        strSource = v[1];
        if( strSource == strMe ):
            if( rBestPerso < rConf ):
                rBestPerso = rConf;
                strBestPerso = k;
        else:
            if( rBestGlobal < rConf ):
                rBestGlobal = rConf;
                strBestGlobal = k;
    if( rBestPerso > 0. ):
        if( rBestGlobal < rBestPerso/2 ):
            return [[strBestPerso,rBestPerso, False]];
        return [[strBestGlobal,rBestGlobal, True],[strBestPerso,rBestPerso, False]];
    return [[strBestGlobal,rBestGlobal, True]];
# UniverseKnowledge_analyseAnswer - end

def UniverseKnowledge_generateUserAnswer( answers ):
    """
    analyse answer from UniverseKnowledge_search, and generate sentence to tell user
    return:
     - if found: [a sentence to told user (multilang already handled), the raw sentence to increase or decrease note]
     - else: [just a sentence] eg: ["i dont know teach me" (multilang already handled)]
    """    
    
    bests = UniverseKnowledge_analyseAnswer( answers );    
    aNearlySentences = { "fr": ["Peut être", "enfin, je crois", "mais je suis pas sur", "probablement"], "en": ["maybe", "I know", "But i'm not sure", "probably"] };
    aSureSentences = { "fr": ["surement", "J'en suis sur", "J'en mettrais ma main dans l'eau", "C'est clair.", "C'est sur.", "Je suis sur de ca", "plusieurs personnes me l'ont deja dit.", "oui c'est vrai", "oui c'est bien vrai", "mais c'est bien sur", "carrément", "surement"], "en": ["I'm sure of it", "yes it is", "It's cristal clear"] };
    aPersoSentences = { "fr": ["Mais moi on m'a dit: ", "Mais je crois personnellement que: "], "en": ["But someone says to me: ", "But I think: "] };        
    aDontKnow = { "fr": ["Je sais pas, dis moi!"], "en": ["I don't know, teach me!"] };        
    print( "abcdk.knowledge.UniverseKnowledge_generateUserAnswer: bests: %s" % str(bests) );
    if( len(bests) < 1 ):
        return [translate.chooseFromDictRandom( aDontKnow )];
    # take first answer
    if( 0 ):
        strAns = bests[0][0].replace( "_", " " );
        rConf = bests[0][1][0];
    # take best answer, and best for me
    if( 1 ):
        bests = UniverseKnowledge_analyseAnswer( answers );
        strAns = bests[0][0];
        rConf = bests[0][0];
    strTxt = strAns;
    if( rConf > 0.8 ):
        strTxt = "%s, %s." % ( strAns, translate.chooseFromDictRandom( aSureSentences ) );
    elif( rConf < 0.3 ):
        strTxt = "%s, %s" % ( strAns, translate.chooseFromDictRandom( aNearlySentences ) );
        
    # add perso:
    if( len(bests)>1 ):
        strAns = bests[1][0];
        rConf = bests[1][0];            
        strTxt += " " + translate.chooseFromDictRandom( aPersoSentences ) + " " + strAns;
    return [strTxt, strAns]; # if we speak of a perso, it would be that one that would be changed
# UniverseKnowledge_generateUserAnswer - end    

def UniverseKnowledge_learn( strQuestion, strAnswer, nModifier = 0, nUseLang = -1 ):
    """
    Learn a new answer in the web K database.
    Return: 
        - True if all's ok
    - strQuestion: question to ask
    - strAnswer: list of answer to add
    - nModifier: 0: creation, 1: add a bonus, -1: add a malus
    """
    global global_UniverseKnowledge_WebServer
    print( "UniverseKnowledge_learn: '%s' => '%s'" % (strQuestion, strAnswer) );
    strCountry = translate.getLangAbbrev( nUseLang );
    strQuestion = stringtools.html_encode( strQuestion );
    strAnswer = stringtools.html_encode( strAnswer );
    strSource = system.getNaoNickName();
    print( "UniverseKnowledge_learn: converted: '%s' => '%s'" % (strQuestion, strAnswer) );
    buf = nettools.getHtmlPage( "%slearn.py?q=%s&a=%s&b=%d&l=%s&s=%s" % (global_UniverseKnowledge_WebServer,strQuestion, strAnswer, nModifier, strCountry, strSource ) );
    print( "UniverseKnowledge_learn: ret: '%s'" % buf );
    return True;
# UniverseKnowledge_learn - end

def UniverseKnowledge_randomInfo():
    """
    Get a random information
    Return same as search
    """
    global global_UniverseKnowledge_WebServer
    print( "UniverseKnowledge_randomInfo:" );    
    strCountry = translate.getLangAbbrev();
    buf = nettools.getHtmlPage( "%srandom_info.py?l=%s" % ( global_UniverseKnowledge_WebServer,strCountry ) );
    print( "UniverseKnowledge_randomInfo: ret: '%s'" % buf );
    retVal = eval(buf);
    if( not typetools.isArray( retVal ) ):
        return None;
    if( retVal == [] ):
        retVal = [{},""]; # for compatibility reason
    return retVal;    
# UniverseKnowledge_learn - end    


def UniverseKnowledge_filldb():
    aBase = {
    "Qui est le président des états unis ?": "Barack Obama",
    "Qui est Barack Obama ?": "le président des états unis",
    "Qui est le président de la belgique?": "Il n'y en a pas!",        
    "Comment on fait les bébés ?": "En plantant des petites graines",
    "Quel est le but de l'univers ?": "42",
    "Qui est NAO ?": "un petit robot",
    "Qui est ton père!": "La recherche",
    };
    
    for k,v in aBase.iteritems():
        UniverseKnowledge_learn( k,v,3,nUseLang=1);
    
    # addition
    nMax = 4;
    for j in range( nMax ):
        for i in range( nMax ):
            strQ = "Combien font %d plus %d" % (i,j);
            UniverseKnowledge_learn( strQ,str(i+j),3,nUseLang=1);
            strQ = "Combien font %d fois %d" % (i,j);
            UniverseKnowledge_learn( strQ,str(i*j),3,nUseLang=1);
# UniverseKnowledge_filldb - end

def UniverseKnowledge_filldb_from_csv( strFilename, nUseLang = -1 ):
    infos = filetools.loadCsv( strFilename );
    for info in infos[1:]: # skip headers
        strQuestion = info[0];
        for strAnswer in info[1:]:
            if( len(strAnswer) > 1 ):
                print( "%s => %s" % (strQuestion, strAnswer) );
                #~ print stringtools.phonetiseFrenchAccent( strQuestion );
                #~ print stringtools.phonetiseFrenchAccent( strAnswer );
                UniverseKnowledge_learn( strQuestion,strAnswer,3,nUseLang=nUseLang);
    
# UniverseKnowledge_filldb_from_csv - end    


def autoTest_UniverseKnowledge():
    print UniverseKnowledge_search( "Qui est le président des états unis ?" );
    print UniverseKnowledge_search( "Qui est Barack Obama ?" );
    
    strMeTest = system.getNaoNickName();
    strAnswer = None;
    bests = UniverseKnowledge_analyseAnswer( strAnswer );
    print( bests );
    assert( strAnswer == bests );
    
    strAnswer = [{},""];
    bests = UniverseKnowledge_analyseAnswer( strAnswer );
    print( bests );
    assert( [] == bests );

    answers = [{"barack obama": [0.5, ""]},""];
    bests = UniverseKnowledge_analyseAnswer( answers );
    print( bests );
    assert( len(bests)==1 );
    assert( bests[0][2] == True );
    assert( bests[0][0] == answers[0].keys()[0] );
    
    answers = [["barack obama", [0.5, ""]] ];
    bests = UniverseKnowledge_analyseAnswer( answers );
    print( bests );
    assert( len(bests)==1 );
    assert( bests[0][2] == True );
    assert( bests[0][0] == answers[0][0] );
    

    answers = [{"barack obama": [0.5, ""],"jean pierre": [0.6, strMeTest]},""];
    bests = UniverseKnowledge_analyseAnswer( answers );
    print( bests );
    assert( len(bests)==2 );
    assert( bests[0][2] == True );
    assert( bests[1][2] == False );
    assert( bests[0][0] == answers[0].keys()[0] ); # WRN: keys are not mandatory sorted !
    assert( bests[1][0] == answers[0].keys()[1] ); # WRN: keys are not mandatory sorted !

    answers = [{"barack obama": [0.2, ""],"jean pierre": [0.6, strMeTest]},""];
    bests = UniverseKnowledge_analyseAnswer( answers );
    print( bests );
    assert( len(bests)==1 );
    assert( bests[0][2] == False );
    assert( bests[0][0] == answers[0].keys()[1] ); # WRN: keys are not mandatory sorted !

    answers = [{"jean pierre": [0.6, strMeTest]},""];
    bests = UniverseKnowledge_analyseAnswer( answers );
    print( bests );
    assert( len(bests)==1 );
    assert( bests[0][2] == False );
    assert( bests[0][0] == answers[0].keys()[0] );
    
    retVal = UniverseKnowledge_learn( "Qui est le président des états unis ?", "Barack Obama" );    
    retVal = UniverseKnowledge_search( "Qui est le président des états unis ?" );
    print( UniverseKnowledge_generateUserAnswer( retVal[0] )[0] );
    print( "raw: %s" % UniverseKnowledge_generateUserAnswer( retVal[0] )[1] );

    retVal = UniverseKnowledge_randomInfo();
    print( "randomInfo, retVal: %s" % retVal );

def autoTest():
    #~ autoTest_MedicamentInfo();
    autoTest_UniverseKnowledge();
    #~ UniverseKnowledge_filldb();    
    if( 0 ):
        strPath = "C:/Documents and Settings/amazel/Mes documents/Downloads/";
        UniverseKnowledge_filldb_from_csv( strPath + "Knowledge_Validated - FR.csv", nUseLang = 1 );
        UniverseKnowledge_filldb_from_csv( strPath + "Knowledge_Validated - EN.csv", nUseLang = 0 );
    # add some knowledge
    #~ UniverseKnowledge_learn( "Comment appelles tu?", "NAO" );
# autoTest


if __name__ == "__main__":
    autoTest();