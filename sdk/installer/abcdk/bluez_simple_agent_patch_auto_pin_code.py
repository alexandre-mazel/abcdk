#!/usr/bin/python

import gobject

import sys
import dbus
import dbus.service
import dbus.mainloop.glib

class Rejected(dbus.DBusException):
	_dbus_error_name = "org.bluez.Error.Rejected"

class Agent(dbus.service.Object):
	exit_on_release = True

	def set_exit_on_release(self, exit_on_release):
		self.exit_on_release = exit_on_release

	@dbus.service.method("org.bluez.Agent",
					in_signature="", out_signature="")
	def Release(self):
		print "Release"
		if self.exit_on_release:
			mainloop.quit()

	@dbus.service.method("org.bluez.Agent",
					in_signature="os", out_signature="")
	def Authorize(self, device, uuid):
		print "Authorize (%s, %s)" % (device, uuid)
		authorize = raw_input("Authorize connection (yes/no): ")
		if (authorize == "yes"):
			return
		raise Rejected("Connection rejected by user")

	@dbus.service.method("org.bluez.Agent",
					in_signature="o", out_signature="s")
	def RequestPinCode(self, device):
		print "RequestPinCode (%s)" % (device)
		# return raw_input("Enter PIN Code: ")
		# Alma 12-06-28: modification to have an auto pin code
		global global_strPinCode;
		print( "Using pin code: '%s'" % global_strPinCode );
		mainloop.quit()
		return global_strPinCode;

	@dbus.service.method("org.bluez.Agent",
					in_signature="o", out_signature="u")
	def RequestPasskey(self, device):
		print "RequestPasskey (%s)" % (device)
		passkey = raw_input("Enter passkey: ")
		return dbus.UInt32(passkey)

	@dbus.service.method("org.bluez.Agent",
					in_signature="ou", out_signature="")
	def DisplayPasskey(self, device, passkey):
		print "DisplayPasskey (%s, %d)" % (device, passkey)

	@dbus.service.method("org.bluez.Agent",
					in_signature="ou", out_signature="")
	def RequestConfirmation(self, device, passkey):
		print "RequestConfirmation (%s, %d)" % (device, passkey)
		confirm = raw_input("Confirm passkey (yes/no): ")
		if (confirm == "yes"):
			return
		raise Rejected("Passkey doesn't match")

	@dbus.service.method("org.bluez.Agent",
					in_signature="s", out_signature="")
	def ConfirmModeChange(self, mode):
		print "ConfirmModeChange (%s)" % (mode)
		authorize = raw_input("Authorize mode change (yes/no): ")
		if (authorize == "yes"):
			return
		raise Rejected("Mode change by user")

	@dbus.service.method("org.bluez.Agent",
					in_signature="", out_signature="")
	def Cancel(self):
		print "Cancel"

def create_device_reply(device):
	print "New device (%s)" % (device)
	mainloop.quit()

def create_device_error(error):
	print "Creating device failed: %s" % (error)
	mainloop.quit()


global global_strPinCode;

if __name__ == '__main__':
	
	# Alma 12-06-28: pop first params:
	print( "*** serial_simple_agent_patch_auto_pin_code.py - begin" );
	global_strPinCode = sys.argv.pop();
	
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

	bus = dbus.SystemBus()
	manager = dbus.Interface(bus.get_object("org.bluez", "/"),
							"org.bluez.Manager")

	if len(sys.argv) > 1:
		path = manager.FindAdapter(sys.argv[1])
	else:
		path = manager.DefaultAdapter()

	adapter = dbus.Interface(bus.get_object("org.bluez", path),
							"org.bluez.Adapter")

	path = "/test/agent"
	agent = Agent(bus, path)

	mainloop = gobject.MainLoop()

	if len(sys.argv) > 2:
		if len(sys.argv) > 3:
			device = adapter.FindDevice(sys.argv[2])
			adapter.RemoveDevice(device)

		agent.set_exit_on_release(False)
		adapter.CreatePairedDevice(sys.argv[2], path, "DisplayYesNo",
					reply_handler=create_device_reply,
					error_handler=create_device_error)
	else:
		adapter.RegisterAgent(path, "DisplayYesNo")
		print "Agent registered"

	mainloop.run()

	#adapter.UnregisterAgent(path)
	#print "Agent unregistered"

	print( "*** serial_simple_agent_patch_auto_pin_code.py - end" );
# D:\Dev\git\appu_shared\sdk>scp -pw nao abcdk\serial*.py nao@10.0.253.75:/home/nao/.local/lib/python2.6/site-packages/abcdk/