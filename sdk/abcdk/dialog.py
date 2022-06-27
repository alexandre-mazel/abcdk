# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Dialog Tools
# Author A. Mazel
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Dialog Tools: handle dialog"

print( "importing abcdk.dialog" );

import arraytools
import metaphone
import numeric
import stringtools

global_nNbrAssertCheck = 0
def assert_check( v1, reference = True, bQuiet = False ):
    global global_nNbrAssertCheck
    global_nNbrAssertCheck += 1
    if not bQuiet: print( "%d: assert_check: %s" % (global_nNbrAssertCheck, str(v1)) )
    if( v1 != reference ):
        retline1 = ""
        retlineref = ""        
        if( len(str(v1)) > 8 or len(str(reference)) > 8 ):
            retline1 = "\n"
            retlineref = "\n"
            
        print( "assert_check (val != ref): %s'%s' != %s'%s'" % (retline1, v1, retlineref, reference) )
        assert(0)    

def assert_checkq( v1, ref ):
    return assert_check(v1,ref,bQuiet = True )
    
def getLastSentence( strText ):
    """
    return the last sentence of a text block
    eg: 
        "Hello I'm nao. What Can I do for you?" => "What Can I do for you?"
        "Je suis content. Je suis même très content." => "Je suis même très content."
    """
    eos = [".","?","!"]
    nPosLastSep = 0
    for i in range(len(strText)-3,0,-1): # -2, because we want too skip last chars
        if( strText[i] in eos ):
            nPosLastSep = i+1
            break
    return strText[nPosLastSep:].strip()
# getLastSentence-end    
assert_checkq( getLastSentence("Hello I'm nao. What Can I do for you?"), "What Can I do for you?" )
assert_checkq( getLastSentence("Je suis content. Je suis même très content."), "Je suis même très content." )
        
        
def flattenList( l ):
    """
    take a compound list and flatten it.
    eg: [1, [2,3], [4, [5, 6] ] ] => [1,2,3,4,5,6]
    """
    out = []
    for e in l:
        if( isinstance( e, list ) ):
            out.extend( flattenList(e) )
        else:
            out.append(e)
    return out
# flattenList - end
assert_check( flattenList( [1, [2,3], [4, [5, 6] ] ] ), [1,2,3,4,5,6] )

def stripObject(l):
    """
    strip a list or a string, if the l is a single string instead of a list
    """
    if( isinstance( l, list ) ):
        out = []
        for e in l:
            out.append(stripObject(e) )
        return out
    return l.strip( " _\r" )
    
def stripFromObject(l, aCharToStrip = "'[]()" ):
    if( isinstance( l, list ) ):
        out = []
        for e in l:
            out.append( stripFromObject(e, aCharToStrip) )
        return out
    return l.strip( aCharToStrip )
    
def stripDecoratorFromObject(l):
    """
    remove ", ', or [ from a list or from a string, if l is a single string instead of a list.
    """
    return stripFromObject( l, "'[]()" )
    
def stripDoubleQuoteFromObject(l):
    """
    remove ", ', or [ from  a list or a string, if the l is a single string instead of a list
    """
    return stripFromObject( l, "\"" )
    
def splitProtecting(s, splitchars, protectchars = "()", enclosingProtectedChar = '"' ):
    """
    like split, but don't split into some protected area. And the protected could be enclosed in " also ! protecting them !
    eg: "bonjour les gens", " ", "()" => ["bonjour", "les", "gens"]
    eg: "bonjour (les gens)", " ", "()" => ["bonjour", "(les gens)"]
    - protectchars: a couple of enter and exit chars
    
    NB: don't handle nested protectors
    NB: don't handle nested enclosers
    
    """
    a = []
    bInEnclosed = False
    bInProtected = False
    nBeginIdx = 0
    for i in range(len(s)):
        if( s[i] in enclosingProtectedChar ):        
            bInEnclosed = not bInEnclosed
            continue
        if( bInEnclosed ):
            continue
        if( not bInProtected ):
            if( s[i] in splitchars ):
                if( i-nBeginIdx > 1 ):
                    a.append( s[nBeginIdx: i] )
                nBeginIdx = i+1
            else:
                if( s[i] == protectchars[0] ):
                    bInProtected = True                    
                    # don't cut while enter a protected area
                    #~ if( i-nBeginIdx > 1 ):
                        #~ a.append( s[nBeginIdx: i-1] )
                    #~ nBeginIdx = i
        else:
            if( s[i] == protectchars[1] ):
                bInProtected = False
                # don't cut when leaving a protected area
                #~ a.append( s[nBeginIdx: i+1] )
                #~ nBeginIdx = i+1
    if( i - nBeginIdx > 1 ):
        assert(  not bInProtected )
        a.append( s[nBeginIdx: i+1] )
        
    return a
                    
assert_check( splitProtecting( "bonjour les gens", " " ), ["bonjour", "les", "gens"] )
assert_check( splitProtecting( "bonjour (les gens)", " " ), ["bonjour", "(les gens)"] )
assert_check( splitProtecting( "(les gens) sont content", " " ), ["(les gens)", "sont", "content"] )
assert_check( splitProtecting( "bonjour comment ca va (pierrot/maxime)", "/" ), ["bonjour comment ca va (pierrot/maxime)"] )
assert_check( splitProtecting( "bonjour comment ca va (pierrot/maxime) / chabada", "/" ), ["bonjour comment ca va (pierrot/maxime) ", " chabada"] )

def findEndOfEntity( strTxt ):
    """
    take a text and find the end of "logic block"
    Return the index of the end of the block or 0 if no more blocks
    - strTxt: "allo mister" => 5; "(allo mister)" => 12; ""il y a"" => 8
    
    """
    nCountParenthesis = 0 # ()
    nCountBracket = 0 # []
    nCountQuote = 0 # ""
    for i in range(len(strTxt) ):
        if( strTxt[i] == "(" ):
            nCountParenthesis += 1
        elif( strTxt[i] == ")" ):
            nCountParenthesis -= 1            
        elif( strTxt[i] == "[" ):
            nCountBracket += 1
        elif( strTxt[i] == "]" ):
            nCountBracket -= 1            
        elif( strTxt[i] == "\"" and nCountQuote == 0 ):
            nCountQuote += 1
        elif( strTxt[i] == "\"" and nCountQuote == 1 ):
            nCountQuote -= 1
        else:
            if( i > 0 and strTxt[i] == " " and nCountParenthesis == 0 and nCountBracket == 0 and nCountQuote == 0 ):
                return i
    if( nCountParenthesis != 0 ):
        print( "ERR: findEndOfEntity: parenthesis error in %s" % strTxt )
    if( nCountBracket != 0 ):
        print( "ERR: findEndOfEntity: bracket error in %s" % strTxt )
    if( nCountQuote != 0 ):
        print( "ERR: findEndOfEntity: quote error in %s" % strTxt )

    return len(strTxt)
 # findEndOfEntity - end
 
