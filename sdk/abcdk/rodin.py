# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Mind Tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################


"""Tools to work with minde and decision..."""

print( "importing abcdk.rodin" );

import actors
import filetools
import html_manager
import music_manager
import naoqitools
import sentence_generator
import stringtools
import speech
import text_comprehension
import ticket
import translate
import naoqitools
import random
import time

import sys
reload(sys)  
sys.setdefaultencoding('Cp1252')

class Rodin:
    def __init__( self ):
        self.tm = ticket.ticketsManager
        self.am = actors.actorsManager
        self.mm = music_manager.songManager
        self.sg = sentence_generator.SentenceGeneratorFr()
        self.flagMute = False
        self.configureFaceDetection()
        try :
            import pepper_bot
            self.ppb = pepper_bot.PepperBot()
        except:
            print "WRG : Rodin : __init__ : we can't import pepper_bot. Check if aiml is installed and if you have the file pepper_bot on your robot. If you don't have this file, it is in appu_shared/sdk/install_hopias. Just do a scp of this file on your robot."
            self.ppb = None
            
    def pepperBotSay(self, text):
        if self.ppb == None :
            return
        answer = self.ppb.askPepperBot(text)
        if answer != None:
            speech.sayAndLight( answer );
            file = open("/home/nao/pepper_bot/save_discuss.txt" ,'a')
            file.write('"%s",\n"%s",\n' %(text,str(answer)))
            file.close()
        pass

    def configureFaceDetection( self ):
        try:
            fr = naoqitools.myGetProxy( "ALFaceDetection" )
            #~ strFullImagePath = "/home/nao/events/" # takes too much time on old robots!
            strFullImagePath = "/home/nao/abcdk_debug/rec_faces/"
            fr.setSaveImagePaths( strFullImagePath, "/tmp/rec_faces_cropped/" )
        except BaseException, err:
            print( "ERR: Rodin.configureFaceDetection: err: %s" % err )
        
        
    def generateSentence( self, tic ):
        actorsId = tic.source
        listActors = self.am.getActors( actorsId = actorsId )
        if( listActors != None and len(listActors) > 0 ):
            actor = listActors[0]
            strOptionnalName = actor.firstName
        else:
            strOptionnalName = "quelqu'un"
            
        
        s = self.sg.generate( 3 , tic.action, tic.verite, strOptionnalName = strOptionnalName )
        s += " " + tic.objet
        return s
        
    def outputToEventFolder( self, txt, nNumSource, strTypeTxt = "no_type" ):
        """
        """
        txt = stringtools.convertForFilename( txt )
        strFilename = filetools.getFilenameFromTime() + "__txt__" + strTypeTxt + "__" + txt + ".txt"
        file = open( "/home/nao/events/" + strFilename, "wt" )
        file.write( txt )
        file.close()
        
        
    def saySomething( self ):
        if self.flagMute :
            print "Mute robot in saySomething because of the flag."
            return
        else:
            self.flagMute = True 
            source = actors.actorsManager.getCurrentActor()

            if( source == None or source == -1 ):
                print( "DBG: rodin: saySomething: nothing to do: source: %s" % source )
                self.flagMute = False
                return
            listActors = self.am.getActors( actorsId = source )
            if( listActors == None or len(listActors) < 1 ):
                print( "DBG: rodin: saySomething: nothing to do: listActors: %s" % listActors )
                self.flagMute = False
                return
             
            actor = listActors[0]
            strOptionnalName = actor.firstName
            
            alea = [1,2,3,4]
            random.shuffle(alea)
            if alea[0] != 1:
                # s = self.sg.generate( 3, tic.action, tic.verite, strOptionnalName = strOptionnalName ) TODO: generation
                # TODO: refactor !!!
                obj = translate.chooseFromDictRandom( { "fr": "les haricots/manger/jouer/programmer/les poulets/la viande/le foot/la course a pied/la musique/boire/jouer aux jeux video/faire des blagues/les poireaux/les hommes/les femmes/les enfants"} )
                ticketQuestion = self.tm.askRandomQuestion(source, "aimer")
                if ticketQuestion != None:
                    obj =  ticketQuestion.objet 
                    print "newQuestion with ticket :" + str(ticketQuestion.objet) + " " + str(ticketQuestion.getData())
                s = str(strOptionnalName) + ", aimes tu " + str(obj) + "?"
                tic = ticket.Ticket( action = "aimer", source = source, objet = obj, isQuestion = True )  

            else :
                s = str(strOptionnalName) +", Que fais-tu ?"
                tic = ticket.Ticket( action = "faire", source = source, isQuestion = True ) 

            speech.sayAndLight( s );
            
                  
            self.tm.createNewTicket( tic )
            self.am.addTicket( source, tic )
            self.flagMute = False
            
    # saySomething - end
        
            
            
        
    def handleFreeText( self, txt ):
        import qi
        html_manager.sendHumanSay(txt)
        
        cmd_music = self.handleMusic(txt)

        if self.handleTime(txt):
            return

        if self.handleDate(txt) :
            return

        if self.handleYesNo(txt) :
            return

        if self.handleWhatDoYouDo(txt):
            return

        if self.handleNews(txt):
            return

        if self.handleVideo(txt):
            return

        nNumSource = actors.actorsManager.getCurrentActor()
        
        self.outputToEventFolder( txt, nNumSource, "free_text" )

        if self.flagMute :
            return 
        else:
            tic = text_comprehension.textComprehension.analyse( txt )
            if( tic != None ):
                tic.source = actors.actorsManager.getCurrentActor()
                print( "DBG: handleFreeText: add tic: %s" % tic )
                self.tm.createNewTicket( tic )
                self.am.addTicket( tic.source, tic )

                # comment
                self.flagMute = True
                """s = self.generateSentence( tic )
                speech.sayAndLight( s );"""
                self.smartSay(tic)
                self.flagMute = False
                return
        if cmd_music:
            return
        self.pepperBotSay(txt) 
                     

    def handleTime(self, txt , city = "Paris", phoneticTresh = 0.8):
        triggerList = ["Quel heure est-il","Donne moi l'heure", "il est quel heure"]
        bAskTime = False
        for tmpTriggerList in triggerList:
            if stringtools.isPhoneticEqual(txt,tmpTriggerList) >= phoneticTresh:
                bAskTime = True
        if bAskTime : 
            timeZone = naoqitools.myGetProxy("ALSystem")
            timeZone.timezone
            timeZone.setTimezone("Etc/Universal")

            # choose the city of your timezone
            # Paris in default
            fuseau = 1;
            if city == "Paris":
                fuseau = 1;
            if city == "London":
                fuseau = 0;
            if city == "Los Angeles":
                fuseau = -8;
            if city == "Chicago":
                fuseau = -6;
            if city == "New York":
                fuseau = -5;
            if city == "Halifax":
                fuseau = -4;
            if city == "Le Cap":
                fuseau = 2;
            if city == "Séoul":
                fuseau = 9;
            if city == "Melbourne":
                fuseau = 10;
            if city == "Tokyo":
                fuseau = 9;

            fuseau = fuseau +1

            H = time.strftime("%H")
            H = int(H) + fuseau

            if H > 24:
                H = H - 24;
            if H < 0 :
                H = 24 + H;

            strTime = time.strftime(":%M:%S")
            strTime = str(H)+strTime
            hour = speech.transcriptTime(strTime, -1,True, True)

            dic = {
                "fr": "Il est ",
                "en": "It's ",
            };

            strTxt = translate.chooseFromDict( dic )+ hour
            speech.sayAndLight( strTxt )
            return 1
        else:
            return 0

    def handleDate(self, txt , phoneticTresh = 0.8):
        triggerList = ["Quel jour sommes nous","Donne moi la date", "Quel est la date d'aujourd'hui"]
        bAskDate = False
        for tmpTriggerList in triggerList:
            if stringtools.isPhoneticEqual(txt,tmpTriggerList) >= phoneticTresh:
                bAskDate = True
        if bAskDate : 
            getdate = time.localtime();
            strDate = str(getdate.tm_year) +"/"+str(getdate.tm_mon)+"/"+str(getdate.tm_mday);
            date = speech.transcriptDate(strDate);

            dic = {
                "fr": "Nous sommes le ",
                "en": "Today is ",
            }

            day = speech.transcriptWeekDay(getdate.tm_wday)
            strTxt = translate.chooseFromDict( dic )+ day +" "+date
            speech.sayAndLight( strTxt )
            return 1
        else :
            return 0


    def handleNews(self, txt, phoneticTresh = 0.8):
        if self.flagMute :
            return 0

        else :
            if stringtools.isPhoneticEqual(txt , "donne moi une nouvelle")>= phoneticTresh:
                self.flagMute = True
                news = ticket.ticketsNews
                news.readNews()
                print "handleNews " + str(news)
                self.flagMute = False
                return 1
            return 0


       
    def handleWhatDoYouDo(self, txt):
        print "handleWhatDoYouDo begin"
        if self.flagMute :
            return 0

        else :
            try:
                lastTicket = (self.tm.memory)[-1]
            except:
                return 0
            # if question is "what do you do ?"
            print "handleWhatDoYouDo : lastTicket action : " + lastTicket.action +" lastTicket isQuestion : " + str(lastTicket.isQuestion) 
            if lastTicket.action == "faire" and lastTicket.isQuestion == True :
                print "handleWhatDoYouDo human say answer"
                phrase = decomposePhrase(txt)
                if phrase != None:

                    self.flagMute = True
                    [sujet,pronom,verbe, complement, verite] = phrase

                    if verbe == "aime":
                        self.flagMute = False
                        return 0
                    #Create tickets and add to current Actors
                    idActor = actors.actorsManager.getCurrentActor()
                    if( idActor == None or idActor == -1 ):
                        print( "DBG: rodin: handleWhatDoYouDo: nothing to do: source: %s" % idActor )
                        self.flagMute = False
                        return 0
                    answerTicket = ticket.ticketsManager.createNewTicket(ticket.Ticket(source=idActor,objet=complement,action=verbe))
                    actors.actorsManager.addTicket(idActor,answerTicket)

                    #end Tickets
                    listActors = self.am.getActors( actorsId = idActor )
                    if( listActors == None or len(listActors) < 1 ):
                        print( "DBG: rodin: handleWhatDoYouDo: nothing to do: listActors: %s" % listActors )
                        self.flagMute = False
                        return 0

                    actor = listActors[0]
                    strOptionnalName = actor.firstName
                    
                    
                    tmpPronom = ""
                    tmpComplement = ""
                    tmpVerbe = verbe
                    negation = ""
                    if complement !=  None:
                        tmpComplement = complement
                    if len(tmpVerbe)>1:
                        if tmpVerbe[-1] == "e":
                            tmpVerbe = tmpVerbe +"r"
                        elif tmpVerbe[-2] == "i" and tmpVerbe[-2] == "s" :
                            tmpVerbe[-1] = "r" 
                        elif tmpVerbe == "suis":
                            tmpVerbe = "etre"
                    

                    voyelle = ['a','e','i','o','u','y']
                    isVoyelle = [1 for x in voyelle if x == tmpVerbe[0]]
                    if isVoyelle != [] and pronom != None :
                        if pronom == "t'":
                            tmpPronom = "m'"
                        elif pronom == "m'":
                            tmpPronom = "s'"
                    else:
                        if pronom == "te":
                            tmpPronom = "me "
                        elif pronom == "me":
                            tmpPronom = "se "
                    if verite == -1:
                        negation =" ne pas"
                    s = strOptionnalName + ", est en train de"+ negation+" " + tmpPronom +" "+ tmpVerbe +" " + tmpComplement 
                    print "handleWhatDoYouDo robot understand : " +s
                    speech.sayAndLight( s );
                    self.flagMute = False
                    return 1
        return 0



    def handleYesNo(self, txt) :
        if self.flagMute :
            return 0
        else:
            try:
                lastTicket = (self.tm.memory)[-1]
            except:
                return 0
            if( txt in ["oui", "non"] and lastTicket.isQuestion == True): # todo refactor: # avoir une m�thode qui donne un degr� de positivit�:
                # TODO: chercher la question precedente et associer cette r�ponse
                self.flagMute = True
                
                #Create tickets and add to current Actors
                idActor = actors.actorsManager.getCurrentActor()
                if( idActor == None or idActor == -1 ):
                    print( "DBG: rodin: handleYesNo: nothing to do: source: %s" % idActor )
                    self.flagMute = False
                    return
                answerTicket = ticket.ticketsManager.createNewTicket(ticket.Ticket(source=idActor,objet=txt,action="answer_question"))
                actors.actorsManager.addTicket(idActor,answerTicket)

                #end Tickets

                questionTicket = self.tm.getLastQuestion()
                import qi

                qi.info("WARNING","\n\n\n " + str(questionTicket) + "\n\n\n")
                
                if txt == "oui":
                    truth = 1
                else:
                    truth = -1

                self.smartSay(questionTicket, verite = truth)

                self.flagMute = False
                return 1
        return 0

    def handleVideo(self , strTxt, phoneticTresh = 0.8):
        if self.flagMute :
            return 0
        else :
            if stringtools.isPhoneticEqual(strTxt , "vidéo")>= phoneticTresh or stringtools.isPhoneticEqual(strTxt , "lance une vidéo")>= phoneticTresh or stringtools.isPhoneticEqual(strTxt , "vidéos")>= phoneticTresh : 
                naoqitools.myGetProxy( "ALMemory" ).raiseEvent( "Application", "Video")
                return 1
            else:
                return 0
        return 0

    def handleMusic(self, strTxt, phoneticTresh = 0.8):
        if self.flagMute :
            return 0
        else :
            retSentence = self.mm.findSentence( strTxt )
            if( retSentence != None):
                # launch a song
                song, sentence = retSentence
                self.flagMute = True
                music_manager.sendPlayWithPosition( song.getSongFile(), sentence )
                self.flagMute = False
                return 1
            if "joue " in strTxt :
                txt = strTxt.replace("joue ","")
                oneSong = self.mm.findMusicByArtist( txt )
                if oneSong == None:
                    oneSong = self.mm.findMusicBySongName(txt)

                if( oneSong != None ):
                    # launch a song
                    print( "une song par artist: %s" % str(list) )
                    self.flagMute = True
                    naoqitools.myGetProxy( "ALMemory" ).raiseEvent( "Application", "Music")
                    music_manager.playMP3( oneSong)
                    naoqitools.myGetProxy( "ALMemory" ).raiseEvent("tabletResponse","end song")
                    self.flagMute = False
                    html_manager.showHTMLWrite(" ","Center","Letter")
                    return 1
                else :
                    self.flagMute = True
                    speech.sayAndLight( "Je n'ai pas cette chanson dans mon répertoire." );
                    self.flagMute = False
        return 0

    def handleLike( self, aLikes ):
        """
        - aLikes: a pair ["txt", value [-1: burk .. 1: j'aime!]
        """
        strObj = aLikes[0]
        rValue = aLikes[1]
        tic = tickets.Ticket( source = actors.actorsManager.getCurrentActor(), action = "aimer", objet = strObj, verite=rValue )
        self.tm.createNewTicket( tic )
        
        
    def innerTest( self ):
        import test
        #~ tic = tickets.Ticket( source = actors.actorsManager.getCurrentActor(), action = "aimer", objet = strObj, verite=rValue )
    
    def smartSay(self, tic, verite = -2):
        if verite == -2:
            truth  = tic.verite
        else:
            truth = verite
        try:
            s0 = self.sg.generate( 2 ,tic.action, truth ) + " " + tic.objet + ". "
        except:
            return
        idActor = actors.actorsManager.getCurrentActor()
        answer = self.tm.getAnswerToQuestion(tic.action, tic.objet, tic.ticketNum)
        print "INF : rodin : smartSay : before if answer s0 = " + s0
        if answer != None  :
            print "INF : rodin : smartSay : after if"
            random.shuffle(answer)
            if int(answer[0].source) != int(idActor) :
                print "INF : rodin : smartSay : different actor :" + str(idActor)
                actorsId = answer[0].source
                listActors = self.am.getActors( actorsId = actorsId )
                if( listActors != None and len(listActors) > 0 ):
                    actor = listActors[0]
                    strOptionnalName = actor.firstName
                else:
                    strOptionnalName = "quelqu'un"
                s1 = self.sg.generate( 3 ,answer[0].action, answer[0].verite , strOptionnalName = strOptionnalName)
                strPhrase = translate.chooseFromDictRandom( { "fr": "C'est marrant /C'est drole /Amusant, /Cela me rappelle que /Tu savais que /Je me souviens que " })
                try :
                    s0 = s0 + strPhrase + s1 + " " + answer[0].objet
                except:
                    return
                if truth == answer[0].verite:
                    if truth == 1 :
                        s3 = " aussi."
                    else :
                        s3 = " non plus."
                else:
                    s3 = "."
                s0 = s0 + s3
            else:
                print "INF : rodin : smartSay : same actor"
                strPhrase = translate.chooseFromDictRandom( { "fr": "C'est marrant /C'est drole /Amusant, /Cela me rappelle que /Je me souviens que " })
                strWordTime = self.sg.getTimeWord(answer[0])
                s0 = s0 + strPhrase + "tu me l'avais dit " + strWordTime
        else :
            print "INF : rodin : smartSay : else of answer"
            strPhrase = translate.chooseFromDictRandom( { "fr": "Tu es la première personne à me le dire./Je ne savais pas./C'est amusant." })
            s0 = s0 + strPhrase
        print "INF : rodin : smartSay : final say :"+s0
        speech.sayAndLight( s0 );
    
