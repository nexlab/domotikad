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

import urllib
from dmlib.utils import webutils as web
from twisted.internet import reactor
import tempfile
from twisted.internet import defer
from twisted.internet import utils as twutils
import os

TTSURI="http://translate.google.com/translate_tts"

def getSampleRate(fname):
   ext=fname.split(".")[-1:]
   if ext in ["silk12","sln12"]: return 12000
   elif ext in ["speex16","slin16","g722","siren7"]: return 16000
   elif ext in ["speex32","slin32","celt32","siren14"]: return 32000
   elif ext in ["celt44","slin44"]: return 44100
   elif ext in ["celt48","slin48"]: return 48000
   else: return 8000
      
class TTS(object):

   agent="Mozilla/5.0 (X11; Linux; rv:8.0) Gecko/20100101"

   def __init__(self, text, lang="it"):
      self.text = urllib.quote(text.encode('utf8', 'ignore'))
      self.audiourl = TTSURI+"?tl="+lang+"&q="+self.text

   def getAudio(self):
      return web.getPage(self.audiourl, agent=self.agent)
 
   def saveAudioFile(self, nfile=False, raw=True):
      if not nfile:
         nfile=tempfile.mktemp(prefix="googletts-", suffix=".mp3")

      def saveFile(fcont):
         f=open(nfile, "w")
         f.write(fcont)
         f.close()
         return defer.succeed(nfile)

      return self.getAudio().addCallback(saveFile)

   def convertAudioFile(self, fsrc=False, fdst=False, removesrc=True, raw=True):
      if not fdst:
         return defer.fail("No destination file")

      def realConvert(fsrc):
         wavtmp=tempfile.mktemp(prefix="googletts-", suffix=".wav")
         #print 'MPG123 CONVERT', fsrc, wavtmp
         wavout = twutils.getProcessOutput("/usr/bin/mpg123", ['-q','-w',wavtmp,fsrc])
         return wavout.addCallback(_finalize, wavtmp, fsrc)

      def _finalize(ret, wavsrc, orig):
         #print 'FINALIZE', wavsrc, fdst
         srate=getSampleRate(fdst)
         if raw: opts=[wavsrc,'-q','-r',str(srate),'-t','raw',fdst]
         else: opts=[wavsrc,'-q','-r',str(srate),fdst]
         p=twutils.getProcessOutput("/usr/bin/sox", opts)
         p.addCallback(_remove, wavsrc)
         if removesrc:
            os.unlink(orig)
         return p

      def _remove(ret, tmpwav):
         os.unlink(tmpwav)
         return ret

      if not fsrc:
         return self.saveAudioFile().addCallback(realConvert)
      return realConvert(fsrc)

if __name__ == '__main__':
   import sys, os

   def converti(fname):
      if len(sys.argv)>4 and sys.argv[4]=='raw':
         tts.convertAudioFile(fname, fdst=sys.argv[1]).addCallback(fine, fname)
      else:
         tts.convertAudioFile(fname, fdst=sys.argv[1], raw=False).addCallback(fine, fname)

   def fine(ex, name):
      print 'FINE', name
      reactor.stop()

   tts=TTS(sys.argv[3], sys.argv[2])
   tts.saveAudioFile().addCallback(converti)
   reactor.run()
