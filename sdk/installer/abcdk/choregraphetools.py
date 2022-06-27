# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Choregraphe tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Choregraphe tools"""
print( "importing abcdk.choregraphetools" );

import math
import os
import sys
import tarfile
import xml.dom.minidom # for xar parsing

import debug
import naoqitools
import stringtools

def boxGetParentName( strBoxName, nParentLevel = 1 ):
    "analyse box name and get the name of parent - in the future we will juste make a self.getParent().getName()"
    "nParentLevel: level of parentness, 2 => grandfather, ..."
    listBoxName = boxExplodeBoxName( strBoxName );
    for i in range( 0, nParentLevel ):
        listBoxName.pop(); # remove last name
    strParentBoxName = "__".join( listBoxName );
#    print( "%s -> %s" % ( strBoxName, str( strParentBoxName ) ) );
    return strParentBoxName;
# boxGetParentName - end

def boxGetLastName( strBoxName ):
    "analyse box name and get the name of the last box - in the future we will juste make a self.getParent().getName()"
    listBoxName = boxExplodeBoxName( strBoxName );
    return listBoxName.pop(); # remove last name
# boxGetLastName - end

def boxPathNameToBoxName( strBoxName ):
    "transform complete choregraphe name to a boxName ALFrameManager__0xace99400__root__cascadedtemplatewhile_1 => cascadedtemplatewhile"
    lastName = boxGetLastName( strBoxName );
    listUnderScored = lastName.split( "_" );
    listUnderScored.pop();
    lastName = "_".join( listUnderScored );

    return lastName; # remove last name
# boxPathNameToBoxName - end

def boxExplodeBoxName( strBoxName ):
    "analyse box name and return all the path of a box ALFrameManager__0xace99400__root__cascadedtemplatewhile_1 => ['ALFrameManager', '0xace99400', 'root', 'cascadedtemplatewhile_1']"
    listBoxName = strBoxName.split( "__" );
    return listBoxName;
# boxExplodeBoxName - end

global_coloriseBox_ActivateOneBox_allBoxState = []; # will contents [ ["pathboxname", nbrActivation], ...]

def coloriseBox_ActivateOneBox_internal( strPathBoxName, bActivate = True ):
    "add an activation color to a single level box"
    global global_coloriseBox_ActivateOneBox_allBoxState;
    debug( "coloriseBox_ActivateOneBox_internal( '%s', %d )" % ( strPathBoxName, bActivate ) );

    global global_SectionCritique;
    while( global_SectionCritique.testandset() == False ):
        debug( "coloriseBox_ActivateOneBox_internal: locked" );
        time.sleep( 0.05 );

    nIdx = -1;
    for i in range( len( global_coloriseBox_ActivateOneBox_allBoxState ) ):
        if( global_coloriseBox_ActivateOneBox_allBoxState[i][0] == strPathBoxName ):
            nIdx = i;
            break;
    if( nIdx == -1 ):
        # first time
        nIdx = len( global_coloriseBox_ActivateOneBox_allBoxState );
        global_coloriseBox_ActivateOneBox_allBoxState.append( [ strPathBoxName, 0 ] );

    strBoxName = choregrapheBoxPathNameToBoxName( strPathBoxName );
    debug( "coloriseBox_ActivateOneBox_internal: '%s' last => '%s'" % ( strPathBoxName, strBoxName ) );
    if( bActivate ):
        global_coloriseBox_ActivateOneBox_allBoxState[nIdx][1] +=1;
        if( global_coloriseBox_ActivateOneBox_allBoxState[nIdx][1] == 1 ):
            # colorise it!
            controller = naoqitools.myGetProxy( "ALChoregrapheController" );
            try:
                controller.setBoxTitleColor( strBoxName, 0., 0., 1. );
            except BaseException, err:
                debug( "coloriseBox_ActivateOneBox_internal: Exception catched: %s" % err );
    else:
        global_coloriseBox_ActivateOneBox_allBoxState[nIdx][1] -=1;
        if( global_coloriseBox_ActivateOneBox_allBoxState[nIdx][1] == 0 ):
            # reset it!
            controller = naoqitools.myGetProxy( "ALChoregrapheController" );
            try:
                controller.setBoxTitleColor( strBoxName, 0., 0., 0. );
            except BaseException, err:
                debug( "coloriseBox_ActivateOneBox_internal: Exception catched: %s" % err );


    global_SectionCritique.unlock();
