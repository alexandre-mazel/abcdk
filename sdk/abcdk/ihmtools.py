# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# method to help constructing some ihm dialog (choice, ...)
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################


"""Tools to work with net, web, ftp, ping..."""

print( "importing abcdk.ihmtools" );

import bodytalk
import leds
import naoqitools
import speech
import sound.play
import system
import translate
import typetools

import time



global_ihmtools_choice_in = False;
global_ihmtools_choice_listChoice = None;


def choice( strQuestion, listChoice, rTimeOut = 12., nDefaultSelection = -1, bUseSpeechReco = True, bRepeatChoosenAnswer = True, bEnableWordSpotting = True, bActivateChoiceProposal = False, astrJointsToExclude = [], bUseDisplay =  True, listSpecificDisplay = None , bTrackFace = False, rConfidenceThreshold = 0.4 ):
    """
    generate a choice to ask user to choose one thing
    return the choice [idx,choice] or None on cancel/timeout with idx is in [0..n-1]
    strQuestion: question to ask user
    listChoice: list of possible things a list or a string separated by ';'
    rTimeOut: in seconds
    nDefaultSelection: pre-selected choice
    bUseSpeechReco: did we use the speech reco ?
    """
    print( "INF: ihmtools.choice: strQuestion: %s, listChoice: %s, rTimeOut: %f, bActivateChoiceProposal: %s, astrJointsToExclude: %s" % ( str( strQuestion ), str( listChoice ), rTimeOut, str(bActivateChoiceProposal), astrJointsToExclude ) );
    global global_ihmtools_choice_in;    
    if( global_ihmtools_choice_in ):
        print("INF: ihmtools.choice: reentering while running, is a bad idea, outputting a None..." );
        return None;
    global_ihmtools_choice_in = True;
    
    if( typetools.isString( listChoice ) ):
        listChoice = listChoice.split( ";" );
    if( listChoice[-1] == "" ):
        listChoice.pop(); 
                
    for i in range(len(listChoice)):
        listChoice[i] = listChoice[i].strip();
        
    if( bActivateChoiceProposal ):
        # add sentences like
        pass 
    global global_ihmtools_choice_listChoice;
    global_ihmtools_choice_listChoice = listChoice;
    mem = naoqitools.myGetProxy( "ALMemory" );
    mem.insertData( "abcdk/ihmtools/choice_stop", False );
    mem.insertData( "WordRecognized", "" );    
    tts = naoqitools.myGetProxy( "ALTextToSpeech" );
    nSelection = nDefaultSelection;
    if( nDefaultSelection != -1 ):
        nNewSelection = nDefaultSelection;
    else:
        nNewSelection = 0;
    if( not bUseSpeechReco ):
        nSelection = -1; # so the current selection will be said
    else:
        nSelection = nNewSelection; # don't tell current choice

    if( len( strQuestion ) > 1 ):
        #leds.setFavoriteColorEyes( True );
        #tts.say( speech.getTextWithCurrentSpeed(strQuestion) );  # why didn't we use the speech with light? or bodytalk ?
        bodytalk.bodyTalk.run( strQuestion, bWaitEndOfRestMovement = False, astrJointsToExclude = astrJointsToExclude ,bUseHead = False, bTrackFace = bTrackFace);

    if bUseDisplay:
        import html_manager
        mem.insertData("tabletResponse","")
        if( listSpecificDisplay == None ):
            html_manager.showHTMLQuestion(strQuestion,listChoice)        
        else:
            html_manager.showHTMLQuestion(strQuestion,listSpecificDisplay)        

    if( bUseSpeechReco ):
        try:        
            strExtractorName = "abcdk.ihmtools";
            asr = naoqitools.myGetProxy( "ALSpeechRecognition" );
            asr.setVisualExpression( True );
            asr.setAudioExpression( False );
            asr.setVocabulary( listChoice, bEnableWordSpotting );
            print( "avant*****************************************" );
            asr.subscribe( strExtractorName );
            print( "apres******************************************" );
        except BaseException, err:
            print("WRN: ihmtools.choice: can't start Automatic Speech Recognition. Using only tactile sensors... err: %s" % str(err) );
            bUseSpeechReco = False; # error occurs, bad...
        
    if( not bUseSpeechReco ):
        sound.play.playSound( "bipReco13.wav" ); 
        sound.play.playSound( "/usr/share/naoqi/wav/begin_reco.wav" ); # depuis la 2.0.x, le nom a changé $$$$ todo: retrocompatibilité plus propre ?
        sound.play.playSound( "/opt/aldebaran/share/naoqi/wav/begin_reco.wav" ) # depuis la 2.5.x, le nom a changé $$$$ todo: retrocompatibilité plus propre ?
        mem.insertData( "WordRecognized", "" ); # for the simulated choice case
        
    if( system.isOnRomeo() ):
        try:
            # $$$$ patch crado pour le bug de la mémoire partagée sur romeo
            mem_romeo_audio = naoqitools.myGetProxy( "ALMemory_audio" );
            mem_romeo_audio.raiseMicroEvent( "WordRecognized", "" );
        except:
            # tu dois pas etre sur un vraiment vrai romeo, c'est pas grave, tu as juste de la chance
            pass

    # loop on tactile
    bFinished = False;
    rDCM_Period = 0.01;
    nNbrChoice = len( listChoice );
    timeBegin = time.time();
    rPreviousConf = -1.; # We store it to differenciate between previous answer and a new one
    bFirstErrorTactile = True;
    while( not bFinished ): # do some test to read an ALMemory that will send us the info, that the box is finished.
        time.sleep( rDCM_Period/2. );
        try:
            bFront = mem.getData( "Device/SubDeviceList/Head/Touch/Front/Sensor/Value" ) > 0.5; # was FrontTactilTouched
            bMiddle = mem.getData( "Device/SubDeviceList/Head/Touch/Middle/Sensor/Value" ) > 0.5;
            bRear = mem.getData( "Device/SubDeviceList/Head/Touch/Rear/Sensor/Value" ) > 0.5;
            bUserCancel = bFront and bMiddle and bRear; # BUG1: hard to realize, because of the time, and it doesn't works if user press slightly at the center to begin.
            # BUG2: because we're just reading the event and not directly the DCM, it's impossible to realize.
        except BaseException, err:
            if( bFirstErrorTactile ):
                print( "on romeo, it could arrive, we doesn't have this data in the memory: %s" % str(err) );
                bFirstErrorTactile = False;
            bFront = bMiddle = bRear = bUserCancel = False;
        
        if( bFront or bMiddle or bRear ):
            print( "INF: ihmtools.choice: touched: %s, %s, %s => user cancel: %s" % (str(bFront), str(bMiddle), str(bRear), str(bUserCancel)) );
            if( bUseSpeechReco ):
                bUseSpeechReco = False;                
                asr.unsubscribe( strExtractorName );


        if( bUserCancel ):
            print( "INF: ihmtools.choice: strQuestion: %s, listChoice: %s,  rTimeOut: %f => USER CANCEL" % ( str( strQuestion ), str( listChoice ), rTimeOut ) );
        else:
            if( bMiddle ):
                bFinished = True;
            elif( bFront ):
              nNewSelection = nSelection + 1;
              timeBegin += 4.; # each choice add a small time amount
            elif( bRear ):
              nNewSelection = nSelection -1;
              timeBegin += 4.; # each choice add a small time amount
        if( nNewSelection != nSelection ):
            if( nNewSelection < 0 ):
                nNewSelection += nNbrChoice;
            elif( nNewSelection >= nNbrChoice ):
                nNewSelection -= nNbrChoice;
            nSelection = nNewSelection;
            print( "INF: ihmtools.choice: current selection: %d" % nSelection );
            tts.say( listChoice[nSelection] + " ?" );
        bCancel = mem.getData( "abcdk/ihmtools/choice_stop" )
        if( bCancel or bUserCancel ):
            bFinished = True;
        if( time.time() > timeBegin + rTimeOut ):
            bFinished = True;
            nSelection = -1;
            
        recognized = mem.getData( "WordRecognized" ); # we check it every time, as it could be simulated from an external point
        #~ print( "recognized: %s" % recognized );
        if( recognized != None and len( recognized ) > 1 ):
            strWord = recognized[0];
            rConfidence = recognized[1];
            if( rPreviousConf != rConfidence ):
                rPreviousConf = rConfidence;
                print( "INF: ihmtools.choice: received: '%s', conf: %5.3f" % ( strWord, rConfidence ) );
                # compat 1.22+: Words posted in WordRecognized have changed format: "hello", is now "<...> hello <...>"
                strWord = strWord.replace( "<...>", "" );
                strWord = strWord.strip();
                #~ print( "INF: ihmtools.choice: received after cleaning: '%s', conf: %5.3f, listChoice: %s" % ( strWord, rConfidence, str(listChoice) ) );
                if( rConfidence > rConfidenceThreshold and strWord in listChoice ):
                    nSelection = listChoice.index( strWord );
                    bFinished = True;
                else:
                    timeBegin = time.time();
            #~ time.sleep( 0.1 ); # in 1.22.x: the string is never resetted, so we enter this very often. We add this sleep to let him breath a bit (that's sad because so, we could miss some tactile event...) (but if we're there, we are in speech mode, so don't worry)


        if bUseDisplay:
            strWord = mem.getData("tabletResponse")
            #print( "qsdqsd strWord:%s" % strWord)
            if( strWord in listChoice ):
                nSelection = listChoice.index( strWord );
                #print( "nSelection:%s" % nSelection)
                bFinished = True;

    # while - end
    if( bUseSpeechReco ):
        asr.unsubscribe( strExtractorName );    
    else:        
        sound.play.playSound( "bipReco14.wav" );
        sound.play.playSound( "/usr/share/naoqi/wav/end_reco.wav" );
        sound.play.playSound( "/opt/aldebaran/share/naoqi/wav/end_reco.wav" );
    global_ihmtools_choice_in = False;
    if( nSelection == -1 ):
        if( tts.getLanguage() == 'French' ):
            tts.say( "Trop tard!" );
        elif( tts.getLanguage() == 'German' ):
            tts.say( "Zu spet!" );
        else:
            tts.say( "Time out!" );
        print( "INF: ihmtools.choice: strQuestion: %s, listChoice: %s,  rTimeOut: %f => TIME OUT" % ( str( strQuestion ), str( listChoice ), rTimeOut ) );
        return None;
    if( bCancel ):
        print( "INF: ihmtools.choice: strQuestion: %s, listChoice: %s,  rTimeOut: %f => CANCELED" % ( str( strQuestion ), str( listChoice ), rTimeOut ) );
        return None;
    if( bRepeatChoosenAnswer ):
        tts.say( listChoice[nSelection] + "." );
    print( "INF: ihmtools.choice: strQuestion: %s, listChoice: %s,  rTimeOut: %f => %d, %s" % ( str( strQuestion ), str( listChoice ), rTimeOut, nSelection, listChoice[nSelection] ) );

    if bUseDisplay:
        # Hide question and response of the web view
        html_manager.sendHumanAnswerToQuestion(listChoice[nSelection])
    return [nSelection,listChoice[nSelection]];
