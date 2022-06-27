# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Chat tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################


"""
Tools to chat (for the moment, only using Google Chat.

WRN: on NAO from choregraphe, you need to change that part in the file "flush_error patch" (being root):

    /usr/lib/python2.7/site-packages/xmpp/debug.py (around line 288):

    self._fh.flush()
=>
        try:
            self._fh.flush();
        except BaseException, err:
            print( "WRN: xmpp/debug.py: from choregraphe bug: flush and StdoutCatcher pas copain: %s" % str( err ) ); # StdoutCatcher instance has no attribute 'flush'

"""

print( "importing abcdk.chat" );

import xmpp, time, mutex

import debug
import stringtools

class Gtalk:
    """
    Google Talk interface
    """
    def __init__( self, strSenderEmail, strPassword ):
        self.sender = strSenderEmail;
        self.password = strPassword;
        print( "INF: abcdk.chat.Gtalk: using account '%s'" % strSenderEmail );
        self.mutexLastMessage = mutex.mutex();
        self.mutexSendReceive = mutex.mutex(); # the outlaying object seems a bit dirty, so we're mutexing all in/out
        self.aLastMessage = []; # for each message received, an array [strText, strSender]
        self.connection = False;
        self.lastConnected = {}; # for each str(sender), the last connection time (so we could wakeup connection when receiving stuffs)
    # __init__ - end

    def __del__( self ):
        self.stopConnected();
    # __del__ - end

    def getConnected( self ):
        """
        Connect to google server
        return True if ok
        """
        print( "INF: abcdk.chat.Gtalk: connecting to server..." );
        jid = xmpp.JID(self.sender)
        print( "2" );
        try:
            self.connection = xmpp.Client('gmail.com')
        except BaseException, err:
            print( "WRN: abcdk.chat.Gtalk.getConnected: From choregraphe there's always this error: %s" % str(err) ); # trying to catch StdoutCatcher instance has no attribute 'flush', but doing so, the object is not created cf flush_error patch
        print( "3" );
        self.connection.connect(('talk.google.com', 5222 ))
        print( "4" );
        result = self.connection.auth( jid.getNode( ), self.password )
        print( "5" );
        print( result );
        print( "6" );
        bRet = result == "sasl";
        print( "7" );
        print( "INF: abcdk.chat.Gtalk: connecting to server, result: %s" % bRet );
        if( bRet ):
            self.connection.RegisterHandler('message', self.handleIncomingMessage );
            self.connection.sendInitPresence();            
        return bRet;
    # getConnected - end
    
    ### deprecated !
    #~ def getPresence( self, strReceiver ):
        #~ bRet = xmpp.protocol.get_presence( strReceiver );
        #~ print( "INF: abcdk.chat.getPresence: %s" % str( bRet ) );
        #~ return bRet;
    
    def update( self ):
        """
        update the connection, receive message...
        return:
            - a message
            - None if no message
            - False when connection is closed by remote
        """
        bRet = self.connection.Process(0.5);
        if( not bRet ):
            return False;
        while( self.mutexLastMessage.testandset() == False ):
            print( "INF: abcdk.chat.Gtalk.update: already initing, waiting..." );
            time.sleep( 0.1 );            
        if( len( self.aLastMessage ) > 0 ):
            message = self.aLastMessage.pop(0);
            print( "message poped: %s" % str( message ) );
        else:
            message = None;
        self.mutexLastMessage.unlock();
        return message;
    # update - end
    
    def handleIncomingMessage( self, connect_object, message_node ):
        """
        handle message, return True if new message or None if none
        """
        while( self.mutexSendReceive.testandset() == False ):
            print( "INF: abcdk.chat.Gtalk.handleIncomingMessage: already in, waiting..." );
            time.sleep( 0.1 );                
        print( "DBG: abcdk.chat.Gtalk.handleIncomingMessage: in!" );
        print( "DBG: abcdk.chat.Gtalk.handleIncomingMessage: from: %s" % str(message_node.getFrom()) );
        print( "DBG: abcdk.chat.Gtalk.handleIncomingMessage: time: %s, lastConnected: %s" % (time.time(), str(self.lastConnected) ) );
        print( dir( message_node ) );
        strSender = str(message_node.getFrom());
        strSender = strSender.split("/")[0]; # sometimes there's "/gmail.4C7A7A3A" after it
        strText=( message_node.getBody() );
        if( not strSender in self.lastConnected.keys() ):
            self.lastConnected[strSender] = 0; # create it
            rTimeLapse = 100000;
        else:
            rTimeLapse = time.time() - self.lastConnected[strSender];
        self.lastConnected[strSender] = time.time();
            
        if strText == "None" or strText == None:
            if( rTimeLapse > 60 ):
                print( "INF: (re)initing discussion with %s (timelapse: %fs)" % (strSender,rTimeLapse) );
                self._sendMessage( "(reconnecting... please retry...)", strSender ); # because when connection was out we just receive empty message ("activity") from sender
            self.mutexSendReceive.unlock();                
            return False;
        print( debug.dumpHexa(strText) );            
        strText=stringtools.phonetiseFrenchAccent( strText );
        print( "\nINF: abcdk.chat.Gtalk.handleIncomingMessage: received: '%s'\n" % strText );      
        print( "DBG: abcdk.chat.Gtalk.handleIncomingMessage: from (simplified): '%s'" % strSender );
        #~ if( "et toi ?"  in strText ):
            #~ self.sendMessage( "carrément, un peu!",  strSender );
        while( self.mutexLastMessage.testandset() == False ):
            print( "INF: abcdk.chat.Gtalk.handleIncomingMessage: already initing, waiting..." );
            time.sleep( 0.1 );            
        self.aLastMessage.append( [strText, strSender] );
        self.mutexLastMessage.unlock();
        self.mutexSendReceive.unlock();
        return True;
    # handleIncomingMessage - end
    
    def _sendMessage( self, strMessage, strReceiver ):
        """
        not armored
        """
        self.connection.send( xmpp.protocol.Message( strReceiver, str(strMessage),"chat") );
        time.sleep(1); # todo: real info
        return True;    
            
    def sendMessage( self, strMessage, strReceiver ):
        """
        return True if ok
        strReceiver: whom to send message ?
        """
        while( self.mutexSendReceive.testandset() == False ):
            print( "INF: abcdk.chat.Gtalk.sendMessage: already in, waiting..." );
            time.sleep( 0.1 );        
        bRet = self._sendMessage( strMessage, strReceiver );
        self.mutexSendReceive.unlock();
        return bRet;


    def stopConnected( self ):
        if( self.connection != False ):
            print( "INF: abcdk.chat.Gtalk.stopConnected: from account '%s'" % self.sender );
            self.connection.disconnect();
            self.connection = False;
