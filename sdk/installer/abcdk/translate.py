# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Translate tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################


"""
Tools to translate small word on the fly:
Send a word in english and a language, and it will return the equivalent in your language
lang order are the same than in constants !:
(EN), FR, SP, IT, GE, CH, PO, KO, JP, BR, TU.

TODO:
 - handled well accent (utf-8)
 - add exotic encoded language (CH, ... (not handled by Scite by now, sniff))
 
"""


print( "importing abcdk.translate" );

import datetime
import os
import random

import constants
import filetools
import numeric
import pathtools
import speech

def getLanguageIdx( nUseLang = -1 ):
    "get current current lang or a specific language if specified"
    if( nUseLang == -1 ):
        nUseLang = speech.getSpeakLanguage();
#    print( "DBG: abcdk.translate.getColor: getLanguageIdx: returning: %d" % nUseLang );
    return nUseLang;
# getLanguageIdx - end

def getLangAbbrev( nUseLang = -1 ):
    """
    get current current language code or a specific language if specified
    return "fr" or "en" or ...
    """
    nUseLang = getLanguageIdx( nUseLang );
    strCodeLang = speech.toLangAbbrev( nUseLang )
    return strCodeLang;
# getLangAbbrev - end

def getLanguageIdxFromAbbrev( strAbbrev = "en" ):
    """
    return the language idx of a lang abbreviation
    """
    return speech.fromLangAbbrev( strAbbrev );
# getLanguageIdxFromAbbrev - end    


def getUndefined( nUseLang = -1 ):
    aLang = ["mot inconnu", "palabra desconocida", "parola sconosciuta", "fremdwort", "unknown word", "unknown word","unknown word","unknown word"];
    return aLang[nUseLang-1];
# getUnknown - end

def getColorList( nUseLang = -1 ):
    """
    Return a list of color for each country (in the same order)
    """
    d = {
        "fr":  [ "noir", "blanc", "gris", "rouge", "vert", "violet", "rose", "bleu", "jaune", "orange", "marron" ],
        "en":  [ "black", "white", "grey", "red", "green", "purple", "pink", "blue", "yellow", "orange", "brown" ],
    };    
    return chooseFromDict( d, nUseLang = nUseLang );
# getColorList - end
        
def getColor( strWord, nUseLang = -1, bFemale = False ):
    "return color exprimated in some foreign language"
    "strWord: word, case insensitive"
    aaLang = {
        # TODO: antiseche pour connaitre l'ordre !!!
        "black": [ "noir", "negro", "nero", "schwarz", "", "", "", "" ],
        "white": [ "blanc" ],
        "grey": [ "gris", ],
        "red": [ "rouge", ],
        "green": [ "vert", ],
        "purple":[ "violet",],
        "pink": ["rose",],
        "blue": [ "bleu", ],
        "yellow": [ "jaune" ],
        "orange": [ "orange" ],
        "undefined": [ "indaifini" ],   
    };
    nUseLang = getLanguageIdx( nUseLang );
    if( nUseLang == 0 ):
        return strWord; # english is default
    strWord = strWord.lower();
    try:
        return aaLang[strWord][nUseLang-1];
    except BaseException, err:
        print( "ERR: abcdk.translate.getColor: while accessing word '%s' for lang idx %d: err: %s" % (strWord, nUseLang, err ) );
    return getUndefined( nUseLang );
# getColor - end

def getDirection( strWord, nUseLang = -1, bFemale = False ):
    "return a word exprimated in some foreign language"
    "strWord: word, case insensitive"
    aaLang = {
        "left": [ "gauche" ],
        "right": [ "droite" ],
        "front": [ "devant" ],
        "rear": [ "arriaire" ],
        "ahead": [ "tout droit" ],
        "behind": [ "derriaire" ],
    };
    nUseLang = getLanguageIdx( nUseLang );
    if( nUseLang == 0 ):
        return strWord; # english is default
    strWord = strWord.lower();
    try:
        return aaLang[strWord][nUseLang-1];
    except BaseException, err:
        print( "ERR: abcdk.translate.getDirection: while accessing word '%s' for lang idx %d: err: %s" % (strWord, nUseLang, err ) );
    return getUndefined( nUseLang );
