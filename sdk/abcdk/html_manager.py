# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Project Hopias
# HTML manager
# Innovation - Protolab - mcaniot@aldebaran.com
# Aldebaran Robotics (c) 2016 All Rights Reserved - This file is confidential.
###########################################################

""" html manager """
print( "importing abcdk.html_manager");

"""
    For the tablet, we need to have a abcdk_html directory with some web access, so you should do this:

    	1) Connect in ssh to the robot.

    	2) Copy and paste this line :
        	su -c "ln -s /home/nao/.local/lib/python2.7/site-packages/abcdk/data/html/ /var/www/abcdk_html"

        3) open nginx.conf whith this line :
        	su -c "nano /etc/nginx/nginx.conf"

        4) Insert the text behind just before location /libs :
        	location /abcdk_html {
            	root /var/www;
        	}

        5) restart with this line:
        	su -c "/etc/init.d/nginx restart"

    You also need a abcdk_videos directory so :
    
    	1) Connect in ssh to the robot.

    	2) Copy and paste this line :
        	su -c "ln -s /home/nao/videos/ /var/www/abcdk_videos"

        3) open nginx.conf whith this line :
        	su -c "nano /etc/nginx/nginx.conf"

        4) Insert the text behind just before location /libs :
        	location /abcdk_videos {
            	root /var/www;
        	}

        5) restart with this line:
        	su -c "/etc/init.d/nginx restart"

    You also need a data2 directory so :
    
    	1) Connect in ssh to the robot.

    	2) Copy and paste this line :
        	su -c "ln -s /home/nao/data2 /var/www/data2"

        3) open nginx.conf whith this line :
        	su -c "nano /etc/nginx/nginx.conf"

        4) Insert the text behind just before location /libs :
        	location /data2 {
            	root /var/www;
        	}

        5) restart with this line:
        	su -c "/etc/init.d/nginx restart"

"""

import actors
import bodytalk
import filetools
import ihmtools
import naoqitools
import os
import threading
import time


# Global variables

## Useful variables
frameManager = naoqitools.myGetProxy("ALFrameManager")
eventName = None
HTMLName = None

## Path
HTML_PATH =  "http://198.18.0.1/abcdk_html/"
VIDEO_PATH = "http://198.18.0.1/abcdk_videos/"
FACES_PATH_WEB = "http://198.18.0.1/data2/faces/"
FACES_PATH_ABSOLUTE = "/var/www/data2/faces/"

## naoqitools
try:
	tabletService = naoqitools.myGetProxy( "ALTabletService" )
except :
	print "WRG : html_manager.py : tabletService doesn't exist, so do nothing with the tablet"
	tabletService = None

try:
    memory = naoqitools.myGetProxy( "ALMemory" )
    memory.insertData( "isLoaded", "" ); 
except BaseException, err:
    print( "WRG: html_manager: err: %s" % err )

# end - global variables

# Tablet functions

def cleanTablet():
	global tabletService
	# we need to do this for cleaning the memory, activities ... of the tablet for watching video
	tabletService.resetTablet()
# end - Tablet functions

# Show HTML functions

def showHTML(appName):
	"""
	appName : string ; "Init", "Image", "Video", "Write", "Question", "Menu" or "Music"
	see the function "whatApp(appName)"
	"""
	global tabletService
	if tabletService != None:
		
		whatApp(appName)

		global memory
		memory.insertData( "isLoaded", "" )

		global HTMLName
		# HTML_PATH is the path between the tablet and the robot.
		tabletService.showWebview(HTML_PATH+HTMLName)

def showHTMLVideo(nameVideo = None):
	"""
	nameVideo : string ; example "video.mp4"
	"""
	global tabletService
	if tabletService != None:
		global eventName
		global HTMLName
		eventName = "HTMLVideo"
		HTMLName = "video.html"
		cleanTablet()
		# we need 0.5 sec before showing the HTML page
		time.sleep(0.5)
		global memory
		memory.insertData( "isLoaded", "" )
		tabletService.showWebview(HTML_PATH+HTMLName)
		if nameVideo != None:
			sendVideo(nameVideo)

def showHTMLMusic(artist = None):
	"""
	artist : string 
	"""
	global tabletService
	if tabletService != None:
		global eventName
		global HTMLName
		eventName = "HTMLMusic"
		HTMLName = "music.html"
		global memory
		memory.insertData( "isLoaded", "" )
		tabletService.showWebview(HTML_PATH+HTMLName)
		if artist != None:
			sendArtist(artist)

def showHTMLMenu():
	global tabletService
	if tabletService != None:
		global eventName
		global HTMLName
		eventName = "HTMLMenu"
		HTMLName = "menu.html"
		global memory
		memory.insertData( "isLoaded", "" )
		tabletService.showWebview(HTML_PATH+HTMLName)

