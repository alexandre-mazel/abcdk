# -*- coding: utf-8 -*-

#~ from __future__ import print_function
#~ def print( s ):
    #~ file = open("/tmp/output", "at" )
    #~ file.write(s)
    #~ file.close()
    


###########################################################
# Aldebaran Behavior Complementary Development Kit
# String tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################


"""Tools to work with string."""

print( "importing abcdk.stringtools" );


def findNumber( strText, nMinValue = -99999999, bFindLast = False ): # todo: int_min
    "find a number (int or float) indication in a text line"
    "return the number or None"
    "bFindLast: when set, the research is from the end"
    nLen = len( strText );
    nBegin = -1;
    nValueToRet = None;
    bStop = False;
    for i in range( nLen ):
#        debugLog( "findNumber: i: " + strText[i] );
        if( strText[i].isdigit() or strText[i] == '.' ):
            if( nBegin == -1 ):
                nBegin = i;
            if( i+1 == nLen ):
                # la chaine se termine par un chiffre, il faut l'analyser maintenant
                bStop = True;
                i += 1; # car on veut utiliser ce dernier charactere aussi
        else:
            if( nBegin != -1 ):
                bStop = True;
        if( bStop ):
            # print( "trying: '%s'" % strText[nBegin:i] );
            try:
                n = int( strText[nBegin:i] );
            except:
                try:
                    n = float( strText[nBegin:i] );
                except:
                    nBegin = i;
                    continue; # burk number
            # print( "findNumber(temp): in '%s': %s" %( strText, str( n ) ) );
            if( n > nMinValue ):
                if( not bFindLast ):
                    return n;
                nValueToRet = n; # memorise for later use
            # if( n > nMinValue ) - end
            bStop = False;
            nBegin = -1;
    return nValueToRet;
# findNumber - end

def findAfter( strText, strTextToFind ):
    "find the text after some text"
    "return '' if not found"
    nFind = strText.find( strTextToFind );
    if( nFind == -1 ):
        return "";
    return strText[nFind+len( strTextToFind ):];
# findAfter - end

def findBetween( strText, strTextBefore = None, strTextAfter = None, bFindLast = False  ):
    "find the text between to text"
    "if 'before text' is not found, return from the beginning"
    "if 'after text' is not found, return til the end"
    "TODO: use substr ! "
    if( strTextBefore == None ):
        nBegin = 0;
    else:
        if( bFindLast ):
            nBegin = strText.rfind( strTextBefore );
        else:
            nBegin = strText.find( strTextBefore );
        if( nBegin == -1 ):
            nBegin = 0;
        else:
            nBegin += len( strTextBefore );

    if( strTextAfter == None ):
        nEnd = len( strText );
    else:
        nEnd = strText.find( strTextAfter,  nBegin );
        if( nEnd == -1 ):
            nEnd = len( strText );
    return strText[nBegin:nEnd];
# findBetween - end

#print findBetween( "toto=35", "=" );


# previously nammed computeCRC_FromString
def computeCRC( strTxt, nLimitToFirstSize = -1 ):
    """compute the crc of one string
    return the value without modulating it
    (often you should Modulo 256 (%256) the result)"""
    i = 0;
    nSize = len( strTxt );
    if( nLimitToFirstSize != -1 ):
        if( nLimitToFirstSize < nSize ):
            nSize = nLimitToFirstSize;
    nSum = 0;
    while( i < nSize ):
        nSum += ord( strTxt[i] );
        i+= 1;
    return nSum;
# computeCRC_FromString - end
# print str( computeCRC_FromString( "Alex", 128 ) );


def transformAsciiAccentToUtf8( s, bDebugChar = False ):
    "change ascii (french?) accents to utf-8"
    strOutput = "";
    nLen = len( s );
    # We remark that only taken the ascii char bigger than E0 and outputting  0xC3 0xA0+(offset compared to E0) is working
    for i in range( 0, nLen ):
        if( bDebugChar ):
            print( "transformAsciiAccentToUtf8: %d %c 0x%x" % ( i, s[i], ord( s[i] ) ) );
        if( ord( s[i] ) >= 0xE0 ): # This works fine, for accent, but not for every strange character, eg: the movie "IRREVERSIBLE", with the last E, mirrored (some: "0xD0 0xAF 0xC6 0x8E")
            strOutput = strOutput + chr(0xC3) + chr( 0xA0+ord( s[i] )-0xE0 );
        else:
            if( ord( s[i] ) > 127 and ord( s[i] ) != 0xC3 and ord( s[i-1] ) != 0xC3 ): # looks like rotten characters, skipping it (but the eacute)
                pass;
            else:
                strOutput = strOutput + s[i];
    return strOutput;