# getDirection - end

def getPeopleName( nUseLang = -1 ):
    "return a person 'people' name exprimated in some foreign language"
    aaLang = {
        "fr": "Gérard Depardieu/Alain Delon/Marion Cotillard/François Mitterand/Johnny Hallyday/François Truffaut/Brigitte Bardot/Jordie/M C Solar/Jean pierre Papin/Eric Cantona/Yannick Noah/Eve Angely/Bruno Maisonnier/Brigitte Lahaie/Alexandre Mazel/Clara Morgane/Céline Dion/Garou/Joey Starr/Molière/Claude Francois",
        "en": "Her Majesty the Queen/Peter Murphy/Amy Winehouse/Tony Blair/Prince William/Mister Bean/James Bond/Robbie Williams/Terry Gilliam/marylin monroe/Victoria Beckam/David Beckam/Sahara Knite/Tamara Noon/Linsey Dawn McKenzie",
        "jp": "takeshi kaneshiro/Ayaho Myazaki/Kazuo Ishiguro/Hiroshi Ishiguro/Kiyoshi Kurosawa/Hiro Hito/Naoki Matsuda/Akira Toriyama/",
        "ch": "zhang ziyi/gong li/Mao Zedong/Deng Xiaoping/Yao Ming/Yi Jianlian/Jet Li/Annabel Chong",
        "ge": "Angela Merkel/boris becker/Jean Sebastian Bach/Fritz Lang/Horst Happert/Mort Shumann/Sexy Cora/Jessica Eichberg",
        "br": "Kaka/Ronaldo/Ayrton Senna/Oscar Niemeyer/Eugenio de Araujo Sales",
        "pt": "Linda de Suza/Maria de Medeiros/Cristiano Ronaldo/Vasco de Gama/Ricardo Carvalho/José Mourinho",
        "tu": "Mustafa Kemal Atatürk/Mehmet le Conquérant/Edouard Balladur/Alice Sapritch/Dario Moreno/Pacha Kara Mustafa de Merzifon/Kénizé Mourad/Calouste Sakis Gulbenkian/Prince Ypsilandi",
    };
    
    return chooseFromDictRandom( aaLang, nUseLang = nUseLang );
# getPeopleName - end

def getSalutation( nCurrentHour24 = -1, nUseLang = -1 ):
    """
    return a word describing the way to salute related to current hour
    nCurrentHour24: the hour [0..23] eg: from int( time.strftime( "%H", time.localtime() ) ), if nCurrentHour24 == -1 => auto hour
    """
    # for each lang, the way to say hello until the limit time (excluded)
    dictHello = {
        'fr': [ [4,"Bonsoir"], [19,"Bonjour"], [24,"Bonsoir"] ],
        'en': [ [4,"Good Evening"], [14, "Good morning"], [19,"Good afternoon"], [24,"Good Evening"] ],
        'pt': [ [4,"bon noite"], [12, "bon dia"], [19,"boa tarde"], [24,"bon noite"] ],
        'jp': [ [3,"konbanwa"], [10, "oayogozaimas"], [19,"konnitchiwa"], [24,"konbanwa"] ],
        'ch': [ [3,"wanshang hao"], [11, "zaoshang hao"], [18,"nihao"], [24,"认识"] ],
    };
    if( nCurrentHour24 == -1 ):
      datetimeObject = datetime.datetime.now()
      nCurrentHour24 = datetimeObject.hour;
      #print( "DBG: getSalutation: using: %d" % nCurrentHour24 );      
    try:
        nUseLang = getLanguageIdx( nUseLang );
        listHour = dictHello[speech.toLangAbbrev( nUseLang ) ];
        for elem in listHour:
            if( nCurrentHour24 < elem[0] ):
                return elem[1];
    except BaseException, err:
        print( "DBG: translate.getSalutation: " + str( err ) );
    return "Hello"; # default one
# getSalutation - end    

#~ print getSalutation( nUseLang=0 );