def getGroupListDelimiters():
    strGroupListDelimiters = ['(', '"', "'"]
    return strGroupListDelimiters
    
def generateListFromString( strTxt ):
    """
    take a list: [hi hello "good morning"] => ["hi", "hello", "good morning"]
    """
    strGroupListDelimiters = getGroupListDelimiters()
    retVal = []
    t = strTxt[1:-1]
    while(1):
        idx = findEndOfEntity(t)
        #~ print( "idx: %d" % idx )
        if( idx <= 0 ):
            break
        if( idx == 1 ):
            t = t[idx+1:]
            continue        
        ent = t[:idx]
        while( ent[0] in strGroupListDelimiters ):
            ent = ent[1:-1]
        retVal.append( ent )
        t = t[idx+1:]
    return retVal
#~ print generateListFromString( '[hi hello "good morning"]' )
#~ exit( 1 )

 
def getEntityList( strTxt ):
    """
    get a list of entity: 
        '[hi hello "good morning"]' => [["hi", "hello", "good morning"]]
        '"hello how are you?"' => ["Hello how are you?"]
        'hello how are you?' => ["Hello how are you?"] special case1: NOT WORKING ! today we've got => ["Hello", "how", "are", "you?"]
    """
    strGroupListDelimiters = getGroupListDelimiters()
    
    #~ if( not strTxt[0] in strGroupListDelimiters ): # special case1
        #~ strTxt = '"' + strTxt + '"' # add explicit markers
        
    retVal = []
    t = strTxt[:]
    while(1):
        idx = findEndOfEntity(t)
        #~ print( "idx: %d" % idx )
        if( idx <= 0 ):
            break
        if( idx == 1 ):
            t = t[idx+1:]
            continue        
        ent = t[:idx]
        
        ent = ent.strip(" _")
        
        while( ent[0] in strGroupListDelimiters ):
            ent = ent[1:-1]
        ent = ent.strip(" _")
        while( ent[0] == '[' ):
            ent = generateListFromString(ent)
        if( isinstance( ent, list ) or 0 ):
            retVal.extend(ent)
        else:
            retVal.append( ent )
        t = t[idx+1:]
    return retVal
# getEntityList - end
#~ assert_check( getEntityList( '[hi hello "good morning"]' ), [ ["hi","hello","good morning"] ] )
#~ assert_check( getEntityList( 'hello how are you?' ), ["hello", "how", "are", "you?"] )
#~ assert_check( getEntityList( '"hello how are you?"' ), ['hello how are you?'] )
#~ assert_check( getEntityList( '([hello how are you?])' ), ['hello how are you?'] )
#~ assert_check( getEntityList( '_([hello how are you?])' ), ['hello how are you?'] )
#~ assert_check( getEntityList( '(_[hello how are you?])' ), ['hello how are you?'] )
#~ assert_check( getEntityList( '(hello man) how are you?' ), ['hello how are you?'] ) # not what ALDialog does
#~ exit(1)

def stringOrArraytoText( sa ):
    """
    convert a string or an array to a text, to simplify user reading
    """
    if( isinstance( sa, list ) ):
        if( len(sa) == 1 ):
            return str(sa[0])
        return str(sa)
    return "'" + sa + "'"
# stringOrArraytoText - end    
    
class DialogTree:
    """
    a tree, in which each node can have two values (question and answer) and a subtree
    """
    def __init__( self, question, answer = "", childrens = [] ):
        self.question = question
        self.answer = answer
        self.childrens = childrens[:] # childrens are list of DialogTree
        self.answerShuffle = [] # when possible answer are possible, shuffle thru them
        self.bEndDialog = False # means this could be the end of the current dialog
        
    def __str__(self):
        return self.toText()
        
    def toText( self, nLevel = 0 ):
        strOut = ""
        strOut += "  " * nLevel + "Q: " + stringOrArraytoText(self.question) + ", A: " + stringOrArraytoText(self.answer)+ "\n"
        for child in self.childrens:
            strOut += "  " * nLevel + child.toText(nLevel+1)
        return strOut
        
    def getFirstLevelLeafWords( self ):
        r = []
        for c in self.childrens:
            r.append(c.question)
        return r
        
    def getFirstLevelLeafs( self ):
        return self.childrens
# class DialogTree - end
        
def DialogTreeTest():
    tt = DialogTree("how are you?", ["fine", "badly"] )
    tt = DialogTree( "Hello", "hello human", [tt] )
    root = DialogTree( "root", "", [tt] )
    root.childrens.append( DialogTree("What time is it", "15h40" ) )
    print root
    print root.getFirstLevelLeafWords()
# DialogTreeTest - end    
#~ DialogTreeTest()
#~ exit(1)

def generateFactorisation( s ):
    """
    find factorisation and factorise them
    "tu pourrais me donner (la date/l'heure) stp" => ["tu pourrais me donner la date stp", "tu pourrais me donner l'heure stp" ]
    "coucou" => ["coucou"]
    NB: return an array, even if only one element in the list
    """
    print( "DBG: generateFactorisation: in: s: %s" % str(s) )
    seg = [] # segment of sentences in an array of text and array
    nCptParenthesis = 0
    nIdxBegin = 0
    aIdxChoicesInSeg = [] # index of each choice
    for i in range(len(s)):
        if( s[i] == '(' ):
            nCptParenthesis += 1
            assert( nCptParenthesis < 2 ) # can't have enclosed parenthesis
            seg.append( s[nIdxBegin:i] )
            nIdxBegin = i+1
        elif( s[i] == ')' ):
            nCptParenthesis -= 1
            if( nCptParenthesis == 0 ):
                seg.append( s[nIdxBegin:i].split('/') )
                nIdxBegin = i+1
                aIdxChoicesInSeg.append( len(seg) - 1 )
    
    if( i - nIdxBegin > 1 ):
        seg.append( s[nIdxBegin:i+1] )    
        
    print( "DBG: generateFactorisation: segment: %s" % str(seg) )
    
    if( len(aIdxChoicesInSeg) < 1 ):
        return [s]
    
    # generate stuffs: generate all  possibilities
    aIdxValue = [0]*len(aIdxChoicesInSeg)
    out = []
    while 1:
        s = ""
        print( "aIdxValue: %s" % aIdxValue )
        idxChoice = 0
        for i in range(len(seg)):
            # for each segment
            print ("%d:%d:%s:%s" % (idxChoice,i,aIdxChoicesInSeg,seg) )            
            if( i not in aIdxChoicesInSeg ):
                s += seg[i]
            else:
                s += seg[i][aIdxValue[idxChoice]]
                idxChoice += 1
        out.append(s)
        
        # inc choice in aIdxValue (like counting)
        i = 0
        while( i < len( aIdxChoicesInSeg ) ):
            print( "%d/%d" % (i, idxChoice ) )
            aIdxValue[i] += 1
            if( aIdxValue[i] < len(seg[aIdxChoicesInSeg[i]]) ):
                break
            aIdxValue[i] = 0
            i += 1 # will increment next idxValue
        if( i == len( aIdxChoicesInSeg ) ):
            break # all finished
    print( "DBG: generateFactorisation: out: %s" % str(out) )
    return out
    