# transformAsciiAccentToUtf8 - end
#~ print( "transformAsciiAccentToUtf8:" );
#~ print( transformAsciiAccentToUtf8("stéphanïe" ) );
#~ print( transformAsciiAccentToUtf8("éèêë" ) );

def clean_encoding(s):
    """
    should work with some gentle string, but...
    """
    if isinstance(s, unicode):
        return s
    else:
        return s.decode('utf8');
# clean_encoding - end
#~ print( "clean_encoding:" );
#~ print( clean_encoding("stéphanïe" ) ); # does'nt works !
#~ print( clean_encoding("éèêë" ) );

def convert_accent( strTxt ):
  "convert accent from dos ascii francais (ISO-8859?) to utf-8"
  strTxt = strTxt.decode( "latin1" );
  strTxt = strTxt.encode( "utf8" );
  return strTxt;
# convert_accent - end
#~ print( "convert_accent:" );
#~ print( convert_accent("stéphanïe" ) );
#~ print( convert_accent("éèêë" ) );


def convertToUtf8( s ):
    """
    Convert anything to utf8 !
    """
    if not isinstance( s, basestring ):
        s = "stringtools.convertToUtf8: ERR: %s not a string !!!" % str(s);
        return s;
    if isinstance( s, str ):
        return transformAsciiAccentToUtf8(s);
    if isinstance( s, unicode ):
        return s.encode('utf8');
# convertToUtf8 - end

#~ print( "convertToUtf8:" );
#~ print( convertToUtf8( "stéphanïe" ) );
#~ print( convertToUtf8( "éèêë" ) );
#~ print( convertToUtf8( u"stéfie" ) );
#~ print( convertToUtf8( str("simple" ) ) );


def removeFrenchAccent( s ):
    """
    Remove french accent from text (a bad unoptimised method)
    """
    strOutput = "";
    nLen = len( s );
    convTable = [
        ["âäà", 'a'],
        ["ç", 'c'],
        ["éèêë", 'e'],
        ["îï", 'i'],
        ["ôö", 'o'],
        ["ùûü", 'u'],
    ];
    if not isinstance( s, str ):
        for i in range( 0, nLen ):
            #~ print( "s[i]: %s" % s[i] );
            for conv in convTable:
                if( s[i] in conv[0] ):
                    strOutput += conv[1];
                    #~ print( "apres lettre: " + strOutput );
                    break;
            else:
                strOutput += s[i];
                #~ print( "apres ajout: " + strOutput );
    else:
        for i in range( 0, nLen ):
            if( ord( s[i] ) == 0xC3 ):
                continue;
            for conv in convTable:
                if( s[i] in conv[0] ):
                    strOutput += conv[1];
                    break;
            else:
                strOutput += s[i];
    return strOutput;
# removeFrenchAccent - end
#~ print( "removeFrenchAccent:" );
#~ print( removeFrenchAccent("stéphanïe" ) );
#~ print( removeFrenchAccent("éèêëàôöç" ) );
#~ print( removeFrenchAccent(convertToUtf8("stéphanïe" ) ));

def convertSubString( s, convTable ):
    """
    Convert all substring in a txt by other string
    convTable: a table wich left part one char to replace by other one, and the right part the word to put
        cf convertForHtmlArgs
        eg: [
                ["âäà", 'a'],
                ["ç", 'c'],
                ["éèêëËÊÉ", 'e'],
                ["îï", 'i'],
                ["ôö", 'o'],
                ["ùûü", 'u'],
            ];
    """
    strOutput = "";
    nLen = len( s );
    for i in range( 0, nLen ):
        if( ord( s[i] ) == 0xC3 ):
            continue;
        for conv in convTable:
            if( s[i] in conv[0] ):
                strOutput += conv[1];
                break;
        else:
            strOutput += s[i];
    return strOutput;
