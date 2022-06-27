#!/usr/bin/python

import threading
import logging
import socket
import time
import os

from abcdk.stk import runner

class MoveFiles(threading.Thread):
    def __init__(self,strPath,strDstHost,rBandwithMax):
        threading.Thread.__init__(self)
        if not runner.is_on_robot():
            raise RuntimeError("Detected that we are not running on a robot. This module should run on a robot")
        self.bThreadRunning = True
        self.strPath = strPath
        self.strDstHost = strDstHost
        self.strDstFolderName = socket.gethostname()
        self.nBandwithMaxBits = int(rBandwithMax * 8)

        os.system( "ssh %s 'mkdir -p %s'" % (self.strDstHost, self.strDstFolderName) )
        logging.info("Start moving from '%s' to '%s'" % (self.strPath, self.strDstHost))

    def isFileOpenForWrite(self, strFilename):
        """
        Is this file already open by the system, for write ?
        (so it's not "finished" / full)
        """
        handler = open( strFilename, "ab" )
        if( handler ):
            handler.close()
            return False
        return True

    def run (self):
        while self.bThreadRunning == True:
            try:
                self.sendFiles(self.strPath)
            except Exception, err:
                logging.error(err)
            time.sleep(10)


    def sendFiles(self,strPath):
        aFiles = sorted(os.listdir(strPath))
        for strFile in aFiles:
            strFullPath = strPath + os.sep + strFile
            if os.path.islink(strFullPath):
                continue
            if os.path.isdir(strFullPath):
                #recursively check the folders
                self.sendFiles( strFullPath)
                continue
            if( self.isFileOpenForWrite( strFullPath ) ):
                logging.debug("File %s is currently open. It won't be copied", strFullPath)
                continue

            nSizeBefore = os.path.getsize( strFullPath )
            if( nSizeBefore > 0 ):
                logging.info( "Move file '%s'" % strFile )
                strCommand = "scp -q -r -l %s \"%s\" \"%s\"" % (self.nBandwithMaxBits,strFullPath, self.strDstHost + ":~/" + self.strDstFolderName + os.sep + strFile ) # TODO check option VerifyHostKeyDNS
                nRet = os.system( strCommand ) 
                if( nRet != 0 ):
                    logging.error( "Error while copying %s: nRet: %s" % (strFile, nRet) )
                else:
                    nSizeAfter = os.path.getsize( strFullPath )
                    if nSizeAfter != nSizeBefore:
                        logging.warning( "Size of '%s' has changed after scp: from %s to %s. \n File will not be removed." % (strFile, nSizeBefore, nSizeAfter) )
                    else:
                        os.remove( strFullPath )


    def stop(self):
        logging.info("Stop move files")
        self.bThreadRunning = False

if __name__ == "__main__":
    logging.basicConfig(filename='moveFiles.log',
        level=logging.DEBUG,
        format='%(levelname)s %(relativeCreated)6d %(threadName)s %(message)s (%(module)s.%(lineno)d)',
        filemode='w')

    mover = MoveFiles(strPath = "/home/nao/test",
                      strDstHost = "robotdata@protolab.aldebaran.com",
                      rBandwithMax = 10.0)
    mover.start()

    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        mover.stop()
