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

from domotika.boards import iboards
from domotika.boards.iotype import BaseBoard, BoardAnalog, BoardInput, BoardOutput, BoardRelay, context2section
from domotika.db import dmdb
from domotika.lang import lang
from zope.interface import implements
from twisted.plugin import IPlugin
from dmlib.utils import webutils as wu
from twisted.internet import defer
from dmlib import constants as C
from twisted.web import microdom as xml

try:
   import hashlib
   md5 = hashlib
   md5.new = hashlib.md5
   sha1 = hashlib.sha1
except:
   import md5
   import sha1



class DMBoard(BaseBoard):

   analist = {}
   inplist = False
   rellist = False
   outlist = False
   hasAnalogs = False
   hasOutputs = True
   hasInputs = True
   hasRelays = True
   hasAmperometers = False


   def __init__(self, host, port, pwd, lang):
      self.fwtype = 'relaymaster'
      self.host = host
      self.port = port
      self.pwd = pwd
      self.lang = lang

   def initialize(self):
      d=self._getBoardConfig()
      d.addCallback(self._setBoardConfig)
      d.addCallback(self._getIOConfig)
      d.addCallback(self._setIOConfig)
      d.addCallback(self._configComplete)
      return d

   def _configComplete(self, *a):
      return defer.succeed(self)

   def _setBoardConfig(self, res):
      self.boardXML = xml.parseXMLString(res)
      return defer.succeed(True)

   def _setIOConfig(self, res):
      xmlsha = sha1()
      xmlsha.update(res)
      self.iohash = xmlsha.hexdigest()
      self.ioXML = xml.parseXMLString(res)
      return defer.succeed(True)   

   def _getBoardConfig(self, *a):
      return wu.getPage("http://"+self.host+":"+str(self.port)+"/ajax.xml", http_user="system", http_password=self.pwd)

   def _getIOConfig(self, *a):
      return wu.getPage("http://"+self.host+":"+str(self.port)+"/ioconf.xml", http_user="system", http_password=self.pwd)

   def getAnalogsNames(self):
      return self.analist

   def getInputsNames(self):
      if not self.inplist:
         ret = {}
         for i in xrange(1, 9):
            inp=BoardInput()
            inp.name = xml.getElementsByTagName(self.ioXML, 'i'+str(i))[0].firstChild().toxml()
            inp.num = i
            inp.host = self.host
            inp.section = 'none'
            inp.enabled = 1
            inp.button_name = inp.name.replace(".", " ").capitalize()
            ret[inp.num]=inp
         self.inplist=ret
         return ret
      return self.inplist

   def getRelaysConfs(self):
      if not self.rellist:
         self.rellist = {}
         self.getOutputsConfs()
      return self.rellist

   def getOutputsConfs(self):
      if not self.outlist:
         if not self.rellist: self.rellist={}
         ret = {}
         rel = {}
         for i in xrange(1, 9):
            out=BoardOutput()
            out.hasRelays=True
            out.hasPwms=False
            out.hasAmperometers=self.hasAmperometers
            out.num = i
            rel[1],rel[2] = BoardRelay(),BoardRelay()
            outstring = xml.getElementsByTagName(self.ioXML, 'o'+str(i))[0].firstChild().toxml()
            if ';' in outstring:
               data=outstring.replace(" ", "").split(";")
            else:
               data=outstring.replace(" ", "").split("|")
            out.dname=data[0]
            out.button_name = out.dname.replace(".", " ").capitalize()
            out.ctx=data[1]
            out.section=context2section(out.ctx)
            out.runtime1=data[2]
            out.runtime2=data[3]
            if len(data) > 16:
               out.breakdelay1=data[4]
               out.rearm1=data[5]
               out.breakdelay2=data[6]
               out.rearm2=data[7]
               out.retard1=data[8]
               out.retard2=data[9]
               out.relay1=data[10]
               out.relay2=data[11]
               out.nanc1=data[12]
               out.nanc2=data[13]
               out.amax1=data[14]
               out.amax2=data[15]
               out.otype=data[16]
               out.enabled=data[17]
            else:
               out.breakdelay1=data[4]
               out.rearm1=0
               out.breakdelay2=data[5]
               out.rearm1=0
               out.retard1=data[6]
               out.retard2=data[7]
               out.relay1=data[8]
               out.relay2=data[9]
               out.nanc1=data[10]
               out.nanc2=data[11]
               out.amax1=data[12]
               out.amax2=data[13]
               out.otype=data[14]
               out.enabled=data[15]
            out.host = self.host
            rel[1].host, rel[2].host = out.host, out.host
            rel[1].dname, rel[2].dname = out.dname, out.dname
            rel[1].ctx, rel[2].ctx = out.ctx, out.ctx
            rel[1].section, rel[2].section = out.section, out.section
            rel[1].runtime = out.runtime1
            rel[2].runtime = out.runtime2
            rel[1].breakdelay = out.breakdelay1
            rel[1].rearm = out.rearm1
            rel[2].breakdelay = out.breakdelay2
            rel[2].rearm = out.rearm2
            rel[1].retard = out.retard1
            rel[2].retard = out.retard2
            rel[1].num = out.relay1
            rel[2].num = out.relay2
            rel[1].nanc = out.nanc1
            rel[2].nanc = out.nanc2
            rel[1].amax = out.amax1
            rel[2].amax = out.amax2
            rel[1].otype, rel[2].otype = out.otype, out.otype
            rel[1].enabled, rel[2].enabled = out.enabled, out.enabled
            rel[1].outnum, rel[2].outnum = i, i
            for r in rel.keys():
               if int(out.otype)==C.DM_OUTPUT_TYPE_ONOFF:
                  rel[r].act=int(C.IKAP_ACT_CHANGE)
                  rel[r].msgtype=C.IKAP_MSG_ACTION
                  rel[r].button_name=rel[r].dname.replace(".", " ").capitalize()
               elif int(out.otype)==C.DM_OUTPUT_TYPE_SIGNALING:
                  rel[r].act=int(C.IKAP_ACT_CHANGE)
                  rel[r].msgtype=C.IKAP_MSG_NOTIFY
                  rel[r].button_name=rel[r].dname.replace(".", " ").capitalize()
               elif int(out.otype)==C.DM_OUTPUT_TYPE_2_RELAY_EXCLUSIVE:
                  if r==1:
                     rel[r].act=int(C.IKAP_ACT_UP)
                     rel[r].button_name=rel[r].dname.replace(".", " ").capitalize()+" "+lang.iostring("up", self.lang)
                  else:
                     rel[r].act=int(C.IKAP_ACT_DOWN)
                     rel[r].button_name=rel[r].dname.replace(".", " ").capitalize()+" "+lang.iostring("down", self.lang)
                  rel[r].msgtype=C.IKAP_MSG_ACTION
               elif int(out.otype)==C.DM_OUTPUT_TYPE_2_RELAY_INCLUSIVE_ON  \
                  or int(out.otype)==C.DM_OUTPUT_TYPE_2_RELAY_INCLUSIVE_OFF:
                  rel[r].act=int(C.IKAP_ACT_CHANGE)
                  rel[r].msgtype=C.IKAP_MSG_ACTION
                  rel[r].button_name=rel[r].dname.replace(".", " ").capitalize()+" "+str(r)
               elif int(out.otype)==C.DM_OUTPUT_TYPE_OPEN_CLOSE_2_RELAYS:
                  if r==1:
                     rel[r].act=int(C.IKAP_ACT_OPEN)
                     rel[r].button_name=rel[r].dname.replace(".", " ").capitalize()+" "+lang.iostring("open", self.lang)
                  else:
                     rel[r].act=int(C.IKAP_ACT_CLOSE)
                     rel[r].button_name=rel[r].dname.replace(".", " ").capitalize()+" "+lang.iostring("close", self.lang)
                  rel[r].msgtype=C.IKAP_MSG_ACTION
               else:
                  rel[r].msgtype=C.IKAP_MSG_NULL
                  rel[r].act=C.IKAP_ACT_NULL
                  rel[r].button_name=rel[r].dname.replace(".", " ").capitalize()

            out.numrel = 1
            out.relays = [rel[1]]
            self.rellist[rel[1].num] = rel[1]
            if int(out.otype) >= C.DM_OUTPUT_TYPE_2_RELAY_EXCLUSIVE:
               out.numrel = 2 
               out.relays.append(rel[2])
               self.rellist[rel[2].num] = rel[2]           
            ret[out.num] = out

         self.outlist = ret
      return self.outlist

class Board(object):
   implements(IPlugin, iboards.IDMBoards)


   def getBoard(self, host, port, pwd, lang):
      return DMBoard(host, port, pwd, lang)


board=Board()
