# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Project Hopias
# Music Manager
# Innovation - Protolab - mcaniot@aldebaran.com
# Aldebaran Robotics (c) 2016 All Rights Reserved - This file is confidential.
###########################################################

""" Music Manager """

print( "importing abcdk.music_manager");


"""
    We need to have a abcdk_songs, so you should do this:

        1) Connect in ssh to the robot.

        2) Copy and paste this line :
            su -c "ln -s /home/nao/songs /var/www/abcdk_songs"

        3) open nginx.conf whith this line :
            su -c "nano /etc/nginx/nginx.conf"

        4) Insert the text behind just before location /libs :
            location /abcdk_songs {
                root /var/www;
            }

        5) restart with this line:
            su -c "/etc/init.d/nginx restart"
"""

# Import
import actors
import copy
import csv
import filetools
import html_manager
import naoqitools
import os
import qi
import random
import stringtools
import ticket
import time


# Class Song : contains metadata of the song
class Song:

    # Constructor
    def __init__(self, songlist = []): 
        """
        all variables are strings but bpm and year are int, keyword and sentence are special

        style depend of the dance name : Rock, Disco, Singer, Musician, Party

        keyword is a string like that "keyword1/keyword2/.../keywordn"

        sentence is a string like that "sentence1/sec_start1/sec_end1//sentence2/sec_start2/sec_end2//...//sentencen/sec_startn/sec_endn" for more explanation see the function sendPlayWithPosition(nameFile, sentence)

        """
        if (songlist == []):
            self.artist =""
            self.songName = ""
            self.songFile = ""
            self.bpm = ""
            self.style = ""
            self.danceStyle =""
            self.year = ""
            self.keyword = ""
            self.sentence = ""
            self.nbTimePlayed = '0'
        else :
            self.artist = songlist[0]
            self.songName = songlist[1] 
            self.songFile = songlist[2]
            self.bpm = songlist[3]
            self.style = songlist[4]
            self.danceStyle = songlist[5] 
            self.year = songlist[6]
            self.keyword = songlist[7] 
            self.sentence = songlist[8] 
            self.nbTimePlayed = '0'
    # end Constructor
    
    # Functions
    def setSong(self, artist,songName,songFile,bpm,style, danceStyle,year,keyword,sentence,nbTimePlayed):
        self.artist = artist
        self.songName = songName
        self.songFile = songFile
        self.bpm = bpm
        self.style = style
        self.danceStyle = danceStyle
        self.year = year
        self.keyword = keyword
        self.sentence = sentence
        self.nbTimePlayed = nbTimePlayed

    def copySong(self,song):
        if song == None:
            self == None
        else :
            self.artist = song.artist
            self.songName = song.songName
            self.songFile = song.songFile
            self.bpm = song.bpm
            self.style = song.style
            self.danceStyle = song.danceStyle
            self.year = song.year
            self.keyword = song.keyword
            self.sentence = song.sentence
            self.nbTimePlayed = song.nbTimePlayed
    # end Functions

    # Get variable
    def getArtist(self):
        return self.artist

    def getSongName(self):
        return self.songName

    def getSongFile(self):
        return self.songFile

    def getBpm(self):
        return self.bpm

    def getStyle(self):
        return self.style

    def getDanceStyle(self):
        return self.danceStyle

    def getYear(self):
        return self.year

    def getKeyword(self):
        return self.keyword

    def getSentence(self):
        return self.sentence

    def getNbTimePlayed(self):
        return self.nbTimePlayed

    # Get variable with it type
    def getType(self,Type):
        if Type == "artist":
            return self.getArtist()
        if Type == "songName":
            return self.getSongName()
        if Type == "songFile":
            return self.getSongFile()
        if Type == "bpm":
            return self.getBpm()
        if Type == "style":
            return self.getStyle()
        if Type == "danceStyle":
            return self.getDanceStyle()
        if Type == "year":
            return self.getYear()
        if Type == "keyword":
            return self.getKeyword()
        if Type == "sentence":
            return self.getSentence()
        if Type == "nbTimePlayed":
            return self.getNbTimePlayed()
    # end Get variable

    # __str__
    def __str__(self):
        return "artist : "+self.artist+"\nsong name : "+self.songName+"\nsong file : "+self.songFile+"\nbpm : "+str(self.bpm)+"\nstyle : "+self.style+"\nDance style : "+self.danceStyle+"\nyear : "+self.year+"\nkeyword : "+self.keyword+"\nsentence : "+self.sentence+"\nnumber of time played : "+ str(self.nbTimePlayed)
    # end __str__

