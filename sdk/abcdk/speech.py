# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Speech tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Speech tools"
print( "importing abcdk.speech" );

import math
import os
import struct
import time
import datetime
import random

import config
import color
import constants
import debug
import filetools
import leds
import naoqitools
import pathtools
import sound
import sound.analyse
import stringtools
import system
import test
import typetools

import mutex

global_mutexSayAndCache = mutex.mutex();

mem = naoqitools.myGetProxy( "ALMemory" );
if( mem != None ):
    mem.raiseMicroEvent( "PleasePauseSpeechRecognition", False ); # so registered box in behavior won't complain
else:
    print( "WRN: ALMemory not found, auto speech recognition won't pause (perhaps)" );

# 18-01-25 Alma: put back lost getSpeakLanguage (todo: find why it disappears)
def getDefaultSpeakLanguage():
  "return the default speak language"
  #return constants.LANG_EN; # TODO: better things ! # CB : gets the real language
  if( not system.isOnNao() ):
    return 0;
  try:
    tts = naoqitools.myGetProxy("ALTextToSpeech");
  except:
    # no tts => anglais
    debug.debug( "WRN: speech.getDefaultSpeakLanguage: no tts found" );
    return constants.LANG_EN;
  if( tts == None ):
    return constants.LANG_EN;
  lang =  tts.getLanguage()
  if lang == "French":
    return constants.LANG_FR;
  else:
    return constants.LANG_EN;  
# getDefaultSpeakLanguage - end

def setSpeakLanguage( nNumLang = getDefaultSpeakLanguage(), proxyTts = False, bChangeAsrAlso = False ):
    """
    change the tts and asr speak language
    Return True or False according to the result of the task
    """
    print( "SetSpeakLanguage to: %d" % nNumLang );
    if( not proxyTts ):
        proxyTts = naoqitools.myGetProxy( "ALTextToSpeech" );
    if( not proxyTts ):
        debug.debug( "ERR: setSpeakLanguage: can't connect to tts" );
        return False;

    try:
        if( nNumLang == constants.LANG_FR ):
            proxyTts.loadVoicePreference( "NaoOfficialVoiceFrench" );            
        elif ( nNumLang == constants.LANG_EN ):
            proxyTts.loadVoicePreference( "NaoOfficialVoiceEnglish" );
        elif ( nNumLang == constants.LANG_SP ):
            proxyTts.loadVoicePreference( "NaoOfficialVoiceSpanish" );
        elif ( nNumLang == constants.LANG_IT ):
            proxyTts.loadVoicePreference( "NaoOfficialVoiceItalian" );
        elif ( nNumLang == constants.LANG_GE ):
            proxyTts.loadVoicePreference( "NaoOfficialVoiceGerman" );
        elif ( nNumLang == constants.LANG_CH ):
            proxyTts.loadVoicePreference( "NaoOfficialVoiceChinese" );
        elif ( nNumLang == constants.LANG_JP ):
            proxyTts.loadVoicePreference( "NaoOfficialVoiceJapanese" );            
        elif ( nNumLang == constants.LANG_PO ):
            proxyTts.loadVoicePreference( "NaoOfficialVoicePolish" );
        elif ( nNumLang == constants.LANG_KO ):
            proxyTts.loadVoicePreference( "NaoOfficialVoiceKorean" );
        elif ( nNumLang == constants.LANG_BR ):
            proxyTts.loadVoicePreference( "NaoOfficialVoiceBrazilian" );            
        elif ( nNumLang == constants.LANG_TU ):
            proxyTts.setLanguage( "Turkish" );
        elif ( nNumLang == constants.LANG_PT ):
            proxyTts.loadVoicePreference( "NaoOfficialVoicePortuguese" );
        else:
            proxyTts.loadVoicePreference( "NaoOfficialVoiceEnglish" );
    except BaseException, err:
        print( "WRN: speech.setSpeakLanguage: current lang number %s is unknown???" % str( nNumLang ) );
        print( "ERR: speech.setSpeakLanguage: loadVoicePreference error: %s" % str(err) );
        print( "INF: speech.setSpeakLanguage: trying a setLanguage" );
        try:
            proxyTts.setLanguage( toSpeakLanguage( nNumLang ) );
        except BaseException, err:
            print( "ERR: speech.setSpeakLanguage: setLanguage, error: %s" % str(err) );
            return False
        
        
    if( bChangeAsrAlso ):
        asr = naoqitools.myGetProxy( "ALSpeechRecognition" );
        if( nNumLang == constants.LANG_BR or nNumLang == constants.LANG_PT or nNumLang == constants.LANG_TU ):
            strLang = toSpeakLanguage( nNumLang );
            if( not strLang in asr.getAvailableLanguages() ):
                print( "WRN: speech.setSpeakLanguage: the asr for lang %d (%s) is not installed, emulating it with french!" % ( nNumLang, strLang ) );
                nNumLang = constants.LANG_FR; # try to emulate them !
        try:
            asr.setLanguage( toSpeakLanguage( nNumLang ) );
        except BaseException, err:
            print( "ERR: speech.setSpeakLanguage: asr.setLanguage, error: %s" % str(err) );
    return True
# setSpeakLanguage - end

def getSpeakLanguage( strLang = "" ):
  "return the current speak language of the synthesis"
  if( strLang == "" ):
    tts = naoqitools.myGetProxy( "ALTextToSpeech", bQuiet = True );
    if( tts == None ):
        return constants.LANG_EN; # default is english!
      
    strLang = tts.getLanguage();
    
  if( strLang ==  "French" ):
    return constants.LANG_FR;
  elif ( strLang ==  "English" ):
    return constants.LANG_EN;
  elif ( strLang ==  "Spanish" ):
    return constants.LANG_SP;
  elif ( strLang ==  "Italian" ):
    return constants.LANG_IT;
  elif ( strLang ==  "German" ):
    return constants.LANG_GE;
  elif ( strLang ==  "Chinese" ):
    return constants.LANG_CH;
  elif ( strLang ==  "Japanese" ):
    return constants.LANG_JP;    
  elif ( strLang ==  "Polish" ):
    return constants.LANG_PO;
  elif ( strLang ==  "Korean" ):
    return constants.LANG_KO;    
  elif ( strLang ==  "Brazilian" ):
    return constants.LANG_BR;   
  elif ( strLang ==  "Turkish" ):
    return constants.LANG_TU;   
  elif ( strLang ==  "Portuguese" ):
    return constants.LANG_PT;
  else:
    print( "WRN: speech.getSpeakLanguage: current language %s is unknown" % str( strLang ) );
    return constants.LANG_EN;
# getSpeakLanguage - end

def getSpeakLangAbbrev():
  """
  return the current speak language of the synthesis using the LangAbbrev ("fr", "jp", ...
  """
  return toLangAbbrev( getSpeakLanguage() );
# getSpeakLangAbbrev - end

def toLangAbbrev( nNumLang ):
    "return the lang abbreviation from a lang number"
    if( nNumLang == constants.LANG_FR ):
        return 'fr';
    if( nNumLang == constants.LANG_EN ):
        return 'en';
    if( nNumLang == constants.LANG_SP ):
        return 'sp';
    if( nNumLang == constants.LANG_IT ):
        return 'it';
    if( nNumLang == constants.LANG_GE ):
        return 'ge';
    if( nNumLang == constants.LANG_CH ):
        return 'ch';
    if( nNumLang == constants.LANG_JP ):
        return 'jp';        
    if( nNumLang == constants.LANG_PO ):
        return 'po';
    if( nNumLang == constants.LANG_KO ):
        return 'ko';
    if( nNumLang == constants.LANG_BR ):
        return 'br';
    if( nNumLang == constants.LANG_TU ):
        return 'tu';
    if( nNumLang == constants.LANG_PT ):
        return 'pt';
    print( "WRN: speech.toLangAbbrev: language number %s is unknown" % str( nNumLang ) );
    return 'en'; # default ?
# toLangAbbrev - end
# print toLangAbbrev( 3 );

def fromLangAbbrev( strLangAbbrev ):
    "return the lang constant from lang abbrevation"
    if( strLangAbbrev == 'fr' ):
        return constants.LANG_FR;
    if( strLangAbbrev == 'en' ):
        return constants.LANG_EN;
    if( strLangAbbrev == 'sp' ):
        return constants.LANG_SP;
    if( strLangAbbrev == 'it' ):
        return constants.LANG_IT;
    if( strLangAbbrev == 'ge' or strLangAbbrev == 'de' ): # we're a bit nice with you !
        return constants.LANG_GE;
    if( strLangAbbrev == 'ch' ):
        return constants.LANG_CH;
    if( strLangAbbrev == 'jp' ):
        return constants.LANG_JP;
    if( strLangAbbrev == 'po' ):
        return constants.LANG_PO;
    if( strLangAbbrev == 'ko' ):
        return constants.LANG_KO;
    if( strLangAbbrev == 'br' ):
        return constants.LANG_BR;
    if( strLangAbbrev == 'tu' ):
        return constants.LANG_TU;
    if( strLangAbbrev == 'pt' ):
        return constants.LANG_PT;        
    print( "WRN: speech.fromLangAbbrev: language abbrev %s is unknown" % str( strLangAbbrev ) );
    return constants.LANG_EN; # default ?
# fromLangAbbrev - end
#print fromLangAbbrev( "it" );

def toSpeakLanguage( nNumLang ):
    "return the language name from a lang number"
    if( nNumLang == constants.LANG_FR ):
        return 'French';
    if( nNumLang == constants.LANG_EN ):
        return 'English';
    if( nNumLang == constants.LANG_SP ):
        return 'Spanish';
    if( nNumLang == constants.LANG_IT ):
        return 'Italian';
    if( nNumLang == constants.LANG_GE ):
        return 'German';
    if( nNumLang == constants.LANG_CH ):
        return 'Chinese';
    if( nNumLang == constants.LANG_JP ):
        return 'Japanese';        
    if( nNumLang == constants.LANG_PO ):
        return 'Polish';
    if( nNumLang == constants.LANG_KO ):
        return 'Korean';
    if( nNumLang == constants.LANG_BR ):
        return 'Brazilian';
    if( nNumLang == constants.LANG_TU ):
        return 'Turkish';
    if( nNumLang == constants.LANG_PT ):
        return 'Portuguese';
    print( "WRN: speech.toSpeakLanguage: language number %s is unknown" % str( nNumLang ) );
    return 'English'; # default ?
# toSpeakLanguage - end
# print toSpeakLanguage( 3 );

def getSpeakLanguageAnsiCode( nNumLang ):
    """
    return the ansi code relative to some ansi code.
    eg: fr => "fr-FR"
    """
    if( nNumLang == constants.LANG_FR ):
        return 'fr-FR';
    if( nNumLang == constants.LANG_EN ):
        return 'en-UK';
    return 'en-UK'; # default ?
# getSpeakLanguageAnsiCode - end    
    

def isLangPresent( nNumLang ):
    "Is lang present in the system"
    strLang = toSpeakLanguage( nNumLang );
    print( "isLangPresent( %s => '%s' ) - called" % (str(nNumLang), strLang ) );
    tts = naoqitools.myGetProxy( "ALTextToSpeech" );
    if( tts != None ):
        if strLang in tts.getAvailableLanguages():
            return True;
    return False;
# isLangPresent - en

def isLangFrench():
  return getSpeakLanguage() == constants.LANG_FR;

def isLangEnglish():
  return getSpeakLanguage() == constants.LANG_EN;

def isLangSpanish():
  return getSpeakLanguage() == constants.LANG_SP;

def isLangItalian():
  return getSpeakLanguage() == constants.LANG_IT;

def isLangGerman():
  return getSpeakLanguage() == constants.LANG_GE;

def isLangChinese():
  return getSpeakLanguage() == constants.LANG_CH;
  
def isLangJapanese():
  return getSpeakLanguage() == constants.LANG_JP; 

def isLangPolish():
  return getSpeakLanguage() == constants.LANG_PO;

def isLangKorean():
  return getSpeakLanguage() == constants.LANG_KO;

def isLangBrazilian():
  return getSpeakLanguage() == constants.LANG_BR;

def isLangTurkish():
  return getSpeakLanguage() == constants.LANG_TU;

def setLangFrench():
  setSpeakLanguage( constants.LANG_FR );

