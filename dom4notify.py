#!/usr/bin/env python
# This file is part of dom4notify. dom4notify is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Andreas Winker 2014

import pyinotify
import subprocess
import sys
import os
import sleekxmpp
import logging

#logging.basicConfig(level=logging.DEBUG)

#FB ACCOUNT INFO
jid = 'username'
password = 'password'

#GAME OPTIONS

#Set game executable and savegame directories
gexecdir = "game exec dir"
sgamedir = "savedgames exec dir"

#Set game options
dgame = "Test_map"
dplayers = "1"
dmap = "silentseas.map"
dera = "1"
dhof = "10"
dind = "5"
dtoa = "5 0 0"
drtoa = "5"
dport = "port"
dip = "ip"

#START GAME

doptions = " -g " + dgame + " --uploadmaxp " + dplayers + " --mapfile " + dmap + " --era " + dera + " --hofsize " + dhof + " --indepstr " + dind + " --thrones " + dtoa + " --requiredap " + drtoa + " --port " + dport

gameinit =  gexecdir + " -S -T --nonationsel --noclientstart" + doptions

subprocess.Popen(gameinit, stdout=subprocess.PIPE, shell=True)

#MESSAGE BOT
class SendMsgBot(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, recipient, message):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.recipient = recipient
        self.msg = message
        self.add_event_handler("session_start", self.start, threaded=True)

    def start(self, event):
        self.send_presence()
        self.get_roster()
        self.send_message(mto=self.recipient,
        mbody=self.msg,
        mtype='chat')
        self.disconnect(wait=True)

#NEW GAME MESSAGE
if not os.path.isdir(sgamedir + dgame):

	#Query Game Server
	gamestate = subprocess.Popen(gexecdir + " --tcpquery" + " --ipadr " + dip + " --port " + dport, stdout=subprocess.PIPE, shell=True)
	(output, error) = gamestate.communicate()

	#Check Game Name
	for cname in output.split(u"\n"):
		if "Gamename" in cname:
			gamename = cname.strip()

	#Check Game Status
	for cstatus in output.split(u"\n"):
		if "Status" in cstatus:
			status = cstatus.strip()

	#If game is waiting for players
	for waiting in output.split(u"\n"):
		if "Waiting" in waiting:
			msg = gamename[10:] + "\n" + "-" + "\n" + "Select Pretender" 

	#Player List
	players = open(dgame + ".txt", "r")
	to = players.readlines()
	players.close()

	#Send Message
	for pnumber in to:
		xmpp = SendMsgBot(jid, password, pnumber, unicode(msg))

		#FB APP SUPPORT
		#xmpp.credentials['api_key'] = ''
		#xmpp.credentials['access_token'] = ''

		if xmpp.connect(('chat.facebook.com', 5222)):
		    xmpp.process(block=True)
		    #print("Done")
		else:
		    print("Unable to connect.")

#EVENTHANDLER

wm = pyinotify.WatchManager() # Watch Manager
mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_CLOSE_WRITE # Watched Events

class EventHandler(pyinotify.ProcessEvent):

     def process_IN_CLOSE_WRITE(self, event):
	suffix = "ftherlnd"	
	if event.pathname.endswith(suffix):

		#MESSAGE SENDING
	
		#Query Game Server
		gamestate = subprocess.Popen(gexecdir + " --tcpquery" + " --ipadr " + dip + " --port " + dport, stdout=subprocess.PIPE, shell=True)
		(output, error) = gamestate.communicate()

		#Check Game Name
		for cname in output.split(u"\n"):
			if "Gamename" in cname:
				gamename = cname.strip()

		#Check Game Status
		for cstatus in output.split(u"\n"):
			if "Status" in cstatus:
				status = cstatus.strip()

		#Check Turn Number
		for turn in output.split(u"\n"):
			if "Turn" in turn:
				msg = gamename[10:] + "\n" + "-" + "\n" + turn.strip()

		#Player List
		players = open(dgame + ".txt", "r")
		to = players.readlines()
		players.close()

		#Send Message
		for pnumber in to:
			xmpp = SendMsgBot(jid, password, pnumber, unicode(msg))

			#FB APP SUPPORT
			#xmpp.credentials['api_key'] = ''
			#xmpp.credentials['access_token'] = ''

			if xmpp.connect(('chat.facebook.com', 5222)):
			    xmpp.process(block=True)
			    #print("Done")
			else:
			    print("Unable to connect.")

handler = EventHandler()
notifier = pyinotify.Notifier(wm, handler)
wdd = wm.add_watch(sgamedir, mask, rec=True, auto_add=True)

notifier.loop()
