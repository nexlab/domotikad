#!/usr/bin/python
import sys, os
import time
import libopenzwave
from libopenzwave import PyManager

"""
{'homeId': 23191651L, 'event': 0, 'valueId': {'index': 0, 'units': '', 'type': 'Bool', 'nodeId': 2, 'value': None, 'commandClass': 'COMMAND_CLASS_NO_OPERATION', 'instance': 1, 'readOnly': False, 'homeId': 23191651L, 'label': '', 'genre': 'Basic', 'id': 72057594071482368L}, 'notificationType': 'NodeEvent', 'nodeId': 2}
"""

def callback(res):
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
         print 'NODEID:', nid, 'NodeLocation:', manager.getNodeLocation(hid, nid) 
         print 'NODETYPE:', manager.getNodeType(hid, nid) 
         print 'NODENAME:', manager.getNodeName(hid, nid)
         print 'NODEBASIC:', manager.getNodeBasic(hid, nid)
         print 'NODEGENERIC:', manager.getNodeGeneric(hid, nid)
         print 'NODESPECIFIC:', manager.getNodeSpecific(hid, nid)
         print 'NODEMANUFACTURERNAME:', manager.getNodeManufacturerName(hid, nid)
         print 'NODEPRODUCTNAME:', manager.getNodeProductName(hid, nid)
   print '******************************'

options = libopenzwave.PyOptions()
#options.create("openzwave/","","--logging false")
options.create("openzwave/","","")
options.lock()

manager = libopenzwave.PyManager()
manager.create()
manager.addWatcher(callback)
manager.addDriver("/dev/ttyUSB0")
time.sleep(360000)

