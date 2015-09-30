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

from twisted.application import service, internet
from twisted.internet import protocol, reactor, defer
from twisted.internet import error as tw_error
from twisted.protocols import basic
import socket, logging, time
from starpy import error, fastagi
import os, logging, time, sys
#from domotika.clouds.google import tts, speech
from domotika.clouds.google import tts as googletts
from domotika.clouds.google import speech
from domotika.clouds.responsivevoice import tts
import tempfile
from txscheduling.cron import CronSchedule, parseCronLine
from dmlib.utils import genutils

log = logging.getLogger( 'FastAGI' )

FAILURE_CODE = -1
LOOPLIMIT = 1800

QUARANTADUE=["dimmi la risposta alla domanda fondamentale sulla vita l'universo e tutto quanto",
             "dimmi la risposta alla domanda fondamentale sulla vita luniverso e tutto quanto",
             "quale la risposta alla domanda fondamentale sulla vita l'universo e tutto quanto",
             "qual e la risposta alla domanda fondamentale sulla vita l'universo e tutto quanto",
             "quale la risposta alla domanda fondamentale sulla vita luniverso e tutto quanto",
             "qual e la risposta alla domanda fondamentale sulla vita luniverso e tutto quanto"]

class BaseCheck(object):

   def __init__(self, fagi):
      self.fagi = fagi
      self.core = fagi.core
      self.extension = self.fagi.variables['agi_extension']
      self.context = self.fagi.variables['agi_context']
      self.variables = self.fagi.variables
      self.start()

   def start(self):
      self.close()

   def getAction(self):
      self.core.getAction(self.extension, self.context).addCallbacks(
         self.checkAction, self.close)

   def getUser(self):
      #self.fagi.getPeerState(self.extension).addCallbacks(
      self.fagi.isValidExten(self.extension, "domotika_users").addCallbacks(
         self.checkUser, self.close )

   def getTrunks(self):
      self.fagi.isValidExten(self.extension, "domotika_trunk").addCallbacks(
         self.checkTrunk, self.close )

   def getAlias(self, usedomain=True):
      def parseCronAlias(result):
         if result and len(result)>0:
            res=result[0]
            try:
               timedict=parseCronLine(
                  " ".join(
                     [res.min, res.hour, res.day, res.month, res.dayofweek]))
            except:
               return False
            loctime=time.localtime()
            if(loctime.tm_mon in timedict["months"]
               and loctime.tm_mday in timedict["doms"]
               and loctime.tm_wday in timedict["dows"]
               and loctime.tm_hour in timedict["hours"]
               and loctime.tm_min in timedict["minutes"]):
               return res
         return False

      return self.core.getAliases(self.extension, self.context, usedomain).addCallbacks(
         parseCronAlias, self.close).addCallbacks(self.checkAlias, self.close)

   def close(self, *e):
      self.fagi.finish()

