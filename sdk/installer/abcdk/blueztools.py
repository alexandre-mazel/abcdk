# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Bluez tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################


"""Tools to use bluez and work with BlueTooth."""

"""
    WARNING:
    WARNING:
    WARNING:
    WARNING: the method used is very UGLY: system call and using external patched shell script
    WARNING:
    WARNING:
    WARNING:
"""



print( "importing abcdk.blueztools" );

import gobject

import dbus
import dbus.mainloop.glib
import os
import time

import abcdk.naoqitools as naoqitools
import abcdk.pathtools as pathtools
import abcdk.stringtools as stringtools
import abcdk.system as system


def create_device_reply(device):
	print "create_device_reply: New device (%s)" % device	
	mainloop = gobject.MainLoop();    
	mainloop.quit()
	print "create_device_reply: ended";

def create_device_error(error):
	print "create_device_error: Creating device failed: %s" % error
	mainloop = gobject.MainLoop();
	mainloop.quit()
	print "create_device_error: ended";
    
class BlueToothToSerial():
    "An object to associate some Bluetooth device to a serial device"
    def __init__( self, strName, strPinCode = "1234" ):
        self.strName = strName; # the human name, eg: "ARDUINOBT"
        self.strMAC = "";
        self.strPinCode = strPinCode;
        self.node = False; # the dbus link object      
        self.nRetryPairing = 0;
        self.lastTimeInformUser = time.time() - 10000;
    # __init__ - end
    
    def askUserToTurnOnHisDevice( self ):
        if( time.time() - self.lastTimeInformUser < 10. ):
            return; # don't do nothing, the device is again on
        self.lastTimeInformUser = time.time();
        tts = naoqitools.myGetProxy( "ALTextToSpeech" );
        if( tts.getLanguage() == 'French' ):
            strMsg = "Allume ton appareil maintenant!";
        else:
            strMsg = "Turn your device on, now!";
        tts.say( strMsg );
    # askUserToTurnOnHisDevice - end
    
    def __discoverAndFindDevice__( self, strName ): # const
        "find the mac of some device, even if not paired"
        "return '' if not found"
        print( "INF: __discoverAndFindDevice__: begin" );
        ret = system.executeAndGrabOutput( "python %s/bluez_test_discovery_find.py --find %s 2>>/dev/null" % (pathtools.getABCDK_Path(), self.strName) );
        ret = stringtools.textToLines( ret );
        print( "ret: %s " % ret );
        print( "INF: __discoverAndFindDevice__: after call" );
        if( len( ret ) < 2 ):
            print( "ERR: __discoverAndFindDevice__: device '%s' not discovered" % strName );
            return "";
        return ret[1];
    # __discoverAndFindDevice__ - end
        
    def __pairRemoteDevice__(self):
        print( "INF: __pairRemoteDevice__: begin" );
        self.strMAC = self.__discoverAndFindDevice__(self.strName);
        if( self.strMAC == "" ):
            print( "INF: __pairRemoteDevice__: end without pairing" );
            return False;
        #~ import serial_simple_agent_patch_auto_pin_code
        #~ reload( serial_simple_agent_patch_auto_pin_code )
        #~ serial_simple_agent_patch_auto_pin_code.launchLoop( self.strPinCode );
        runningAgent = system.mySystemCall( "python %s/bluez_simple_agent_patch_auto_pin_code.py %s &" % ( pathtools.getABCDK_Path(), self.strPinCode ), bWaitEnd = False, bStoppable = True );
        time.sleep( 1.0 );
        self.askUserToTurnOnHisDevice();
        print( "INF: __pairRemoteDevice__: *** TURN YOU DEVICE '%s' ON, NOW !!! **************************************************************" % self.strMAC );
        print( "INF: ___pairRemoteDevice__: creating device for mac: '%s'" % self.strMAC );
        system.mySystemCall( "bluez-test-device create %s" % self.strMAC );
        #~ print( "AA" );
        #~ dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        #~ bus = dbus.SystemBus()
        #~ print( "AA2" );
        #~ mainloop = gobject.MainLoop()
        #~ print( "BB" );
        #~ manager = dbus.Interface(bus.get_object("org.bluez", "/"), "org.bluez.Manager")
        #~ adapter_path = manager.DefaultAdapter()
        #~ print( "CC" );
        #~ adapter = dbus.Interface(bus.get_object("org.bluez", adapter_path), "org.bluez.Adapter")
        
        #~ print( "*** TURN YOU DEVICE ON, NOW !!! **************************************************************" );
        #~ time.sleep( 0.5 );
        #~ print( "__pairRemoteDevice__: Creating device" );
        #~ adapter.CreateDevice( "00:07:80:51:10:73", reply_handler=create_device_reply, error_handler=create_device_error ); #TODO: la bonne mac!
        #~ print( "__pairRemoteDevice__: mainloop running" );
        #~ mainloop.run(); # todo: found the step present in simpleagent and bluez-test-device (but I need to found how to forget remote device, first :) )
        print( "INF: ___pairRemoteDevice__: end" );
        runningAgent.stop(); # try to stop the agent turning in background # In case of error, one script per failure continue to run, but once a pairing is succeed all will be destroyed
        return True;
    # __pairRemoteDevice__ - end
    
    def create( self ):
        "create the link, return it's name or False on error"
        print( "INF: BlueToothToSerial: Creating a serial link for '%s'" % self.strName );
        bus = dbus.SystemBus();
        manager = dbus.Interface( bus.get_object("org.bluez", "/"), "org.bluez.Manager" );
        print( "2" );
        try:
            adapter_path = manager.DefaultAdapter();
        except BaseException, err:
            print( "ERR: BlueToothToSerial: error no adapter found (forget to plug your BT in the NAO's head?) err: %s" % err );
            self.node = False;
            return False;            
        print( "2n" );
        adapter = dbus.Interface( bus.get_object("org.bluez", adapter_path), "org.bluez.Adapter");

        # find the mac of the device
        self.strMAC = "";
        for path in adapter.ListDevices():
            device = dbus.Interface(bus.get_object("org.bluez", path), "org.bluez.Device");
            properties = device.GetProperties();
            print( "DBG: BlueToothToSerial: Enumerating device(s): %s: %s" % (properties["Alias"], properties["Address"]) );
            if( self.strName == properties["Alias"] ):                
                self.strMAC = properties["Address"];
                break;
        if( self.strMAC == "" ):
            print( "ERR: BlueToothToSerial: can't find an adapter with the name '%s'" % self.strName );
            # trying to pair it first
            if( self.nRetryPairing < 5 ):
                self.nRetryPairing += 1;
                self.__pairRemoteDevice__();
                return self.create();            
            return False;
        
        print( "INF: BlueToothToSerial: Creating a serial link for '%s' with mac '%s'" % ( self.strName, self.strMAC ) );
        
        service = "spp";
        print( "3" );
        path = adapter.FindDevice( self.strMAC )
        print( "4" );
        self.serial = dbus.Interface( bus.get_object("org.bluez", path), "org.bluez.Serial" );
        print( "5" );
        self.askUserToTurnOnHisDevice();
        try:
            self.node = self.serial.Connect( service );
        except BaseException, err:
            print( "ERR: BlueToothToSerial: error connecting: %s" % err );
            self.node = False;
            return False;
        print( "6" );
        print( "INF: BlueToothToSerial: Connected: %s <==> %s" % ( self.strMAC, self.node ) );
        return str( self.node );
    # create - end
    
    def getConnectedPort( self ):
        "return the current connected port or False, if no port"
        return str( self.node );
    # getConnectedPort - end
    
    def __del__(self):
        print( "INF: BlueToothToSerial: Destroying the serial link for '%s' with mac '%s'" % ( self.strName, self.strMAC ) );
        if( self.node != False ):
            print( "INF: BlueToothToSerial: Destroying..." );    
            self.serial.Disconnect( self.node );
            self.node = False;
        print( "INF: BlueToothToSerial: Destroyed!" );
    # __del__ - end
    
