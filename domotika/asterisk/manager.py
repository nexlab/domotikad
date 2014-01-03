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

from twisted.internet import reactor, defer, task
import os, logging
from logging import handlers as loghandlers
#from Database import utils as dbutils
from starpy import manager

#configFile = dbutils.configFile

log = logging.getLogger('AMI')


class UMAMIClient(object):

   originated={}

   def __init__(self, ami, core, factory):
      self.ami = ami
      self.core = core
      self.factory = factory
      self.ami.checkconnect = True
      self.ami.pingcron = task.LoopingCall(self.ami.pingCron)
      self.ami.pingcron.start(5.0)
      log.debug("Ami PING Cron started")
      self.registerEvents()

   def registerEvents(self):
      log.debug("Register Events")
      self.ami.registerEvent(None, self.event_parser)

   def checkOriginateRetry(self, aid):
      if aid in self.originated.keys():
         if self.originated[aid]["retry"] > 0 and self.originated[aid]['callstatus']!="Success":
            self.originated[aid]["retry"]=self.originated[aid]["retry"]-1
         else:
            del self.originated[aid]
            return None
         if self.originated[aid]['callstatus']=='start':
            return reactor.callLater(self.originated[aid]['retrytimeout'], self.checkOriginateRetry, aid)
         else:
            rd=self.originated[aid]
            self.startCall(**rd)
            
   def startCall(self, localextension='h', localcontext='domotika_internal', 
                extension='h', context='domotika_internal', callerid="Domotika", 
                timeout=60, async=True, variable={},
                retry=0, retrytimeout=10, callstatus='start'):
      rd={
            'localextension':localextension,
            'localcontext':localcontext,
            'extension':extension,
            'context':context,
            'callerid':callerid,
            'timeout':timeout,
            'async':async,
            'variable':variable,
            'retry':retry,
            'retrytimeout':retrytimeout,
            'callstatus':callstatus
          }
      def registerCall(res):
         if res['response']=='Success' and retry>0:
            if not res['actionid'] in self.originated.keys():
               self.originated[res['actionid']] = rd
            return reactor.callLater(retrytimeout, self.checkOriginateRetry, res['actionid'])

         if res['actionid'] in self.originated.keys():
            del self.originated[res['actionid']]
         return res

      self.ami.originate(
            'Local/'+str(localextension)+'@'+localcontext,
            context=context,
            exten=extension,
            priority='1',
            callerid=callerid,
            async=async,
            timeout=timeout,
            variable=variable
      ).addCallback(registerCall)

   def VoipCall(self, *a, **kw):
      log.info("VoipCall: "+str(a)+" "+str(kw))

   def event_parser(self, manager, event):
      log.debug("AMI Event: "+str(event))
      f=getattr(self, 'evt_'+event['event'], None)
      if f and callable(f):
         return f(event)

   def evt_OriginateResponse(self, event):
      if event['actionid'] in self.originated.keys():
         self.originated[event['actionid']]['callstatus']=event['response']

   def evt_DTMF(self, event):
      def statusparse(res, direction):
         eventtype = 'dtmf-'+direction
         status=res[1]
         variable=event['digit']
         if 'context' in status.keys():
            caller=status['calleridnum']
            called=status['extension']
            context=status['context']
            log.info("DTMF: "+" ".join([str(eventtype), str(caller), str(called), str(context), str(variable)]))
            return self.core.amiEventReceived(eventtype, caller, called, context, variable)
         elif direction=='received':
            return self.ami.status(res[1]['bridgedchannel']).addCallback(statusparse, 'received')

      def statuscheck(res):
         if event['direction']=='Received':
            return statusparse(res, 'sent')
         else:
            return self.ami.status(res[1]['bridgedchannel']).addCallback(statusparse, 'received')

      log.debug("EVENT DTMF")
      if event['begin']=='Yes':
         return self.ami.status(event['channel']).addCallback(statuscheck)
      return False

   def evt_Dial(self, event):
      if 'subevent' in event.keys() and event['subevent']=='Begin':
         self.core.amiCall('Dial', src=event['calleridnum'],
                           srcname=event['calleridname'],
                           srcchannel=event['channel'],
                           dst=event['dialstring'],
                           dstchannel=event['destination'])
         
   def evt_Hangup(self, event):
      self.core.amiCall('Hangup', src=event['calleridnum'],
                        srcname=event['calleridname'],
                        srcchannel=event['channel'],
                        dst=event['connectedlinenum'],
                        dstname=event['connectedlinename'])