class DMSpeechRecognition(BaseCheck):
   
   loopcount=0
   looplimit=LOOPLIMIT
   commandmode=False
   commandlimit=5
   commandcount=0

   def audio(self, name):
      return '/home/domotika/audio/speech-'+name

   def start(self):
      def answered(*a):
         s=fastagi.InSequence()
         s.append(self.fagi.Playback, self.audio('ciao'))
         s.append(self.fagi.Playback, self.audio('comepossoaiutarti'))
         return s().addCallback(self.startlisten)
      return self.fagi.answer().addCallback(answered)
   
   def startlisten(self, *a):
      self.loopcount=0
      self.commandcount=0
      self.commandmode=True
      log.debug("Enter command mode")
      return self.listen()

   def listen(self, *a):
      fname=tempfile.mktemp(prefix="tmpspeech-")
      return self.fagi.recordFile(fname, 'sln', '#', 
                     timeout=15, beep=False, silence=2).addCallback(self.recognize, fname)

   def recognize(self, res, fname):

      def speechres(res):
         if len(res)==0:
            # Speech hasn't recognized any word, silence?
            self.loopcount+=1
            self.commandcount+=1
            if self.loopcount > self.looplimit:
               log.debug("Listen cycle overrun")
               return self.close()
            if self.commandcount > self.commandlimit and self.commandmode:
               log.debug("Exit command mode")
               self.commandmode=False
               return self.fagi.Playback(self.audio("chiamamibisogno")).addCallback(self.listen)
            log.debug("Listen cycle loop number "+str(self.loopcount))
            return self.listen()

         sres=res[0]
         if 'text' in sres:
            log.debug("Recognized: "+str(sres))
            if float(sres["confidence"]) > 0.4:
               if sres['text']==self.core.getTriggerWord():
                  return self.fagi.Playback(
                     self.audio('comepossoaiutarti')).addCallback(
                     self.startlisten
                  )
               elif sres['text']==self.core.getStopWord():
                  s=fastagi.InSequence()
                  if 'grazie' in sres['text']:
                     s.append(self.fagi.Playback, self.audio('prego'))
                  else:
                     s.append(self.fagi.Playback, self.audio('ok'))
                  s.append(self.fagi.Playback, self.audio('ciao'))
                  return s().addCallback(self.close)
               elif sres['text']==self.core.getStopCommandWord():
                  log.debug("Exit command mode")
                  self.commandmode=False
                  s=fastagi.InSequence()
                  if 'grazie' in sres['text']:
                     s.append(self.fagi.Playback, self.audio('prego'))
                  else:
                     s.append(self.fagi.Playback, self.audio('ok'))
                  s.append(self.fagi.Playback, self.audio('chiamamibisogno'))
                  return s().addCallback(self.listen)
               if self.commandmode:
                  if sres['text'] in ['come ti chiami','qual e il tuo nome','dimmi il tuo nome']:
                     return self.fagi.Playback(self.audio('ilmionome')).addCallback(self.startlisten)
                  elif sres['text'] in ['chi e il tuo papa','chi e tuo padre']:
                     return self.fagi.Playback(self.audio('ilmiopapa')).addCallback(self.startlisten)
                  elif sres['text'] in QUARANTADUE:
                     return self.fagi.Playback(self.audio('42')).addCallback(self.startlisten)
                  elif sres['text']=='grazie':
                     return self.fagi.Playback(self.audio('prego')).addCallback(self.listen)
                  else:
                     try:
                        vr = self.core.voiceReceived(sres["text"], sres["confidence"]).addCallback(
                           self.voiceres)
                        return vr
                     except:
                        ares=False
                        log.debug("voiceReceiver failed")
                        return self.voiceres()
               
            else: # low confidence
               if self.commandmode:
                  s=fastagi.InSequence()
                  s.append(self.fagi.Playback, self.audio('noncapito'))
                  s.append(self.fagi.Playback, self.audio('ripeti'))
                  s.append(self.fagi.Playback, self.audio('perfavore'))
                  return s().addCallback(self.startlisten)
         return self.listen()
      log.debug("Starting to recognize text")
      gs=speech.SpeechRec(fname+".sln",maxresults=1)
      return gs.getSpeech(removeorig=True, removeflac=True).addCallback(speechres).addCallback(self.close)

   def voiceres(self, res=()):

      def _remove(res, playfile):
         try:
            os.unlink(playfile)
         except:
            pass
         return self.startlisten()

      def _converted(ret, playfile):
         fname=".".join(playfile.split(".")[:-1])
         return self.fagi.Playback(fname).addCallback(
            _remove, playfile).addErrback(
            _remove, playfile)

      if len(res)>1:
         ares = str(res[0]).lower()
         vres = False
         if res[1]:
            vres = str(res[1]).lower()
         log.debug("voiceReceiver result: "+str(ares)+" "+str(vres))
      else:
         ares = False

      if not ares:
         s=fastagi.InSequence()
         s.append(self.fagi.Playback, self.audio('nonriesco'))
         s.append(self.fagi.Playback, self.audio('ad'))
         s.append(self.fagi.Playback, self.audio('eseguire'))
         return s().addCallback(self.startlisten)

      if ares=='ok' or ares=='true':
         s=fastagi.InSequence()
         s.append(self.fagi.Playback, self.audio('ok'))
         return s().addCallback(self.startlisten)
      #elif ares=='output':
         
      elif ares=='noact':
         s=fastagi.InSequence()
         s.append(self.fagi.Playback, self.audio('nessunacorrispondenza'))
         s.append(self.fagi.Playback, self.audio('forse'))
         s.append(self.fagi.Playback, self.audio('capitomale'))
         return s().addCallback(self.startlisten)
      elif ares and vres:
         gtts=tts.TTS(ares, 'it')
         playfile=tempfile.mktemp(prefix="googletts-", suffix=".sln")
         return gtts.convertAudioFile(fdst=playfile).addCallback(_converted, playfile)
      else:
         s=fastagi.InSequence()
         s.append(self.fagi.Playback, self.audio('noncapito'))
         return s().addCallback(self.startlisten)