def getWord( strWord, nUseLang = -1, bFemale = False ):
    "return a word exprimated in some foreign language"
    "strWord: word, case insensitive"
    aaLang = {
        "unknown": [ "inconnu" ],
        "undefined": [ "indaifini" ],
        "lost": [ "perdu" ],
        "win": [ "gagnai" ],
     
    };
    nUseLang = getLanguageIdx( nUseLang );
    if( nUseLang == 0 ):
        return strWord; # english is default
    strWord = strWord.lower();
    try:
        return aaLang[strWord][nUseLang-1];
    except BaseException, err:
        print( "ERR: abcdk.translate.getWord: while accessing word '%s' for lang idx %d: err: %s" % (strWord, nUseLang, err ) );
    return getUndefined( nUseLang );
# getWord - end

def chooseText( aList, nUseLang = -1 ):
    """
    choose text among some, according to the lang
    aList: an array of text ["hello","bonjour", ...]    
    """
    nUseLang = getLanguageIdx( nUseLang );
    try:
        return aList[nUseLang];
    except BaseException, err:
        print( "ERR: abcdk.translate.chooseText: while accessing word '%s' for lang idx %d: err: %s" % (str(aList), nUseLang, err ) );
    return getUndefined( nUseLang );
# chooseText - end

def chooseFromDict( dictText, nUseLang = -1 ):
    """
    choose text among some, according to the lang
    aList: a dictionnary of text {'en': "hello", 'fr':"bonjour", ...}
    """
    nUseLang = getLanguageIdx( nUseLang );
    strCodeLang = speech.toLangAbbrev( nUseLang );
    try:
        return dictText[strCodeLang];
    except BaseException, err:
        print( "ERR: abcdk.translate.chooseFromDict: while accessing word '%s' for lang idx %d: err: %s" % (str(dictText), nUseLang, err ) );
    return getUndefined( nUseLang );
# chooseFromDict - end

def chooseFromDictRandom( dictText, nUseLang = -1 ):
    """
    pick a text in a list, according to the lang
    - aList: a dictionnary of text {en': "hello/good morning", 'fr':"bonjour/coucou/salut", ...}
    - alternate form: {en': ["hello", "good morning"], 'fr':["bonjour","coucou", salut", ...]}
    """
    nUseLang = getLanguageIdx( nUseLang );
    strCodeLang = speech.toLangAbbrev( nUseLang )
    try:
        strTexts = dictText[strCodeLang];
        if( isinstance( strTexts, list ) ):
            aText = strTexts; # alternate form
        else:
            aText = strTexts.split("/");
        return aText[numeric.randomDifferent(0,len(aText)-1)];
    except BaseException, err:
        print( "ERR: abcdk.translate.chooseFromDictRandom: while accessing word '%s' for lang idx %d: err: %s" % (str(dictText), nUseLang, err ) );
    return getUndefined( nUseLang );
# chooseFromDictRandom - end
#~ print( chooseFromDictRandom( {'en': "hello/good morning", 'fr':"bonjour/coucou/salut" } ) );
#~ print( chooseFromDictRandom( {'en': ["hello","good morning"], 'fr':["bonjour","coucou","salut"] } ) );
#~ print( chooseFromDictRandom( {'en': "hello", 'fr':"bonjour" } ) );

def translateTechnicBodyWord( strCompoundWord, nUseLang = -1 ):
    """
    Translate Robot technic word to every langage
    RightShoulderBoard => Droite épaule Carte: (un peu bof)
    """
    nUseLang = getLanguageIdx( nUseLang );
    strCodeLang = speech.toLangAbbrev( nUseLang );
    aEN = ["Board", "Foot", "Shin", "Thigh", "Hip", "Hand", "Arm", "Shoulder", "Head", "Touch", "Chest", "US", "Face", "Left", "Right", "Trunk", "Neck", "Roll", "Yaw", "Pitch"];
    aFR = ["Carte", "Pied", "Tibia", "Cuisse", "Hanche", "Main", "Bras", "épaule", "Tête", "Tactile", "Torse", "UltraSon", "Visage", "Gauche", "Droite", "Tronc", "Cou", "Role", "Yo", "Pitche" ];
    
    # add Spaces:
    strCompoundWordAndSpaces = strCompoundWord[0];
    for letter in strCompoundWord[1:]:
        if( letter.isupper() ):
            strCompoundWordAndSpaces += " ";
        strCompoundWordAndSpaces += letter;
    strCompoundWord = strCompoundWordAndSpaces;
    strCompoundWord = strCompoundWord.replace( "R ", "Right " );
    strCompoundWord = strCompoundWord.replace( "L ", "Left " );
    
    listReplace = aEN;
    if( strCodeLang == "fr" ):
        listReplace = aFR;
    for nIdx in range( len( listReplace ) ):
        strCompoundWord = strCompoundWord.replace( aEN[nIdx], listReplace[nIdx] );
    return strCompoundWord;
