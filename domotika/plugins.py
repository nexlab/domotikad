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

from twisted.internet import reactor, protocol, task
from db import dmdb as dmdb
from dmlib.singleton import Singleton
import time
import os, sys, logging, traceback
import base64

log = logging.getLogger( 'Core' )
PINGTIMEOUT=30

class Registry(Singleton):

   plugins={}

   def __init__(self, *args, **kwargs):
      #super(Singleton).__init__(self)
      Singleton.__init__( self )

   def register(self, name, process):
      self.plugins[name] = process

   def unregister(self, name):
      if name in self.plugins.keys():
         del self.plugins[name]


PLUGINREGISTRY = Registry.getInstance()
PLUGINDIR=os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'plugins')

class BasePlugin(protocol.ProcessProtocol):
   
   lastping = 0
   pingcheck=False
   exitontimeout=True
   name = 'BasePlugin'
   _callbacks={}

   def __init__(self, *a, **kw):
      try:
         import setproctitle
         setproctitle.setproctitle('domotikad_plugin_'+os.path.basename(str(sys.argv[0]).replace('.dmpl','')))
      except:
         pass

   def write(self, msg):
      #self.transport.write("<"+msg+"\r\n")
      sys.stdout.write("<"+msg+"\r\n")
      sys.stdout.flush()

   def connectionMade(self):
      self.timer = task.LoopingCall(self._checkPing)
      self.timer.start(PINGTIMEOUT)
      self.pluginStart()

   def _checkPing(self):
      if not self.pingcheck:
         self.pingcheck=True
         self.lastping=time.time()
      else:
         if time.time()-self.lastping > PINGTIMEOUT*3:
            try:
               self.sendlog('debug' 'Pong not received, exit')
            except:
               pass
            if self.exitontimeout:
               reactor.stop()

   def connectionLost(self, reason):
      self.sendlog('debug', "Plugin %s disconnected with reason: %s" % (str(self.name), reason))

   def dataReceived(self, data):
      self.sendlog('debug',"plugin dataReceived"+str(data))
      d=data.split("\r\n")
      for data in d:
         if data:
            reactor.callLater(0, self.processData, data)

   def processData(self, data):
      self.sendlog('debug', "Plugin %s received DATA: %s" %(self.name, str(data)))
      if not data.startswith(">"):
         return
      data=data[1:].replace("\n", "").replace("\r", "")
      if data.startswith("EVENT:"):
         if data.split(':')[1] in self._callbacks.keys():
            f=self._callbacks[data.split(':')[1]]
            if f and callable(f):
               if(len(data.split(':')[2:]) > 0):
                  f(data.split(':')[2:])
               else:
                  f()
      elif data.startswith("PING:"):
         self.lastping=time.time()
         self.write(data.replace("PING","PONG"))
      else:
         try:
            f=getattr(self, 'on_'+data.split(':')[0])
            if f and callable(f):
               if(len(data.split(':')) > 1):
                  log.debug(str(data.split(':')[1:]))
                  f(*(data.split(':')[1:]))
               else:
                  f()
            else:
               m=str(data.split(':')[0])
               self.sendlog('debug', "Plugin "+str(self.name)+" doesn't implement on_"+m+" method")
         except:
            self.sendlog('debug', "Error reading packet")
            traceback.print_exc()

   def on_WEB(self, *a, **kw):
      pass

   def registerCallback(self, event, callback):
      self.write("REGISTER:"+str(event))
      self._callbacks[str(event)]=callback

   def unregisterCallback(self, event):
      self.write("UNREGISTER:"+str(event))
      del self._callbacks[str(event)]

   def sendlog(self, level, msg):
      message="LOG:"+str(level)+":"+self.name+":"+base64.b64encode(str(msg))
      self.write(message)

   def sendEvent(self, eventname, *eventargs):
      self.write("EVENT:"+str(eventname)+":"+base64.b64encode(":".join([str(x) for x in eventargs])))

   def sendIKAP(self, dst, ctx=False, act=False, arg=False, msgtype=False,
      src=False, ipdst="255.255.255.255"):
      self.write("IKAPSEND:"+":".join([ctx,act,arg,msgtype,src,ipdst]))

   def sendSEQUENCE(self, sequencename, action="start"):
      self.write("SEQUENCE:"+":".join([sequencename, action]))

   def sendEXECUTE(self, command):
      self.write("EXECUTE:"+base64.b64encode(str(command)))


