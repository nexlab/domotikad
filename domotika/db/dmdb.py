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

from twisted.enterprise import adbapi
from twistar.registry import Registry 
from twistar.dbobject import DBObject
import os, sys
import time
from twisted.internet import defer, reactor
import logging
from dmlib import dmdomain
from dmlib.utils import genutils
from MySQLdb.converters import conversions

from twistar.dbconfig.base import InteractionBase
InteractionBase.LOG = True

try:
   from MySQLdb import OperationalError
except:
   pass

curdir=os.path.abspath(os.path.dirname(sys.argv[0]))
store=None

log = logging.getLogger( 'DMDB' )

class Transaction(object):

   QueryList=[]

   def addQuery(self, query):
      self.QueryList.append(query)

   def executeTransaction(self, dbpool):
      dbpool.runInteraction(self._executeTransaction)

   def _executeTransaction(self, tnx):
      if len(self.QueryList>0):
         for q in iter(self.QueryList):
            #log.debug("EXECUTE TRANSACTION CYCLE "+q)
            tnx.execute(q)
         self.QueryList=[]
         return tnx.fetchall()
      return None


class ReconnectingConnectionPool(adbapi.ConnectionPool):
    def _runInteraction(self, interaction, *args, **kw):
        try:
            return adbapi.ConnectionPool._runInteraction(self, interaction, *args, **kw)
        except OperationalError, e:
            if e[0] not in (2006, 2013):
               raise
            log.debug(" >> MYSQL Resetting DB pool")
            for conn in self.connections.values():
               self._close(conn)
               self.connections.clear()
               ret=adbapi.ConnectionPool._runInteraction(self, interaction, *args, **kw)
               return ret

    def _runOperation(self, trans, *args, **kw):
        trans.execute(*args, **kw)
        return trans.rowcount


def initialize(cfg):
   global store

   conv=conversions.copy()
   conv[246]=float

   if cfg.get('database', 'dbtype').lower() == 'mysql':
      store=ReconnectingConnectionPool(
         'MySQLdb', cfg.get('database', 'dbhost'), cfg.get('database','dbuser'),
         cfg.get('database','dbpass'), cfg.get('database','dmdbname'), cp_max=20, cp_reconnect=True,
         conv=conv)
   else:
      log.error("No supported dbtype")
      return
   Registry.DBPOOL = store
   Registry.dmcfg = cfg
   Registry.Transaction = Transaction()

def dbset():
   global store
   Registry.DBPOOL = store

class Analog(DBObject):
   TABLENAME="analog"

class Output(DBObject):
   TABLENAME="output"

class PWM(DBObject):
   TABLENAME="pwm"

class Relay(DBObject):
   TABLENAME="relay"

class Input(DBObject):
   TABLENAME="input"

class Actions(DBObject):
   TABLENAME="actions"

class ActionStatus(DBObject):
   TABLENAME="actstatus"

class SequenceConf(DBObject):
   TABLENAME="sequence_conf"

class SequenceData(DBObject):
   TABLENAME="sequence_data"
 
class Timers(DBObject):
   TABLENAME="timers"

class MediaSources(DBObject):
   TABLENAME="mediasources"

class QServers(DBObject):
   TABLENAME="qservers"

class DMBoards(DBObject):
   TABLENAME="dmboards"

class MotionDetection(DBObject):
   TABLENAME="motion_detection"

class AsteriskActions(DBObject):
   TABLENAME="voip_actions"

class AsteriskAliases(DBObject):
   TABLENAME="voip_aliases"

class AsteriskEvents(DBObject):
   TABLENAME="voip_events"

class PWMStatus(DBObject):
   TABLENAME="pwmstatus"

class RelStatus(DBObject):
   TABLENAME="relstatus"

class InpStatus(DBObject):
   TABLENAME="inpstatus"

class AnaStatus(DBObject):
   TABLENAME="anastatus"

class Config(DBObject):
   TABLENAME="daemon_config"

   def updateConf(self, section, key, value):
      pass