def setLangEnglish():
  setSpeakLanguage( constants.LANG_EN );

def setLangSpanish():
  setSpeakLanguage( constants.LANG_SP );

def setLangItalian():
  setSpeakLanguage( constants.LANG_IT );

def setLangGerman():
  setSpeakLanguage( constants.LANG_GE );

def setLangChinese():
  setSpeakLanguage( constants.LANG_CH );
  
def setLangJapanese():
  setSpeakLanguage( constants.LANG_JP );  

def setLangPolish():
  setSpeakLanguage( constants.LANG_PO );
  
def setLangKorean():
  setSpeakLanguage( constants.LANG_KO );

def setLangBrazilian():
  setSpeakLanguage( constants.LANG_BR );
  
def setLangTurkish():
  setSpeakLanguage( constants.LANG_TU );

def setLangPortuguese():
  setSpeakLanguage( constants.LANG_PT );

def changeLang():
#  if( config.nNumLang == constants.LANG_FR ):
#    config.nNumLang = constants.LANG_EN;
#  else:
#    config.nNumLang = constants.LANG_FR;
    print( "speech.changeLang: TODO reecrire sans utiliser nNumLang" ); # TODO
# changeLang - end

def getVoice():
  "return the current voice of the synthesis"
  tts = naoqitools.myGetProxy( "ALTextToSpeech" );
  strLang = tts.getVoice();
  return strLang;
# getVoice - end

def assumeTextHasDefaultSettings( strTextToSay, nUseLang = -1 ):
    "look if text has voice default params( RSPD, VCT, Vol...) if not, add it, and return it"
    if( nUseLang == -1 ):
        nUseLang = getSpeakLanguage();
        
    if( nUseLang == constants.LANG_CH ):
        return strTextToSay; # current bug => don't add modifiers to this speak languages!
        
    if( nUseLang == constants.LANG_JP ):
        return strTextToSay; # current bug => don't add modifiers to this speak languages!        

    if( strTextToSay.find( "\\RSPD=" ) == -1 ):
        strTextToSay = "\\RSPD=" + str( config.nSpeakSpeed ) + "\\ " + strTextToSay;
    if( strTextToSay.find( "\\VCT=" ) == -1 ):
        strTextToSay = "\\VCT=" + str( config.nSpeakPitch ) + "\\ " + strTextToSay;
    if( strTextToSay.find( "\\VOL=" ) == -1 ):
        strTextToSay = "\\VOL=" + str( config.nSpeakVolume ) + "\\ " + strTextToSay;
    return strTextToSay;
# assumeTextHasDefaultSettings - end


def sayAndCache_getFilename( strTextToSay, nUseLang = -1, strUseVoice = None ):
    "return the filename linked to the sentence to say (using precomputed text)"
    "nUseLang: if different of -1: speak with a specific languages (useful, when text are already generated: doesn't need to swap languages for nothing!"

    # we will generate a string without some specific characters
    # specific characters are all but A-Za-z0-9

    #allchars = "";
    #for i in range( 1, 256):
    #  allchars += ord( i );
    #allcharsbutalphanum = allchars.translate(None, 'abcdefghi ...)

    #  szFilename = strTextToSay.replace( " ", "_" ); # this line cut the compatybility with ALDemo
    #  szFilename = strTextToSay.replace( "\n", "__" ); # this line cut the compatybility with ALDemo
    #  szFilename = szFilename.translate( string.maketrans("",""), ' ,;.?!/\\\'"-:><=' );

    szFilename = "";
    for i in range( len( strTextToSay ) ):
        ch = strTextToSay[i];
        if( ch.isalnum() ):
            szFilename += ch;
        elif( ch == ' ' ):
            szFilename += '_';
        else:
            szFilename += "%X" % ( ord( ch )%16 );

    szFilename = szFilename[:160]; # limit filename to 160 chars
    if( nUseLang == -1 ):
        nUseLang = getSpeakLanguage();
    if( strUseVoice == None ):
        strUseVoice = getVoice();
    szFilename = str( nUseLang ) + '_' + strUseVoice + '_' + szFilename;
    return szFilename;
# sayAndCache_getFilename - end

def sayAndCache_InformPrepare( strUseVoice = None ):
    "inform user we will prepare a text, and that would take sometimes"
    aListTextWait = ["Wait a little I'm preparing what I would say", "Attend un peu, je r�fl�chis a ce que je vais dire" ];
    if( getSpeakLanguage() <= constants.LANG_FR ):
        listTextWait = aListTextWait[getSpeakLanguage()];
    else:
        listTextWait = aListTextWait[constants.LANG_EN];
    sayAndCache_internal( listTextWait, bStoreToNonVolatilePath = True, bWaitEnd = False, strUseVoice = strUseVoice ) # c'est r�cursif, mais si le texte est plus court que la limite, alors c'est ok (render� juste la premiere fois)
# sayAndCache_InformPrepare - end

def sayAndCache_internal( strTextToSay, bJustPrepare = False, bStoreToNonVolatilePath = False, bDirectPlay = False, nUseLang = -1, bWaitEnd = True, bCalledFromSayAndCacheFromLight = False, strUseVoice = None ):
  "generate a text in a file, then read it, next time it will be directly played from that file"
  "bJustPrepare: render the text to a file, but don't play it now"
  "bStoreToNonVolatilePath: copy the generated file to a non volatile path (/usr/generatedvoices)"
  "nUseLang: if different of -1: speak with a specific languages (useful, when text are already generated: doesn't need to swap languages for nothing!"
  "strUseVoice: if different of None or default: use specific voice"
  "return the length of the text in seconds, or None if impossible"
  print( "sayAndCache_internal( '%s', bJustPrepare: %s, bStoreToNonVolatilePath: %s, bDirectPlay: %s, nUseLang: %d, bWaitEnd: %s, bCalledFromSayAndCacheFromLight: %s, strUseVoice: '%s' )" % ( strTextToSay, str( bJustPrepare ), str( bStoreToNonVolatilePath ), str( bDirectPlay ), nUseLang, str( bWaitEnd ), str( bCalledFromSayAndCacheFromLight ), str( strUseVoice ) ) );
  if( not config.bPrecomputeText ):
      print( "sayAndCache: disabled by configuration: bPrecomputeText is false" );
      if( bJustPrepare ):
          return None; # do nothing
      tts = naoqitools.myGetProxy( "ALTextToSpeech" );
      tts.say( strTextToSay );
      return None;
  if( 0 ):
    print( "sayAndCache: FORCING DIRECT_PLAY CAR SINON C'EST BUGGE DANS LA VERSION COURANTE!");  
    bDirectPlay = True;
  
  if( strUseVoice == "default" ):
      strUseVoice = None;
  
  if( config.bRemoveDirectPlay ):
    print( "WRN: DISABLING DIRECT_PLAY SETTINGS for testing/temporary purpose" );
    bDirectPlay = False;  
  
  strTextToSay = assumeTextHasDefaultSettings( strTextToSay, nUseLang );
  szFilename = sayAndCache_getFilename( strTextToSay, nUseLang, strUseVoice );
  
  szPathVolatile = pathtools.getVolatilePath() + "generatedvoices" + pathtools.getDirectorySeparator();
  try:
    os.mkdir( szPathVolatile );
  except BaseException, err:
    pass
  
  
#  if( not szFilename.isalnum() ): # the underscore is not an alphanumeric, but is valid there
#    debug.debug( "WRN: sayAndCache: some chars are not alphanumeric in filename '%s'" % szFilename );
  szPathFilename = szPathVolatile + szFilename + ".raw";
  print( "AAAA Testing existence of '%s' AAAA\n" % szPathFilename );
  bGenerate = not filetools.isFileExists( szPathFilename );
  
  if( bGenerate ):
    szAlternatePathFilename = pathtools.getCachePath() + "generatedvoices" + pathtools.getDirectorySeparator() + szFilename + ".raw"; # look in a non volatile path
    
    if( filetools.isFileExists( szAlternatePathFilename ) ):
      debug.debug( "sayAndCache: get static precomputed text for '%s'" % ( strTextToSay ) );
      filetools.copyFile( szAlternatePathFilename, szPathFilename );
      bGenerate = not filetools.isFileExists( szPathFilename );  #update this variable
    # if alternate
  # if bGenerate
  
  if( bGenerate ):
    # generate it!
    debug.debug( "sayAndCache: generating '%s' to file '%s'" % ( strTextToSay, szPathFilename ) );
    sayAndCache_InformProcess();
    timeBegin = time.time();
    tts = naoqitools.myGetProxy( "ALTextToSpeech" );
    
    nPreviousLanguage = -1;
    if( nUseLang != -1 ):
        nPreviousLanguage = getSpeakLanguage();        
        # change the language to the wanted one
        bRet = setSpeakLanguage( nUseLang );
        if not bRet:
            print( "WRN: sayAndCache_internal: changing lang fail, text won't be said..." )
            return None
    if( len( strTextToSay ) > 150 and ( not bJustPrepare or bCalledFromSayAndCacheFromLight ) ):
        # if it's a long text, we had a blabla to tell the user we will wait (if it's a just prepare from inner, we don't use it)
        sayAndCache_InformPrepare( strUseVoice = strUseVoice );
        
    if( strUseVoice != None ):
        tts.setVoice( strUseVoice );
    
    print( "TTS TO FILE 1 - to %s - BEGIN" % str( szPathFilename ) );
    tts.sayToFile( strTextToSay, szPathFilename );
    print( "TTS TO FILE 1 - END" );
    sayAndCache_InformProcess_end();
    
    if( nPreviousLanguage != -1 ):
        print( "sayAndCache: resetting to previous language (%d) (will arrive only after a generation)" % nPreviousLanguage );
        setSpeakLanguage( nPreviousLanguage );
    
    debug.debug( "sayAndCache: generating text to file - end (tts) - time: %fs" % ( time.time() - timeBegin ) );    
    timeBegin = time.time();
    
    sound.analyse.removeBlankFromFile( szPathFilename );
    debug.debug( "sayAndCache: generating text to file - end (post-process1) - time: %fs" % ( time.time() - timeBegin ) );
    timeBegin = time.time();

    if( bStoreToNonVolatilePath ):
      try:
        os.makedirs( pathtools.getCachePath() + "generatedvoices" + pathtools.getDirectorySeparator());
      except Exception as err:
        print( "DBG: sayAndCache_internal: when trying to create folder, error: %s" % err )
        pass
      szAlternatePathFilename = pathtools.getCachePath() + "generatedvoices" + pathtools.getDirectorySeparator() + szFilename + ".raw"; # a non volatile path
      filetools.copyFile( szPathFilename, szAlternatePathFilename );

    time.sleep( 0.1 ); # pour laisser la synthese souffler un peu (dans les scripts je mettais 300ms)
    debug.debug( "sayAndCache: generating text to file - end (post-process2) - time: %fs" % ( time.time() - timeBegin ) );
    
  statinfo = os.stat( szPathFilename );
  rLength = statinfo.st_size / float(22050*1*2); # sizefile => secondes
    
  if( not bJustPrepare ):
