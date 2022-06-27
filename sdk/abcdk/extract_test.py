__author__ = 'lgeorge'
try: import BeautifulSoup
except: pass
import HTMLParser

def oldTest():
    h = HTMLParser.HTMLParser()
    with open('chanson.htm', 'r') as htmlFile:
        soup = BeautifulSoup.BeautifulSoup(htmlFile)
        aString = soup.findAll('pre')
        for paragraphe in aString:
            for field  in paragraphe.split(','):
                aRes = [ h.unescape(strParagraph.text) for strParagraph in  aString ]

    # artiste - titre , artiste - titre, artiste-titre ...
    for e in aString:
        print e
        print "  FIN  "