class Users(DBObject):
   TABLENAME="users"


class UsersGroup(DBObject):
   TABLENAME="users_groups"

class EmailConf(DBObject):
   TABLENAME="email_conf"

class Email(DBObject):
   TABLENAME="email"

class SpeechActions(DBObject):
   TABLENAME="speech_actions"

class Uniques(DBObject):
   TABLENAME="uniques"

class Statuses(DBObject):
   TABLENAME="statuses"
   
class StatusRealtime(DBObject):
   TABLENAME="statusrealtime"

class StatusActions(DBObject):
   TABLENAME="status_actions"

class Notifications(DBObject):
   TABLENAME="notifications"

class Flags(DBObject):
   TABLENAME="flags"

class StatsCharts(DBObject):
   TABLENAME="stats_charts"

class StatsChartsSeries(DBObject):
   TABLENAME="stats_charts_series"

class StatsConf(DBObject):
   TABLENAME="stats_conf"

class StatsData(DBObject):
   TABLENAME="stats_data"

class StatsHistory(DBObject):
   TABLENAME="stats_history"

def cleanFlags():
   Registry.getConfig().delete("flags", where=["expire<="+str(time.time())])

def insertFlag(name, expire=None):
   if expire:
      expire="'"+str(expire)+"'"
   else:
      expire="NULL"
   qstr="INSERT INTO flags (name,expire) VALUES ('"+name+"',"+expire
   qstr+=") ON DUPLICATE KEY UPDATE expire="+expire
   return Registry.DBPOOL.runOperation(qstr)
   

def setUnique(name, value):
   t=time.time()
   querystr="""INSERT INTO uniques (name,value,lastupdate) VALUES ('%s', '%s', '%s') 
               ON DUPLICATE KEY UPDATE value='%s',lastupdate='%s' """ % (str(name), str(value),str(t), str(value),str(t))
   return Registry.DBPOOL.runOperation(querystr)

def updateNetStatus(nst):
   return setUnique('netstatus',nst)

def _retValueQuery(res, defval='DEFAULT'):
   if res:
      return res.value
   else:
      return defval

def getNetStatus():
   return Uniques.find(where=["name='netstatus'"],limit=1).addCallback(_retValueQuery, 'DEFAULT')

def getStatusRealtime(stname):
   return StatusRealtime.find(where=["status_name=?", stname],limit=1).addCallback(_retValueQuery, False)

def _getStatusAction(res):
   if res:
      return res
   return []

def getStatusAction(stname):
   return StatusActions.find(where=["status_name=? AND active=1", stname]).addCallback(_getStatusAction)

def updateStatusRealtime(stname, status, changed=False):
   querystr="INSERT INTO statusrealtime (status_name,value,lastupdate"
   if changed:
      querystr+=",lastchange"
   now=time.time()
   querystr+=") VALUES ('%s','%s','%s'" %(stname, status, str(now))
   if changed:
      querystr+=",'"+str(now)+"'"
   querystr+=") ON DUPLICATE KEY UPDATE lastupdate='%s',value='%s'" % (str(now), status)
   if changed:
      querystr+=",lastchange='%s'" % str(now)
   return Registry.DBPOOL.runOperation(querystr)


def populatePReltimeStatus(dbobj, status=0, ts=0):
   log.debug(" >> POPULATE PWM RELTIME")

def populateRRealtimeStatus(dbobj, status=0, ts=0, amp=0):
   log.debug(" >> POPULATE RELAY REALTIME")
   for res in dbobj:
      rs=RelStatus()
      rs.board_name=res.board_name
      rs.board_ip=res.board_ip
      rs.buttonid=res.id
      rs.outnum=res.outnum
      rs.outtype=res.outtype
      rs.ctx=res.ctx
      rs.relnum=res.relnum
      rs.status=status
      rs.lastupdate=ts
      rs.lastchange=ts
      rs.ampere=amp
      rs.save().addCallback(log.info)