#    debug.debug( "speech::sayAndCache: launching sound now!" );
    if( bWaitEnd ):
        sound.analyseSound_pause( True );
    if( bDirectPlay ):
        nLang = nUseLang;
        if( nLang == -1 ):
            nLang = getSpeakLanguage();
        nFreq = 22050;
        if( nLang == constants.LANG_CH or nLang == constants.LANG_KO ):
            nFreq = 17000; # parce que c'est beau, (ca fait a peu pres du speed a 72%) # todo: ca d�synchronise les yeux qui se lisent trop vite ! argh !
        if( strUseVoice == None ):
            strUseVoice = getVoice();
        if( 'Antoine16' in strUseVoice ):
            nFreq = 16000;
        system.mySystemCall( "aplay -c1 -r%d -fS16_LE -q %s" % ( nFreq, szPathFilename ), bWaitEnd = bWaitEnd );
    else:
        leds = naoqitools.myGetProxy( "ALLeds", True );
        leds.post.fadeRGB( "RightFootLeds", 0xFF0000, 0.7 ); # right in red (skip)
        audioProxy = naoqitools.myGetProxy( "ALAudioPlayer", True );
        # read it in background and check if someone press the right feet a long times => skip text playing
        
        id = audioProxy.post.playFile(szPathFilename);
        if( not bWaitEnd ):
            # attention: no unpause of analyse dans ce cas la!
            return rLength;
        nbrFramesBumpersPushed = 0;
        nbrFramesBumpersPushedMinToSkip = 2;
        strTemplateKeyName = "Device/SubDeviceList/%sFoot/Bumper/%s/Sensor/Value";
        stm = naoqitools.myGetProxy( "ALMemory" );
        while( audioProxy.isRunning( id ) ):
            time.sleep( 0.1 ); # time for user to release precedent push
            listRightFeetBumpers = stm.getListData( [strTemplateKeyName % ( "R", "Left" ), strTemplateKeyName % ( "R", "Right" )] );
            if( listRightFeetBumpers[0] > 0.0 or listRightFeetBumpers[1] > 0.0 ):
                nbrFramesBumpersPushed += 1;
                if( nbrFramesBumpersPushed >= nbrFramesBumpersPushedMinToSkip ):
                    print( "sayAndCache: skipping current text reading because users press on right bumpers" );
                    audioProxy.stop( id );
        leds.post.fadeRGB( "RightFootLeds", 0x000000, 0.2 ); # turn off it
        # while - end
    #if( bDirectPlay ) - end
    sound.analyseSound_resume( True );
  # if( not bJustPrepare ) - end
  print( "sayAndCache_internal: End !!!");
  return rLength;
# sayAndCache_internal - end


def sayAndCache( strTextToSay, bJustPrepare = False, bStoreToNonVolatilePath = False, bDirectPlay = False, nUseLang = -1, bWaitEnd = True, bCalledFromSayAndCacheFromLight = False, strUseVoice = None ):
    "the entry point from external call of sayAndCache"
    "cf sayAndCache_internal for documentation"
    global global_mutexSayAndCache;
    while( global_mutexSayAndCache.testandset() == False ):
        print( "sayAndCache: locked, waiting" );
        time.sleep( 0.5 );

    ret = sayAndCache_internal( strTextToSay, bJustPrepare, bStoreToNonVolatilePath, bDirectPlay, nUseLang, bWaitEnd, bCalledFromSayAndCacheFromLight, strUseVoice );
    global_mutexSayAndCache.unlock();
    return ret;
# sayAndCache - end

def sayAndCacheAndLight( strTextToSay, bJustPrepare = False, bStoreToNonVolatilePath = False, nEyesColor = 0, nUseLang = -1, strUseVoice = None ):
    "say a cached text with light animation"
    "nEyesColor: 0: white, 1: blue, 2: green; 3: red, 4: romeo, 5: use all blue leds of the head (romeonino)"
    "nUseLang: if different of -1: speak with a specific languages (useful, when text are already generated: doesn't need to swap languages for nothing!"
    "strUseVoice: if different of None or default: use specific voice"
    "return the length of the text in seconds, or None if impossible"
    print( "sayAndCacheAndLight( '%s', bJustPrepare: %s, bStoreToNonVolatilePath: %s, nEyesColor: %s, nUseLang: %s )" % ( strTextToSay, str( bJustPrepare ), str( bStoreToNonVolatilePath ), str( nEyesColor ), str( nUseLang ) ) );
    if( not config.bPrecomputeText ):
        print( "sayAndCacheAndLight: disabled by configuration: bPrecomputeText is false" );
        if( bJustPrepare ):
            return None; # do nothing
        tts = naoqitools.myGetProxy( "ALTextToSpeech" );
        tts.say( strTextToSay );
        return None;

    global global_mutexSayAndCache;
    while( global_mutexSayAndCache.testandset() == False ):
        print( "sayAndCacheAndLight: locked, waiting" );
        time.sleep( 0.5 );

    if( strUseVoice == "default" ):
        strUseVoice = None;
        

    rLength = sayAndCache_internal( strTextToSay, bJustPrepare = True, bStoreToNonVolatilePath = bStoreToNonVolatilePath, bDirectPlay = False, nUseLang = nUseLang, bWaitEnd = True, bCalledFromSayAndCacheFromLight = True, strUseVoice = strUseVoice ); # we store it to disk, only if we must do it
    if( rLength == None ):
        print( "INF: sayAndCacheAndLight('%s'): sayAndCache_internal returned None" % str( strTextToSay ) );
        global_mutexSayAndCache.unlock();
        return;

    # this two lines are done too in sayAndCache...
    strTextToSay = assumeTextHasDefaultSettings( strTextToSay, nUseLang );
    szFilename = sayAndCache_getFilename( strTextToSay, nUseLang, strUseVoice = strUseVoice );

    szPathVolatile = pathtools.getVolatilePath() + "generatedvoices" + pathtools.getDirectorySeparator();
    rSampleLenSec = 0.05;
#    szPathFilenamePeak = szPathVolatile + szFilename + ("_%5.3f.egy" % rSampleLenSec);
    szPathFilenamePeak = szFilename + ("_%5.3f.egy" % rSampleLenSec);
    szPathFilenamePeakCache = pathtools.getCachePath() + "generatedvoices" + pathtools.getDirectorySeparator() + szPathFilenamePeak;
    szPathFilenamePeak = szPathVolatile + szPathFilenamePeak;
    anLedsColorSequency = [];
    aBufFile = "";
    bFileGenerated = False;
    if( not filetools.isFileExists( szPathFilenamePeak ) ):
        if( filetools.isFileExists( szPathFilenamePeakCache ) ):
            filetools.copyFile( szPathFilenamePeakCache, szPathFilenamePeak );
    if( not filetools.isFileExists( szPathFilenamePeak ) ):
        # generate peak file
        timeBegin = time.time();
        print( "sayAndCacheAndLight: generating peak light - begin\n" );
        szPathFilename = szPathVolatile + szFilename + ".raw";
        anLedsColorSequency = [];
        try:
            une = naoqitools.myGetProxy( 'UsageNoiseExtractor' );
            anLedsColorSequency = une.analyseSpeakSound( szPathFilename, int( rSampleLenSec * 1000 ), False );
        except BaseException, err:
            print( "ERR: sayAndCacheAndLight( '%s' ): err: %s" % ( strTextToSay, str( err ) ) );
            print( "ERR: sayAndCacheAndLight => trying old cpp version" );
            anLedsColorSequency = sound.analyseSpeakSound( szPathFilename, rSampleLenSec * 1000 );
        print( "sayAndCacheAndLight: analyseSpeakSound - end - time: %fs\n" % float( time.time() - timeBegin ) );        
#        print( "anLedsColorSequency: %d samples: %s\n" % ( len( anLedsColorSequency ), str( anLedsColorSequency ) ) );
        
        print( "Writing file with %d peak samples (time: %d)\n" % ( len( anLedsColorSequency ), int( time.time() ) ) );
        #         struct.pack_into( "f"*len( anLedsColorSequency ), aBufFile, anLedsColorSequency[:] );
        for peakValue in anLedsColorSequency:
            aBufFile += struct.pack( "f", peakValue );
        try:
            file = open( szPathFilenamePeak, "wb" );
            file.write( aBufFile );
        except RuntimeError, err:
            print( "ERR: sayAndCacheAndLight( '%s' ): err: %s" % ( strTextToSay, str( err ) ) );
        print( "sayAndCacheAndLight: Written file with a size of %d in '%s'" % ( len( aBufFile ), szPathFilenamePeak ) );
        file.close();
        if( bStoreToNonVolatilePath ):
            filetools.copyFile( szPathFilenamePeak, szPathFilenamePeakCache );
        bFileGenerated = True;
        print( "sayAndCacheAndLight: generating peak light - end - time: %fs\n" % float( time.time() - timeBegin ) );
    else:
        if( not bJustPrepare ):
            # read it
            print( "Reading file containing peak samples" );
            try:
                file = open( szPathFilenamePeak, "rb" );
            except RuntimeError, err:
                print( "ERR: sayAndCacheAndLight( '%s' ): err: %s" % ( strTextToSay, str( err ) ) );
                global_mutexSayAndCache.unlock();
                return None;
            try:
                aBufFile = file.read();
                print( "aBufFile len: %d" % len( aBufFile ) );
                nNbrPeak = len( aBufFile ) / struct.calcsize("f");
                anLedsColorSequency = struct.unpack_from( "f"*nNbrPeak, aBufFile );
            finally:
                file.close();

    if( bJustPrepare ):
        global_mutexSayAndCache.unlock();
        return rLength;
        
#    anLedsColorSequency += (0.05,); # a la fin on laisse les leds un peu allum� (non c'est trop abrupte a voir par ailleurs)
    print( "sending leds order, len: %d" % len( anLedsColorSequency ) );

    bFirst = True;
    if( False ):
        # avec methode postQueueOrders
        strLedsGroup = 'FaceLeds';
        if( nEyesColor == 1 ):
            strLedsGroup = 'AllLedsBlue'; # 'FaceLedsBlue'; mais ca n'existe pas!
        elif( nEyesColor == 2 ):
            strLedsGroup = 'AllLedsGreen';
        elif( nEyesColor == 3 ):
            strLedsGroup = 'AllLedsRed';
        aListOrder = [];
        aListOrder.append( "ALLeds = ALProxy( 'ALLeds')" );
        for value in anLedsColorSequency:
            if( bFirst ):
                bFirst = False;
                rTime = 0.;
            else:
                rTime = 0.02;
            aListOrder.append( "ALLeds.setIntensity( '%s', %f, %f )" % ( strLedsGroup, value, rTime ) );
        aListOrder.append( "ALLeds.fadeRGB( '%s', 0x101010, 0.2 )" % strLedsGroup ); # a la fin on laisse les leds un peu allum�
        postQueueOrders( aListOrder, rSampleLenSec - 0.02 + 0.016 );
    else:
        aRGB = [];
        aTime = [];

        rRegularTimePerEnlightment = rSampleLenSec - 0.00120;
        
        if( strUseVoice == None ):
            strUseVoice = getVoice();
        if( 'Antoine16' in strUseVoice ):
            rRegularTimePerEnlightment = ( ( rSampleLenSec * 22050 ) / 16000 );
        
        for value in anLedsColorSequency:
            nValue = int( 0xff * value );
            if( nEyesColor == 1 ):
                pass # nValue = nValue
            elif( nEyesColor == 2 ):
                nValue = nValue << 8;
            elif( nEyesColor == 3 ):
                nValue = nValue << 16;
            #~ elif( nEyesColor == 4 ):
                #~ nValue = int( 0xff * value ); # Roméo
            else:
                nValue = (nValue << 16) | (nValue << 8) | (nValue);
#            print( "0x%s" % nValue );
            aRGB.append( nValue );
            if( bFirst ):
                bFirst = False;
                aTime.append( 0.00 ); # En fait pour le premier coup, on le veut maintenant !
            else:                
                aTime.append( rRegularTimePerEnlightment );
#        aRGB = [ 0xFFFFFF, 0xFF, 0xFF00, 0xFF0000 ];
#        aTime = [1.0, 1.0, 1.0,1.0];
        aRGB.append( 0x101010 ); # a la fin on laisse les leds un peu allum�
        aTime.append( 0.2 );
#        print( "aRGB: %s" % str( aRGB ) );
#        print( "aTime: %s" % str( aTime ) );
        leds = naoqitools.myGetProxy( 'ALLeds');
        if( nEyesColor == 4 ):
            # romeo
            leds.post.fadeListRGB( 'LeftFaceLed5', aRGB, aTime );
            leds.post.fadeListRGB( 'LeftFaceLed6', aRGB, aTime );
            leds.post.fadeListRGB( 'LeftFaceLed7', aRGB, aTime );
        if( nEyesColor == 5 ):
            # romeonino
            leds.post.fadeListRGB( 'EarLeds', aRGB, aTime );
            leds.post.fadeListRGB( 'BrainLeds', aRGB, aTime );
            leds.post.fadeListRGB( 'FaceLeds', aRGB, aTime );            
        else:
            leds.post.fadeListRGB( 'FaceLedsExternal', aRGB, aTime );
    # if test methods - end
    rLength = sayAndCache_internal( strTextToSay, bJustPrepare = False, bStoreToNonVolatilePath = False, bDirectPlay = True, nUseLang = nUseLang, bWaitEnd = True, bCalledFromSayAndCacheFromLight = False, strUseVoice = strUseVoice );
    
    if( not bStoreToNonVolatilePath and bFileGenerated ):
        # cleaning file !
        #nothing to do, we don't create it in a hard place
        # os.unlink( szPathFilenamePeak );
        # os.unlink( pathtools.getCachePath() + "generatedvoices" + pathtools.getDirectorySeparator() + szFilename + ".raw" );
        pass
    # if - end
    
    global_mutexSayAndCache.unlock();
    return rLength;
    
