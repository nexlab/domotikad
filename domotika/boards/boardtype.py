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

import logging
from dmlib import constants as C
from zope.interface import implements
import iboards
from dmlib.utils import webutils as wu
from twisted.internet import defer
from dmlib import constants as C
from twisted.web import microdom as xml
from domotika.lang import lang
from iotype import BoardAnalog, BoardInput, BoardOutput, BoardRelay
from twisted.web import error
from dmlib.utils.pwgen import GeneratePwd
from dmlib.utils import genutils
from twisted.internet import reactor
from domotika.db import dmdb
import urllib

log = logging.getLogger( 'Core' )

try:
   import hashlib
   md5 = hashlib
   md5.new = hashlib.md5
   sha1 = hashlib.sha1
except:
   import md5
   import sha1


# i_[idx]_[ananum+totinp]_[statusnum]_[act]
ANAINDEX={
   'ananame': ['08', '00'],
   'status_name': ['09', '00'],
   'enabled': ['05', '00'],
   'anatype': ['11', '00'],
   'mintime': ['06', '00'],
   'minval': ['12', '00'],
   'maxval': ['13', '00'],
   'continuos_domain': ['02','01'],
   'continuos_msg': ['07','01'],
   'continuos_ctx': ['03','01'],
   'continuos_act': ['01','01'],
   'continuos_time': ['10','01'],
   'continuos_opt': ['14','01'],
   'continuos_optstring': ['15','01'],
   'continuos_dst': ['04','01'],
   'min_domain': ['02','02'],
   'min_msg': ['07','02'],
   'min_ctx': ['03','02'],
   'min_act': ['01','02'],
   'min_level': ['10','02'],
   'min_opt': ['14','02'],
   'min_optstring': ['15','02'],
   'min_dst': ['04','02'],
   'max_domain': ['02','03'],
   'max_msg': ['07','03'],
   'max_ctx': ['03','03'],
   'max_act': ['01','03'],
   'max_level': ['10','03'],
   'max_opt': ['14','03'],
   'max_optstring': ['15','03'],
   'max_dst': ['04','03'],
}



def context2section(ctx):
   if int(ctx) in C.SECTIONS.keys():
      section=C.SECTIONS[int(ctx)]
   else:
      section="none"

   return section


class BaseBoard(object):
   """ """
   implements(iboards.IBoard)

   analist = False
   inplist = False
   rellist = False
   outlist = False
   hasAnalogs = False
   hasOutputs = False
   hasInputs = False
   hasPWMs = False
   hasRelays = False
   pwd=False
   user="system"
   core=False
   firstAna = 13
   numAna = 2
   numInp = 12
   numOut = 12
   initialized = False
   boardid = False 

   analogLock = False
   inputLock = False
   outputLock = False
   pwmLock = False
  
   def __init__(self, core, host, port, pwd, lang):
      #self.fwtype = 'relaymaster'
      self.host = host
      self.port = port
      self.pwd = pwd
      self.lang = lang
      self.core = core

   def endinit(self, res):
      self.initialized=True
      return res

   def initialize(self):
      d=self._getBoardConfig()
      d.addCallback(self._setBoardConfig)
      d.addCallback(self._getIOConfig) 
      d.addCallback(self._setIOConfig) 
      d.addCallback(self._configComplete)
      return d.addCallback(self.endinit)


   def sendUnLock(self):
      def _send(res):
         if res:
            return self.core.boardOK(res.id)
      if (not self.analogLock
         and not self.inputLock
         and not self.outputLock
         and not self.pwmLock):

         boardname=str(xml.getElementsByTagName(self.boardXML, 'cfg_hostname')[0].firstChild().toxml())
         boardip=str(xml.getElementsByTagName(self.boardXML, 'cfg_ip')[0].firstChild().toxml())
         log.info("Unlocking board module "+str(boardname)+" at "+str(boardip))

         if not self.boardid:
            return dmdb.DMBoards.find(where=["name='%s' and ip='%s'" %(boardname, boardip)], limit=1).addCallback(_send)
         return self.core.boardOK(boardid)      

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
      return self.requestPage("http://"+self.host+":"+str(self.port)+"/ajax.xml")
      
   def _getIOConfig(self, *a):
      return self.requestPage("http://"+self.host+":"+str(self.port)+"/ioconf.xml")

   def _requestPageErr(self, err, uri=False, method='GET', postdata=None, nolocation=False, second=False):
      if err.getErrorMessage().split()[0] == '401' and not second:
         log.info('Board '+str(self.host)+' doesn\'t appears to support SETOTP command for uri '+str(uri))
         return wu.getPage(uri, http_user=self.user, http_password=self.pwd, 
            method=method, postdata=postdata).addErrback(self._requestPageErr, uri, nolocation=nolocation, second=True)
      log.error("Page "+str(uri)+"can't be accessed! ("+err.getErrorMessage()+")")
      raise error.Error(err.getErrorMessage().split()[0], err.getErrorMessage())

   def _requestPageOk(self, res, uri):
      log.info('Board '+str(self.host)+' OTP Request OK for uri '+str(uri))
      return res

   def _requestOTPPage(self, uri, pwd, method='GET', postdata=None, nolocation=False):
      log.info("Send OTP Request for "+str(uri)+" with pwd "+str(pwd))
      return wu.getPage(uri, http_user='otp', http_password=str(pwd), method=method, postdata=postdata, nolocation=nolocation
         ).addCallback(self._requestPageOk, uri
         ).addErrback(self._requestPageErr, uri, method, postdata, nolocation)

   def _requestPage(self, res, uri, pwd, method='GET', postdata=None, nolocation=False):
      return self._requestOTPPage(uri, pwd, method, postdata, nolocation)

   def requestPage(self, uri, method='GET', postdata=None, nolocation=False):
      pwd=GeneratePwd(leng=16)
      self.core.setOTP(pwd, self.host)
      d=defer.Deferred()
      d.addCallback(self._requestPage, uri, pwd, method, postdata, nolocation)
      reactor.callLater(.5, d.callback, True)
      return d

   def getAnalogsNames(self):
      return {}

   def getInputsNames(self):
      return {}

   def getRelaysConfs(self):
      return {}

   def getOutputsConfs(self):
      return {}


