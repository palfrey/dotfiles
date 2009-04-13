import dbus, os
# Get the ConsoleKit manager
bus = dbus.SystemBus()
manager_obj = bus.get_object('org.freedesktop.ConsoleKit', '/org/freedesktop/ConsoleKit/Manager')
manager = dbus.Interface(manager_obj, 'org.freedesktop.ConsoleKit.Manager')

# For each of my sessions..
for ssid in manager.GetSessionsForUnixUser(os.getuid()):
	obj = bus.get_object('org.freedesktop.ConsoleKit', ssid)
	session = dbus.Interface(obj, 'org.freedesktop.ConsoleKit.Session')
	# Get the X11 display name
	dpy = session.GetX11Display()
	if dpy:
		print "dpy",dpy
		# If we have a display, set the environment variable
		#os.putenv("DISPLAY", dpy);
		break
