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

from twisted.application import service
from twisted.internet import defer, reactor, task, protocol, threads
from dmlib.utils.genutils import configFile, FakeObject
from dmlib.utils import genutils
from lang import lang
import logging, sys, os
from web import web
import ikapserver
import subprocess
import time, copy
from web import proxy, mediaproxy
from twisted.web import microdom as xml
from singleton import clients, sequences, crontabs, statuses
from singleton import oldboards as oldb
from dmlib.utils import webutils as wu
from dmlib import constants as C
from db import dmdb 
import time
from txscheduling import task  as txcron
from txscheduling.cron import CronSchedule, parseCronLine
from txscheduling.interfaces import ISchedule
from netifaces import interfaces, ifaddresses, AF_INET
import struct
from dmlib import dmdomain
import plugins
import events 
from mail import dmmail as email
from mail import dmsmtp 
from asterisk import manager as ami
from asterisk import fastagi as fagi
from voiceui import voiceui as voice
from boards import pluggable as pluggableBoards
from boards.iotype import context2section
from mediasources import pluggable as pluggableMediasouces
import sky
from clouds.openweathermap import weather 

try:
   import hashlib
   md5 = hashlib
   md5.new = hashlib.md5
   sha1 = hashlib.sha1
except:
   import md5
   import sha1



ALLIP=C.IKAP_BROADCAST

ACTION_STATUS={}

log = logging.getLogger( 'Core' )


def converWday(wday):
   wday=wday+1
   if wday==7:
      wday=0
   return wday

class ConvenienceCaller(object):
   """
      This metaclass build and abstraction of an object instance so
      that other objects can call it as it is a module, and permit
      to the original object to setup a specific callback
      to the caller so it can manage the calls originated by the caller
      with local methods
   """
   def __init__(self, callerfunc):
      """
         @params callerfunc: function/method to be used as callback
                             inside the original class of the abstract object

      """
      self.callerfunc=callerfunc

   def __getattribute__(self, name):
      """
         This do the magic, transforming every called method in a call
         to the callerfunction of the original object

         This method isn't intended to be called directly!
      """
      callerfunc = object.__getattribute__(self, 'callerfunc')
      return callerfunc(name)