# coloriseBox_ActivateOneBox_internal - end

def coloriseBox_Activate( strPathBoxName, bActivate = True ):
    "colorise the title of a box and all its parents, to show it's activity"
    "we will memorise for each box, the number of child activated, so it will show the state of all child"
    try:
        controller = naoqitools.myGetProxy( "ALChoregrapheController" );
    except:
        return; # no controller found...

    strParentName = boxGetParentName( strPathBoxName );
    if( strParentName != "root" ):
        coloriseBox_ActivateOneBox_internal( strParentName, bActivate );

    # activate this level
    coloriseBox_ActivateOneBox_internal( strPathBoxName, bActivate );
# coloriseBox_Activate - end

def coloriseBox_Desactivate( strPathBoxName ):
    return coloriseBox_Activate( strPathBoxName, False );
# coloriseBox_Desactivate - end



def boxGetFrameNumber( strPathBoxName ):
    "Get the frame number of the timeline of a box running in a timeline"
    "return None if the box isn't in a timeline"
    strTimelineName = boxGetParentName( strPathBoxName, 3 );
    try:
        mem = naoqitools.myGetProxy( "ALMemory" );
        nVal = mem.getData( strTimelineName );
        return nVal;
    except BaseException, err:
#        print( "WRN: boxGetFrameNumber: error is: %s" % str( err ) );
        return None;
# boxGetFrameNumber - end

class FrameNumber:
    "Store the frame number of each box of some behaviors"
    def __init__( self ):
        self.animations_FrameNumber = dict(); # will store for each total box name the number of frame in the enclosed box
    
    def reset( self ):
        self.animations_FrameNumber = dict(); 
        
    def resetBox( self, strPathBoxName ):
        "reset the sub tree of one box"
        debug.debug( "INF: choregraphetools.FrameNumber.resetBox( '%s' )" % strPathBoxName );    
        self.animations_FrameNumber[strPathBoxName] = 0;
    # resetBox - end
    
    def increaseParent( self, strPathBoxName ):
        "called from children"
        fm = naoqitools.myGetProxy( "ALFrameManager" );
        nNbrFrame = fm.getMotionLength( strPathBoxName ) * fm.getTimelineFps( strPathBoxName );
        debug.debug( "INF: choregraphetools.FrameNumber.increaseParent( '%s' ), nNbrFrame: %d )" % ( strPathBoxName, nNbrFrame ) );
        strBoxParentName = boxGetParentName( strPathBoxName );
        try:
            self.animations_FrameNumber[strBoxParentName] += nNbrFrame;
        except:
            # not existing => create it
            self.animations_FrameNumber[strBoxParentName] = nNbrFrame;
    # increaseParent - end
    
    def get( self, strPathBoxName ):
        try:
            nNbrFrame = self.animations_FrameNumber[strPathBoxName];
        except:
            nNbrFrame = 0;
        debug.debug( "INF: choregraphetools.FrameNumber.get( '%s' ): %d" % ( strPathBoxName, nNbrFrame ) );
        return nNbrFrame;
    # get - end
    
# class FrameNumber - end

frameNumber = FrameNumber(); "the singleton to access FrameNumber class"

#~ frameNumber.resetBox( "toto" );
#~ frameNumber.increaseParent( "toto__tutu" );
#~ print( "fng: %d" + frameNumber.get( "toto" ) );


def generateWebInterface( someBox ):
    "Generate the web interface from a box, using its current parameter"
    #~ for param in someBox.getParametersList():
        #~ print( "param: " + str( param ) );
        #~ print debug.dump( someBox );
        #~ # can't work: no params properties :
    
# generateWebInterface - end