def populateIRealtimeStatus(dbobj, status=0, ts=0):
   log.debug(" >> POPULATE INPUT REALTIME")
   for res in dbobj:
      ist=InpStatus()
      ist.board_name=res.board_name
      ist.board_ip=res.board_ip
      ist.buttonid=res.id
      ist.inpnum=res.inpnum
      ist.inpname=res.inpname
      ist.status=status
      ist.lastupdate=ts
      ist.lastchange=ts
      ist.save().addCallback(log.info)

def populateARealtimeStatus(dbobj, status=0, ts=0):
   log.debug(" >> POPULATE ANALOG REALTIME")
   for res in dbobj:
      ist=AnaStatus()
      ist.board_name=res.board_name
      ist.board_ip=res.board_ip
      ist.buttonid=res.id
      ist.ananum=res.ananum
      ist.ananame=res.ananame
      ist.status=status
      ist.lastupdate=ts
      ist.lastchange=ts
      ist.save().addCallback(log.info)

def emptyRealtimeStatus():
   # XXX Add other realtime statuses
   resetAllRelStatus()
   resetAllInpStatus()
   resetAllAnaStatus()
   resetAllPwmStatus()   

def createRealtimeStatus():
   # XXX Add other realtime statuses
   log.debug(" >> start populating realtime")
   emptyRealtimeStatus()
   Relay.find(where=['active=1']).addCallback(populateRRealtimeStatus)
   Input.all().addCallback(populateIRealtimeStatus)
   Analog.all().addCallback(populateARealtimeStatus)
   Pwm.all().addCallback(populatePRealtimeStatus)


def resetAllPwmStatus():
   return Registry.getConfig().delete("pwmstatus")

def resetAllRelStatus():
   return Registry.getConfig().delete("relstatus")

def resetAllAnaStatus():
   return Registry.getConfig().delete("anastatus")

def resetAllInpStatus():
   return Registry.getConfig().delete("inpstatus")

def updateRelStatusQuery(bname, bip, rel, st, amp):
   querystr="""UPDATE relstatus SET status='%s',lastupdate='%s',ampere='%s' 
               WHERE board_name='%s' AND relnum='%s'""" % (str(st), str(float(time.time())), str(amp), bname, str(rel))
   log.debug("updateRelStatuQuery %s" % querystr)
   return querystr

def _insertRelStatusIfNotUpdated(numrows, bname, bip, rel, status, amp):
   if numrows < 1:
      ts=str(int(time.time()))
      wstr1="board_name='%s' AND relnum='%s' AND board_ip='%s'" %(bname, str(rel), str(bip))
      wstr="active=1 AND board_name='%s' AND relnum='%s' AND board_ip='%s'" %(bname, str(rel), str(bip))
      return RelStatus.find(where=[wstr1]).addCallback(
         _realRelStatusInsert, wstr, status, ts, amp
      )
   return defer.succeed(True)

def _realRelStatusInsert(res, wstr, status, ts, amp):
   if not res:
      Relay.find(where=[wstr]).addCallback(
         populateRRealtimeStatus, status, ts, amp
      )

def updateRelStatus(bname, bip, rel, st, amp=0):
   d = Registry.DBPOOL.runOperation(updateRelStatusQuery(bname, bip, rel, st, amp))
   return d.addCallback(_insertRelStatusIfNotUpdated, bname, bip, rel, st, amp)



def _realInsertAnalog(res, wstr,  status, ts):
      if not res:
         log.debug("insertAnalogStatusIfNotUpdated %s" % wstr)
         Analog.find(where=[wstr]).addCallback(
            populateARealtimeStatus, status, ts
         )


def _insertAnaStatusIfNotUpdated(numrows, bname, bip, ana, status):
   if numrows < 1:
      ts=str(float(time.time()))

      AnaStatus.find(where=['lastupdate>=?',ts])
      wstr="board_name='%s' AND ananum='%s' AND board_ip='%s'" %(bname, str(ana), str(bip))
      log.debug("insertAnalogStatusIfNotUpdated %s" % wstr)
      AnaStatus.find(where=[wstr]).addCallback(
         _realInsertAnalog, wstr, status, ts
      )


