# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Test tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Test tools"""
print( "importing abcdk.test" );

import sys

import config

def isAutoTest():
    "Do we have to launch autotest?"
    try:
        bTest = len( sys.argv ) > 1 and sys.argv[1] == 'test';
        bTest = bTest or config.bAutoTestEnabled;
        if( bTest ):
            print( "AUTO-TEST is ON" );
        return bTest;
    except:
        return False; # no command line nor...
# isAutoTest - end

def activateAutoTestOption():
    print( "abcdk.test: activateAutoTestOption..." );    
    config.bAutoTestEnabled = True;
    config.bInChoregraphe = False;
    config.bDebugMode = True;
    import naoqitools
    reload( naoqitools ); # so that the new ip adress is used
# activateAutoTestOption - end

global_nNbrAssertCheck = 0
def assert_check( v1, reference = True ):
    global global_nNbrAssertCheck
    global_nNbrAssertCheck += 1
    print( "%d: assert_check: %s" % (global_nNbrAssertCheck, str(v1)) )
    if( v1 != reference ):
        print( "assert_check: '%s' != '%s'" % (v1, reference) )
        assert(0)    

def assert_check_float( v1, reference, rThreshold = 0.01 ):
    global global_nNbrAssertCheck
    global_nNbrAssertCheck += 1
    print( "%d: assert_check: %s" % (global_nNbrAssertCheck, str(v1)) )
    if( abs(v1 - reference) > rThreshold ):
        print( "assert_check: '%s' ~!= '%s'" % (v1, reference) )
        assert(0)          
        
        
def assert_check_comp( v1, reference, compFunc ):
    global global_nNbrAssertCheck
    global_nNbrAssertCheck += 1
    print( "%d: assert_check: %s" % (global_nNbrAssertCheck, str(v1)) )
    if( not compFunc( v1, reference ) ):
        print( "assert_check: '%s' !== '%s'" % (v1, reference) )
        assert(0)            
        
print type(assert_check_comp        )