# convertSubString - end

def convertForHtmlArgsDumb( strTxt ):
    """
    convert a string to a string sendable as an argument for a web page.
    eg: "Le président des états unis" => "Le_president_des_etats_unis" (exemple non contractuel)
    """
    convTable = [
        ["âäà", 'a'],
        ["ç", 'ss'],
        ["éèêëËÊÉ", 'ai'],
        ["îï", 'i'],
        ["ôö", 'o'],
        ["ùûü", 'u'],
    ];
    strOut = strTxt.replace( " ", "_" );
    strOut = convertSubString( strOut, convTable );
    return strOut;
# convertForHtmlArgsDumb - end


def phonetiseFrenchAccent( strTxt ):
    """
    Transform a text with french accent to a not problematic ascii < 0x7f sentences, but sounding quite the same.
    v0.71
    """
    strOut = strTxt;
    #~ strOut = strOut.replace( " ", "_" );
    #~ import debug
    #~ print debug.dumpHexa( strOut );
    #~ strOut = strOut.encode('Latin-1', 'strict');

    #~ convTable = [
        #~ ["âäà", 'a'],
        #~ ["çÇ", 'ss'],
        #~ ["éèêëËÊÉ", 'ai'],
        #~ ["îï", 'i'],
        #~ ["ôö", 'o'],
        #~ ["ùûü", 'u'],
    #~ ];
    #~ strOut = convertSubString( strOut, convTable );
    # normal latin1 conversion
    convTable = [
        [[0xE2, 0xE4, 0xE0], 'a'],              # "âäà"
        [[0xE7, 0xC7], 'ss'],                    # "çÇ"
        [[0xE9, 0xE8,0xEA, 0xEB,0xCB, 0xCA, 0xC9], 'ai'], # "éèêëËÊÉ"
        [[0xEE, 0xEF], 'i'],        # "îï"
        [[0xF4, 0xF6], 'o'],        # "ôö"
        [[0xF9, 0xFB, 0xFC], 'u'],        # "ùûü"
    ];
    # oem style conversion
    altConvTable = [
        [[0xA2, 0xA4, 0xA0], 'a'],              # "âäà"
        [[0xA7, 0xC7], 'ss'],                    # "çÇ"
        [[0xA9, 0xA8,0xAA, 0xAB,0xAB, 0xAA, 0xA9], 'ai'], # "éèêëËÊÉ"
        [[0xAE, 0xEF], 'i'],        # "îï"
        [[0xB4, 0xB6], 'o'],        # "ôö"
        [[0xB9, 0xBB, 0xBC], 'u'],        # "ùûü"
    ];
    strOutput = "";
    nLen = len( strOut );
    i = 0;
    while( i < nLen ):
        if( ord(strOut[i]) == 0xC3 ):
            i += 1;
            for conv in altConvTable:
                if( ord(strOut[i]) in conv[0] ):
                    strOutput += conv[1];
                    break;
            else:
                print( "WRN: unhandled alt char at pos %d: (0x%2x)" % (i, ord(strOut[i] ) ) );
                pass; # unknown char is skipped!
        else:
            for conv in convTable:
                if( ord(strOut[i]) in conv[0] ):
                    strOutput += conv[1];
                    break;
            else:
                strOutput += strOut[i];
        i += 1;
    return strOutput;
# phonetiseFrenchAccent - end
#~ print( phonetiseFrenchAccent( u"stéphanïe" ) );
#~ print( phonetiseFrenchAccent( u"Qui est le président des états unis ?" ) );
#~ print( phonetiseFrenchAccent( u"C'est quoi la meilleure sÃ©rie tÃ©lÃ©" ) );

def html_encode( strTxt ):
    """
    convert a string to a string sendable as an argument for a web page.
    eg: "Le président des états unis" => "Le%20pr%C3%A9sident%20des%20%C3%89tats%20Unis%20fait%2030%" (exemple non contractuel)
    v0.6
    """
    strOutput = "";
    nLen = len( strTxt );
    for i in range( 0, nLen ):
        if( ord( strTxt[i] ) > 0x7f or ord( strTxt[i] ) <= 0x20  ):
            strOutput += "%%%02X" % ord( strTxt[i] );
        elif( strTxt[i] == "%" ):
            strOutput += "%%";
        else:
            strOutput += strTxt[i];
    return strOutput;