def updateAnalogStatusQuery(bname, bip, ana, st):
   querystr="""UPDATE anastatus SET status='%s',lastupdate='%s' 
               WHERE board_name='%s' AND ananum='%s'""" % (str(st), str(float(time.time())), bname, str(ana))
   log.debug("updateAnalogStatuQuery %s" % querystr)
   return querystr

def updateAnalogStatus(bname, bip, ana, st):
   d = Registry.DBPOOL.runOperation(updateAnalogStatusQuery(bname, bip, ana, st))
   d.addCallback(_insertAnaStatusIfNotUpdated, bname, bip, ana, st)

def _insertActionStatusIfNotUpdated(numrows, bip, status, status2):
   if numrows < 1:
      ts=float(time.time())
      log.debug("insertActionStatusIfNotUpdated %s" % str(bip))
      a=ActionStatus()
      a.status=status
      a.status2=status2
      a.lastupdate=ts
      a.lastchange=ts
      a.buttonid=bip
      a.save()

def updateActionStatusQuery(bip, st1, st2):
   querystr="""UPDATE actstatus SET status='%s',status2='%s',lastupdate='%s'
      WHERE buttonid='%s'""" % (str(st1),str(st2),str(float(time.time())),str(bip))
   log.debug("updateActionStatuQuery %s" % querystr)
   return querystr

def updateActionStatus(bip, st1, st2):
   d = Registry.DBPOOL.runOperation(updateActionStatusQuery(bip, st1, st2))
   d.addCallback(_insertActionStatusIfNotUpdated, bip, st2, st2)


def updateInputStatusQuery(bname, bip, inp, st):
   querystr="""UPDATE inpstatus SET status='%s',lastupdate='%s'
      WHERE board_name='%s' AND inpnum='%s'""" % (str(st), str(float(time.time())), bname, str(inp))
   log.debug("updateInputStatuQuery %s" % querystr)
   return querystr

def updateInputStatusFromReceived(host, src, status, iotype, iosubtype):
   qs="""UPDATE inpstatus SET status='%s',lastupdate='%s' 
         WHERE inpname='%s' AND board_ip='%s'""" %(str(status), str(float(time.time())), str(src), str(host))
   log.debug("updateInputStatusFromReceived"+str(qs))
   return Registry.DBPOOL.runOperation(qs)

def _insertInpStatusIfNotUpdated(numrows, bname, bip, inp, status):
   if numrows < 1:
      ts=str(float(time.time()))

      InpStatus.find(where=['lastupdate>=?',ts])
      wstr="board_name='%s' AND inpnum='%s' AND board_ip='%s'" %(bname, str(inp), str(bip))
      log.debug("insertInputStatusIfNotUpdated %s" % wstr)
      InpStatus.find(where=[wstr]).addCallback(
         _realInsertInput, wstr, status, ts
      )

def _realInsertInput(res, wstr,  status, ts):
      if not res:
         log.debug("insertInputStatusIfNotUpdated %s" % wstr)
         Input.find(where=[wstr]).addCallback(
            populateIRealtimeStatus, status, ts
         )

def updateInputStatus(bname, bip, inp, st):
   d=Registry.DBPOOL.runOperation(updateInputStatusQuery(bname, bip, inp, st))
   d.addCallback(_insertInpStatusIfNotUpdated, bname, bip, inp, st)

def addUpdateInputStatus(bname, bip, inp, st):
   Registry.Transaction.addQuery(updateInputStatusQuery(bname, bip, inp, st))

def setInputStatusQuery(src, host, st):
   querystr="""UPDATE inpstatus SET status='%s',lastupdate='%s' 
      WHERE board_ip='%s' AND inpname='%s'""" %(str(st), str(float(time.time())), str(src), str(host))
   return querystr

def setInputStatus(src, host, st):
   log.debug("InpStatus board_ip=%s AND inpname=%s" % (host, src))
   return Registry.DBPOOL.runOperation(setInputStatusQuery(src, host, st))

