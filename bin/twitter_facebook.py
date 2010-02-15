#!/usr/bin/python
from facebook import Facebook
from pickle import dump,load
from urllib2 import *
from xml.dom.minidom import parse
from time import sleep,localtime,strftime

# Get api_key and secret_key from a file
fbs = open('facebook_keys.txt').readlines()
facebook = Facebook(fbs[0].strip(), fbs[1].strip())

while True:
	print strftime("%a, %d %b %Y %H:%M:%S", localtime())
	try:
		session = load(file(".session"))
		print session
		facebook.secret = session['secret']
		facebook.session_key = session['session_key']
		facebook.session_key_expires = session['expires']
		facebook.uid = session['uid']
	except (EOFError,IOError):
		token = facebook.auth.createToken()
		print "token",facebook.auth._client.auth_token
		# Show login window
		facebook.login()

		# Login to the window, then press enter
		print 'After logging in, press enter...'
		raw_input()
		res = facebook.auth.getSession()
		dump(res,file(".session","w"))

	try:
		data = parse(urlopen("http://twitter.com/statuses/user_timeline/palfrey.xml"))

		laststatus = data.getElementsByTagName("text")[0].firstChild.data

		status = facebook.fql.query("select status from user where uid=%s"%facebook.uid)[0]['status']['message']
		if len(status)>140:
			status = status[:136]+" ..."
		print "status '%s'"%status,len(status)
		print "last '%s'"%laststatus,len(laststatus)
		if status!=laststatus:
			print "updating twitter"
			passwds = HTTPPasswordMgrWithDefaultRealm()
			passwds.add_password(None,"http://twitter.com/statuses/update.xml","palfrey","epsilon")
			opener = build_opener(HTTPBasicAuthHandler(passwds))
			opener.open("http://twitter.com/statuses/update.xml","status=%s"%status)
		else:
			print "status == last status, no update"
	except HTTPError,e:
		print "Error",e
		sleep(60) # 1 minute before retry
		continue
	except Exception,e:
		print "Non-http Error",e
		sleep(60) # 1 minute before retry
		continue
	print "sleeping"
	sleep(10*60) # 10 minutes

