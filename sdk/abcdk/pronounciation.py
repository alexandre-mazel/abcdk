import json
import time
import datetime
import os
import random
import time

#import Levenshtein # Levenshtein.distance: nbr of letters inserted, ratio: a number (doesn't work on my nao)

import facerecognition
import filetools
import metaphone # taken from https://github.com/dracos/double-metaphone/blob/master/metaphone.py, thanks to Andrew Collins and ...
import nettools
import pathtools

class Pronounciation(object):
    DataUrl = "http://studio.aldebaran-robotics.com/humans/pronounciation.json?reload_bugging_proxy_AR_random=24"
    def __init__(self):
        object.__init__(self)
        self.data = []

    def remove_accents(self, data):
        import unicodedata
        import string
        if(type(data) == str):
            data = unicode(data.encode("utf-8"))
        return ''.join(x for x in unicodedata.normalize('NFKD', data) if x in string.ascii_letters).lower()

    def getFromWeb(self):
        """
        retrieve pronounciation dictionnary from the web
        """
        try:
            data = nettools.getHtmlPage(Pronounciation.DataUrl,
                    bWaitAnswer=True,
                    rTimeOutForAnswerInSec = 10.0,
                    bUseCache = True,
                    strUser = "nao", strPassword = "naonao", # a very small protection
                    )

            self.data = json.loads(data)
        except:
            print "[WRN] Impossible to load the pronounciation file ..."
            self.data = None

    def _get(self, keyword, language):
        """
            return a keyword by language for Nao speaking
        """
        if self.data == None:
            return keyword
        keyword = self.remove_accents(keyword)
        if keyword.lower() in self.data:
            occ = self.data[keyword]
            #if if occ is a dict, we have some language for this words
            if type(occ) == dict:
                # if I have a translation for this language
                if language in occ:
                    return occ[language]
                # no language found : return the default value
                if "en" in occ:
                    return occ["en"]
            else:
                # I have only one alternative !
                return occ
        return keyword

    def get(self, keywords, language="default"):
        """
        return a good pronounciation for NAO depending of the language
        keywords can be a string or a list :
            keywords = "jerome francois yuki"
            keywords = ["jerome", "francois"]
        language by default = default
        return a pronouciable word for each one
        """
        if type(keywords) == list:
            results = []
            for keyword in keywords:
                # this recursive call is normal (I want to manage multiple words
                # in the same string
                results.append(self.get(keyword, language))
            return results
        else:
            words = keywords.split(" ")
            result = ""
            for word in words:
                result += self._get(word, language)
                if word is not words[-1]:
                    result += " "
            return result

# instance simulate a singleton, a good way to do that ?
instance = Pronounciation()
if( 0 ):  # 13-11-15 Alma: commenting those autoloading as it takes time when generating documentation... (because there's a bug (at least on windows))
    instance.getFromWeb();

if __name__ == "__main__":
    print instance.get(u"Jerome")
    print instance.get(u"Jerome", "en")
    print instance.get(u"Jerome", "fr")
    print instance.get(u"Jerome celine", "fr")
    print instance.get(["Jerome", "celine"], "fr")
    print instance.get(["Jerome angelica", "celine"])
    print instance.get(["Jerome", "celine"], "notexit")
    print instance.get(u"celine")