class ANABoard(object):

   def getAnalogsNames(self):
      if not self.analist:
         ret = {}
         for i in [self.firstAna, self.firstAna+self.numAna-1]:
            ana=BoardAnalog()
            ana.name = xml.getElementsByTagName(self.ioXML, 'i'+str(i))[0].firstChild().toxml()
            ana.num = i-12
            ana.host = self.host
            ana.section = 'none'
            ana.enabled = 1
            ana.button_name = ana.name.replace(".", " ").capitalize()
            ret[ana.num] = ana
         self.analist=ret
         return ret
      return self.analist

   def syncAnalogs(self):
      if self.analogLock:
         return
      self.analogLock=True
      if not self.initialized:
         self.initialize().addCallback(
            self._ioAnalogsDelete).addCallback(
            self._syncAnalogs)
      else:
         self._ioAnalogsDelete().addCallback(
         self._syncAnalogs)

   def _ioAnalogsDelete(self, res=None):
      boardname=str(xml.getElementsByTagName(self.boardXML, 'cfg_hostname')[0].firstChild().toxml())
      boardip=str(xml.getElementsByTagName(self.boardXML, 'cfg_ip')[0].firstChild().toxml())
      return dmdb.runOperation("DELETE FROM ioconf_analogs WHERE boardname='%s' AND boardip='%s'" %(str(boardname), str(boardip)))

   def _syncAnalogs(self, res=None):
      boardname=str(xml.getElementsByTagName(self.boardXML, 'cfg_hostname')[0].firstChild().toxml())
      boardip=str(xml.getElementsByTagName(self.boardXML, 'cfg_ip')[0].firstChild().toxml())
      log.info("Syncing board "+str(boardname)+" at "+str(boardip))
      for i in [self.firstAna, self.firstAna+self.numAna-1]:
         aname=xml.getElementsByTagName(self.ioXML, 'i'+str(i))[0].firstChild().toxml()
         for n in xrange(1, 5):
            sconf=str(xml.getElementsByTagName(self.ioXML, 'i'+str(i)+'s'+str(n))[0].firstChild().toxml()).split(';')
            d=dmdb.IOConfAnalogs()
            d.boardname=boardname
            d.boardip=boardip
            d.ananum=i-self.firstAna+1
            d.ananame=aname
            d.status_num=n
            d.status_name=sconf[0]
            d.enabled='yes' if sconf[2]=='1' else 'no'
            d.anatype=int(sconf[3])
            d.mintime=int(sconf[1])
            d.minval=int(sconf[28])
            d.maxval=int(sconf[29])
            d.continuos_domain=str(sconf[4])
            d.continuos_msg=int(sconf[8])
            d.continuos_ctx=int(sconf[7])
            d.continuos_act=int(sconf[9])
            d.continuos_time=int(sconf[6])
            d.continuos_opt=int(sconf[10])
            d.continuos_optstring=str(sconf[11])
            d.continuos_dst=str(sconf[5])
            d.min_domain=str(sconf[12])
            d.min_msg=int(sconf[16])
            d.min_ctx=int(sconf[15])
            d.min_act=int(sconf[17])
            d.min_level=int(sconf[14])
            d.min_opt=int(sconf[18])
            d.min_optstring=str(sconf[19])
            d.min_dst=str(sconf[13])
            d.max_domain=str(sconf[20])
            d.max_msg=int(sconf[24])
            d.max_ctx=int(sconf[23])
            d.max_act=int(sconf[25])
            d.max_level=int(sconf[22])
            d.max_opt=int(sconf[26])
            d.max_optstring=str(sconf[27])
            d.max_dst=str(sconf[21])
            d.save() 

      self.analogLock=False
      self.sendUnLock()

   def pushAnalogs(self, ananum=False, status='*', dataonly=False, bname=False):
      if self.analogLock:
         return
      if genutils.is_number(status) and int(status) in [1,2,3,4]:
         s=int(status)
      else:
         s=str(status)
      if not ananum or ananum=='*':
         self._pushAnalog(1, s, dataonly, bname).addCallback(lambda x: self._pushAnalog(2, s, dataonly, bname))
      else:
         if genutils.is_number(ananum) and int(ananum) in [1,2]:
            self._pushAnalog(int(ananum), s, dataonly, bname)

   def _sendAnalogIOConf(self, res, dataonly=False):
      def endPush(res):
         log.info("Push for "+str(uri)+" finished")
         self.analogLock=False
         self.sendUnLock()
         return defer.succeed(True)

      def normalize(v):
         if v in ['yes','no']:
            return '1' if v=='yes' else '0'
         return urllib.quote(str(a[k]))

      postdata=""
      for ana in res:
         if dataonly:
            if type(dataonly).__name__!='list':
               dataonly=str(dataonly).replace(" ","").split(",")
         else:
            dataonly=ANAINDEX.keys()
         a=ana.__dict__
         for k in dataonly:
            if k in a.keys():
               if len(postdata)>0:
                  postdata+="&"
               postdata+="i_"+ANAINDEX[k][0]+"_"+str(a['ananum']+self.firstAna-1).zfill(2)+"_"
               postdata+=str(a['status_num']).zfill(2)+"_"+ANAINDEX[k][1]+"="
               postdata+=normalize(a[k])
      uri="http://"+self.host+":"+str(self.port)+"/ioconf.xml"
      log.info("Posting Analog config to "+str(uri))
      log.info(postdata)
      return self.requestPage(uri, method='POST', postdata=postdata, nolocation=True).addCallbacks(endPush, endPush)


   def _getAnalogIOConf(self, res, num, status, dataonly=False, bname=False):
      boardname=bname
      boardip=self.host
      if not bname:
         boardname=str(xml.getElementsByTagName(self.boardXML, 'cfg_hostname')[0].firstChild().toxml())
      #sqlstring="SELECT * FROM ioconf_analogs WHERE boardname='%s' AND boardip='%s'" % (boardname, boardip)
      sqlstring="boardname='%s' AND boardip='%s' and ananum='%s'" % (boardname, boardip, str(num))
      if genutils.is_number(status) and status != '*':
         sqlstring+=" AND status_num='%s'" % str(status)
      elif status!='*':
         sqlstring+=" AND DMDOMAIN(status, '%s')=1"
      #dmdb.runQuery(sqlstring).addCallback(self._sendAnalogIOConf, dataonly)
      return dmdb.IOConfAnalogs.find(where=[sqlstring]).addCallback(self._sendAnalogIOConf, dataonly)

   def _pushAnalog(self, num, status, dataonly=False, bname=False):
      log.info('PUSH ANALOG NUMBER '+str(num))
      self.analogLock=True
      if not bname and not self.initialized:
         return self.initialize().addCallback(self._getAnalogIOConf, num, status, dataonly, bname)
      return self._getAnalogIOConf(True, num, status, dataonly, bname)

class INPBoard(object):


   def getInputsNames(self):
      if not self.inplist:
         ret = {}
         for i in xrange(1, self.numInp+1):
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

   def syncInputs(self):
      pass


   def pushInputs(self, inpnum=False, status=1):
      pass

class OUTBoard(object):

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
         for i in xrange(1, self.numOut+1):
            out=BoardOutput()
            out.num = i
            out.hasRelays=True
            out.hasPwms=False
            out.hasAmperometers=self.hasAmperometers
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
               out.rearm2=0
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

   def syncOutputs(self):
      pass

   def pushOutputs(self, numout=False):
      pass