# sayAndCacheAndLight - end

def sayAndCache_InformProcess():
    "set a peculiar color in eyes before rendering sound"
    leds = naoqitools.myGetProxy( "ALLeds" );
    for i in range( 4 ):
        leds.post.fadeRGB( 'FaceLed' + str( i*2 ), 0xFF00, 0.1 );
        leds.post.fadeRGB( 'FaceLed' + str( i*2+1 ), 0x00FF, 0.1 );
# sayAndCache_InformProcess - end

def sayAndCache_InformProcess_end():
    "set a peculiar color in eyes before rendering sound"
    leds = naoqitools.myGetProxy( "ALLeds" );
    leds.post.fadeRGB( 'FaceLeds', 0x8080FF, 0.1 );
# sayAndCache_InformProcess - end
    

def sayAndCache_launchBackgroundPlay( strTextToSay, bJustPrepare = False, nUseLang = -1 ):
    """
    updated version to be used with bodytalk
    return an ID of AudioPlay task or 0 if just prepared
    nUseLang: an number as a lang constant or a "xx" country code
    """
    
    strTextToSay = assumeTextHasDefaultSettings( strTextToSay, nUseLang );
    
    if typetools.isString(nUseLang):
        if nUseLang == "":
            nUseLang = -1
        else:
            nUseLang = fromLangAbbrev( nUseLang )
    
    
    rRet = sayAndCache( strTextToSay = strTextToSay, bJustPrepare = True, nUseLang = nUseLang, bStoreToNonVolatilePath = True )
    print( "INF: sayAndCache_launchBackgroundPlay: sayAndCache success: %s" % str(rRet) )
    if  bJustPrepare or rRet == None:
        return 0
    ap = naoqitools.myGetProxy("ALAudioPlayer")
    filename = sayAndCache_getFilename( strTextToSay, nUseLang = nUseLang )
    completename = pathtools.getCachePath() + "generatedvoices" + pathtools.getDirectorySeparator() + filename + ".raw"
    print( "INF: sayAndCache_launchBackgroundPlay: playing file %s" % completename )
    id = ap.post.playFile( completename )
    return id

def sayMumbled( strText ):
    sayAndCache( strText, bJustPrepare = True );
    strText = assumeTextHasDefaultSettings( strText );
    szFilename = sayAndCache_getFilename( strText );
    szPathFilename = pathtools.getVolatilePath() + "generatedvoices" + pathtools.getDirectorySeparator() + szFilename + ".raw";
    szProcessed = szPathFilename + "_mumbled.raw";
    if( not processSoundMumbled( szPathFilename, szProcessed ) ):
        return False;
    nFreq = 22050;
    system.mySystemCall( "aplay -c1 -r%d -fS16_LE -q %s" % ( nFreq, szProcessed ) );    
    return True;
# sayMumbled - end
    


def uiSay( strText ):
    strSpeed = "\\RSPD=%d\\ " % config.nSpeakSpeedUI;
    sayAndCache( strSpeed + strText, bJustPrepare = False, bStoreToNonVolatilePath = True ); 
# uiSay - end

global_bSpeechHasBeenChanged = False;
def setSpeakSpeed( nNewSpeed = 100 ):
    print( "abcdk.speech.setSpeakSpeed: changing speak speed from %d to %s" % (config.nSpeakSpeed, nNewSpeed ) );
    config.nSpeakSpeed = nNewSpeed;    
    global global_bSpeechHasBeenChanged;
    global_bSpeechHasBeenChanged = True;
# setSpeakSpeed - end

def changeSpeakSpeed( nRelativeSpeed ):
    setSpeakSpeed( config.nSpeakSpeed + nRelativeSpeed );
# changeSpeakSpeed - end    
    

def insertPauseInSpace( strTxt, nPauseTimeMs = 100 ):
    """
    Take a text and add a small pause in each space
    """
    if( len(strTxt) < 2 ):
        return strTxt;
        
    strTxtOut = strTxt[:2];
    for i in range( 2, len( strTxt )-1 ):
        if( strTxt[i] == ' ' and strTxt[i-2] != '\\' and strTxt[i-1] != '\\' and strTxt[i+1] != '\\' ):
            strTxtOut += "\\PAU=%d\\ " % nPauseTimeMs;
        else:
            strTxtOut += strTxt[i];
    return strTxtOut + strTxt[-1];
# insertPauseInSpace - end

def emulateVoiceForRomeo():
    """
    Simulate a low pitched voice using the standard voice
    """
    global global_bSpeechHasBeenChanged
    global_bSpeechHasBeenChanged = True;
    # then in getTextWithCurrentSpeed, the romeo patch would be applied

def getTextWithCurrentSpeed( strTxt ):
    """
    Take a text and apply the current speed config
    """
    strTxt = str(strTxt);
    global global_bSpeechHasBeenChanged;
    if( not global_bSpeechHasBeenChanged ):
        return strTxt; # no change at all (seems like we don't want to use this feature)
       
    #~ print( "DBG: abcdk.speech.getTextWithCurrentSpeed: received: %s" % strTxt );
    nSpeed = config.nSpeakSpeed;
    nAddSpace = 0;
    if( nSpeed < 50 ):
        strTxt = insertPauseInSpace( strTxt, (50-nSpeed)*10 );
        #~ print( "DBG: abcdk.speech.getTextWithCurrentSpeed: after insert space: %s" % strTxt );        
        nSpeed = 50;
        
    # find for the last RSPD command, and integrate our speed after the asked one
    idx = strTxt.rfind( "RSPD" );
    if( idx != -1 ):
        # find last slash
        idx = strTxt[idx:].find( "\\ " ) + idx;        
        if( idx != -1 ):
            idx += 2; # skip the slash and the space
            strTxtOut = strTxt[:idx] + ( "\\RSPD=%d\\ " % nSpeed ) + strTxt[idx:];
    if( idx == -1 ):
        # no speed command or weird stuffs, trying standard way
        strTxtOut = ( "\\RSPD=%d\\ " % nSpeed ) + strTxt;
    #~ print( "DBG: abcdk.speech.getTextWithCurrentSpeed: at end: %s" % strTxtOut );
    
    # change for Romeo
    if( True ):
        if( system.isOnRomeo() and getSpeakLanguage() != constants.LANG_FR ): # in french we already have the good voice
            # change voice to match romeo shape
            nNewPitch = 50;
            # find for the last VCT command, and integrate our VCT after the asked one
            idx = strTxt.rfind( "VCT" );
            if( idx != -1 ):
                # find last slash
                idx = strTxt[idx:].find( "\\ " ) + idx;
                if( idx != -1 ):
                    idx += 2; # skip the slash and the space
                    strTxtOut = strTxt[:idx] + ( "\\VCT=%d\\ " % nNewPitch ) + strTxt[idx:];
            if( idx == -1 ):
                # no speed command or weird stuffs, trying standard way
                strTxtOut = ( "\\VCT=%d\\ " % nNewPitch ) + strTxt;
    print( "getTextWithCurrentSpeed: strTxt: '%s', strTxtOut: '%s'" % (strTxt, strTxtOut ) );
    return strTxtOut;
# getTextWithCurrentSpeed - end

global_mutexSayAndLight = mutex.mutex();

def sayAndLight( strText, nLightType = 0 , bUseDisplay = True):
    """
    Simple say with random light in eyes (or mouth depending of the robot)
    - nLightType: style of light to set on NAO
        - 0: subtil leds (eyes)
        - 1: eyes + lighten ears and brain
        - 2: just ears and brain
    return: True if ok or False if problem, aborted or ...
    """
    while( global_mutexSayAndLight.testandset() == False ):
        print( "sayAndLight: already used, waiting..." );
        time.sleep( 0.5 );
    if bUseDisplay :
      import html_manager
      html_manager.showHTMLWrite(strText, "Center","Letter") 

    mem = naoqitools.myGetProxy( "ALMemory" );
    mem.raiseMicroEvent( "Speaking", 1 )
    
    strText = getTextWithCurrentSpeed( strText );
    tts = naoqitools.myGetProxy( "ALTextToSpeech" );
    if tts != None:
        id = tts.post.say( strText );
    if( nLightType > 0 ):
        leds.ledsDcm.setBrainLedsIntensity( 1., 100, bDontWait = True );
        leds.ledsDcm.setEarsLedsIntensity( 1., 100, bDontWait = True );
    rPeriod = 0.2;
    bStop = False;
    global global_bMustStopSay;
    global_bMustStopSay = False;
    bAborted = False;
    nBaseColor = leds.getFavoriteColorEyes();
    #~ print( "nBaseColor = 0x%x" % nBaseColor );
    bOnRomeo = system.isOnRomeo();
    timeBegin = time.time();  
    while( not bStop and not bAborted ):
        # nIntensity = random.randint(0,255) + ( random.randint(0,255) <<8 ) + ( random.randint(0,255) << 16 );
        if( nLightType < 2 ):
            nColor = color.interpolateColor( nBaseColor, 0xFFFFFF, random.random()/2 );
            #~ print( "nColor = 0x%x" % nColor );
            if( bOnRomeo ):
                #~ leds.setMouthLeds( [nColor]*3, rPeriod );
                if( random.random() > 0.7 ):
                    nColor = 0;
                else:
                    nColor = random.randint(10,0xFF)
                leds.ledsDcm.setMouthColor( rPeriod, nColor );
            else:            
                leds.ledsDcm.setEyesColor( rPeriod, nColor );
        time.sleep( rPeriod );
        if( global_bMustStopSay ):
            try:
                tts.stop( id );
            except BaseException, err:
                print( "ERR: abcdk.sayAndLight, but perhaps normal: %s" % str(err) );                
            bAborted = True;
        try:
            bStop = not tts.isRunning( id );
        except BaseException, err:
            print( "ERR: abcdk.sayAndLight, but perhaps normal: %s" % str(err) );
            bStop = True;  # task has disappeard
        rDuration = time.time() - timeBegin;
        if( rDuration > 3 and rDuration > len( strText ) / 5. ): # too much time !!!
            print( "ERR: abcdk.sayAndLight: BIG PROBLEM: tts takes too much time to release, killing it! (sentence: %s, len: %s, time taken: %5.2fs)" % ( strText, len(strText), rDuration ) );
            bAborted = True;
            tts.stopAll(); # brutal request!
    # while - end
    if( nLightType > 0 ):
        leds.ledsDcm.setBrainLedsIntensity( 0., 100, bDontWait = True );
        leds.ledsDcm.setEarsLedsIntensity( 0., 100, bDontWait = True );
    if( nLightType < 2 ):
        leds.setFavoriteColorEyes( False );
    if( bOnRomeo ):
        leds.ledsDcm.setMouthColor( 0.4, 0 );
    mem.raiseMicroEvent( "Speaking", 0 )
    global_mutexSayAndLight.unlock();
    return not bAborted;
# sayAndLight - end

def stopSay():
    # we stop all abcdk.speech
    global global_bMustStopSay;
    global_bMustStopSay = True;
# stopSay - end

def transcriptFloat( rVal, nUseLang = -1 ):
    "convert a float into a speechable string "
    "5.3 => '5 point 3'"
    "- nUseLang: the lang to use, or -1 to use current language"
    if( nUseLang == -1 ):
        nUseLang = getSpeakLanguage();
    nPart1 = int( rVal );
    if( nPart1 < 0 ):
        strSign = "-";
        nPart1 = -nPart1;
    else:
        strSign = "";    
    nMultiplicatorForPrecision = 1000000000;
    nPart2 = round( ( abs(rVal) - nPart1 ) * nMultiplicatorForPrecision );
    nSignifiantZero = 0;
    if( nPart2 == 0 ):
        return "%s %d" % ( strSign, nPart1 );
    while( nPart2 * math.pow( 10, nSignifiantZero ) < nMultiplicatorForPrecision ):
        nSignifiantZero += 1;
    nSignifiantZero -= 1;
    while( nPart2 % 10 == 0 and nPart2 > 0 ):
        nPart2 /= 10;
    #~ print( "modf: " + str( math.modf( rVal ) ) );
    #~ print( "trunc: " + str( math.trunc( rVal ) ) );
    strSignifiantZero = "zero " * nSignifiantZero;
    if( nUseLang == constants.LANG_FR  ):
        strPoint = "virgule";
    else:
        strPoint = "point";
    return "%s %d %s %s%d" % ( strSign, nPart1, strPoint, strSignifiantZero, nPart2 );
