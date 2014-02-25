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

#ver 0.2

import pyinotify
import subprocess
import sys
import os
import sleekxmpp
import logging
import time

#FB ACCOUNT INFO
jid = ""
password = ""

#GAME OPTIONS

#Set game executable and savegame directories
gexecdir = ""
sgamedir = ""

#Logging
logging.basicConfig(filename=sgamedir + "logfile.log",level=logging.DEBUG)

#Set game options
dgame = "Test_map"
dplayers = "2"
dmap = "silentseas.map"
dera = "1"
dhof = "10"
dind = "5"
dtoa = "5 0 0"
drtoa = "5"
dport = "40000"
dip = "127.0.0.1"

#START GAME

doptions = " -g " + dgame + " --uploadmaxp " + dplayers + " --mapfile " + dmap + " --era " + dera + " --hofsize " + dhof + " --indepstr " + dind + " --thrones " + dtoa + " --requiredap " + drtoa + " --port " + dport

gameinit =  gexecdir + "dom4.sh -S -T --nonationsel --noclientstart" + doptions

subprocess.Popen(gameinit, stdout=subprocess.PIPE, shell=True)

#MESSAGE BOT
class SendMsgBot(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, recipient, message):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.recipient = recipient
        self.msg = message
        self.add_event_handler("session_start", self.start, threaded=True)

    def start(self, event):
        for self.pnumber in self.recipient:
            self.send_message(mto=self.pnumber, mbody=self.msg, mtype='chat')
            time.sleep(1)
        self.disconnect(wait=False)

#NEW GAME MESSAGE
if not os.path.isdir(sgamedir + dgame):

    #Query Game Server
    gamestate = subprocess.Popen(gexecdir + "dom4.sh --tcpquery --ipadr " + dip + " --port " + dport, stdout=subprocess.PIPE, shell=True)
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
            msg = gamename[10:] + "\n" + "-" + "\n" + "Select Pretenders"

    #Player List
    players = open(sgamedir + dgame + ".txt", "r")
    to = list(players.readlines())
    players.close()

    #Send Message
    xmpp = SendMsgBot(jid, password, to, unicode(msg))

    #FB APP SUPPORT
    #xmpp.credentials['api_key'] = ''
    #xmpp.credentials['access_token'] = ''

    if xmpp.connect(('chat.facebook.com', 5222)):
        xmpp.process(block=True)
    else:
        print("Unable to connect.")

#EVENTHANDLER

wm = pyinotify.WatchManager() # Watch Manager
mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_CLOSE_WRITE # Watched Events

class EventHandler(pyinotify.ProcessEvent):

    def process_IN_CLOSE_WRITE(self, event):

        suffix = dgame + "/ftherlnd"

        if event.pathname.endswith(suffix):

            #MESSAGE SENDING

            #Query Game Server
            gamestate = subprocess.Popen(gexecdir + "dom4.sh --tcpquery" + " --ipadr " + dip + " --port " + dport, stdout=subprocess.PIPE, shell=True)
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
            players = open(sgamedir + dgame + ".txt", "r")
            to = list(players.readlines())
            players.close()

            #Send Message
            xmpp = SendMsgBot(jid, password, to, unicode(msg))

            #FB APP SUPPORT
            #xmpp.credentials['api_key'] = ''
            #xmpp.credentials['access_token'] = ''

            if xmpp.connect(('chat.facebook.com', 5222)):
                xmpp.process(block=True)
            else:
                print("Unable to connect.")

handler = EventHandler()
notifier = pyinotify.Notifier(wm, handler)
wdd = wm.add_watch(sgamedir, mask, rec=True, auto_add=True)

notifier.loop()
