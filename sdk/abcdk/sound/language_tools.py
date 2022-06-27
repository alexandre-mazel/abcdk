import logging

# Define the singleton metaclass
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class LanguageTools():
    #specify that LanguageTools is an instantiation of the metaclass Singleton
    __metaclass__ = Singleton

    def __init__(self,qiapp):
        self.qiapp = qiapp
        if self.qiapp != None:
            self.memory = self.qiapp.session.service("ALMemory")
            self.tts = self.qiapp.session.service("ALTextToSpeech")
            self.asr = self.qiapp.session.service("ALSpeechRecognition")
        else:
            # fuck compatibility of retro compatibility of cleaning that mess to come back to a efficient emulated old naoqi v1 Arghhghghghghgh
            import abcdk.naoqitools as naoqitools
            self.memory = naoqitools.myGetProxy("ALMemory")
            self.tts = naoqitools.myGetProxy("ALTextToSpeech")
            self.asr = naoqitools.myGetProxy("ALSpeechRecognition")
            

    def getSpeakLanguage(self):
        """
        return the default speak language
        """
        return  self.tts.getLanguage()
    # getDefaultSpeakLanguage - end

    def setSpeakLanguage(sefl, strLang, bChangeAsrAlso = False ):
        """
        change the tts and asr speak language
        """
        logging.debug("SetSpeakLanguage to: %d" % nNumLang )

        try:
            self.tts.loadVoicePreference( "NaoOfficialVoice" + strLang )
        except BaseException, err:
            logging.error( "Is lang %s unknown?" % str( strLang ) )
            logging.error( "%s" % str(err) )
            logging.info( "Trying a call to setLanguage" )
            try:
                self.tts.setLanguage( strLang )
            except BaseException, err:
                logging.error( "SetLanguage, error: %s" % str(err) )
            
            
        if( bChangeAsrAlso ):
            try:
                asr.setLanguage( strLang )
            except BaseException, err:
                logging.error( "asr.setLanguage, error: %s" % str(err) )
    # setSpeakLanguage - end

    def getSpeakLanguage(self):
      return self.tts.getLanguage()

    def getSpeakLangAbbrev(self):
      """
      return the current speak language of the synthesis using the LangAbbrev ("fr", "jp", ...
      """
      return toLangAbbrev(self, getSpeakLanguage() )
    # getSpeakLangAbbrev - end

    def toLangAbbrev(self, strLang ):
        "return the lang abbreviation from a lang number"
        if( strLang == "French" ):
            return 'fr'
        if( strLang == "English" ):
            return 'en'
        if ( strLang == "Spanish" ):
            return 'sp'
        if ( strLang == "Italian" ):
            return 'it'
        if ( strLang == "German" ):
            return 'ge'
        if ( strLang == "Chinese" ):
            return 'ch'
        if ( strLang == "Japanese" ):
            return 'jp'
        if ( strLang == "Polish" ):
            return 'po'
        if ( strLang == "Korean" ):
            return 'ko'
        if ( strLang == "Brazilian" ):
            return 'br'
        if ( strLang == "Turkish" ):
            return 'tu'
        if ( strLang == "Portuguese" ):
            return 'pt'

        logging.warning( "Language %s is unknown" % strLang  )
        raise (BaseException("Language %s is unknown" % strLang))


    def fromLangAbbrev(self, strLangAbbrev ):
        "return the lang constant from lang abbrevation"
        if( strLangAbbrev == 'fr' ):
            return "French"
        if( strLangAbbrev == 'en' ):
            return "English"
        if( strLangAbbrev == 'sp' ):
            return "Spanish"
        if( strLangAbbrev == 'it' ):
            return "Italian"
        if( strLangAbbrev == 'ge' or strLangAbbrev == 'de' ): 
            return "German"
        if( strLangAbbrev == 'ch' ):
            return "Chinese"
        if( strLangAbbrev == 'jp' ):
            return "Japanese"
        if( strLangAbbrev == 'po' ):
            return "Polish"
        if( strLangAbbrev == 'ko' ):
            return "Korean"
        if( strLangAbbrev == 'br' ):
            return "Brazilian"
        if( strLangAbbrev == 'tu' ):
            return "Turkish"
        if( strLangAbbrev == 'pt' ):
            return "Portuguese"

        logging.warning( "Language abbrev %s is unknown" % str( strLangAbbrev ) )
        raise( BaseException( "Language abbrev %s is unknown" % str( strLangAbbrev ) ))

    def getSpeakLanguageAnsiCode(self, strLang ):
        """
        return the ansi code relative to some ansi code.
        eg: fr => "fr-FR"
        """
        if( strLang == "French" ):
            return 'fr-FR'
        if( strLang == "English" ):
            return 'en-UK'

        logging.warning( "Language %s is unknown" % str( strLang ) )
        raise( BaseException( "Language %s is unknown" % str( strLang ) ))
    # getSpeakLanguageAnsiCode - end    
        

    def isLangPresent(self, strLang ):
        """
        Is lang present in the system
        """
        return strLang in self.tts.getAvailableLanguages()
    # isLangPresent - en


    def getVoice(self):
      """
      return the current voice of the synthesis
      """
      return self.tts.getVoice()
