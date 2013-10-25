###########################################################################
# Copyright (c) 2011-2013 Unixmedia S.r.l. <info@unixmedia.it>
# Copyright (c) 2011-2013 Franco (nextime) Lanza <franco@unixmedia.it>
#
# Domotika System Controller Daemon "domotikad"  [http://trac.unixmedia.it]
#
# This file is part of domotikad.
#
# domotikad is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import sys

from OpenSSL.SSL import SSLv3_METHOD

from twisted.mail.smtp import ESMTPSenderFactory
from twisted.python.usage import Options, UsageError
from twisted.internet.ssl import ClientContextFactory
from twisted.internet import defer 
from twisted.internet import reactor
from email.mime.text import MIMEText
from domotika.db import dmdb
from cStringIO import StringIO
import logging

log = logging.getLogger( 'Mail' )


class DMEmail(object):

   needauth=False
   username=None
   password=None
   server="127.0.0.1"
   port=25
   tls=False
   sender="Domotika By Unixmedia <domotika@unixmedia.it>"
   to=False
   tolist=[]
   subject="This is an email from Domotika"
   cc=False
   bc=False
   message="This is a message from Domotika"


   #def __init__(self):
   #   pass

   def setFrom(self, senderAddress):
      self.sender = senderAddress

   def getFrom(self):
      return self.sender

   def setTo(self, toAddresses):
      self.tolist = toAddresses
      self.to=",".join(toAddresses)

   def getTo(self):
      return self.tolist

   def setCc(self, ccAddresses):
      self.cclist = ccAddresses
      self.cc=",".join(ccAddresses)

   def setSubject(self, subject):
      self.subject = subject

   def setMessage(self, message):
      self.message = message

   def setUsername(self, username):
      self.username = username

   def setPassword(self, password):
      self.password = password

   def setServer(self, server, port=25):
      self.server = server
      self.port = port

   def needAuth(self, need=True):
      self.needauth = need

   def needTls(self, tls=True):
      self.tls = tls

   def end(r):
      try:
         self.reactor.disconnect()
      except:
         pass
      return 'OK'

   def send(self, usemime=True):
      log.info("Sending email from "+str(self.sender)+" to "+str(self.to)+" with subject "+str(self.subject))
      contextFactory = ClientContextFactory()
      contextFactory.method = SSLv3_METHOD
         
      if usemime:
         msg = MIMEText(self.message)
         msg["Subject"] = self.subject
         msg["From"] = self.sender
         msg["To"] = self.to
         msgstring = msg.as_string()
      else:
         msgstring = self.message

      d = defer.Deferred()
      senderFactory = ESMTPSenderFactory(
         self.username,
         self.password,
         self.sender.split()[-1],
         self.tolist,
         StringIO(msgstring),
         d,
         contextFactory=contextFactory,
         requireAuthentication=self.needauth,
         requireTransportSecurity=self.tls
      )

      self.reactor = reactor.connectTCP(self.server, self.port, senderFactory)
      return d.addCallbacks(self.end)


def _realSendMime(ser, res):
   if ser:
      for s in ser:
         e=DMEmail()
         e.setServer(s.server, s.port)
         e.setUsername(s.username)
         e.setPassword(s.password)
         if s.use_auth=='true':
            e.needAuth(True)
         else:
            e.needAuth(False)
         if s.use_tls=='true':
            e.needTls(True)
         else:
            e.needTls(False)
         for m in res:
            e.setFrom(m.sender)
            e.setTo(m.to.split(','))
            e.setSubject(m.subject)
            e.setMessage(m.message)
            e.send()

def _sendEmailMime(res):
   if res:
      dmdb.EmailConf.find().addCallback(_realSendMime, res)

def _realSendMail(ser, sender, recipient, message):
   if ser:
      e=DMEmail()
      e.setFrom(sender)
      e.setTo(recipient.split(','))
      e.setMessage(message)
      
      for s in ser:
         e.setServer(s.server, s.port)
         e.setUsername(s.username)
         e.setPassword(s.password)
         if s.use_auth=='true':
            e.needAuth(True)
         else:
            e.needAuth(False)
         if s.use_tls=='true':
            e.needTls(True)
         else:
            e.needTls(False)
         d=e.send(usemime=False)
      return d
   return defer.fail('Cannot send email: no server configured')

def sendMail(sender, recipient, message):
   return dmdb.EmailConf.find().addCallback(_realSendMail, sender, recipient, message)


def sendEmailByName(name):
   dmdb.Email.find(where=["name=?", name]).addCallback(_sendEmailMime)


def sendEmailById(mailid):
   dbdb.Email.find(where=["id=?", mailid]).addCallback(_sendEmailMime)