# transcriptFloat - end

def getWeekDayLibelle_Fr():
    return [ "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche" ];
# getWeekDayLibelle_Fr

def getWeekDayLibelle_En():
    return [ "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday" ];
# getWeekDayLibelle_En


def transcriptWeekDay( nNumDay, nUseLang = -1 ):
    "return the name of the week day"
    "nNumDay: 0=monday, ..., 6=sunday, as returned by datetime.date.today().weekday()"
    "nUseLang: the lang to use, or -1 to use current language"
    if( nUseLang == -1 ):
        nUseLang = getSpeakLanguage();
    listName = getWeekDayLibelle_En();
    if( nUseLang == constants.LANG_FR  ):
        listName = getWeekDayLibelle_Fr();
    if( nNumDay>= 6 or nNumDay < 0 ):
        nNumDay = nNumDay % 7;
    return listName[nNumDay];
# transcriptWeekDay - end
# print transcriptWeekDay( 0 );

def getMonthLibelle_Fr():
    return [ "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Aout", "Septembre", "Octobre", "Novembre", "Décembre" ];
# getMonth_Fr

def getMonthLibelle_En():
    return [ "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December" ];
# getMonthLibelle_En


def  getDayPerMonth( nMonth ):
    # TODO: handle we are the 30 and tomorrow is 1.  We choose to handle 31, because it's the only safe test with no false positif.
    listDay = [ 31, 28, 31, 30, 31, 30,       31, 31, 30, 31, 30,31];
    return listDay[nMonth+1];
# getDayPerMonth - end    

def getDayLibelle_En( nNum ):
    if( nNum == 11 or nNum == 12 or nNum == 13 ):
        return str( nNum ) + 'th';
    
    if( nNum%10 == 1  ):
        return str( nNum ) + 'st';
    if( nNum%10 == 2 ):
        return str( nNum ) + 'nd';
    if( nNum%10 == 3 ):
        return str( nNum ) + 'rd';
    return str( nNum ) + 'th';
# getDayLibelle_En

def decodeDate( strDate ):
    "extract int from string date"
    "strDate: 'YYYY/MM/DD'"
    "output [nYear, nMonth, nDay]"
    nYear = stringtools.findNumber( strDate );
    nMonth = stringtools.findNumber( strDate[strDate.find('/'):] );    
    nDay= stringtools.findNumber( strDate[strDate.rfind('/'):] );
    return [ nYear, nMonth, nDay ];
# decodeDate - end

def decodeTime( strTime ):
    "extract int from string date"
    "strDate: 'HH:MM:SS'"
    "output [nHour, nMin, nSec]"
    
    nHour = stringtools.findNumber( strTime );
    nMin = 0;
    nSec = 0;
    idxMin = strTime.find(':');
    if( idxMin != -1 ):
        nMin = stringtools.findNumber( strTime[idxMin:] );    
        idxSec = strTime.find(':', idxMin+1 );
        if( idxSec != -1 ):
            nSec = stringtools.findNumber( strTime[idxSec:] );
    return [nHour, nMin, nSec];
# decodeTime- end


def transcriptDate( strDate, nUseLang = -1, bSmart = False ):
    "convert a date into a speechable string "
    "'2008/12/31' => '31 Décembre 2008'"
    "'2008/12/31' => '31 December 2008'"
    "'2008/12'    => 'December 2008'"
    "nUseLang: the lang to use, or -1 to use current language"
    "Hint: in python the formatting is: it's datetime.datetime.now().strftime( '%Y/%m/%d' )"
    
    nYear = stringtools.findNumber( strDate );
    nMonth = stringtools.findNumber( strDate[strDate.find('/'):] );    
    nDay= stringtools.findNumber( strDate[strDate.rfind('/'):] );
    if( nYear > 2000 ):
        if( strDate.find('/') == strDate.rfind('/') ):
            # a year and no day, so we are in a month and year only
            nDay = 99;
    if( nUseLang == -1 ):
        nUseLang = getSpeakLanguage();
    strOut = "";    
    if( bSmart and int( time.strftime("%Y") ) == nYear ):
        bSameYear = True;
        strYear = "";    
    else:
        bSameYear = False;
        strYear = str( nYear );
    if( bSmart and int( time.strftime("%m") ) == nMonth and bSameYear ):
        bSameMonth = True;
        strMonth = "";    
    else:
        bSameMonth = False; # can't have same month if not same year
        if( nUseLang == constants.LANG_FR  ):    
            strMonth = getMonthLibelle_Fr()[nMonth-1];
        else:
            strMonth = getMonthLibelle_En()[nMonth-1];
               
    #~ nTomorrow = int( time.strftime("%d") ) + 1;
    #~ nDayThisMonth = getDayPerMonth( int( time.strftime("%m") ) );
    #~ if( nTomorrow > nDayThisMonth ): 
        #~ nTomorrow -= (nDayThisMonth - 1); # day 0 is actually 1.
    #~ print( "nTomorrow: %d (nDayThisMonth:%d)" % ( nTomorrow, nDayThisMonth ) );
    
    tomorrow = datetime.datetime.now() + datetime.timedelta( 1 );
    nTomorrow = int( tomorrow.strftime("%d")  );
#    print( "nTomorrow: %d" % ( nTomorrow ) );
    
    aftertomorrow = datetime.datetime.now() + datetime.timedelta( 2 );
    nAfterTomorrow = int( aftertomorrow.strftime("%d")  );
#    print( "nAfterTomorrow: %d" % ( nAfterTomorrow ) );
    
    if( bSmart ):
        if( int( time.strftime("%d") ) == nDay and bSameMonth ):
            strDay = "";    
        elif( nTomorrow == nDay and bSameMonth ):
            strMonth = "";
            if( nUseLang == constants.LANG_FR  ):
                strDay = "demain";
            else:
                strDay = "tomorrow";
        elif( nAfterTomorrow == nDay and bSameMonth ):
            strMonth = "";
            if( nUseLang == constants.LANG_FR  ):
                strDay = "après-demain";
            else:
                strDay = "the day after tomorrow";
        else:
            bSmart = False; # so we have to set the day
    if( not bSmart ):        
        if( nUseLang == constants.LANG_FR  ):            
            strDay = str( nDay );
        else:
            strDay = getDayLibelle_En( nDay );

    if( nDay == 99 ):
        strDay = "";
    # strOut = getMonthLibelle_En()[nMonth-1] + ", " + getDayLibelle_En( nDay ) + ' ' + strYear;
    strOut =  strDay + ' ' +  strMonth + ' ' + strYear
    
    return strOut;
# transcriptDate - end

# print( "transcriptDate:" + transcriptDate( "2011/10/02", bSmart = True ) );
# print( "transcriptDate:" + transcriptDate( "2011/10", bSmart = False ) );


def transcriptTime( strTime, nUseLang = -1, bAddOClock = True, bSmart = False ):
    """
    convert a time into a speechable string (english and french)
    '15:00:00' => '15 o'clock'
    - nUseLang: the lang to use, or -1 to use current language
    - bAddOClock: if false, won't add O'Clock, nor pile
    - bSmart: if True, don't speak too much
    
    Hint: in python the formatting is: it's datetime.datetime.now().strftime( '%H:%M:%S' )
    
    """
    
    nHour = stringtools.findNumber( strTime );
    nMin = 0;
    nSec = 0;
    idxMin = strTime.find(':');
    if( idxMin != -1 ):
        nMin = stringtools.findNumber( strTime[idxMin:] );    
        idxSec = strTime.find(':', idxMin+1 );
        if( idxSec != -1 ):
            nSec = stringtools.findNumber( strTime[idxSec:] );    
            
    if( nUseLang == -1 ):
        nUseLang = getSpeakLanguage();
    strOut = "";
    if( nUseLang == constants.LANG_FR  ):
        if( nHour == 0 ):
            strHour = "minuit";
        elif( nHour == 12 ):
            strHour = "midi";
        else:
            strHour = str( nHour ) + " heures";
        
        if( nMin != 0 ):
            strMin = " " + str( nMin );
        else:
            if( bAddOClock ):
                strMin = " pile";
            else:
                strMin = "";
            
        strSec = "";
        if( nSec != 0 and not bSmart ):
            strSec = " et " + str( nSec ) + " secondes";
            
    else:

        bNumbers = False;
        if( nHour == 0 and nMin == 0 ):
            strHour = "midnight";
        elif( nHour == 12 and nMin == 0 ):
            strHour = "noon";            
        else:
            bNumbers = True;
            bPM = False;
            if( nHour >= 12 ):
                if( nHour != 12 ):
                    nHour -= 12;
                bPM = True;
            strHour = str( nHour );
        
        if( nMin != 0 ):
            if( nMin < 10 ):
                strMin = " o " + str( nMin );
            else:
                strMin = " " + str( nMin );
        else:
            if( not nHour in [0,12] and bAddOClock ):
                strMin = " o'clock";
            else:
                strMin = "";
            
        strSec = "";
        if( nSec != 0 and not bSmart ):
            strSec = " and " + str( nSec ) + " seconds";
        if( bNumbers ):
            if( bPM ):
                strSec += " PM";
            else:
                strSec += " AM";
    # english
    strOut = strHour + strMin + strSec;

    return strOut;
# transcriptTime - end
#~ print transcriptTime( "15:05", 0 );
#~ print transcriptTime( "12", 0 );
#~ print transcriptTime( "11", 0 );
#~ print transcriptTime( "11", 0, bAddOClock = False );
#~ print transcriptTime( "09:05", 0 );

def getTimeDelay( strDate, strTime ):
    "return a delay in seconds between a date/time and now!"
    "TODO: optimise?" "to move outside this modules?"
    # class datetime.timedelta([days[, seconds[, microseconds[, milliseconds[, minutes[, hours[, weeks]]]]]]])
    now = datetime.datetime.today();
    
    nYear, nMonth, nDay = decodeDate( strDate );
    nHour, nMin, nSec = decodeTime( strTime );
    
    ourDateTime = datetime.datetime( nYear, nMonth, nDay, nHour, nMin, nSec );
    td = datetime.timedelta( days = ourDateTime.day - now.day, hours = ourDateTime.hour - now.hour, minutes = ourDateTime.minute - now.minute );
    nTotalSeconds = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6; # total_seconds is in python 2.7
    nTotalSeconds += ( ourDateTime.month - now.month ) *31*24*3600; # roughly...
    nTotalSeconds += ( ourDateTime.year - now.year ) *365*24*3600; # roughly...
    return nTotalSeconds;
# getTimeDelay - end
# print( "getTimeDelay: " + str( getTimeDelay( "2013/11/15", '16:00:00' ) ) );

def transcriptDateTime( strDate, strTime, nUseLang = -1, bSmart = False ):
    "convert a date (YYYY/MM/DD) and time (HH:MM:SS) into a speechable string "
    "bSmart:"
    "  don't specify date if it's today"
    "  don't specify year, if this year"
    "  don't specify month, if this month" # although...
    
    if( nUseLang == -1 ):
        nUseLang = getSpeakLanguage();
        
    nDurationSec = getTimeDelay( strDate, strTime );        
    
    if( bSmart and strDate == time.strftime("%Y/%m/%d")  ):
        strDate = "";
    else:
        strDate = transcriptDate( strDate, nUseLang = nUseLang, bSmart =  bSmart );
    strTime = transcriptTime( strTime, nUseLang = nUseLang, bSmart = bSmart );
    
    if( nUseLang == constants.LANG_FR  ):
        if( strDate == "" ):
            if( nDurationSec < 30 ):
                aText = ["maintenant", "grouilles toi", "vite, c'est maintenant", "tout de suite"];
                return aText[random.randint(0,len(aText)-1)];
            elif( nDurationSec < 60*10 ):
                aText = ["dans %d minute", "précisément dans %d minute", "dans pas moins de %d minute", "dans %d marsupilami"];
                return aText[random.randint(0,len(aText)-1)] % ( nDurationSec / 60 );
            return "a %s" % strTime;
        if( strDate[0].isalpha() ):
            return "%s a %s" % ( strDate, strTime );
        return "le %s a %s" % ( strDate, strTime );
    
    # every other language => english
    if( strDate == "" ):
        return "at %s" % strTime;
    if( strDate[0].isalpha() ):
        return "%s at %s" % ( strDate, strTime );
    return "the %s at %s" % ( strDate, strTime );
