# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Misc tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Misc tools"

print( "importing abcdk.misc" );

import os
import constants


def reloadAllModules():
    "Force reloading all modules"
    allModules = constants.allModuleName;
    strLocalPath = os.path.dirname( __file__ );
    strThisModuleName = os.path.basename( __file__ ).split('.')[0];
    print( "INF: abcdk.misc.reloadAllModules: reloading all abcdk module, from this path '%s'" % strLocalPath );
    for strModuleName in allModules:
        if( strModuleName == strThisModuleName ): # zap this module
            continue;
        print( "reloading '%s'" % strModuleName );
        try:
            obj = __import__( strModuleName, globals() );
            reload( obj );
        except BaseException, err:
            print( "WRN: abcdk.misc.reloadAllModules: while reloading '%s' got error %s. You should relaunch naoqi before using this module." % (strModuleName, err ) );
    print( "INF: abcdk.misc.reloadAllModules - end" );
# reloadAllModules - end

def importAllModulesAsGlobals():
    """
    Add all abcdk modules to the global scope, it's just to ensure that even just on install, all the boxes will have abcdk services
    """
    import naoqitools
    pb = naoqitools.myGetProxy( "ALPythonBridge" );
    allModules = constants.allModuleName;
    for strModuleName in allModules:
        strEval = "import abcdk.%s" % strModuleName;
        print( "evaluating: %s" % strEval );
        pb.eval( strEval );
# importAllModulesAsGlobals - end

def duplicateList( pOriginalList ):
    "totally duplicate a list object, even if it contents enclosed list or sub enclosed list..."
    newlist = [];
#    newList = pOriginalList;
    for elem in pOriginalList:
        if( isinstance( elem, list ) ):
            newlist.append( duplicateList( elem ) );
        else:
            newlist.append( elem );
    return newlist;
# duplicateList - end

def duplicateList_test():
    "test the duplicateList method"
    def mafuncChange( somelist ):
        "without duplication"
        for i in range( len(somelist) ):
            somelist[i][0]*=2;
            
    def mafunc( pSomelist ):
        "with duplication"
        somelist = duplicateList( pSomelist );
        mafuncChange( somelist );

    maliste= [[1],[3],[5],[10,20,30],[[100,200]], ];

    print( str( maliste ) );
    mafunc( maliste );
    print( str( maliste ) );    
    mafuncChange( maliste );
    print( str( maliste ) );
# duplicateList_test - end
    
# duplicateList_test();

import inspect

# needs to be primed with an empty set for loaded
def recursivelyReloadAllSubmodules(strModule, aLoaded=None):
    """ Reload all submodules (usefull to reload numpy)

    recursively_reload_all_submodules(mymodule, set())
    from: http://stackoverflow.com/questions/5364050/reloading-submodules-in-ipython
    """
    print("strModule %s" % strModule)
    for name in dir(strModule):
        member = getattr(strModule, name)
        if inspect.ismodule(member) and member not in aLoaded:
            recursivelyReloadAllSubmodules(member, aLoaded)
        aLoaded.add(strModule)
    reload(strModule)
# end recursivelyReloadAllSubmodules


