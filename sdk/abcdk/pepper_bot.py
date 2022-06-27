# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Project Hopias
# pepper bot
# Innovation - Protolab - mcaniot@aldebaran.com
# Aldebaran Robotics (c) 2016 All Rights Reserved - This file is confidential.
###########################################################

print "import abcdk.pepper_bot"

try:
	import aiml
except:
	print "You need to do su pip install aiml"
 

import ector
import os

""" Check if you have installed beautiful soup"""
import wiki_scrapper

""" You need the file pepper_bot on your robot. You will find this file on
appu_shared/sdk/install_hopias. You make a scp -r pepper_bot nao@ip_robot:."""

FILENAME_TO_TMP = "/home/nao/pepper_bot/aiml/tmp_learn.aiml"
FILENAME_TO_DATA = "/home/nao/pepper_bot/aiml/data_learn.aiml"
PATH_TO_BRAIN = "/home/nao/pepper_bot/data/pepper.brn"
PATH_TO_AIML = "/home/nao/pepper_bot/aiml/*.aiml"
TAG_END= "</aiml>"
TAG_BEG= "<aiml>"

BOT_PREDICATES = {
	"name": "Pepper",
	"birthday": "6 juin 2016",
	"location": "Paris",
	"master": "Maxime",
	"gender": "female",
	"human" : "humain"
}

Q_LIST1 = ["Qui","Quand","Ou","Quand","Comment","Combien","Pourquoi","Quel","Quelle"]
Q_LIST2 = ["Que signifie ", "Que veux dire "]

# Class PepperBot : manage the bot for giving an answer to the human
class PepperBot:
	def __init__( self ):
		self.human_name = "humain"
		self.robot_name = "Pepper"
		self.k = aiml.Kernel()
		self.ector = ector.Ector(botname="Pepper",username="humain")
		self.lastSentenceRobot = None
		self.lastSentenceHuman = None

		'''# Load the AIML files on first load, and then save as "brain" for speedier startup
		if os.path.isfile(PATH_TO_BRAIN) is False:
			self.k.learn(PATH_TO_AIML)
			self.k.respond("load aiml b")
			self.k.saveBrain(PATH_TO_BRAIN)
		else:
		    self.k.loadBrain(PATH_TO_BRAIN)
		'''

		self.k.learn(PATH_TO_AIML)
		self.k.respond("load aiml b")
		self.k.saveBrain(PATH_TO_BRAIN)
		# Give the bot a name and lots of other properties
		for key,val in BOT_PREDICATES.items():
			self.k.setBotPredicate(key, val)
		self.transferTmpTpdata()

	def askAiml(self,human_question):
		robot_answer = self.k.respond(human_question)
		return self.handleWordForLearning(robot_answer)

	def askEctorBot(self, human_question):
		return self.ector.askEctor(human_question)

	def askPepperBot(self,human_question , human_name = "human", bUseEctor = False):
		self.k.setBotPredicate("human", human_name)
		robot_answer = self.askWiki(human_question)
		if isinstance(robot_answer,list) and len(robot_answer) > 2 and robot_answer[1] != []:
			import ihmtools
			result = ihmtools.choice(robot_answer[0],robot_answer[1],rTimeOut = 60, bRepeatChoosenAnswer = False ,bActivateChoiceProposal = False,astrJointsToExclude = [] );
			if result != None:
				import speech

				idx = result[0]
				link = robot_answer[2]
				robot_answer = self.askWiki("cherche " + link[idx])
				speech.sayAndLight("ok laisse moi y réfléchir.")
				return robot_answer
			else:
				return None
		if robot_answer == None:
			robot_answer = self.askAiml(human_question)
			if robot_answer == None and bUseEctor:
				robot_answer = self.askEctorBot(human_question)

		if robot_answer == None :
			robot_answer = "Je ne comprend pas ta question."

		self.lastSentenceHuman = human_question
		self.lastSentenceRobot = str(robot_answer)
		return self.lastSentenceRobot

	# search on wikipedia the answer
	def askWiki(self, wordSearch):
		text = wordSearch
		if "cherche " in text :
			text = text.replace("cherche ",'')
			historyScrapper = wiki_scrapper.HistoryScrapper()
			answer = None
			try :
				historyScrapper.getDescription(text.split(" "))
				answer = historyScrapper.resume
			except:
				print "WRG : pepper_boy : askWiki : No link for historic "
				return "Désolé cela ne me dit rien."
			if answer != "":
				return answer
			else:
				answer = historyScrapper.infoList
				return answer
		else:
			return None

	def handleWordForLearning(self,robot_answer):
		text = robot_answer
		if text == "NONE" :
			return None
		if "Ok, je saurai maintenant que " in text :
			text = text.replace("Ok, je saurai maintenant que ",'')
			if " est " in text :
				text = text.split(" est ")
				self.learnWhatisWhat(Q_LIST1," est "+text[0],text[1])
			elif "signifie" in text :
				text = text.split("signifie")
				self.learnWhatisWhat(Q_LIST2, text[0],text[1])
				self.learnWhatisWhat(Q_LIST2, text[1],text[0])
			elif "veux dire" in text :
				text = text.split("veux dire")
				self.learnWhatisWhat(Q_LIST2, text[0],text[1])
				self.learnWhatisWhat(Q_LIST2, text[1],text[0])
		return str(robot_answer)

	def initTmp(self):
		string_to_save = '<?xml version="1.0" encoding="UTF-8"?>\n\n<aiml>\n</aiml>'
		open(FILENAME_TO_TMP, 'w').close()
		with open(FILENAME_TO_TMP, 'r+') as tmp_file:
			tmp_file.write(string_to_save)

	def learnWhatisWhat(self,questionningList ,word1,word2):
		for tmp in questionningList:
			self.learn(tmp+word1,word2)

	def learn(self,question ,answer):
		string_to_save = "<category><pattern>%s</pattern><template>%s</template></category>\n\n"%(question.upper(),answer) +TAG_END 
		with open(FILENAME_TO_TMP, 'r+') as tmp_file:
			text = tmp_file.read()
			i = text.index(TAG_END)
			tmp_file.seek(0)
			tmp_file.write(text[:i] + string_to_save + text[i + len(TAG_END):])
		self.k.learn(FILENAME_TO_TMP)

	def transferTmpTpdata(self):
		
		with open(FILENAME_TO_TMP, 'r+') as tmp_file:
			tmp_text = tmp_file.read()
			i = tmp_text.index(TAG_BEG)
			tmp_file.seek(0)
			string_to_save = tmp_text[len(TAG_BEG)+ i:]
			with open(FILENAME_TO_DATA, 'r+') as save_file:
				save_text =  save_file.read()
				j = save_text.index(TAG_END)
				save_file.seek(0)
				save_file.write(save_text[:j] + string_to_save + save_text[j + len(TAG_END):])
		self.initTmp()
		self.k.learn(FILENAME_TO_DATA)

# end - Class PepperBot