def showHTMLInit():
	global tabletService
	if tabletService != None:
		global eventName
		global HTMLName
		eventName = "HTMLInit"
		HTMLName = "init.html"
		global memory
		memory.insertData( "isLoaded", "" )
		tabletService.showWebview(HTML_PATH+HTMLName)
		# fake time for loading page
		time.sleep(5)

def showHTMLImage(nameImage = None):
	"""
	nameImage : string; example "img.png"
	"""
	global tabletService
	if tabletService != None:
		global eventName
		global HTMLName
		eventName = "HTMLImage"
		HTMLName = "image.html"
		global memory
		memory.insertData( "isLoaded", "" )
		tabletService.showWebview(HTML_PATH+HTMLName)
		if nameImage != None:
			sendImage(nameImage)

def showHTMLQuestion(question = None, response = None):
	"""
	question : string
	response : string; example "rep1;rep2;rep3;...;repn" 
	"""
	global tabletService
	if tabletService != None:
		global eventName
		global HTMLName
		eventName = "HTMLQuestion"
		HTMLName = "question.html"
		global memory
		memory.insertData( "isLoaded", "" )
		tabletService.showWebview(HTML_PATH+HTMLName)
		if question != None and response != None:
			sendQuestion(question,response)

def showHTMLPlayMessage(name_author = "xxx", name_target ="xxx", img_file = "image_message.png"):
	global tabletService
	if tabletService != None:
		global eventName
		global HTMLName
		eventName = "HTMLPlayMessage"
		HTMLName = "play_message.html"
		global memory
		memory.insertData( "isLoaded", "" )
		tabletService.showWebview(HTML_PATH+HTMLName)
		sendPlayMessage(name_author,name_target, img_file)

def showHTMLRecord(name_author = "xxx", name_target ="xxx"):
	global tabletService
	if tabletService != None:
		global eventName
		global HTMLName
		eventName = "HTMLRecord"
		HTMLName = "record.html"
		global memory
		memory.insertData( "isLoaded", "" )
		tabletService.showWebview(HTML_PATH+HTMLName)
		sendRecord(name_author,name_target)

def showHTMLWrite(text = None, position = None, mode = None, speechMode = False, bHumanFace = True, bEraseWrite = True):
	"""
	text : string
	position: string ; "Center" or "Left" ; put the text on the screen in the middle or in the left.
	mode : string ; "Letter" or "Block" ; print letter by letter or in one block.
	speechMode : bool ; True or False ; True is with the body talk and False is without.
	"""

	global tabletService
	if tabletService != None:
		
		global eventName
		global HTMLName
		if eventName != "HTMLWrite":
			eventName = "HTMLWrite"
			HTMLName = "write.html"
			global memory
			memory.insertData( "isLoaded", "" )
			tabletService.showWebview(HTML_PATH+HTMLName)
		if text != None and position != None and mode != None:
			if bEraseWrite:
				sendEraseWrite()
			sendWrite(text,position,mode, speechMode)
			if bHumanFace :
				showHumanFace()

# end - Show HTML functions


# Different function for sending to the HTML page

def sendToHTML(command):
	global eventName
	global memory
	cpt = 0 
	# we must verify if the page is loaded or not
	if memory.getData("isLoaded") == "" :
		while memory.getData("isLoaded") == "" :
			if cpt <= 10:
				cpt = cpt + 0.1
				print "INF : html_manager : sendToHTML : wait " + eventName +". Time : "+ str(cpt) + " sec."
				time.sleep(0.1)
			else :
				print "ERR : html_manager : sendToHTML : stop waiting "+ eventName +". Error in sendToHTML loop."
				return
		# you need 0.2 sec before sending the command to the HTML page
		time.sleep(0.2)
	print "INF : html_manager : sendToHTML : raise event in "	+ eventName 
	memory.raiseEvent(eventName,command)

def sendArtist(artist):
	sendToHTML("artist;" + artist)

def sendVideo(nameVideo):
	sendToHTML("video;"+VIDEO_PATH+nameVideo)

def sendWrite(text,position,mode, speechMode = False):
	sendToHTML([text,position,mode])
	if speechMode == True:
		speech(text)

def sendEraseWrite():
	sendToHTML(["erase_all","",""])

def sendQuestion(question,response):
	if( isinstance( response, list ) ):
		response = ";".join(response)

	sendToHTML([question,response])

def sendHumanAnswerToQuestion(answer):
	sendToHTML(["human_answer",answer])

def sendImage(nameImage):
	sendToHTML(nameImage)

def sendShowImage(strPathAndFilename):
	strRemoteFile = findPathImage(strPathAndFilename)
	sendImage(strRemoteFile)

def sendHumanSay(txt):
	global memory
	memory.raiseEvent("HTMLHumanSay", txt)

def sendHumanFace(strPathAndFilename):
	global memory
	memory.raiseEvent("HTMLHumanFace", strPathAndFilename)

def sendEraseHumanSay():
	global memory
	memory.raiseEvent("HTMLHumanSay", "erase_all")

