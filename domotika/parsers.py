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


from dmlib.utils import genutils
from twisted.internet import defer
from db import dmdb
from dmlib import dmdomain



def statusParser(trigger, sun, restype='string'):

   def matchReturnDomain(match, val, reverse=False):
      if dmdomain.match(match, val):
         if restype=='int':
            if reverse: return 0
            return 1
         else:
            if reverse: return False
            return True
      if restype=='int':
         if reverse: return 1
         return 0
      else:
         if reverse: return True
         return False


   def parseReturn(qres, reverse=False):
      qr=False
      if type(qres).__name__=='int' and restype=='int':
         qr=qres
      else:
         if type(qres).__name__=='int':
            qres=str(qres)
         if qres and len(qres)>0:
            try:
               qr=qres[0][0]
            except:
               if type(qres).__name__=='str':
                  qr=qres
               elif restype=='string':
                  qr=str(qres)
               else:
                  qr=False
      if qr:
         if restype in ['int','bool']:
            if qr in ["1",1,'true','y','si','yes']:
               if restype=='int':
                  if reverse: return 0
                  return 1
               else: # restype=='bool':
                  if reverse: return False
                  return True
         else:
            return qr
      if restype=='int':
         if reverse: return 1
         return 0
      else:
         if restype=='bool' and reverse: return True
         return False


   def doQuery(sqlstring, reverse=False):
      return dmdb.Registry.DBPOOL.runQuery(sqlstring).addCallback(parseReturn, reverse)


   oneatleast=False
   reverse=False
   if ((trigger.startswith("REV ANY ") or trigger.startswith("REV:ANY:") or
       trigger.startswith("ANY REV ") or trigger.startswith("ANY:REV:")) and
       restype!='string'):
      reverse=True
      oneatleast=True
      trigger=trigger[8:]
   elif trigger.startswith("REV ") or trigger.startswith("REV:") and restype!='string':
      reverse=True
      trigger=trigger[4:]
   elif trigger.startswith("ANY ") or trigger.startswith("ANY:") and restype!='string':
      oneatleast=True
      trigger=trigger[4:] 

   if not reverse:
      defres=False
      if restype=='int':
         defres=0
   else:
      defres=True
      if restype=='int':
         defres=1



   ret=defer.succeed(defres)
   if trigger.startswith("FILE ") or trigger.startswith("FILE:"):
      if os.path.isfile(trigger[5:].split()[0]):
         f = open(trigger[5:].split()[0], "r")
         ret=defer.succeed(parseReturn(f.read(), reverse))
         f.close()
   elif trigger.startswith("FILEEXISTS ") or trigger.startswith("FILEEXISTS:"):
      if os.path.isfile(trigger[11:].split()[0]):
         ret=defer.succeed(parseReturn('1', reverse))
      else:
         ret=defer.succeed(parseReturn('0', reverse))
   elif trigger.startswith("SYSTEM ") or trigger.startswith("SYSTEM:"):
      cmdline=trigger[7:]
      ret=subprocess.Popen(cmdline.replace("\r\n", " "),
         shell=True, stdout=subprocess.PIPE,preexec_fn = os.setsid, close_fds=True)
      ret=defer.succeed(parseReturn(ret.communicate()[0], reverse))
   elif trigger.startswith("SQL ") or trigger.startswith("SQL:"):
      sqlstring = trigger[4:]
      ret=doQuery(sqlstring, reverse)
   elif trigger.startswith("TMPFLAG ") or trigger.startswith("TMPFLAG:"):
      fl=trigger[8:].split()
      if len(fl)>0:
         try:
            ret=doQuery("SELECT COUNT(name) FROM flags WHERE name='"+str(fl[0])+"'", reverse)
         except:
            pass
   elif (trigger.startswith("CRONSTATUS ") or trigger.startswith("CRONSTATUS:") or   # DEPRECATED, USE CRONACTIVE
         trigger.startswith("CRONACTIVE ") or trigger.startswith("CRONACTIVE:")):
      tid=trigger[11:].split()
      if len(tid)>0 and genutils.is_number(tid[0]):
         try:
            ret=doQuery("SELECT active FROM timers WHERE id="+str(tid[0]), reverse)
         except:
            pass
      elif len(tid)>0 and len(tid[0])>0:
         try:
            if not oneatleast:
               if not reverse:
                  ret=doQuery("SELECT MIN(active) from timers WHERE DMDOMAIN(timer_name, '"+str(tid[0])+"')=1") # All active?
               else:
                  ret=doQuery("SELECT MAX(active) from timers WHERE DMDOMAIN(timer_name, '"+str(tid[0])+"')=1", reverse=True) # all off?
            else:
               if not reverse:
                  ret=doQuery("SELECT MAX(active) from timers WHERE DMDOMAIN(timer_name, '"+str(tid[0])+"')=1") # at least one active?         
               else
                  ret=doQuery("SELECT MIN(active) from timers WHERE DMDOMAIN(timer_name, '"+str(tid[0])+"')=1", reverse=True) # at least one off?
         except:
            pass
   elif trigger.startswith("ACTIONACTIVE ") or trigger.startswith("ACTIONACTIVE:"):
      aid=trigger[13:].split()
      if len(aid)>0 and genutils.is_number(aid[0]):
         try:
            ret=doQuery("SELECT active FROM actions WHERE id="+str(aid[0]), reverse)
         except:
            pass
      elif len(aid)>0 and len(aid[0])>0:
         try:
            if not oneatleast:
               if not reverse:
                  ret=doQuery("SELECT MIN(active) from actions WHERE DMDOMAIN(action_name, '"+str(tid[0])+"')=1") # All active?
               else:
                  ret=doQuery("SELECT MAX(active) from actions WHERE DMDOMAIN(action_name, '"+str(tid[0])+"')=1", reverse=True) # all off?
            else:
               if not reverse:
                  ret=doQuery("SELECT MAX(active) from actions WHERE DMDOMAIN(action_name, '"+str(tid[0])+"')=1") # at least one active?         
               else
                  ret=doQuery("SELECT MIN(active) from actions WHERE DMDOMAIN(action_name, '"+str(tid[0])+"')=1", reverse=True) # at least one off?

         except:
            pass

   elif (trigger.startswith("BOARDSTATUS ") or trigger.startswith("BOARDSTATUS:")        # DEPRECATED, USE BOARDACTIVE
         trigger.startswith("BOARDACTIVE ") or trigger.startswith("BOARDACTIVE:")):
      bname=trigger[12:].split()
      if len(bname)>0:
         try:
            ret=doQuery("SELECT online FROM dmboards WHERE name='"+str(bname[0])+"'", reverse)
         except:
            pass
      else:
         try:
            if not oneatleast:
               if not reverse:
                  ret=doQuery("SELECT MIN(online) FROM dmboards")
               else:
                  ret=doQuery("SELECT MAX(online) FROM dmboards", True)
            else:
               if not reverse:
                  ret=doQuery("SELECT MAX(online) FROM dmboards")
               else:
                  ret=doQuery("SELECT MIN(online) FROM dmboards", True)
         except:
            pass

   elif trigger.startswith("INPSTATUS ") or trigger.startswith("INPSTATUS:"):
      tid=trigger[10:].split()
      if len(tid)>0 and genutils.is_number(tid[0]):
         try:
            ret=doQuery("SELECT status FROM inpstatus WHERE buttonid="+str(tid[0]), reverse)
         except:
            pass
   elif trigger.startswith("RELSTATUS ") or trigger.startswith("RELSTATUS:"):
      tid=trigger[10:].split()
      if len(tid)>0 and genutils.is_number(tid[0]):
         try:
            ret=doQuery("SELECT status FROM relstatus WHERE buttonid="+str(tid[0]), reverse)
         except:
            pass
   elif trigger.startswith("ACTSTATUS ") or trigger.startswith("ACTSTATUS:"):
      tid=trigger[10:].split()
      if len(tid)>0 and genutils.is_number(tid[0]):
         try:
            ret=doQuery("SELECT status FROM actstatus WHERE buttonid="+str(tid[0]), reverse)
         except:
            pass
   elif trigger.startswith("AMPSTATUS ") or trigger.startswith("AMPSTATUS:"):
      if ':' in trigger:
         amp=trigger[10:].split(":")
      else:
         amp=trigger[10:].split()
      if len(amp)>0 and restype=='string':
         if genutils.is_number(amp[0]):
            try:
               ret=doQuery("SELECT ampere from relstatus WHERE buttonid="+str(amp[0]), reverse=False)
            except:
               pass
      elif len(amp)>2 and restype in ['bool','int']:
         if genutils.is_number(amp[0]) and amp[1] in ['<=','>=','=','!=','>','<'] and genutils.is_number(amp[2]):
            try:
               ret=doQuery("SELECT COUNT(ampere) from relstatus where ampere"+str(amp[1])+str(amp[2])+" and buttonid="+str(amp[0]), reverse)
            except:
               pass
   elif trigger.startswith("ANASTATUS ") or trigger.startswith("ANASTATUS:"):
      if ':' in trigger:
         ana=trigger[10:].split(":")
      else:
         ana=trigger[10:].split()
      if len(ana)>0 and restype=='string':
         if genutils.is_number(ana[0]):
            try:
               ret=doQuery("SELECT status from anastatus WHERE buttonid="+str(ana[0]), reverse=False)
            except:
               pass
      elif len(ana)>2 and restype in ['bool','int']:
         if genutils.is_number(ana[0]) and ana[1] in ['<=','>=','=','!=','>','<'] and genutils.is_number(ana[2]):
            try:
               ret=doQuery("SELECT COUNT(status) from anastatus where status"+str(ana[1])+str(ana[2])+" and buttonid="+str(ana[0]), reverse)
            except:
               pass
   elif trigger.startswith("AMPDOMAIN ") or trigger.startswith("AMPDOMAIN:"):
      dmctx=""
      if ':' in trigger:
         dmd=trigger[10:].split(":")
      else:
         dmd=trigger[10:].split()
      if len(dmd)>1 and restype=='string' and dmd[0] in ['SUM','AVG','MIN','MAX','COUNT']:
         try:
            ret=doQuery("select "+dmd[0]+"""(relstatus.ampere) from relstatus,relay
                        WHERE relstatus.buttonid=relay.id AND DMDOMAIN(relay.domain, '"""+str(dmd[1])+"')=1", reverse=False)
         except:
            pass
      elif restype in ['bool','int'] and len(dmd)>3 and dmd[0] in ['SUM','AVG','MIN','MAX','COUNT'] and dmd[2] in ['<=','>=','=','!=','>','<']:
         try:
            ret=doQuery("SELECT IF((select "+dmd[0]+"""(relstatus.ampere) from relstatus,relay
                        WHERE relstatus.buttonid=relay.id AND DMDOMAIN(relay.domain, '"""+str(dmd[1])+"')=1)"+dmd[2]+dmd[3]+",1,0)", reverse)
         except:
            pass
   elif trigger.startswith("ANADOMAIN ") or trigger.startswith("ANADOMAIN:"):
      dmctx=""
      if ':' in trigger:
         dmd=trigger[10:].split(":")
      else:
         dmd=trigger[10:].split()
      if len(dmd)>1 and restype=='string' and dmd[0] in ['SUM','AVG','MIN','MAX','COUNT']:
         try:
            ret=doQuery("select "+dmd[0]+"""(status) from anastatus
                        WHERE DMDOMAIN(ananame, '"""+str(dmd[1])+"')=1", reverse=False)
         except:
            pass
      elif restype in ['bool','int'] and len(dmd)>3 and dmd[0] in ['SUM','AVG','MIN','MAX','COUNT'] and dmd[2] in ['<=','>=','=','!=','>','<']:
         try:
            ret=doQuery("SELECT IF((select "+dmd[0]+"""(status) from anastatus
                        WHERE DMDOMAIN(ananame, '"""+str(dmd[1])+"')=1)"+dmd[2]+dmd[3]+",1,0)", reverse)
         except:
            pass
   elif trigger.startswith("RELDOMAIN ") or trigger.startswith("RELDOMAIN:"):
      dmctx=""
      if ':' in trigger:
         dmd=trigger[10:].split(":")
      else:
         dmd=trigger[10:].split()
      if len(dmd)>1 and genutils.is_number(dmd[1]):
         dmctx=" AND relay.ctx='"+dmd[1]+"'"
      try:
         if not oneatleast:
            if not reverse:
               ret=doQuery("""select min(relstatus.status) from relstatus,relay where 
                  relstatus.buttonid=relay.id AND DMDOMAIN(relay.domain,'"""+str(dmd[0])+"')=1"+dmctx, reverse=False) # all closed
            else:
               ret=doQuery("""select max(relstatus.status) from relstatus,relay where 
                  relstatus.buttonid=relay.id AND DMDOMAIN(relay.domain,'"""+str(dmd[0])+"')=1"+dmctx, reverse=True) # all open
         else:
            if not reverse:
               ret=doQuery("""select max(relstatus.status) from relstatus,relay where 
                  relstatus.buttonid=relay.id AND DMDOMAIN(relay.domain,'"""+str(dmd[0])+"')=1"+dmctx, reverse=False) # at least one closed
            else:
               ret=doQuery("""select min(relstatus.status) from relstatus,relay where 
                  relstatus.buttonid=relay.id AND DMDOMAIN(relay.domain,'"""+str(dmd[0])+"')=1"+dmctx, reverse=True) # at least one open
      except:
         pass
   elif trigger.startswith("ACTDOMAIN ") or trigger.startswith("ACTDOMAIN:"):
      if ':' in trigger:
         dmd=trigger[10:].split(":")
      else:
         dmd=trigger[10:].split()
      try:
         if not oneatleast:
            if not reverse:
               ret=doQuery("""select min(actstatus.status) from actstatus,actions where 
                  actstatus.buttonid=actions.id AND DMDOMAIN(actions.action_name,'"""+str(dmd[0])+"')=1", reverse=False) # all true
            else:
               ret=doQuery("""select max(actstatus.status) from actstatus,actions where
                  actstatus.buttonid=actions.id AND DMDOMAIN(actions.action_name,'"""+str(dmd[0])+"')=1", reverse=True) # all false
         else:
            if not reverse:
               ret=doQuery("""select max(actstatus.status) from actstatus,actions where
                  actstatus.buttonid=actions.id AND DMDOMAIN(actions.action_name,'"""+str(dmd[0])+"')=1", reverse=False) # at least one true
            else:
               ret=doQuery("""select min(actstatus.status) from actstatus,actions where 
                  actstatus.buttonid=actions.id AND DMDOMAIN(actions.action_name,'"""+str(dmd[0])+"')=1", reverse=True) # at least one false
      except:
         pass
   elif trigger.startswith("INPDOMAIN ") or trigger.startswith("INPDOMAIN:"):
      dmd=trigger[10:].split()
      try:
         if not oneatleast:
            if not reverse:
               ret=doQuery("select MIN(status) FROM inpstatus WHERE DMDOMAIN(inpname, '"+str(dmd[0])+"')=1", reverse=False) # all close
            else:
               ret=doQuery("select MAX(status) FROM inpstatus WHERE DMDOMAIN(inpname, '"+str(dmd[0])+"')=1", reverse=True) # all open
         else:
            if not reverse:
               ret=doQuery("select MAX(status) FROM inpstatus WHERE DMDOMAIN(inpname, '"+str(dmd[0])+"')=1", reverse=False) # at least one close
            else:
               ret=doQuery("select MIN(status) FROM inpstatus WHERE DMDOMAIN(inpname, '"+str(dmd[0])+"')=1", reverse=True) # at least one open
      except:
         pass
   elif trigger.startswith("NETSTATUS"):
      if restype in ['int', 'bool']:
         try:
            testvalue=trigger[10:].split()[0]
            ret=dmdb.getNetStatus().addCallback(matchReturnDomain, testvalue, reverse)
         except:
            pass
      else:
         ret=defer.succeed(dmdb.getNetStatus())
   elif trigger.startswith("STATUS ") or trigger.startswith("STATUS:"):
      if ':' in trigger:
         st=trigger[7:].split(':')
      else:
         st=trigger[7:].split()
      if restype in ['string','int']:
         reverse=False
      if restype in ['bool','int'] and len(st)>2 and st[1] in ['<=','>=','=','!=','>','<','domain']:
         if st[1]=='domain':
            try:
               ret=doQuery("""SELECT COUNT(value) FROM statusrealtime 
                     WHERE DMDOMAIN(status_name, '"""+str(st[0])+"')=1 AND DMDOMAIN(value,'"+st[2]+"')=1", reverse)
            except:
               pass
         elif genutils.is_number(st[2]):
            try:
               ret=doQuery("""SELECT COUNT(value) FROM statusrealtime 
                     WHERE DMDOMAIN(status_name, '"""+str(st[0])+"')=1 AND CONVERT(value, SIGNED)="+st[1]+st[2], reverse)
            except:
               pass
      elif restype in ['bool','int'] and len(st)==2 and genutils.is_number(st[1]):
         try:
            ret=doQuery("""SELECT COUNT(value) FROM statusrealtime 
               WHERE DMDOMAIN(status_name, '"""+str(st[0])+"')=1 AND CONVERT(value, SIGNED)="+st[1], reverse)
         except:
            pass
      elif restype=='string' and len(st)>0:
         try:
            ret=doQuery("SELECT value FROM statusrealtime WHERE DMDOMAIN(status_name,'"+str(st[0])+"')=1")
         except:
            pass
   elif trigger.startswith("UNIQUE ") or trigger.startswith("UNIQUE:"):
      if ':' in trigger:
         st=trigger[7:].split(':')
      else:
         st=trigger[7:].split()
      if restype in ['string','int']:
         reverse=False

      if restype in ['bool','int'] and len(st)>2 and st[1] in ['<=','>=','=','!=','>','<','domain']:
         if st[1]=='domain':
            try:
               ret=doQuery("""SELECT COUNT(value) FROM uniques
                     WHERE DMDOMAIN(name, '"""+str(st[0])+"')=1 AND DMDOMAIN(value,'"+st[2]+"')=1", reverse)
            except:
               pass
         elif genutils.is_number(st[2]):
            try:
               ret=doQuery("""SELECT COUNT(value) FROM uniques
                     WHERE DMDOMAIN(name, '"""+str(st[0])+"')=1 AND CONVERT(value, SIGNED)"+st[1]+st[2], reverse)
            except:
               pass

      elif restype=='string' and len(st)>0:
         try:
            ret=doQuery("SELECT value FROM uniques WHERE DMDOMAIN(name,'"+str(st[0])+"')=1")
         except:
            pass
   elif trigger.startswith('DAYREAL'):
      ret=defer.succeed(sun.getReal()['status']).addCallback(parseReturn, reverse)
   elif trigger.startswith('DAYMAX'):
      ret=defer.succeed(sun.getMax()['status']).addCallback(parseReturn, reverse)
   elif trigger.startswith('DAYCIVIL'):
      ret=defer.succeed(sun.getCivil()['status']).addCallback(parseReturn, reverse)
   elif trigger.startswith('DAYASTRO'):
      ret=defer.succeed(sun.getAstro()['status']).addCallback(parseReturn, reverse)

   elif trigger=="TRUE" or trigger=="1":
      ret= defer.succeed(1).addCallback(parseReturn, reverse)
   elif trigger=="FALSE" or trigger=="0":
      ret= defer.succeed(0).addCallback(parseReturn, reverse)
   return ret

