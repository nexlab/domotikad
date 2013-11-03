import logging
from gateways import igateways, modules

log = logging.getLogger('Core')

try:
   from twisted.plugin import IPlugin, getPlugins
except ImportError:
   pass
else:
   list(getPlugins(igateways.IDMGateways, modules)) # To refresh cache


def getGatewayPlugin(name):
   for p in getPlugins(igateways.IDMGateways, modules):
      qual = "%s.%s" % (p.__module__, p.__class__.__name__)
      log.info("Calling Gateway Module "+qual)
      if p.__module__.split('.')[-1]==name:
         return p
   return None



