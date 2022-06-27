# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Project Hopias
# wiki scrapper
# Innovation - Protolab - mbusy@aldebaran.com - mcaniot@aldebaran.com
# Aldebaran Robotics (c) 2016 All Rights Reserved - This file is confidential.
###########################################################


import urllib2
import cookielib
import urllib
try:
	from bs4 import BeautifulSoup
except:
	print "You need to install with pip beautifulsoup4"

TEXT_HOMONYMIE_PERS = 'Cette <a href="/wiki/Aide:Homonymie" title="Aide:Homonymie">page d’homonymie</a> répertorie différentes personnes portant le même nom.'
TEXT_HOMONYMIE_OBJ = 'Cette page d’<a href="/wiki/Aide:Homonymie" title="Aide:Homonymie">homonymie</a> répertorie les différents sujets et articles partageant un même nom.'

# Class HistoryScrapper : find on wikipedia the resume of the research
class HistoryScrapper:
	"""
	Class to retreive the  data from the internet
	"""

	def __init__(self):
		"""
		Constructor
		"""

		self.wordSearch   = ""
		self.resume = ""
		self.infoList = []
		self.cookieJar   = cookielib.CookieJar()
		self.opener      = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookieJar))


	def cleanCrochet(self, text):
		cleanText = ""
		remain = False
		for tmp in text :
			if tmp == "[":
				remain = True
			else:
				if tmp == "]":
					remain = False
				elif remain == False:
					cleanText += tmp
		return cleanText

	def cleanText(self, rawResume):
		soup = BeautifulSoup(rawResume)

		for script in soup(["script", "style"]):												# kill all script and style elements
			script.extract()    																# rip it out
		
		text = soup.get_text()													# get text
		lines = (line.strip() for line in text.splitlines())						# break into lines and remove leading and trailing space on each
		chunks = (phrase.strip() for line in lines for phrase in line.split("  "))	# break multi-headlines into a line each
		text = '\n'.join(chunk for chunk in chunks if chunk) 					# drop blank lines
		text = text.encode('utf-8', 'ignore')
		text = self.cleanCrochet(text) 
		return text

	def decode(self,  text ):
		if "%" in text:
			return urllib.unquote(text)
		try:
			new_text = text.decode('utf-8')
		except:
			new_text = urllib.unquote(text)
		return BeautifulSoup(new_text).get_text()

	def getDescription(self, wordSearch):
		"""
		Get the  description for the given  name
		Parameters :
			wordSearch - The given  name
		""" 

		self.wordSearch  = wordSearch
		wordSearchURL    = ""
		prewordSearchURL = ""
		rawResume  = ""

		if len(self.wordSearch) == 1:														#  name treatement
			wordSearchURL = wordSearch.pop()
			wordSearchURL = wordSearchURL[0].upper() +  wordSearchURL[1:]
		
		else:
			wordSearchURL = wordSearch.pop()

			for element in wordSearch:
				prewordSearchURL += element[0].upper() +  element[1:] + "_"
			wordSearchURL2 = prewordSearchURL + wordSearchURL
			wordSearchURL = prewordSearchURL + wordSearchURL[0].upper() +  wordSearchURL[1:]
			
		url             = "https://fr.wikipedia.org/wiki/" + wordSearchURL
		print url
		try :
			httpRequest     = urllib2.Request(url)
			page            = self.opener.open(httpRequest)
		except:
			wordSearchURL = wordSearchURL2
			url = "https://fr.wikipedia.org/wiki/" + wordSearchURL
			print url
			httpRequest     = urllib2.Request(url)
			page            = self.opener.open(httpRequest)
		
		rawdata         = page.read()
		
		lines_of_data   = rawdata.split('\n')													# Treatement on rawdata
		
		special_lines = list()																	# Keep the resume
		startIntro    = False
		endIntro      = False
		isHomonymie_obj = None
		isHomonymie_pers = None
		isHomonymie_obj   = [line for line in lines_of_data if line.find(TEXT_HOMONYMIE_OBJ)>-1]
		isHomonymie_pers   = [line for line in lines_of_data if line.find(TEXT_HOMONYMIE_PERS)>-1]
		#print str (isHomonymie_pers) + str (isHomonymie_obj)
		if isHomonymie_pers == [] and isHomonymie_obj == []:
			print (wordSearchURL in line or wordSearchURL.split("_")[0].lower() in line or wordSearchURL.split("_")[0] in line or wordSearchURL.split("_")[0].upper() in line)
			for line in lines_of_data:
				if '<p>' in line and (wordSearchURL in line or wordSearchURL.split("_")[0].lower() in line or wordSearchURL.split("_")[0] in line or wordSearchURL.split("_")[0].upper() in line) and "modifier l'article" not in line and "Une réorganisation et une clarification du contenu est nécessaire" not in line and "page de discussion" not in line :
					startIntro = True

				if startIntro:
					special_lines.append(line)
					if line.find('</p>'):
						endIntro = True

				if endIntro:
					startIntro = False
					endIntro   = False
					break

			print str(special_lines) + "\n"
			for line in special_lines:																# Get the resume
				rawResume += line

			self.resume = self.decode(rawResume)
			self.resume = self.cleanText(self.resume)
		else:
			special_lines   = [line for line in lines_of_data if (('<a href="/wiki/' ) in line and wordSearchURL in line)]
			print '\n\n\n' +str(special_lines)
			proposition = []
			link = []
			for tmp in special_lines:
				if 'title="' in tmp and 'href="' in tmp:
					tmp_name_search = ((tmp.split('title="')[1]).split('"')[0])
					if (wordSearchURL in tmp_name_search  or wordSearchURL.split("_")[0] in tmp_name_search)and not '/' in tmp_name_search:
						proposition.append(tmp_name_search)
						tmp_link = ((tmp.split('href="')[1]).split('"')[0]).replace("/wiki/",'')
						tmp_link = tmp_link.replace('_',' ')
						link.append(tmp_link)
			self.infoList = ["Tu recherches quoi en particulier ?", proposition,link]

# end - Class HistoryScrapper