def generateWebInterface_RunningBehaviors( someBox ):
    "Generate the web interface of behavior and running behaviors"
    
    bm = naoqitools.myGetProxy( "ALBehaviorManager" );
    strPageContents = "";    
    listBehaviors = bm.getInstalledBehaviors();
    listRunning = bm.getRunningBehaviors();
    
    # generate callback
    
    strPageContents += "<head><meta http-equiv='refresh' content='6'><script>";
    strPageContents += """
    function sendNaoqiOrder( strOrder )
    {
        parent.sendNaoqiOrder( strOrder );
    };
    """;
    for strBehav in listBehaviors:
        strPageContents += "function toggle_%s()" % strBehav;
        strPageContents += """
        {
            if( document.getElementById('check_%s').checked )
            {
                sendNaoqiOrder( "ALMemory.raiseMicroEvent( 'behavior_launching', ['%s', True] )" );
            }
            else
            {
                sendNaoqiOrder( "ALMemory.raiseMicroEvent( 'behavior_launching', ['%s', False] )" );
            }        
        }
        """ % (strBehav, strBehav, strBehav);
        
    strPageContents += "</script></head>";
    strPageContents += "<body>Installed Behaviors<br><br>\n";
    
    strPageContents += "<table width=100%><tr>\n";    
    nCpt = 0;
    for strBehav in listBehaviors:
        bRunning = strBehav in listRunning;
        if( bRunning ):
            strChecked = "checked";
        else:
            strChecked = "";
        strPageContents += "<td width=20%><input type='checkbox' id='check_" + strBehav + "' value='checkbox' onclick='toggle_" + strBehav +"()' " + strChecked + " />" + strBehav + "<br></td>\n";
        nCpt += 1;
        if( nCpt > 4 ):
            strPageContents += "</tr></table><br><br><table width=100%><tr>";
            nCpt = 0;
    # finish current line
    while( nCpt <= 4 ):
        nCpt += 1;
        strPageContents += "<td width=20%>&nbsp;</td>";
    strPageContents += "</tr></table>\n";

    try:
        file = open( "/home/nao/www/ui/frame_behavior.html", "wt" );
        if( not file ):
            return;
        file.write( strPageContents );
        file.close();
    except:
            return;

# generateWebInterface_RunningBehaviors - end

def logToChoregraphe( strText, bIsError = False ):
    "print logs in the choregraphe debug print (like box.log)"
    debug.debug( "logToChoregraphe: '%s'" % strText );
    try:
        chor = naoqitools.myGetProxy( "ALChoregraphe" );
        # print( chor.getMethodList() ); # current bug in the web browser: can't browse ALChoregraphe !
        # print( chor.getMethodHelp( "onPythonError" ) ); # current bug in the web browser: can't browse ALChoregraphe !
        if( not bIsError ):
            chor.onPythonPrint( str( strText ) );
        else:
            chor.onPythonError( "???", "???", str( strText ) ); # bad: can't get the box name, pfffff, so it won't be wrotten => features disabled
    except BaseException, err:
        print( "choregraphetools.logToChoregraphe: err: %s" % str( err ) );
# logToChoregraphe - end

    
def assertInBox( bExpression, strOptionnalMessage = None ):
    # co = sys._getframe(1).f_code; # return one more, call we are in a method !
    # print debug.dump( co );
    # print "ASSERTION: %s (%s @ %3d)" % (co.co_name, co.co_filename, co.co_firstlineno);
    
    if( strOptionnalMessage != None ):
        strOptionnalMessage = " ( message: " + strOptionnalMessage + " )";
    else:
        strOptionnalMessage  = "";
        
    
    if( not bExpression ):
        logToChoregraphe( "assertInBox.error at %s%s" % ( str( debug.getFileAndLinePosition( 1 ) ), strOptionnalMessage ), bIsError = True );
        eval( assert_error ); # make it red, with some quite good reason explained :)
        
# assertInBox - end

# assertInBox(1);

import bz2
import zlib
import gzip
import StringIO
import tarfile

def decompress( data, nLenMax = -1 ):
    print debug.dumpHexa(data[:100])
    i = 0;
    if( nLenMax == -1 ):
        nLenMax = len(data)-8; # 8: minimal size to find an archive
    while( i < nLenMax ):
        #~ dataBin = [];
        #~ for ch in data[i:]:
            #~ dataBin.append( ord(ch ) );
        try:

            #~ bufferFile = StringIO.StringIO("coucou");
            #~ print bufferFile.read();
            #~ bufferFile.write( "salut" );
            #~ bufferFile.seek( 0 );
            #~ print bufferFile.read();            
            bufferFile = StringIO.StringIO(data[i:]);
            ar = tarfile.open( fileobj=bufferFile, mode='r:*' );
            print( "\nGOOD: TAR: found at offset of %d (uncompressed len: %d)" % (i, len(uncompressed)) );
            return uncompressed;
        except BaseException, err:
            print( "BAD: TAR: for offset: %d: %s" % ( i, err ) );

        try:
            uncompressed = zlib.decompress(data[i:], 16+zlib.MAX_WBITS);
            print( "\nGOOD: ZLB: found at offset of %d (uncompressed len: %d)" % (i, len(uncompressed)) );
            return uncompressed;            
        except BaseException, err:
            print( "BAD: ZLB: for offset: %d: %s" % ( i, err ) );

        try:
            decompressor = bz2.BZ2Decompressor();
            uncompressed = decompressor.decompress(data[i:]);
            #~ uncompressed = bz2.decompress( data[i:] );
            print( "\nGOOD: BZ2: found at offset of %d (uncompressed len: %d)" % (i, len(uncompressed)) );
            return uncompressed;
        except BaseException, err:
            print( "BAD: BZ2: for offset: %d: %s" % ( i, err ) );
        i += 1;
    # while - end
    return None; 