def sendEraseHumanFace():
	global memory
	memory.raiseEvent("HTMLHumanFace", "erase_all")

def sendPlayMessage(name_author,name_target, img_file):
	sendToHTML([name_author,name_target])
	sendHumanFace(FACES_PATH_WEB + img_file)

def sendRecord(name_author,name_target):
	sendToHTML([name_author,name_target])

# end - Different function for sending to the HTML page


# Others functions

def showHumanFace(idH = -1):
	import rodin
	tmp_rodin = rodin.rodin
	if idH == -1:
		idHuman = tmp_rodin.am.currentActor
	else:
		idHuman = idH
	print "INF : html_manager : showHumanFace : new id " + str(idHuman)
	if( idHuman == None or idHuman == -1 ):
		print( "DBG: html_manager: showHumanFace: no actor: source: %s" % idHuman )
		sendHumanFace(FACES_PATH_WEB+"unknown.jpg")
		return
	listActors = tmp_rodin.am.getActors( actorsId = idHuman )
	print( "INF: html_manager: showHumanFace: listActors //" + str(listActors) +"// & //" + str(tmp_rodin.am.actorList) + "//")
	if( listActors != None and len(listActors) > 0 ):
		print( "INF: html_manager: showHumanFace: listActors ok !")
		actor = listActors[0]
		# if the path in actor exists
		pathInActorExists = os.path.exists(FACES_PATH_ABSOLUTE+actor.pictureFileName)
		if pathInActorExists:
			sendHumanFace(FACES_PATH_WEB+actor.pictureFileName)
		else:
			# if the path in the robot exists
			nameFilePhoto = actor.firstName.lower()+ "__" + actor.lastName.lower()+".jpg"
			pathInRobotExists = os.path.exists(FACES_PATH_ABSOLUTE+nameFilePhoto)
			print "INF : html_manager : showHumanFace : path : "+ FACES_PATH_ABSOLUTE+nameFilePhoto + " and exists :" + str(pathInRobotExists) + " id :" + str(idHuman) + " idHuman "+ str(actor.idNumber)
			tmp_rodin.am.printActors()
			if pathInRobotExists:
				sendHumanFace(FACES_PATH_WEB+nameFilePhoto)
			else:
				sendHumanFace(FACES_PATH_WEB+"nophoto.jpg")

def findPathImage(strPathAndFilename):
	tabletService = naoqitools.myGetProxy( "ALTabletService" );
	strWebRemotePath = "http://%s/tmp/" % tabletService.robotIp();
	dummy, strExt = os.path.splitext(strPathAndFilename)
	
	strHttp = "http://";
	bUrl = False;
	if( strPathAndFilename[:len(strHttp)] != strHttp ):
		# local filename
		strLocalWebTmp = "/tmp/www/";
		bCopiedToTmp = False;
		strFilename = os.path.basename( strPathAndFilename );
		if( strPathAndFilename[:len(strLocalWebTmp)] != strLocalWebTmp ):
			bRet = filetools.copyFile( strPathAndFilename, "/var/www/tmp/" + strFilename );
			if( not bRet ):
				return False;
			strRemoteFile = strWebRemotePath + strFilename;
			bCopiedToTmp = True;
		else:
			strRemoteFile = strWebRemotePath + strPathAndFilename.replace( strLocalWebTmp, "" );
	else:
		# url
		strRemoteFile = strPathAndFilename;
		bUrl = True;
	return strRemoteFile

def whatApp(appName):
	"""
	It initializes the global variable eventName and HTMLName.
	It is the name of the event and the name of the HTML file.
	The HTML page will communicate thank to the event "eventName".
	"""
	global eventName
	global HTMLName

	if (appName== 'Init'):
		eventName = "HTMLInit"
		HTMLName = "init.html"

	if (appName== 'Menu'):
		eventName = "HTMLMenu"
		HTMLName = "menu.html"

	if (appName== 'Image'):
		eventName = "HTMLImage"
		HTMLName = "image.html"

	if (appName== 'Video'):
		eventName = "HTMLVideo"
		HTMLName = "video.html"

	if (appName== 'Question'):
		eventName = "HTMLQuestion"
		HTMLName = "question.html"

	if (appName== 'Write'):
		eventName = "HTMLWrite"
		HTMLName = "write.html"

	if (appName== 'Music'):
		eventName = "HTMLMusic"
		HTMLName = "music.html"

def speechReco(answer):
	result = ihmtools.choice( [], answer, rTimeOut = 180, bRepeatChoosenAnswer = False);
	if( result != None ):
		naoqitools.myGetProxy( "ALMemory" ).raiseEvent("tabletResponse",result[1])

def speech(text):
	bodytalk.bodyTalk.run( text, bWaitEndOfRestMovement = False, astrJointsToExclude = [] ,bUseHead = False, bTrackFace = True);

#end - Others functions