# end - Class Song

# Class SongManager : class for searching song in a .csv file
class SongManager:

    # Constructor
    def __init__(self, pathCSV ='/var/www/abcdk_songs/metaData/metaData.csv'):
        '''
        pathCSV : contains the path to the file metaData.csv.

        songList : it is a list of Song class. It is the library of song where we will search song information.

        nblisten : it is a variable for comparing the number of listening of each song. With that, we can play the song
        with the smaller number of listening. It is initialize with a big number.

        '''

        self.pathCSV = pathCSV
        self.songList = []
        self.nblisten = 10000000.0
        self.songList = self.importFromCSV()
    # end Constructor

    # Functions
    def importFromCSV(self):
        """
        we import all the lines of the .csv file, create song with the metaData in the line and put it
        in the songList.
        """ 
        s = Song()
        songList = []
        f = csv.reader(open(self.pathCSV,"rb"))
        i = 0
        for row in f:
            if i == 0 :
                i = 1
            else :
                songList.append(Song(row))
        return songList 

    def randomSong(self):
        return random.shuffle(self.songList)

    def findAllWord(self,word,Type, phoneticTresh = 0.8):
        """
        we find all song with word in the songList with the Type (example : artist, songName ...)
        """
        print "start findAllWord by %s " %(Type)
        tmpList = []
        indice = -1
        for i in range(0,len(self.songList)):
            # if it is the type keyword you need to remove the "/" and compare all of keywords
            if (Type == "keyword"):
                tmp = self.songList[i].getType(Type).split("/")
                for j in range(len(tmp)):
                    if (stringtools.isPhoneticEqual(tmp[j],word) >= phoneticTresh) :
                        indice = i
                        print "The word %s was found in songList[%d]" % (word,indice)
                        tmpList.append(self.songList[i])
            # search the word in the list by type
            if (stringtools.isPhoneticEqual(self.songList[i].getType(Type), word) >= phoneticTresh) :
                indice = i
                print "The word %s was found in songList[%d]" % (word,indice)
                tmpList.append(self.songList[i])
        # if indice don't change so the file doesn't exist
        if indice == -1:
            print "File doesn't exist"
            return None
        random.shuffle(tmpList)
        return tmpList

    def findWord (self,word,Type, phoneticTresh = 0.8):
        """
        we find one song with a word in the songList with the Type (example : artist, songName ...)
        """
        print "start findWord by %s" %(Type)
        self.nblisten = 10000000.0
        indice = -1
        for i in range(0,len(self.songList)):
            # if it is the type keyword you need to remove the "/" and compare all of keywords
            if (Type == "keyword") and self.nblisten >= float(self.songList[i].nbTimePlayed):
                tmp = self.songList[i].getType(Type).split("/")
                for j in range(len(tmp)):
                    if (stringtools.isPhoneticEqual(tmp[j],word) >= phoneticTresh):
                        indice = i
                        print "The word %s was found in songList[%d]" % (word,indice)
                        self.nblisten = float(self.songList[i].nbTimePlayed)
            # search the word in the list by type
            if (stringtools.isPhoneticEqual(self.songList[i].getType(Type), word) >= phoneticTresh) and self.nblisten >= float(self.songList[i].nbTimePlayed):
                indice = i
                print "The word %s was found in songList[%d]" % (word,indice)
                self.nblisten = float(self.songList[i].nbTimePlayed)
        # if indice don't change so the file doesn't exist
        if indice == -1:
            print "File doesn't exist"
            return None
        self.songList[indice].nbTimePlayed =float (self.songList[indice].nbTimePlayed) + 1
        return self.songList[indice]

    def findSentence(self,word , phoneticTresh = 0.8):
        """
        we find the sentence with word
        """
        print "start findSentence"
        self.nblisten = 10000000.0
        indice = -1
        list_sentence = []
        for i in range(0,len(self.songList)):
            if (self.nblisten >= float(self.songList[i].nbTimePlayed)):
                    tmp = ((self.songList[i]).getSentence()).split("//")
                    for j in range(0,len(tmp)):
                        tmp_sentence = tmp[j].split("/")
                        if tmp_sentence[0] != "":
                            if (stringtools.isPhoneticEqual(tmp_sentence[0], word)>= phoneticTresh):
                                indice = i
                                print "The word %s was found in songList[%d]" % (word,indice)
                                self.nblisten = float(self.songList[i].nbTimePlayed)
                                list_sentence = tmp_sentence
        # if indice don't change so the file doesn't exist
        if indice == -1:
            print "File doesn't exist"
            return None
        self.songList[indice].nbTimePlayed =float (self.songList[indice].nbTimePlayed) + 1

        return [self.songList[indice], list_sentence]

    # different search by type 
    def findMusicByArtist(self,artist, phoneticTresh = 0.8):
        return self.findWord(artist,"artist", phoneticTresh)

    def findMusicBySongName(self,songName, phoneticTresh = 0.8):
        return self.findWord(songName,"songName", phoneticTresh)

    def findMusicByStyle(self,style, phoneticTresh = 0.8):
        return self.findWord(style,"style", phoneticTresh)

    def findMusicByYear(self,year, phoneticTresh = 0.8):
        return self.findWord(year,"year", phoneticTresh)

    def findMusicByKeyword(self,keyword, phoneticTresh = 0.8):
        return self.findWord(keyword,"keyword", phoneticTresh)

    def findMusicBySentence(self,sentence, phoneticTresh = 0.8):
        return self.findSentence(sentence, phoneticTresh)
    # end Functions

