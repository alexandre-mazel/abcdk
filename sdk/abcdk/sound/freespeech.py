# -*- coding: utf-8 -*-
###########################################################
# Aldebaran Behavior Complementary Development Kit
# Speech Recognition tools (alternate or ...)
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

import os
import logging
import time

try: 
    import speech_recognition 
except: 
    pass

try:
    from bs4 import BeautifulSoup 
except:
    pass

from abcdk.sound import language_tools

# Define the singleton metaclass
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class FreeSpeech():
    """
    Freespeech with google
    """
    #specify that FreeSpeech is an instantiation of the metaclass Singleton
    __metaclass__ = Singleton
    
    def __init__( self, qiapp ):
        self.lt = language_tools.LanguageTools(qiapp)

    def cleanText(self, rawResume):
        """ encode with bs4 for handle special character """
        soup = BeautifulSoup(rawResume)

        for script in soup(["script", "style"]):                                                
            script.extract()                                                                    
        
        text = soup.get_text()                                           
        lines = (line.strip() for line in text.splitlines())                       
        chunks = (phrase.strip() for line in lines for phrase in line.split("  ")) 
        text = '\n'.join(chunk for chunk in chunks if chunk)                  
        text = text.encode('utf-8', 'ignore')
        return text
        
    def cleanText2( self, txt ):
        try:
            txt = str(txt)
        except BaseException, err:
            logging.debug( "can't convert text to ascii?" )
            try:
                txt = self.cleanText(txt)
            except:
#                    logging.warning("freespeech : analyse : you need to install beautifulsoup4")
                #Methode with "ai"
                unicoded = unicode(txt).encode('utf8')
                logging.debug( "unicoded: %s" % unicoded )
                utxt = str(unicoded)
                logging.debug( "txt: %s" % utxt )
                txt = ""
                for c in utxt:
                    if ord(c) < 128:
                        txt += c
                    else:
                        logging.debug( "bad char: %s %d" % (c, ord(c) ) )
                        ordc = ord(c)
                        if( ordc in [168, 169, 170, 171] ):
                            txt += "ai"
                        if( ordc in [160] ):
                            txt += "a"
                        
            logging.debug( "txt2: %s" % txt )
        return txt
        

    def analyse( self, strSoundFilename, strUseLang = "", bStoreToEvents = False ):
        """
        Send a file to the speech recognition engine.
        Return: an array [[strRecognizedText, rConfidence], [strAlternateRecognizedText, rConfidence] ...]
        or None if nothing recognized
        """
        try:
            import speech_recognition
        except:
            logging.error( "FreeSpeech.analyse: remote free speech server is not available... (speech_recognition: is not installed on this robot ? copy some binary to the site-library" )
            return None
        
    
        #~ logging.info( "FreeSpeech.analyse: sending to speech reco '%s'" % strSoundFilename )
        
        strAnsiLang = strUseLang
        if( strAnsiLang == "" ):
            strAnsiLang = self.lt.getSpeakLanguageAnsiCode( self.lt.getSpeakLanguage() )
            logging.debug( "After autodetection, using Lang input: %s" % strAnsiLang )
        else:
            logging.debug( "Using Lang input: %s" % strAnsiLang )

        retVal = None
        
        timeBegin = time.time()
        
        r = speech_recognition.Recognizer()
        
        with speech_recognition.WavFile(strSoundFilename) as source:
            audio = r.record(source) # read the entire WAV file
        # recognize speech using Google Speech Recognition
        try:
            # for testing purposes, we're just using the default API key
            retFromReco =r.recognize_google(audio, language = strAnsiLang, show_all = True )
            logging.debug( "retFromReco: %s" % retFromReco )
            if retFromReco != []:
                
                alt = retFromReco['alternative']
                strTxt = alt[0]['transcript']

                # when reco does not return a confidence, use -1 as an error code
                if 'confidence' in alt[0]:
                    rConf = alt[0]['confidence']
                else:
                    logging.debug('no confidence returned')
                    rConf = -1.0
            
                strTxt = self.cleanText2( strTxt )
                logging.info("Google Speech Recognition thinks you said: '%s' (conf:%5.2f)\n" % (strTxt, rConf) )
                retVal = [ [strTxt,rConf] ]

        except speech_recognition.UnknownValueError:
            pass
            
        except speech_recognition.RequestError as e:
            logging.error("Could not request results from Google Speech Recognition service; {0}".format(e))
    
        rProcessDuration = time.time() - timeBegin
        self.rSkipBufferTime = rProcessDuration  # if we're here, it's already to zero

        if retVal == None: logging.info("Google Speech Recognition could not understand audio\n")

        return retVal
