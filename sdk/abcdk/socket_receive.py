# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Receive files to analyse from Network using socket
# Author: A.Mazel, L.George, ...
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Socket Receive"

# this module ear to a socket to receive stuffs (cf socket_send for send example)

print( "importing abcdk.socket_receive" );

import socket
import struct
import numpy as np

kTypeUnknown = -1
kTypeAudioRaw = 1 # [samplerate, nbrbits, nbr channel, interlaced datas]
kTypeAudioWav = 2
kTypeAudioMp3 = 3
kTypeAudioOgg = 4

kTypeImageRaw = 50 # [x,y,nbrplane,interlaced planes]
kTypeImageJpg = 51
kTypeImagePng = 52
kTypeImageCv2 = 53 # [x (short),y(short),nbrplane(char), data] all as a numpy tostringified

kActionUnknown = -1
kActionAuto = 1
kActionObjectRecognitionCnn = 2
kActionVad = 3
kActionAudioIdentification = 4

# TODO: type from ext and ext from type! (using an array or a dict)

def getTypeFromExt( strFilename ):
    nDataType = kTypeUnknown
    strExt = strFilename.split('.')[-1]    
    if strExt.lower() in ["jpg", "jpeg"]:
        nDataType = kTypeImageJpg
    if strExt.lower() in ["png"]:
        nDataType = kTypeImagePng
    if strExt.lower() in ["wav", "wave"]:
        nDataType = kTypeAudioWav
    if strExt.lower() in ["mp3"]:
        nDataType = kTypeAudioMp3
    return nDataType


def receiveN(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = ''
    while len(data) < n:
        nRemainingWaitedData = n - len(data)
        #~ print( "DBG: waiting for size: %s" % nRemainingWaitedData )
        packet = sock.recv(nRemainingWaitedData)
        if not packet:
            return None
        data += packet
    return data
# receiveN - end   

def sendSizedBuffer( conn, data ):
    data = struct.pack('<L', len(data)) + data    
    conn.sendall( data )

class Message:
    def __init__(self):
        self.nType = kTypeUnknown
        self.nAction = kActionUnknown
        self.data = []
        
    def readFromSocket( self, conn ):
        """
        return the number of data read.
        data should be in the form of: [packet_size (excluding packet size) (uint32 LSB), type of data (int8), type of action(int8), datas]
        return True if ok or False on error
        """
        raw_msglen = receiveN(conn, 4)
        if not raw_msglen:
            return False
            
        msglen = struct.unpack('<L', raw_msglen)[0]
        datas = receiveN( conn, msglen )
        if not datas:
            return False
        self.nDataType = struct.unpack('<b', datas[0])[0]
        self.nActionType = struct.unpack('<b', datas[1])[0] # here we must use struct.calcsize (or assume '<b' size is 1 !!!
        if self.nDataType == kTypeImageCv2:
            print( "fromstring!" )
            
            shape = [ struct.unpack("<h", datas[2:4])[0], struct.unpack("<h", datas[4:6])[0], struct.unpack("<b", datas[6:7])[0] ]
            print shape
            
            self.data = np.fromstring( datas[7:], np.uint8 )
            print( "lendata: %s" % len( self.data ) )
            self.data = np.reshape(self.data, (shape[1], shape[0],shape[2]) )
            print( "lendata: %s" % len( self.data ) )
            print( "shape: %s" % str(self.data.shape) )            
        else:
            self.data = datas[2:]
            assert( len(self.data) == msglen-2 )
        print( "INF: Message.readFromSocket: receive new datas: type %d, action: %d, sizedata: %d" % (self.nDataType,self.nActionType,len(self.data)) )
        return True
    # readFromSocket - end
    
    def writeToFile( self, strPath = "/tmp/", strFilename = None ):
        """
        - strFilename: filename to use if None => time stamp
        """
        if strFilename == None:
            import datetime
            datetimeObject = datetime.datetime.now()
            strFilename = datetimeObject.strftime( "%Y_%m_%d-%Hh%Mm%Ss%fms" );
            strFilename = strFilename.replace( "000ms", "ms" ); # because there's no flags for milliseconds
        strFileDst = strPath + strFilename
        print( "INF: : Message.writeToFile: writing to '%s', size: %s" % (strFileDst, len(self.data)) )
        if self.nDataType == kTypeImageCv2:
            import cv2
            cv2.imwrite( strFileDst + ".jpg", self.data )
        else:
            f = open( strFileDst, "wb" )
            f.write( self.data )
            f.close()        
    # writeToFile - end
    
    def analyse( self, optionnalCallbackMethod ):
        """
        analyse the message, based on his type and action
        return the analysed results (action dependant)
        """
        if optionnalCallbackMethod != None:
            return optionnalCallbackMethod( self.data )
        if nActionType==kActionObjectRecognitionCnn:
            pass # TODO
    # analyse - end
        
# class Message - end        

class SocketReceiver:
    """
    ear a socket and receive file. then do things with files
    """
    def __init__(self):
        self.bMustStop = False
        self.socket = None
    # __init__ - end
    
    def isRunning(self):
        return self.socket != None
        
    def run(self, nPortNumber = 10000, optionnalCallbackMethod = None, strPathStoreAllMessages = None):
        """
        Run socket server. Will never stop unless error.
        - strPathStoreAllMessages: give a path to where to write all incoming messages (None => don't store)
        """
        
        strHost = "" # Symbolic name meaning all available interfaces
        
        self.socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        print( "INF: SocketReceiver: earing on port: %s" % nPortNumber )
        
        self.socket.bind(( strHost, nPortNumber ))
        
        self.socket.listen(1)
        while not self.bMustStop:
            # wait for a new connection
            conn, addr = self.socket.accept()
            print 'Connected by', addr
            
            while 1:
                mess = Message()
                bSuccess = mess.readFromSocket(conn)
                if not bSuccess: # finished
                    break
                
                if strPathStoreAllMessages != None:
                    mess.writeToFile(strPathStoreAllMessages)
                ret = mess.analyse(optionnalCallbackMethod)
                print( "DBG: returned value: %s" % str(ret) )
                sendSizedBuffer(conn, repr(ret))
            conn.close()        
        # while - end
        
        print( "INF: SocketReceiver: earing on port: %s - disconnected" % nPortNumber )
        self.socket = None
        
    # run - end
    
    def stop(self):
        self.bMustStop = True
    # stop - end
# class SocketReceiver - end


def autoTest():
    import test
    import time
    test.activateAutoTestOption();
    s = SocketReceiver()
    nPortNumber = 10000
    s.run( nPortNumber )
    #time.sleep( 1000 )
    s.stop()
# autoTest - end

if( __name__ == "__main__" ):
    autoTest();
