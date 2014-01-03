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

from filters import words
import re
import logging
from domotika.db import dmdb
from twisted.internet import reactor, defer, task

log = logging.getLogger("Speech")

def filtertext(txt, lang="it"):
   txt=txt.replace("'", " ")
   tags = re.sub(r'([^\s\w]|_)+', ' ', txt).split()
   cleanw = [i for i in tags if i not in words.REMOVE[lang]]
   actionsidx = [i for i,x in enumerate(cleanw) if x in words.ACTIONS[lang].keys()]
   if len(actionsidx)>0:
      actionidx = max(actionsidx)
      actionname = cleanw[actionidx]
      action = words.ACTIONS[lang][actionname]
      targets = cleanw[actionidx+1:]
   else:
      action = False
      targets = cleanw
      actionname = ""

   return {"clean":cleanw, "action":action, "actionname": actionname, "target":targets}


class VoiceUI(object):

   result=False

   def __init__(self, txt="", confidence=0.0, lang="it"):
      self.txt=txt
      self.lang=lang
      self.confidence=confidence
      self.result=filtertext(txt, lang)
      log.debug("Recognized '"+str(txt)+"' with confidence "+str(confidence) )
      log.info("Filter TEXT is: "+str(self.result)+" with confidence "+str(confidence) )

   def getSpeechActions(self):
      def actionsres(res):
         return res
      if self.result:
         return dmdb.checkSpeechActions(" ".join(self.result["target"])).addCallback(actionsres)
      return defer.succeed(False)


if __name__ == '__main__':
   import sys
   print filtertext(sys.argv[1])