# translateTechnicBodyWord - end
#~ print translateTechnicBodyWord( "RightShoulderBoard", 1 );
#~ print translateTechnicBodyWord( "RHipYawPitch", 1 );

def translateBoardName( strCompoundWord, nUseLang = -1 ):
    """
    Translate Robot Board Name to every langage, text to speechable
    """
    nUseLang = getLanguageIdx( nUseLang );
    strCodeLang = speech.toLangAbbrev( nUseLang );
    aEN = ["Foot", "Shin", "Thigh", "Hip", "Hand", "Arm", "Shoulder", "Head", "Touch", "Chest", "US", "Face"];
    aFR = ["Pied", "Tibia", "Cuisse", "Hanche", "Main", "Bras", "épaule", "Tête", "Tactile", "Torse", "UltraSon", "Visage" ];
    
    listReplace = aEN;
    if( strCodeLang == "fr" ):
        listReplace = aFR;
    for nIdx in range( len( listReplace ) ):
        strCompoundWord = strCompoundWord.replace( aEN[nIdx], listReplace[nIdx] );
    # change side
    
    if( "Board" in strCompoundWord ):
        strCompoundWord = "Carte " + strCompoundWord.replace( "Board", "" ); # TODO multilang !
    if( "Left" in strCompoundWord ):
        strCompoundWord = strCompoundWord.replace( "Left", "" ) + " Gauche"; # TODO multilang !
    if( "Right" in strCompoundWord ):
        strCompoundWord = strCompoundWord.replace( "Right", "" ) + " Droite"; # TODO multilang !        
    return strCompoundWord;
# translateBoardName - end
#~ print translateBoardName( "RightShoulderBoard", 1 );

def getRoomName(  nUseLang = -1 ):
    d = {
        "fr":  [ "bureau", "cuisine", "chambre", "salle à manger", "salon", "salle de bain", "entrée", "accueil", "toilettes", "débarras", "atelier", "studio", "grenier", "cave", "salle de réunion","laboratoire"],
        "en":  [ "office", "kitchen", "bedroom", "dining room", "living room", "bathroom", "entrance", "reception", "rest room", "storeroom", "workshop", "studio", "attic", "cellar", "meeting room", "laboratory"],
    };
    
    return chooseFromDict( d, nUseLang = nUseLang );
# getRoomName - end

def getNoName(  nUseLang = -1 ):
    d = {
        "fr":  "Pas de nom",
        "en":  "No name",
    };
    
    return chooseFromDict( d, nUseLang = nUseLang );
# getNoName - end