# transcriptDateTime - end
#~ print( transcriptDateTime( "2013/11/16", "15:00:00", nUseLang = 1, bSmart = True ) );

def transcriptDateTimeObj( objDateTime, nUseLang = -1, bSmart = False ):
    "convert a datetime object into a speechable string "
    "see transcriptDateTime for details"
    strDate = "%d/%02d/%02d" % (objDateTime.year, objDateTime.month, objDateTime.day);
    strTime = "%d:%d:%d" % ( objDateTime.hour, objDateTime.minute, objDateTime.second );
    return transcriptDateTime( strDate, strTime, nUseLang = nUseLang, bSmart = bSmart );
# transcriptDateTime - end


def transcriptDuration( rTimeSec, nUseLang = -1, bSmart = False, nSmartLevel = 2 ):
    """
    convert a duration into a speechable string 
    rTimeSec: time in seconds
    bSmart: limit output to be short
    nSmartLevel: when bSmart: choose the number of information to output
    """
    strOut = "";
    nLastOutputtedUnit = 1000;

    # we will limit to 2 values
    nCptValue = 0;
    nMaxValue = 16;
    if( bSmart ):
        nMaxValue = nSmartLevel;

    if( nUseLang == -1 ):
        nUseLang = getSpeakLanguage();
        
    astrUnitsPerLang = [
        ["milliseconde", "millisseconde"],
        ["seconde", "seconde"],
        ["minute", "minute"],
        ["hour", "heure"],
        ["day", "jour"],
        ["month", "mois"],
    ];
        
    if( rTimeSec < 0.001 ):
        return "0 %s" % astrUnitsPerLang[0][nUseLang];

    nDividend = 60*60*24*30; # 30 day per month as an average!
    if( rTimeSec >= nDividend and nCptValue < nMaxValue ):
        nVal = int( rTimeSec / nDividend );
        strUnit = astrUnitsPerLang[5][nUseLang];
        #~ if( nVal >= 2. ): # don't add 's' for mois nor months
            #~ strUnit += 's';        
        strOut += "%d %s " % ( nVal,  strUnit );
        rTimeSec -= nVal * nDividend;
        nCptValue += 1;
        nLastOutputtedUnit = 0;

    nDividend = 60*60*24;
    if( rTimeSec >= nDividend and nCptValue < nMaxValue and ( nLastOutputtedUnit > -1 or not bSmart ) ):
        nVal = int( rTimeSec / nDividend );
        strUnit = astrUnitsPerLang[4][nUseLang];
        if( nVal >= 2. ):
            strUnit += 's';        
        strOut += "%d %s " % ( nVal , strUnit );
        rTimeSec -= nVal * nDividend;
        nCptValue += 1;
        nLastOutputtedUnit = 1;
        
    nDividend = 60*60;
    if( rTimeSec >= nDividend and nCptValue < nMaxValue and ( nLastOutputtedUnit > 0 or not bSmart ) ):
        nVal = int( rTimeSec / nDividend );
        strUnit = astrUnitsPerLang[3][nUseLang];
        if( nVal >= 2. ):
            strUnit += 's';
        strOut += "%d %s " % ( nVal , strUnit );
        rTimeSec -= nVal * nDividend;
        nCptValue += 1;
        nLastOutputtedUnit = 2;
        
    nDividend = 60;
    if( rTimeSec >= nDividend and nCptValue < nMaxValue and  ( nLastOutputtedUnit > 1 or not bSmart ) ):
        nVal = int( rTimeSec / nDividend );
        strUnit = astrUnitsPerLang[2][nUseLang];
        if( nVal >= 2. ):
            strUnit += 's';        
        strOut += "%d %s " % ( nVal , strUnit );
        rTimeSec -= nVal * nDividend;
        nCptValue += 1;
        nLastOutputtedUnit = 3;
        
    nDividend = 1;
    if( rTimeSec >= nDividend and nCptValue < nMaxValue and  ( nLastOutputtedUnit > 2 or not bSmart ) ):
        nVal = int( rTimeSec / nDividend );
        strUnit = astrUnitsPerLang[1][nUseLang];
        if( nVal >= 2. ):
            strUnit += 's';        
        strOut += "%d %s " % ( nVal , strUnit );
        rTimeSec -= nVal * nDividend;
        nCptValue += 1;
        nLastOutputtedUnit = 4;
        
    if( rTimeSec > 0. and nCptValue < nMaxValue and ( nLastOutputtedUnit > 3 or not bSmart ) ):
        strUnit = astrUnitsPerLang[0][nUseLang];
        if( int( rTimeSec*1000 ) >= 2. ):
            strUnit += 's';
        strOut += "%3d %s" % ( int( rTimeSec*1000 ) , strUnit );
        nCptValue += 1;
        nLastOutputtedUnit = 5;
        
    return strOut;    
    return strOut;
# transcriptDuration - end    
#~ print transcriptDuration( 153213213.546, bSmart = False );
#~ print transcriptDuration( 153213213.549, bSmart = True, nSmartLevel = 1 );
#~ print transcriptDuration( 60*60*24+1, bSmart = False );
#~ print transcriptDuration( 60*60*24+1, bSmart = True );


def transcriptMoneyEuro( rValue, nUseLang = -1, bUseCentzInsteadOfCentimes = False ):
    "convert a money value into a speechable string "
    "'15,03' => '15 euros et 3 centz"
    "nUseLang: the lang to use, or -1 to use current language"
    
    "WARNING: 15.3 => 15 euros et 30 CENTS"
    "NB: previous bug was with 13.44 => 13 euros and 43 cents"
    
    if( nUseLang == -1 ):
        nUseLang = getSpeakLanguage();
    strOut = "";
    nEuros = int( rValue );
    nCents = int( ( ( rValue - nEuros ) * 100 + 0.5 ) ); # +0.5: to remove the rounded error produced by float (13.44=>13.43 bug)
    if( nUseLang == constants.LANG_FR  ):
        if( nEuros >= 1 or nCents == 0 ):
            strOut += "%d euros" % ( nEuros ); # NB: the 's' is not heard, so we don't handle this case
        if( nCents != 0 ):
            if( nEuros > 0 ):
                strOut += " et ";
            if( not bUseCentzInsteadOfCentimes ):
                strOut += "%d centime" % nCents;
            else:
                if( nCents > 1 ):
                    strOut += "%d centz" % nCents;
                else:
                    strOut += "%d cennte" % nCents;
            
    else:
        if( nEuros > 1 ):
            strOut += "%d euros" % ( nEuros );
        elif( nEuros == 1 or nCents == 0 ):
            strOut += "%d euro" % ( nEuros );            
        if( nCents != 0 ):
            if( nEuros > 0 ):
                strOut += " and ";
            if( nCents > 1 ):
                strOut += "%d cents" % nCents;
            else:
                strOut += "%d cent" % nCents;
    return strOut;
# transcriptMoneyEuro - end

def plural( strWord, nNbr = 2 ):
    """
    convert a word into its plural (multilang melting pot)
    nNbr: permits to convert only if needed, and to have the test in this method
    """
    if( abs(nNbr) <= 1 ):
        return strWord;
    
    aDict = {
        "inch": "inches",
        "foot": "feet",
        "cheval": "chevaux",
        "horse": "horses",
    };
    try:
        return aDict[strWord];
    except BaseException, err:
#        print( "WRN: abcdk.plural: word %s is not handled: %s" % (strWord, err ) ); # it's not a bug, it's just word that doesn't change when used with plural
        pass
    return strWord;
# plural - end

def transcriptDistance( rValue, nUseLang = -1, bUseInchIfEnglish = False, bRound = True, bSmart = True ):
    """
    convert a distance into a speechable string.
    return a string
    15.32 => 15 metres 32
    rValue: value in meter
    nUseLang: lang to use (-1, for current)
    bUseInchIfEnglish: convert to inch if the current language is english
    bRound: round the value to human acceptable things
    bSmart: don't tell units if no used of
    """
    # for each units, the divider from 1 meter
    astrUnits = [
        [1000, "kilometer", "kilomètre"],
        [1, "meter", "mètre"],
        [0.01, "centimeter", "centimètre"],
        [0.001, "milimeter", "milimètre"],
        [0.000001, "micrometer", "micromètre"],
    ];

    astrUnitsInch = [
        [0.3048, "foot", "pied"],
        [0.0254, "inch", "pouces"],
    ];
    # astrTall = [" height", " de haut"];
    astrComma = ["point", "virgule"];
    
    if( nUseLang == -1 ):
        nUseLang = getSpeakLanguage();
        
    bUseInch = False;        
    if( nUseLang == 0 and bUseInchIfEnglish ):
        bUseInch = True;
        astrUnits = astrUnitsInch;
    
    strTxt = "";
    nCptOutput = 0; # count number of outputted units
    bHasComma = False;
    for idx, unit in enumerate( astrUnits ):
        bLastUnit = (idx == len( astrUnits )-1);
        if( rValue / unit[0] >= 1 or bLastUnit ):
            if( bLastUnit and nCptOutput == 0 ):
                # use a floating point
                rValueEnt = rValue / unit[0];
                bHasComma = True;
                strReal = "%f" % rValueEnt;
                # remove non significative 0 (it should exists in formating, but don't find it by now)
                while( strReal[-1] == '0' ):
#                    print( "transcriptDistance: remove non significative 0 from %s" % strReal );
                    strReal = strReal[:-1];
                strTxt += strReal + " ";
            else:
                if( nCptOutput >= 1 and bSmart ):
                    # round it
                    rValueEnt = int( (rValue / unit[0])+0.5 );
                else:
                    rValueEnt = int( rValue / unit[0] );
                strTxt += str( rValueEnt ) + " ";
            if( nCptOutput < 1 or not bSmart ):
                strUnit = unit[nUseLang+1];
                strUnit = plural( strUnit, rValueEnt );
                strTxt += strUnit + " ";
            rValue = rValue - (rValueEnt*unit[0]);
#            print( "rValueEnt: %f, remains: %f" % ( rValueEnt, rValue ) );
            nCptOutput += 1;
            if( nCptOutput == 2 and bSmart ):
                break;
        else:
            if( nCptOutput == 1 and bSmart ):
                # we've previously outputted a value, it's enough
                break;
                
    # change all point by a comma to have better pronounciation
    if( bHasComma ):
        strTxt  = strTxt.replace( ".", " " + astrComma[nUseLang] + " " );
    return strTxt;
# transcriptDistance - end



def transcriptDirection( v, nUseLang = -1 ):
    "nao say a direction from a vector expressed in it's own repere"
    astrFr = [ "devant moi",         # 0
                   "derrière moi",
                    "a ma gauche",
                    "a ma droite",      # 3
                    "vers le haut",
                    "vers le bas",                    
                ];
    astrEn = [ "in front of me",         # 0
                   "behind me",
                    "to my left",
                    "to my right",      # 3
                    "up",
                    "down",                    
                ];
                

    if( nUseLang == -1 ):
        nUseLang = getSpeakLanguage();
        
    if( nUseLang == 1 ):        
        aTxt = astrFr;
    else:
        aTxt = astrEn;
    nIdx = 0;
    
    if( abs(v[0]) > abs(v[1] ) ):
        if( abs(v[0]) > abs(v[2]) ):
            if( v[0] > 0 ):
                nIdx = 0;
            else:
                nIdx = 1;
        else:
            if( v[2] > 0 ):
                nIdx = 4;
            else:
                nIdx = 5;
    else:
        if( abs(v[1]) > abs(v[2]) ):
            if( v[1] > 0 ):
                nIdx = 2;
            else:
                nIdx = 3;
        else:
            if( v[2] > 0 ):
                nIdx = 4;
            else:
                nIdx = 5;
    return aTxt[nIdx];
