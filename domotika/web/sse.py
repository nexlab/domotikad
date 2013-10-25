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

from twisted.internet import interfaces, task
from twisted.web.resource import Resource
from twisted.web import server
from zope.interface import implements
from corepost.convert import convertForSerialization, generateXml, convertToJson
import logging, time
from dmlib.utils import genutils

log = logging.getLogger( 'Webgui' )


class Producer():
   implements(interfaces.IPushProducer)
 
   def __init__(self, request):
      self.request = request
      self.produce = True
      self.loop = task.LoopingCall(self.sendComment)
      self.loop.start(30)
      request.registerProducer(self, True)   
 
   def sendComment(self):
      self.write(raw=":keepalive\n")

   def stopProducing(self):
      log.debug("stopProducing")
      try:
         self.loop.stop()
      except:
         pass
      self.produce = False
      self.request.unregisterProducer()
      self.request.finish()
 
   def pauseProducing(self):
      log.debug("pauseProducing")
      self.produce = False
      # kill immediately
      self.stopProducing()
 
   def resumeProducing(self):
      log.debug("resumeProducing")
      self.produce = True
 
   def write(self, data=[], event=None, eid=None, raw=None):
      if self.produce:
         message = ""
         if eid != None:
            message += "id: " + str(eid) + "\n"
         if event != None:
            message += "event: " + str(event) + "\n"
         for line in data:
            message += "data: " + str(line) + "\n"
         if raw != None:
            self.request.write(raw)
         self.request.write(message + "\n")
 
 
class SseResource(Resource):
 
   isLeaf = True

   def __init__(self, core, username):
      Resource.__init__(self)
      self.producers = []
      self.loops = []
      self.core = core
      self.username = username
 
   def connectionClosed(self, message, producer):
      log.debug("Connection closed")
      log.debug(message)
      try:
         self.loops.stop()
      except:
         pass
      self.producers.remove(producer)
      log.debug(self.producers)
 
   def render_GET(self, request):
      android_native=False
      old_chrome=False
      old_ie=False
      ua = str(request.getHeader('user-agent'))
      if ua.startswith("Mozilla/5.0 (Linux; U; Android") and 'Mobile Safari' in ua and not 'Chrome/' in ua and not 'dolphin' in ua.lower() and not 'Firefox/' in ua:
         android_native=True
         log.debug("Native Android user agent detected: "+str(request.getHeader('user-agent')))
      elif 'MSIE' in ua:
         uaie=ua.split()
         ver=int(uaie[uaie.index('MSIE')+1].split(".")[0])
         if ver<10:
            old_ie=True
      elif not 'Android' in ua and ('Chrome/1' in ua or 'Chromium/1' in ua):
         if 'Chromium/1' in ua:
            uach=int(ua.split('Chromium/1')[1].split('.')[0])
         else:
            uach=int(ua.split('Chrome/1')[1].split('.')[0])
         if uach<14:
            old_chrome=True
      request.setHeader("Content-Type", "text/event-stream")
      request.setHeader("Cache-Control", "no-cache")
      request.setHeader("Connection", "keep-alive")
      #request.setHeader("Access-Control-Allow-Origin", "http://localhost")
      request.setHeader("Access-Control-Allow-Origin", "*")
      leid=0
      try:
         leid=request.getHeader("last-event-id")
      except:
         pass
      if leid==0:
         if 'lasteventid' in request.args.keys():
            try:
               leid=request.args.keys()[0]
            except:
               pass
      # flush headers
      request.write(":");
      if old_ie or old_chrome:
         request.write(" "*2048); # Fix for IE < 10 and Chrome < 13
      if android_native:
         self.android_native=True
         request.write(" "*4096);
      request.write("\n")
      if android_native:
         request.write("retry:1\n")
      else:
         request.write("retry:1000\n")
 
      log.debug("Connection added")
      producer = Producer(request)
      producer.android_native=android_native
      if genutils.is_number(leid):
         producer.leid=leid
      else:
         producer.leid=0
      self.producers.append(producer)
      log.debug(self.producers)
      d = request.notifyFinish()
      d.addCallback(self.connectionClosed, producer)
      d.addErrback(self.connectionClosed, producer)
      return server.NOT_DONE_YET
 
   def write(self, data=[], event=None):
      for producer in self.producers:
         producer.leid+=1
         producer.write(data, event, producer.leid)
         if producer.android_native: # This is a work around cause android need a 4096 padding cause if a bad buffer management, so we switch to long polling
            producer.stopProducing()

   def sendJSON(self, event='notify', data=False):
      ser=convertForSerialization({'data': data, 'ts': time.time()})
      self.write(event=event, data=[convertToJson(ser)])
      