# generateFactorisation - end    
assert_check( generateFactorisation( "tu pourrais me donner (la date/l'heure) stp" ), ["tu pourrais me donner la date stp","tu pourrais me donner l'heure stp"] )
assert_check( generateFactorisation( "quelle heure est il (stp/)" ), ["quelle heure est il stp", "quelle heure est il "] )
assert_check( generateFactorisation( "coucou" ), ["coucou"] )
assert_check( generateFactorisation( "(coucou)" ), ["coucou"] )
assert_check( generateFactorisation( "un BBBB(coucou/caca)EEEE" ), ['un BBBBcoucouEEEE', 'un BBBBcacaEEEE'] )
assert_check( generateFactorisation( "un (coucou/caca) ainsi qu'un (toto/titi)" ), ["un coucou ainsi qu'un toto", "un caca ainsi qu'un toto", "un coucou ainsi qu'un titi", "un caca ainsi qu'un titi"] )


def analyseLineProtolab( txt ):
    """
    take a line: "label: questions >> answers ^options" and return a list of ["label", q, a, options ] 
    with questions and answers a string
    and options a list of strings
    q and a: a list of possibles choice (an array, even if only one element in the list)
    """
    retVal = []
    idxEndLabel = txt.find(":")
    retVal.append( stripObject(txt[:idxEndLabel]) )
    #~ print("idxEndLabel: %s" % idxEndLabel )
    t = txt[idxEndLabel+1:]
    el = t.split( ">>" )
    # options handling
    strOption = None
    if "^" in el[-1]:
        splitted = el[-1].split( "^" )
        el[-1] = splitted[0]
        strOption = splitted[1].split(",")
        
    if( 1 ):
        # changing _(...) in BBBB(...)EEEE
        
        #~ print( "DIALOG BBBBEEEE begin: %s" % el[0] )
        
        bChanged = True
        while bChanged:
            bChanged = False
            print( "%s" % el[0] )
            for i in range(len(el[0] )):
                if el[0][i] == '_' and el[0][i+1] == '(':
                    #~ print( "CCCCCCCCCCCCCCCCC" )
                    out = el[0][:i] + "BBBB"
                    j = i
                    while j < len(el[0]):
                        if el[0][j] == ')':
                            out += el[0][i+1:j] + ")EEEE" + el[0][j+1:]
                            el[0] = out
                            bChanged = True                            
                            break
                        j += 1
                    if j == len(el[0]):
                        assert( "missing ')'" == 0 )
                    break
        #~ print( "DIALOG BBBBEEEE after: %s" % el[0] )
        
    print( "el: %s" % el )
    for e in el:
        e = splitProtecting( e, "/", "()")

        print( "e1: %s" % e )
        for i in range( len(e) ):
                l = generateFactorisation(e[i])
                if( isinstance( l, list ) and len(l) > 1 ):
                    e[i] = l
                else:
                    e[i] = l[0]
        e = flattenList(e)
        e = stripObject(e)
        e = stripDecoratorFromObject(e)
        e = stripDoubleQuoteFromObject(e) # at the extreme end, we remove the double quote (then we must should stop to strip for ) or anything...
        retVal.append(e)
    
    # options handling
    if( strOption != None ):
        retVal.append(strOption)
        
    print( "analyseLineProtolab: '%s' => %s" % (txt, retVal) )
                
    return retVal
# analyseLineProtolab - end
assert_check( analyseLineProtolab( ' concept: greetings >> hi/hello/"good morning"' ), [ "concept", ["greetings"], ["hi","hello","good morning" ] ] )
assert_check( analyseLineProtolab( 'u5: coucou>>caca' ), [ "u5", ["coucou"], ["caca"] ] )
assert_check( analyseLineProtolab( 'u5: bye>>salut ^eod' ), [ "u5", ["bye"], ["salut"], ["eod"] ] )
assert_check( analyseLineProtolab( 'u5: bye>>salut ^eod,futurestuffs' ), [ "u5", ["bye"], ["salut"], ["eod","futurestuffs"] ] )
assert_check( analyseLineProtolab( 'u5: un (coucou/caca)>>(pipi)' ), [ "u5", ["un coucou", "un caca"], ["pipi" ] ] )
assert_check( analyseLineProtolab( 'u5: un (coucou/caca)>>(pipi/popo)' ), [ "u5", ["un coucou", "un caca"], ["pipi", "popo" ] ] )
assert_check( analyseLineProtolab( 'u5: un (coucou/caca) / cradouillo >>(pipi/popo)' ), [ "u5", ["un coucou", "un caca", "cradouillo"], ["pipi", "popo" ] ] )
assert_check( analyseLineProtolab( 'u5: un (coucou/caca) / cradouillo / jean-(pierre/paul)>>"je ne comprend pas!"' ), [ "u5", ["un coucou", "un caca" ,"cradouillo", 'jean-pierre', 'jean-paul'], ["je ne comprend pas!" ] ] )
assert_check( analyseLineProtolab( 'u5: (coucou)>>(pipi)' ), [ "u5", ["coucou"], ["pipi" ] ] )
#assert_check( analyseLineProtolab( 'u2: * >> "ok (j\'ai rien compris)"' ), [ "u2", ["*"], ["ok (j'ai rien compris)" ] ] )
assert_check( analyseLineProtolab( 'u2: * >> "ok (j\'ai rien compris)"' ), [ "u2", ["*"], ["ok j'ai rien compris" ] ] ) # current state
assert_check( analyseLineProtolab( "u5: avion/bateau >> moi aussi j'aime les engins" ), [ "u5", ["avion","bateau"], ["moi aussi j'aime les engins" ] ] )
assert_check( analyseLineProtolab( "u: tu pourrais me donner (la date/l'heure) stp / quelle jour on est?>> 8h40" ), [ "u", ["tu pourrais me donner la date stp","tu pourrais me donner l'heure stp","quelle jour on est?"], ["8h40" ] ] )