# class BlueToothToSerial - end

def isBluetoothAdapterPresent():
    "Is there a bluetooth adapter (dongle) in the nao's head"
    "create the link, return it's name or False on error"
    "just an information for the user, it's not mandatory to call this method before trying to create link"
    print( "INF: BluezTools.isBluetoothAdapter: begin" );
    bus = dbus.SystemBus();
    manager = dbus.Interface( bus.get_object("org.bluez", "/"), "org.bluez.Manager" );
    try:
        adapter_path = manager.DefaultAdapter();
    except BaseException, err:
        print( "INF: BluezTools.isBluetoothAdapter: error no adapter found (forget to plug your BT in the NAO's head?) err: %s" % err );
        return False;            
    return True;
# isBluetoothAdapterPresent - end

def removeAssociation( strName ):
    "Remove an association with a remote device"
    "Return true if ok, false elsewhere"
    bus = dbus.SystemBus();
    manager = dbus.Interface( bus.get_object("org.bluez", "/"), "org.bluez.Manager" );
    print( "2" );
    try:
        adapter_path = manager.DefaultAdapter();
    except BaseException, err:
        print( "ERR: removeAssociation: error no adapter found (forget to plug your BT in the NAO's head? err: %s" % err );
        return False;            
    print( "2n" );
    adapter = dbus.Interface( bus.get_object("org.bluez", adapter_path), "org.bluez.Adapter");

    # find the mac of the device
    strMAC = "";
    for path in adapter.ListDevices():
        device = dbus.Interface(bus.get_object("org.bluez", path), "org.bluez.Device");
        properties = device.GetProperties();
        print( "DBG: removeAssociation: Enumerating device(s): %s: %s" % (properties["Alias"], properties["Address"]) );
        if( strName == properties["Alias"] ):                
            strMAC = properties["Address"];
            break;
    if( strMAC == "" ):
        print( "ERR: removeAssociation: can't find an adapter with the name '%s'" % strName );
        return False;
    
    # system.mySystemCall( "bluez-test-device remove %s" % strMAC );    
    print( "INF: removeAssociation: removing '%s'..." % strMAC );
    path = adapter.FindDevice(strMAC);
    adapter.RemoveDevice(path);
    print( "INF: removeAssociation: done!" );
    return True;
# removeAssociation - end

def autoTest():
    pass
        
pass