# decompress - end    
        
    
def debianize( strFilename ):
    """
    Explode debian binary
    return an array of pair [[filename1, data1], [filename2, data2]], with all datas uncompressed and unparsed.
    """
    
    #~ data = gzip.GzipFile( strFilename ).read();
    #~ print data;
    #~ return;
    
    #~ data = gzip.open( strFilename ).read();
    #~ print data;
    #~ return;    
    
    #~ uncompressedData = bz2.BZ2File(strFilename).read()
    #~ print str(uncompressedData)
    #~ return;
    
    #~ file = open( strFilename, 'rb' );
    #~ data = file.read();
    #~ file.close();
    #~ print debug.dumpHexa( data );
    
    #~ ar = tarfile.open(strFilename, 'r:*')
    #~ for item in ar:
        #~ print( str(item) );
        #~ print( "%s:" % item.name );
        #~ #print debug.dumpHexa(item.buf);
        #~ #print zlib.decompress(item.buf)
        #~ #print zlib.decompress(ar.extractfile(item).read())
        #~ data = ar.extractfile(item.name).read()
        #~ print data # works !
    #~ ar.close()    
    #~ return;
        
    fileLists = [];
    file = open( strFilename );
    data = file.read();
    file.close();
    
    print( "data len: %d" % len( data ) );

    nDataCompressedOffset = 0; # 132

    # works fine on toto.gz
    #~ f = gzip.open(strFilename, 'rb')
    #~ file_content = f.read()
    #~ print file_content
    #~ f.close()   
    
    #~ decompressor = bz2.BZ2Decompressor();
    #~ uncompressed = decompressor.decompress(data[nDataCompressedOffset:]);
        
    #~ uncompressed = zlib.decompress(data[nDataCompressedOffset:]);
    
    uncompressed = decompress( data );
    print( "uncompressed: %s" % str( uncompressed ) );
# debianize - end

def domNodeTypeToString( nNodeType ):
    if( nNodeType == xml.dom.minidom.Node.ELEMENT_NODE ):
        return "ELEMENT_NODE";
    if( nNodeType == xml.dom.minidom.Node.ATTRIBUTE_NODE ):
        return "ATTRIBUTE_NODE";
    if( nNodeType == xml.dom.minidom.Node.TEXT_NODE ):
        return "TEXT_NODE";
    if( nNodeType == xml.dom.minidom.Node.CDATA_SECTION_NODE ):
        return "CDATA_SECTION_NODE";
    if( nNodeType == xml.dom.minidom.Node.ENTITY_REFERENCE_NODE ):
        return "ENTITY_REFERENCE_NODE";
    if( nNodeType == xml.dom.minidom.Node.PROCESSING_INSTRUCTION_NODE ):
        return "PROCESSING_INSTRUCTION_NODE";
    if( nNodeType == xml.dom.minidom.Node.COMMENT_NODE ):
        return "COMMENT_NODE";
    if( nNodeType == xml.dom.minidom.Node.DOCUMENT_NODE ):
        return "DOCUMENT_NODE";
    if( nNodeType == xml.dom.minidom.Node.DOCUMENT_TYPE_NODE ):
        return "DOCUMENT_TYPE_NODE";
    if( nNodeType == xml.dom.minidom.Node.DOCUMENT_FRAGMENT_NODE ):
        return "DOCUMENT_FRAGMENT_NODE";
    if( nNodeType == xml.dom.minidom.Node.NOTATION_NODE ):
        return "NOTATION_NODE";

    return "unknown type";
# domNodeTypeToString - end