class DialogManager:
    def __init__(self):
        self.mem = None
        self.reset()
        
    def reset( self ):
        self.rApproximateMatchingThreshold = 0.7                
        self.dialogRoot = DialogTree( "root" )
        self.concepts = dict()
        self.listProposal = [] # a list of leaf good to activate at proactive startup (leaf that robot can use to introduce a dialog) [U: instead of u:]
        self.listBusy = []
        self.listBye = []
        
        #
        # all following are state variables: don't duplicate them on copy
        #
        self.activeLeaf = None
        self.nState = False # dialog state: 0: not really started, 1: started (user has speak to robot...), 2: cold/end state (eg: bye received)
        
        self.localVar = dict()
        # for resume feature
        self.strLastSaid = None # the robot has spoke
        self.strLastHeard = None # then the human speak
        self.strJustSaid = None # then we send a text to tts (heard or not ?)
        
    def __str__( self ):
        strOut = ""
        strOut += "concepts: %s\n" % self.concepts
        strOut += "dialogRoot: %s\n" % self.dialogRoot
        strOut += "listProposal: %s\n" % str(self.listProposal)   
        strOut += "listBusy: %s\n" % str(self.listBusy)
        strOut += "listBye: %s\n" % str(self.listBye)        
        strOut += "activeLeaf: %s\n" % str(self.activeLeaf)
        strOut += "getPossibleWords: %s\n" % str(self.getPossibleWords())        
        return strOut
        
    def duplicate( self, rhs ):
        """
        duplicate another DialogManager, but with cleared dialog state
        """
        self.reset()
        self.mem = rhs.mem
        self.rApproximateMatchingThreshold = rhs.rApproximateMatchingThreshold
        self.dialogRoot = rhs.dialogRoot # weak copy, but won't be modified
        self.concepts = arraytools.dup(rhs.concepts) # deep copy        
        self.listProposal = rhs.listProposal # idem
        self.listBusy = rhs.listBusy # idem
        self.listBye = rhs.listBye # idem
        # we don't copy activeLeaf nor nState

    def isJustInitalised(self):
        return self.nState == 0
        
    def isStarted(self):
        return self.nState == 1
        
    def isFinished(self):
        return self.nState == 2
        
    def setApproximateMatchingThreshold( self, rNewValue ):
        self.rApproximateMatchingThreshold = rNewValue
                
        
    def connectToALMemory( self ):
        import naoqitools
        self.mem =  naoqitools.myGetProxy( "ALMemory" )
        print( "WRN: abcdk.dialog.connectToALMemory: cannot connect to ALMemory" )
        
    
    def analyseLine( self, txt ):
        """
        Analyse a line "label: (yes) [yes ok]" and return a list of ["label", "yes", ["yes", "ok"]]
        special case 1: "label: yes ok sir" => ["label", "yes" "ok sir"]
        """
        txt = txt.strip(" _")
        retVal = []
        idxEndLabel = txt.find(":")
        retVal.append( txt[:idxEndLabel] )
        #~ print("idxEndLabel: %s" % idxEndLabel )
        t = txt[idxEndLabel+1:]
        el = getEntityList( t )
        print( "el: %s" % el )
        for e in el:
            e = stripObject(e)
            while( e[0] in ["[", "(" ] ):
                e = getEntityList(e) # explode every entity in sub entity
            e = stripObject(e)
            
            retVal.append(e)
        
        if( len(retVal) > 3 ): # special case 1
            print( "special case: retVal: %s !!!" % retVal)
            retVal[2] = " " . join( retVal[2:] )
            retVal = retVal[:3]
            
        print( "analyseLine: '%s' => %s" % (txt, retVal) )
                    
        return retVal
    # analyseLine - end
        
    def expandConcept( self, strConcept ):
        """
        take a concept and return a list of possible words for this concept
        """
        try:
            return self.concepts[strConcept]
        except KeyError, err:
            print( "WRN: abcdk.dialog.expandConcept: can't find concept '%s', (err:%s)" % (strConcept,str(err)) )
        assert(0)
        
    def loadFromTopicFile(self, strFilename ):
        """
        load a dialog from an Aldebaran topic file
        """
        self.reset()
        file = open( strFilename, "rt" )
        buf = file.read()
        file.close()
        
        lines = buf.split("\n")
        for line in lines[2:]:
            if( len(line) < 2 ):
                continue            
            if( line[0] == "#" ):
                continue
            print( "\n\nDBG: input line: '%s'" % line )
            tag, q, a = self.analyseLine( line )
            idx = line.find("concept:")
            if( tag == "concept" ):
                print( "new concept: %s => %s"% (q,a) )
                self.concepts[q] = a
            else:
                if( tag == "u" ):
                    nLevel = 0
                elif( tag[0] == "u" ):
                    nLevel = ord(tag[1]) - ord('0')

                leaf = self.dialogRoot
                for i in range(nLevel):
                    leaf = leaf.childrens[-1]
                #~ print( "dialogRoot: %s" % self.dialogRoot )
                #~ print( "leaf to update: %s" % leaf )
                if( q[0] == '~' ):
                    q = self.expandConcept(q[1:])
                new_leaf = DialogTree( q, a )
                #~ print( "new_leaf: %s" % leaf )
                leaf.childrens.append(new_leaf)
                #~ print( "tree end dialogRoot: %s" % self.dialogRoot )
        # for lines - end
        print( "imported dialog:\n%s" % self )
    # loadFromTopicFile - end
    
    def loadFromProtolabFile(self, strFilename ):
        """
        load a dialog from a Protolab topic file
        """
        self.reset()
        file = open( strFilename, "rt" )
        buf = file.read()
        buf = buf.replace( "\r", "" ) # dos2unix
        file.close()
        
        lines = buf.split("\n")
        for line in lines[2:]:
            line = line.strip()
            if( len(line) < 2 ):
                continue            
            if( line[0] == "#" ):
                continue
            print( "\n\nDBG: input line: '%s'" % line )
            retVal = analyseLineProtolab( line )
            if( len(retVal) == 3 ):
                retVal.append(None)
            tag, q, a, options = retVal
            idx = line.find("concept:")
            if( tag == "concept" ):
                assert( len(q) == 1 ) # or else concept error !
                q = q[0]
                print( "new concept: %s => %s"% (q,a) )
                self.concepts[q] = a
            else:
                bProposal = False
                if( tag.lower() == "u" ):
                    nLevel = 0
                    if( tag.upper() == tag ): # == "U" == tag
                        bProposal = True
                elif( tag[0].lower() == "u" ):
                    nLevel = ord(tag[1]) - ord('0')
                    

                leaf = self.dialogRoot
                for i in range(nLevel):
                    leaf = leaf.childrens[-1]
                #~ print( "dialogRoot: %s" % self.dialogRoot )
                #~ print( "leaf to update: %s" % leaf )
                for i in range(len(q)):
                    if( q[i][0] == '~' ):
                        print( "expanding concept of '%s'" % q[i][1:] )
                        q[i] = self.expandConcept(q[i][1:])
                q = flattenList(q)
                new_leaf = DialogTree( q, a )
                #~ print( "new_leaf: %s" % leaf )
                if( options != None and "eod" in options ):
                    new_leaf.bEndDialog = True
                leaf.childrens.append(new_leaf)
                #~ print( "tree end dialogRoot: %s" % self.dialogRoot )
                if bProposal:
                    self.listProposal.append( new_leaf )
                if( options != None and "busy" in options ):
                    self.listBusy.append( new_leaf )
                if( options != None and "bye" in options ):
                    self.listBye.append( new_leaf )                    
        # for lines - end
        print( "imported dialog:\n%s" % self )
    # loadFromProtolabFile - end    
    
    def activateLeaf(self, leaf):
        self.activeLeaf = leaf
        print( "INF: new active leaf:\n%s" % str(leaf) )
        print( "INF: new possible words: %s" % str(self.getPossibleWords()) )
        
    def getPossibleLeafs(self):
        """
        return the list of all possible leafs
        """
        listActive = [] # we want to point to real object (not copy them!)
        listActive.extend( self.dialogRoot.getFirstLevelLeafs() )
        if( self.activeLeaf != None ):
            listActive.extend(self.activeLeaf.getFirstLevelLeafs() )
        return listActive

    def getPossibleWords(self):
        """
        return the list of all possible words
        """
        out = []
        listL = self.getPossibleLeafs()
        for l in listL:
            if( isinstance( l.question, list ) ):
                out.extend( l.question )
            else:
                out.append( l.question )
        return out
        
    def storeLocalMatch( self, s ):
        """
        store a sentence and sub sentence.
        - s: "hello"  => store 0 => "hello"
                or "hello BBBBmanEEE" => store 0 => "hello man" and 1 => man
        """
        splited = s.split( "BBBB" )
        for sub in splited[1:]:
            sub = sub.split("EEEE")[0]
            self.storeLocal( sub )
        sWithoutMatch = s.replace( "BBBB", "" ).replace( "EEEE", "" )            
        self.storeLocal( sWithoutMatch )

    def storeLocal( self, s ):
        self.localVar[str(self.nNbrVariableInHumanSentence+1)] = s # store this variable
        self.nNbrVariableInHumanSentence += 1
        print( "DBG: storeLocal: %d => '%s'" % (self.nNbrVariableInHumanSentence,s )  )
        
    def matchText( self, s1, s2 ):
        """
        s2 could contain wildcards!
        return a confidence (the bigger, the better)
        """
        if( 0 ):
            # direct matching
            if( s1.lower() == s2.lower() ):
                return 1.
            return 0.
        if( s2 == "*" ):
            self.storeLocal( s1 ) # BUG: we store even, if it's not the best !!!!!
            return self.rApproximateMatchingThreshold # everything match * but not exactly
            
        bEndWithStar = False
        if( s2[-1] == "*" ): # handle only finishing by '*' TODO: handle all case
            bEndWithStar = True
            s2 = s2[:-1]
    
        
        bApproximativeSearch = 1
        metaQuery = metaphone.dm(unicode( s1 ) );
        if( len(metaQuery[0]) < 1 ):
            return 0.
        metaK = metaphone.dm(unicode(s2));
        print( "   DBG: %s (%s) comp to %s (%s)" % (metaQuery,s1, metaK, s2) );
        if( metaK == metaQuery ):
            print( "   INF: found in metaphone: %s ~= %s" % ( s1, s2 ) );
            return 1.
        if( bEndWithStar ):
            print( "check star: %s and %s" %(metaQuery[:len(metaK)],metaK) )
            if( metaQuery[0][:len(metaK[0])] == metaK[0] ):
                subSearch = metaphone.fromMetaphoneAtEnd( metaQuery[0][len(metaK[0]):], s1 )
                self.storeLocal( subSearch ) # BUG: we store even, if it's not the best !!!!!
                print( "   INF: found in metaphone with star: %s ~= %s" % ( s1, s2 ) );
                return 0.95                
        if( bApproximativeSearch ):
            # compute distance
            rMidLen = ( len(metaK[0]) + len( metaQuery[0] ) ) / 2;
            rDist = stringtools.levenshtein( metaK[0], metaQuery[0] ) / float(rMidLen);
            rConfidence = 0.9 - rDist # TODO: why ('AL', 'ALF') (yellow) comp to ('HL', '') (hello) give a distance of 0 ?
            print( "DBG: rMidLen: %s, rDist: %s, rConfidence: %s" % (rMidLen, rDist,rConfidence) )
            return rConfidence
        return 0.
    # matchText - end
        
    def getVariableValue( self, s ):
        """
        get the value of a variable
        * look first in the dialog variable ($1, ...)
        * then in the ALMemory        
        - s: the name of the variable
        return the string contained in the variable
        """
        try:
            return self.localVar[s]
        except KeyError, err:
            print( "DBG: key not found, err: %s" % err )
            try:
                #~ print( "DBG: is mem not none?" )
                if self.mem != None:
                    #~ print( "DBG: mem not none!" )
                    return self.mem.getData( s )
            except BaseException, err:
                print( "ERR: getVariableValue: err: %s" % str(err) )
        print( "WRN: getVariableValue: don't know how to evaluate: '%s'" % str(s) )
        return s
        
    def assignValueToVariable( self, strVarName, value ):
        value = self.evaluateSentence(value)
        print( "INF: assigning to variable '%s' value '%s'" % (strVarName, value) )
        if( self.mem != None ):
            self.mem.raiseMicroEvent( strVarName, value )
        else:
            print( "WRN: abcdk.dialog.assignValueToVariable: cannot raise event nammed '%s', as self.mem is None !!!"  % strVarName )
        return ""
    
    def __evaluateVariable( self, strVarName ):        
        """
        evaluate a variable or an assignation
        """
        #~ print( "DBG: __evaluateVariable: found a variable (or an assignation): '%s'" % strVarName )
        if( '=' not in strVarName ):
            return self.getVariableValue(strVarName)
        # it's just a demand to send a variable in the memory
        splitted = strVarName.split('=')
        return self.assignValueToVariable(splitted[0], splitted[1] )
        
        
    def evaluateSentence( self, s ):
        """
        receive a string
        look for $variable_name in a string and replace them by variable_value.
        look also for variable assignation in the string
        """
        print( "DBG: evaluateSentence: '%s'..." % (s) )
        out = ""
        bInVariableName = False
        nBeginIdx = 0
        for i in range(len(s)):
            if( not bInVariableName ):
                if( s[i] == "$" ):
                    bInVariableName = True
                    if( i-nBeginIdx > 0 ):
                        out +=  s[nBeginIdx: i]
                    nBeginIdx = i+1
            else:
                if( s[i] in [" ", ",", ".", ":", ";","?","!"] ): # not =
                    # end of variable
                    bInVariableName = False
                    strVarName = s[nBeginIdx: i]
                    out += self.__evaluateVariable( strVarName )
                    nBeginIdx = i # keep the last char
        if( i - nBeginIdx >= 0 ):
            if bInVariableName:
                out += str( self.__evaluateVariable( s[nBeginIdx: i+1] ) )
            else:
                out += str( s[nBeginIdx: i+1] )
            
        out = out.strip() # some value could have been evaluate and disappear, leaving orphans spaces => strip
        print( "DBG: evaluateSentence: ending, results: '%s' => '%s'" % (s, out) )
        return out
    # evaluate - end
        
        
        
    def getTextToSay( self, leaf ):
        """
        receive a list of possible thing to do, evaluate and pick one
        return the string to say
        - leaf:  a leaf containg the answer to pick one from # list of strings to say, eg: ["hello", "hi", "hello $gender"]
        """
        s = self.evaluateSentence(leaf.answer[0])
        #~ for i in range(30): # prevent infinite loop # but why looping ?
            #~ s = self.evaluateSentence(leaf.answer[0])
            #~ if( s != "" ):
                #~ return s
        return s
        #~ return  "Can't say how to tell: " + leaf.answer[0]
        
        
    def _computeTextForLeaf( self, leaf ):
        """
        this leaf has been choosen, get text to say related to it
        """
        strTextToSay = self.getTextToSay(leaf)
        print( "INF: ***** text to say: '%s'" % strTextToSay )
        self.activateLeaf( leaf )
        print( "localVal: %s" % self.localVar )
        self.storeSaidText( strTextToSay )
        if leaf.bEndDialog:
            self.nState = 2
        return strTextToSay        
        
    def receiveText( self, strText ):
        """
        - strText: a text or a pair: ["txt", confidence] or an array of pair  [ ["txt1", conf1], ["txt2", conf2], ... ]
        return a text to say or None if nothing found
        """
        print( "*" * 10 )
        print( "INF: receiveText: receiving '%s'" % str(strText) )
        self.nState = 1
        
        if isinstance( strText, list ):
            if isinstance( strText[0], list ):
                # list of pair
                strText = strText[0] # todo: choose the right one
            strText = strText[0] # todo: check confidence
        
        print( "INF: receiveText: using txt '%s'" % strText )
        
        self.strLastHeard = strText
        
        self.nNbrVariableInHumanSentence = 0
        listL = self.getPossibleLeafs()
        rMax = 0.
        bestL = None # best leaf
        bestW = "ERR: not found"  # best word
        for l in listL:
            listWordsForThisLeaf = l.question
            if( not isinstance( listWordsForThisLeaf, list ) ):
                listWordsForThisLeaf = [listWordsForThisLeaf]
            for w in listWordsForThisLeaf:
                wWithoutTag = w.replace("BBBB", "").replace("EEEE","")
                rValue = self.matchText( strText,  wWithoutTag ) # remove markers
                if( rValue > rMax ):
                    print( "DBG: new best: %s" % rValue )
                    rMax = rValue
                    bestL = l
                    bestW = w
        if( rMax  >= self.rApproximateMatchingThreshold ):                
                print( "INF: receiveText: '%s' match with '%s' (conf: %5.3f)" % (strText, bestL.question, rMax) )                
                self.storeLocalMatch( bestW )
                return self._computeTextForLeaf( bestL )
        print( "INF: no match!" )
        self.storeSaidText( None )
        return None
    # receiveText - end
        
    def setLocalVar( self, strVarName, value ):
        self.localVar[strVarName] = value
        
    def storeSaidText( self, strTextToSay ):
        """
        robot memorise what he said to be able to repeat it later
        """
        self.strLastSaid = self.strJustSaid
        self.strJustSaid = strTextToSay
        
    def getProposalText( self ):
        """
        find something to say to user as startup
        """
        if( len( self.listProposal ) == 0 ):
            return None
        nChoosen = numeric.randomDifferent( 0, len( self.listProposal ) - 1 )
        return self._computeTextForLeaf( self.listProposal[nChoosen] )

    def getBusyText( self ):
        """
        find something to say to user as busy
        """
        if( len( self.listBusy ) == 0 ):
            return None
        nChoosen = numeric.randomDifferent( 0, len( self.listBusy ) - 1 )
        return self._computeTextForLeaf( self.listBusy[nChoosen] )

    def getByeText( self ):
        """
        find something to say to user as busy
        """
        if( len( self.listBye ) == 0 ):
            return None
        nChoosen = numeric.randomDifferent( 0, len( self.listBye ) - 1 )
        return self._computeTextForLeaf( self.listBye[nChoosen] )

        
    def getResumeText( self, nUseLang = -1 ):
        """
        dialog has been interrupted, resume it with an explicit sentence.
        """
        import translate
        strOut = ""
        if( self.strLastSaid != None ):
            strTxt = translate.chooseFromDict ( { "en": "I said: '%s'", "fr": "Je disais: '%s'"}, nUseLang = nUseLang )
            strOut +=  strTxt % getLastSentence(self.strLastSaid)
        if( self.strLastHeard != None and self.strLastHeard != "None" ): # "None": weird bug           
            if( strOut != "" ):
                strTxt = translate.chooseFromDict ( { "en": "you answer: '%s'", "fr": "vous avez répondu: '%s'"}, nUseLang = nUseLang )                            
                strOut += translate.chooseFromDict ( { "en": ", then ", "fr": ", et "}, nUseLang = nUseLang )
                strOut +=  strTxt % self.strLastHeard                
            else:
                strTxt = translate.chooseFromDict ( { "en": "you said: '%s'", "fr": "vous avez dit: '%s'"}, nUseLang = nUseLang )
                strOut +=  strTxt % getLastSentence(self.strLastHeard)
            
        if( self.strJustSaid != None ):            
            if( strOut != "" ):
                strOut += translate.chooseFromDict ( { "en": ", and ", "fr": ", et "}, nUseLang = nUseLang )
            strTxt = translate.chooseFromDict ( { "en": "I was just saying '%s'", "fr": "J'étais en train de dire: '%s'"}, nUseLang = nUseLang )            
            strOut +=  strTxt % self.strJustSaid
            
        if( strOut == "" ):
            strOut = self.getProposalText()
        return strOut
        
        
    def innerTest( self ):
        # quick test that should require no external data
        self.setLocalVar( "gender", "sir" )
        assert_check( self.evaluateSentence( "hello $gender" ), "hello sir" )
        assert_check( self.evaluateSentence( "hello $gender glad to see you!" ), "hello sir glad to see you!" )
        assert_check( self.evaluateSentence( "hello $gender, glad to see you!" ), "hello sir, glad to see you!" )
        assert_check( self.evaluateSentence( "hello $gender." ), "hello sir." )
        assert_check( self.evaluateSentence( "$new_value=$gender" ), "" )
        assert_check( analyseLineProtolab( 'u: ("is the demo running?") >> "the demo is running."'), ['u', ['is the demo running?'], ['the demo is running.']] )
        print( "\nINF: GOOD: Dialog.innerTest SUCCESS !!!\n\n" )
    # innerTest - end