# html_encode - end
#~ strTxt = "Le président des États Unis fait 30%";
#~ print( strTxt );
#~ print( html_encode( strTxt ) );

def html_decode( strTxt ):
    """
    convert a string to a string sendable as an argument for a web page.
    eg: "Le président des états unis" => "" (exemple non contractuel)
    v0.6
    """
    strOutput = "";
    nLen = len( strTxt );
    i = 0;
    while( i < nLen ):
        if( strTxt[i] == "%" ):
            if( strTxt[i+1] == "%" ):
                strOutput += "%";
                i += 1;
            else:
                #~ print( strTxt[i+1:i+3] );
                nNum = int( strTxt[i+1:i+3], base=16 );
                strOutput += chr( nNum );
                i += 2;
        else:
            strOutput += strTxt[i];
        i += 1;
    return strOutput;
# html_decode - end
#~ print( html_decode( "Le%20pr%C3%A9sident%20des%20%C3%89tats%20Unis%20fait%2030%%" ) );
#~ print( html_decode( "%C3%87a%20te%20parle%20les%20%C3%89tats-Unis" ) );



def isVersionFresher( strPrev, strNext ):
    "return True if strNext contains a fresher version number than strPrev (not equal)"
    "version are something like 1.0, 0.9, 1.8.16, 1.100.1888, ..."
    "1.0 is equal to 1."
    aPrev = strPrev.split( '.' );
    aNext = strNext.split( '.' );

    # change 1. by 1.0
    if( aPrev[-1] == '' ):
        aPrev[-1] = '0';
    # change 1. by 1.0
    if( aNext[-1] == '' ):
        aNext[-1] = '0';

    #~ print( "aPrev: %s" % str( aPrev ) );
    #~ print( "aNext: %s" % str( aNext ) );
    for idx in range( len( aNext ) ):
        if( len( aPrev ) <= idx ):
            return True;
        if( aPrev[idx] != aNext[idx] ):
            return int(aNext[idx]) > int( aPrev[idx] );
    return False; # equal => False

# isVersionFresher - end

def dictionnaryToString( aDico ):
  "return a beautiful and sorted string describing a dictionnaries for debugging or printing..."
  s = "# dictionnary has %d element(s):\n" % ( len( aDico ) );
  for k, v in sorted( aDico.iteritems() ):
    s += "  '%s': %s,\n" % ( str(k), str(v) );
  return s;
# dictionnaryToString - end

def sizeToString( nValSize ):
    "return a printable 'smart' size representing a disk size"
    " 3 => 3"
    " 2000 => 1.9k"
    " 20000000 => 20M"
    "..."

    aszUnits = ["", "K", "M", "G", "T" ];
    nUnit = 1024;
    nIdx = 0;
    while( nUnit <= nValSize ):
        nUnit *= 1024;
        nIdx += 1;
    if( nIdx != 0 ):
        rValue = nValSize/float(nUnit/1024);
        strValue = "%6.1f" % rValue;
    else:
        strValue = str( nValSize );
    return strValue + " " + aszUnits[nIdx];
# sizeToString - end
#print( sizeToString( 1024*1024*1024 ) );

def timeToString( rTimeSec ):
    "convert a time in second to a string"
    "convert to be compact and meaning full"
    "v0.6"
    # we will limit to 2 values
    nCptValue = 0;
    strOut = "";
