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

import logging
log = logging.getLogger( 'Core' )

from dmlib.singleton import Singleton

class EventListenersRegistry(Singleton):
   registry={}

   def __init__(self, *args, **kwargs):
      Singleton.__init__( self )

   def register(self, name, pname, cback):
      if name in self.registry.keys():
         self.registry[name][pname]=cback
      else:
         self.registry[name] = {pname:cback}

   def postEvent(self, event):
      log.debug("Event Posted "+str(event)+" "+str(event.name))
      log.debug(self.registry)
      if event.name in self.registry.keys():
         for cback in self.registry[event.name].values():
            if callable(cback):
               cback(event)  

   def unregisterEvent(self, eventname, pname):
      if eventname in self.registry.keys():
         if pname in self.registry[eventname].keys():
            del self.registry[eventname][pname]
            if len(self.registry[eventname])==0:
               del self.registry[eventname]

   def unregisterAllEvents(self, pname):
      for eventname in self.registry.keys():
         if pname in self.registry[eventname].keys():
            del self.registry[eventname][pname]
            if len(self.registry[eventname])==0:
               del self.registry[eventname]

EVENTLISTENERS = EventListenersRegistry.getInstance()

def postEvent(event):
   return EVENTLISTENERS.postEvent(event)

def registerEvent(name, pname, cback):
   return EVENTLISTENERS.register(name, pname, cback)

def unregisterAllEvents(name):
   return EVENTLISTENERS.unregisterAllEvents(name)

def unregisterEvent(eventname, name):
   return EVENTLISTENERS.unregister(eventname, name)

class BaseEvent(object):

   name='BASEEVENT'
   rawdata=[]

class TimerEvent(BaseEvent):
   """ TimerEvent """
   name="TIMER"
   def __init__(self, tact, tid=0, tname=''):
      self.rawdata = [tact, tid, tname]
      self.timerid = tid
      self.timername = tname 
      self.timeract = tact

class StatusEvent(BaseEvent):
   """ StatusEvent """
   name="STATUS"
   def __init__(self, sact, sid=0, sname=''):
      self.rawdata = [sact, sid, sname]
      self.statusid = sid
      self.statusname = sname
      self.statusact = sact
  


class ActionEvent(BaseEvent):
   """ ActionEvent """
   name="ACTION"
   def __init__(self, command):
      self.rawdata = [command]
      self.command = command


class SequenceEvent(BaseEvent):
   """ SequenceEvent """
   name="SEQUENCE"
   
   def __init__(self, event, seqname, seqtype, src='', step=0):
      self.rawdata = [ event, seqname, seqtype, src, step ] 
      self.event = event
      self.seqname = seqname
      self.seqtype = seqtype
      self.src = src
      self.step = step

class DeviceEvent(BaseEvent):
   """ DeviceEvent """
   name="DEVICE"

   def __init__(self, event, who, args=False):
      self.rawdata = [event, who, args]
      self.event = event
      self.who = who
      self.args = args

class PluginEvent(BaseEvent):
   """ PluginEvent """
   name="PLUGINEVENT"
   def __init__(self, pname=False, eventname=False, eventargs=None):
      self.rawdata = [pname, eventname, eventargs]
      self.pname = pname
      self.eventname = eventname
      self.eventargs = eventargs

class NetworkEvent(BaseEvent):
   """ NetworkReceivedEvent """
   name="NETWORK"

   def __init__(self, dst, src, ikahdr, arg, host):
      self.rawdata = [dst, src, ikahdr.ctx, ikahdr.msgtype, ikahdr.act, arg, host]
      self.dst = dst
      self.src = src
      self.ctx = ikahdr.ctx
      self.msgtype = ikahdr.msgtype
      self.arg = arg
      self.host = host

class VoipCallEvent(BaseEvent):
   """ VoipCallEvent """
   name="VOIPCALL"

   def __init__(self, evt='',src='',srcname='',srcchannel='',dst='',dstname='',dstchannel=''):
      self.rawdata = [evt,src,srcname,srcchannel,dst,dstname,dstchannel]
      self.src=src
      self.srcname=srcname
      self.srcchannel=srcchannel
      self.dst=dst
      self.dstname=dstname
      self.dstchannel=dstchannel
      self.event=evt

class SpeechRecognizedEvent(BaseEvent):
   """ SpeechRecognizedEvent """
   name="SPEECHREC"

   def __init__(self, src, txt, confidence, lang):
      self.rawdata = [ src, txt, confidence, lang ]
      self.src = src
      self.txt = txt
      self.confidence = confidence
      self.lang = lang


class AmiEvent(BaseEvent):
   """ AmiEvent """
   name="AMIEVENT"

   def __init__(self, voip_action_name, eventtype, caller, called, context, variable):
      self.rawdata = [voip_action_name, eventtype, caller, called, context, variable]
      self.voip_action_name = voip_action_name
      self.eventtype = eventtype
      self.caller = caller
      self.called = called
      self.context = context
      self.variable = variable