# class DialogManager - end

class DialogManagerMultiUser:
    """
    manage multi user at the same time.
    handle switch of user decisions and resuming
    """
    def __init__( self ):
        self.dialogPerUser = dict() # for each user: str(id) => current dialog
        self.defaultDialogManager = None
        self.setCurrentUserToNone()
        
    def setCurrentUserToNone( self ):
        self.currentUserID = None
        
        
    def setDefaultDialogManager( self, dialogManager ):
        self.defaultDialogManager = DialogManager()
        self.defaultDialogManager.duplicate( dialogManager )
        
    def getCurrentUser( self ):
        return self.currentUserID
        
    def _createNewUser( self, id, dialogManager = None ):
        """
        A new user arrive, create a new dialog for him
        - dialogManager: a dialogManager to associate to this user, if None default one will be used
        """
        #~ print( "INF: abcdk.DialogManagerMultiUser._createNewUser: creating a dialog instance for '%s'" % id )
        self.dialogPerUser[str(id)] = DialogManager()        
        
        if( dialogManager == None ):
            dialogManager = self.defaultDialogManager
            
        self.dialogPerUser[str(id)].duplicate( dialogManager )
    # _createNewUser - end

    def welcomeNewUser( self, id, dialogManager = None ):
        """
        A new user arrive, create a new dialog for him
        - dialogManager: a dialogManager to associate to this user, if None default one will be used
        return a text to say to him
        """
        print( "INF: abcdk.DialogManagerMultiUser.welcomeNewUser: creating a dialog instance for '%s'" % id )
        self._createNewUser( id, dialogManager )
        self.currentUserID = str(id)
        return self.dialogPerUser[str(id)].getProposalText()
    # welcomeNewUser - end
    
    def switchToUser( self, id, dialogManager = None ):
        """
        We were speaking to someone, we want to switch to another user.
        - id: the id of the user, if -1 or None: there won't be any active user
        - dialogManager: a dialogManager to associate to this user, if None default one will be used        
        - bBusy: when set: harshly tell new user the robot isn't ready
        return [txt1, txt2]: txt1: text to say to current user, txt2: text to say to new user
        """
        print( "INF: abcdk.DialogManagerMultiUser.switchToUser: switch from '%s' to '%s'" % ( self.currentUserID, id ) )
        if id == -1 or id == None:
            strByeText = ""
            if self.currentUserID != None:
                strByeText = self.dialogPerUser[str(self.currentUserID)].getByeText()
                self.setCurrentUserToNone()
            return strByeText, ""
            
        if self.currentUserID == str(id):
            print( "WRN: abcdk.DialogManagerMultiUser.switchToUser: try to switch to same user than current one(%s)" % str(id) )
            return "",""
            
        if( str(id) not in self.dialogPerUser.keys() ):
            self._createNewUser( id, dialogManager )
            
        txt1 = ""
        if self.currentUserID != None and self.dialogPerUser[self.currentUserID].isStarted():
            txt1 = "scuse me"
            txt2 = self.dialogPerUser[str(id)].getBusyText()
        else:
            txt2 = self.dialogPerUser[str(id)].getResumeText()
        self.currentUserID = str(id)
        print( "INF: abcdk.DialogManagerMultiUser.switchToUser: returning: '%s', '%s'" % ( txt1, txt2 ) )
        return txt1, txt2
    # addNewUser - end
    
    def receiveText( self, txt ):
        if( self.currentUserID == None ):
            print( "WRN: abcdk.DialogManagerMultiUser.receiveText: no user selected, using default dialog!" )
            dia = self.defaultDialogManager
        else:
            dia = self.dialogPerUser[str(self.currentUserID)]
        return dia.receiveText( txt )
        
    def renameUserID( self, nPrevID, nNewID ):
        # TODO: renaming a key in a dict ?
        print( "INF: abcdk.DialogManagerMultiUser.renameUserID: changing name of %s by %s" % (nPrevID, nNewID) )
        self.dialogPerUser[str(nNewID)] = self.dialogPerUser[str(nPrevID)]
        del self.dialogPerUser[str(nPrevID)]
        if self.currentUserID == str(nPrevID):
            self.currentUserID = str(nNewID)
            
    def isDefaultFinished( self ):
        """
        is the current dialog finished ? if no current dialog, will return False
        """
        try:
            return self.dialogPerUser[str(self.currentUserID)].isFinished()
        except: pass
        return False
        
    def isFinished( self, nUserID ):
        """
        is the dialog of some user finished ?
        """
        try:
            return self.dialogPerUser[str(nUserID)].isFinished()
        except: pass
        return None
        
        
    def innerTest( self ):
        if( self.defaultDialogManager == None ):
            return
        self.defaultDialogManager.innerTest()
        
    