class DMPlayFile(BaseCheck):
   
   def start(self):
      def getfname(r):
         return self.fagi.getFullVariable("${PLAYFILE}").addCallback(self.play, r)
      return self.fagi.getFullVariable("${REPLAY}").addCallback(getfname)

   def play(self, fname, replay):
      sequence = fastagi.InSequence()
      sequence.append(self.fagi.answer)
      sequence.append(self.fagi.wait, 3)
      i=0
      while i < int(replay):
         sequence.append(self.fagi.Playback, fname)
         sequence.append(self.fagi.wait,1)
         i+=1
      sequence.append(self.fagi.hangup)
      sequence.append(self.fagi.finish)
      return sequence()

class DMSayText(BaseCheck):

   def start(self):
      def ttsgetlang(r,t):
         return self.fagi.getFullVariable("${TTSLANG}").addCallback(getengine, t, r)
      def getengine(l, r, t):
         return self.fagi.getFullVariable("${TTSENGINE}").addCallback(self.selectEngine, t, l, r)
      def getsaytext(r):
         return self.fagi.getFullVariable("${SAYTEXT}").addCallback(ttsgetlang, r)
      return self.fagi.getFullVariable("${REPLAY}").addCallback(getsaytext)

   def selectEngine(self, engine, saytext, tlang, replay):
      def _converted(ret, playfile):
         return self.play(saytext, replay, 
            ".".join(playfile.split(".")[:-1]), ".".join(playfile.split(".")[-1:]))
      if engine=='google':
         gtts=googletts.TTS(saytext, tlang) 
         playfile=tempfile.mktemp(prefix="googletts-", suffix=".sln")
         return gtts.convertAudioFile(fdst=playfile).addCallback(_converted, playfile)
      elif engine=="responsivevoice":
         gtts=tts.TTS(saytext, tlang)
         playfile=tempfile.mktemp(prefix="googletts-", suffix=".sln")
         return gtts.convertAudioFile(fdst=playfile).addCallback(_converted, playfile)
      else:
         return self.play(saytext, replay)

   def play(self, saytext, replay, playfile=False, fileformat="sln"):
      def _remove(r):
         os.unlink(playfile+"."+fileformat)
      sequence = fastagi.InSequence()
      sequence.append(self.fagi.answer)
      if playfile:
         sequence.append(self.fagi.wait, 1)
      else:
         sequence.append(self.fagi.wait, 3)
      i=0
      while i < int(replay):
         if playfile:
            sequence.append(self.fagi.Playback, playfile)
         else:
            sequence.append(self.fagi.Festival, saytext)
         sequence.append(self.fagi.wait,1)
         i+=1
      sequence.append(self.fagi.hangup)
      sequence.append(self.fagi.finish)
      s = sequence()
      if playfile:
         s.addCallbacks(_remove, _remove)
      return s


class CheckIn(BaseCheck):

   def start(self):
      self.getAlias(usedomain=False)

   def checkAlias(self, res):
      if res:
         alias=res
         if genutils.isTrue(res.launch_voipaction):
            self.core.manageAction(alias.voip_action_name)
         return self.fagi.goTo(alias.contextto, alias.aliasto)
      return self.close()


class CheckInternals(BaseCheck):

   def start(self):
      self.getUser()

   def checkUser(self, res):
      log.debug("CHECKUSER "+res)
      if str(res)=="1":
         return self.fagi.goTo("domotika_users", self.extension)
      self.getAlias()

   def checkAlias(self, res):
      if res:
         alias=res
         if genutils.isTrue(res.launch_voipaction):
            self.core.manageAction(alias.voip_action_name)
         return self.fagi.goTo(alias.contextto, alias.aliasto)  
      self.getAction()              


   def checkAction(self, res):
      if res!='NOACT':
         sequence = fastagi.InSequence()
         sequence.append(self.fagi.answer)
         sequence.append(self.fagi.wait, 1)
         sequence.append(self.fagi.Festival, res)
         sequence.append(self.fagi.hangup)
         sequence.append(self.fagi.finish)
         return sequence()
      self.getTrunks()

   def checkTrunk(self, res):
      if str(res)=="1":
         return self.fagi.goTo("domotika_trunk", self.extension)
      self.close()