# end - class SongManager 

songManager = SongManager()


# Song Controler

"""
This Functions are for controling the audio.

"""

fileId = None
ip = naoqitools.myGetProxy( "ALTabletService").robotIp()
port = 9559
session = qi.Session()
session.connect("tcp://" + ip + ":" + str(port))
player = session.service("ALAudioPlayer")

def playMP3(song, bUseDisplay = True):
    global player
    global fileId
    if not (song != None and isinstance( song, Song )):
        print "Error no file exist"
    else:
        #Create tickets and add to current Actors
        idActor = actors.actorsManager.getCurrentActor()
        if( idActor == None or idActor == -1 ):
            print( "DBG: music_manager: playMP3: nothing to do: source: %s" % idActor )
        else :
            musicTicket = ticket.ticketsManager.createNewTicket(ticket.Ticket(source=idActor,objet=song.getSongName(),action="music_manager"))
            actors.actorsManager.addTicket(idActor,musicTicket)
        #end Tickets

        player.stopAll()
        fileId = player.loadFile("/var/www/abcdk_songs/" + song.getSongFile())
        if bUseDisplay:
            html_manager.showHTMLMusic(song.getArtist()+"-"+ song.getSongName())
        player.play(fileId, _async=True)
        commandLoop()
        print "end of the song"
        naoqitools.myGetProxy( "ALMemory" ).raiseEvent("tabletResponse","end song")

def commandLoop():
    global player
    global fileId
    mem = naoqitools.myGetProxy( "ALMemory" );
    mem.insertData( "tabletResponse", "" );
    print "begin command loop in music_manager.py"
    while mem.getData("tabletResponse")!= "Pepper stop":
        response = mem.getData("tabletResponse")
        if response != "":
            mem.insertData("tabletResponse","") 
            print "command sent : " + response
            choiceCommand(response)
        if fileId != None:
            if player.getFileLength(fileId) <= player.getCurrentPosition(fileId) :
                mem.insertData("tabletResponse","Pepper stop")
    sendStop()    

