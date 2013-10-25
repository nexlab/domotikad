###########################################################################
# Copyright (c) 2011-2013 Unixmedia S.r.l. <info@unixmedia.it>
# Copyright (c) 2011-2013 Franco (nextime) Lanza <franco@unixmedia.it>
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

import urllib
from dmlib.utils import webutils as web
from twisted.internet import reactor
import tempfile
from twisted.internet import defer
from twisted.internet import utils as twutils
import os, struct
import json, unicodedata
import logging

try:
   log = logging.getLogger('Core').getChild('Clouds.Google.Speech')
except:
   log = logging.getLogger('Core')

SPEECHURL="https://www.google.com/speech-api/v1/recognize"

def checkEndianess():
   if struct.pack('@h', 1) == struct.pack('<h', 1):
      return 'little'
   return 'big'

class SpeechRec(object):

   agent="Mozilla/5.0 (X11; Linux) AppleWebKit/537.1 (KHTML, like Gecko)"
   resulttext=False
   grammar="builtin:dictation" # "builtin:search"
   

   def __init__(self, fname, dstname=False, lang="it", maxresults=1, gain=-5):
      self.orig = fname
      self.gain = gain
      if not dstname or not dstname.endswith(".flac"):
         self.flacname = tempfile.mktemp(prefix="googlespeechrec-", suffix=".flac")
      else:
         self.flacname = dstname
      self.lang = lang
      self.maxresults = maxresults

   def _convertFile(self):
      if self.orig.endswith(".wav"):
         o1=["-t","wav"]
         o2=["-r","8000"]
         o3=[]
      elif self.orig.endswith(".sln"):
         o1=["-b","16","-t","raw","-r","8000","-e","signed-integer","--endian",checkEndianess()]
         o2=[]
         o3=["norm", str(self.gain),"highpass","100"]
      elif self.orig.endswith(".flac"):
         return twutils.getProcessOutput("/bin/cp", ["-a", self.orig ,self.flacname])
      else:
         o1=[]
         o2=["-r","8000"]
         o3=[]
      opts=['-q',"-V 0"]+o1+[self.orig]+o2+["-t","flac",self.flacname]+o3
      p=twutils.getProcessOutput("/usr/bin/sox", opts)          
      return p

   def removeOrigFile(self):
      if os.path.exists(self.orig):
         os.unlink(self.orig)

   def removeFlacFile(self):
      if os.path.exists(self.flacname):
         os.unlink(self.flacname)

   def _webRequest(self):
      args="?xjerr=1&client=chromium&pfilter=0&lang="+self.lang+"&lm="+self.grammar+"&maxresults="+str(self.maxresults)
      headers={"Content-Type": "audio/x-flac; rate=8000"}
      f=open(self.flacname,'rb')
      audio=f.read()
      f.close()
      url=SPEECHURL+args
      return web.getPage(url, method='POST', postdata=audio, headers=headers, agent=self.agent)

   def getSpeech(self, removeorig=False, removeflac=False):
      
      def parseres(res):
         if removeflac:
            self.removeFlacFile()
         r=[]
         try:
            rt=json.loads(res)
            for h in rt[u'hypotheses']:
               r.append({'text':unicodedata.normalize('NFKD',h[u'utterance']).encode("ascii","ignore"),"confidence":h[u'confidence']})     
         except:
            r=[{'text':"","confidence":0.0}]
         return defer.succeed(r)
      def fileConverted(*a):
         if removeorig:
            self.removeOrigFile()   
         return self._webRequest().addCallback(parseres)

      if self.resulttext:
         return defer.succeed(self.resulttext)
      if os.path.exists(self.orig):
         p=self._convertFile()
         return p.addCallback(fileConverted)
      return defer.fail("Cannot get text for "+self.orig)
      


if __name__ == '__main__':
   import sys
   def printres(res):
      print res
      reactor.stop()
   gs=SpeechRec(sys.argv[1],maxresults=3)
   gs.getSpeech().addCallback(printres)
   reactor.run()