def commit():
   return Registry.Transaction.executeTransaction(Registry.DBPOOL)

def runQuery(q):
   return Registry.DBPOOL.runQuery(q)

def runOperation(q):
   return Registry.DBPOOL.runOperation(q)


def backwardLastChange(table, bid, ts):
   qstr="UPDATE "+table+" SET lastchange="+str(ts)+" WHERE buttonid="+str(bid)
   runOperation(qstr)


def ioSync(ts):
   qstr="""(select buttonid,status,ampere,'relay' as devtype from relstatus where lastchange>=%s) 
           UNION 
           (select buttonid,status,'0','input' as devtype from inpstatus where lastchange>=%s)
           UNION
           (select buttonid,status,'0','analog' as devtype from anastatus where lastchange>=%s)
           UNION
           (select buttonid,status,status2,'action' as devtype from actstatus where lastchange>=%s)
        """ % (ts,ts,ts,ts)
   return runQuery(qstr)

def getAllRelays():
   return Relay.all()

def resetDynOutputs():
   return Registry.getConfig().delete("output", where=["dynamic=1"])

def resetDynPwms():
   return Registry.getConfig().delete("pwm", where=["dynamic=1"])

def resetDynAnalogs():
   return Registry.getConfig().delete("analog", where=["dynamic=1"])

def resetDynRelays():
   return Registry.getConfig().delete("relay", where=["dynamic=1"])

def resetDynInputs():
   return Registry.getConfig().delete("input", where=["dynamic=1"])

def resetDynActions():
   return Registry.getConfig().delete("actions", where=["dynamic=1"])

def resetBoards():
   return Registry.getConfig().delete("dmboards")

def resetDynMediaSources():
   return Registry.getConfig().delete('video', where=["dynamic=1"])

def getVideoProxyList():
   return QServers.find(where=['mediaproxy=1'], orderby="RAND()")

def matchIncomingPacket(dst, src, msgtype, ctx, act, islocal=False):
   localonly=""
   if not islocal:
      localonly="AND local_only=0"
   sq="rcv_ctx='%s' AND rcv_act='%s' AND rcv_msgtype='%s' AND active=1 " %(str(ctx), str(act), str(msgtype))
   sq+=localonly
   sq+=" AND ikap_src!='%s'"  %(str(src))
   sq+=" AND ((DMDOMAIN(rcv_dst, '%s')=1 AND exact_dst=0) OR (rcv_dst='%s' AND exact_dst > 0))" %(str(dst), str(dst))
   sq+=" AND (DMDOMAIN('%s',rcv_src)=1 OR rcv_src='')""" %(str(src))
   log.debug(sq)
   return Actions.find(where=[sq])


def getActionLoops():
   return Actions.find(where=["active>0 AND action_loop_enabled>0"])

def getActionById(actid):
   return Actions.find(where=["active>0 AND action_loop_enabled>0 and id="+str(int(actid))])

def getSequence(seqname):
   return SequenceConf.find(where=['name=?', seqname], limit=1)

def setNextStep(sname, st):
   #querystr="UPDATE sequence_data SET step_done=1 WHERE step<"+str(st)+" AND sequence_name='"+sname+"'"
   querystr="UPDATE sequence_data SET step_done=IF(position<"+str(st)+",1,0) WHERE sequence_name='"+sname+"'"
   return Registry.DBPOOL.runOperation(querystr)

def getRunningSequences():
   return SequenceConf.find(where=['running=1'])


def getSequenceStep(seqname, randomic=False):
   # XXX Gestione del caso randomic
   return SequenceData.find(where=['sequence_name=? AND step_done=0', seqname], limit=1,orderby="position,id ASC")

def _cleanSequence(res, seqname, randomic):
   return getSequenceStep(seqname, randomic)  

def cleanSequence(seqname, randomic=False):
   return Registry.DBPOOL.runQuery(
         "UPDATE sequence_data SET step_done=0 WHERE sequence_name='"+str(seqname)+"'").addCallback(
      _cleanSequence, seqname, randomic)


