#!/usr/bin/env python

from twisted.internet import epollreactor
epollreactor.install()

from twisted.internet import reactor
from twisted.application import service, internet, app, reactors
from twisted.spread import pb
from twisted.manhole.telnet import ShellFactory

import sys
from dmlib.daemonizer import Daemonizer

from logging import handlers as loghandlers
import logging
import sys

 
from datetime import datetime
import base64, os
import subprocess

from openzwave.scene import ZWaveScene
from openzwave.controller import ZWaveController
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
from louie import dispatcher, All
import json
import pickle 
import time

BASEDIR=os.path.abspath(os.path.dirname(os.path.abspath(sys.argv[0]))+"/../../")
CONFIGDIR=os.path.join(BASEDIR, "conf")
CURDIR=os.path.abspath(os.path.dirname(os.path.abspath(sys.argv[0])))

DEVICE="/dev/ttyUSB0"


loglevels = {
   'info': logging.INFO,
   'warning': logging.WARNING,
   'error': logging.ERROR,
   'critical': logging.CRITICAL,
   'debug': logging.DEBUG
}
#LOGLEN=104857600 # 100 mega
#LOGLEN=10485760 # 10 mega
LOGLEN=26214400 # 25 mega


class ZWaveDaemon(Daemonizer):

   def __init__(self):
      Daemonizer.__init__(self, BASEDIR+'/run/zwaved.pid')


   def main_loop(self):
      application = service.Application("ZWaved")
      ZWaveService=ZWaveServer()
      #serviceCollection = service.IServiceCollection(application)
      #ZWaveService.setServiceParent(serviceCollection)
      zpb=ZWavePB(ZWaveService)
   
      shell_factory = ShellFactory()
      shell_factory.username = 'admin'
      shell_factory.password = 'domotika'
      shell_factory.namespace['domotika'] = ZWaveService
      reactor.listenTCP(4041, shell_factory, interface="127.0.0.1")

      reactor.listenTCP(8800, pb.PBServerFactory(zpb), interface="127.0.0.1")
      reactor.run()
      

class ZWavePB(pb.Root):

   clients=[]

   def __init__(self, zwserver):
      self.zwserver = zwserver
      self.zwserver.pb = self

   def remote_setClient(self, client):
      self.clients.append(client)

   def remote_ZWaveNetwork(self, call, *a, **kw):
      cs=call.split(".")
      log.debug("Remote ZWaveNetwork called "+str(cs))
      f=getattr(self.zwserver.network, cs[0], None)
      if len(cs)>1:
         for i in cs[1:]:
            f=getattr(f, i, None)
            if not f:
               return None
            
      if f and callable(f):
         return f(*a, **kw)
      return f

   def notifyClients(self, msg, *a, **kw):
      log.debug("Client notify "+str(msg))
      for client in self.clients:
         try:
            client.callRemote("zwevent", msg, *a, **kw)
         except:
            self.clients.remove(client)

#class ZWaveServer(service.Service):
class ZWaveServer(object):

   def __init__(self):
      options = ZWaveOption(DEVICE, config_path=BASEDIR+"/daemons/zwave/openzwave/", 
         user_path=BASEDIR+"/daemons/zwave/user", cmd_line="")
      options.set_log_file(BASEDIR+"/logs/OZW_Log.log")
      options.set_append_log_file(False)
      options.set_console_output(False)
      #options.set_logging("Debug")
      options.set_logging("Error")
      options.lock()
      self.options = options
      self.starttime=time.time()

      #Create a network object
      self.network = ZWaveNetwork(options, log=None)

      log.info("Waiting for network awaked...")
      dispatcher.connect(self.waitForNetworkWakeUp, ZWaveNetwork.SIGNAL_NETWORK_AWAKED)
      dispatcher.connect(self.waitForNetworkReady, ZWaveNetwork.SIGNAL_NETWORK_READY)

   
   def waitForNetworkWakeUp(self, network):
      self.pb.notifyClients("network.wakeup")
      log.info('Network is wakedup in '+str(time.time()-self.starttime)+' seconds. Waiting for network ready...')

   def waitForNetworkReady(self, network):
      self.pb.notifyClients("network.ready")
      log.info('Network is ready in '+str(time.time()-self.starttime)+' seconds')
      self.zwaveStarted()

   def zwaveStarted(self):
      dispatcher.connect(self.node_update, ZWaveNetwork.SIGNAL_NODE)
      dispatcher.connect(self.node_value_update, ZWaveNetwork.SIGNAL_VALUE)
      network=self.network
      log.info("Network home id : %s" % network.home_id_str)
      log.info("Controller node id : %s" % network.controller.node.node_id)
      log.info("Nodes in network : %s" % network.nodes_count)
      for node in network.nodes:
         log.info("Node %s - Name : %s" % (network.nodes[node].node_id,network.nodes[node].name))
         log.info("Node %s - Manufacturer name / id : %s / %s" % (network.nodes[node].node_id,network.nodes[node].manufacturer_name, network.nodes[node].manufacturer_id))
         log.info("Node %s - Product name / id / type : %s / %s / %s" % (network.nodes[node].node_id,network.nodes[node].product_name, network.nodes[node].product_id, network.nodes[node].product_type))
         
   def node_update(self, network, node):
      log.debug("node."+str(node)+".updated")
      self.pb.notifyClients("node."+str(node)+".updated")

   def node_value_update(self, network, node, value):
      log.debug("node."+str(node)+":VALUE:"+str(value))
      self.pb.notifyClients("node."+pickle.dumps(node)+":VALUE:"+pikle.dumps(value))

     
         

if __name__ == '__main__':
   formatter = logging.Formatter('%(asctime)s => %(name)-12s: %(levelname)-8s %(message)s')
   logdict={"corelog": {"file":"zwaved.log","name":[("ZWave","general")]}}
   for l in logdict.keys():
      logdict[l]["handler"] = loghandlers.RotatingFileHandler(
         BASEDIR+'/logs/'+logdict[l]["file"], 'a', LOGLEN, 5)
      logdict[l]["handler"].setLevel(logging.DEBUG)
      logdict[l]["handler"].setFormatter(formatter)

   logging.basicConfig()

   log = logging.getLogger( 'ZWave' )
   log.addHandler(logdict["corelog"]["handler"])
   log.setLevel( logging.INFO )



   if len(sys.argv) > 1:
      log.debug("Starting daemon with option "+sys.argv[1])
      if sys.argv[1]=='debug':
         log.setLevel( logging.DEBUG )
      ZWaveDaemon().process_command_line(sys.argv)
   else:
      print 'Please specify start, stop or debug option'