def getListYesNo( nUseLang = -1 ):
    """
    Return a list of word with the positivism of each one: yes: 1, no: -1.
    It should be answer to question like: did you like this ? Did you hear me?
    """
    d = {
        "fr":  [ 
                    ["oui", +1.],
                    ["super", +1.],
                    ["ok", +1.],
                    ["très bien", +1.],
                    ["carrément", +1.],
                    ["tout a fait", +1.],
                    ["complétement", +1.],
                    ["affirmatif", +1.],
                    ["d'accord", +1.],
                    ["bien", +0.9],
                    ["ssa va", +0.8],
                    ["avec plaisir", +0.8],
                    ["pas mal", +0.4],
                    ["un peu", +0.2],
                    ["bof", -0.3],
                    ["pas trop", -0.5],
                    ["non", -1.],
                    ["mal", -1.],
                    ["négatif", -1.],
                    ["point du tout", -1.],
                    ["pas du tout", -1.],
                ],
        "en":  [ 
                    ["yes", +1.],
                    ["great", +1.],
                    ["completely", +1.],
                    ["right", +1.],
                    ["ok", +1.],
                    ["totally", +1.],
                    ["affirmatif", +1.],
                    ["good", +0.9],
                    ["it's ok", +0.8],
                    ["why not", +0.6],
                    ["not bad", +0.4],
                    ["a few", +0.2],
                    ["quite", +0.2],
                    ["not much", -0.5],
                    ["no", -1.],
                    ["not at all", -1.],
                ],
        "ko":  [ 
                    ["ie", +1.],
                    ["anyo", -1.],
                ],
        "de":  [ 
                    ["ja", +1.],
                    ["nein", -1.],
                ],
        "ch":  [ 
                    ["chiais", +1.],
                    ["mé-io", -1.],
                ],
        "jp":  [ 
                    ["aille", +1.],
                    ["iiai", -1.],
                ],                
    };
    return chooseFromDict( d, nUseLang = nUseLang );
# getListYesNo - end

def getChristianName( nUseLang = -1 ):
    """
    Return a list of firstname related to a country
    """
    
    buf = filetools.getFileContents( pathtools.getABCDK_Path() + os.sep + "data" + os.sep + "christian_name_list_%s.txt" % getLangAbbrev( nUseLang = nUseLang ) );
    print( "buf: %s" % buf );
    aList = buf.split( '\n' );
    return aList;
# getChristianName - end    

def getTeamName( nUseLang = -1 ):
    """
    Return a list of people in our team
    """
    aList = ["Alexandre", "Laurent", "Rodolphe", "Steev", "Blaise", "Pierre", "Marc-Antoine", "Amel", "William", "Thomas", "Estelle", "Gilbert", "Arnaud", "Samy" ];
    return aList;
# getTeamName - end    

def generateOwnerPossibilities( aaList, nUseLang = -1 ):
    """
    take a list of list and generate all posibilities
    - aaList: a tuple of list eg: (["Bureau", "Chambre"], [ "Alexandre", "Laurent"] )
    => 
    in french: "Bureau Alexandre", "Bureau de Laurent", "Chambre de Alexandre", "Chambre de Laurent"
    in english: "Alexandre'Bureau", "Laurent's Bureau" ...
    
    """
    nUseLang = getLanguageIdx( nUseLang );
    
    a = [];    
    for place in aaList[0]:
        for owner in aaList[1]:
            if( nUseLang == constants.LANG_EN ):
                s = owner + "'s" + place;
            else:
                s = place + " de " + owner;
            a.append( s );
    return a;
# generateOwnerPossibilities - end

    

def translateLanguageName( strLangName, nUseLang = -1 ):
    """
    "Japanese" => "Japonais"
    - strLangName: the language name in english    
    """
    # dictionnary without english word
    aDict = {
        "Brazilian":  { "fr": "Brai-zilien" },
        "Chinese":  { "fr": "Chinois" },
        "English": { "fr": "Anglais" },
        "French":  { "fr": "Franssais" },
        "German":  { "fr": "Allemand" },
        "Italian":  { "fr": "Italien" },
        "Japanese":  { "fr": "Japonais" },
        "Korean":  { "fr": "Coréen" },
        "Portuguese":  { "fr": "Portugais" },
        "Spanish":  { "fr": "Espagnol" },
        "Turkish":  { "fr": "Turque" },
    };
    
    if( nUseLang == constants.LANG_EN ):
        return strLangName;
    
    try:
        return chooseFromDict( aDict[strLangName], nUseLang = nUseLang );
    except Exception, err:
        print( "ERR: abcdk.translate.translateLanguageName: while accessing word '%s', err: %s" % ( strLangName, err ) );
    return getUndefined( nUseLang = nUseLang );        
# translateLanguageName - end
    

