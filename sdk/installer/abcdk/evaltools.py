# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Eval tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

# this module should be called eval, but risk of masking with the keyword eval.

"Eval tools"
print( "importing abcdk.evaltools" );

import sys
import threading

import config
import debug


class ASyncEvalThread( threading.Thread ):
    "To handle asynchron evaluation (eval in another thread)"
    def __init__(self, strPythonCode, globaldico = None, localdico = None, bStoppable = False ):
        threading.Thread.__init__( self );
        self.strPythonCode = str( strPythonCode );
        self.globaldico = globaldico;
        self.localdico = localdico;
        self.bStoppable = bStoppable;
        self.bMustStop = False;
    # init - end

    def run( self ):
        import debug # import the module in the children thread
        debug.debug( "evaltools.ASyncEvalThread evaluating '%s'" % self.strPythonCode );
        self.bMustStop = False;
        sys.settrace( self.globaltrace ); # permit to kill thread, WRN: it's a debug purpose functionnality not existing or all platform and ...
        #~ self.strPythonCode = """
#~ import signal
#~ print( 'installing handler...' );
#~ def handler(signum, frame):
    #~ print 'Signal handler called with signal', signum;
    #~ exit( 42 );
#~ signal.signal(signal.SIGTERM, handler)
#~ """ + self.strPythonCode; => ERROR signal only works in main thread
        if( config.bDebugMode ):
            debug.logToChoregraphe( "ASyncEvalThread: strPythonCode: '%s'" % self.strPythonCode );
        exec( self.strPythonCode, self.globaldico, self.localdico ); # TODO: here: do something to test bMustStop is not Set to True, if so exit
        debug.debug( "altools: ASyncEvalThread evaluating '%s' - end" % ( self.strPythonCode ));
    # run - end

    def stop( self, rTimeOut = 3.0 ):
        "stop the process"
        #   if( not self.isFinished() ): # doesnt return a correct value!
        debug.debug( "ASyncEvalThread.stop(): stopping..." );
        self.bMustStop = True;
        return self.join( rTimeOut ); #wait with a timeout of n sec # attention au bout de n sec, il ne kill pas le join mais juste il rend la main...
    # stop - end

    def isFinished( self ):
        "is the process finished ?"
        bAlive = self.isAlive();
        debug.debug( "ASyncEvalThread.isFinished() => %s" % str( bAlive ) );
        return bAlive;
    # isFinished - end

    def globaltrace(self, frame, why, arg):
#        debug.logToChoregraphe( "globaltrace( frame='%s', why='%s', arg='%s' )" % (frame, why, arg) );
        if why == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, why, arg):
#        debug.logToChoregraphe( "localtrace( frame='%s', why='%s', arg='%s' )" % (frame, why, arg) );
        if self.bMustStop:
            if why == 'line':
                raise sys.exit( -9 );
        return self.localtrace;

# ASyncEvalThread - end

def asyncEval( strPythonCode, globaldico =globals(), localdico = locals() ):
  "launch an evaluation in another python thread, a tricky specific manner"
  evaluationThreadObj = ASyncEvalThread( strPythonCode, globaldico, localdico );
  evaluationThreadObj.start();
  return evaluationThreadObj;
# asyncEval