def domAttributesToString( node ):
    """
    return a string describing all attributes of a node
    """
    strOut = "node has %d attribute(s):\n" % node.attributes.length;
    for i in range(node.attributes.length):
        attr = node.attributes.item(i);
        strOut += "- %s:'%s'\n" % (attr.name, attr.value );
    return strOut;
# domAttributesToString - end

def domNodeToString( node, nDepth = 0, aListChildParentNum = [], aListChildParentName = [] ):
    "print a node list to a string" 
    strTab = "    " *  nDepth;
    if( nDepth > 0 ):
        strTab += "| ";
    strOut = strTab + "--------------------\n";
    if( node == None ):
        return strTab + "None!";
    try:
        strOut += strTab + "nodeType: %d (%s)\n" % ( node.nodeType, domNodeTypeToString( node.nodeType ) );
    except BaseException, err:
        print( "WRN: domNodeToString: nodeType: %s" % err );
    try:
        strOut += strTab + "localName: '%s'\n" % node.localName;
    except:
        pass
    try:
        strOut += strTab + "nodeName: '%s'\n" % node.nodeName;
    except:
        pass
    try:
        strOut += strTab + "nodeValue: '%s'\n" % node.nodeValue;
    except:
        pass
    try:
        strOut += strTab + "nodeData: '%s'\n" % node.nodeData;
    except:
        pass
    try:
        strOut += strTab + "attr name: '%s'\n" % node.getAttribute( "name" );
    except:
        pass        
    #~ try:
        #~ strOut += strTab + "attributes: '%s'\n" % str(node.attributes);
    #~ except BaseException, err:
        #~ print( "WRN: domNodeToString: attributes: %s" % err );
#            try:
    if( node.hasChildNodes() ):
            strOut += strTab + "Child(s): %d child(s):\n" % len( node.childNodes );
            nNumChild = 1;
            aListChildParentName.append( node.localName );
            strTotalPath = "";
            for name in aListChildParentName:
                strTotalPath += "/%s" % name;
            for nodeChild in node.childNodes:
                strChildNumberParentPrefix = "";
                for number in aListChildParentNum:
                    strChildNumberParentPrefix += "%d." % number;
                aListChildParentNum.append( nNumChild );
                strOut += strTab + "Child " + strChildNumberParentPrefix + str(  nNumChild ) + " (%s):\n" % strTotalPath+ domNodeToString( nodeChild, nDepth + 1, aListChildParentNum, aListChildParentName );
                aListChildParentNum.pop();
                nNumChild += 1;
            aListChildParentName.pop();
#                    strOut += strTab + "\n";
#            except:
#                strOut += strTab + "(error occurs while accessing to child)";
    strOut += "    " *  nDepth + "--------------------\n";
    return strOut;
# domNodeToString - end

def domGetFirstText(node):
    "travel the node and return the value of the first node type found with type TEXT_NODE"
    "it's a travel in depth first"
    
    if( node != None ):
        if( node.nodeType == node.TEXT_NODE ):
            return node.nodeValue.strip();
        if( node.hasChildNodes() ):
            for nodeChild in node.childNodes:
                text = domGetFirstText( nodeChild );
                if( text != None ):
                    return text;
    return None;
# getText - end

def domFindElement( node, strElementName ):
    "find a child by its name"
    if( not node.hasChildNodes() ):
        if(  node.nodeName == strElementName ):
            return node;
    else:
        for nodeChild in node.childNodes:
            if( nodeChild.nodeName == strElementName ):
                return nodeChild;
    return None;
# domFindElement - end
    
def domFindElementByPath( node, astrElementPathName ):
    """find a child of a child of a child... by its name tree"""
    """eg: ["starting-condition", "condition", "script_type"] """
    element = node;
    for name in astrElementPathName:
        element = domFindElement( element, name );
        if( element == None ):
            return None;
    return element;
# domFindElementByPath - end


#~ def nodeToText( node, _nNumLevel = 0 ):
    #~ """
    #~ return a string describing an xml node from minidom
    #~ """
    #~ strOut = "";
    #~ strOut += "__" * _nNumLevel + "node.nodeName: %s\n" % node.nodeName;
    #~ if( node.nodeType == node.TEXT_NODE ):
        #~ strOut += "__" * _nNumLevel + "node.data: %s\n" % node.data;
    #~ try:
        #~ element = node.getElementsByTagName( "name" );
        #~ strOut += "__" * _nNumLevel + "node.name: %s\n" % element.data;
    #~ except:
        #~ pass
        
    #~ for idx, subNode in enumerate( node.childNodes ):
        #~ strOut += "__" * _nNumLevel + "Child %d:\n%s" % ( idx, nodeToText( subNode, _nNumLevel = _nNumLevel +1 ) );
    #~ return strOut;