# transcriptDirection - end
#print( transcriptDirection( [-0,-1,0] ) );
#print( transcriptDirection( [-0.1472894549369812, -0.8651672005653381, 0.479365736246109] ) );

def transcriptOrdering( nNum, nUseLang = -1, bIsFeminine = False ):
    "convert a number to an ordered number"
    "1 => first"
    "2 => second"
    "..."
    "cf sayPlace for test/usage/..."
    
    nNum = int( nNum );

    if( nUseLang == -1 ):
        nUseLang = getSpeakLanguage();
    
    if( nUseLang == 1 ):
        # French - tested between 1 & 64 (but should work after that)
        if( nNum == 1 ):
            if( bIsFeminine ):
                return "première";
            return "premier";
        if( nNum <= 3 or nNum == 6 or nNum == 10 or nNum == 11 or nNum == 12 or ( nNum > 20 and nNum % 10 in [2,3,6] ) ):
            return str( nNum ) + "-zième";            
        if( nNum == 8 ):
            return str( nNum ) + "-tième";
        if( nNum > 20 and nNum % 10 == 1 ):            
            return str( nNum -  nNum % 10 ) + " et-une-ième";            
        return str( nNum ) + "-i-ième";
    
    # English
    if( nNum == 11 or nNum == 12 or nNum == 13 ):
        return str( nNum ) + 'th';
    
    if( nNum%10 == 1  ):
        return str( nNum ) + 'st';
    if( nNum%10 == 2 ):
        return str( nNum ) + 'nd';
    if( nNum%10 == 3 ):
        return str( nNum ) + 'rd';
    return str( nNum ) + 'th';    
# transcriptOrdering - end


class LocalizedText:
  "multi-lang text functionnality, with caching"
  "WRN: we 're accepting to have some sentence with more lang than others"
  "TODO: this class is too old, and we should find something more convenient to meet our requirements"

  def __init__( self ):
    self.aListSentences = [];
    self.nNbrLangMax = 0;
    self.nCurrentLanguage = 0;
    self.bPrecompute = config.bPrecomputeText;
    self.bStoreToNonVolatile = False; # if True, after generate text, it will be stored to the tmp non volatile path, so no generation at next boot
  # __init__ - end

  def setPrecompute( self, bNewState ):
    "change the precompute option, to true or false. WRN: do it before calling the add method, if you don't want to precompute them at startup"
    self.bPrecompute = bNewState
  # setPrecompute - end

  def changeCurrentLangToDefault( self ):
    "change the language to reflect the default, the text will then be prepared for the current lang"
    self.setCurrentLang( getDefaultSpeakLanguage() );
  # changeCurrentLangToDefault - end

  def setCurrentLang( self, nNumCurrentLang ):
    "change the language, the text will then be prepared for the current lang"
    print( "LocalizedText.setCurrentLang: changing to lang %d" % nNumCurrentLang );
    self.nCurrentLanguage = nNumCurrentLang;
    setSpeakLanguage( self.nCurrentLanguage );
    self.prepareTextOneLang( self.nCurrentLanguage );
  # setCurrentLang - end

  def setStoreToNonVolatile( self, bNewVal ):
    "Set or unset the StoreToNonVolatile option"
    self.bStoreToNonVolatile = bNewVal;
  # setStoreToNonVolatile - end

  def getCurrentLang( self ):
    return self.nCurrentLanguage;
  # getCurrentLang - end

  # add a new sentence of the form ["hello", "bonjour"];
  # return the ID of the new created text
  def add( self, aMultiLangSentence ):
    # transform accent
    for i in range( 0, len( aMultiLangSentence ) ):
      # aMultiLangSentence[i] = assumeTextHasDefaultSettings( transformAsciiAccentForSynthesis( aMultiLangSentence[i] ) );
      aMultiLangSentence[i] = assumeTextHasDefaultSettings( aMultiLangSentence[i] );
    self.aListSentences.append( aMultiLangSentence );
    self.nNbrLangMax = max( self.nNbrLangMax, len( aMultiLangSentence ) );
    return len( self.aListSentences ) - 1;
  # add - end

  def say( self, nID, nStyle = 0 ):
    if nStyle == 0:
      sayWithEyes2( self.getText( nID ), 1, self.bPrecompute );
    else:
      sayAndEyes( self.getText( nID ), True );
  # say - end

  # permits to get current text for various reason
  def getText( self, nID ):
    if( nID < 0 or nID >= len( self.aListSentences ) ):
      print( "LocalizedText.getText: id %d out of bound" % nID );
    if( self.nCurrentLanguage < 0 or self.nCurrentLanguage >= len( self.aListSentences[nID] ) ):
      print( "LocalizedText.getText: self.nCurrentLanguage %d out of bound" % self.nCurrentLanguage );
    return self.aListSentences[nID][self.nCurrentLanguage];
  # getText - end

  def prepareTextOneLang( self, nNumLang ):
    #leds = myGetProxy( "ALLeds" );
    if not self.bPrecompute:
      return
    setSpeakLanguage( nNumLang );
    for sentence in self.aListSentences:
      if( nNumLang < len( sentence )  ):
        txt = sentence[nNumLang];
        print( "LocalizedText.prepareAllText: preparing this text: '%s' (lang %d)" %( txt, nNumLang ) );
#        leds.post.rasta( 0.5 );
        sayAndCache( txt, True, self.bStoreToNonVolatile );

#        leds.stop( nID );
  # prepareTextOneLang - end

  def prepareAllText( self ):
    print( "LocalizedText.prepareAllText" );
    for nNumLang in range(0, self.nNbrLangMax ): # changer de langue a la volée n'est pas immédiat, donc il faut parcourir langue par langue
      self.prepareTextOneLang( nNumLang );
    # set the default language
    setSpeakLanguage( self.nCurrentLanguage );
  # prepareAllText - end

  # return the number of different text (in each lang)
  def getNbrText( self ):
    return len( self.aListSentences );
  # getNbrText - end

# class LocalizedText - end

def say( s, bWaitEnd = True ):
    tts = naoqitools.myGetProxy( "ALTextToSpeech" );
    if( not bWaitEnd ):
        return tts.post.say( s );
    tts.say( s );
#say - end

def postSay( s ):
    tts = naoqitools.myGetProxy( "ALTextToSpeech" );
    return tts.post.say( s );
#say - end

# say something using standard APPU interaction (leds, talk jingle...)
# to use text from ID use the getText method from your xar file
def speak( s, bStoreToNonVolatilePath = False ):
  try:
    sound.playSoundSpeaking();
    leds = naoqitools.myGetProxy( "ALLeds" );
    nTimeEyes = len( s ) *50; # temps de lire une lettre :)
    if( nTimeEyes < 500 ):
      nTimeEyes = 500;
    # leds.pCall( "eyesRandom", nTimeEyes );
  #  idEyesRandom = leds.pCall( "randomEyes", nTimeEyes / 1000.0 );
    leds.fadeRGB( "FaceLeds", 0x8585ff, 0.4 );

    s = assumeTextHasDefaultSettings( s );
    sayAndCache( s, bJustPrepare = False, bStoreToNonVolatilePath = bStoreToNonVolatilePath, bDirectPlay = False );
#  leds.stop( idEyesRandom );
    leds.fadeRGB( "FaceLeds", 0x108040, 0.4 );
  except BaseException, err:
    print( "speak: ERR: " + str( err ) );
    pass
# speak - end

def speakLight( strTxt, nEmotion = 0 ):
    "say a sentence with eyes light on when speaking, and off after"
    "emotion change the leds color: 0: neutre, ."
    
    tts = naoqitools.myGetProxy( 'ALTextToSpeech' );
    leds = naoqitools.myGetProxy( "ALLeds" );
    mem = naoqitools.myGetProxy( "ALMemory" );
    mem.raiseMicroEvent( "PleasePauseSpeechRecognition", True );
    time.sleep( 0.2 ); # wait some buffer are flushed
    leds.post.fadeRGB( "FaceLeds", 0xffffff, 0.5 );
    tts.say( strTxt );
    time.sleep( 0.7 ); # wait some more!
    leds.post.fadeRGB( "FaceLeds", 0x101010, 0.5 );
    mem.raiseMicroEvent( "PleasePauseSpeechRecognition", False );    
# speakLight - end

def speechEmo( txt, strEmotion = "Standard", bWaitEnd = True, bPrecompute = False ):
    "talk using a specific emotion"
    "strEmotion, can be 'Standard', 'Happy', 'Sad', 'Loud', 'Proxi' or NAO"
    "Return -1 on error, or the ID of the speaking task"
    "New version: add eyes light"
    print( "speechEmo( '%s', strEmotion = '%s', bPrecompute = %s" % (txt, str( strEmotion ), str( bPrecompute ) ) );
    try:
        tts = naoqitools.myGetProxy( 'ALTextToSpeech' );
        ad = naoqitools.myGetProxy( 'ALAudioDevice' );
    except BaseException, err:
        print( "ERR: abcdk.speech.speechEmo: " + str( err ) );
        return -1;

    nFreq = 22050;
    if( strEmotion.lower() == 'NAO'.lower() ):
        strUseVoice = 'Julie22Enhanced';
    else:
        strUseVoice = 'Antoine16' + strEmotion;
        nFreq = 16000;

    if( bPrecompute ):
        return sayAndCache( txt, strUseVoice = strUseVoice, bWaitEnd = bWaitEnd, bDirectPlay = True, bStoreToNonVolatilePath = True );
    else:
        tts.setVoice( strUseVoice );
        ad.setParameter( "outputSampleRate", nFreq );
        try:
            if( bWaitEnd ):
                tts.say( txt );
                return;
            return tts.post.say( txt );
        except BaseException, err:
            print( "ERR: abcdk.speech.speechEmo: " + str( err ) );
    return -1;
# speechEmo - end

def getEmoText( arListRatio, rNeutral = 0., nUseLang = -1 ):
    "Get a text describing an emotion"
    "arListRatio: the ratio of each emotions: [Proud, Happy, Excitement, Fear, Sadness, Anger]"    
    "nUseLang: the lang to use, -1 to use the current one"
    
    if( nUseLang == -1 ):
        nUseLang = getSpeakLanguage();
        
    aaListFr = [ 
                     ["Je suis trop fort.", "Je suis bien fier de moi.", "Je suis un force de la nature.", "hum","Ohoh"],
                     ["Youpi!", "Super!", "Chouette!", "C'est trop cool!", "Oui, c'est ça!", "Bravo!", "Je suis bien, bien content."],
                     ["Houlalala!", "Youhou!", "Hooooo", "Chouette, chouette, chouette!"],
                     ["Au secours!", "Aaaah", "J'ai peur"],
                     ["Snif.", "Je suis triste.", "mince!"],
                     ["Raaah!", "Rondudu!", "Flute!", "Peuchère!"],
                     ["Je suis un peu bof.", "Mouais."], # neutral
                ];
    aaListEn = [
            [ "I'm proud of that!"],
            [ "Great!", "Cool!", "I'm happy!"],
            ["Youhou!"],
            ["Help!"],
            ["I'm sad!"],
            ["Damn!", "F word!"],
            ["Hunhun"], # neutral
        ];
    
    if( nUseLang == constants.LANG_FR  ):
        aaListToUse = aaListFr;
    else:
        aaListToUse = aaListEn;
    nIdxEmotion = 6; # default if neutral
    
    if( rNeutral < 0.5 ):
        nIdxMax = 0;
        for i in range(1, 6):
            if( arListRatio[nIdxMax] < arListRatio[i] ):
                nIdxMax = i;
        nIdxEmotion = nIdxMax;
    print( "INF: getEmoText: using emotion: %d" % nIdxEmotion );
    strTxt = aaListToUse[nIdxEmotion][int( ( random.random() ) * len( aaListToUse[nIdxEmotion] ) )];
    return strTxt;
# getEmoText - end

# print( "EmoText: '%s'" % getEmoText( [0,1,0,0,0,0], nUseLang = 1 ) );

