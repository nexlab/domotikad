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

from twisted.internet import reactor, stdio, task, defer
from domotika.plugins import BasePlugin
import base64, os, sys
from dmlib.utils.genutils import configFile
from domotika.db import dmdb
from dmlib import dmdomain
import time
from datetime import datetime
import subprocess

NAME="StatsPlugin"
VERSION=0.1
DESCRIPTION=""
AUTHOR="Franco (nextime) Lanza"
COPYRIGHT=""
LICENSE=""
PLUGINENGINE=0.1

BASEDIR=os.path.abspath(os.path.dirname(sys.argv[0])+"/../../")
CONFIGDIR=os.path.join(BASEDIR, "conf")


def is_number(s):
   try:
      float(s) # for int, long and float
   except ValueError:
      try:
         complex(s) # for complex
      except ValueError:
         return False
   except:
      return False
   return True

class StatsPlugin(BasePlugin):

   name=NAME
   tasks={}
   checkconf=False
   eventreg={}

   def pluginStart(self):
      #self.registerCallback('NETWORK', self.evt_NETWORK)
      self.cfg = configFile(CONFIGDIR+"/domotikad.conf")
      self.cfg.readConfig()
      dmdb.initialize(self.cfg)
      dmdb.StatsConf.find(where=["active=1"]).addCallback(self.startCrons)
      task.LoopingCall(self.checkConfig).start(60)

   def compareConf(self, res):
      if not self.checkconf:
         self.checkconf = res
      else:
         if self.checkconf != res:
            self.checkconf = res
            self.sendlog('info', 'Reloading config')
            self.on_REHASH()

   def checkConfig(self):
      dmdb.StatsConf.find(where=["active=1"]).addCallback(self.compareConf)

   def startCrons(self, res):
      for row in res:
         self.sendlog('debug', row)
         if row.selector.startswith("IKAP:"):
            if len(row.selector.split(":")) > 1:
               sel = row.selector.split(":")[1].split(";")
               selector={}
               for s in sel:
                  if s.split("=") > 1:
                     selector[s.split("=")[0]] = s.split("=")[1]
               if len(selector) > 0:   
                  selector["name"] = row.name
                  selector["stats_type"] = row.stats_type
                  if not "NETWORK" in self.eventreg.keys():
                     self.registerCallback('NETWORK', self.evt_NETWORK)     
                     self.eventreg["NETWORK"] = []
                  self.eventreg["NETWORK"].append(selector)

         elif row.interval > 0:
            if row.selector.startswith("SQL:"):
               if row.stats_type=="realtime":
                  self.tasks[row.name] = task.LoopingCall(self.queryForRealtime, row.name, 
                     row.selector[4:], int(row.expire)*60)
                  self.tasks[row.name].start(int(row.interval)*60)        
               else:
                  self.tasks[row.name] = task.LoopingCall(self.queryForHistory, row.name,
                     row.selector[4:], int(row.expire)*60)
                  self.tasks[row.name].start(int(row.interval)*60)

            elif row.selector.startswith("SQLCOUNT:"):
               if row.stats_type=="realtime":
                  self.tasks[row.name] = task.LoopingCall(self.queryCountForRealtime, row.name, 
                     row.selector[9:], int(row.expire)*60)
                  self.tasks[row.name].start(int(row.interval)*60)
               else:
                  self.tasks[row.name] = task.LoopingCall(self.queryCountForHistory, row.name,
                     row.selector[9:], int(row.expire)*60)
                  self.tasks[row.name].start(int(row.interval)*60)

            elif row.selector.startswith("SYSTEM:"):
               if row.stats_type=="realtime":
                  self.tasks[row.name] = task.LoopingCall(self.systemRealtime, row.name,
                     row.selector[7:], int(row.expire)*60)
                  self.tasks[row.name].start(int(row.interval)*60)
               else:
                  self.tasks[row.name] = task.LoopingCall(self.systemHistory, row.name,
                     row.selector[7:], int(row.expire)*60)
                  self.tasks[row.name].start(int(row.interval)*60)

            elif row.selector.startswith("FILE:"):
               if row.stats_type=="realtime":
                  self.tasks[row.name] = task.LoopingCall(self.fileRealtime, row.name,
                     row.selector[5:], int(row.expire)*60)
                  self.tasks[row.name].start(int(row.interval)*60)
               else:
                  self.tasks[row.name] = task.LoopingCall(self.fileHistory, row.name,
                     row.selector[5:], int(row.expire)*60)
                  self.tasks[row.name].start(int(row.interval)*60)
         else:
            pass
 
   def runQuery(self, query):
      return dmdb.Registry.DBPOOL.runQuery(query)

   def runOperation(self, query):
      return dmdb.Registry.DBPOOL.runOperation(query)

   def updateStatsConfTime(self, name):
      self.runOperation("UPDATE stats_conf SET lastupdate="+str(int(time.time()))+" WHERE name='"+str(name)+"'")

   def deleteOldRecords(self, name, table, expire):
      self.runOperation("DELETE FROM "+table+" WHERE name='"+name+"' AND lastupdate<"+str(time.time()-expire))



   def _queryRes(self, res, name, table='stats_data', sql=True, toadd=False):
      if sql:
         val=res[0][0]
      else:
         val=res
      if is_number(val):
         valnum=float(val)
      else:
         valnum=0

      if table=='stats_data':
         query="""INSERT INTO stats_data (name,datetime,data,txtdata,lastupdate) 
            VALUES ('"""+str(name)+"""',NOW(),'"""+str(float(valnum))+"""','"""+str(val)+"""',"""+str(int(time.time()))+""")"""
         self.runOperation(query)

      elif table=='stats_history':
         now=datetime.now()
         h=str(now.hour).zfill(2)
         n=str(float(valnum))
         date=str(now.year)+"-"+str(now.month).zfill(2)+"-"+str(now.day).zfill(2)
         if not toadd:
            query="""UPDATE stats_history SET 
               lastupdate="""+str(int(time.time()))+""",date=NOW(),h"""+h+"""="""+n+"""
               WHERE name='"""+str(name)+"""' AND date='"""+date+"""'"""
         else:
            query="""UPDATE stats_history SET 
               lastupdate="""+str(int(time.time()))+""",date=NOW(),h"""+h+"""=h"""+h+"""+"""+n+"""
               WHERE name='"""+str(name)+"""' AND date='"""+date+"""'"""
         d = self.runOperation(query)
         d.addCallback(self._queryHistoryInsert, res, name, date, h, n)

   def queryForRealtime(self, name, query, expire):
      self.updateStatsConfTime(name)
      self.deleteOldRecords(name, 'stats_data', expire)
      d = self.runQuery(query)
      d.addCallback(self._queryRes, name, 'stats_data')

   def queryForHistory(self, name, query, expire):
      self.updateStatsConfTime(name)
      self.deleteOldRecords(name, 'stats_history', expire)
      d = self.runQuery(query)
      d.addCallback(self._queryRes, name, 'stats_history')


   def _queryHistoryInsert(self, numrows, res, name, date, h, n):
      if numrows < 1:
         query="""INSERT INTO stats_history (name,date,h"""+h+""",lastupdate)
            VALUES ('"""+name+"""','"""+date+"""',"""+n+""","""+str(int(time.time()))+""")"""
         self.runOperation(query)

   def _queryCountRes(self, res, name, table='stats_data'):

      if table=='stats_data':
         query="""INSERT INTO stats_data (name,datetime,data,txtdata,lastupdate) 
            VALUES ('"""+str(name)+"""',NOW(),'"""+str(len(res))+"','"""+str(len(res))+"""',"""+str(int(time.time()))+")"""
         self.runOperation(query)

      elif table=='stats_history':
         now=datetime.now()
         h=str(now.hour).zfill(2)
         n=str(len(res))
         date=str(now.year)+"-"+str(now.month).zfill(2)+"-"+str(now.day).zfill(2)
         query="""UPDATE stats_history SET lastupdate="""+str(int(time.time()))+""",date=NOW(),h"""+h+"""="""+n+"""
            WHERE name='"""+str(name)+"""' AND date='"""+date+"""'"""
         d = self.runOperation(query)
         d.addCallback(self._queryHistoryInsert, res, name, date, h, n)

   def queryCountForRealtime(self, name, query, expire):
      self.updateStatsConfTime(name)
      self.deleteOldRecords(name, 'stats_data', expire)
      d = self.runQuery(query)
      d.addCallback(self._queryCountRes, name, 'stats_data')

   def queryCountForHistory(self, name, query, expire):
      self.updateStatsConfTime(name)
      self.deleteOldRecords(name, 'stats_history', expire)
      d = self.runQuery(query)
      d.addCallback(self._queryCountRes, name, 'stats_history')

   def fileRealtime(self, name, fname, expire):
      self.updateStatsConfTime(name)
      self.deleteOldRecords(name, 'stats_data', expire)
      r="0"
      try:
         if os.path.isfile(fname):
            f=open(fname, "r")
            r=f.read()
            f.close()
      except:
         pass
      self._queryRes(r, name, 'stats_data', sql=False)


   def fileHistory(self, name, fname, expire):
      self.updateStatsConfTime(name)
      self.deleteOldRecords(name, 'stats_history', expire)
      r="0"
      try:
         if os.path.isfile(fname):
            f=open(fname, "r")
            r=f.read()
            f.close()
      except:
         pass
      self._queryRes(r, name, 'stats_history', sql=False)


   def systemRealtime(self, name, cmd, expire):
      self.updateStatsConfTime(name)
      self.deleteOldRecords(name, 'stats_data', expire)
      r="0"
      try:
         p=subprocess.Popen(cmd.replace("\r\n", " "),
               shell=True, stdout=subprocess.PIPE,preexec_fn = os.setsid, close_fds=True)
         r=p.communicate()[0]
      except:
         pass
      self._queryRes(r, name, 'stats_data', sql=False)


   def systemHistory(self, name, cmd, expire):
      self.updateStatsConfTime(name)
      self.deleteOldRecords(name, 'stats_history', expire)
      r="0"
      try:
         p=subprocess.Popen(cmd.replace("\r\n", " "),
                    shell=True, stdout=subprocess.PIPE,preexec_fn = os.setsid, close_fds=True)
         r=p.communicate()[0]
      except:
         pass
      self._queryRes(r, name, 'stats_history', sql=False)

   def reConfig(self):
      dmdb.StatsConf.find(where=["active=1"]).addCallback(self.startCrons)

   def on_REHASH(self):
      for t in self.tasks.keys():
         try:
            self.tasks[t].stop()
         except:
            pass
         del self.tasks[t]
      self.tasks={}
      for c in self.eventreg.keys():
         self.unregisterCallback(c)
         del self.eventreg[c]
      self.eventreg = {}
      reactor.callLater(3, reConfig)

   def networkEventMatch(self, er, data):
      ret=False
      try:
         # ['IOSTATUS.NOW', 'CAMERETTATER15 ', '65534', '5', '3', '\x02\x02\x01\x00\x06@\x07\xe0\x01\xef\xe5\xf0\x02\x07i\xabP\x00\x00\x00\x00\x00\x00\x00J', '192.168.4.215']
         # ['RELAYSTATUS.CHANGE', 'E0D015         ', '65534', '5', '3', 'RELAY', ' 9 CHANGED TO', 'OFF', '192.168.3.203']
         dst=data[0].replace(" ","")
         src=data[1].replace(" ","")
         ctx=data[2]
         msgtype=data[3]
         act=data[4]
         arg=data[5:len(data)-1]
         host=data[len(data)-1]
         
         if "arg" in er.keys():
            try:
               ret=True
               a=er["arg"].split("|")
               for ar in a:
                  aidx=int(ar.split(",")[0])
                  amatch=ar.split(",")[1]
                  if aidx <= len(arg)-1:
                     if arg[aidx] != amatch:
                        return False
                  else:
                     return False
            except:
               pass

         if "dmdomain" in er.keys():
            ret=True
            if not dmdomain.match(er["dmdomain"], dst):
               return False

         if "revdmdomain" in er.keys():
            ret=True
            if not dmdomain.match(dst, er["dmdomain"]):
               return False      

         if "exactdomain" in er.keys():
            ret=True
            if er["exactdomain"] != dst:
               return False

         if "src" in er.keys():
            ret=True
            if src != er["src"]:
               return False

         if "exactsrc" in er.keys():
            ret=True
            if src != er["exactsrc"]:
               return False

         if "srcdomain" in er.keys():
            ret=True
            if not dmdomain.match(er["srcdomain"], src):
               return False

         if "ctx" in er.keys():
            ret=True
            if int(er["ctx"]) != int(ctx):
               return False

         if "msgtype" in er.keys():
            ret=True
            if int(er["msgtype"]) != int(msgtype):
               return False

         if "act" in er.keys():
            ret=True
            if int(er["act"]) != int(act):
               return False

         if "host" in er.keys():
            ret=True
            if not host.startswith(er["host"]):
               return False

         if "parsearg" in er.keys():
            # XXX TODO Qui bisogna inventarsi un parser per gli argomenti
            return False

         return ret
      except:
         return False
      

   def evt_NETWORK(self, data):
      self.sendlog('info', data)
      if "NETWORK" in self.eventreg.keys():
         for er in self.eventreg["NETWORK"]:
            if self.networkEventMatch(er, data):
               if er["stats_type"] == "realtime":
                  self._queryRes("1", er["name"], 'stats_data', sql=False)
               else:
                  self._queryRes("1", er["name"], 'stats_history', sql=False, toadd=True)
            