# Gtalk - end

def constructUsingAccount( strName ):
    """
    Create an account using pre-recorded password (factory method)
    (for the moment it's hardcoded in plain text, but one day, without changing the interface...)
    strName: the sender email adress (you could ommit @gmail.com as it's the default value)
    """
    if( not "@" in strName ):
        strName += "@gmail.com";
            
    if( "naoalex16" in strName.lower() ):
        strPwd = "NaoAlex16pw";
    else:
        raise BaseException( "ERR: abcdk.chat.constructUsingAccount: you should pre-configurate your password!" );
        return None;
    return Gtalk( strName, strPwd );
# constructUsingAccount - end    

def gtalk_autotest():
    talk = constructUsingAccount( "naoalex16" );
    talk.getConnected();
    amazel = "amazel@aldebaran-robotics.com";
    zelma = "alexandre.zelma@gmail.com";
    talk.sendMessage( "coucou, ca boume? grave ?",  zelma );
    print( "gtalk_autotest: waiting for potential message..." );
    while( True ):
        retVal = talk.update();
        if( retVal == None ):
            continue;
        strMessage, strSender = retVal;
        if( "et toi ?" in strMessage ):
            talk.sendMessage( "carrément !", strSender );
# gtalk_autotest - end    

if __name__ == "__main__":
    gtalk_autotest();