def getStatusSchedules():
   return Statuses.find(where=["active=1"])

def getTimerSchedules():
   return Timers.find(
      where=["(fromyear <= YEAR(NOW()) OR fromyear IS NULL) AND (toyear >= YEAR(NOW()) OR toyear IS NULL) AND active = 1 AND (limit_run = 0 OR run_count > 0)"])

def getCron(timerid):
   return Timers.find(where=["id=?", timerid], limit=1)

def getStatus(statusid):
   return Statuses.find(where=["id=?", statusid], limit=1)


def getRelay(bname, bip, rel, active=True):
   wstr1="board_name='%s' AND relnum='%s' AND board_ip='%s'" %(bname, str(rel), str(bip))
   wstr="active=1 AND board_name='%s' AND relnum='%s' AND board_ip='%s'" %(bname, str(rel), str(bip))
   if active:
      return Relay.find(where=[wstr])
   return Relay.find(where=[wstr1])



def addBoard(btype, fwtype, fwver, name, ip, confhash, webport=80, ptype='UDP4', port=6654):
   querystr="""INSERT INTO dmboards  (name,ip,port,transport,webport,type,fwtype,fwversion,last_status_request,last_status_update,detected,online,confhash)
   VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','0','0','1','1','%s')""" %(str(name), str(ip), str(port), str(ptype),
                                                                     str(webport), str(btype), str(fwtype), str(fwver), str(confhash))
   Registry.DBPOOL.runOperation(querystr)


def updateBoardLastStatusRequest(ip):
   Registry.DBPOOL.runOperation("UPDATE dmboards SET last_status_request='%s' WHERE ip='%s'"
                  %(str(float(time.time())), str(ip)))

def updateBoardLastStatus(ip, port, transport, src):
   qstring="UPDATE dmboards SET last_status_update='%s',online=1 WHERE ip='%s'" %(str(float(time.time())), str(ip))
   qstring+=" AND transport='%s'" % transport
   qstring+=" AND port='%s'" % str(port)
   qstring+=" AND name='%s'" % str(src)
   Registry.DBPOOL.runOperation(qstring)


def getLongestUpdatedBoard(num=1):
   return Registry.DBPOOL.runQuery("SELECT ip,id FROM dmboards ORDER BY last_status_request LIMIT %d" % int(num))

def getBoardById(bid=0):
   return DMBoards.find(where=["id=?", bid], limit=1)


def checkMotionDetectionEvent(camera, zone, estatus, etype):
   qstr="""active>0 AND (event_status=%d OR event_status=255)
        AND event_type=%d AND DMDOMAIN('%s', event_camera)=1
        AND DMDOMAIN('%s', event_zone)=1""" %(estatus, etype, str(camera), str(zone))
   log.debug("MOTION EVENT SEARCH: "+qstr)
   return MotionDetection.find(where=[qstr])

def checkAmiEvent(eventtype, caller, called, context, variable=False):
   qstr="""active='yes' AND event_type='%s' AND voip_action_name IS NOT NULL AND DMDOMAIN('%s', context)=1
        AND DMDOMAIN('%s', caller)=1 AND DMDOMAIN('%s', called)=1 """ %(eventtype, str(context), str(caller), str(called))
   if variable:
      qstr+=""" AND DMDOMAIN('%s', variable)=1 """ %(str(variable)) 
   return AsteriskEvents.find(where=[qstr])

def checkAsteriskActionByName(name):
   qstr="""active>0 AND voipaction_name='%s'""" %(str(name))
   return AsteriskActions.find(where=[qstr])

def checkAsteriskAction(extension, context):
   qstr="""active>0 AND extension='%s' AND DMDOMAIN('%s', context_dmdomain)=1""" %(str(extension), str(context))
   return AsteriskActions.find(where=[qstr])

