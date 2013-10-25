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

from twisted.mail import smtp, maildir  
from zope.interface import implements  
from twisted.internet import protocol, reactor, defer  
import os  
from email.Header import Header    
import dmmail
import logging

log = logging.getLogger( 'Mail' )

class MailMessageSender(object):  
   implements(smtp.IMessage)    

   def __init__(self, recipient, sender):  
      self.lines = []    
      self.recipient = recipient
      self.sender = sender

   def lineReceived(self, line):  
      self.lines.append(line)    

   def eomReceived(self):  
      self.lines.append('') 
      messageData = '\n'.join(self.lines)  
      return dmmail.sendMail(self.sender, self.recipient, messageData)    

   def connectionLost(self):  
      print "Connection lost unexpectedly!"  
      # unexpected loss of connection; don't save  
      del(self.lines)    

class MailDelivery(object):  
   implements(smtp.IMessageDelivery)    
   
   def __init__(self):
      self.sender="domotika@unixmedia.it"
      self.recipient="none@unixmedia.it"

   def receivedHeader(self, helo, origin, recipients):  
      myHostname, clientIP = helo  
      headerValue = "by %s from %s with ESMTP ; %s" % (  myHostname, clientIP, smtp.rfc822date())  
      return "Received: %s" % Header(headerValue)    

   def validateTo(self, user):  
      #if not user.dest.domain in self.validDomains:  
      #   raise smtp.SMTPBadRcpt(user)
      self.recipient=str(user.dest)
      log.debug("Accepting mail for %s..." % user.dest)  
      return lambda: MailMessageSender(self.recipient, self.sender)    

   def validateFrom(self, helo, originAddress):  
      self.sender=originAddress.addrstr
      return originAddress    

class SMTPFactory(protocol.ServerFactory):  

   def buildProtocol(self, addr):  
      delivery = MailDelivery()  
      smtpProtocol = smtp.SMTP(delivery)  
      smtpProtocol.factory = self  
      return smtpProtocol    


def getSmtp():
   return SMTPFactory()