class DMFastAGIProtocol( fastagi.FastAGIProtocol ):
  """
  The clean FastAGIProtocol implement all AGI commands available.
  Anyway, it is usefull to use many of dialplan applications
  from AGI with EXEC agi command to have a complete control
  over a call, so, instead to call agi.execute from our apps,
  i prefer to enhance the FastAGIProtocol with some usefull
  commands here like Playback or Queue...
  """

  def lineReceived(self, line):
    if str(line)=='HANGUP':
      return self.finish()
    return fastagi.FastAGIProtocol.lineReceived(self, line)

  def getPeerState(self, ext):
    return self.getFullVariable("${DEVICE_STATE(SIP/"+ext+")}")

  def isValidExten(self, ext, context): 
    return self.getFullVariable("${VALID_EXTEN("+context+","+ext+",1)}")

  def goTo(self, context, extension, priority=1):
    log.debug("Goto to "+str(context)+" "+str(extension)+" "+str(priority))
    sequence = fastagi.InSequence()
    sequence.append(self.setContext, context)
    sequence.append(self.setExtension, extension)
    sequence.append(self.setPriority, priority)
    sequence.append(self.finish)
    return sequence()

 
  def Festival(self, text):
    return self.execute('FESTIVAL', "'"+text+"'")

  def Playback(self, file):
    """ use EXEC Playback instead of STREAM FILE command to play audio files """
    return self.execute('PLAYBACK', file).addCallback(
      self.checkFailure, failure='-1',
    )

  def Background(self, file):
    """ use EXEC Background instead of STREAM FILE command to play audio files """
    return self.execute('BACKGROUND', file).addCallback(
      self.checkFailure, failure='-1',
    )

  def getFullVariable(self, variable):
    def stripBrackets(value):
      return value.strip()[1:-1]
    command = '''GET FULL VARIABLE "%s"''' % (variable,)
    return self.sendCommand(command).addCallback(
        self.checkFailure, failure='0',
    ).addCallback(self.secondResultItem).addCallback(stripBrackets)


  def System(self, cmd):
    """ Execute a shell command on the Asterisk server with the System() application on *"""
    log.debug('Executing shell command %s', cmd)
    def SystemCall(cmd):
      return self.execute('System', cmd).addCallback(
        self.checkFailure, failure='-1'
      )
    def checkSystemReturn(res):
      return self.getVariable('SYSTEMSTATUS').addCallback( CheckExitStatus )

    def CheckExitStatus(result):
      # We need to check SYSTEMSTATUS channel variables to know the result of the command
      # FAILURE or SUCCESS show return status of the command
      log.debug('System command execution returnet with %s', result)
      if result == 'SUCCESS':
        return True
      return False

    return SystemCall(cmd).addCallback( checkSystemReturn )

  def Queue(self, *args):
    """ Queue from dialplan applications """
    return self.execute('QUEUE', *args)

  def setCDRUserfield(self, value):
    """ set the CDR User Field """
    return self.execute('Set', 'CDR(userfield)=%s' % value).addCallback(
      self.checkFailure
    )

  def setLanguage(self, lang):
    """ set the Language of a channel """
    return self.execute('Set', 'CHANNEL(language)=%s' % lang).addCallback(
      self.checkFailure
    )

class DMFastAGIFactory( protocol.Factory ):
  """Factory generating FastAGI server instances
  """
  protocol = DMFastAGIProtocol
  def __init__( self, mainFunction, core ):
    """Initialise the factory

    mainFunction -- function taking a connected FastAGIProtocol instance
      this is the function that's run when the Asterisk server connects.
    """
    self.mainFunction = mainFunction
    self.core = core

  def buildProtocol(self, addr):
    p = self.protocol()
    p.factory = self
    p.core = self.core
    return p


def selectFagiService(service):
   log.debug("FAGI SERVICE: "+str(service))
   if service.variables['agi_network_script'] == 'in':
      CheckIn(service)
   else:
      if service.variables['agi_extension'] == 'domotika_playfile':
         DMPlayFile(service)
      elif service.variables['agi_extension'] == 'domotika_saytext':
         DMSayText(service)
      elif service.variables['agi_extension'] == 'domotika_speechrec':
         DMSpeechRecognition(service)
      elif service.variables['agi_extension'] == 'failed':
         service.hangup()
         service.finish()
      else:
         if service.variables['agi_network_script'] == 'internal':
            CheckInternals(service)
         else:
            service.finish()


def getFastAGI(core):
   f = DMFastAGIFactory(selectFagiService, core)
   return f



