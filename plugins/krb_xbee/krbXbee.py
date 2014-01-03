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

from twisted.internet import reactor, stdio, task, defer
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint
from domotika.plugins import BasePlugin
import base64, os, sys
from dmlib.utils.genutils import configFile
from domotika.db import dmdb
from dmlib import dmdomain
import time
from datetime import datetime
import subprocess
from zigbee import ZigBeeProtocol



NAME="KerberosZigbeePlugin"
VERSION=0.1
DESCRIPTION=""
AUTHOR="Franco (nextime) Lanza"
COPYRIGHT=""
LICENSE=""
PLUGINENGINE=0.1

BASEDIR=os.path.abspath(os.path.dirname(sys.argv[0])+"/../../")
CONFIGDIR=os.path.join(BASEDIR, "conf")

xbee=[]

class KerberosProtocol(ZigBeeProtocol):
   def __init__(self, *a, **kw):
      super(KerberosProtocol, self).__init__(*a, **kw)
      xbee.append(self)

   def handle_packet(self, xbeePacketDictionary):
      res = xbeePacketDictionary
      print res


class KerberosFactory(Factory):
   def buildProtocol(self, addr):
      return KerberosProtocol(escaped=True)

class KrbXbeePlugin(BasePlugin):

   exitontimeout=False
   name=NAME
   def pluginStart(self):
      #self.registerCallback('NETWORK', self.evt_NETWORK)
      self.cfg = configFile(CONFIGDIR+"/domotikad.conf")
      self.cfg.readConfig()

      endpoint1 = TCP4ServerEndpoint(reactor, 10001)
      endpoint1.listen(KerberosFactory())
      endpoint2 = TCP4ClientEndpoint(reactor, "192.168.4.253", 10002)
      endpoint2.connect(KerberosFactory())
      endpoint3 = TCP4ClientEndpoint(reactor, "192.168.4.253", 4000)
      endpoint3.connect(KerberosFactory())


      

   def runQuery(self, query):
      return dmdb.Registry.DBPOOL.runQuery(query)

   def runOperation(self, query):
      return dmdb.Registry.DBPOOL.runOperation(query)

            
