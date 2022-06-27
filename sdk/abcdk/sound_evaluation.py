# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Sound evaluation
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Tools to evaluate the speech recognition"""
print( "importing abcdk.sound_evaluation" );

import os
import time

import naoqi

import speech


def decodeFilename( strFilename ):
    """
    Takes a filename and decode its name.
    - strFilename: a filename eg: alexandre__en__nice_to_meet_you__2.wav
    Return an array:
        ["speakername", "lang", "message", "instance_number"]
        eg: ["alexandre","en","nice to meet you", 2]
    """
    nNumOccurence = 1
    aSplitted = strFilename.lower().split(".")[0].split("__")
    strSpeakerName = aSplitted[0]
    strLang = aSplitted[1]
    strMessage = aSplitted[2].replace( "_", " " )
    if( len(aSplitted) > 3 ):
        nNumOccurence = int(aSplitted[3])
    return [strSpeakerName,strLang,strMessage,nNumOccurence]
# decodeFilename - end

def autotest_decodeFilename():
    res = decodeFilename( "alexandre__en__nice_to_meet_you.wav" )
    assert( res == ["alexandre", "en", "nice to meet you", 1] )    
    res = decodeFilename( "Alexandre__fr__nice_to_meet_you__2.wav" )
    assert( res == ["alexandre", "fr", "nice to meet you", 2] )
# autotest_decodeFilename - end

def encodeFilename( strSpeakerName, strLang, strMessage, nNumOccurence = 1):
    """
    Generate a filename based on some wanted sound properties
    Return: the filename without extension
    """
    strMessageNormalised = strMessage.replace(" ", "_")
    strMessageNormalised = strMessageNormalised.replace("'", "_")
    strFilename = "%s__%s__%s" % (strSpeakerName, strLang, strMessageNormalised )
    if( nNumOccurence > 1 ):
        strFilename += "__%d" % nNumOccurence
    return strFilename
# encodeFilename - end

def decodeFilename_name_age( strFilename ):
    """
    take a sound file name and return data extracted from filename.
    return a list of field: ["name", age, is_female, recorder_name, title, occurence number, comments]
    eg: alexandre_m__41__male__pepper__ref__1__but_bonjour.wav => ["alexandre m", 41, False, "pepper", "ref", 1, "but_bonjour"]
    """
    nNumOccurence = 1
    aSplitted = strFilename.lower().split(".")[0].split("__")
    strSpeakerName = aSplitted[0]
    strAge = aSplitted[1]
    nAge = int(strAge)
    bIsFemale = aSplitted[2].lower() == "female"
    strRecorderName = aSplitted[3]
    strRecordTitle = aSplitted[4]
    strNumOccurence = aSplitted[5]
    nNumOccurence = int(strNumOccurence)
    strComments = ""
    if len( aSplitted ) > 6:
        strComments = aSplitted[6]
    
    strSpeakerName = strSpeakerName.replace( "_", " " )
        
    return [strSpeakerName,nAge, bIsFemale, strRecorderName, strRecordTitle, nNumOccurence, strComments]
# decodeFilename_name_age - end    
#~ print decodeFilename_name_age( "alexandre_m__41__male__pepper__ref__1__but_bonjour.wav" )

def analysePathBase( strPath ):
    """
    analyse the path where are the cleaned sound for audio identification
    TODO: rename this method ! => class...
    """
    dMale = {}
    dFemale = {}
    for file in sorted(os.listdir(strPath)):
        #~ print file
        l = decodeFilename_name_age( file )
        nSize = os.path.getsize( strPath + "/" + file )
        strGender = "Male"
        if( l[2] ):
            strGender = "Female"
        print( "name: %s, age: %s, %s, comments: %s, filesize: %sk" % (l[0], l[1], strGender, l[6], nSize/1024 ) )
        if( l[2] ):            
            dFemale[l[0]] = l[1]            
        else:
            dMale[l[0]] = l[1]
    # for each file - end
    
    print( "dMale (%s): %s" % (len(dMale),dMale) )
    print( "dFemale (%s): %s" % (len(dFemale),dFemale) )
    
#~ analysePathBase( "F:/sounds/voices/2_cleaned/aldebaran_team/" )
#~ exit(0)



class RemotePlayer:
    """
    Play a sound remotely (on a raspberry or ...)
    """
    def __init__( self, strRemoteIP = "localhost", strHostType = "RaspberryWebServer" ):
        self.strRemoteIP = strRemoteIP
        self.strCommandTemplate = "http://%s:8000/playsound?file=%s&volume=%s"
    
    def playfile( self, strSpeakerName, strMessage, strLang = "en", nNumOccurence = 1, nVolume = 100 ):
        # sur les sons alexandre fr, avec le sonometre, a 60 cm
        # (la caisse enleve 20db de l'exterieur)
        # volume en % => db (mesure1-mesure2-...)
        #  3 => 67.8
        # 10 => 65.9-68.7-68.7
        # 30 => 73-74.176.8
        # 50 => 79.1-80.7-81.8
        # 75 => 87.5-88.7-88.8
        # 100 => 94.6-95-96
        strSoundFile = encodeFilename( strSpeakerName, strLang, strMessage, nNumOccurence )
        strSoundFile = "/home/pi/sounds_for_evaluation/%s.wav" % strSoundFile
        strCommand = self.strCommandTemplate % (self.strRemoteIP, strSoundFile, nVolume )
        #~ print( "DBG: RemotePlayer.playfile: strCommand: %s" % strCommand )
        os.system( "wget -q \"%s\" &" % strCommand ) # without the \" the & is taken as a command commuter
        
# class RemotePlayer - end

def autotest_RemotePlayer():
    rp = RemotePlayer("10.0.161.58")
    rp.playfile( "angelica", "hello" )
# autotest_RemotePlayer - end


class SpeechRecognitionTest:
    """
    Launch speech recognition test
    the sound must be manually copied to the raspberry.
    the analysed sounds could be heard from this path: /home/nao/.local/speech_reco_heard/
    """
    def __init__( self, strLocalIP, strRemoteIP ):
        self.strLocalIP = strLocalIP
        self.strRemoteIP = strRemoteIP
        self.asr = False
        
    def __del__( self ):
        self.stopAsr()
        
    def startAsr( self, aListWord, strLang ):
        print( "INF: SpeechRecognitionTest.startAsr: aListWord: %s" % ( str( aListWord ) ) );
        self.aListAsrWords = aListWord

        self.asr = naoqi.ALProxy( "ALSpeechRecognition", self.strLocalIP, 9559 )
        self.tts = naoqi.ALProxy( "ALTextToSpeech", self.strLocalIP, 9559 )
        self.mem = naoqi.ALProxy( "ALMemory", self.strLocalIP, 9559 );

        try:
            self.strExtractorName = "abcdk.SpeechRecognitionTest";
            
            try:
                self.asr.unsubscribe( self.strExtractorName )
            except RuntimeError, err:
                pass
            
            
            strLangName = speech.toSpeakLanguage(speech.fromLangAbbrev( strLang ))
            self.tts.setLanguage( strLangName )
            self.asr.setLanguage( strLangName )
            
            self.asr.setVisualExpression( False ); # True makes infinite recursive call in leds.off()
            strPathFileHeard = "/home/nao/.local/speech_reco_heard/"
            self.asr._enableAudioLogging( strPathFileHeard );
            bEnableWordSpotting = False
            self.asr.setVocabulary( self.aListAsrWords, bEnableWordSpotting );
            self.asr.subscribe( self.strExtractorName );
        except BaseException, err:
            print("ERR: SpeechRecognitionTest.startAsr: can't start Automatic Speech Recognition. Err: %s" % str(err) );
            #~ self.asr.unsubscribe( self.strExtractorName );
            return ""
            
            
        bIsOnRomeo = True
        if( bIsOnRomeo ):
            try:
                # $$$$ patch crado pour le bug de la mémoire partagée sur romeo
                mem_romeo_audio = naoqi.ALProxy( "ALMemory_audio", self.strLocalIP, 9559 );
                mem_romeo_audio.raiseMicroEvent( "WordRecognized", "" );
            except:
                # tu dois pas etre sur un vraiment vrai romeo, c'est pas grave, tu as juste de la chance
                pass
    # startAsr - end
        
    def stopAsr(self):
        try:
            if( self.asr ):
                self.asr.unsubscribe( self.strExtractorName );        
        except BaseException, err:
            #~ print("WRN: SpeechRecognitionTest.stopAsr: can't stop Automatic Speech Recognition. Err: %s" % str(err) );
            pass

            
    def getHeardWord( self, rTimeOut ):
        """
        get heard word. We return word only if confidence > 0.4 or the best choice if timeout is elapsed.
        return [heard word, confidence (0..1), rDuration elapsed]
        """
        print( "INF: SpeechRecognitionTest.getHeardWord: starting (rTimeOut: %5.2fs)" % rTimeOut )
        self.mem.insertData( "WordRecognized", "" );        
        rPeriod = 0.1;
        nNbrChoice = len( self.aListAsrWords )
        timeBegin = time.time()
        rPreviousConf = -1.; # We store it to differenciate between previous answer and a new one
        rBestConfidence = -1.
        strBestWord = ""
        while 1:
            time.sleep( rPeriod );
                
            recognized = self.mem.getData( "WordRecognized" ); # we check it every time, as it could be simulated from an external point
            #~ print( "recognized: %s" % recognized )
            if( recognized != None and len( recognized ) > 1 ):
                strWord = recognized[0]
                rConfidence = recognized[1]
                if( rPreviousConf != rConfidence ):
                    rPreviousConf = rConfidence
                    print( "INF: SpeechRecognitionTest.getHeardWord: received: '%s', conf: %5.3f" % ( strWord, rConfidence ) );
                    # compat 1.22+: Words posted in WordRecognized have changed format: "hello", is now "<...> hello <...>"
                    strWord = strWord.replace( "<...>", "" )
                    strWord = strWord.strip()
                    print( "INF: SpeechRecognitionTest.getHeardWord: received after cleaning: '%s', conf: %5.3f, self.aListAsrWords: %s" % ( strWord, rConfidence, str(self.aListAsrWords) ) );
                    if( rConfidence > 0.4 and strWord in self.aListAsrWords ):
                        strBestWord = strWord
                        rBestConfidence = rConfidence                        
                        break
                    if( rBestConfidence < rConfidence ):
                        strBestWord = strWord                            
                        rBestConfidence = rConfidence
                        
            rDuration = time.time() - timeBegin
            #~ print( "DBG: SpeechRecognitionTest.getHeardWord, waiting for word, time: %5.2fs, best: %s, conf: %f" % (rDuration, strBestWord, rBestConfidence) )
            if( rDuration > rTimeOut ):
                break;
        # while - end
        rDuration = time.time() - timeBegin
        return [strBestWord, rBestConfidence, rDuration]
    # getHeardWord - end
        
        
        
    def run( self, strLang = "en", nNbrLoop = 3 ):
        if( strLang == "en" ):
            aListSpeaker = ["angelica"]
            aListWord = ["hello", "yes", "no", "see you later", "what's for lunch", "what's your name", "how is it going", "have fun", "good morning", "good night"]
        if( strLang == "fr" ):
            aListSpeaker = ["alexandre"]
            aListWord = ["bonjour", "bonjour marco", "bonjour romeo", "comment t'appelles tu", "hello", "quel jour sommes nous", "quelle heure est il", "rodolphe", "samy", "laurent", "alexandre", "natalia"]
            
        rp = RemotePlayer( self.strRemoteIP )
        rTimeOut = 5.
        nNbrGood = 0
        nNbrTested = 0
        rSumConfidence = 0.
        rSumDuration = 0.
        aListVolumeToTest = [2,3,4,5,6,7,8,9, 10, 12, 14, 16, 18, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
        #~ aListVolumeToTest = [10, 100]
        aDetailedResults = "";
        for nNumLoop in range(nNbrLoop):
            for nVolumePercent in aListVolumeToTest:
                print( "\nINF: getHeardWord.run: launching a test with volume: %d%%\n" % nVolumePercent )
                strSpeaker = aListSpeaker[0]
                self.startAsr(aListWord, strLang)
                time.sleep( 1. ) # wait for end of bip
                nPerVolumeNbrGood = 0
                nPerVolumeNbrTested = 0
                rPerVolumeSumConfidence = 0
                for word in aListWord:
                    print( "INF: getHeardWord.run: " + "*"*65 )
                    print( "INF: getHeardWord.run: launching a test with %s on word: '%s'" % (strSpeaker, word) )
                    rp.playfile( strSpeaker, word, strLang, 1, nVolumePercent )
                    strHeardWord, rConfidence, rDuration = self.getHeardWord(rTimeOut)
                    print( "INF: getHeardWord.run: expected: %s, recognised: %s, %5.2f, duration: %5.2fs" % (word, strHeardWord, rConfidence, rDuration) )
                    nPerVolumeNbrTested += 1
                    if( word == strHeardWord ):
                        print( "INF: getHeardWord.run: GOOD !" )
                        nPerVolumeNbrGood += 1
                        rPerVolumeSumConfidence += rConfidence
                        rSumDuration += rDuration
                    time.sleep( 1. ) # wait for end of bip
                 # for word - end
                strOut = "\t# results for volume: %d%%\n" % nVolumePercent
                strOut += "\t# good: %d/%d (%3d%%)\n" % (nPerVolumeNbrGood, nPerVolumeNbrTested, nPerVolumeNbrGood*100/nPerVolumeNbrTested)
                if( nPerVolumeNbrGood > 0 ):
                    strOut += "\t# avg conf: %5.2f\n" % (rPerVolumeSumConfidence/nPerVolumeNbrGood)
                    
                strOut += "\t#\n"                
                print( "\nINF: getHeardWord.run:\n" + strOut )
                aDetailedResults += strOut
                 
                nNbrTested += nPerVolumeNbrTested
                nNbrGood += nPerVolumeNbrGood
                rSumConfidence += rPerVolumeSumConfidence
                self.stopAsr()
            # for volume - end
        # for loop - end

        # detail
        print( "\n\nDetailed results:\n" + aDetailedResults )

        # sum up
        print( "\nINF: getHeardWord.run: results:\n" )
        print( "\t# good: %d/%d (%3d%%)" % (nNbrGood, nNbrTested, nNbrGood*100/nNbrTested) )
        if( nNbrGood > 0 ):
            print( "\t# avg conf: %5.2f" % (rSumConfidence/nNbrGood) )
            print( "\t# avg duration: %5.2fs" % (rSumDuration/nNbrGood) )
        
        
        #
        # RÃ©sultats obtenues sur 10 runs. Dans le cas ou on fait plusieurs fois 10 runs, on garde le meilleur ou on met les extremes
        # (effectivement on ne devrait pas avoir de diffÃ©rence notable, c'est triste)
        #
        
        #
        # Avec ancienne A41:
        #
        
        # at 60cm:
        # en
        # good: 100/100 (100%)
        # avg conf:  0.54
        # avg duration:  1.82s
        #
        # fr
        # good: 120/120 (100%)
        # avg conf:  0.58
        # avg duration:  1.77s
        
        # at 1m:
        # en
        # good: 75/100 ( 75%) / 79
        # avg conf:  0.54
        # avg duration:  1.54s
        #
        # fr
        # good: 120/120 (100%)
        # avg conf:  0.59
        # avg duration:  1.80s
        
        # at 1 m with reverb (plastic card):
        # en
        # good: 73/100 ( 73%)
        # avg conf:  0.55
        # avg duration:  1.69s
        # fr
        # good: 120/120 (100%)
        # avg conf:  0.61
        # avg duration:  1.77s
        

     
        
        
        
        #
        # Nouvelle carte micro avec B01:
        #
        # 60cm:
        # en
        #~ good: 100/100 (100%)
        #~ avg conf: 0.60
        #~ avg duration: 1.55s
        
        # fr
        #~ good: 120/120 (100%)
        #~ avg conf: 0.61 / 0.6
        #~ avg duration: 1.89s / 1.95
        
        # at 1 m with reverb (plastic card):        
        # en
        # good: 90/100 ( 90%)
        # avg conf:  0.59
        # avg duration:  1.77s        
        # fr
        # good: 120/120 (100%)
        # avg conf:  0.60
        # avg duration:  1.94s


        #
        # resultats en cours
        # 
        # good: 120/120 (100%)
        # avg conf:  0.61
        # avg duration:  1.94s
        

        # good: 120/120 (100%)
        # avg conf:  0.62
        # avg duration:  1.91s
        
# SpeechRecognitionTest - end

def process_SpeechRecognitionTestResults( strFilename ):
    """
    when results of SpeechRecognitionTest are in a file. Process them to generate a csv
    """
    with open(strFilename, "rt") as file:
        buf = file.read()
        file.close()
        lines = buf.split("\n")
        dRes = dict()
        for line in lines:
            #~ print line
            line = line.strip()
            strBeginResult = "# results for volume: "
            strPercentGood = "# good: "
            if strBeginResult in line:
                strEnd = line[len(strBeginResult):]
                strEnd = strEnd.split("%")[0]
                nPercent = int( strEnd )
            elif strPercentGood in line:
                strEnd = line[len(strPercentGood):]
                strEnd = strEnd.split("/")[0]
                nGood = int( strEnd )
                print( "%d%% => %d" % (nPercent, nGood) )
                strKey = "%5.3f" % (nPercent/100.)
                try:
                    dRes[strKey] += nGood
                except KeyError:
                    dRes[strKey] = nGood
                
            else:
                pass
                
    print dRes
    strOut = ""
    
    for key in sorted(dRes.keys()):
        print key
    for key in sorted(dRes.keys()):
        print dRes[key]   
        
    nSum = 0
    for key in sorted(dRes.keys()):
        strOut += "%s, %d\n" % (key, dRes[key])
        nSum += dRes[key]
        
    print( "sum: %d" % nSum )
        
    return strOut
    
print process_SpeechRecognitionTestResults( "/tmp2/pepper_preamp_en.txt" )
exit(1)
    

def autorun_SpeechRecognitionTest( strRemoteIP = "10.0.161.47", strLang = "en", nNbrLoop = 2):
    """
    - strRemoteIP: the IP of the raspberry broadcasting wav file
    to launch me from a robot: 
    python -c "import abcdk.sound_evaluation;abcdk.sound_evaluation.autorun_SpeechRecognitionTest(strLang = 'en', nNbrLoop = 2)"
    """
    srt = SpeechRecognitionTest( "localhost", strRemoteIP )
    srt.run(strLang, nNbrLoop)
    
# autorun_SpeechRecognitionTest - end    

def autotest():
    autotest_decodeFilename()
    autotest_RemotePlayer()
# autotest - end    


if __name__=="__main__":
    autotest();
    