def checkAsteriskAlias(extension, context, usedomain=True):
   if usedomain:
      qstr="""active>0 AND extension='%s' AND DMDOMAIN('%s', context_dmdomain)=1""" %(str(extension), str(context))
   else:
      qstr="""active>0 AND extension='%s' AND context_dmdomain='%s'""" %(str(extension), str(context))
   return AsteriskAliases.find(where=[qstr])


def cleanOldStatus(ts):
   Registry.getConfig().delete("anastatus", where=["lastupdate<"+str(ts)])
   Registry.getConfig().delete("inpstatus", where=["lastupdate<"+str(ts)])
   Registry.getConfig().delete("relstatus", where=["lastupdate<"+str(ts)])
   Registry.getConfig().delete("pwmstatus", where=["lastupdate<"+str(ts)])

def cleanUndetected():
   Registry.getConfig().delete("analog", where=["detected=0 AND dynamic>0"])
   Registry.getConfig().delete("relay", where=["detected=0 AND dynamic>0"])
   Registry.getConfig().delete("input", where=["detected=0 AND dynamic>0"])
   Registry.getConfig().delete("actions", where=["detected=0 AND dynamic>0"])
   Registry.getConfig().delete("output", where=["detected=0 AND dynamic>0"])
   Registry.getConfig().delete("pwm", where=["detected=0 AND dynamic>0"])
   #Registry.getConfig().delete("dmboards", where=["detected=0"])

def boardIPChanged(name, ip, ptype='UDP4', port=6654):
   for table in ['input','relay','analog','inpstatus','relstatus','anastatus']:
      querystr="UPDATE "+table+" SET board_ip='"+ip+"' WHERE board_name='"+name+"'"
      log.debug(querystr)
      Registry.DBPOOL.runOperation(querystr)  

def boardConfigNotChanged(name, ip, webport, ptype='UDP4', port=6654):
   for table in ['output','relay','input','analog']:
      querystr="UPDATE "+table+" SET detected=1 WHERE dynamic=1 AND active=1 AND board_name='"+name+"' AND board_ip='"+ip+"'"
      log.debug(querystr)
      Registry.DBPOOL.runOperation(querystr)
   querystr="UPDATE dmboards SET webport="+str(webport)+" WHERE name='"+name+"' AND ip='"+ip+"' AND port='"+str(port)+"' AND transport='"+ptype+"'"
   Registry.DBPOOL.runOperation(querystr)

def updateWebPort(name, ip, webport, port=6654, ptype='UDP4'):
   querystr="UPDATE dmboards SET webport="+str(webport)+" WHERE name='"+name+"' AND ip='"+ip+"'"
   querystr+=" AND transport='"+str(ptype)+"'"
   if ptype=='TCP4':
      querystr+=" AND port='"+str(port)+"'"
   Registry.DBPOOL.runOperation(querystr)

def initializeAutoDetection():
   for table in ['relay','input','analog','actions','output','pwm']: 
      querystr="UPDATE "+table+" SET detected=0 WHERE dynamic=1"
      log.debug(querystr)
      Registry.DBPOOL.runOperation(querystr)
   querystr="UPDATE dmboards SET detected=0,online=0"
   log.debug(querystr)
   Registry.DBPOOL.runOperation(querystr)      

def checkSpeechActions(speech):
   return SpeechActions.find(where=['speech_string=? AND active>0', speech])

def insertNotify(source, user, msg, expire=0):
   n=Notifications()
   n.source=source
   n.userdst=user
   n.message=msg
   n.expire=expire   
   n.added=float(time.time())
   return n.save()

def markNotifyAsRead(user, nids):
   if nids=='*':
      return runOperation("UPDATE notifications SET readed=1 WHERE userdst='"+str(user)+"' AND readed=0")
   else:
      return runOperation("UPDATE notifications SET readed=1 WHERE userdst='"+str(user)+"' AND id="+str(nids)+" AND readed=0")
      

def expireNotify():
   now = time.time()
   try:
      Registry.DBPOOL.runOperation("DELETE FROM notifications WHERE readed>0 OR expire<="+str(int(now)))
   except:
      pass

