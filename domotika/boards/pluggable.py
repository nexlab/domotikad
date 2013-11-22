import logging
import iboards, modules

log = logging.getLogger('Core')

try:
   from twisted.plugin import IPlugin, getPlugins
except ImportError:
   pass
else:
   list(getPlugins(iboards.IDMBoards, modules)) # To refresh cache


def getBoardPlugin(name):
   for p in getPlugins(iboards.IDMBoards, modules):
      qual = "%s.%s" % (p.__module__, p.__class__.__name__)
      log.info("Calling Board Module "+qual)
      if p.__module__.split('.')[-1]==name:
         return p
   return None