# class Rodin - end

rodin = Rodin()

# change this function in another file
def decomposePhrase(phrase) : 
    tmp_txt = phrase.split(" ")
    sujet = None
    pronom = None
    verbe = None
    complement = None
    verite = 1
    if len(tmp_txt) > 1 :
        listPP1 = ["je",  "tu",  "nous", "vous" , "il", "elle", "ils", "elles" ]
        sujet = "".join([sujet for sujet in listPP1 if sujet == tmp_txt[0]])
        if sujet != "":
            tmp_txt = tmp_txt[1:]
            if "ne" == tmp_txt[0]:
                if len(tmp_txt) > 1:
                    tmp_txt = tmp_txt[1:]
                    verite = -1

            listPP2 = ["me", "moi" ,"te", "toi", "se", "en", "y","le", "la",  "les" , "lui", "soi" ,"leur", "eux","lui", "leur","nous","vous"]
            pronom = "".join([pronom for pronom in listPP2 if pronom == tmp_txt[0]])
            if pronom == "":

                if "t'" in tmp_txt[0]:
                    pronom = "t'"

                if "m'" in tmp_txt[0]:
                    pronom = "m'"

                if "l'" in tmp_txt[0]:
                    pronom = "l'"

                if pronom != "": 
                    tmp_txt[0] = tmp_txt[0].replace(pronom,'')
                    verbe = tmp_txt[0]
                else:
                    if "n'" in tmp_txt[0]:
                        tmp_txt[0] = tmp_txt[0].replace("n'",'')
                        verite = -1

                    verbe = tmp_txt[0] 
                    pronom = None
            else:
                tmp_txt = tmp_txt[1:]
                if len(tmp_txt) >= 1:
                    verbe= tmp_txt[0]
                else:
                    return None

        else :
            if "j'" in tmp_txt[0]:
                sujet = "j'" 
                verbe = tmp_txt[0].replace("j'",'')
            else:
                return None

    else:
        if "j'" in tmp_txt[0]:
            sujet = "j'"
            verbe= tmp_txt[0].replace("j'",'')
        else:
            return None

    if len(tmp_txt) > 1:
        complement= (" ").join(tmp_txt[1:])
        if "pas" in complement and verite == -1:
            complement = complement.replace("pas",'')
            if complement == '':
                complement = None
     
    return [sujet,pronom,verbe, complement , verite]

def createActorsFromFaceReco():
    fr = naoqitools.myGetProxy( "ALFaceDetection" )
    lFaces = fr.getLearnedFacesList()
    for l in sorted(lFaces):
        splitted = l.split( "_" )
        firstName = splitted[1]
        lastName = splitted[2]
        actors.actorsManager.createNew( firstName=firstName, lastName=lastName, gender = 0)

def autoTest():
    r = Rodin()
    r.innerTest()

if( __name__ == "__main__" ):
    autoTest()
    