def getNotifications(username,onlysince=0,usecount=False):
      def retcount(res):
         if res:
            return res[0][0]
         return 0
      if usecount:
         return runQuery("SELECT COUNT(id) from notifications WHERE readed=0 AND userdst='%s' AND added>='%s'" %(username,str(float(onlysince)))).addCallback(retcount)
      return Notifications.find(where=['readed=0 AND userdst=? AND added>=?', username, float(onlysince)],orderby="added ASC")


def getBoards():
   return DMBoards.find(where=["detected=1"])

def getAllUsers(activeonly=True):
   if activeonly:
      return Users.find(where=["active=1"])
   return Users.find()

def getUsersInGroup(group, activeonly=True):
   if activeonly:
      return UsersGroup.find(where=["group=?", group])
   return UsersGroup.find(where=["group=?", group])


def updateUserData(username, pwd, email, dhome, mhome, tts=False, 
                  lang="it",slide=False, webspeech='touch', speechlang='it-IT', 
                  theme='dmblack',leftb='hidden-sm', rightb='hidden-sm'):
   def onRes(res):
      if res>0:
         return defer.succeed(username+" correctly updated")
      else:
         return defer.fail("User not found")
   password=genutils.hashPwd(pwd)
   qstring="""
      UPDATE users SET email='%s',desktop_homepath='%s',mobile_homepath='%s',last_update='%s',language='%s'""" %(email,dhome,mhome,str(time.time()),lang)
   if password:
      qstring+=",passwd='%s'" %(password)
   if tts:
      qstring+=",tts=1"
   else:
      qstring+=",tts=0"
   if slide:
      qstring+=",slide=1"
   else:
      qstring+=",slide=0"
   qstring+=",webspeech='%s'" % webspeech
   qstring+=",speechlang='%s'" % speechlang
   qstring+=",gui_theme='%s'" % str(theme)
   qstring+=",left_bar='%s'" % str(leftb)
   qstring+=",right_bar='%s'" % str(rightb)
   qstring+=" WHERE username='%s' AND active > 0" %(username)
   log.debug(qstring)
   return runOperation(qstring).addCallback(onRes)
      

def getAllPermissions(user):
   qstring="""
      SELECT * FROM (
            (select default_permissions as permission,'*' as selection, 3 as level from users where username='"""+user+"""')
         UNION
            (select permission_value,permission_selection,1  from users_permissions where username='"""+user+"""')
         UNION
            (select permission_value,permission_selection,2  from groups_permissions WHERE groupname in
               (select  groupname FROM users_groups WHERE username='"""+user+"""')
            )
      ) AS U order by length(selection) DESC,level"""
   return runQuery(qstring)

def getPermissionForPath(user, path):
   if path.startswith('/'): path=path[1:]
   if path.endswith('/'): path=path[:-1]
   path=path.replace("/",".")
   qstring="""
      SELECT * FROM (
            (select default_permissions as permission,'*' as selection, 3 as level from users where username='"""+user+"""')
         UNION
            (select permission_value,permission_selection,1  from users_permissions where username='"""+user+"""' and permission_selector='path'  
               and DMDOMAIN('"""+path+"""', permission_selection)=1 order by length(permission_selection) DESC limit 1)
         UNION
            (select permission_value,permission_selection,2  from groups_permissions WHERE permission_selector='path' and groupname in
               (select  groupname FROM users_groups WHERE username='"""+user+"""') 
               and DMDOMAIN('"""+path+"""', permission_selection)=1 order by length(permission_selection) DESC limit 1
            )
      ) AS U order by length(selection) DESC,level LIMIT 1"""
   return runQuery(qstring)


def getChartData(chartname):
   return StatsCharts.find(where=["name='%s'" % str(chartname)])

def getChartSeries(chartname):
   log.debug("SELECT * FROM stats_charts_series WHERE active=1 AND name='%s'" % str(chartname))
   return StatsChartsSeries.find(where=["name='%s'" % str(chartname)])
