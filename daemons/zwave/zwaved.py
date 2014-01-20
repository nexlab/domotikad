#!/usr/bin/python
import sys, os
import time
import libopenzwave
from libopenzwave import PyManager
from twisted.internet import epollreactor
epollreactor.install()
from twisted.internet import reactor
from dmlib.daemonizer import Daemonizer
from dmlib.utils.genutils import configFile
import logging, time, sys, os
from logging import handlers as loghandlers
from corepost import Response, NotFoundException, AlreadyExistsException
from corepost.web import RESTResource, route, Http
from corepost.convert import convertForSerialization, generateXml, convertToJson
from corepost.enums import MediaType, HttpHeader
import yaml




try:
   import setproctitle
   setproctitle.setproctitle('domotika_zwaved')
   print 'Setting process title to', sys.argv[0]
except:
   pass

log = logging.getLogger( 'ZWaved' )

CURDIR=os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.append(os.path.abspath(CURDIR+"/../../"))

from domotika.web import sse

"""
{'homeId': 23191651L, 'event': 0, 'valueId': {'index': 0, 'units': '', 'type': 'Bool', 'nodeId': 2, 'value': None, 'commandClass': 'COMMAND_CLASS_NO_OPERATION', 'instance': 1, 'readOnly': False, 'homeId': 23191651L, 'label': '', 'genre': 'Basic', 'id': 72057594071482368L}, 'notificationType': 'NodeEvent', 'nodeId': 2}
"""

class DMZWave(object):

   def __init__(self):
      cfgfile=os.path.abspath("/".join([CURDIR, 'conf','zwave.conf']))
      self.cfg=configFile(cfgfile)
      self.cfg.readConfig()
      self.options = libopenzwave.PyOptions()
      #self.options.create("openzwave/","","--logging false")
      self.options.create("openzwave/","","")
      self.options.lock()

      self.manager = libopenzwave.PyManager()
      self.manager.create()
      self.manager.addWatcher(self.callback)
      for controller in self.cfg.get('controller', 'dev').replace(' ','').split(','):
         self.manager.addDriver(controller)
      

   def callback(self, res):
      print '------------------------------'
      print res
      print '=============================='
      if 'valueId' in res.keys():
         if 'nodeId' in res['valueId'].keys():
            #nid=res['valueId']['nodeId']
            nid=res['nodeId']
            hid=res['homeId']
            ntype=res['notificationType']
            print 'NOTIFICATION', ntype
            print 'NODEID:', nid, 'NodeLocation:', self.manager.getNodeLocation(hid, nid) 
            print 'NODETYPE:', self.manager.getNodeType(hid, nid) 
            print 'NODENAME:', self.manager.getNodeName(hid, nid)
            print 'NODEBASIC:', self.manager.getNodeBasic(hid, nid)
            print 'NODEGENERIC:', self.manager.getNodeGeneric(hid, nid)
            print 'NODESPECIFIC:', self.manager.getNodeSpecific(hid, nid)
            print 'NODEMANUFACTURERNAME:', self.manager.getNodeManufacturerName(hid, nid)
            print 'NODEPRODUCTNAME:', self.manager.getNodeProductName(hid, nid)
      print '******************************'


class ZWaved(Daemonizer):

   def main_loop(self):
      DMZWave()     
      reactor.run()


if __name__ == '__main__':


   if len(sys.argv) > 1:
      log.debug("Starting daemon with option "+sys.argv[1])
      ZWaved().process_command_line(sys.argv)
   else:
      print 'Please specify start, stop or debug option'

