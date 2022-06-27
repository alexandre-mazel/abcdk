import aruco_def # generated from csv with list of known aruco

def getDictionaryType():
    return aruco_def.nDictionaryType
    

def getArucoName( nNumber ):
    """
    name is always in english
    return "" if unknown
    """
    try:
        return aruco_def.dictDesc[nNumber]['en']
    except BaseException as err:
        print("DBG: getArucoName: %s" % str(err) )
        pass
    return ""

def getArucoMeaning( nNumber, strLang = "French" ):
    """
    return the good sentence related to the current robot tts language.
    send the lang as returned from ALTextToSpeech.getLanguage
    return "" if unknown
    """
    try:
        strLn = strLang[:2].lower()
        return aruco_def.dictDesc[nNumber][strLn]
    except BaseException as err:
        print("DBG: getArucoMeaning: %s" % str(err) )
        pass
    return ""