#choice - end



def choiceStopAll():
    "stop all running choice menu (it would be silly to have more than one at a time"
    mem = naoqitools.myGetProxy( "ALMemory" );
    mem.insertData( "abcdk/ihmtools/choice_stop", True );
# choiceStopAll - end

def choiceSimulateHeard( nIdxChoice ):
    nIdxChoice = int(nIdxChoice);
    print( "INF: ihmtools.choiceSimulateHeard: nIdxChoice: %d" % nIdxChoice );
    global global_ihmtools_choice_listChoice;
    mem = naoqitools.myGetProxy( "ALMemory" );
    strWord = global_ihmtools_choice_listChoice[nIdxChoice];
    print( "INF: ihmtools.choiceSimulateHeard: strWord: %s" % strWord );
    mem.raiseMicroEvent( "WordRecognized", [strWord,1.] );
    try:
        # $$$$ patch crado pour le bug de la mémoire partagée sur romeo
        mem_romeo_audio = naoqitools.myGetProxy( "ALMemory_audio" );
        mem_romeo_audio.raiseMicroEvent( "WordRecognized", [strWord,1.] );
    except:
        # tu dois pas etre sur un romeo, c'est pas grave, tu as juste de la chance
        pass

def askConfirmation( strQuestion, rTimeOut = 12., bAskConfirmation = False, bRepeatChoosenAnswer = True, bUseDisplay = True ):
    """
    ask user to confirm something.
    return 1 if it confirms, -1 if not, or any values between that two choices; or None on cancel/timeout
    - bAskConfirmation: ask a second time for confirmation
    """
    if( bAskConfirmation ):
        while( True ):
            retValChoosen = askConfirmation( strQuestion, rTimeOut = rTimeOut, bUseDisplay=bUseDisplay );
            if( retValChoosen == None  ):
                return None;
            if( abs(retValChoosen) < 0.5 ):
                return retValChoosen;
            d = {
                "fr":  "Es tu sur d'avoir fait le bon choix ?",
                "en":   "Are you sure of your choice ?",
            };
            strQuestionConfirmation = translate.chooseFromDict( d );
            retValConfirmation = askConfirmation( strQuestionConfirmation, rTimeOut = rTimeOut, bRepeatChoosenAnswer = False, bUseDisplay = bUseDisplay );
            if( retValConfirmation == None ):
                return None;
            if( abs(retValConfirmation) < 0.5 ):
                return 0.;
            if( retValConfirmation > 0. ):
                return retValChoosen;
            # else, re-ask it
            d = {
                "fr":  "ok, alors je te repose la question:",
                "en":  "ok, so I ask you again:",
            };
            strTxt = translate.chooseFromDict( d );
            speech.sayAndLight( strTxt, 1 );
            # looping
        # while - end
    # ask confirm - end
        
    #~ yesnoMultilang = {
        #~ "fr": ["oui","non"], 
        #~ "en": ["yes","no"], 
        #~ "ko": ["ie","anyo"],
        #~ "de": ["ja","nein"],
        #~ "ch": ["chiais","mé-io"],
        #~ "jp": ["aille","iiai"],
    #~ };
    #~ choices = translate.chooseFromDict( yesnoMultilang );
    listChoiceWithRatio = translate.getListYesNo();
    #~ print( "listChoiceWithRatio: " % listChoiceWithRatio );
    listChoice = [ a[0] for a in listChoiceWithRatio ];
    retVal = choice( strQuestion, listChoice, rTimeOut, bRepeatChoosenAnswer = bRepeatChoosenAnswer, listSpecificDisplay = ["oui", "non"], bUseDisplay=bUseDisplay );
    if( retVal != None ):
        rVal = listChoiceWithRatio[retVal[0]][1];
        print( "INF: ihmtools.askConfirmation: get idx: %s='%s' => val: %s" % (retVal[0], retVal[1], rVal ) );
        return rVal;
    return retVal;
