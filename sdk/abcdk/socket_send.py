# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# send files to analyse to Network using socket
# Author: A.Mazel, L.George, ...
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Socket Send"

# this module send stuffs to a socket

print( "importing abcdk.socket_send" );

import socket
import struct
import numpy as np
import ast # Abstract Syntax Trees

import socket_receive # for Message type and class and enums

class SocketSender:
    """
    ear a socket and receive file. then do things with files
    """
    def __init__(self):
        self.socket = None
    # __init__ - end
    
    def __del__(self):
        self.disconnect()
    
    def connect( self, strHostname = "localhost", nPortNumber = 10000, bVerbose = False ):
        if bVerbose: print( "INF: SocketSender: connecting to %s:%s" % (strHostname,nPortNumber) )
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((strHostname, nPortNumber))
    
    def sendFile(self, strFilename, nActionToDo = socket_receive.kActionUnknown ):
        file = open( strFilename, "rb" )
        datas = file.read()
        file.close()
        nDataType = socket_receive.getTypeFromExt(strFilename)
        return self.sendData(datas,nDataType,nActionToDo)
    
    def sendData( self, data, nDataType = socket_receive.kTypeUnknown, nActionToDo = socket_receive.kActionUnknown, bVerbose = False, bWaitResult = False ):
        """
        prepare data to be sent as raw.
        - bWaitResult: wait for results from remote server, and return it
        Return: 
        - if bWaitResult: return results from remote server. or None on error
        - else: return None
        
        """
        
        if nDataType == socket_receive.kTypeImageCv2:
            shape = data.shape
            print shape
            print( "len data: %s" % len(data) )            
            """
            data = data.flatten()
            print( "len data: %s" % len(data) )
            data = np.concatenate( (np.array(shape), data) ) # here we lost the 640 => faire un vrai format binaire, peuchere ! et envoyer tout en binaire comme des pros !
            print( "len data: %s" % len(data) )
            #data = data.tostring()
            print( "len data: %s" % len(data) )
            """
            data = struct.pack('<h', int(shape[0])) + struct.pack('<h', int(shape[1])) + struct.pack('<b', int(shape[2])) + data.flatten().tostring()
            print( "len data: %s" % len(data) )

        if bVerbose: print( "INF: SocketSender.sendData: sending data size: %s" % len(data) )
        dataWithHeader = struct.pack('<L', int(len(data)+2)) + struct.pack('<b', nDataType) + struct.pack('<b',nActionToDo) + data
        self.socket.sendall( dataWithHeader )
        
        if not bWaitResult:
            return None
            
        # receive results:    
        raw_msglen = socket_receive.receiveN( self.socket, 4)
        if not raw_msglen:
            return None
            
        msglen = struct.unpack('<L', raw_msglen)[0]
        if bVerbose: print( "INF: SocketSender.sendData: receving answer: data size: %s" % msglen )
        datas_ret = socket_receive.receiveN( self.socket, msglen )
        if not datas_ret:
            return None
        return ast.literal_eval(datas_ret)
    
    def disconnect(self):
        if self.socket != None:
            self.socket.close()
            self.socket = None
# class SocketSender - end

def autoTest():
    import test
    import time
    test.activateAutoTestOption();
    s = SocketSender()
    s.connect()
    s.sendFile( "/tmp/RomeoVole.png" )
    s.disconnect()
# autoTest - end

if( __name__ == "__main__" ):
    autoTest();
