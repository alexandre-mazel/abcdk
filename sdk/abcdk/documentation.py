# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Documentation tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Aldebaran Behavior Complementary Development Kit: documentation module"""

import datetime
import os

import cache
import color
import config
import constants
import documentation
import debug
import evaltools
import filetools
import misc
import naoqitools
import motiontools
import pathtools
import poselibrary
import profiler
import system
import test
import typetools

def generateDocumentation( objectToDocument, bShowPrivate = False, nBaseLevel = 0 ):
    "return a documentation of all methods and objects contains in an object"
    class Dummy:
        """ a small class just to deduce class type further"""
        def __init__(self):
            pass
    # class Dummy - end
    
    strDoc = "";
    nLenHashLine = 60;
    strDoc += "#" + " " * nBaseLevel + "-" * nLenHashLine + "\n";
    try:
        strName = objectToDocument.__name__;
    except:
        strName = "(noname)";
    try:
        strTypeName = type( objectToDocument ).__name__;
    except:
        strTypeName = "(noname)";        
    strDoc += "#" + " " * nBaseLevel + " %s '%s': %s\n" % ( strTypeName, strName, str( objectToDocument.__doc__ ) );
    strDoc += "#" + " " * nBaseLevel + "-" * nLenHashLine + "\n";
#    strDoc += "# summary:\n";
    stdDocClass = "";
    stdDocMethod = "";
    stdDocData = "";
    
    for attrName in dir( objectToDocument ):
        if( not bShowPrivate and ( attrName[0:2] == '__' or attrName[0:4] == "dict" ) ):
            continue;
        if( "autoTest" in attrName ):
            continue;
        some_object = getattr( objectToDocument, attrName );
        try:
            if( isinstance( some_object, type(constants) ) ): # quand on importe un module, il apparait dans le scope de l'objet qui l'a importé
                continue;
        except BaseException, err:
            print( "ERROR: generateDocumentation: pb on object '%s' (err:%s)" % ( attrName, err ) );
#            continue;
        strDesc = "";
        if( typetools.isDict( some_object ) ):
            strDesc = "a dictionnary.";
        elif( isinstance( some_object, type( bool ) ) and not isinstance( some_object, type( Dummy ) ) ):
            strDesc = "a bool.";
        elif( typetools.isInt( some_object ) ):
            strDesc = "an integer.";
        elif( isinstance( some_object, float ) ):
            strDesc = "a float.";            
        elif( isinstance( some_object, list ) ):
            strDesc = "a list.";            
        elif( typetools.isString( some_object ) ):
            strDesc = "a string.";            
        elif( isinstance( some_object, type( Dummy ) ) ):
            attrName = "class " + attrName;
            strDesc = some_object.__doc__;
        else:
            if( some_object.__doc__ == None ):
                strDesc = "TODO: DOCUMENT ME";
            else:
                strDesc = some_object.__doc__;
        if( isinstance( some_object, type( generateDocumentation ) ) ):
            attrName = attrName + "(" + ")";
        strToAdd = "#" + " " * nBaseLevel + " - %s: %s\n" % ( attrName, strDesc );
        if( isinstance( some_object, type( generateDocumentation ) ) ):
            stdDocMethod += strToAdd;
        elif( isinstance( some_object, type( Dummy ) ) ):
            stdDocClass += strToAdd;
            stdDocClass += generateDocumentation( some_object, nBaseLevel = nBaseLevel + 6 );            
        else:
            stdDocData += strToAdd;
    if( stdDocClass != "" ):
        strDoc += "#" + " " * nBaseLevel + " Class:\n" + stdDocClass;            
    if( stdDocMethod != "" ):
        strDoc += "#"+ " " * nBaseLevel +" Method:\n" + stdDocMethod;
    if( stdDocData != "" ):
        strDoc += "#"+ " " * nBaseLevel +" Data:\n" + stdDocData;
    strDoc += "#" + " " * nBaseLevel + "-" * nLenHashLine + "\n";            
    return strDoc;
# generateDocumentation - end

def generateAllDocumentation():
    "compute all the documentation and return it to a string"
    strDoc = "";
    strDoc += '#' * 60 + "\n";
    strDoc += "### Aldebaran Behavior Complementary Development Kit: Full Module documentation  ###\n";
    strDoc += '#' * 60 + "\n";

    allModules = sort(constants.allModuleName);
    for strModuleName in allModules:
        if( strModuleName  == "documentation" ):
            continue; # weird: it doesn't accept this module type anymore
        #import importlib # argh require python 2.7. #=> faire les import a la main
        # importlib.import_module( strModuleName ); 
        strDoc += generateDocumentation( eval( strModuleName ) );

    return strDoc;
# generateAllDocumentation - end

# print( generateDocumentation( constants ) );
# print( generateDocumentation( color ) );

# try to get params info:
#print( generateDocumentation( generateDocumentation, bShowPrivate = True ) );
#import inspect
#print( "le truc: " + inspect.getdoc(generateDocumentation) or inspect.getcomments(generateDocumentation) );
#    args, varargs, varkw = getargs(func.func_code)


# TODO: generer aussi les html avec pydoc
#import pydoc
#pydoc.writedocs( "config" )

#print generateAllDocumentation();

# to generate on the fly, try this:
# python -c "import documentation; import color ; print documentation.generateDocumentation( color )"

def generateAllDocumentationToWebsite( strDocDestPath ):
    import __init__
    for strModule in constants.allModuleName:
        if( strModule != "documentation" ):
            strDest = strDocDestPath + strModule + ".txt";
            print( "documentation of %s goes to %s" % (strModule, strDest) );
            strCommand = "import documentation; import %s ; docu = documentation.generateDocumentation( %s ); file = open('%s','wt');file.write(docu);file.close();" % (strModule,strModule,strDest);
            print( "command is: '%s'" % strCommand );
            os.system( "python -c \"%s\"" % strCommand );
    # generate web page
    file = open( strDocDestPath + "index.html", "wt" );
    strVersion = __init__.__version__;
    strDate = datetime.datetime.now().strftime( '%Y/%m/%d' );
    file.write( "<FONT SIZE=+2>A</Font>ldebaran <FONT SIZE=+2>B</Font>ehavior <FONT SIZE=+2>C</Font>omplementary <FONT SIZE=+2>D</Font>evelopment <FONT SIZE=+2>K</Font>it<BR>\n<FONT SIZE=-1>Compact Documentation generated from version %s, the %s <BR>\n<BR></FONT>\n" %  ( strVersion, strDate ) );
    for strModule in constants.allModuleName:
        file.write( "<A HREF='%s.txt'>%s</A><BR>\n" % (strModule,strModule) );
    file.close();
# generateAllDocumentationToFile - end            
# generateAllDocumentationToFile - end
# generateAllDocumentationToFile( "d:\\abcdk_doc\\" ); # => bing infinite recursion

# to generate all documentation (working):
# mkdir abcdk_doc
# python -c "import documentation; documentation.generateAllDocumentationToWebsite( 'C:/work/Dev/git/appu_shared/sdk/abcdk_doc/' );"
# then copy generated to the server:
# scp ../abcdk_doc/* amazel@studio.aldebaran-robotics.com:/var/www/abcdk_doc/