# askConfirmation - end

def askConfirmationStopAll():
    choiceStopAll();
# askConfirmationStopAll - end


global_ihmtools_waitAskInteraction_in = False
global_waitAskInteraction_simulate = -1;

def waitAskInteraction( rTimeOut = 12., bRepeatChoosenAnswer = True,  rConfidenceThreshold = 0.4 ):
    """
    wait for a message from the user "hello / could you help me / ..."
    return [nType, strMsg] with:
    nType:
        - 0: no ask for interaction (cancel or timeout)
        - 1: user say something like hello
        - 2: user say something like how are you ?
        - 3: user ask for help
        - 4: user say something ?
    strMsg: the sentence said by the user
    
    """
    print( "INF: ihmtools.waitAskInteraction: rTimeOut: %f" % rTimeOut );
    global global_ihmtools_waitAskInteraction_in;  
    global global_waitAskInteraction_simulate;
    if( global_ihmtools_waitAskInteraction_in ):
        print("INF: ihmtools.choice: reentering while running, is a bad idea, outputting a None..." );
        return None;
    global_ihmtools_waitAskInteraction_in = True;
    global_waitAskInteraction_simulate = -1;

    mem = naoqitools.myGetProxy( "ALMemory" );
    mem.insertData( "WordRecognized", "" );    
    mem.insertData( "abcdk/ihmtools/wait_ask_interaction_stop", False );    
    
    tts = naoqitools.myGetProxy( "ALTextToSpeech" );
    
    # NB: all the dictionnary must be in lower text!
    dHello = {
        "fr":  ["bonjour","bonsoir","hello","salut","coucou"],
        "en":   ["good morning","good night","hello","hi"],
    };
    
    dHowAreYou = {
        "fr":  ["comment ça va","comment va tu","ça va","ça boume"],
        "en":  ["how are you","howdy"],
    };
    
    dQuestion = {
        "fr":  ["pourriez vous m'aider","aide moi","question","s'il te plait","s'il vous plait"],
        "en":  ["could you help me","help","please"],
    };
    
    listChoice = [];
    listChoice.extend( translate.chooseFromDict( dHello ) );
    listChoice.extend( translate.chooseFromDict( dHowAreYou ) );
    listChoice.extend( translate.chooseFromDict( dQuestion ) );    

    try:        
        strExtractorName = "abcdk.ihmtools";
        asr = naoqitools.myGetProxy( "ALSpeechRecognition" );
        asr.setVisualExpression( True );
        asr.setVocabulary( listChoice, True );
        print( "avant*****************************************" );
        asr.subscribe( strExtractorName );
        print( "apres******************************************" );
    except BaseException, err:
        print("WRN: ihmtools.choice: can't start Automatic Speech Recognition. Using only tactile sensors... err: %s" % str(err) );
        bUseSpeechReco = False; # error occurs, bad...
        
    try:
        # $$$$ patch crado pour le bug de la mémoire partagée sur romeo
        mem_romeo_audio = naoqitools.myGetProxy( "ALMemory_audio" );
        mem_romeo_audio.raiseMicroEvent( "WordRecognized", "" );
    except:
        # tu dois pas etre sur un romeo, c'est pas grave, tu as juste de la chance
        pass
        

    # loop on tactile
    bFinished = False;
    rDCM_Period = 0.01;
    timeBegin = time.time();
    rPreviousConf = -1.; # We store it to differenciate between previous answer and a new one
    bFirstErrorTactile = True;
    nType = 0;
    strMsg = "";
    while( not bFinished ): # do some test to read an ALMemory that will send us the info, that the box is finished.
        time.sleep( rDCM_Period/2. );
        try:
            bFront = mem.getData( "Device/SubDeviceList/Head/Touch/Front/Sensor/Value" ) > 0.5; # was FrontTactilTouched
            bMiddle = mem.getData( "Device/SubDeviceList/Head/Touch/Middle/Sensor/Value" ) > 0.5;
            bRear = mem.getData( "Device/SubDeviceList/Head/Touch/Rear/Sensor/Value" ) > 0.5;
            bUserCancel = bFront and bMiddle and bRear; # BUG1: hard to realize, because of the time, and it doesn't works if user press slightly at the center to begin.
            # BUG2: because we're just reading the event and not directly the DCM, it's impossible to realize.
        except BaseException, err:
            if( bFirstErrorTactile ):
                print( "on romeo, it could arrive, we doesn't have this data in the memory: %s" % str(err) );
                bFirstErrorTactile = False;
            bFront = bMiddle = bRear = bUserCancel = False;
        
        if( bFront or bMiddle or bRear ):
            break;
            
        bCancel = mem.getData( "abcdk/ihmtools/wait_ask_interaction_stop" )
        if( bCancel ):
            nType = 4;
            break;      

        #~ print( "global_waitAskInteraction_simulate: %s" % global_waitAskInteraction_simulate );
        if( global_waitAskInteraction_simulate != -1 ):
            nType = global_waitAskInteraction_simulate;
            break;
            
        recognized = mem.getData( "WordRecognized" ); # we check it every time, as it could be simulated from an external point
        #~ print( "recognized: %s" % recognized );
        if( recognized != None and len( recognized ) > 1 ):
            strWord = recognized[0];
            rConfidence = recognized[1];
            if( rPreviousConf != rConfidence ):
                rPreviousConf = rConfidence;
                print( "INF: ihmtools.choice: received: '%s', conf: %5.3f" % ( strWord, rConfidence ) );
                # compat 1.22+: Words posted in WordRecognized have changed format: "hello", is now "<...> hello <...>"
                strWord = strWord.replace( "<...>", "" );
                strWord = strWord.strip();
                #~ if( strWord[-1] == "?" ):
                    #~ strWord = strWord[:-1];
                #~ print( "INF: ihmtools.choice: received after cleaning: '%s', conf: %5.3f, listChoice: %s" % ( strWord, rConfidence, str(listChoice) ) );
                if( ( rConfidence > rConfidenceThreshold and strWord in listChoice) or rConfidence > rConfidenceThreshold*1.5 ):
                    strMsg = strWord;
                    bFinished = True;
                else:
                    timeBegin = time.time();
            #~ time.sleep( 0.1 ); # in 1.22.x: the string is never resetted, so we enter this very often. We add this sleep to let him breath a bit (that's sad because so, we could miss some tactile event...) (but if we're there, we are in speech mode, so don't worry)
    # while - end
    asr.unsubscribe( strExtractorName );
    
    global_ihmtools_waitAskInteraction_in = False;
    
    if( strMsg != "" ):
        aList = [translate.chooseFromDict( dHello ), translate.chooseFromDict( dHowAreYou ), translate.chooseFromDict( dQuestion )];
        for i in range(len(aList)):
            for item in aList[i]:
                #~ print( "DBG: ihmtools.waitAskInteraction: comparing'%s' and '%s' from list %d" % (item,strMsg,i) );
                if( item in strMsg.lower() ):
                    print( "DBG: ihmtools.waitAskInteraction: '%s' found in '%s' from list %d" % (item,strMsg,i) );
                    nType = i+1;
                    break;
            if( nType != 0 ):
                # found it in the current list
                break;
        else:
            nType = len(aList); # => unknown
    print( "INF: ihmtools.waitAskInteraction: exiting with [%s,%s]" % (nType, strMsg) );
        
    return [nType, strMsg];
# waitAskInteraction - end

def waitAskInteraction_stopAll():
    mem = naoqitools.myGetProxy( "ALMemory" );
    mem.insertData( "abcdk/ihmtools/wait_ask_interaction_stop", True ); # we use an ALMemory variable to prevent missing a signal, related to some reloading of the lib or ...
    
def waitAskInteraction_simulate(nChoice):
    global global_waitAskInteraction_simulate;
    print( "INF: ihmtools.waitAskInteraction_simulate: simulating a choice %d" % (nChoice) );
    global_waitAskInteraction_simulate = nChoice;