def getLangPresent( nUseLang = -1 ):
    """
    Get all lang installed on the system for both tts and asr.
    Remove duplicate !
    - nUseLang: use specific tts language (-1 for current one)
    Return [list_lang,list_lang_in_current_language]
    - list_lang: a list of lang eg: ["French", "Japanese", ...]
    - list_lang_in_current_language: same list but ready to pronunciate, eg: ["Francais", "Japonais", ...]
    """
    
    nUseLang = getLanguageIdx( nUseLang );
    
    import naoqitools
    tts = naoqitools.myGetProxy( "ALTextToSpeech" );
    listLang = tts.getAvailableLanguages();
    print( "getAvailableLanguages: %s" % listLang );    
    listLang = list(set( listLang ));
    print( "getAvailableLanguages (no dup): %s" % listLang );
    listLangTrad = [];
    for strLang in listLang:
        strLangTrad = translateLanguageName( strLang, nUseLang = nUseLang );
        listLangTrad.append( strLangTrad );
    retVal = [ listLang, listLangTrad ];
    print( "INF: abcdk.translate.getLangPresent: returning: %s" % (retVal) );
    return retVal;
# getLangPresent - end

def getTitle( rAge, rGender,  nUseLang = -1 ):
    """
    get "Mister" or "Madam" relative to an age and gender
    param:
    - rAge: from 0 to 200
    - rGender: from -1 to 1  1: man, -1: woman, (0: don't know)
    """
    
    if( abs( rGender ) < 0.4 ):
        dUnknown = {"fr": "humain", "en": "human"};        
        strOut = dUnknown;
    else:
        aText = [
            {"fr": "petit bébé tout mignon", "en": "small baby"}, {"fr": "petite bébé toute mignonne", "en": "small girlie baby"},
            {"fr": "mon enfant","en": "my boy"}, {"fr": "petite fille", "en":"young girl" },
            {"fr": "jeune homme","en": "young man"}, {"fr": "jeune fille", "en": "miss"},
            {"fr": "monsieur", "en": "sir"},{"fr": "madeuhmoiselle", "en": "madam" },
            {"fr": "monsieur", "en": "sir"},{"fr": "madame", "en": "madam" },
            ];
            
        nIdxGender = 0;
        if( rGender < 0. ):
            nIdxGender = 1;
        if( rAge < 3 ):
            strOut = aText[0+nIdxGender];
        elif( rAge < 11 ):
            strOut = aText[2+nIdxGender];
        elif( rAge < 20 ):
            strOut = aText[4+nIdxGender];
        elif( rAge < 30 ):
            strOut = aText[6+nIdxGender];
        else:
            strOut = aText[8+nIdxGender];
    strOut = chooseFromDict( strOut, nUseLang=nUseLang );
    
    return strOut;
# getTitle  - end

def _print_and_assert( waited_result, strTxt ):
    print( strTxt );
    assert( waited_result == strTxt );

def autoTest():
    nUseLang = 1; # french
    _print_and_assert( "blanc", getColor( "White", nUseLang = nUseLang ) );
    _print_and_assert( "gris", getColor( "grey", nUseLang = nUseLang ) );
    _print_and_assert( "mot inconnu", getColor( "caca", nUseLang = nUseLang ) );
    _print_and_assert( "droite", getDirection( "right", nUseLang = nUseLang ) );
    _print_and_assert( "inconnu", getWord( "unknown", nUseLang = nUseLang ) );
    _print_and_assert( "perdu", getWord( "lost", nUseLang = nUseLang ) );
    
    _print_and_assert( "Bonjour", chooseText( ["Hello", "Bonjour", "saluto"], nUseLang = nUseLang ) );
    
    strTitle = getTitle( 20, 0.7, nUseLang = 0 );
    print( strTitle );
    assert( strTitle == "mister" );
    strTitle = getTitle( 20, -0.7, nUseLang = 1 );
    print( strTitle );
    assert( strTitle == "madeuhmoiselle" );    
    strTitle = getTitle( 20, -0.3, nUseLang = 0 );
    print( strTitle );
    assert( strTitle == "human" );        
# autoTest - end

if( __name__ == "__main__" ):
    autoTest();