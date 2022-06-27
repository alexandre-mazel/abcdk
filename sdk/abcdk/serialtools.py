# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Serial tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################


"""Tools to work with serial port."""


print( "importing abcdk.serialtools" );

import serial # http://pyserial.sourceforge.net/
import time

import debug
import system

#~ ser = serial.Serial(13)
#~ print ser.portstr       # check which port was really used
#~ ser.write("hello");      # write a string
#~ ser.close();

class SerialTools():
    """
    Send and receive data in a specific way:
        ["dataname",value]\n  a pair [data,value], the value can be an integer, a float, a string, an array, an array of int, value, string, array...
        #blablabla\n            a comments, it will only been printed in the console.
        \n can be replaced by the two char: RN
    """
    
    def __init__( self, portNameOrNumber, nBaudRate, timeout, parity = serial.PARITY_NONE, rtscts = 0 ): # not sure about the rtscts default value
        """portNameOrNumber: the name of the port to open, it could be:
            - an explicit name, 
            - "" or "(autodetect)"
            - a word with some wildcard, eg: "ttyUSB*", it would then try to open ttyUSB0, ttyUSB1, ...
        """
        
        self.portNameOrNumber = portNameOrNumber;
        self.strAutoDetectAtOpenWithWildCards = "";
        self.bAutoDetectAtOpen = False;        
        if( "*" in portNameOrNumber ):
            self.strAutoDetectAtOpenWithWildCards = portNameOrNumber.replace( "*", "" );
            self.bAutoDetectAtOpen = True;
        elif( portNameOrNumber == "" or portNameOrNumber == "(autodetect)" ):
            self.bAutoDetectAtOpen = True;
        self.nBaudRate = nBaudRate;
        self.timeout = timeout;
        self.parity = parity;
        self.rtscts = rtscts;
        self.serial = False; # means closed
        self.timeLastOpenRetry = time.time() - 10000;
        self.bUserWantToOpen = False; # to prevent system to reopen automatically the port if user don't explicitly open it.
    # __init__ - end
        
    def __del__( self ):
        if( self.serial != False ):
            self.serial.close();
    # __del__ - end
    
    def open( self ):
        # return True when opening has succeed
        print( "INF: SerialTools.open: opening port..." );
        self.bUserWantToOpen = True;
        return self.__open();
    # open - end
        
        
    def __open( self ):
        # return True when opening has succeed
        print( "INF: SerialTools.__open: opening port" );
        if( self.bAutoDetectAtOpen ):
            listPort, listNew = system.findExternalPort( strFilter = self.strAutoDetectAtOpenWithWildCards );
            if( len( listNew ) > 0 ):
                self.portNameOrNumber = listNew[0];
            elif( len( listPort ) > 0 ):
                self.portNameOrNumber = listPort[0]; # we should try it as a loop
            else:
                pass # by default we let the current stuff, we pray for it has been set recently or ... (in the worst case, it's bullshit, and the opening will fail...)
            print( "INF: SerialTools.__open: Autodetecting port: using '%s'" % self.portNameOrNumber );
        try:
            self.serial = serial.Serial( self.portNameOrNumber, self.nBaudRate, timeout = self.timeout, parity = self.parity );      # rtscts = self.rtscts
        except BaseException, err:
            print( "ERR: SerialTools.__open: FAILURE: %s" % str( err ) );
            if( self.serial != False ): # never
                self.serial.close(); # just in case
            self.serial = False; # just in case
            return False;
        print( "INF: SerialTools.__open: SUCCEED: opened '%s'" % self.serial.portstr );
        return True;
    # __open - end
    
    def close( self ):
        self.bUserWantToOpen = False;
        print( "INF: SerialTools.close: closing..." );
        self.__close();
        print( "INF: SerialTools.close: closed..." );
    # close - end
    
    def __close( self ):
        # internal closing
        print( "INF: SerialTools.__close: closing..." );
        if( self.serial != False ):
            self.serial.close();
            self.serial = False;
        print( "INF: SerialTools.__close: closed..." );
    # close - end    
    
    def handleCommunicationError(self):
        # handle error (peripheric has disappear, so we try to reopen it after a while)
        if( self.bUserWantToOpen and time.time() - self.timeLastOpenRetry > 5. ):
             # every 5 seconds, we retry to reopen it
             print( "INF: SerialTools.handleCommunicationError: trying to reopen the port!" );
             self.__close();
             self.__open();
             self.timeLastOpenRetry = time.time();
    # handleCommunicationError - end
    
    def sendComments( self, strMsg ):
        "strMsg is without EOL \n"
        "Return True if ok"
        if( self.serial == False ):
            print( "ERR: SerialTools.sendComments: port not open" );
            self.handleCommunicationError();
            return False;
        print( "INF: SerialTools.sendComments: sending comments: '%s'" % str( strMsg ) );
        try:
            self.serial.write( "#" + unicode( strMsg + '\r\n') );
        except BaseException, err:
            print( "ERR: Serialtools.sendComments: error while sending, skipping for a while, err: %s" % str( err ) );
            self.handleCommunicationError();
            return False;        
            
        return True;
    # sendComments - end
    
    def sendData( self, strDataName, value ):
        "strDataName is without EOL \n"
        "value a python object"
        "Return True if ok"
        if( self.serial == False ):
            print( "ERR: SerialTools.sendComments: port not open" );
            self.handleCommunicationError();
            return False;
        strData = str( value );
        print( "INF: SerialTools.sendComments: sending data: '%s', value: %s" % ( strDataName, strData ) );
        try:
            self.serial.write( "[\"%s\",%s]\r\n" % ( strDataName, strData ) );
        except BaseException, err:
            print( "ERR: Serialtools.sendData: error while sending, skipping for a while, err: %s" % str( err ) );
            self.handleCommunicationError();
            return False;        
        return True;
    # sendData - end
    
    def getRawData( self, nMaxData = 1024*8, nTimeOut = 4 ):
        "get raw data from serial"
        "nTimeOut: time out while waiting for data (-1 for no timeout)"
        "Return raw data or False on error or '' if no data before timeout"
        if( self.serial == False ):
            print( "ERR: SerialTools.getData: port not open" );
            self.handleCommunicationError();
            return False;
        try:
            self.serial.timeout = nTimeOut;
        except BaseException, err:
            print( "ERR: Serialtools.getData: error while parametring, skipping for a while, err: %s" % str( err ) );
            self.handleCommunicationError();
            return False;            
        nBeginTime = time.time();
        s = "";
        nLen = 0;
        while( True ):
            try:
                data = self.serial.read(16);
            except BaseException, err:
                print( "ERR: Serialtools.getData: error while reading, skipping for a while, err: %s" % str( err ) );
                self.handleCommunicationError();
                return False;
            if( data == "" ):
                return s; # timeout
            s += data;
            nLen += len( data );
            if( time.time() - nBeginTime >= nTimeOut or nLen >= nMaxData ):
                return s;
        # while - end
        # never goes here
    # getData - end    
    
    def getData( self, nTimeOut = 4 ):
        "get data in a well wrotten format"
        "nTimeOut: time out while waiting for data (-1 for no timeout)"
        "Return a pair [dataName, value]"
        "Return False on error or if no data before timeout"
        if( self.serial == False ):
            print( "ERR: SerialTools.getData: port not open" );
            self.handleCommunicationError();
            return False;
        try:
            self.serial.timeout = nTimeOut;
        except BaseException, err:
            print( "ERR: Serialtools.getData: error while parametring, skipping for a while, err: %s" % str( err ) );
            self.handleCommunicationError();
            return False;            
        nBeginTime = time.time();
        while( True ):
            try:
                s = self.serial.readline();
            except BaseException, err:
                print( "ERR: Serialtools.getData: error while reading, skipping for a while, err: %s" % str( err ) );
                self.handleCommunicationError();
                return False;
            if( s == "" ):
                return False; # timeout
            # remove eol
            s = s[:-2];            
            if( s[0] == '#' ):
                print( "DBG: SerialTools.getData: comments: '%s'" % str( s[1:] ) );
            elif( s[0] == '[' ):
                try:
                    print( "INF: SerialTools.getData: data: '%s'" % str( s ) );
                    return eval(s); # convert "["toto", 13]" in the array object ["toto", 13]
                except BaseException, err:
                    print( "ERR: while evaluating data information '%s', err: %s" % ( s, str( err ) ) ); # often when launching the behavior, we could receive some end of message, so it is bad formatted.
            else:
                print( "WRN: SerialTools.getData: unknown data type received: %s" % debug.dumpHexa( s ) );
            if( time.time() - nBeginTime >= nTimeOut ):
                return False;
    # getData - end
# class SerialTools - end

def autoTest():
#    import serial.tools.list_ports
#    serial.tools.list_ports.main()

    st = SerialTools( 12, 115200, timeout=4 ); # 12 # "/dev/rfcomm1"
    st.open();
    st.sendComments( "coucou" ); # #coucouRN
    st.sendData( "Buzzer", [440,1000] ); # ["Buzzer",[440,1000]]RN
    st.sendData( "Led1", 1 ); # ["Led1",255]RN
    st.sendData( "Motor", 10 ); # ["Motor",10]RN
    for i in range( 10 ):
        s = st.getData( 10 );
        print( "s: '%s'" % str( s ) );
    
    
#~ print( "opening..." );
#~ ser = serial.Serial(12, 15200, timeout=4);
#~ print ser.portstr;
#~ print( "reading..." );
#~ s = ser.readline();
#~ print( "s: '%s'" % str( s ) );
#~ print( "closing..." );
#~ ser.close();