#    strOut = "(%5.2f) " % rTimeSec;

    if( rTimeSec < 0.001 ):
        return "0 ms";

    nDividend = 60*60*24*30; # 30 day per month as an average!
    if( rTimeSec >= nDividend and nCptValue < 2 ):
        nVal = int( rTimeSec / nDividend );
        strOut += "%d min " % nVal;
        rTimeSec -= nVal * nDividend;
        nCptValue += 1;

    nDividend = 60*60*24;
    if( rTimeSec >= nDividend and nCptValue < 2 ):
        nVal = int( rTimeSec / nDividend );
        strOut += "%d j " % nVal;
        rTimeSec -= nVal * nDividend;
        nCptValue += 1;

    nDividend = 60*60;
    if( rTimeSec >= nDividend and nCptValue < 2 ):
        nVal = int( rTimeSec / nDividend );
        strOut += "%d hour " % nVal;
        rTimeSec -= nVal * nDividend;
        nCptValue += 1;

    nDividend = 60;
    if( rTimeSec >= nDividend and nCptValue < 2 ):
        nVal = int( rTimeSec / nDividend );
        strOut += "%d min " % nVal;
        rTimeSec -= nVal * nDividend;
        nCptValue += 1;

    nDividend = 1;
    if( rTimeSec >= nDividend and nCptValue < 2 ):
        nVal = int( rTimeSec / nDividend );
        strOut += "%d s " % nVal;
        rTimeSec -= nVal * nDividend;
        nCptValue += 1;

    if( rTimeSec > 0. and nCptValue < 2 ):
        strOut += "%3d ms" % int( rTimeSec*1000 );
        nCptValue += 1;

    return strOut;
# timeToString - end

# print timeToString( 60*60+15);

def textToLines( strText ):
    "receive a text and cut it in an array of line"
    aLines = [];
    nBegin = 0;
    nEnd = len( strText );
    while( True ):
        nFind = strText[nBegin:].find( "\n" );
        # print( "nBegin: %d, nFind: %d, nEnd: %d" % (nBegin, nFind, nEnd) );
        if( nFind > 0 ):
            aLines.append( strText[nBegin:nFind+nBegin] );
            nBegin = nFind+nBegin+1;
        elif( nFind == 0 ):
            nBegin += 1;
        else:
            break;
    if( nBegin < nEnd ):
        aLines.append( strText[nBegin:] );
    return aLines;
# textToLines - end

# print( "text: %s" % str( textToLines( "a text:\nyoupla!\n\nGogo!\ncoucou") ) );

def getFinalRhyme( strText ):
    "analyse a sentence and return the final rhyme"
    # basic approach: search for last audible sound (too bad)
    aListFinal = ["a", "e", "i", "o", "u"];
    for i in range( len( strText )-1, -1, -1 ):
        if( strText[i] in aListFinal ):
            return strText[i];
    return "";
# getFinalRhyme - end
# print( "getFinalRhyme(): '%s'" % str( getFinalRhyme("bonjour papa") ) );

def getPoilau( strText ):
    "analyse a sentence and return the final rhyme"
    # basic approach: search for last audible sound (too bad)
    aListFinal = {
                            # set shortest at the end! (impossible: it's a dict!)
                            "ate": "patte",
                            "atte": "patte",
                            "an": "dent",
                            "en": "dent",
                            "a": "bras",
                            "ette": "roupette",
                            "é": "pied",
                            "ou": "coucou",
                            "ard": "dard",
                            "ouille": "grenouille",
                            "o": "dos",
                            "eil": "orteil",
                            "euf": "sseuf",
                            "ine": "céline",
                            "in": "valentin",
                            "ien": "chien",
                            "i":"zizi",
                            "isse":"clitoris",
                            "esse":"fesse",
                            "0": "dos",
                            "1": "main",
                            "2": "yeux",
                            "3": "doigt",
                            "4": "patte",
                            "5": "seins",
                            "6": "cuisse",
                            "7": "quéquette",
                            "8": "bite",
                            "9": "keufs",
                            "10": "saucisse",
                            "12": "barbouze",
                            "13": "fraise",
                            "14": "naoqi 1 14",
                            "16": "obese",
                            "20": "main",
                    };

    nPosMax = -1;
    strBetterFinal = "";
    nBetterLen = 0;
    for k,v in aListFinal.iteritems():
        nPos = strText.rfind( k );
        # print( "rfind '%s' in '%s' => %d" % (k,strText, nPos ) );
        nLenK = len( k );
        if( nPos+nLenK > nPosMax+nBetterLen ): # longer is better
            if( nPos > len( strText ) * 0.7 ): # sinon ca semble pas trop a la fin
                nPosMax = nPos;
                strBetterFinal = v;
                nBetterLen = len( k );
    return strBetterFinal;