class domotikaService(service.Service):


   alarm=False
   initialized=False
   confstatus=False
   lastconfigChange = 0
   lateststatuschange = 0
   autocron=False
   autostatuses=False
   relays = {}
   statsTimers={}
   actstatusremain = 0
   actionloops={}
   lastsync=0.0
   lastCLIENTSync=0.0
   boardconfigchanged = False
   upnp_detected_ips=[]
   udp=False
   tcp=False
   daemonstatus='normal'

   def __init__(self, *args, **kwargs):
      log.info('Initializing Core')
      self.curdir=kwargs['curdir']
      self.config=kwargs['config']
      sys.path.append(self.curdir+"/domotika")
      log.debug('Current dir: '+self.curdir)
      if self.parent:
         self.parent.__new__(self.parent, self, *args)
      self.lastupdatestatus=0
      self.clients = clients.ClientRegistry()
      #self.boardsyspwd = genutils.board_syspwd(self.config.get("general", "boards_syspwd"))
      #self.devadminpwd  = genutils.devs_adminpwd(self.config.get("general", "devices_admpwd"))
      dmdb.initialize(self.config)

   def isStarted(self):
      
      self.isConfigured()

   def isConfigured(self):
      self.timer = task.LoopingCall(self.getRelayStatus)
      self.actiontimer = task.LoopingCall(self.actionStatus)
      self.cleanStatusTimer = task.LoopingCall(self.cleanOldStatus)
      self.boardsyspwd = genutils.board_syspwd(self.config.get("general", "boards_syspwd"))
      self.devadminpwd  = genutils.devs_adminpwd(self.config.get("general", "devices_admpwd"))
      self.sun = sky.DMSun(self.config.get("geo", "latitude"), self.config.get("geo", "longitude"), self.config.get("geo", "elevation"))
      if self.config.get("general", "timeserver").lower() in ['yes','y','1','true', 'on']:
         self.timeserver = task.LoopingCall(self.broadcastTime)
      self.notifytimer = task.LoopingCall(self.expireNotify)
      self.notifytimer.start(60)
      self.clienttimer = task.LoopingCall(self.expireClients)
      self.clienttimer.start(60)

      self.actiontimer.start(int(self.config.get("general", "action_status_timer")))
      self.timer.start(int(self.config.get("ikapserver", "timeupdates"))) 
      if self.config.get("general", "timeserver").lower() in ['yes','y','1','true', 'on']:
         if(unicode(self.config.get("general", "timeinterval")).isnumeric()):
            self.timeserver.start(int(self.config.get("general", "timeinterval")))
      if int(self.config.get("general", "remove_old_status")) > 0:
         self.cleanStatusTimer.start(int(self.config.get("general", "remove_old_status")))
      self.startDNS()
      if self.config.get("general", "autodetect").lower() in ['yes','y','1','true', 'on']:
         self.autoDetectBoards()

      flags=task.LoopingCall(self.cleanFlags)
      flags.start(1)

      self.startUPNPService()
      self.startAsteriskServices()
      self.initializeCrontab()
      self.initializeStatuses()
      self.initializeSequences()
      self.initializePlugins()
      self.startActionLoops()
      self.startClientsSync()
      if int(self.config.get('media', 'localtranscode')) > 0 and 'vlc' in str(self.config.get('media','transcode')).split(','):
         self.startVLC()
      self.startOpenWeatherMap()
      self.initialized=True

   def startOpenWeatherMap(self):
      weather.OWMWeather(self.config.get("geo", "latitude"), 
         self.config.get("geo", "longitude"), 
         self.config.get("geo", "location"), 
         self.config.get("geo", "openweathermap_appid"))


   def startVLC(self):
      self.vlc = mediaproxy.VLCFactory()
      self.vlc.start()
      reactor.callLater(3, self.startVLCClient)


   def startVLCClient(self):
      self.vlcclient = reactor.connectTCP('127.0.0.1', 4212, mediaproxy.VLCClientFactory())


   def startDNS(self):
      import nameserver
      ns1=(self.config.get("dns", "ns1"), 53)
      ns2=(self.config.get("dns", "ns2"), 53)
      host=self.config.get("dns", "host")
      ip=self.config.get("dns", "ip")
      iface=self.config.get("ikapserver", "ethdev")
      nameserver.startDNS(host, ip, iface, [ns1, ns2])


   def cleanFlags(self):
      dmdb.cleanFlags()

   def refreshActionLoops(self):
      dmdb.getActionLoops().addCallback(self.actionLoopTasks)

   def startClientsSync(self):
      self.lastsync=float(time.time())
      self.lastCLIENTSync=self.lastsync
      t = task.LoopingCall(self.clientsSync)
      t.start(0.5)

   def updateDaemonStatus(self, status='normal'):
      self.daemonstatus=status
      self.clientSend('daemonstatus', self.daemonstatus)

   def clientsSync(self):
      def _clientSend(res, ts):
         #log.info(res)
         if res and len(res) > 0:
            log.debug("Sending CLIENT Sync "+str({'lastupdate': ts, 'statuses': res}))
            self.lastCLIENTSync=ts
            self.clientSend('sync', {'lastupdate': ts, 'statuses': res})
      ts=self.lastsync
      self.lastsync=float(time.time())
      #log.info(str(ts)+" "+str(self.lastsync))
      dmdb.ioSync(str(ts)).addCallback(_clientSend, ts)

   def startActionLoops(self):
      t=task.LoopingCall(self.refreshActionLoops)
      t.start(60)

   def actionLoopTasks(self, res):
      log.debug("ACTION LOOP TASKS")
      IDS={}
      for i in res:
         IDS[i.id]={'timing': i.action_loop_interval}
      for i in self.actionloops.keys():
         if i not in IDS.keys() or IDS[i]['timing']!=self.actionloops[i]['timing']:
            try:
               self.actionloops[i]['timer'].stop()
            except:
               pass
            finally:
               del self.actionloops[i]
         elif i in IDS.keys():
            del IDS[i]
      for i in IDS.keys():
         self.actionloops[i]={}
         self.actionloops[i]['timer']=task.LoopingCall(self.executeLoopAction, i)
         #self.actionloops[i]['timing']=res[i].action_loop_interval
         self.actionloops[i]['timing']=IDS[i]['timing']
         self.actionloops[i]['timer'].start(self.actionloops[i]['timing'])
         
   def executeLoopAction(self, actid):
      def goActions(res):
         for r in res:
            log.debug("Execute action loop for action id "+str(r.id))
            self.parseAction(r, 'action')
      dmdb.getActionById(actid).addCallback(goActions)   

   def expireNotify(self):
      dmdb.expireNotify()

   def expireClients(self):
      for c in self.clients.getAll():
         try:
            if c['time']<time.time()-180:
               self.clients.del_session(c['suid'])
         except:
            try:
               self.clients.del_session(c['suid'])
            except:
               pass

   @defer.inlineCallbacks
   def sendNetStatus(self, cbres=None, force=False, ipdst="255.255.255.255"):
      st=yield dmdb.getNetStatus()
      #ret=list(st)[0]
      log.debug("Sending Status "+str(st)+" "+str(force))
      if type(st).__name__=='str':
         if st!='DEFAULT' or force:
            self.sendCommand(str(st), msgtype=C.IKAP_MSG_ACTION, ctx=C.IKAP_CTX_STATUS, act=C.IKAP_ACT_CHANGE, ipdst=ipdst)


   def broadcastTime(self, ipdst="255.255.255.255"):
      if self.config.get("general", "timeserver").lower() in ['yes','y','1','true', 'on']:
         log.debug("Broadcasting Time to "+str(ipdst))
         self.sendCommand("SETTIME", arg_parse=False, arg=struct.pack("<L", int(time.time())), act=C.IKAP_ACT_BOARD, ctx=C.IKAP_CTX_SYSTEM, msgtype=C.IKAP_MSG_ACTION, ipdst=ipdst)


   def initializePlugins(self):
      caller = ConvenienceCaller(self._cmdFromPlugin)
      self.plugins=plugins.Loader(caller)

   def initializeSequences(self):
      dmdb.getRunningSequences().addCallback(self.resetRunningSequences)

   def resetRunningSequences(self, res):
      if res:
         for r in res:
            if int(r.running) > 0:
               r.running=0
               r.save()

   def initializeCrontab(self):
      # Start a reset of the crontabs every 
      # 1 January of ever day.
      s=txcron.ScheduledCall(self.resetCrontab)
      s.start(CronSchedule('0 0 1 1 *'))

      # Recheck cron schedules every minute
      s=txcron.ScheduledCall(self.rescheduleCrontab)
      s.start(CronSchedule('* * * * *'))
      dmdb.getTimerSchedules().addCallback(self.scheduleCronEvents)


   def initializeStatuses(self):
      # Start a reset of the crontabs every 
      # 1 January of ever day.
      s=txcron.ScheduledCall(self.resetStatuses)
      s.start(CronSchedule('0 0 1 1 *'))

      # Recheck cron schedules every minute
      s=txcron.ScheduledCall(self.rescheduleStatuses)
      s.start(CronSchedule('* * * * *'))
      dmdb.getStatusSchedules().addCallback(self.scheduleStatusEvents)
     

   def cleanOldStatus(self):
      dmdb.cleanOldStatus(int(time.time())-int(self.config.get("general", "remove_old_status")))

   def resetCrontab(self):
      events.postEvent(events.TimerEvent('RESET'))
      self.autocron=False
      cs=crontabs.CrontabsRegistry()
      # XXX Make this  async?
      for c in cs.getAllKeys():
         cs.del_cron(c)
      dmdb.getTimerSchedules().addCallback(self.scheduleCronEvents)

   def resetStatuses(self):
      events.postEvent(events.StatusEvent('RESET'))
      self.autostatuses=False
      ss=statuses.StatusesRegistry()
      # XXX Make this  async?
      for s in ss.getAllKeys():
         ss.del_status(s)
      dmdb.getStatusSchedules().addCallback(self.scheduleStatusEvents)

   def _removeExpiredCron(self, rlist):
      cs=crontabs.CrontabsRegistry()
      # XXX Make this  async?
      for c in cs.getAllKeys():
         if c not in rlist:
            log.info("TIMER "+str(c)+" cancelled")
            cs.del_cron(c)

   def _removeExpiredStatuses(self, rlist):
      ss=statuses.StatusesRegistry()
      # XXX Make this  async?
      for s in ss.getAllKeys():
         if s not in rlist:
            log.info("STATUSES  "+str(s)+" cancelled")
            ss.del_status(s)

   def _rescheduleCrontabs(self, res):
      # XXX make this async?
      if self.autocron:
         rlist=[]
         cs=crontabs.CrontabsRegistry()
         for r in res:
            rlist.append(r.id)
            if cs.cronid_exists(r.id):
               s=cs.get_cron(r.id)
               if not (s.schedule == CronSchedule(self.parseSchedule(r))):
                  log.info("TIMER: Cron schedule changed for cron id: "+str(r.id))
                  log.info("TIMER change: "+str(s.schedule)+" - "+str(ISchedule(CronSchedule(self.parseSchedule(r)))))
                  cs.del_cron(r.id)
                  s=txcron.ScheduledCall(self.manageCrontab, r.id)
                  s.start(CronSchedule(self.parseSchedule(r)))
                  cs.add_cron(r.id, s)
               elif not s.running:
                  s.start()
            else:
               s=txcron.ScheduledCall(self.manageCrontab, r.id)
               s.start(CronSchedule(self.parseSchedule(r)))
               cs.add_cron(r.id, s)
         reactor.callLater(0, self._removeExpiredCron, rlist)
        

   def rescheduleCrontab(self):
      events.postEvent(events.TimerEvent('RESCHEDULE'))
      dmdb.getTimerSchedules().addCallback(self._rescheduleCrontabs)

   def _rescheduleStatuses(self, res):
      # XXX make this async?
      if self.autostatuses:
         rlist=[]
         ss=statuses.StatusesRegistry()
         for r in res:
            rlist.append(r.id)
            if ss.statusid_exists(r.id):
               s=ss.get_status(r.id)
               if not (s.interval == r.trigger_interval):
                  log.info("STATUSES: schedule changed for status id: "+str(r.id))
                  log.info("STATUSES change: "+str(s.interval)+" - "+str(r.trigger_interval))
                  ss.del_status(r.id)
                  l=task.LoopingCall(self.manageStatuses, r.id)
                  l.start(r.trigger_interval)
                  ss.add_status(r.id, l)
               elif not s.running:
                  s.start(r.trigger_interval)
            else:
               l=task.LoopingCall(self.manageStatuses, r.id)
               l.start(r.trigger_interval)
               ss.add_status(r.id, l)
         reactor.callLater(0, self._removeExpiredStatuses, rlist)


   def rescheduleStatuses(self):
      events.postEvent(events.StatusEvent('RESCHEDULE'))
      dmdb.getStatusSchedules().addCallback(self._rescheduleStatuses)

   def parseSchedule(self, res):
      return " ".join([res.min, res.hour, res.day, res.month, res.dayofweek])

   def scheduleStatusEvents(self, res):
      log.debug("STATUSES: "+str(res))
      ss=statuses.StatusesRegistry()
      for s in res:
         events.postEvent(events.StatusEvent('SCHEDULE', s.id))
         l=task.LoopingCall(self.manageStatuses, s.id)
         l.start(s.trigger_interval)
         ss.add_status(s.id, l)
      self.autostatuses=True

   def scheduleCronEvents(self, res):
      log.debug("TIMER: "+str(res))
      cs=crontabs.CrontabsRegistry()
      for r in res:
         events.postEvent(events.TimerEvent('SCHEDULE', r.id))
         s=txcron.ScheduledCall(self.manageCrontab, r.id)
         s.start(CronSchedule(self.parseSchedule(r)))
         cs.add_cron(r.id, s)
      self.autocron=True

   def resetBoards(self, *a, **kw):
      return dmdb.resetBoards()

   def resetPwmList(self, *a, **kw):
      dmdb.resetAllPwmStatus()
      return dmdb.resetDynPwms()

   def resetOutputList(self, *a, **kw):
      return dmdb.resetDynOutputs()

   def resetRelayList(self, *a, **kw):
      dmdb.resetAllRelStatus()
      return dmdb.resetDynRelays()

   def resetAnalogList(self, *a, **kw):
      dmdb.resetAllAnaStatus()
      return dmdb.resetDynAnalogs()

   def resetInputList(self, *a, **kw):
      dmdb.resetAllInpStatus()
      return dmdb.resetDynInputs()

   def resetActionList(self, *a, **kw):
      return dmdb.resetDynActions()

   def resetMediaSourcesList(self, *a, **kw):
      self.upnp_detected_ips=[]
      return dmdb.resetDynMediaSources()

   def autoDetectBoards(self, *a, **kw):
      log.info("Start building boardlist")

      self.updateDaemonStatus('boardsdetection')

      # make sure boards are time synced
      self.broadcastTime()
      
      # setting up database for detection
      dmdb.initializeAutoDetection()
      self.confstatus=1
      self.boardconfigchanged=False
      reactor.callLater(0.5, self._autoDetectionStart)

   def _autoDetectionStart(self):
      self.sendCommand("BOARDTYPE", arg=ALLIP, act=C.IKAP_ACT_BOARD, ctx=C.IKAP_CTX_SYSTEM, msgtype=C.IKAP_MSG_REQUESTCONF)
      self.timeconfstatus=reactor.callLater(15, self.endConfStatus)


   def checkDoubleRelDevice(self, dres, domain):
      dmdb.Relay.find(where=["domain=? AND active=1 AND outnum!=0", domain], orderby="board_ip,outnum").addCallback(self.createDevice, domain, dres, 'relay')

   def checkDoubleInpDevice(self, dres, domain):
      dmdb.Input.find(where=["inpname=? AND active=1 AND inpnum!=0", domain], orderby="board_ip,inpnum").addCallback(self.createDevice, domain, dres, 'input')

   def checkDoubleAnaDevice(self, dres, domain):
      dmdb.Analog.find(where=["ananame=? AND active=1 AND ananum!=0", domain], orderby="board_ip,ananum").addCallback(self.createDevice, domain, dres, 'analog')

   def retriveDeviceInputs(self):
      log.debug("retriveDeviceInputs")
      dmdb.runQuery("SELECT DISTINCT(inpname) FROM input WHERE active=1 AND inpnum!=0").addCallback(self.idomainRetrivied)

   def retriveDeviceAnalogs(self):
      log.debug("retriveDeviceAnalogs")
      dmdb.runQuery("SELECT DISTINCT(ananame) FROM analog WHERE active=1 AND ananum!=0").addCallback(self.adomainRetrivied)

   def startDevicePopulation(self, r):
      dmdb.runQuery("SELECT DISTINCT(domain) FROM relay WHERE active=1 AND outnum!=0").addCallback(self.odomainRetrivied)

   def endConfStatus(self):
      log.info("finished building boardlist")
      self.updateDaemonStatus('normal')
      self.confstatus=False
      self.initializeDatabases()

   def initializeDatabases(self):
      dmdb.emptyRealtimeStatus()
      dmdb.cleanUndetected()

   def insertInput(self, res, inp, name, fwver):
      # XXX: Come gestiamo il fatto che gli "enabled" siano o meno attivati
      #      sugli stati della scheda? un'idea e' mettere a 0 active se nessuno
      #      degli stati e' enabled, ma ha senso farlo, oppure ci basiamo
      #      sul fatto che usiamo la websection a none?
      if not res:
         log.debug("INPUT %s is NEW (%s, %s)" % (inp.name, name, inp.host))
         res=[]
         res.append(dmdb.Input())
         res[0].dynamic=1
         res[0].websection=inp.section
         res[0].button_name=inp.button_name
         res[0].active=inp.enabled
         res[0].board_name=name
         res[0].board_ip=inp.host
         res[0].inpnum=inp.num
         res[0].inpname=inp.name
         res[0].position=0
         
      else:
         log.debug("INPUT %s exists (%s, %s)" % (inp.name, name, inp.host))

      for c in res:
         c.detected=1
         if(c.inpname!=inp.name and c.dynamic!=0):
            c.inpname=inp.name
            c.websection=inp.section
            c.button_name=inp.button_name
            c.position=0
            c.dynamic=1
            c.active=inp.enabled
         c.save().addCallback(log.info)

   def insertAnalog(self, res, ana, name, fwver):
      # XXX: Come gestiamo il fatto che gli "enabled" siano o meno attivati
      #      sugli stati della scheda? un'idea e' mettere a 0 active se nessuno
      #      degli stati e' enabled, ma ha senso farlo, oppure ci basiamo
      #      sul fatto che usiamo la websection a none?
      if not res:
         log.debug("ANALOG %s is NEW (%s, %s)" % (ana.name, name, ana.host))
         res=[]
         res.append(dmdb.Analog())
         res[0].dynamic=1
         res[0].websection=ana.section
         res[0].active=ana.enabled
         res[0].board_ip=ana.host
         res[0].ananame=ana.name
         res[0].ananum=ana.num
         res[0].board_name=name
         res[0].button_name=ana.button_name
      else:
         log.debug("ANALOG %s exists (%s, %s)" % (ana.name, name, ana.host))

      for c in res:
         c.detected=1
         if(c.ananame!=ana.name and c.dynamic!=0):
            log.debug("Analog definition is changed")
            c.ananame=ana.name
            c.websection=ana.section
            c.button_name=ana.button_name
            c.dynamic=1
            c.active=ana.enabled
         c.save().addCallback(log.info)


   def boardIOConf(self, bplugin, name, fwver, btype, ptype, port, *arg, **kwarg):
      try:
         self.timeconfstatus.reset(15)
      except:
         pass

      if bplugin.hasAnalogs:
         for a in bplugin.getAnalogsNames().values():
            dmdb.Analog.find(where=["""ananum=? AND board_name=? """, a.num, name ]).addCallback(self.insertAnalog,
               a, name, fwver
            )
       
      if bplugin.hasInputs:
         for i in bplugin.getInputsNames().values():
            dmdb.Input.find(where=["""inpnum=? AND board_name=? """, i.num, name]).addCallback(self.insertInput,
               i, name, fwver
            )
      if bplugin.hasOutputs:
         for o in bplugin.getOutputsConfs().values():
            # OUTPUT NOTE: is based on output not on relay! an output can have more than 1 relay...
            dmdb.Relay.find(where=["""outnum=? AND board_name=? """, i, name]).addCallback(self.insertRelay,
               o, name, fwver
            )
            dmdb.Output.find(where=["""outnum=? AND board_name=? """, i, name]).addCallback(self.insertOutput,
               o, name, fwver
            )

   def insertOutput(self, res, out, name, fwver):

      log.debug("Try to ass output "+str(out.num)+" on board "+str(name)+" ip "+str(out.host))

      i=0
      if res:
         log.debug("OUTPUT %s exists (%s, %s)" % (out.dname, name, out.host))
         for c in res:
            if c.outtype!=int(out.otype):
               log.debug("OUTPUT type changed. Delete old entries")
               c.delete()
               del res[i]
            else:
               i=i+1
      if not res:
         res=[]
      rlen=len(res)

      if(rlen==0): # Is a new entry
         o=dmdb.Output() 
         o.dynamic = 1
      else:
         o=res[0]
      o.board_name=name
      o.board_ip=out.host
      o.outnum=out.num
      o.outtype=int(out.otype)
      o.ctx=int(out.ctx)
      o.active=out.enabled
      o.domain=out.dname
      o.websection=out.section
      o.button_name=out.button_name
      o.detected=1
      o.has_relays=1 if out.hasRelays else 0
      o.has_pwms=1 if out.hasPwms else 0
      o.save().addCallback(log.info)

   def insertRelay(self, res, out, name, fwver):

      log.debug("Try to ass relay "+str(out.num)+" on board "+str(name)+" ip "+str(out.host))
 
      i=0
      if res:
         log.debug("RELAY %s exists (%s, %s)" % (out.dname, name, out.host))
         for c in res:
            if c.outtype!=int(out.otype) or i >= out.numrel:
               log.debug("RELAY type changed or too many relays. Delete old entries")
               c.delete()
               del res[i]
            else:
               i+=1      
     
      log.debug("RELAY ADD %s (%s, %s)" % (out.dname, name, out.host))
      
      if not res:
         res=[]
      rlen=len(res)
         
      i=0
      while(i<out.numrel):
         if rlen<i+1: # "if is a new entry"
            res.append(dmdb.Relay())
            res[i].dynamic=1
         
         if res[i].dynamic!=0: # old dynamic or new   
            res[i].board_name=name
            res[i].board_ip=out.host
            res[i].outnum=out.num
            res[i].outtype=int(out.otype)
            res[i].ctx=int(out.ctx)
            if int(out.ctx)==C.IKAP_CTX_LIGHT:
               res[i].color_on='orange'
            if out.numrel>1:
               rep=out.relays[i].button_name.replace(out.button_name, "").lstrip()
               if len(rep) > 0:
                  res[i].text_on=rep
                  res[i].text_off=rep
            res[i].active=out.enabled
            res[i].domain=out.dname
            res[i].position=i
            res[i].websection=out.section
            res[i].relnum=out.relays[i].num
            res[i].act=out.relays[i].act
            res[i].msgtype=out.relays[i].msgtype
            res[i].button_name=out.relays[i].button_name    
            res[i].has_amp=1 if out.hasAmperometers else 0
         i+=1

      for c in res:
         c.detected=1
         c.save().addCallback(log.info)



   def checkIfBoardChanged(self, dbres, bplugin, btype, fwver, name, ptype='UDPv4', port=6654):

      needioupdate=False
      needipupdate=False
      if dbres:
         log.info("Board found "+str(name))
         dbb=dbres[0]
         dbb.detected=1
         dbb.last_status_request=float(time.time())
         dbb.last_status_update=float(time.time())
         if ptype=='UDP4':
            port=int(self.config.get('ikapserver', 'port'))

         if(dbb.transport!=ptype):
            log.info("Board "+str(name)+" has changed transport")
            dbb.transport=ptype
         if(dbb.port!=port):
            log.info("Board "+str(name)+" has changed port and has relevant transport")
            dbb.port=port
            needipupdate=True
         if(dbb.ip!=bplugin.host):
            log.info("Board "+str(name)+" has changed IP addr")
            dbb.ip=bplugin.host
            needipupdate=True
         if needipupdate:
            dmdb.boardIPChanged(name, bplugin.host, ptype, port)
         if(dbb.fwversion!=fwver):
            log.info("Board "+str(name)+" has changed Firmware version")
            dbb.fwversion=fwver
         if(dbb.webport!=bplugin.port):
            log.info("Board "+str(name)+" has changed Webport")
            dbb.webport=bplugin.port
         if(dbb.confhash!=bplugin.iohash):
            log.info("Board "+str(name)+" has changed IO config")
            dbb.confhash=bplugin.iohash     
            needioupdate=True
         else:
            if ptype=='UDP4':
               port=int(self.config.get('ikapserver', 'port'))
            log.info("Board isn't changed")
            dmdb.boardConfigNotChanged(name, bplugin.host, bplugin.port, ptype, port)
         dbb.save().addCallback(log.info)

      else:
         log.info("BOARD "+name+" NOT FOUND! add it")
         
         if ptype=='UDP4':
            port=int(self.config.get('ikapserver', 'port'))
         dmdb.addBoard(btype, bplugin.fwtype, fwver, name, bplugin.host, bplugin.iohash, bplugin.port, ptype, port)
         needioupdate=True
      if(needioupdate):
         self.boardconfigchanged=True
         log.info("Board config for "+name+" is changed or is a new board.")
         self.boardIOConf(bplugin,name,fwver,btype,ptype,port)
      if int(fwver) < 5:
         log.debug("ADD "+str(bplugin.host)+" at Oldboards list")
         o=oldb.OldBoards()
         o.add_board(bplugin.host)

   def askForBoardData(self, bplugin, btype, fwver, name, ptype='UDP4', port=6654):
      d=dmdb.DMBoards.find(where=["type=? AND name=? AND fwtype=?", btype, name, bplugin.fwtype])
      return d.addCallback(self.checkIfBoardChanged, bplugin, btype, fwver, name, ptype, port)

   def addBoard(self, btype, fwver, name, ip, webport=80, ptype='UDP4', port=6654):
      log.debug(" ".join(["ADDBoard", str(name),  str(btype), str(fwver), str(ip)]))
      p=pluggableBoards.getBoardPlugin(btype)
      if p:
         pboard = p.getBoard(ip, webport, self.boardsyspwd, str(self.config.get('general', 'language')))
         log.info("Support module for "+str(btype)+" board LOADED")
         pboard.initialize().addCallback(self.askForBoardData, btype, fwver, name, ptype, port)

      else:
         log.error("Support module for "+str(btype)+" board NOT FOUND!")
      
      try:
         if self.confstatus:
            self.timeconfstatus.reset(25)
      except:
         pass

   # ['porta.pi.laboratorio', 'porta.pi.laboratorio', 5, 4, 4, '\xc0\xa8\x04\xdd\xff\xa3\x01\x00\x00', {'raw': '\xc0\xa8\x04\xdd\xff\xa3\x01\x00\x00', 'ip': '192.168.4.221', 'io_type': 255, 'OPT_DATA': None, 'act_ret': 1, 'unused': None, 'io_subtype': 163, 'OPT_TYPE': None, 'arg_data': 0}]
   def updateStatusFromReceived(self, host, port, ptype, argdict, src):
      if 'ip' in argdict.keys() and host==argdict['ip']:
         if 'io_type' in argdict.keys():
            if argdict['io_type']==C.DM_INPUT_TYPE_DIGITAL:
               if 'io_subtype' in  argdict.keys() and argdict['io_subtype'] in [C.DM_DIGITAL_INPUT_TYPE_OPENCLOSE, C.DM_DIGITAL_INPUT_TYPE_CONTINUOS_OPENCLOSE]:
                  if 'act_ret' in argdict.keys():
                     if argdict['act_ret']==1:
                        status=0
                        log.debug("SETTING INPUT "+str(src)+" ON HOST "+str(host)+" AS OPEN")
                     elif argdict['act_ret']==2:
                        status=1
                        log.debug("SETTING INPUT "+str(src)+" ON HOST "+str(host)+" AS CLOSED")
                     if argdict['act_ret'] in [1, 2]:
                        dmdb.updateInputStatusFromReceived(host, src, status, argdict['io_type'], argdict['io_subtype']) 

   def sendIOSTATUSRequest(self, who, fromdb=False):
      if fromdb:
         log.debug("FROM DB "+str(who))
         for res in who:
            self.sendCommand("IOSTATUS.NOW", arg=ALLIP, act=C.IKAP_ACT_BOARD,
                  ctx=C.IKAP_CTX_SYSTEM, msgtype=C.IKAP_MSG_REQUESTCONF, ipdst=res[0])
            dmdb.updateBoardLastStatusRequest(res[0])
            reactor.callLater(int(self.config.get('ikapserver', 'timecheckoffline')), self.checkOnlineBoards, res[1])
      else:
         if who!=ALLIP:
            ip=who
         else:
            ip="255.255.255.255"
         self.sendCommand("IOSTATUS.NOW", arg=ALLIP, act=C.IKAP_ACT_BOARD,
             ctx=C.IKAP_CTX_SYSTEM, msgtype=C.IKAP_MSG_REQUESTCONF, ipdst=ip)

   def checkOnlineBoards(self, bid):
      def _checkBoard(res):
         log.debug("CHECK ONLINE BOARD "+str(bid)+" "+str(res))
         if res:
            if float(time.time())-res.last_status_update > int(self.config.get('ikapserver', 'timeoffline')):
               res.online=0
               res.save()
      dmdb.getBoardById(bid).addCallback(_checkBoard)


   def getRelayStatus(self):
      now=time.time()
      if(int(self.config.get('ikapserver', 'timeupdates'))<=now-self.lastupdatestatus):
         log.debug("Sending IOSTATUS.NOW Request")
         if(self.config.get('ikapserver', 'rollingupdates').lower() in ['yes', '1', 'y','true']):
            log.debug("ROLLING IOSTATUS")
            dmdb.getLongestUpdatedBoard(int(self.config.get('ikapserver', 'rollinnum'))).addCallback(
               self.sendIOSTATUSRequest, True
                  )
         else:
            self.sendIOSTATUSRequest(ALLIP)
      else:
         log.debug("Not sending IOSTATUS.NOW Request")

   def parseStatusRequest(self, trigger, restype='string'):

      def matchReturnDomain(match, val, reverse=False):
         if dmdomain.match(match, val):
            if restype=='int':
               if reverse: return 0
               return 1
            else:
               if reverse: return False
               return True
         if restype=='int':
            if reverse: return 1
            return 0
         else:
            if reverse: return True
            return False

      def parseReturn(qres, reverse=False):
         qr=False
         if type(qres).__name__=='int' and restype=='int':
            qr=qres
         else:
            if type(qres).__name__=='int':
               qres=str(qres)
            if qres and len(qres)>0:
               try:
                  qr=qres[0][0]
               except:
                  if type(qres).__name__=='str':
                     qr=qres
                  elif restype=='string':
                     qr=str(qres)
                  else:
                     qr=False
         if qr:
            if restype in ['int','bool']:
               if qr in ["1",1,'true','y','si','yes']:
                  if restype=='int':
                     if reverse: return 0
                     return 1
                  else: # restype=='bool':
                     if reverse: return False
                     return True
            else:
               return qr
         if restype=='int':
            if reverse: return 1
            return 0
         else:
            if restype=='bool' and reverse: return True
            return False
            

      def doQuery(sqlstring, reverse=False):
         return dmdb.Registry.DBPOOL.runQuery(sqlstring).addCallback(parseReturn, reverse)


      reverse=False
      if trigger.startswith("REV ") or trigger.startswith("REV:") and restype!='string':
         reverse=True
         trigger=trigger[4:]

      if not reverse:
         defres=False
         if restype=='int':
            defres=0
      else:   
         defres=True
         if restype=='int':
            defres=1

      ret=defer.succeed(defres)
      if trigger.startswith("FILE ") or trigger.startswith("FILE:"):
         if os.path.isfile(trigger[5:].split()[0]):
            f = open(trigger[5:].split()[0], "r")
            ret=defer.succeed(parseReturn(f.read(), reverse))
            f.close()
      if trigger.startswith("FILEEXISTS ") or trigger.startswith("FILEEXISTS:"):
         if os.path.isfile(trigger[11:].split()[0]):
            ret=defer.succeed(parseReturn('1', reverse))
         else:
            ret=defer.succeed(parseReturn('0', reverse))
      elif trigger.startswith("SYSTEM ") or trigger.startswith("SYSTEM:"):
         cmdline=trigger[7:]
         ret=subprocess.Popen(cmdline.replace("\r\n", " "),
            shell=True, stdout=subprocess.PIPE,preexec_fn = os.setsid, close_fds=True)
         ret=defer.succeed(parseReturn(ret.communicate()[0], reverse))
      elif trigger.startswith("SQL ") or trigger.startswith("SQL:"):
         sqlstring = trigger[4:]
         ret=doQuery(sqlstring, reverse)
      elif trigger.startswith("TMPFLAG ") or trigger.startswith("TMPFLAG:"):
         fl=trigger[8:].split()
         if len(fl)>0:
            try:
               ret=doQuery("SELECT COUNT(name) FROM flags WHERE name='"+str(fl[0])+"'", reverse)
            except:
               pass
      elif trigger.startswith("CRONSTATUS ") or trigger.startswith("CRONSTATUS:"):
         tid=trigger[11:].split()
         if len(tid)>0 and genutils.is_number(tid[0]):
            try:
               ret=doQuery("SELECT active FROM timers WHERE id="+str(tid[0]), reverse)
            except:
               pass
      elif trigger.startswith("BOARDSTATUS ") or trigger.startswith("BOARDSTATUS:"):
         bname=trigger[12:].split()
         if len(bname)>0:
            try:
               ret=doQuery("SELECT online FROM dmboards WHERE name='"+str(bname[0])+"'", reverse)
            except:
               pass
      elif trigger.startswith("INPSTATUS ") or trigger.startswith("INPSTATUS:"):
         tid=trigger[10:].split()
         if len(tid)>0 and genutils.is_number(tid[0]):
            try:
               ret=doQuery("SELECT status FROM inpstatus WHERE buttonid="+str(tid[0]), reverse)
            except:
               pass
      elif trigger.startswith("RELSTATUS ") or trigger.startswith("RELSTATUS:"):
         tid=trigger[10:].split()
         if len(tid)>0 and genutils.is_number(tid[0]):
            try:
               ret=doQuery("SELECT status FROM relstatus WHERE buttonid="+str(tid[0]), reverse)
            except:
               pass
      elif trigger.startswith("AMPSTATUS ") or trigger.startswith("AMPSTATUS:"):
         if ':' in trigger:
            amp=trigger[10:].split(":")
         else:
            amp=trigger[10:].split()
         if len(amp)>0 and restype=='string':
            if genutils.is_number(amp[0]):
               try:
                  ret=doQuery("SELECT ampere from relstatus WHERE buttonid="+str(amp[0]), reverse=False)
               except:
                  pass
         elif len(amp)>2 and restype in ['bool','int']:
            if genutils.is_number(amp[0]) and amp[1] in ['<=','>=','=','!=','>','<'] and genutils.is_number(amp[2]):
               try:
                  ret=doQuery("SELECT COUNT(ampere) from relstatus where ampere"+str(amp[1])+str(amp[2])+" and buttonid="+str(amp[0]), reverse)
               except:
                  pass
               
      elif trigger.startswith("ANASTATUS ") or trigger.startswith("ANASTATUS:"):     
         if ':' in trigger:
            ana=trigger[10:].split(":")
         else:
            ana=trigger[10:].split()
         if len(ana)>0 and restype=='string':
            if genutils.is_number(ana[0]):
               try:
                  ret=doQuery("SELECT status from anastatus WHERE buttonid="+str(ana[0]), reverse=False)
               except:
                  pass
         elif len(ana)>2 and restype in ['bool','int']:
            if genutils.is_number(ana[0]) and ana[1] in ['<=','>=','=','!=','>','<'] and genutils.is_number(ana[2]):
               try:
                  ret=doQuery("SELECT COUNT(status) from anastatus where status"+str(ana[1])+str(ana[2])+" and buttonid="+str(ana[0]), reverse)
               except:
                  pass
      elif trigger.startswith("AMPDOMAIN ") or trigger.startswith("AMPDOMAIN:"):
         dmctx=""
         if ':' in trigger:
            dmd=trigger[10:].split(":")
         else:
            dmd=trigger[10:].split()
         if len(dmd)>1 and restype=='string' and dmd[0] in ['SUM','AVG','MIN','MAX','COUNT']:
            try:
               ret=doQuery("select "+dmd[0]+"""(relstatus.ampere) from relstatus,relay
                           WHERE relstatus.buttonid=relay.id AND DMDOMAIN(relay.domain, '"""+str(dmd[1])+"')=1", reverse=False)
            except:
               pass
         elif restype in ['bool','int'] and len(dmd)>3 and dmd[0] in ['SUM','AVG','MIN','MAX','COUNT'] and dmd[2] in ['<=','>=','=','!=','>','<']:
            try:
               ret=doQuery("SELECT IF((select "+dmd[0]+"""(relstatus.ampere) from relstatus,relay
                           WHERE relstatus.buttonid=relay.id AND DMDOMAIN(relay.domain, '"""+str(dmd[1])+"')=1)"+dmd[2]+dmd[3]+",1,0)", reverse)
            except:
               pass
      elif trigger.startswith("ANADOMAIN ") or trigger.startswith("ANADOMAIN:"):
         dmctx=""
         if ':' in trigger:
            dmd=trigger[10:].split(":")
         else:
            dmd=trigger[10:].split()
         if len(dmd)>1 and restype=='string' and dmd[0] in ['SUM','AVG','MIN','MAX','COUNT']:
            try:
               ret=doQuery("select "+dmd[0]+"""(status) from anastatus
                           WHERE DMDOMAIN(ananame, '"""+str(dmd[1])+"')=1", reverse=False)
            except:
               pass
         elif restype in ['bool','int'] and len(dmd)>3 and dmd[0] in ['SUM','AVG','MIN','MAX','COUNT'] and dmd[2] in ['<=','>=','=','!=','>','<']:
            try:
               ret=doQuery("SELECT IF((select "+dmd[0]+"""(status) from anastatus
                           WHERE DMDOMAIN(ananame, '"""+str(dmd[1])+"')=1)"+dmd[2]+dmd[3]+",1,0)", reverse)
            except:
               pass
      elif trigger.startswith("RELDOMAIN ") or trigger.startswith("RELDOMAIN:"):
         dmctx=""
         if ':' in trigger:
            dmd=trigger[10:].split(":")
         else:
            dmd=trigger[10:].split()
         if len(dmd)>1 and genutils.is_number(dmd[1]):
            dmctx=" AND relay.ctx='"+dmd[1]+"'"
         try:
            if reverse:
               ret=doQuery("""select IF(max(relstatus.status)>0,0,1) from relstatus,relay where 
                  relstatus.buttonid=relay.id AND DMDOMAIN(relay.domain,'"""+str(dmd[0])+"')=1"+dmctx, reverse=False)
            else:
               ret=doQuery("""select min(relstatus.status) from relstatus,relay where 
                  relstatus.buttonid=relay.id AND DMDOMAIN(relay.domain,'"""+str(dmd[0])+"')=1"+dmctx, reverse=False);
         except:
            pass
      elif trigger.startswith("INPDOMAIN ") or trigger.startswith("INPDOMAIN:"):
         dmd=trigger[10:].split()
         try:
            if reverse:
               ret=doQuery("select IF(max(status)>0,0,1) FROM inpstatus WHERE DMDOMAIN(inpname, '"+str(dmd[0])+"')=1", reverse=False)
            else:
               ret=doQuery("select min(status) FROM inpstatus WHERE DMDOMAIN(inpname, '"+str(dmd[0])+"')=1", reverse=False)
         except:
            pass
      elif trigger.startswith("NETSTATUS"):
         if restype in ['int', 'bool']:
            try:
               testvalue=trigger[10:].split()[0]
               ret=dmdb.getNetStatus().addCallback(matchReturnDomain, testvalue, reverse)
            except:
               pass
         else:
            ret=defer.succeed(dmdb.getNetStatus())
      elif trigger.startswith("STATUS ") or trigger.startswith("STATUS:"):
         if ':' in trigger:
            st=trigger[7:].split(':')
         else:
            st=trigger[7:].split()
         if restype in ['string','int']:
            reverse=False
         if restype in ['bool','int'] and len(st)>2 and st[1] in ['<=','>=','=','!=','>','<','domain']:
            if st[1]=='domain':
               try:
                  ret=doQuery("""SELECT COUNT(value) FROM statusrealtime 
                        WHERE DMDOMAIN(status_name, '"""+str(st[0])+"')=1 AND DMDOMAIN(value,'"+st[2]+"')=1", reverse)
               except:
                  pass
            elif genutils.is_number(st[2]):
               try:
                  ret=doQuery("""SELECT COUNT(value) FROM statusrealtime 
                        WHERE DMDOMAIN(status_name, '"""+str(st[0])+"')=1 AND CONVERT(value, SIGNED)="+st[1]+st[2], reverse)
               except:
                  pass
         elif restype in ['bool','int'] and len(st)==2 and genutils.is_number(st[1]):
            try:
               ret=doQuery("""SELECT COUNT(value) FROM statusrealtime 
                  WHERE DMDOMAIN(status_name, '"""+str(st[0])+"')=1 AND CONVERT(value, SIGNED)="+st[1], reverse) 
            except:
               pass
         elif restype=='string' and len(st)>0:
            try:
               ret=doQuery("SELECT value FROM statusrealtime WHERE DMDOMAIN(status_name,'"+str(st[0])+"')=1")
            except:
               pass
      elif trigger.startswith("UNIQUE ") or trigger.startswith("UNIQUE:"):
         if ':' in trigger:
            st=trigger[7:].split(':')
         else:
            st=trigger[7:].split()
         if restype in ['string','int']:
            reverse=False

         if restype in ['bool','int'] and len(st)>2 and st[1] in ['<=','>=','=','!=','>','<','domain']:
            if st[1]=='domain':
               try:
                  ret=doQuery("""SELECT COUNT(value) FROM uniques
                        WHERE DMDOMAIN(name, '"""+str(st[0])+"')=1 AND DMDOMAIN(value,'"+st[2]+"')=1", reverse)
               except:
                  pass
            elif genutils.is_number(st[2]):
               try:
                  ret=doQuery("""SELECT COUNT(value) FROM uniques
                        WHERE DMDOMAIN(name, '"""+str(st[0])+"')=1 AND CONVERT(value, SIGNED)"+st[1]+st[2], reverse)
               except:
                  pass

         elif restype=='string' and len(st)>0:
            try:
               ret=doQuery("SELECT value FROM uniques WHERE DMDOMAIN(name,'"+str(st[0])+"')=1")
            except:
               pass

      elif trigger.startswith('DAYREAL'):
         ret=defer.succeed(self.sun.getReal()['status']).addCallback(parseReturn, reverse)
      elif trigger.startswith('DAYMAX'):
         ret=defer.succeed(self.sun.getMax()['status']).addCallback(parseReturn, reverse)
      elif trigger.startswith('DAYCIVIL'):
         ret=defer.succeed(self.sun.getCivil()['status']).addCallback(parseReturn, reverse)
      elif trigger.startswith('DAYASTRO'):
         ret=defer.succeed(self.sun.getAstro()['status']).addCallback(parseReturn, reverse)

      elif trigger=="TRUE" or trigger=="1":
         ret= defer.succeed(1).addCallback(parseReturn, reverse)
      elif trigger=="FALSE" or trigger=="0":
         ret= defer.succeed(0).addCallback(parseReturn, reverse)
      return ret

   def _retriveActionStatus(self, ret):
      def _actionStatusResult(sret2, sret1, res):
         if res:
            ACTION_STATUS[res.id] = {'status': int(sret1), 'status2': int(sret2), 'id': res.id, 'buttonid': res.id}
            log.debug("updating status for action "+str(res.id)+":"+str(ACTION_STATUS[res.id]))
            dmdb.updateActionStatus(res.id, int(sret1), int(sret2))

      def _secondStatus(sret1, res):
         if res.status2:
            try:
               return self.parseStatusRequest(res.status2, restype='int').addCallback(_actionStatusResult, sret1, res)
            except:
               return _actionStatusResult(0, 0, res)
         else:
            if res.status:
               return _actionStatusResult(0, sret1, res)

      if(self.actstatusremain>0):
         res=ret[self.actstatusremain-1]
         if res.status:
            try:
               self.parseStatusRequest(res.status, restype='int').addCallback(_secondStatus, res)
            except:
                _secondStatus(0, res)
         else:
            _secondStatus(0, res)

      if(self.actstatusremain>0):
         self.actstatusremain=self.actstatusremain-1
         reactor.callLater(.05, self._retriveActionStatus, ret)
         
   def _actionStatus(self, ret):
      if ret:
         self.actstatusremain=len(ret)
      self._retriveActionStatus(ret)

   def actionStatus(self, actid=False):
      
      if(self.actstatusremain==0 or actid):
         qstr='active=1'
         if actid:
            qstr+=" AND id=%s" %str(actid)
         r=dmdb.Actions.find(where=[qstr],orderby="position,button_name ASC")
         r.addCallback(self._actionStatus)

   def _sendNotify(self, nsource, username, msg, expiretime=0):
      def _inserted(res):
         for c in self.clients.getAll():
            try:
               if c['session'].mind.perms.username==username:
                  self.clientSend('notify',{'msg':msg,'nid':res.id,'source':res.source}, c['session'])
            except:
               pass
      dmdb.insertNotify(nsource, username, msg, expiretime).addCallback(_inserted)
 
   def clientSend(self, event, data, session=False):
      if not session:
         for c in self.clients.getAll():
            try:
               #if not 'ts' in data.keys():
               #   data['ts'] = float(time.time())
               c['session'].sse.sendJSON(event=event, data=data)
            except:
               pass
      else:
         try:
            session.sse.sendJSON(event=event, data=data)
         except:
            pass
     
   def executeAction(self, command):
      def multipleInsertNotify(dbres, nsrc, expire, msg):
         if dbres:
            for ue in dbres:
               self._sendNotify(nsrc, ue.username, msg, expire)
     
      events.postEvent(events.ActionEvent(command))
      if command.startswith("SYSTEM "):
         log.debug(command)
         subprocess.Popen(
            command.replace("SYSTEM ","").replace("\r\n", " "), 
            shell=True, preexec_fn = os.setsid)
      elif command.startswith("NETSTATUS "):
         try:
            nst=command.split()[1]
         except:
            nst="DEFAULT"
         dmdb.updateNetStatus(nst).addCallback(self.sendNetStatus, True)
      elif command.startswith("EMAIL "):
         mname=" ".join(command.split()[1:])
         email.sendEmailByName(mname)

      elif command.startswith("NOTIFY ") or command.startswith("NOTIFY:"):
         expire=time.time()+float(self.config.get("general", "notify_expiretime"))
         com=command[7:]
         csrc=com.split()[0]
         cdst=com.split()[1]
         msg=" ".join(com.split()[2:])
         
         if cdst=='all' and not ':' in cdst:
            dmdb.getAllUsers().addCallback(multipleInsertNotify, csrc, expire, msg)
         elif ':' in cdst:
            tdst=cdst.split(':')[0]
            dst=cdst.split(':')[1]
            if tdst=='user':
               self._sendNotify(csrc, dst, msg, expire)
            elif tdst=='group':
               dmdb.getUsersInGroup(dst).addCallback(multipleInsertNotify, csrc, expire, msg)


      elif command.startswith("SQL ") or command.startswith("SQL:"):
         sqlstring=command[4:]
         try:
            dmdb.runOperation(sqlstring)
         except:
            pass

      elif command.startswith("TMPFLAG ") or command.startswith("TMPFLAG:"):
         if ':' in command:
            fc=command[8:].split(':')
         else:
            fc=command[8:].split()
         if len(fc)>1:
            if genutils.is_number(fc[1]):
               expire=time.time()+float(fc[1])
               dmdb.insertFlag(fc[0], expire)
         elif len(fc)>0:
               dmdb.insertFlag(fc[0])               

      elif command.startswith("STATUS ") or command.startswith("STATUS:"):
         if ':' in command:
            fc=command[8:].split(':')
         else:
            fc=command[8:].split()
         if len(fc)>1:
            dmdb.updateStatusRealtime(fc[0], fc[1])

      elif command.startswith("CRON "):
         try:
            cact=str(command.split()[1]).lower()
            tid=int(command.split()[2])
            if cact in ['enable','disable','change']:
               sqlstring="update timers set active="
               if cact=='change':
                  sqlstring+="IF(active=1, 0, 1)"
               elif cact=='disable':
                  sqlstring+="0"
               elif cact=='enable':     
                  sqlstring+="1"
            sqlstring+=" where id="+str(tid)
            dmdb.runOperation(sqlstring)
         except:
            pass
      elif command.startswith("PLUGIN "):
         pname=command.replace("PLUGIN ","").split(":")[0]
         preq=command.replace("PLUGIN ","").split(":")[1:]
         self.plugins.push_request(pname, preq)
      elif command.startswith("PHONECALL "):
         command=command.replace("PHONECALL ","")
         callfrom=command.split()[0]
         callto=command.split()[1]
         self.astmanager.startCall(callfrom, extensionto=callto)
      elif command.startswith("PHONESAY "):
         command=command.replace("PHONESAY ","")
         ptext=command.split("] ")[0][1:]
         popts=command.split("] ")[1].split()[0]
         pretry=1
         pinterval=30
         engine="festival"
         preplay=4
         tlang='it'
         if ":" in popts:
            for opt in popts.split(","):
               popt=opt.split(":")
               if popt[0]=='retry':
                  pretry=int(popt[1])
               elif popt[0]=='interval':
                  pinterval=int(popt[1])
               elif popt[0]=='replay':
                  preplay=int(popt[1])
               elif popt[0]=='engine' and str(popt[1]) in ['festival','google']:
                  engine=str(popt[1])
               elif popt[0]=='lang':
                  ttslang=str(popt[1])
            pnumbers=command.split("] ")[1].split()[1:]
         else:
            pnumbers=command.split("] ")[1].split()
         self.astmanager.phoneSay(ptext, pnumbers, retry=int(pretry),
                                   interval=int(pinterval), replay=int(preplay), engine=str(engine))

      elif command.startswith("PHONEPLAY "):
         command=command.replace("PHONEPLAY ","")
         pfile=command.split()[0]
         popts=command.split()[1]
         pretry=1
         pinterval=30
         preplay=4
         if ":" in popts:
            for opt in popts.split(","):
               popt=opt.split(":")
               if popt[0]=='retry':
                  pretry=int(popt[1])
               elif popt[0]=='interval':
                  pinterval=int(popt[1])
               elif popt[0]=='replay':
                  preplay=int(popt[1])
            pnumbers=command.split()[2:]
         else:
            pnumbers=command.split()[1:]
         self.astmanager.phonePlay(pfile, pnumbers, retry=int(pretry), 
                                   interval=int(pinterval), replay=int(preplay))



   def parseAction(self, res, restype="action"):
      if restype=="action":
         try:
            timedict=parseCronLine(
               " ".join(
                   [res.min, res.hour, res.day, res.month, res.dayofweek]))
         except:
            return
         loctime=time.localtime()
         if(loctime.tm_mon in timedict["months"]
            and loctime.tm_mday in timedict["doms"]
            and converWday(loctime.tm_wday) in timedict["dows"]
            and loctime.tm_hour in timedict["hours"]
            and loctime.tm_min in timedict["minutes"]):

            if (time.time()-float(res.lastrun)) < float(res.min_time):
               return
            elif res.limit_run:
               if int(res.run_count) > 0:
                  res.run_count=int(res.run_count)-1
               else:
                  return
            res.lastrun=time.time()
            res.save()
         else:
            return

      if genutils.isTrue(res.execute):
         self.executeAction(res.command)
      if genutils.isTrue(res.ikapacket):
         self.sendCommand(res.ikap_dst, act=res.ikap_act, ctx=res.ikap_ctx, msgtype=res.ikap_msgtype,
            arg=res.ikap_arg, src=res.ikap_src, ipdst=str(res.ipdest))
      if genutils.isTrue(res.launch_sequence) and res.launch_sequence_name != None:
         dmdb.getSequence(res.launch_sequence_name).addCallback(self.manageSequence)

      if restype=="sequence":
         pass

   def sendRelayCmd(self, res, act=False):
      # NOTE: We have a cron than use lastchange field to send
      #       any sync status data from the relstatus table.
      #       It check lastchange timestamp every 500ms, 
      #       and this mean that if we have an update after last
      #       update but before our sendCommand, we can have strange beaviour.
      #       For example, let me say i switch off a relay with amperomepert
      #       on board. The amperometer has updated the relstatus before us
      #       and after last update timer. In case our next sync will be triggered
      #       in the time between when we send our command and when we get the
      #       answer, we will have our button in the gui "fliker" on/off.
      #       on the browser of the client has sent the command.
      #
      #       To avoid this we can just set backward the lastchange time when we
      #       expect a relay to answer to our command. This way we will eventually
      #       drop an unusefull sync, but we will drop it for all clients.
      # 
      #       I think this is acceptable as to limit this sync drop only
      #       for the client that has sent the command, we will be in a situation
      #       where potentially a large number of clients will be a DoS for too
      #       many timers scheduled.
      try:
         dmdb.backwardLastChange('relstatus', res.id, self.lastsync-0.5)   
      except:
         log.error("Cannot change lastchange field in relstatus for record "+str(res))

      if not act:
         act=res.act
      try:
         self.sendCommand(res.domain, act=act, ctx=res.ctx, msgtype=res.msgtype, ipdst=str(res.ipdest))
      except:
         self.sendCommand(res.domain, act=act, ctx=res.ctx, msgtype=res.msgtype)
      return res


   def sequenceConditionTest(self, testvalue):

      testvalue=str(testvalue)
      return self.parseStatusRequest(testvalue, restype='bool')

   def sequenceNext(self, seqname, seqtype):
      dmdb.getSequenceStep(seqname).addCallback(self.sequenceStep, seqname, seqtype)

   def sequenceStep(self, res, seqname, seqtype, first=False):

      log.info("SEQUENCE STEP: "+str(seqname)+" "+str(res)+" "+str(first))
      if not res and not first:
         # Sequence is finished!
         log.info("SEQUENCE "+str(seqname)+" finished? "+str(res)+" "+str(first))
         if seqtype==C.SEQUENCE_TYPE_CONTINUE:
            dmdb.getSequence(seqname).addCallback(self.stopSequence)
         # XXX E gli altri tipi?
      else:
         if first:
            dmdb.cleanSequence(seqname).addCallback(self.sequenceStep, seqname, seqtype)
         else:
            exstep=False
            try:
               timedict=parseCronLine(
                  " ".join(
                     [res.min, res.hour, res.day, res.month, res.dayofweek]))
               loctime=time.localtime()
               if(loctime.tm_mon in timedict["months"]
                  and loctime.tm_mday in timedict["doms"]
                  and converWday(loctime.tm_wday) in timedict["dows"]
                  and loctime.tm_hour in timedict["hours"]
                  and loctime.tm_min in timedict["minutes"]):
                  exstep=True
            except:
               pass                 
            
           
            usecon=False
            immediatenext=False
            conval=defer.succeed(True)
            if genutils.isTrue(res.use_condition) and exstep:
               usecon=True
               exstep=False
               immediatenext=True
               conval=self.sequenceConditionTest(res.condition)


            return conval.addCallback(self._sequenceStep, usecon, exstep, immediatenext, res, seqname, seqtype)

   def _sequenceStep(self, conval, usecon, exstep, immediatenext, res, seqname, seqtype):
      res.step_done=1
      res.save()

      def doNextStep(*a):
         s=sequences.SequenceRegistry()
         rid=reactor.callLater(0, self.sequenceNext, seqname, seqtype)
         s.add_sequence(seqname, rid)
         return

      if usecon:
         log.info("Sequence condition check (RESULT:"+str(conval)+" CONDITION: "+str(res.condition_act)+" ACTVALUE: "+str(res.condition_actvalue)+")")
         if genutils.isTrue(conval):
            if res.condition_act=='GOTOSTEP':
               if genutils.is_number(res.condition_actvalue):
                  return dmdb.setNextStep(int(res.condition_actvalue)).addCallback(
                           doNextStep
                        )  
            elif res.condition_act=='GOTOSEQ':
               dmdb.getSequence(res.condition_actvalue).addCallback(
                  self.manageSequence, 'sequence')
               if seqtype==C.SEQUENCE_TYPE_CONTINUE:
                  dmdb.getSequence(seqname).addCallback(self.stopSequence)
               return
            elif res.condition_act=='STOP':
               if seqtype==C.SEQUENCE_TYPE_CONTINUE:
                  dmdb.getSequence(seqname).addCallback(self.stopSequence)
               return
            elif res.condition_act=='RESTART':
               return dmdb.getSequence(seqname).addCallback(
                  self.manageSequence, 'restart')
            elif res.condition_act=='IGNORE':
               # doesn't execute this step
               # and pass to next step in normal timing
               immediatenext=False
            elif res.condition_act=='NEXT':
               # pass to the next step immediatly
               pass
            elif res.condition_act=='EXECUTEIF':
               # Execute this step
               # normally and go to next step in normal timing
               exstep=True
               immediatenext=False


      if exstep:
         try:
            events.postEvent(events.SequenceEvent("STEP", seqname, seqtype, step=res.id))
         except:
            pass
         try:
            self.parseAction(res, 'sequence')
         except:
            log.debug("ParseAction failed for sequence name "+str(seqname)+" at step "+str(res.id))
         res.lastrun=time.time()
      res.save() 
      if seqtype==C.SEQUENCE_TYPE_CONTINUE:
         nextt=0.1
         if res.time_next > 0.1:
            nextt=res.time_next
         if not exstep and not usecon:
            nextt=0
         elif not exstep and usecon:
            if immediatenext:
               nextt=0
             
         s=sequences.SequenceRegistry()
         rid=reactor.callLater(nextt, self.sequenceNext, seqname, seqtype)
         s.add_sequence(seqname, rid)


   def stopSequence(self, res):
      res.running=0
      events.postEvent(events.SequenceEvent("STOP", res.name, res.type))
      res.save()
      s=sequences.SequenceRegistry()
      rid=s.get_sequence(res.name)
      if rid:
         s.del_sequence(res.name)

   def initSequence(self, res):
      res.running=1
      res.lastrun=time.time()
      
      res.save()
      return dmdb.getSequenceStep(res.name)


   def manageSequence(self, res, cmdsrc='action'):
      if (not res
         or ((time.time()-float(res.lastrun)) < float(res.min_time)
            and cmdsrc not in ['restart','sequence'])):
         return
      events.postEvent(events.SequenceEvent("REQUESTED", res.name, res.type, cmdsrc))
      if res.type==C.SEQUENCE_TYPE_CONTINUE:
         if res.running:
            if cmdsrc not in ['cron', 'motion', 'restart', 'sequence','statuses']: #, 'voip']:
               self.stopSequence(res)
            return
         else:
            # sequence start
            self.initSequence(res).addCallback(
               self.sequenceStep ,res.name, res.type, True)
            

   def executeStatus(self, res):

      def queryReturn(qres):
         try:
            if qres and len(qres)>0:
               return qres[0][0]
         except:
            if type(qres).__name__=='str':
               return qres
         return False

      def doQuery(sqlstring):
         return dmdb.Registry.DBPOOL.runQuery(sqlstring).addCallback(queryReturn)

      log.debug("STATUSES EXECUTE ID: "+str(res.id)+" NAME: "+str(res.status_name))
      events.postEvent(events.StatusEvent('EXECUTE', res.id, res.status_name))
      if res:
         if not genutils.isTrue(res.active):
            ss=statuses.StatusesRegistry()
            ss.del_status(res.id)
            return
         ret=defer.succeed(False)
         trigger=res.trigger
         self.parseStatusRequest(trigger, restype='string').addCallback(self.manageStatusAction, res)

   @defer.inlineCallbacks
   def manageStatusAction(self, status, res):
      changed=False
      if status:
         # detect if changed
         oldstatus=yield dmdb.getStatusRealtime(res.status_name)
         # NOTE: we have a changed status only if oldstatus exists
         #       or we will start onchange events even on the first call
         #       (for example at the reboot!)
         #if not oldstatus or oldstatus!=status:
         if oldstatus and oldstatus!=status:
            changed=True

         # update statusrealtime table
         dmdb.updateStatusRealtime(res.status_name, status, changed)

         # execute action if needed
         rtact=yield dmdb.getStatusAction(res.status_name)
         for ract in rtact:
            if (ract.action_type=='onchange' and changed) or ract.action_type=='continouos':
               try:
                  timedict=parseCronLine(
                     " ".join(
                        [ract.min, ract.hour, ract.day, ract.month, ract.dayofweek]))
               except:
                  continue
               loctime=time.localtime()
               if(loctime.tm_mon in timedict["months"]
                  and loctime.tm_mday in timedict["doms"]
                  and converWday(loctime.tm_wday)  in timedict["dows"]
                  and loctime.tm_hour in timedict["hours"]
                  and loctime.tm_min in timedict["minutes"]):
                     # Do nothing mean "ok, maybe it's to be executed
                     pass  
               else:
                  continue

               if genutils.is_number(status) and genutils.is_number(ract.value) and ract.selector in ['>','<','>=','<=']:
                  if ract.selector=='>':
                     if float(status)<=float(ract.value):
                        continue
                  elif ract.selector=='<':
                     if float(status)>=float(ract.value):
                        continue
                  elif ract.selector=='>=':
                     if float(status)<float(ract.value):
                        continue
                  elif ract.selector=='<=':
                     if float(status)>float(ract.value):
                        continue
               elif ract.selector in ['=','!=','domain']:
                  if ract.selector=='=':
                     if str(ract.value) != str(status):
                        continue
                  elif ract.selector=='!=':
                     if str(ract.value) != str(status):
                        continue
                  elif ract.selector=='domain':
                     if not dmdomain.match(str(ract.value), str(status)):
                        continue
               else:
                  continue
 
               if (time.time()-float(ract.lastrun)) < float(ract.min_time):
                  continue

               # if we are here, the actions is to be executed!
               ract.lastrun=time.time()
               ract.save()

               if genutils.isTrue(ract.ikapacket):
                  self.sendCommand(ract.ikap_dst, act=ract.ikap_act, ctx=ract.ikap_ctx, msgtype=ract.ikap_msgtype,
                     arg=ract.ikap_arg, src=ract.ikap_src, ipdst=str(ract.ipdest))
               if genutils.isTrue(ract.use_command):
                  reactor.callLater(ract.retard, self.executeAction, ract.command)
               if genutils.isTrue(ract.launch_sequence) and ract.launch_sequence_name != None:
                  reactor.callLater(ract.retard, self.launchSequence, ract.launch_sequence_name, 'statuses')



   def launchSequence(self, name, sequencecaller='unknown'):
      return dmdb.getSequence(name).addCallback(self.manageSequence, sequencecaller)

   def executeCrontab(self, res):
      log.info("TIMER EXECUTE ID: "+str(res.id)+" NAME: "+str(res.timer_name))
      events.postEvent(events.TimerEvent('EXECUTE', res.id, res.timer_name))
      if not genutils.isTrue(res.active):
         cs=crontabs.CrontabsRegistry()
         cs.del_cron(res.id)
      elif res.jump_next > 0:
         res.jump_next=res.jump_next-1
         
         res.save()
      elif res.limit_run > 0:
         if res.run_count > 0:
            res.run_count=res.run_count-1
            res.lastrun=time.time()
            
            res.save()
            if genutils.isTrue(res.ikapacket):
               self.sendCommand(res.ikap_dst, act=res.ikap_act, ctx=res.ikap_ctx, msgtype=res.ikap_msgtype,
                  arg=res.ikap_arg, src=res.ikap_src, ipdst=str(res.ipdest))
            if genutils.isTrue(res.use_command):
               self.executeAction(res.command)
            if genutils.isTrue(res.launch_sequence) and res.launch_sequence_name != None:
               dmdb.getSequence(res.launch_sequence_name).addCallback(self.manageSequence, 'cron')
         else:
            cs=crontabs.CrontabsRegistry()        
            cs.del_cron(res.id)
      else:
         res.lastrun=time.time()
         
         res.save()
         if genutils.isTrue(res.ikapacket):
            self.sendCommand(res.ikap_dst, act=res.ikap_act, ctx=res.ikap_ctx, msgtype=res.ikap_msgtype,
               arg=res.ikap_arg, src=res.ikap_src, ipdst=str(res.ipdest))
         if genutils.isTrue(res.use_command):
            self.executeAction(res.command)
         if genutils.isTrue(res.launch_sequence) and res.launch_sequence_name != None:
            dmdb.getSequence(res.launch_sequence_name).addCallback(self.manageSequence, 'cron')

   
   def manageMotionDetection(self, results):
      for res in results:
         log.info("MOTION DETECTION ID: "+str(res.id)+" NAME: "+str(res.motion_name))
         if res.active!=0:

            try:
               timedict=parseCronLine(
                     " ".join(
                        [res.min, res.hour, res.day, res.month, res.dayofweek]))
            except:
               continue
            loctime=time.localtime()
            if(loctime.tm_mon in timedict["months"]
               and loctime.tm_mday in timedict["doms"]
               and converWday(loctime.tm_wday)  in timedict["dows"]
               and loctime.tm_hour in timedict["hours"]
               and loctime.tm_min in timedict["minutes"]):

               if time.time()-float(res.lastrun) < float(res.min_time):
                  continue
               res.lastrun=time.time()            
               
               res.save()

               if genutils.isTrue(res.ikapacket):
                  self.sendCommand(res.ikap_dst, act=int(speechres["action"]), ctx=res.ikap_ctx, msgtype=res.ikap_msgtype,
                     arg=res.ikap_arg, src=res.ikap_src, ipdst=str(res.ipdest))

               if genutils.isTrue(res.use_command):
                  self.executeAction(res.command)

               if genutils.isTrue(res.launch_sequence) and res.launch_sequence_name != None :
                  dmdb.getSequence(res.launch_sequence_name).addCallback(self.manageSequence, 'motion')

   def manageAsteriskAlias(self, results):
      if len(results) > 0:
         for res in results:
            log.info("Asterisk alias found id: "+str(res.id))
            if genutils.isTrue(res.launch_voipaction):
               dmdb.checkAsteriskActionByName(res.voip_action_name).addCallback(self.manageAsteriskAction)
            return str(res.contextto)+":"+str(res.aliasto)
      return 'NOALIAS'

   def manageAsteriskAction(self, results):
      if len(results) > 0:
         for res in results:
            log.info("ASTERISK ACTION ID: "+str(res.id)+" NAME: "+str(res.voipaction_name))
            if genutils.isTrue(res.active):
               try:
                  timedict=parseCronLine(
                     " ".join(
                        [res.min, res.hour, res.day, res.month, res.dayofweek]))
               except:
                  continue
               loctime=time.localtime()
               if(loctime.tm_mon in timedict["months"]
                  and loctime.tm_mday in timedict["doms"]
                  and converWday(loctime.tm_wday)  in timedict["dows"]
                  and loctime.tm_hour in timedict["hours"]
                  and loctime.tm_min in timedict["minutes"]):

                  if time.time()-float(res.lastrun) < float(res.min_time):
                     continue
                  res.lastrun=time.time()
                  
                  res.save()
                  if genutils.isTrue(res.ikapacket):
                     self.sendCommand(res.ikap_dst, act=res.ikap_act, ctx=res.ikap_ctx, msgtype=res.ikap_msgtype,
                        arg=res.ikap_arg, src=res.ikap_src, ipdst=str(res.ipdest))

                  if genutils.isTrue(res.use_command):
                     self.executeAction(res.command)
                  if genutils.isTrue(res.launch_sequence) and res.launch_sequence_name != None:
                     dmdb.getSequence(res.launch_sequence_name).addCallback(self.manageSequence, 'voip')
                  #XXX Come gestire i ko_text2speech?
                  return str(res.ok_text2speech)

         return 'NESSUNA AZIONE POSSIBILE AL MOMENTO'
      else:
         return 'NOACT'

   def manageSpeechActions(self, results, speechres={"action":False}):
      if len(results) > 0 and speechres["action"]:
         for res in results:
            log.info("SPEECH ACTION ID: "+str(res.id)+" NAME: "+str(res.speechaction_name))
            if genutils.isTrue(res.active):
               try:
                  timedict=parseCronLine(
                     " ".join(
                        [res.min, res.hour, res.day, res.month, res.dayofweek]))
               except:
                  continue
               loctime=time.localtime()
               if(loctime.tm_mon in timedict["months"]
                  and loctime.tm_mday in timedict["doms"]
                  and converWday(loctime.tm_wday) in timedict["dows"]
                  and loctime.tm_hour in timedict["hours"]
                  and loctime.tm_min in timedict["minutes"]):

                  if time.time()-float(res.lastrun) < float(res.min_time):
                     continue
                  res.lastrun=time.time()
                  res.save()
                  if genutils.isTrue(res.ikapacket):
                     # XXX Manca gestione local only e ipdest!
                     # XXX Gestire gli arg! (e lo use arg! per il received)
                     self.sendCommand(res.ikap_dst, act=int(speechres["action"]), ctx=res.ikap_ctx, msgtype=res.ikap_msgtype,
                        arg=res.ikap_arg, src=res.ikap_src, ipdst=str(res.ipdest))

                  if genutils.isTrue(res.use_command):
                     self.executeAction(res.command)
                  if genutils.isTrue(res.launch_sequence) and res.launch_sequence_name != None:
                     dmdb.getSequence(res.launch_sequence_name).addCallback(self.manageSequence, 'speech')
                  #XXX Come gestire i ko_text2speech?
                  return str(res.ok_text2speech)

         return 'NESSUNA AZIONE POSSIBILE AL MOMENTO'
      else:
         return 'NOACT'

   def manageStatuses(self, statusid):
      log.debug("STATUS MANAGE ID: "+str(statusid))
      dmdb.getStatus(statusid).addCallback(self.executeStatus)

   def manageCrontab(self, timerid):
      log.info("TIMER MANAGE ID: "+str(timerid))
      dmdb.getCron(timerid).addCallback(self.executeCrontab)

   def checkRcvArg(self, dbarg, argdict):
      try:
         arg=str(dbarg).split()
         for a in arg:
            ar=a.split(':',)
            if len(ar)>1:
               cmd=ar[0]
               sel=ar[1]
               if cmd=='OVERCURRENT':
                  if len(argdict['raw'])>1:
                     oar=struct.unpack("<B", argdict['raw'][1])[0]  
                     if int(sel)!=int(oar):
                        return False
                  else:
                     return False   
               elif cmd=='IP':
                  if argdict['ip'] is None or sel!=argdict['ip']:
                     return False
               elif cmd=='OPT':
                  sel=sel.replace('.',',')
                  if sel.startswith("RGB:"):
                     if ',' in sel:
                        sel=sel.replace("RGB:","1,")
                     else:
                        sel=sel.replace("RGB:","01")
                  elif sel.startswith("PRESET:"):
                     if ',' in sel:
                        sel=sel.replace("PRESET:","2,")
                     else:
                        sel=sel.replace("PRESET:","02")
                  elif sel.startswith("DIMMER:"):
                     if ',' in sel:
                        sel=sel.replace("DIMMER:","3,")
                     else:
                        sel=sel.replace("DIMMER:","03")
                  if ',' in sel:
                     # '255,255,255'
                     sel=map(int, sel.split(','))  
                  else:
                     # 'ffffff'
                     sel=[int(h, 16) for h in [sel[i:i+2] for i in range(0,len(sel), 2)]]
                  if len(sel)<1:
                     return False
                  if argdict['OPT_TYPE'] is None or sel[0]!=argdict['OPT_TYPE']:
                     return False
                  if len(sel)<2 and argdict['OPT_DATA']:
                     return False
                  if argdict['OPT_DATA'] is None and len(sel)>1:
                     return False
                  if sel[1:]+[0]*(len(argdict['OPT_DATA'])-len(sel[1:]))!=argdict['OPT_DATA']:
                     return False

               elif cmd=='IOTYPE':
                  if argdict['io_type'] is None or int(sel)!=argdict['io_type']:
                     return False
               elif cmd=='ACTRET':
                  if argdict['act_ret'] is None or int(sel)!=argdict['act_ret']:
                     return False
               elif cmd=='IOSUBTYPE':
                  if argdict['io_subtype'] is None or int(sel)!=argdict['io_subtype']:
                     return False
               elif cmd=='ARGDATA':
                  if argdict['arg_data'] is None:
                     return False
                  s=sel.split(':')
                  if len(s) > 1:
                     op=s[0]
                     v=s[1]
                     if op=='>' and not argdict['arg_data']>int(v):
                        return False
                     elif op=='>=' and not argdict['arg_data']>=int(v):
                        return False
                     elif op in ['=','=='] and argdict['arg_data']!=int(v):
                        return False
                     elif op=='<' and not argdict['arg_data']<int(v):
                        return False
                     elif op=='<=' and not argdict['arg_data']<=int(v):
                        return False
                  else:
                     if int(sel)!=argdict['arg_data']:
                        return False
            else:
               return False
      except:
         log.warning("Parse recv_arg failed: "+str(dbarg))              
         return False
      return True      

   def manageRecvPkt(self, res, argdict):
      # XXX Usiamo un generator o reactor.callLater?
      if res:
         log.debug("ManageRcvPkt "+str(res))
         for r in res:
            if genutils.isTrue(r.use_rcv_arg):
               if argdict and self.checkRcvArg(r.rcv_arg, argdict):
                  self.parseAction(r)
            else:
               self.parseAction(r)

   def on_callback(self, who, cmd, *args, **kwargs):
      f=getattr(self, who+'_on_'+cmd, None)
      if f and callable(f):
         return f(*args, **kwargs)


   def _callback(self, who, cmd, *args, **kwargs):
      """
         The callback that try to find an appropriate method exported
         to a higher level object by the ConvenienceCaller metaclass.

         This isn't intended to be called by the user directly, instead pass it
         to the instance of the higher level object initialization or by
         setting it using the abstraction of the ConvenienceCaller metaclass
      """
      try:
         f=getattr(self, who+'_on_'+cmd)
         if f and callable(f):
            return f
      except:
         raise AttributeError(" ".join([cmd, 'doesn\'t exists']))

   def _cmdFromAmi(self, command):
      return self._callback('ami', command)

   def _cmdFromFastAGI(self, command):
      return self._callback('fagi', command)

   def _cmdFromPlugin(self, command):
      return self._callback('plugin', command)

   def _cmdFromWeb(self, command):
      return self._callback('web', command)

   def _cmdFromDomIka(self, command):
      return self._callback('domika', command)

   def _cmdFromUPNP(self, command):
      return self._callback('upnp', command)


   def getProxy(self):
      return proxy.DomProxy

   def startUPNPService(self, *a, **kw):
      if str(self.config.get('upnp', 'enable')).lower() in ['yes', '1', 'y','true']:
         log.debug("starting UPNP Services")
         import upnp
         caller = ConvenienceCaller(self._cmdFromUPNP)
         self.upnp=upnp.startServer(caller)


   def getAuthWebServer(self):
      from nevow import appserver
      caller = ConvenienceCaller(self._cmdFromWeb)
      self.authsite =  web.getAuthResource(caller)
      return appserver.NevowSite(self.authsite)


   def getSmtp(self):
      return dmsmtp.getSmtp()

   def startAsteriskServices(self):
      if str(self.config.get('asterisk', 'manager_enable')).lower() in ['yes', '1', 'y','true']:
         caller = ConvenienceCaller(self._cmdFromAmi)
         self.astmanager = ami.UMAMIFactory(caller, self.config.get("asterisk", "manager_user"), self.config.get("asterisk", "manager_pass"))
         self.ami=self.astmanager.login(self.config.get("asterisk", "manager_ip"), int(self.config.get("asterisk", "manager_port")))

   def getFastAGI(self):
      caller = ConvenienceCaller(self._cmdFromFastAGI)
      self.fagi = fagi.getFastAGI(caller)
      return self.fagi

   def getDomIkaUDP(self):
      caller = ConvenienceCaller(self._cmdFromDomIka)
      self.udp = ikapserver.DomIkaUDP(caller)
      return self.udp

   def getDomIkaTCP(self):
      caller = ConvenienceCaller(self._cmdFromDomIka)
      self.tcp = ikapserver.DomIkaServerFactory(caller)
      return self.tcp

   def parseDBArg(self, dbarg):
      iface=self.config.get("ikapserver", "ethdev")
      try:
         to=netifaces.ifaddresses(iface)[2][0]['addr']
      except:
         try:
            to=netifaces.ifaddresses(iface+':0')[2][0]['addr']
         except:
            to='0.0.0.0'

      if not dbarg or dbarg=='':
         return {'ip': to} 

      if not ':' in dbarg:
         return dbarg

      ret={'ip': to}
      arg=str(dbarg).split()
      for a in arg:
         try:
            if ':' in a:
               ar=a.split(':',1)
               if len(ar)>1:
                  cmd=ar[0]
                  sel=ar[1]
                  if cmd=='RAW':
                     return sel
                  elif cmd=='IP':
                     ret['ip']=sel
                  elif cmd=='ARGDATA':
                     ret['arg_data']=int(sel)
                  elif cmd=='IOSUBTYPE':
                     ret['io_subtype']=int(sel)
                  elif cmd=='ACTRET':
                     ret['act_ret']=int(sel)
                  elif cmd=='IOTYPE':
                     ret['io_type']=int(sel)
                  elif cmd=='OPT':
                     sel=sel.replace('.',',')
                     if sel.startswith("RGB:"):
                        if ',' in sel:
                           sel=sel.replace("RGB:","1,")
                        else:
                           sel=sel.replace("RGB:","01")
                     elif sel.startswith("PRESET:"):
                        if ',' in sel:
                           sel=sel.replace("PRESET:","2,")
                        else:
                           sel=sel.replace("PRESET:","02")
                     elif sel.startswith("DIMMER:"):
                        if ',' in sel:
                           sel=sel.replace("DIMMER:","3,")
                        else:
                           sel=sel.replace("DIMMER:","03")
                     if ',' in sel:
                        # '255,255,255'
                        sel=map(int, sel.split(','))
                     else:
                        sel=[int(h, 16) for h in [sel[i:i+2] for i in range(0,len(sel), 2)]]
                     if len(sel)>0:
                        ret['OPT_TYPE']=sel[0]
                     if len(sel)>1:
                        ret['OPT_DATA']=sel[1:]
         except:
            pass
      return ret

   def sendUDPRAWCommand(self, data, ipdst='255.255.255.255'):
      if str(self.config.get('ikapserver', 'enable')).lower() in ['yes', '1', 'y','true']:
         if self.udp:
            self.udp.sendRawPacket(data, ipdst)

   def sendTCPRAWCommand(self, data, ipdst='255.255.255.255'):
      if str(self.config.get('ikapserver', 'tcpenable')).lower() in ['yes', '1', 'y','true']:
         if self.tcp:
            self.tcp.sendRawData(data, ipdst)

   def sendCommand(self, *k, **kw):
      if 'arg' in kw.keys():
         if 'arg_parse' in kw.keys():
            if not kw['arg_parse']==False:
               kw['arg']=self.parseDBArg(kw['arg'])
            del kw['arg_parse']
         else:
            kw['arg']=self.parseDBArg(kw['arg'])
      send=False
      if str(self.config.get('ikapserver', 'enable')).lower() in ['yes', '1', 'y','true']:
         if self.udp:
            self.udp.sendCommand(*k, **kw)
            send=True
      if str(self.config.get('ikapserver', 'tcpenable')).lower() in ['yes', '1', 'y','true']:
         if self.tcp:
            send=True
            self.tcp.sendCommand(*k, **kw)
      if send:
         log.debug("SENDING NEW COMMAND: "+str(k)+" "+str(kw))
      


   def voiceRecognized(self, txt, confidence=0.0, lang="it", voicesrc='VoIP'):
      log.debug("voiceRecognized: ["+txt+"] confidence: "+str(confidence)+" lang: "+lang+" src: "+voicesrc)

      def speechactres(res, v):
         if len(res)>0:
            return defer.succeed(
                  self.manageSpeechActions(res, v.result)).addCallback(
                  actionres, v.result)
         else:
            useoutput=genutils.isTrue(self.config.get('voiceui', 'useoutput'))
            if useoutput:
               return ('OUTPUT', False)
            return ('NOACT',False)

      def actionres(ares, vres):
         return (ares, vres)

      events.postEvent(events.SpeechRecognizedEvent(voicesrc, txt, confidence, lang))
      v=voice.VoiceUI(txt, confidence, lang)
      actres = v.getSpeechActions().addCallback(
         speechactres, v)
      return actres

   def isLocalSource(self, host, ptype='UDP4'):
      if ptype!='UDP4':
         return False
      localsources=[]
      for ifaceName in interfaces():
         localsources+=[i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET,
            [{'addr':'0.0.0.0'}])]
         try:
            localsources+=[i['broadcast'] for i in ifaddresses(ifaceName).setdefault(AF_INET,
               [{'broadcast':'0.0.0.0'}])]
         except:
            pass
         localsources+=[i['netmask'] for i in ifaddresses(ifaceName).setdefault(AF_INET,
                        [{'netmask':'0.0.0.0'}])]

      if host not in localsources:
         return False
      return True


   def parseChartSeries(self, series, chartdata, chartname):

      ret=""
      def getSelectorSubtype(serie):
         if str(serie.selector_subtype)=='back_in_time':
            ret=" AND date >= DATE_ADD(NOW(),"
            ret+=" INTERVAL -"+str(serie.selector_numopt)+" DAY)"
         elif str(serie.selector_subtype)=='limits':
            if serie.selector_start:
               ret+=" AND date >= '"+str(serie.selector_start)+"'"
            if serie.selector_stop:
               ret+=" AND date <= '"+str(serie.selector_stop)+"'"
         return ret

      def parseSelectorName(cmd, serie):
         cmd=cmd.replace("#OPTNUM#", str(serie.selector_numopt))
         cmd=cmd.replace("#NAME#", str(serie.name))
         cmd=cmd.replace("#START#",str(serie.selector_start))
         cmd=cmd.replace("#STOP#",str(serie.selector_stop))
         cmd=cmd.replace("#SUBTYPE#",str(serie.selector_subtype))
         cmd=cmd.replace("#ID#",str(serie.id))
         return cmd

      def addAxes(result, chartdata):
            axes={ 
               'xaxis': {
                  'renderer': "eval('$.jqplot.DateAxisRenderer')",
                  'tickRenderer': "eval('$.jqplot.CanvasAxisTickRenderer')",
                  'autoscale': True,
                  'tickOptions': {
                     'angle': 30
                  }
               },
               'yaxis': {
                  'min': 0,
                  'tickOptions': {}
               }
            }       
            if chartdata[0].x_numberTicks:
               if result['maxseriecount']<int(chartdata[0].x_numberTicks):
                  axes['xaxis']['numberTicks']=result['maxseriecount']
               else:
                  axes['xaxis']['numberTicks']=int(chartdata[0].x_numberTicks)
            if chartdata[0].x_formatString:
               axes['xaxis']['tickOptions']['formatString']=chartdata[0].x_formatString

            if chartdata[0].y_numberTicks:
               axes['yaxis']['numberTicks']=int(chartdata[0].y_numberTicks)

            if chartdata[0].y_formatString:
               axes['yaxis']['tickOptions']['formatString']=chartdata[0].y_formatString
            else:
               axes['yaxis']['tickOptions']['formatString']='%.'+str(chartdata[0].y_label_precision)+'f'

            result['opt']['axes']=axes

            return result

      def sqlQuery(result, query, idx):
         log.debug(query)
         return dmdb.runQuery(query).addCallback(addResult, idx, result)

      def addResult(res, idx, result):
         data=[]
         for l in res:
            data.append([l[0].strftime("%Y-%m-%d %H:%M:%S"), l[1]])
         result['data'].append(data)
         if len(res) > result['maxseriecount']:
            result['maxseriecount'] = len(res)
         return result
         
      def hourlySqlQuery(result, query, idx, serie):
         return dmdb.runQuery(query).addCallback(hourlyResult, idx, result, serie)

      def hourlyResult(res, idx, result, serie):
         from datetime import datetime
         today=datetime.strftime(datetime.now(), '%Y-%m-%d')
         hournow=int(datetime.strftime(datetime.now(), '%H'))
         data=[]
         for l in res:
            if str(serie.selector_subtype)=='back_in_time' and today==str(l[0]):
               maxh=hournow+1
            else:
               maxh=24
            for h in xrange(0,24):
               data.append([str(l[0])+" "+str(h).zfill(2)+":00AM", l[h+1] ])
         result['data'].append(data)
         if len(data) > result['maxseriecount']:
            result['maxseriecount'] = len(data)
         return result

      log.debug('PARSE CHART SERIES FOR '+str(chartname))
      grid_shadow=True
      grid_border=True
      legend_show=True
      if chartdata[0].grid_shadow=='false':
         grid_shadow=False
      if chartdata[0].grid_border=='false':
         grid_border=False
      if chartdata[0].legend_show=='false':
         legend_show=False
      opt={ 'title': chartdata[0].title,
            'legend':{
               'show': legend_show,
               'location': chartdata[0].legend_position,
               'renderOptions': {
                  'placement': chartdata[0].legend_placement
               }
            },
            'grid':{
               'shadow': grid_shadow,
               'drawBorder': grid_border,
               'background': chartdata[0].grid_background
            },
            'axes':{},
            'highlighter':{'show':True,'sizeAdjust': 7.5},
            'cursor':{'show':False},
            'series':[],
            'seriesDefaults': {'rendererOptions': {'smooth':True, 'shadowAlpha': 0.1, 'fillToZero': True}}
          }
      result={'opt':opt, 'data':[], 'maxseriecount':0}
      idx=0
      callbacks=[]
      for s in series:
         addserie=True
         if s.selector_type=='SQL':
            callbacks.append([sqlQuery, s.selector_name, idx])
         elif s.selector_type=='daily_sum':
            query="SELECT date as 'x', SUM("
            query+="+".join(['h'+str(x).zfill(2) for x in range(0,24)])
            query+=") as 'y' FROM stats_history WHERE"
            if str(s.selector_name).startswith('dmdomain:'):
               query+=" DMDOMAIN(name, '"+parseSelectorName(str(s.selector_name).replace('dmdomain:',''), s)+"')=1"
            elif str(s.selector_name).startswith('like:'):
               query+=" name LIKE '"+parseSelectorName(str(s.selector_name).replace('like:',''), s)+"'"
            else:
               query+=" name='"+parseSelectorName(str(s.selector_name), s)+"'"

            query+=getSelectorSubtype(s)
            query+=" group by date"
            callbacks.append([sqlQuery, query, idx])
         elif s.selector_type=='hourly_sum':
            query="SELECT date,"
            query+=",".join(['SUM(h'+str(x).zfill(2)+") as h"+str(x).zfill(2) for x in range(0,24)])
            query+=" FROM stats_history WHERE"
            if str(s.selector_name).startswith('dmdomain:'):
               query+=" DMDOMAIN(name, '"+parseSelectorName(str(s.selector_name).replace('dmdomain:',''), s)+"')=1"
            elif str(s.selector_name).startswith('like:'):
               query+=" name LIKE '"+parseSelectorName(str(s.selector_name).replace('like:',''), s)+"'"
            else:
               query+=" name='"+parseSelectorName(str(s.selector_name), s)+"'"
            query+=getSelectorSubtype(s)
            query+=" group by date" 
            callbacks.append([hourlySqlQuery, query, idx, s])
         else:
            addserie=False

         if addserie:
            marker_show=True
            if str(s.marker_show)=='false':
               marker_show=False
            fill=True
            if str(s.fill)=='false':
               fill=False
            result['opt']['series'].append({
               'label': s.label,
               'lineWidth': s.line_width,
               'markerOptions': {
                  'style': s.marker_style,
                  'size': s.marker_size
               },
               'color': s.color,
               'showMarker': marker_show,
               'showLine': True,
               'fill': fill,
               'fillAndStroke': True,
               'highlighter': {
                  'formattingString': s.highlighter_formatString
               }
            })

         idx+=1
         
      d=defer.succeed(result)
      for c in callbacks:
         d.addCallback(c[0], *c[1:])
      d.addCallback(addAxes, chartdata)
      return d


   def getChartData(self, resdata, chartname):
      if resdata and len(resdata)>0:
         return dmdb.getChartSeries(chartname).addCallback(self.parseChartSeries, resdata, chartname)
      return defer.fail('No chart with the name '+str(chartname))

   def web_on_getChartData(self, chartname):
      log.debug('GET CHART DATA FOR '+str(chartname))
      return dmdb.getChartData(chartname).addCallback(self.getChartData, chartname)

   def web_on_getDaemonStatus(self):
      return self.daemonstatus

   def web_on_startAutoDetection(self, force=False):
      if force:
         self.resetBoards()
      self.autoDetectBoards()
      return self.daemonstatus

   def web_on_getAuth(self, usr, pwd):
      return dmdb.Users.find(where=["username='%s' AND passwd='%s' AND active=1" % ( usr, pwd)])

   def web_on_getPermissionForPath(self, user, path):
      return dmdb.getPermissionForPath(user, path)

   def web_on_getAllUsers(self, activeonly=False):
      return dmdb.getAllUsers(activeonly)

   def web_on_getUserFromID(self, uid):
      return dmdb.Users.find(where=['id=?', uid], limit=1)

   def web_on_getUserFromName(self, name):
      return dmdb.Users.find(where=['username=?', name], limit=1)

   def web_on_updateUserData(self, username, pwd, email, dhome, mhome, tts, 
                              lang, slide=False, webspeech='touch', speechlang='it-IT', 
                              theme='dmblack', leftb='hidden-sm', rightb='hidden-sm'):
      return dmdb.updateUserData(username, pwd, email, dhome, mhome, tts, lang,slide, 
                                 webspeech, speechlang, theme, leftb, rightb) 

   def web_on_getMaxLocalTranscode(self):
      return int(self.config.get('media', 'localtranscode'))

   def web_on_configGet(self, section, var):
      return self.config.get(section, var)

   def web_on_getRelays(self, ts):
      return dmdb.RelStatus.find(where=['lastupdate>=?',ts])
   
   def web_on_getInputs(self, ts):
      return dmdb.InpStatus.find(where=['lastupdate>=?',ts])
   
   def web_on_getActionStatus(self):
      return [{'data': ACTION_STATUS.values(), 'command': 'updateactions'}]

   def web_on_getIpCamList(self):
      return dmdb.MediaSources.find(where=['type=? AND active=1','ipcam'],
         orderby="position,button_name,ip ASC")

   def web_on_getRelayList(self):
      return dmdb.Relay.find(where=['active=1'],orderby="position,button_name ASC")

   def web_on_getActionList(self):
      return dmdb.Actions.find(where=['active=1'],orderby="position,button_name ASC")

   def web_on_getInputList(self):
      return dmdb.Input.find(where=['active=1'],orderby="position,button_name ASC")

   def web_on_getNotifications(self, username, onlysince=0, usecount=False):
      return dmdb.getNotifications(username,onlysince,usecount)

   def web_on_markReadNotifications(self, username, nid=False):
      if nid and (nid=='*' or int(nid) > 0): 
         return dmdb.markNotifyAsRead(username, nid)
      else:
         return defer.succeed(False)

   def web_on_updateSession(self, sessuid, session, obj):
      return self.clients.update_session(sessuid, session, obj)
      #pass

   def web_on_sendAction(self, command):
      log.debug("SENDACTION: "+str(command))
      try:
         if unicode(command.split('_')[1]).isnumeric():
            
            if(command.split('_')[0]=='actions'):
               dmdb.Actions.find(where=['id=?', str(command.split('_')[1])], limit=1).addCallback(self.parseAction)
            elif(command.split('_')[0]=='relays'):
               dmdb.Relay.find(where=['id=?', str(command.split('_')[1])], limit=1).addCallback(self.sendRelayCmd)
            elif(command.split('_')[0]=='inputs'):
               log.debug('INPUT %s PRESSED' % str(command.split('_')[1]))
      except:
         log.debug('Not a Relay command')

   def web_on_setRelayById(self, rid, status=""):
      if len(status)==0:
         return dmdb.Relay.find(where=['id=?', str(rid)], limit=1).addCallback(self.sendRelayCmd)
      elif status=='on':
         return dmdb.Relay.find(where=['id=?', str(rid)], limit=1).addCallback(self.sendRelayCmd, C.IKAP_ACT_ON)
      elif status=='off':
         return dmdb.Relay.find(where=['id=?', str(rid)], limit=1).addCallback(self.sendRelayCmd, C.IKAP_ACT_OFF)
      elif status=='change':
         return dmdb.Relay.find(where=['id=?', str(rid)], limit=1).addCallback(self.sendRelayCmd, C.IKAP_ACT_CHANGE)
      return defer.fail('Wrong action')

   def web_on_setActionById(self, aid):
      def _execAction(res):
         self.parseAction(res)
         return res
      return dmdb.Actions.find(where=['id=?', str(aid)], limit=1).addCallback(_execAction)


   def web_on_uiCommand(self, command):
      log.debug("UICOMMAND: "+str(command))
      ret='KO'
      if command[0]=='reset':
         self.resetBoards()
         self.resetRelayist()
         self.resetAnalogList()
         #self.resetMediaSourcesList()
         self.resetActionList()
         self.resetPwmList()
         self.resetOutputList()
         self.resetInputList().addCallback(self.autoDetectBoards)
         self.confstatus=1
         ret='OK'
      elif command[0]=='refresh':
         self.resetBoards()
         self.autoDetectBoards()
         self.confstatus=1
         ret='OK'
      return ret
   
   def web_on_motionDetection(self, etype, estatus, camera, zone):
      dmdb.checkMotionDetectionEvent(camera, zone, estatus, etype).addCallback(
         self.manageMotionDetection
      )

   def web_on_asteriskAction(self, extension, context):
      return dmdb.checkAsteriskAction(extension, context).addCallback(
               self.manageAsteriskAction
             )

   def web_on_asteriskAliases(self, extension, context):
      return dmdb.checkAsteriskAlias(extension, context).addCallback(
            self.manageAsteriskAlias
         )

   def web_on_configuringStatus(self):
      if self.confstatus:
         return 'TRUE'
      return 'FALSE'

   def web_on_voiceReceived(self, txt, confidence=0.0, lang="it"):
      return self.voiceRecognized(txt, confidence, lang, voicesrc='RestAPI')

   def plugin_on_registerEvent(self, event, pname, cback):
      log.debug("plugin_on_registerEvent "+str(event)+" "+str(cback))
      events.registerEvent(event, pname, cback)

   def plugin_on_unregisterAllEvents(self, pname):
      log.debug("plugin_on_unregisterAllEvents "+str(pname))
      events.unregisterAllEvents(pname)

   def plugin_on_unregisterEvent(self, eventname, pname):
      log.debug("plugin_on_unregisterEvent "+str(eventname)+" "+str(pname))
      events.unregisterEvent(eventname, pname)

   def plugin_on_manageSequence(self, seqname, action):
      if action=='start':
         dmdb.getSequence(seqname).addCallback(self.manageSequence, 'plugin')
      elif action=='stop':
         dmdb.getSequence(seqname).addCallback(self.stopSequence)

   def plugin_on_postEvent(self, pname, eventname, eventargs):
      events.postEvent(events.PluginEvent(pname, eventname, eventargs))

   def plugin_on_sendCommand(command,ctx,act,arg,msgtype,src,ipdst):
      self.sendCommand(command, msgtype=msgtype, ctx=ctx, act=act, arg=arg, src=src, ipdst=ipdst)

   def plugin_on_execute(cmd):
      self.executeAction(cmd)

   def domika_on_broadcastTime(self, ipdst="255.255.255.255"):
      self.broadcastTime(ipdst)

   def domika_on_updateWebPort(self, src, host, webport, port, ptype):
      return dmdb.updateWebPort(src, host, webport)

   def domika_on_configGet(self, section, var):
      return self.config.get(section, var)

   def domika_on_setRelayStatus(self, bname, bip, port, ptype, rel, st, amp=0):
      d=dmdb.updateRelStatus(bname, bip, rel, st, amp)
      d.addCallback(dmdb.getRelay, bname, bip, rel)

   def domika_on_setAnalogStatus(self, bname, bip, port, ptype, ana, st):
      dmdb.updateAnalogStatus(bname, bip, ana, st)

   def domika_on_setInputStatus(self, bname, bip, port, ptype, inp, st):
      o=oldb.OldBoards()
      if bip in o.get_boardlist():
         if st in [0, "0"]: st=1
         else: st=0
      dmdb.updateInputStatus(bname, bip, inp, st)

   def domika_on_commitDBChanges(self):
      return dmdb.commit()

   def domika_on_setAlarmActive(self):
      log.debug("ALLARME ATTIVO")

   def domika_on_allarmeIntrusione(self):
      log.debug("ALLARME INTRUSO")

   def domika_on_addBoard(self, btype, fwver, name, ip, webport=80, port=6654, ptype='UDP4'):
      # XXX Choose a better way to do that!
      #     and change the fixed things!
      if(self.confstatus==1):
         self.addBoard(btype, fwver, name, ip, webport, ptype, port)
         try:
            self.timeconfstatus.reset(15)
         except:
            pass

   def domika_on_updateLastStatusTime(self):
      log.debug("Last Update Status EXTERNAL")
      self.lastupdatestatus=time.time()

   def domika_on_updateBoardLastStatus(self, host, port, ptype, src):
      dmdb.updateBoardLastStatus(host, port, ptype, src)

   def domika_on_isLocalSource(self, host, ptype):
      return self.isLocalSource(host, ptype)

   def domika_on_manageIncomingPacket(self, ikahdr, src, dst, arg, host, port, ptype, argdict, rawdata):
      islocal=self.isLocalSource(host, ptype)
      if dst!="IOSTATUS.NOW":
         log.info("RECEIVED: "+str([ dst, src, ikahdr.ctx, ikahdr.msgtype, ikahdr.act, arg, argdict]))
      else:
         log.debug("RECEIVED: "+str([ dst, src, ikahdr.ctx, ikahdr.msgtype, ikahdr.act, arg, argdict]))
      if not islocal:
         if dst.startswith("BOOTED") and ikahdr.ctx==C.IKAP_CTX_SYSTEM and ikahdr.msgtype==C.IKAP_MSG_NOTIFYCONF:
            events.postEvent(events.DeviceEvent("BOOTED", src))
            log.error("RECEIVED: "+str([ dst, src, ikahdr.ctx, ikahdr.msgtype, ikahdr.act, arg, argdict]))
         elif dst.startswith("NETWORK.") and ikahdr.ctx==C.IKAP_CTX_SYSTEM and ikahdr.msgtype==C.IKAP_MSG_NOTIFYCONF:
            reactor.callLater(0.1, self.sendNetStatus, None, False, host)
      if (ikahdr.msgtype==C.IKAP_MSG_ACTION   
          and ikahdr.act==C.IKAP_ACT_CHANGE
          and ikahdr.ctx==C.IKAP_CTX_STATUS):
          dmdb.updateNetStatus(dst)
      
      self.updateStatusFromReceived(host, port, ptype, argdict, src)

      dmdb.matchIncomingPacket(dst, src, 
            ikahdr.msgtype, ikahdr.ctx, 
            ikahdr.act, islocal=islocal).addCallback(
               self.manageRecvPkt, argdict
            )
      events.postEvent(events.NetworkEvent(dst, src, ikahdr, arg, host))
      if arg:
         astr=struct.unpack('<'+str(len(arg))+'B', arg)
      else:
         astr=""
      if len(astr) > 6 and astr[4]==C.DM_INPUT_TYPE_DIGITAL:
         dmdb.setInputStatus(src, host, astr[6])

      if ptype=='UDP4':
         self.sendTCPRAWCommand(rawdata, ikahdr.msgtype)
      else:
         self.sendUDPRAWCommand(rawdata, ikahdr.msgtype)


   def upnp_on_configGet(self, section, var):
      return self.config.get(section, var)

   def upnp_on_addMediaSource(self, device):
      if not device['host'] in self.upnp_detected_ips:
         self.upnp_detected_ips.append(device['host'])
         log.debug("UPNP DETECTED DEVICE FROM UPNP: "+str(device))
         p=pluggableMediasouces.getMediaSourcePlugin(device['modelNumber'], device['manufacturer'])
         if p:
            videodev = p.getMediaSource(device['host'], self.devadminpwd)
            videodev.setUPNPLocation(device['location'])
            videodev.addDevice()
      else:
         log.debug("UPNP DETECTED ALREADY EXISTS FOR UPNP: "+str(device))

   def ami_on_amiEventReceived(self, eventtype, caller, called, context, variable=False):
      def checkEvent(res):
         if res:
            for r in res:
               events.postEvent(events.AmiEvent(r.voip_action_name, eventtype, caller, called, context, variable))    
               dmdb.checkAsteriskActionByName(r.voip_action_name).addCallback(self.manageAsteriskAction)
            return res
      return dmdb.checkAmiEvent(eventtype, caller, called, context, variable).addCallback( checkEvent )

   def ami_on_amiCall(self,evt='',src='',srcname='',srcchannel='',dst='',dstname='',dstchannel=''):
      events.postEvent(events.VoipCall(evt,src,srcname,srcchannel,dst,dstname,dstchannel))

   def fagi_on_getTriggerWord(self):
      return str(self.config.get("voiceui", "triggerword")).lower()

   def fagi_on_getStopWord(self):
      return str(self.config.get("voiceui", "stopword")).lower()

   def fagi_on_getStopCommandWord(self):
      return str(self.config.get("voiceui", "stopcommand")).lower()

   def fagi_on_getAliases(self, extension, context, usedomain=True):
      return dmdb.checkAsteriskAlias(extension, context, usedomain)

   def fagi_on_getAction(self, extension, context):
      return dmdb.checkAsteriskAction(extension, context).addCallback(
               self.manageAsteriskAction
             )

   def fagi_on_voiceReceived(self, txt, confidence=0.0, lang="it"):
      return self.voiceRecognized(txt,confidence,lang,voicesrc='VoIP')


