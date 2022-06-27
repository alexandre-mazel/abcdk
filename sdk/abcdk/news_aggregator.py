# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# news_aggregator tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################


"""Tools to work with our own news aggregator"""

print( "importing abcdk.news_aggregator" )

import datetime
import time
import urllib2

class NewsAggregator:
    """
    Our news aggregator is a file on a webserver manually generated or external scripts scrapping various news website.
    
    it consists of:
        -  stamp.dat: a stamp file: regenerated after each news generation, if it doesn't change, you don't have to download the next (big) data file.
        (you can also look a the data file stamp?) (cf look also to web caching).
        a text file containing format: YYYY_MM_DD_HH_MM_SS
        NDEV
        
        - news.dat: a csv file: each line is a news. format: 
        news_id; title; the_news; img_href (on protolab or elsewhere); date news (YYYY_MM_DD_HH_MM_SS); tags (lowercase, separated by ",");source;
        
    Examples:
        # basic:
        import abcdk.news_aggregator
        if abcdk.news_aggregator.newsAggregator.update():
            strToSpeak = abcdk.news_aggregator.newsAggregator.getLastNews()
            
        # flavoured:
        (ALKnowledge_OfUser.* has to be defined elsewhere)
        import abcdk.news_aggregator
        abcdk.news_aggregator.newsAggregator.update():
        listAllLikedStuffs = ALKnowledge_OfUser.getAllStuffsLikedByHuman()
        listNews = abcdk.news_aggregator.newsAggregator.getAllNewsFromTags(listAllLikedStuffs)
        for news in listNews:
            if listNews[0] not in ALKnowledge_OfUser.alreadySaidNews:
               strToSpeak =  "Voici une nouvelle qui devrait te plaire: d'apres %s: %s. %s" % (listNews[1], listNews[2]. listNews[3])
                
        
    """
    def __init__( self, bAutotest = False ):        
        self.aNews = dict() # the list of each news id => news cf class comments (~4 lines above)
        self.lastStamp = None
        self.bAutotest = bAutotest
        
    def getFileFromServer( self, bGetRealData = False ):
        """
        get stamp or data file contents, relatively to bGetRealData value
        """
        strSrc = 'http://protolab.aldebaran.com/news_server/'
        if self.bAutotest:
            strSrc += "autotest/"
            
        if not bGetRealData:
            strSrc += 'stamp.dat'
        else:
            strSrc += 'news.dat'
        httpRequest = urllib2.Request(strSrc)
        page = urllib2.build_opener().open(httpRequest)
        rawdata = page.read()
        print( "DBG: news_aggregator: getFileFromServer: rawdata: %s" % rawdata )
        return rawdata
        
    def stampToTime( self, strStamp ):
        """
        convert a YYYY_MM_DD_HH_MM_SS string to a system time in second
        """
        splitted = strStamp.split("_")
        dtt = datetime.datetime(int(splitted[0]), int(splitted[1]), int(splitted[2]), int(splitted[3]), int(splitted[4]), int(splitted[5]), 0 )
        t = time.mktime(dtt.timetuple()) # + dtt.microsecond / 1E6
        return t
        
    def _analyse( self, rawdata ):
        """
        analyse a raw data file contents, store news to self.aNews
        """
        linesOfData        = rawdata.split('\n')
        
        self.aNews = dict()
        for line in linesOfData:
            if len(line) < 3 or line[0] == "#":
                continue # eof or ...
            f = line.split(";")
            self.aNews[str(f[0])] = f[1:]
        
        
    def update( self ):
        """
        return true if news has been updated
        """
        rawdata = self.getFileFromServer()
        timeStamp = self.stampToTime( rawdata )
        print( "DBG: news_aggregator: getFileFromServer: timeStamp: %s" % timeStamp )
        if self.lastStamp != None and timeStamp - self.lastStamp < 0.1:
            return False
            
        self.lastStamp = timeStamp
        rawdata = self.getFileFromServer(True)
        self._analyse( rawdata )
            
        return True
        
    def getAllNews( self ):
        """
        return the dict of all news
        """
        return self.aNews
        
    def getLastNews( self ):
        """
        For compat: take last news and say it in a "Hopias demo" style:
        """
        # take last indexed one (must be on timestamp)
        n = sorted(self.aNews)[-1]
        news = self.aNews[n]
        print news
        source = news[4]
        title = news[0]
        resume = news[1]
        strN = "Voici la nouvelle %s la plus rÃ©cente: %s. %s" % (source, title, resume)
        return strN
        
    def getAllNewsFromTags( self, listTags = False ):
        """
        get all news specific to a liked tag
        - listTag: a list of lower case string  (when None: all tags are ok)

        return [] if no news or a list of [news_id, source, title, resume]
        """
        listNews = []
        for k, news in self.aNews.iteritems():
            if listTags != False:
                tags = news[3].split(",")            
                for t in listTags:
                    if t in tags:
                        break
                else: # du for
                    continue # no interesting tags in this news
            if 1: # already said ?
                listNews.append( [ k, news[4], news[0], news[1] ] )
        return listNews
        
    def __str__( self ):
        strOut = ""
        strOut += "last stamp: %s" % self.lastStamp
        strOut += "aNews: %s" % self.aNews
        return strOut
        
#class NewsAggregator - end

newsAggregator = NewsAggregator()


def autoTest():
    import test
    
    na = NewsAggregator( bAutotest = True )
    test.assert_check(na.update(),True)
    test.assert_check(na.update(),False)
    
    news = na.getAllNews()
    print( "DBG: news_aggregator: autoTest: news: %s" % news )
    test.assert_check(len(news),3)
    print na.getLastNews()
    
    news = na.getAllNewsFromTags()
    test.assert_check(len(news),3)
    test.assert_check(news[0][0], '1' )    # not mandatory: depends of the order in the dictionnary
    
    news = na.getAllNewsFromTags(["sport", "pipi"])
    print( "DBG: news_aggregator: autoTest: newsft: %s" % news )    
    test.assert_check(news[0][0], '2' )
    test.assert_check("Brest" in news[0][2])
    
    news = na.getAllNewsFromTags(["pipi"])
    test.assert_check(news, [] )    

# autoTest - end

if __name__ == "__main__":
    autoTest();
#~ import datetime
#~ print datetime.datetime.now().month