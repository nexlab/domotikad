###########################################################################
# Copyright (c) 2011-2014 Unixmedia S.r.l. <info@unixmedia.it>
# Copyright (c) 2011-2014 Franco (nextime) Lanza <franco@unixmedia.it>
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

import json
from twisted.internet import defer, task, reactor, protocol
from nevow import inevow, rend, tags, loaders, flat, athena, stan, guard
import logging, os, sys
from twisted.web import resource, static, server
import time
from txsockjs.factory import SockJSResource, SockJSFactory
from autobahn.websocket import WebSocketServerFactory, WebSocketServerProtocol
from autobahn.resource import WebSocketResource, HTTPChannelHixie76Aware
import dmjson as dmj

log = logging.getLogger( 'Webgui' )

curdir=os.path.abspath(os.path.dirname(sys.argv[0]))



def relstatus(dbobj, ts=True, res=[]):
   if ts:
      res.append({'command': 'updatets', 'data':ts})
   if len(dbobj)>0:
      dbret={'command': 'updaterelays', 'data':[]}
      for ret in dbobj:
         dbret['data'].append(ret.toHash(['id', 'buttonid', 'board_name','board_ip','outnum','ctx','outtype','relnum','status','lastupdate']))
      res.append(dbret)
   return res


def inputstatus(dbobj, ts=True, res=[]):
   if ts:
      res.append({'command': 'updatets', 'data':ts})
   if len(dbobj)>0:
      dbret={'command': 'updateinputs', 'data':[]}
      for ret in dbobj:
         dbret['data'].append(ret.toHash(['id', 'buttonid', 'board_name','board_ip','inpnum','status','lastupdate']))
      res.append(dbret)
   return res



class DomotikaAjaxProtocol(object):


   def messageReceived(self, message, binary):
      f=getattr(self, 'on_command_'+message.split(":")[0], None)
      if f and callable(f):
         log.debug("Received "+str(message.split(":")[0])+" command")
         return f(message)
      else:
         self.messageSend(message, binary)

   def _getIOStatus(self, d, ts):
      rs = self.factory.core.getRelays(ts)
      rs.addCallback(relstatus, False, d)
      return rs.addCallback(dmj.jsonize_text)

   def on_command_getIOStatus(self, data):
      wts=data.split(":")[1].split("=")[1]
      ret=self.factory.core.getActionStatus()
      ts=int(time.time())-1
      ist=self.factory.core.getInputs(wts)
      ist.addCallback(inputstatus, ts, ret).addCallback(self._getIOStatus, wts)
      return ist.addCallback(self.messageSend)

   def connectionMade(self, who):
      log.debug('AJAX connectionMade called by '+str(who))

   def connectionLost(self, who, reason):
      log.debug('AJAX connectionLost called by '+str(who)+' for reason '+str(reason))



class AutobahnProtocolWrapper(WebSocketServerProtocol, DomotikaAjaxProtocol):

   def onMessage(self, msg, binary):
      self.messageReceived(msg, binary)

   def messageSend(self, msg, binary=False):
      log.debug("SEND MESSAGE "+str(msg))
      self.sendMessage(msg, binary)

   def connectionMade(self):
      WebSocketServerProtocol.connectionMade(self)
      DomotikaAjaxProtocol.connectionMade(self, 'autobahn')

   def connectionLost(self, reason):
      DomotikaAjaxProtocol.connectionLost(self, 'autobahn', reason)
      WebSocketServerProtocol.connectionLost(self, reason)


class SockJSServerProtocolWrapper(protocol.Protocol, DomotikaAjaxProtocol):

   def dataReceived(self, data):
      log.debug("SockJS RECEIVED: "+str(data))
      self.messageReceived(data, False)

   def messageSend(self, msg, binary=False):
      self.transport.write(msg)

   def connectionMade(self):
      DomotikaAjaxProtocol.connectionMade(self, 'sockjs')

   def connectionLost(self, reason):
      DomotikaAjaxProtocol.connectionLost(self, 'sockjs', reason)



class SockJSServerFactory(protocol.Factory):
   
   protocol = SockJSServerProtocolWrapper

   def buildProtocol(self, addr):
      log.debug("SockJS BuildProtocol for "+str(addr))
      p = self.protocol()
      p.core = self.core
      p.factory = self
      return p



def getAutoBahn(core, port=80):
   #from twisted.python import log as tlog
   #tlog.startLogging(sys.stdout)

   wsuri = "ws://localhost"
   if not port in ['80','443']:
      wsuri+=":"+str(port)
   #factory = WebSocketServerFactory(wsuri, debug=True, debugCodePaths=True)
   factory = WebSocketServerFactory(wsuri)
   factory.core = core
   factory.protocol = AutobahnProtocolWrapper
   factory.setProtocolOptions(allowHixie76 = True)
   resource = WebSocketResource(factory)
   log.debug("AutoBahn started")
   return resource


def getSocketJSResource(core):
   options = {
      'websocket': False,
      'cookie_needed': False,
      'heartbeat': 25,
      'timeout': 5,
      'streaming_limit': 128 * 1024,
      'encoding': 'cp1252', # Latin1
      #'sockjs_url': '/resources/js/sockjs-0.3.min.js'
      #'sockjs_url': 'https://d1fxtkz8shb9d2.cloudfront.net/sockjs-0.3.js'
   }
   f = SockJSServerFactory()
   f.core = core
   return SockJSResource(f, options)
   
