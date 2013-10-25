import logging
from video import ivideodev
import importlib
import os

log = logging.getLogger('Core')

try:
   from twisted.plugin import IPlugin, getPlugins
except ImportError:
   pass
else:
   for i in os.listdir('domotika/video/modules'):
      if os.path.isdir('domotika/video/modules/'+i):
         list(getPlugins(ivideodev.IVideoDev, importlib.import_module('domotika.video.modules.'+i))) # To refresh cache


def getVideodevPlugin(name, manufacturer='generic'):
   try:
      if os.path.isdir('domotika/video/modules/'+str(manufacturer)):
         mod = importlib.import_module('domotika.video.modules.'+str(manufacturer))
      else:
         mod = importlib.import_module('domotika.video.modules.generic')
   except:
      return None
   for p in getPlugins(ivideodev.IVideoDev, mod ):
      qual = "%s.%s" % (p.__module__, p.__class__.__name__)
      log.debug("Calling Board Module "+qual)
      if p.__module__.split('.')[-1]==name:
         return p
   return None



