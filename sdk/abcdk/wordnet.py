# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Project Hopias
# wordnet
# Innovation - Protolab - mcaniot@aldebaran.com
# Aldebaran Robotics (c) 2016 All Rights Reserved - This file is confidential.
###########################################################

try:
	from nltk import data
	from nltk import wordpunct_tokenize
	from nltk.stem import SnowballStemmer
	from nltk.stem.snowball import FrenchStemmer 
	from nltk.stem.wordnet import WordNetLemmatizer
	from nltk import stem
	from nltk.corpus import wordnet
	from nltk.corpus import stopwords
	from nltk.tokenize import WordPunctTokenizer
	from nltk.corpus import sentiwordnet 
	from nltk.tokenize import word_tokenize
	from nltk.tokenize import RegexpTokenizer
	from nltk import pos_tag
except ImportError:
	print '[!] You need to install nltk (http://nltk.org/index.html)'


def _calculate_languages_ratios(text):
	"""
	Calculate probability of given text to be written in several languages and
	return a dictionary that looks like {'french': 2, 'spanish': 4, 'english': 0}
	
	@param text: Text whose language want to be detected
	@type text: str
	
	@return: Dictionary with languages and unique stopwords seen in analyzed text
	@rtype: dict
	"""

	languages_ratios = {}

	tokens = wordpunct_tokenize(text)
	words = [word.lower() for word in tokens]

	# Compute per language included in nltk number of unique stopwords appearing in analyzed text
	for language in stopwords.fileids():
		stopwords_set = set(stopwords.words(language))
		words_set = set(words)
		common_elements = words_set.intersection(stopwords_set)
		languages_ratios[language] = len(common_elements) # language "score"

	return languages_ratios

def detect_language(text):
	"""
	Calculate probability of given text to be written in several languages and
	return the highest scored.
	
	It uses a stopwords based approach, counting how many unique stopwords
	are seen in analyzed text.
	
	@param text: Text whose language want to be detected
	@type text: str
	
	@return: Most scored language guessed
	@rtype: str
	"""

	ratios = _calculate_languages_ratios(text)

	most_rated_language = max(ratios, key=ratios.get)

	return most_rated_language

def getAntonyms(word, lang = 'fra'):
	# example : good -> bad
	antonyms = []
	for syn in wordnet.synsets(word,lang= lang):
		for l in syn.lemmas():
			if l.antonyms():
				antonyms.append(l.antonyms()[0].name())
	return antonyms

def getBaseForm(word, lang = 'french'):
	french_stemmer = SnowballStemmer(lang)
	return french_stemmer.stem(word)

# in english
def getDefinition(synsetWord):
	return synsetWord.definition()

def getHypernyms(word):
	# example : hypernyms of dog are canin, beast, animal ...
	hyper = lambda s: s.hypernyms()
	w = putInSynset(translate(word))
	wn = wordnet.synset(w)
	return getSynsetListInFrench(list(wn.closure(hyper)))

def getHyponyms(word):
	# example :  the hyponyms of dog are dalmatian, boxer, terrier ... 
	hypo = lambda s: s.hyponyms()
	w = putInSynset(translate(word))
	wn = wordnet.synset(w)
	return getSynsetListInFrench(list(wn.closure(hypo)))

# in english
def getInfinitive(word):
	lemmatizer = WordNetLemmatizer()
	return lemmatizer.lemmatize(word,'v')

def getSenti(synsetWord):
	quote = sentiwordnet.senti_synset(synsetWord)
	'''if quote.pos_score() > quote.neg_score():
		return "good"
	elif quote.pos_score() < quote.neg_score():
		return "bad"
	else:
		return "neutral"'''
	return quote.pos_score() - quote.neg_score()

def getSentiText(text):
	# return a number between -1 if it is bad and 1 if it is good
	wordList = getWord(text)
	neg_score = 0
	pos_score = 0
	for tmp in wordList:
		tmp_translate = wordnet.synsets(tmp,lang ='fra')
		if len(tmp_translate)>0:
			tmp_translate = tmp_translate[0].name()
			#print tmp_translate
			quote = sentiwordnet.senti_synset(tmp_translate)
			pos_score = quote.pos_score()
			neg_score = quote.neg_score()
	'''if pos_score > neg_score:
		return "good"
	elif pos_score < neg_score:
		return "bad"
	else:
		return "neutral"'''
	return pos_score-neg_score
	pass

def getSentiWord(synsetWord):
	return sentiwordnet.senti_synsets(synsetWord)

def getSynonyms(word, lang = 'fra'):
	# example : synonyms of fire are heat, light ...
	synonyms = []
	for syn in wordnet.synsets(word,lang=lang):
		for l in syn.lemmas(lang=lang):
			synonyms.append(l.name())
	return synonyms