# class DialogManagerMultiUser - end
dialogManagerMultiUser = DialogManagerMultiUser()

def autoTest():    
    dia = DialogManager()
    dia.innerTest()
    if 1: 
        dia.loadFromProtolabFile( "../../../datas/autotest/dialog_sample_format_protolab.txt" )
        assert( len(dia.listProposal) == 1 )
        dia.setLocalVar( "gender", "mister" )
        dia.setLocalVar( "sir_or_madam", "sir" )
        assert( dia.concepts["yes"] != [] )
        assert( dia.concepts["no"] != [] )
        assert_check( dia.isStarted(), False )
        assert_check( dia.receiveText( "hello" ),  "hello, how are you sir ?" )
        assert_check( dia.isStarted(), True )
        assert_check( dia.isFinished(), False )
        assert_check( dia.receiveText( "helo" ), "hello, how are you sir ?" )
        assert_check( dia.receiveText( "hi" ), "hello, how are you sir ?" )
        assert_check( dia.receiveText( "bof" ), "oh mince!, pourquoi ca ?" )
        assert_check( dia.receiveText( "wwe" ), "ok j'ai rien compris" )
        assert_check( dia.receiveText( "j'ai tres mal au jambe!" ), None )
        assert_check( dia.receiveText( "tu aimes les flageolet?" ), "tu veux savoir si j'aimes les flageolet ?" )
        assert_check( dia.receiveText( "not at all" ), "ok" )
        assert_check( dia.receiveText( "tu pourrais me donner l'heure?" ), "8h40" )
        assert_check( dia.receiveText( "tu pourrais me donne leur?" ), "8h40" )
        assert_check( dia.getProposalText(), "hello, how are you sir ?" )
        assert_check( dia.receiveText( "bien" ),  "cool" )
        assert_check( dia.isFinished(), False )
        assert_check( dia.receiveText( "bye" ),  "bye, see you later!" )
        assert_check( dia.isFinished(), True )
        
        assert_check( dia.receiveText( "jaguar" ), 'what did you mean, the animal or the car?' )
        assert_check( dia.receiveText( "I want to pee!"), "so, you want to pee?" )
        assert_check( dia.receiveText( "I want to shout!"), "so, you want to shout?" )
        #assert_check( dia.receiveText( "my name is mazel"), "hello mr mazel" ) # need to generalise concept even in sub sentence + store from concept
        
        
    if 1:
        dia.loadFromProtolabFile( "../../../datas/autotest/dialog_format_protolab_ears_demo.txt" )
        assert( len(dia.listProposal) == 1 )
        dia.setLocalVar( "gender", "madam" )
        dia.setLocalVar( "mister_or_madam", "madam" )
        
        assert_check( dia.receiveText( "is the demo running?" ), "the demo is running.")
        assert_check( dia.receiveText( "hello" ), "Hello. My name is NAO, I am happy to welcome you, at the Grand Hotel. \PAU=800\ What can I do for you madam ?")
        assert_check( dia.receiveText( "chicken please" ), "Do you have a reservation madam ?")
        assert_check( dia.receiveText( "yes" ), "What is your name?")
        assert_check( dia.receiveText( "roosevelt" ), "Let me check madam roosevelt. \PAU=1000\ Perfect, I found your reservation. Have a nice stay! bye!" )
        assert_check( dia.receiveText( "do you like apple?" ), "You want to know if I like apple ? I don't know madam, and you?" )
        assert_check( dia.receiveText( "yes" ), "great" )
        assert_check( dia.receiveText( "no" ), None ) # out of context!
        assert_check( dia.receiveText( "Is there a restaurant ?" ), "yes madam . There's some restaurant, just in front of the hotel." )
        assert_check( dia.getResumeText(), "you said: 'Is there a restaurant ?', and I was just saying 'yes madam . There's some restaurant, just in front of the hotel.'" )
        assert_check( dia.getResumeText(nUseLang=1), "vous avez dit: 'Is there a restaurant ?', et J'étais en train de dire: 'yes madam . There's some restaurant, just in front of the hotel.'" )
        assert_check( dia.receiveText( "thanks" ), None )
        assert_check( dia.getResumeText(), "I said: 'There's some restaurant, just in front of the hotel.', then you answer: 'thanks'" )
        dia2 = DialogManager()
        dia2.duplicate(dia)
        assert_check( dia2.receiveText( "chicken please" ), "Do you have a reservation gender ?") # gender and not madam as locals aren't copied
        
    if 1:
        # dialogManagerMulti test
        dmm = DialogManagerMultiUser()
        dmm.setDefaultDialogManager( dia )
        assert_check( dmm.welcomeNewUser( "Alex" ), "Hello. My name is NAO, I am happy to welcome you, at the Grand Hotel. \PAU=800\ What can I do for you gender ?" )        
        assert_check( dmm.getCurrentUser(), "Alex" )
        assert_check( dmm.switchToUser( "Pat" ), ('', 'Hello. My name is NAO, I am happy to welcome you, at the Grand Hotel. \\PAU=800\\ What can I do for you gender ?') )
        assert_check( dmm.receiveText( "thanks" ), None )
        assert_check( dmm.switchToUser( "Jo" ), ('scuse me', "I'm busy, is it really important?") )
        assert_check( dmm.getCurrentUser(), "Jo" )
        assert_check( dmm.renameUserID( "Jo", "Tom" ), None )
        assert_check( dmm.getCurrentUser(), "Tom" )
        assert_check( dmm.receiveText( "No" ), "ok, so please wait your turn." )
        assert_check( dmm.isDefaultFinished(), True )
        assert_check( dmm.isFinished("Tom"), True )
        assert_check( dmm.isFinished("Jo"), None )
        assert_check( dmm.isFinished("Pat"), False )
        assert_check( dmm.switchToUser( -1 ), ( "Good bye gender . And remember that I am here to help you, do not hesitate to ask me.", "" ) )
        assert_check( dmm.switchToUser( -1 ), ("","") )
        assert_check( dmm.switchToUser( "Pat" ), ("","I said: '\\PAU=800\\ What can I do for you gender ?', then you answer: 'thanks'") )
        assert_check( dmm.switchToUser( "Pat" ), ("","") ) # just to track this silly bug of changing to same user
        assert_check( dmm.switchToUser( -1 ), ("Good bye gender . And remember that I am here to help you, do not hesitate to ask me.", "") )
        assert_check( dmm.switchToUser( "New guy with no one just before" ), ("", "Hello. My name is NAO, I am happy to welcome you, at the Grand Hotel. \\PAU=800\\ What can I do for you gender ?") )
        
        
        
    
    if 0:
        dia.loadFromTopicFile( "../../../datas/autotest/dialog_sample_naoqi_format.txt" )
        dia.receiveText( "yellow" )
        dia.receiveText( "hell how" )
        dia.receiveText( "how are you?" )
        assert_check( dia.receiveText( "jaguar" ), False )
        assert_check( dia.receiveText( "the car" ), False )
        dia.receiveText( "yes" )
        dia.receiveText( "yes" )
        dia.receiveText( "yes" )
        print( "new dia stat: %s" % str(dia) )
        
    if 1:
        dia.reset()
        dia.loadFromTopicFile( "../../../datas/autotest/dialog_sample_complex_naoqi_format.txt" )
        print( "dia complex: %s" % str(dia) )
        dia.receiveText( "hi" )
        dia.receiveText( "checkin please" )
        dia.receiveText( "yes" )
        dia.receiveText( "roosevelt" )

    if 1:
        dia.reset()
        dia.loadFromProtolabFile( "../../../datas/autotest/dialog_hopias_main.txt" )
        print( "dia complex: %s" % str(dia) )
        assert_check( dia.receiveText( "est-ce que tu aimes les chevaux ?" ), "Tu veux savoir si j'aime les chevaux ? Je ne sais pas human_name, et toi?" )
        assert_check( dia.receiveText( "j'aime les poireaux" ), "j'ai entendu: j'aime les poireaux" ) # was "" before!
    
if( __name__ == "__main__" ):
    autoTest()
