import logging
import imediasource
import importlib
import os

log = logging.getLogger('Core')

try:
   from twisted.plugin import IPlugin, getPlugins
except ImportError:
   pass
else:
   for i in os.listdir('domotika/mediasources/modules'):
      if os.path.isdir('domotika/mediasources/modules/'+i):
         list(getPlugins(imediasource.IMediaSource, importlib.import_module('domotika.mediasources.modules.'+i))) # To refresh cache


def getMediaSourcePlugin(name, manufacturer='generic'):
   try:
      if os.path.isdir('domotika/mediasources/modules/'+str(manufacturer)):
         mod = importlib.import_module('domotika.mediasources.modules.'+str(manufacturer))
      else:
         mod = importlib.import_module('domotika.mediasources.modules.generic')
   except:
      return None
   for p in getPlugins(imediasource.IMediaSource, mod ):
      qual = "%s.%s" % (p.__module__, p.__class__.__name__)
      log.debug("Calling MediaSource Module "+qual)
      if p.__module__.split('.')[-1]==name:
         return p
   return None