#~ # nodeToText - end

def findElementByName( node, strName ):
    nodes = [];
    for subnode in node.childNodes:
        if( subnode.nodeName == strName ):
            nodes.append( subnode );
        else:
            nodes.extend( findElementByName( node = subnode, strName = strName ) );
    return nodes;
# findElementByName - end
    
def extractAnimationsFromXar( strFilename ):
    """
    Parse a xar to find animations.
    return a dictionnary of animations or False on error
    """
    print( "INF: extractAnimationFromXar: parsing '%s'" % strFilename );
    allAnims = dict();
    xar = xml.dom.minidom.parse( strFilename );
    choregrapheNode = xar.childNodes[0]; # first is "ChoregrapheProject"
    strXarVersion = choregrapheNode.getAttribute( "xar_version" );
    print( "strXarVersion: %s" % strXarVersion );
    #~ print( domNodeToString( choregrapheNode ) );
    # look for root box
    for node in choregrapheNode.childNodes:
        if( node.nodeType != xml.dom.minidom.Node.TEXT_NODE and node.hasAttribute( "name" ) ):
            if( node.getAttribute( "name" ) == "root" ):
                break;
    else:
        return False;
    rootNode = node;
    #~ print( domNodeToString( rootNode ) );
    listNodesBox = findElementByName( rootNode, "Box" ); # find all elements with a specific name, and return them in an array
    print( "listNodesBox found: %d" % len( listNodesBox ) );
    #~ print( domNodeToString( listNodesBox[8] ) );
    for node in listNodesBox:
        strAnimationName = node.getAttribute( "name" );
        strAnimationName = strAnimationName.replace( " ", "_" );
        listTimeline = findElementByName( node, "Timeline" );
        #~ print( domNodeToString( listTimeline[0] ) );
        listNames = [];
        listTimes = [];
        listPositions = [];        
        for timeline in listTimeline:
            if( len(listTimeline) > 1 ):
                print( "ERR: more than one timeline in a box: not handled case! (strAnimationName:%s)"  % strAnimationName );
                return;
            #~ print( str( timeline.attributes ) );
            #~ print( domNodeToString( timeline ) );
            #~ print( domAttributesToString( timeline ) );
            nFps = int( timeline.getAttribute( "fps" ) );
            #~ print( "fps: %d" % nFps );
            listActuator = findElementByName( timeline, "ActuatorCurve" );
            for actuator in listActuator:
                strActuatorName = str(actuator.getAttribute( "actuator" )); # str => remove unicode
                listNames.append( strActuatorName );
                listKey = findElementByName( actuator, "Key" );
                keyTimes = [];
                keyPositions = [];
                if( len(listKey) < 1 ):
                    print( "WRN: extractAnimationFromXar: in the box %s, the joint %s is used but no keys are defined for it, removing it from the used joint list..." % ( strAnimationName, strActuatorName ) );
                    del listNames[-1];
                    continue;
                for key in listKey:
                    rKeyNumber = float( key.getAttribute( "frame" ) );
                    rKeyVal = float( key.getAttribute( "value" ) ) * math.pi/180;
                    keyTimes.append( rKeyNumber / nFps );
                    listTangent = findElementByName( actuator, "Tangent" );
                    if( len( listTangent ) == 0 ):
                        keyPositions.append( rKeyVal );  # no splines there
                    else:
                        keyPositions.append( [rKeyVal] );  # prepare for appending spline info
                    for tangent in listTangent:
                        #~ print( domAttributesToString( tangent ) );
                        strInterpType=tangent.getAttribute( "interpType" );
                        strSide=tangent.getAttribute( "strSide" );
                        rAbscissaParam=float( tangent.getAttribute( "abscissaParam" ) )/nFps;
                        rOrdinateParam=float( tangent.getAttribute( "ordinateParam" ) ) * math.pi/180;
                        if( strInterpType == "linear" ):
                            keyPositions[-1].append( [1,rAbscissaParam,rOrdinateParam] ); # todo, validate parameters!
                        elif( strInterpType == "bezier" ):
                            keyPositions[-1].append( [2,rAbscissaParam,rOrdinateParam] ); # todo, validate parameters!
                        else:
                            print( "ERR: extractAnimationFromXar: this type isn't handled: '%s'" % strInterpType );
                listTimes.append( keyTimes );
                listPositions.append( keyPositions );
            # for actuator
        allAnims[strAnimationName] = [listNames,listTimes,listPositions];
        # for timeline        
    # for node
    print( "INF: extractAnimationFromXar: exiting with %d anim(s)" % len(allAnims) );
    return allAnims;