class PluginProtocol(protocol.ProcessProtocol):

   lastpong=0
   pingstarted=False
   exitontimeout=True

   def __init__(self, core, name, loader, *args, **kw):
      self.core = core
      self.name = name
      self.loader = loader

   def connectionMade(self):
      log.debug("Plugin connection...")
      self.timer = task.LoopingCall(self.pingpong)
      self.timer.start(PINGTIMEOUT)


   def outReceived(self, data):
      log.debug("RAWDATA: "+str(data))
      d = data.split("\r\n")
      for data in d:
         if data:
            reactor.callLater(0, self.processInput, data)

   def pingpong(self):
      log.debug("SEND PING TO PLUGIN "+self.name)
      if self.pingstarted:
         if time.time()-self.lastpong > PINGTIMEOUT*3:
            log.debug("PING TIMEOUT FOR "+self.name)
            if self.exitontimeout:
               self.core.unregisterAllEvents(self.name)
               self.transport.loseConnection()
         self.write("PING:"+str(int(time.time())))
      else:
         self.pingstarted=True
         self.write("PING:"+str(int(time.time())))

   def processInput(self, data):
      if not data.startswith("<"):
         return
      data=data[1:].replace("\n", "").replace("\r", "")
      log.debug("Plugin Data Received: %s" % data)
      try:
         f=getattr(self, 'on_'+data.split(':')[0])
         if f and callable(f):
            if(len(data.split(':')) > 1): 
               log.debug(str(data.split(':')[1:]))
               f(*(data.split(':')[1:])) 
            else:
               f() 
      except:
         log.debug("Error reading packet")
         traceback.print_exc()

   def errReceived(self, data):
      log.debug("Plugin Error Received: %s" % data)

   def connectionLost(self, reason):
      log.debug("Plugin Connection Lost %s" %(str(reason)))
      self.core.unregisterAllEvents(self.name)
   
   def stopPlugin(self):
      self.core.unregisterAllEvents(self.name)
      PLUGINREGISTRY.unregister(self.name)
      self.process.loseConnection()

   def processEnded(self, reason):
      log.debug("Plugin Process Ended %s" %(str(reason)))
      self.core.unregisterAllEvents(self.name)
      PLUGINREGISTRY.unregister(self.name)
      reactor.callLater(PINGTIMEOUT, self.loader.reloadPlugin, self.name)

   def write(self, msg):
      self.transport.write(">"+msg+"\r\n")
   
   def push_event(self, event):
      log.debug("Push Event requested")
      self.write('EVENT:'+str(event.name)+":"+":".join(str(x) for x in event.rawdata))

   def on_EVENT(self, eventname, eventargs):
      self.core.postEvent(self.name, eventname, base64.b64decode(eventargs).split(":"))

   def on_REGISTER(self, event):
      log.debug("Plugin Register Event "+str(event))
      self.core.registerEvent(event, self.name, self.push_event)     
   
   def on_UNREGISTER(self, eventname):
      log.debug("Plugin Unregister Event "+str(eventname))
      self.core.unregisterEvent(eventname, self.name)

   def on_SEQUENCE(self, sequencename, action="start"):
      log.debug("Plugin request action "+str(action)+" for sequence "+str(sequencename))
      self.core.manageSequence(sequencename, action)

   def on_EXECUTE(self, command):
      log.debug("Plugin request execution "+str(base64.b64decode(command)))
      self.core.execute(command)

   def on_IKAPSEND(self, dst, ctx=0, act=0, arg=0, msgtype=0,
      src=False, ipdst="255.255.255.255" ):
      if not src:
         src="Q.PLUGIN."+str(self.name)
      if len(src) > 32:
         src=src[0:32]
      if len(dst) <= 32:
         try:
            ctx=int(ctx)
            act=int(act)
            msgtype=int(msgtype)
            self.core.sendCommand(dst,ctx,act,arg,msgtype,src,ipdst)
         except:
            pass


   def on_LOG(self, level, name, msg):
      log.debug("Received Log Request")
      lmsg=":".join([name, base64.b64decode(msg)])
      if level == 'debug':
         log.debug(lmsg)
      elif level == 'info':
         log.info(lmsg)
      elif level == 'warning':
         log.warning(lmsg)
      elif level == 'error':
         log.error(lmsg)

   def on_PONG(self, ptime):
      self.lastpong = time.time()


class Loader(object):
   
   def __init__(self, core):
      log.debug("Initializing plugins...")
      log.debug("add pythonpath %s" % os.path.abspath(os.path.dirname(sys.argv[0])))
      self.core = core
      for name in os.listdir(PLUGINDIR): 
         self.loadPlugin(name)

   def reloadPlugin(self, name):
      log.debug("Reloading Plugin "+str(name))
      log.debug("add pythonpath %s" % os.path.abspath(os.path.dirname(sys.argv[0])))
      if name in os.listdir(PLUGINDIR):
         self.loadPlugin(name)

   def push_request(self, plugin, *request):
      log.debug("Push request "+str(*request)+" to plugin(s) "+str(plugin))
      if plugin=='*':
         for p in PLUGINREGISTRY.plugins.keys():
            try:
               PLUGINREGISTRY.plugins[p].write(":".join(*request))
            except:
               log.debug("Cannot send request "+str(request)+" to "+str(p))
      else:
         if plugin in PLUGINREGISTRY.plugins.keys():
            try:
               PLUGINREGISTRY.plugins[plugin].write(":".join(*request))
            except:
               log.debug("Cannot send request "+str(*request)+" to "+str(plugin))
         else:
            log.debug("Plugin "+str(plugin)+" doesn't exists or not loaded")

   def webRequest(self, pname, ppath, pargs, pheaders):
      self.push_request(pname, ['WEB', ppath, base64.b64encode(pargs), base64.b64encode(pheaders)])
      return 'OK' # XXX vediamo di ritornare qualcosa di utile?

   def loadPlugin(self, name):
      if name in PLUGINREGISTRY.plugins.keys():
         log.debug("stopping plugin "+str(name))
         try:
            PLUGINREGISTRY.plugins[name].stopProcess()
         except:
            log.debug("error stopping plugin "+str(name))

      if os.path.isdir(os.path.join(PLUGINDIR, name)):
         pdir=os.path.join(PLUGINDIR, name)
         if os.path.isfile(os.path.join(pdir, name+".dmpl")):
            log.debug("detected plugin in %s" %pdir)
            try:
               pluginInstance=PluginProtocol(self.core,name,self)
               process = reactor.spawnProcess(pluginInstance, os.path.join(pdir, name+".dmpl"),
                  args=[os.path.join(pdir, name+".dmpl")],
                  env={'PYTHONPATH': os.path.abspath(os.path.dirname(sys.argv[0]))}
                  )
               pluginInstance.process = process
               log.info("Plugin %s started" % name)
               PLUGINREGISTRY.register(name, pluginInstance)
            except:
               log.info("Cannot start plugin %s" % name )
               traceback.print_exc()