class UMAMIProtocol( manager.AMIProtocol ):

   def connectionLost(self, reason):
      try:
         self.pingcron.stop()
         log.debug("Ami PING Cron stopped")
      except:
         pass
      return manager.AMIProtocol.connectionLost(self, reason)

   def pingCron(self):
      log.debug("PING")
      self.ping()

   def login(self, *args, **kwargs):
      log.debug("LOGIN")
      return manager.AMIProtocol.login(self, *args, **kwargs)


class UMAMIFactory( manager.AMIFactory ):

   protocol = UMAMIProtocol
   ami = False
   client = False
   calls = {}

   def __init__(self, core, user, pwd):
      self.core = core
      manager.AMIFactory.__init__(self, user, pwd)

   def login( self, server='localhost', port=5038, timeout=5 ):
      """Connect, returning our (singleton) protocol instance with login completed

      XXX This is messy, we'd much rather have the factory able to create
      large numbers of protocols simultaneously
      """
      log.debug("initialize")
      self.restarting = False
      self.connected = False
      self.server = server
      self.port = port
      self.timeout = timeout
      self.loginDefer = defer.Deferred()
      self.interface = reactor.connectTCP(server,port,self, timeout=timeout)
      return self.loginDefer.addCallback(self.StartClientSession)

   def clientConnectionLost(self, connector=None, reason=None):
      if not self.restarting:
         log.debug("client connection lost")
         self.connected = False
         return reactor.callLater(1, self.clientReconnect)
      else:
         log.debug("client configuration changed")
         return defer.succeed(True)

   def clientReconnect(self):
      log.debug("client reconnect")
      self.loginDefer = defer.Deferred()
      self.interface = reactor.connectTCP(self.server,self.port,self, timeout=self.timeout)
      return self.loginDefer.addCallback(self.StartClientSession)


   def clientConnectionFailed(self, connector, reason):
      log.debug("client connection failed")
      self.connected = False
      return reactor.callLater(self.timeout, self.clientConnectionLost)
      #return self.clientConnectionLost(connector, reason)


   def StartClientSession(self, ami):
      log.debug("Start client session")
      self.connected = True
      self.ami = ami
      self.client = UMAMIClient(ami, self.core, self)
      return ami

   def getStatus(self):
      return self.connected

   def phoneSay(self, saytext=False, destinations=[], retry=1, interval=60, 
               replay=1, engine='festival', ttslang='it'):
      if len(destinations) > 0 and self.client and saytext and len(saytext)>0:
         var={'SAYTEXT':saytext,'REPLAY':str(replay), 
               'TTSENGINE':str(engine), 'TTSLANG':str(ttslang)}
         for dest in destinations:
            if dest and len(dest)>0:
               self.client.startCall(dest, extension='domotika_saytext', timeout=interval, variable=var,
                     retry=retry, retrytimeout=interval)

   def phonePlay(self, playfile=False, destinations=[], retry=1, interval=60, replay=1):
      if len(destinations) > 0 and self.client and playfile and len(playfile)>0:
         if "." in playfile: # Clear file extension
            playfile=".".join(playfile.split(".")[:-1])
         var={'PLAYFILE':playfile,'REPLAY':str(replay)}
         for dest in destinations:
            if dest and len(dest)>0:
               self.client.startCall(dest, extension='domotika_playfile', timeout=interval, variable=var,
                     retry=retry, retrytimeout=interval)

            
   def startCall(self, extensionfrom='h', contextfrom='domotika_internal', 
                        extensionto='h', contextto='domotika_internal'):  
      if self.client:
         return self.client.startCall(extensionfrom, contextfrom, extensionto, contextto)