# getPoilau - end
#~ print( "getPoilau(): '%s'" % str( getPoilau("bonjour papa") ) );
#~ print( "getPoilau(): '%s'" % str( getPoilau("bonjour maman") ) );
#~ print( "getPoilau(): '%s'" % str( getPoilau("bonjour krazucki") ) );
#~ print( "getPoilau(): '%s'" % str( getPoilau("Bonjour, je suis NaoAlex, Mon adresse internet est 10 ") ) );

def floatArrayToText( a, nPrecision = 2 ):
    """
    output a float array using a fixed precision
    """
    import typetools
    strOut  = "[ ";
    strFormat = "%%.%df" % nPrecision;
    bFirst = True;
    for value in a:
        if( bFirst ):
            bFirst = False;
        else:
            strOut += ", ";
        if( typetools.isArray( value ) ):
            strOut += floatArrayToText( value, nPrecision = nPrecision );
        else:
            strOut +=  strFormat % value;
    return strOut + "]";
# floatArrayToText - end
#~ print( floatArrayToText( [ 1.90009, 3, [2.339, 10000.7] ] ) );

def levenshtein( a,b ):
    """
    Calculates the Levenshtein distance between a and b.
    from http://hetland.org/coding/python/levenshtein.py
    """

    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n

    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]
# levenshtein - end

#~ print( levenshtein( "bateau", "batau" ) );
#~ print( levenshtein( "bateau", "bataux" ) );
#~ print( levenshtein( "KSTLPRSTNTTSTTSNS", "KSTPRKPM" ) );

def isPhoneticEqual( s1, s2 ):
    """
    return the phonetic equality between of two string: [0., .. 1.] : 0 completely different, from 0 to 1: the more resesembling, 1: equal]
    """
    import metaphone
    #~ print metaphone.dm( unicode(s1) )
    #~ print metaphone.dm( unicode(s2) )
    try:
        meta1 = metaphone.dm( unicode(s1) )[0]
        meta2 = metaphone.dm( unicode(s2) )[0]
    except BaseException, err:
        print( "ERR: can't metaphone '%s' or '%s': err: %s" % (s1, s2, err ) )
        meta1 = s1
        meta2 = s2
    if meta1 == meta2:
        return 1.

    rMidLen = ( len(meta1) + len( meta2 ) ) / 2;
    if( rMidLen < 1 ):
        return 0.
    rDist = 0.9 - levenshtein( meta1, meta2 )/float(rMidLen)
    if( rDist < 0. ):
        rDist = 0.
    return rDist
# isPhoneticEqual - end    

#~ print isPhoneticEqual( "Gabriel", "Gabrielle" )
#~ print isPhoneticEqual( "Gabriel", "Jean pierre kalfon le grand" )
#~ print isPhoneticEqual( "Alexandre", "Robert" )
#~ print isPhoneticEqual( "Alexandre", "Alexandra" )
#~ print isPhoneticEqual( "Alexandre", "Alexandrin" )
#~ print isPhoneticEqual( "Alexandre", "Alexis" )
#~ print isPhoneticEqual( "Je t'aime le lundi", "Je t'aime le mardi" )
#~ print isPhoneticEqual( "lundi", "mardi" )
#~ exit(0)