def getTextAppreciation( rNote, nUseLang = -1 ):
    """"Get a text describing an appreciation, should be pasted to "c'est" or "it's"
    rNote: an appreciation from -1 (very bad, to 1 perfect, 0 is neutral)
    nUseLang: the lang to use, -1 to use the current one
    """
    
    # Imagine you're speaking about a movie you just see.
    if( nUseLang == -1 ):
        nUseLang = getSpeakLanguage();
        
    aaListFr =   [
                        [ 
                            ["très mauvais", "très nul", "exécrable", "ignoble", "atroce", "tout pourri", "vraiment nul", "excessivement mauvais", "nul à en pleurer"],
                            ["mauvais", "nul", "pitoyable"],
                            ["pas terrible", "très bof", "passable"],
                        ],
                        [
                            ["moyen", "bof", "passable", "neutre"],
                        ],
                        [ 
                            ["pas mal", "correct", "sympa"],
                            ["plutot pas mal", "plutot sympa"],
                            ["bien", "super", "cool", "chouette"],
                            ["formidable", "presque parfait", "superbe", "extra", "top", "tip top", "grandiose"],
                            ["parfait", "excellent", "hypère bien", "trop génial", "génial", "trop cool", "génialissime", "trop bien"],
                        ],
                ];
    aaListEn = [
                        [ 
                            ["very bad"],
                            ["bad"],
                        ],
                        [
                            ["medium"],
                        ],
                        [ 
                            ["not bad", "not so bad"],
                            ["quite good", "quite nice"],
                            ["super", "cool", "good", "nice", "correct"],
                            ["awesome", "great" ],
                            ["perfect", "excellent"],
                        ],
                ];
    
    if( nUseLang == constants.LANG_FR  ):
        aaListToUse = aaListFr;
    else:
        aaListToUse = aaListEn;
    
    rQuiteZero = 0.05;
    if( rNote < -rQuiteZero ):
        if( rNote < -1. ):
            rNote = -1.;
        nNbrVariation = len( aaListToUse[0] );
        aList = aaListToUse[0][int( (1+rNote)*nNbrVariation)];
    elif( rNote < rQuiteZero ):
        aList = aaListToUse[1][0];
    else:
        if( rNote > 0.999 ):
            rNote = 0.999;        
        nNbrVariation = len( aaListToUse[2] );
        aList = aaListToUse[2][int( rNote*nNbrVariation)];
        
    strTxt = aList[int( ( random.random() ) * len( aList ) )];
    return strTxt;
# getEmoText - end

#~ print( "getTextAppreciation: '%s'" % getTextAppreciation( 0.1, nUseLang = 0 ) );
#~ exit(1);

def getSomeRandomMultilangText( aBigMultilangArray, nUseLang = -1 ):
    """"Get a text describing something"
    nUseLang: the lang to use, -1 to use the current one
    It's a bit inner library purpose
    """
    
    # Imagine you're speaking about a movie you just see.
    if( nUseLang == -1 ):
        nUseLang = getSpeakLanguage();
        
    if( nUseLang == constants.LANG_FR  ):
        aaListToUse = aBigMultilangArray[1];
    else:
        aaListToUse = aBigMultilangArray[0];
        
    strTxt = aaListToUse[int( ( random.random() ) * len( aaListToUse ) )] + "!";
    return strTxt;
# getSomeRandomMultilangText - end

def getEncouragement( nUseLang = -1 ):
    """"Get a text describing an encouragement"
    nUseLang: the lang to use, -1 to use the current one
    """
    aaListFr =   [
                        "vas-y", "continue", "c'est bien", "ouiii", "allez encore un petit effort", "tu es sur la bonne voie",
                ];
    aaListEn =   [
                        "go ahead", "let's go", "continue",
                ];
    
    return getSomeRandomMultilangText([aaListEn,aaListFr], nUseLang );
# getEncouragement - end
#print( "getEncouragement: '%s'" % getEncouragement( nUseLang = 1 ) );

def getExhortation( nUseLang = -1 ):
    """"Get a text describing an encouragement"
    nUseLang: the lang to use, -1 to use the current one
    """
    aaListFr =   [
                        "oui?", "hum", "hum,hum", "et?","ah", "oh","je vois,","continue,"
                ];
    aaListEn =   [
                        "I see,", "hum", "a", "e"
                ];
    
    return getSomeRandomMultilangText([aaListEn,aaListFr], nUseLang );
# getEncouragement - end
# print( "getExhortation: '%s'" % getExhortation( nUseLang = 1 ) );

def bodyLight( strTextToSay, nUseLang = -1, strUseVoice = None ):
    "lighten all blue leds of the body relatively to a text spoken"
    "the spoken text duration is computed roughly"
    "HINT: we should register to speech detection, and wait each time it's spoken, then lights leds!"
    "So it shoud be soon deprecated"
    strTextToSay = assumeTextHasDefaultSettings( strTextToSay, nUseLang );
    sayAndCache( strTextToSay, bJustPrepare = True, nUseLang = nUseLang, strUseVoice = strUseVoice );
    strFilename = sayAndCache_getFilename( strTextToSay, nUseLang = nUseLang, strUseVoice = strUseVoice );
    strFilename = pathtools.getVolatilePath() + "generatedvoices" + pathtools.getDirectorySeparator() + strFilename + ".raw";
    rDuration = os.path.getsize( strFilename ) / (22050 * 2.);
    print( "rDuration: %5.2f" % rDuration );
    leds = naoqitools.myGetProxy( "ALLeds" );
    rTimeBegin = 0.2;
    rTimeEnd = 0.4;
    leds.post.fadeListRGB( "AllLeds", [0xFFFFFF,0xFFFFFF, 0.], [rTimeBegin, rDuration-rTimeBegin-rTimeEnd,rTimeEnd] );
# bodyLight - end

def warmup(  nUseLang = -1 ):
    """
    say a text to warm up the tts, so there will be less glitch (the phoneme would be loaded from the disk (in the disk cache or in the tts motor)
    """
    
    print( "INF: abcdk.speech.warmup: beginning..." );
    
    tts = naoqitools.myGetProxy("ALTextToSpeech");
    if( nUseLang == -1 ):
        nUseLang = getSpeakLanguage();
    else:
        setSpeakLanguage( nUseLang );    
    
    mem = naoqitools.myGetProxy( "ALMemory" );
    strAlreadyMadeKey = "AbcdkSpeechWarmupDone" + str(nUseLang);
    
    try:
        bRet = mem.getData( strAlreadyMadeKey );
        if( bRet ):
            # already made...
            return;
    except:
        pass
    
    aVoyelle = ["a", "e", "i", "o", "u", "on", "en", "ou"];
    aConsonne = ["b", "c", "d", "f", "g", "m", "n", "p", "s", "t", "v", "z"];
    
    txt = "";
    for cons in aConsonne:
        for voy in aVoyelle:
            txt += cons + voy + " ";
    tts.say( "\\VOL=5\\ \\RSPD=250\\ "+ txt + "\\RSPD=95\\ " );
    mem.insertData( strAlreadyMadeKey, True );
# warmup - end

def sayAbbreviated( strLong, strShort = "", bDuringNaoqiSession = False ):
    """
    say something but don't repeat the long version if it has already said during this boot session
    - bDuringNaoqiSession: if true, it's during naoqi session, else it's during this boot session NDEV
    """
    strFilename = sayAndCache_getFilename( strLong + strShort );
    if( os.path.exists( strFilename ) ):
        txt = strShort;
        nLightType = 0; # more subtil
    else:
        file = open( strFilename, "wt" );
        file.write( "1" );
        file.close();
        txt = strLong;
        nLightType = 1;
    return sayAndLight( txt, nLightType = nLightType, bUseDisplay = False );
# sayAbbreviated - end

def autoTest():
    test.activateAutoTestOption();
    #~ speechEmo( "Coucou les femmes, je vais toutes vous baiser, avec mon gros outils, vous allez bien le sentir !", "Happy" );
    #~ speechEmo( "Oh oui, c'est bon!", "Loud" );
    #~ speechEmo( "Valentin, je t'encule, drogué!", "Proxi" );
    #~ speechEmo( "Il parait que si tu l'as courte, c'est meilleur!", "NAO" );
    #~ speechEmo( "voix precalculé 1", "Loud", bPrecompute = True );
    #~ speechEmo( "voix precalculé 2", "Proxi", bPrecompute = True );
    
    strText = transcriptOrdering( 1, 1 );
    assert( strText == "premier" );
    strText = transcriptOrdering( 1, 0 );
    assert( strText == "1st" );
    strText = transcriptOrdering( 121.1, 1 );
    assert( strText == "120 et-une-ième" );
    

    print( "transcriptFloat: " + transcriptFloat( 5.00123 ) );
    print( "transcriptFloat: " + transcriptFloat( -5.00123 ) );
    print( "transcriptFloat: " + transcriptFloat( 0.0 ) );
    
    print( "transcriptDate: " + transcriptDate( "2008/12/31", constants.LANG_FR ) );
    print( "transcriptDate: " + transcriptDate( "2008/12/31", constants.LANG_EN ) );
    print( "transcriptDate: " + transcriptDate( "2011/01/31", constants.LANG_FR, bSmart = True ) );
    print( "transcriptDate: " + transcriptDate( "2011/1/20", constants.LANG_EN, bSmart = True ) );    

    for nLang in [constants.LANG_FR, constants.LANG_EN]:
        print( "transcriptTime: " + transcriptTime( "7:30", nLang ) );
        print( "transcriptTime: " + transcriptTime( "12:00", nLang ) );
        print( "transcriptTime: " + transcriptTime( "12:05:59", nLang ) );
        print( "transcriptTime: " + transcriptTime( "15:00", nLang ) );
        print( "transcriptTime: " + transcriptTime( "17", nLang ) );
        print( "transcriptTime: " + transcriptTime( "23:05", nLang ) );
        print( "transcriptTime: " + transcriptTime( "00:00", nLang ) );

    for nLang in [constants.LANG_FR, constants.LANG_EN]:
        print( "transcriptDateTime: " + transcriptDateTime( "2008/1/20", "15:03",  nLang, bSmart = True ) );
        print( "transcriptDateTime: " + transcriptDateTime( "2011/6/13", "17:03",  nLang, bSmart = True ) );
        print( "transcriptDateTime: " + transcriptDateTime( time.strftime("%Y/%m/%d"), "18:00",  nLang, bSmart = True ) );
        
    print( str( getTimeDelay( "2011/06/15", "17:00" ) ) );

    for nLang in [constants.LANG_FR, constants.LANG_EN]:
        print( "transcriptMoneyEuro: " + transcriptMoneyEuro( 0, nLang ) );
        print( "transcriptMoneyEuro: " + transcriptMoneyEuro( 1, nLang ) );
        print( "transcriptMoneyEuro: " + transcriptMoneyEuro( 3, nLang ) );
        print( "transcriptMoneyEuro: " + transcriptMoneyEuro( 3.01, nLang ) );
        print( "transcriptMoneyEuro: " + transcriptMoneyEuro( 12.18, nLang ) );
        print( "transcriptMoneyEuro: " + transcriptMoneyEuro( 13.44, nLang ) );
        print( "transcriptMoneyEuro: " + transcriptMoneyEuro( 0.99, nLang ) );
        print( "transcriptMoneyEuro: " + transcriptMoneyEuro( 0.1, nLang ) );
        print( "transcriptMoneyEuro: " + transcriptMoneyEuro( 0.00, nLang ) );
        
        print( transcriptDistance( 15.32, nLang, bUseInchIfEnglish = True ) );
        print( transcriptDistance( 1500, nLang ) );
        print( transcriptDistance( 15*1000+3.21, nLang ) );
        print( transcriptDistance( 15*1000+3.21, nLang, bSmart = False ) );
        print( transcriptDistance( 15*1000+3.21, nLang, bSmart = False, bUseInchIfEnglish = True ) );
        print( transcriptDistance( 1000.2001, nLang ) );
        print( transcriptDistance( 1000.0003, nLang ) );
        print( transcriptDistance( 0.00000013, nLang, bUseInchIfEnglish = True ) );
        print( transcriptDistance( 1, nLang, bUseInchIfEnglish = True ) );
        print( transcriptDistance( 0.33, nLang, bUseInchIfEnglish = True ) );
    
    #~ for i in range( 32 ):
        #~ print( getDayLibelle_En( i ) );
    
# autoTest - end

if( __name__ == "__main__" ):
    autoTest();