def getSynsetListInFrench(wordList):
	frenchList = []
	for syn in wordList:
		for l in syn.lemmas(lang="fra"):
			frenchList.append(l.name())
	return frenchList

def getWord(text):
	tokens = tokenizeByWord(text)
	french_stopwords = set(stopwords.words('french'))
	return [token for token in tokens if token.lower() not in french_stopwords]

def isSimilar(word1, word2):
	w1 = putInSynset(translate(word1))
	w2 = putInSynset(translate(word2)) 
	w1 = wordnet.synset(w1)
	w2 = wordnet.synset(w2)
	if w1.wup_similarity(w2) > 0.8 :
		return True
	else :
		return False

def putInSynset(word):
	result = (tagText(word)[0][1]).lower()
	tag = result[0]
	if tag == 'p':
		tag = 'n'
	if tag == 'j':
		tag = 'a'
	return (word+'.'+tag+'.01')

def stem_words(word):
	stemmer = stem.RegexpStemmer('s$|')
	return stemmer.stem(word)

def tagText(text):
	words = tokenizeByWord(text)
	return pos_tag(words)

def tokenizeByPhrase(text):
	tokenizer = data.load('tokenizers/punkt/french.pickle')
	return tokenizer.tokenize(text)

def tokenizeByWord(text, bPunctuation = False):
	if bPunctuation :
		tokenizer = WordPunctTokenizer()
	else:
		tokenizer = RegexpTokenizer(r'\w+')
	return tokenizer.tokenize(text)

def translate(word):
	tmp_word = stem_words(word)
	word_translate = translateWithSynonyms(tmp_word)
	if word_translate == "ERROR":
		word_translate = translateWithSynonyms(getBaseForm(word))

	if word_translate == "ERROR":
		try:
			word_translate = googleTranslateInEnglish(word)
		except :
			print "We can't use google translate for " + word
	return word_translate

def translateWithSynonyms(word):
	wordlist = wordnet.synsets(word,lang='fra')
	translateList = []
	for tmp in wordlist:
		for lemma in tmp.lemmas():
			translateList.append(lemma.name())

	finalList = []		
	for tmp in translateList:
		for synset in wordnet.synsets(tmp):
			for lemma in synset.lemmas():
				finalList.append(lemma.name())

	finalList = sorted(finalList)

	i = 0
	cpt = 0
	cpt_max = 0
	indice = -1
	for tmp in finalList:
		i = i +1
		if i < len(finalList):
			if tmp == finalList[i]:
				cpt = cpt + 1
				if cpt > cpt_max:
					indice = i
					cpt_max = cpt
			else:
				cpt = 0
	if indice == -1 :
		return "ERROR"
	else:
		return finalList[indice]

def googleTranslateInEnglish(word, lang = "fr"):
	try:
		import goslate
	except:
		print "Error You need to install goslate"
	gs = goslate.Goslate()
	return gs.translate(word,'en',lang ) 

def encodeList(wordList):
	if isinstance(wordList, list):
		new_list = []
		for tmp in wordList:
			new_list.append(tmp.encode('utf-8'))
		return new_list
	else:
		return wordlist.encode('utf-8')

if( __name__ == "__main__" ):

	print "chat et chien sont-ils similaire ? " + str(isSimilar("chat","chien")) + "\n\n\n\n"
			
	print "cherchons les synonymes de feu : " + str(getSynonyms("feu")) + "\n\n\n\n"
			
	print "cherchons les antonymes de bien : " + str(getAntonyms("bien")) + "\n\n\n\n"

	print "cherchons les hyponymes de chien : " + str(getHyponyms("chien")) + "\n\n\n\n"

	print "cherchons les hypernymes de chien : " + str(getHypernyms("chien")) + "\n\n\n\n"

	print "sentiment de bad : " + str(getSenti("bad.n.01")) + "\n\n\n\n"
			
	text = "je suis malade"
			
	print "sentiment du texte je suis malade : " + str(getSentiText(text)) + "\n\n\n\n" #wordnet.synsets("content",lang='fra')[0].name() #translate("content")
	
	print "cherchons les nom dans la phrase "+ text+ " : " + str(getWord(text)) + "\n\n\n\n"

	print "tokenize le texte par phrase "+ "je suis malade. J'aime les gens"+ " : " + str(tokenizeByPhrase("je suis malade. J'aime les gens")) + "\n\n\n\n"

	print "tokenize la phrase par mot " + text + " " +str(tokenizeByWord(text))

	print "On tag la phrase "  + "I am sick" + " : " + str(tagText("I am sick")) + "\n\n\n\n"
	pass