def correctSentence( strTxt ):
    """
    Correct a sentence so it's well correct.
    eg: "Va dans le bureau de estelle" => "Va dans le bureau d'estelle"
    """
    print( "INF: stringtools.correctSentence: input '%s'" % strTxt );
    bModified = True;
    while( bModified ):
        # brute replace
        strTxtNew = strTxt.replace( "de le", "du" );

        strTxtNew = strTxtNew.replace( "de e", "d'e" );
        strTxtNew = strTxtNew.replace( "de E", "d'E" );
        strTxtNew = strTxtNew.replace( "de a", "d'a" );
        strTxtNew = strTxtNew.replace( "de A", "d'A" );
        strTxtNew = strTxtNew.replace( "le e", "l'e" );
        strTxtNew = strTxtNew.replace( "le E", "l'E" );
        strTxtNew = strTxtNew.replace( "le a", "l'a" );
        strTxtNew = strTxtNew.replace( "le A", "l'A" );
        strTxtNew = strTxtNew.replace( "le i", "l'i" );
        strTxtNew = strTxtNew.replace( "le I", "l'I" );

        strTxtNew = strTxtNew.replace( "IT", "I T" );

        # specific word following
        words = strTxtNew.split();
        #~ print words
        for idx, word in enumerate( words ):
            if( word.lower() == "bureau" ):
                if( idx + 1 < len( words ) ):
                    if( not words[idx+1].lower() in ["de", "du", "d'", "le", "la"] and words[idx+1][1] != "'" ):
                        strTxtNew = strTxtNew.replace( word, word + " de" ); # not optimal: only on replace per loop (even if a lot of specific word in that sentence)
                        break;
                if( idx - 1 >= 0 ):
                    if( not words[idx-1].lower() in ["le", "la", "du"] ):
                        strTxtNew = strTxtNew.replace( word, "le " + word ); # not optimal: only on replace per loop (even if a lot of specific word in that sentence)
                        break;
            if( word.lower() == "dans" ):
                if( idx + 1 < len( words ) ):
                    if( not words[idx+1].lower() in ["le", "la"] and ( len(words[idx+1]) < 2 or words[idx+1][1] != "'" ) ):
                        strTxtNew = strTxtNew.replace( word, word + " le" ); # not optimal: only on replace per loop (even if a lot of specific word in that sentence)
                        break;

        if( strTxtNew == strTxt ):
            bModified = False;
        else:
            strTxt = strTxtNew;
            #~ print( "intermediaire: '%s'" % strTxt );
    return strTxt;

# correctSentence - end

def correctSentenceAutoTest():
    listTest = [
                    "Va dans bureau laurent",
                    "Va dans bureau de estelle",
                    "va a le accueil",
                    "va dans bureau alex",
                    "va dans accueil",
                    "c'est le robot de le chef",
                    "va voir dans le bureau",
                    "va voir dans IT",
                    "va voir dans pod du bureau de laurent",
                    "J'irais bien voir dans maquette!"
                ];
    listCorrected = [
                    "Va dans le bureau de laurent",
                    "Va dans le bureau d'estelle",
                    "va a l'accueil",
                    "va dans le bureau d'alex",
                    "va dans l'accueil",
                    "c'est le robot du chef",
                    "va voir dans le bureau",
                    "va voir dans l'I T",
                    "va voir dans le pod du bureau de laurent",
                    "J'irais bien voir dans le maquette!",
                ];

    for idx, txt in enumerate( listTest ):
        strRet = correctSentence( txt );
        print( "'%s' =>\n'%s'" % (txt, strRet ) );
        assert( strRet == listCorrected[idx] );
        # other case:
        #~ strRet = correctSentence( txt.lower() );
        #~ assert( strRet == listCorrected[idx].lower() ); # fonctionne pas avec IT !
#correctSentenceAutoTest - end

#~ correctSentenceAutoTest();

def generatePossibleCombination( aaList ):
    """
    take a list of list and generate all posibilities
    - aaList: a tuple of list eg: (["Bureau", "Chambre"], [ "Alexandre", "Laurent"] )
    => "Bureau Alexandre", "Bureau Laurent", "Chambre Alexandre", "Chambre Laurent"
    """
    a = [];
    for e1 in aaList[0]:
        for e2 in aaList[1]:
            a.append( e1 + " " + e2 );
    return a;
# generatePossibleCombination - end

def extractMainKeyWords(aSentence):
    """
    aSentence is a list of words: "Hier je suis allé voir la tour Eiffel"
    in this case we want to extract tour Eiffel
    """
    # Main keywords have more than 4 letters
    if type(aSentence) == str:
        aSentence = aSentence.split(' ')
    nMininumNbrLetters = 3
    aPossibleWords = [strWord for strWord in aSentence if (len(strWord) > nMininumNbrLetters)]

    # for now we consider than main keywords are at the end of the string (the last 2 words)
    nNbrLastWords = 2
    nNbrLastWords = min(len(aPossibleWords), nNbrLastWords)
    aPossibleWords = aPossibleWords[-nNbrLastWords:]
#    print aPossibleWords
    return aPossibleWords
    