def sendCommandMP3(command, phoneticTresh = 0.8):
    textProx = naoqitools.myGetProxy( "ALTextToSpeech" );
    lang = textProx.getLanguage()
    wordList = []
    if lang == "French":
        wordList = ["pause","lecture","suivant","précédent","plus","moins","menu","stop"]
    elif lang == "English":
        wordList = ["pause","play","next","previous","plus","minus","menu","stop"]

    cmd = None
    if stringtools.isPhoneticEqual(command , "Pepper " + wordList[0])>= phoneticTresh :
        cmd = "Pepper pause"
    elif stringtools.isPhoneticEqual(command , "Pepper "+ wordList[1])>= phoneticTresh:
        cmd = "Pepper lecture"
    elif stringtools.isPhoneticEqual(command , "Pepper "+ wordList[2])>= phoneticTresh:
        cmd = "Pepper suivant" 
    elif stringtools.isPhoneticEqual(command , "Pepper "+ wordList[3])>= phoneticTresh:
        cmd = "Pepper précédent"
    elif stringtools.isPhoneticEqual(command , "Pepper "+ wordList[4])>= phoneticTresh:
        cmd = "Pepper plus"
    elif stringtools.isPhoneticEqual(command , "Pepper "+ wordList[5])>= phoneticTresh:
        cmd = "Pepper moins"
    elif stringtools.isPhoneticEqual(command , "Pepper "+ wordList[6])>= phoneticTresh:
        cmd = "Pepper menu"
    elif stringtools.isPhoneticEqual(command , "Pepper "+ wordList[7])>= phoneticTresh:
        cmd = "Pepper stop"

    if cmd != None:
        html_manager.sendToHTML(cmd)
    

def choiceCommand(command):
    global fileId
    if fileId != None:
        if command == "Pepper pause":
            sendPause()
        elif command == "Pepper lecture":
            sendPlay()
        elif command == "Pepper suivant":
            sendNext() 
        elif command == "Pepper précédent":
            sendBack()
        elif command == "Pepper plus":
            sendVolume(1)
        elif command == "Pepper moins":
            sendVolume(-1)

def sendPause():
    global player
    global fileId
    player.pause(fileId)

def sendPlay():
    global player
    global fileId
    player.play(fileId,_async=True)


def sendPlayWithPosition(nameFile, sentence):
    """
    With the sentence, you have the beginning and the end of the part of the song you want to play.
    Remember, sentence is a string like that "sentence1/sec_start1/sec_end1//sentence2/sec_start2/sec_end2//...//sentencen/sec_startn/sec_endn".
    We will play at the sec_start and stop at the sec_end.
    """
    
    global player
    global fileId

    player.stopAll()
    position1 = float(sentence[-2])
    position2 = float(sentence[-1])

    fileId = player.loadFile("/var/www/abcdk_songs/"+nameFile)
    player.play(fileId, _async=True)
    time.sleep(0.1)
    player.goTo(fileId,position1)
    time.sleep(position2 - position1)
    player.stopAll()

def sendStop():
    global player
    global fileId
    if fileId != None:
        sendPause()
        player.unloadFile(fileId)
        fileId = None
    player.stopAll()
    initVolume()
    

def sendNext():
    global player
    global fileId
    tmp = player.getCurrentPosition(fileId) + 10
    if tmp < player.getFileLength(fileId):
        player.goTo(fileId,tmp)

def sendBack():
    global player
    global fileId
    tmp = player.getCurrentPosition(fileId) - 10
    if tmp > 0:
        player.goTo(fileId, tmp)

def sendVolume(nb):
    son = naoqitools.myGetProxy("ALAudioDevice")
    son.setOutputVolume(son.getOutputVolume() + nb*10)

def initVolume():
    son = naoqitools.myGetProxy("ALAudioDevice")
    son.setOutputVolume(50)

# end - Song controller
