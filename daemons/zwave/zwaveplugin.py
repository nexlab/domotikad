from twisted.internet import reactor, stdio
from twisted.spread import pb
import pickle
import sys
try:
   from domotika.plugins import BasePlugin
except:
   sys.path.append("/home/domotika/")
   from domotika.plugins import BasePlugin

from dmlib.utils.genutils import configFile
from domotika.db import dmdb
from dmlib import dmdomain
  
from datetime import datetime
import base64, os
import subprocess
import time

NAME="ZWavePlugin"
VERSION=0.1
DESCRIPTION=""
AUTHOR="Franco (nextime) Lanza"
COPYRIGHT=""
LICENSE=""
PLUGINENGINE=0.1

BASEDIR=os.path.abspath(os.path.dirname(os.path.abspath(sys.argv[0]))+"/../../")
CONFIGDIR=os.path.join(BASEDIR, "conf")


class ReconnectingPBFactory(pb.PBClientFactory):

   def clientConnectionLost(self, connector, reason, reconnecting=1):
      print "Reconnecting..."
      reconnecting=1
      return pb.PBClientFactory.clientConnectionLost(self, connector, reason, reconnecting)

class ZWavePlugin(BasePlugin, pb.Referenceable):

   def _checkPing(self):
      pass

   def pluginStart(self):
      factory = ReconnectingPBFactory()
      factory.getRootObject().addCallback(self.gotZWave)  
      reactor.connectTCP("localhost", 8800, factory)    
       
   def gotZWave(self, zw):
      zw.callRemote("setClient", self)
      def print_remote(res):
         print res
      zw.callRemote("ZWaveNetwork", "state").addCallback(print_remote)
      zw.callRemote("ZWaveNetwork", "controller.ozw_library_version").addCallback(print_remote)

   def remote_zwevent(self, event):
      print str(event)
      #print pickle.loads(event)#
      return 'remoteCalled zwevent'

if __name__ == '__main__':
   plugin=ZWavePlugin()
   stdio.StandardIO(plugin)
   reactor.run()