def getSomethingToTell( astrTexts ):
    """
    receive a list of text ["hello", "hi"] and choose which one to say
    astrTexts: a list of text, a single text or a single text with "/" in it
    """
    import numeric
    if( isinstance( astrTexts, list ) ):
        aTexts = astrTexts; # alternate form
    else:
        aTexts = astrTexts.split("/");
    return aTexts[numeric.randomDifferent(0,len(aTexts)-1)];
#~ print getSomethingToTell( "hello" )
#~ print getSomethingToTell( ["hello", "hi"] )
#~ print getSomethingToTell( "hello/hi/good morning" )

def convertForFilename( strTxt ):
    """
    convert a text to be usable as filename
    "toto est content" => "toto_est_content"
    """
    s = strTxt
    s = s.replace( " ", "_" )
    s = s.replace( "'", "_" )
    s = s.replace( "\"", "_" )
    s = s.replace( ",", "_" )
    s = s.replace( ":", "_" )
    s = s.replace( "/", "_" )
    s = s.replace( "\\", "_" )
    s = s.replace( "-", "_" )
    return s
# convertForFilename - end


def autoTest():
    import test
    strNumber = "<br><strong>My IP Country Latitude</strong>: (46) <br><b>My IP Address City</b>:&nbsp;&nbsp; <font color='#980000'>Pa";
    nVal = findNumber( strNumber );
    print( "nVal: %s" % str( nVal ) );
    strNumber = "blablabla 3.59";
    nVal = findNumber( strNumber );
    print( "nVal: %s" % str( nVal ) );
    assert( nVal == 3.59 );
    assert( sizeToString( 3 ) == "3 " );
    assert( sizeToString( 1500 ) == "   1.5 K" );
    assert( sizeToString( 1024*1024*1024 ) == "   1.0 G" );
    res = timeToString( 60*60+15 );
    print( "'%s'" % res );
    assert( res == "1 hour 15 s " );

    strText = "Hello Alexandre";
    strOut = findAfter( strText, "Hello " );
    print( "findAfter: '%s'" % strOut );
    assert( strOut == "Alexandre" );
    strOut = findAfter( strText, "introuvable" );
    assert( strOut == "" );

    strText = "Hello Alexandre, comment ca va?";
    strOut = findBetween( strText, "Hello ",  ", comment ca va?" );
    print( "findBetween: '%s'" % strOut );
    assert( strOut == "Alexandre" );
    strOut = findBetween( strText, "introuvable1",  "introuvable2" );
    print( "findBetween: '%s'" % strOut );
    strOut = findBetween( strText );
    print( "findBetween: '%s'" % strOut );
    assert( strOut == strText );

    assert( isVersionFresher( "1.0", "1.1" ) );
    assert( not isVersionFresher( "1.0", "1.0" ) );
    assert( not isVersionFresher( "1.", "1.0" ) );
    assert( not isVersionFresher( "1.1", "1.0" ) );
    assert( isVersionFresher( "1.1", "1.1.5.6.7" ) );
    assert( isVersionFresher( "1.1", "2" ) );
    assert( not isVersionFresher( "1.1", "0" ) );
    assert( not isVersionFresher( "1.1", "" ) );

#    print extractMainKeyWords("Hier je suis aller voir la tour eiffel")
    assert(extractMainKeyWords("Hier je suis aller voir la tour eiffel") == ['tour', 'eiffel'])
    assert(extractMainKeyWords("Ouais dehors il y a plein de nuages") == ['plein', 'nuages'])
    
    test.assert_check( isPhoneticEqual( "Gabriel", "Gabrielle" ), 1. )
    test.assert_check( isPhoneticEqual( "Gabriel", "Alexandre" ), 0. )
    test.assert_check( levenshtein( "chicken please", "checkin please" ), 2 )
    test.assert_check( levenshtein( "chicken please", "checking please" ), 3 )
    
    test.assert_check_float( isPhoneticEqual( "Alexandre", "Alexis" ), 0.4 )
    test.assert_check_float( isPhoneticEqual( "aicoute moi", "écoute moi" ), 0.718 ) # TODO: gerer les accents
    test.assert_check( isPhoneticEqual( "chicken please", "checkin please" ), 1. )   
# autoTest - end

if __name__ == "__main__":
    autoTest();
#~ import datetime
#~ print datetime.datetime.now().month