# extractAnimationsFromXar - end

def animationsToTxt( allAnims, astrListToExport = [] ):
    """
    export animations to txt (with comments), so that it could be parsed from a file (serialisations)
    - astrListToExport: to export only some animation in the dict, eg: astrListToExport = ["BT_"];
    """
    import motiontools # to avoid cyclic import
    strOut = "";
    allAnimExported = [];
    for k,v in allAnims.iteritems():
        if( len(astrListToExport) > 0 ):
            for strExport in astrListToExport:
                if( strExport in k ):
                    break;
            else:
                print( "INF: animationsToTxt: skipping animation '%s'" % k.encode("utf-8") ); # even if the box is named "sendPaté", we can so print it.
                continue;
        allAnimExported.append( k );
        rTotalLength = motiontools.getTimelineDuration( v[1] );
        strOut += "animation_%s=[\n" % k;
        strOut += "    # duration: %5.2fs\n" % rTotalLength;
        strOut += "    # Names (%d joint(s)):\n" % len(v[0]);
        strOut +="     " + str( v[0] ) + ",\n";
        strOut += "    # Times:\n";
        if( True ):
            # output key info
            strOut += "    # KeyInfo:";
            for idx, timeArray in enumerate(v[1]):
                if( idx < len(v[0]) and len( timeArray ) > 0 ):
                    strOut += " %s: %d key(s), from: %5.2fs to %5.2fs;" % (v[0][idx], len(timeArray), timeArray[0], timeArray[-1]);
                else:
                    print( "WRN: animationsToTxt: this case should not been found if exporter has removed empty joint" );
                    if( idx < len(v[0]) ):
                        strOut += " %s: %d key(s), no keyframe!" % (v[0][idx], len(timeArray) );
                    else:
                        strOut += " nothing !?!";
            strOut += "\n"
            
        strOut +="     " + stringtools.floatArrayToText( v[1], 2 ) + ",\n";
        strOut += "    # Values:\n";
        strOut +="     " + stringtools.floatArrayToText( v[2], 2 ) + ",\n";
        strOut += "];\n";
    strOut += "allAnims = [";
    for k in allAnimExported:
        strOut += " animation_%s," % k;
    strOut += '];\n';
    strOut += "dictAnims = {";
    for k in allAnimExported:
        strOut += "\"%s\": animation_%s," % (k,k);
    strOut += '};\n';    
    return strOut;
# animationsToTxt - end

def autoTest_exportAnimation():
    strFileSrc = "d:\\tempChore2\\behavior.xar";
    strFileSrc = "C:\\work\\Dev\\git\\appu_shared\\animations\\misc\\alex_RomeoFull1\\behavior.xar";
    allAnims = extractAnimationsFromXar( strFileSrc );
    print animationsToTxt( allAnims, ["BT_"] );
    file = open( "/temp.py", "wt" );
    file.write( animationsToTxt( allAnims ).encode("utf-8") ); # even if the animations has a "é" on the name, it will work
    file.close();
# autoTest_exportAnimation - end    

def exportAnimation( strFilename ):
    """
    Export animation from a choregraphe file NOT FINISHED !!!
    """
    if( not os.path.exists( strFilename ) ):
        print( "exportAnimation: file '%s' not found" % strFilename );
        return -1;
    tar = tarfile.open( strFilename, "r:" );
    print str( tar.list() );

def autoTest():
    #~ debianize( "D:\\Dev\\git\\appu_data\\test_animations.crg.gz" );
    #~ debianize( "D:\\Dev\\git\\appu_shared\\temp\\toto.gz" );
    #~ debianize( "D:\\Dev\\git\\appu_shared\\temp\\toto.bz" );
    autoTest_exportAnimation();
    
if( __name__ == "__main__" ):    
    autoTest(); 
