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

from twisted.internet import defer, task, reactor, protocol
from nevow import inevow, rend, tags, loaders, flat, athena, stan, guard
from twisted.web import http, resource, static, server
import time
from common import permissionDenied, uni

from corepost import Response, NotFoundException, AlreadyExistsException
from corepost.web import RESTResource, route, Http
from corepost.convert import convertForSerialization, generateXml, convertToJson
from corepost.enums import MediaType, HttpHeader
import yaml

from functools import wraps, partial
from twisted.web.http import Request
from dmlib.utils import genutils 

import logging, os, sys


log = logging.getLogger( 'Webgui' )

curdir=os.path.abspath(os.path.dirname(sys.argv[0]))


class RestPages(rend.Page):

   def child_(self, ctx):
      return permissionDenied()
      
   def childFactory(self, ctx, name):
      log.debug("No child found (%s)" % name)
      return permissionDenied()

   def locateChild(self, ctx, segments):
      name=segments[0]
      session = inevow.ISession(ctx)
      if '.' in name:
         if name=='v1.0':
            r=RestV10Pages()
            r.core=self.core
            r.session=session
            return r, segments[1:]
         if name=='v1.2' and len(segments)>1:
            r=RestV12Pages()
            r.core=self.core
            r.session=session
            request = inevow.IRequest(ctx)
            request.postpath=list(segments[1:])
            return r, segments[1:]
      return rend.Page.locateChild(self, ctx, name)

class ResponseConversion(object):

   def __init__(self, request, code=200, entity=None, headers={}, ctype=None):
      self.code = code
      self.entity=entity if entity != None else ""
      self.headers=headers
      self.request=request
      self.ctype=ctype
      self.serialized = convertForSerialization(self.entity)
      
      if ctype=='json':
         self.__convertToJson()
      elif ctype=='jsonp':
         self.__convertToJsonp()
      elif ctype=='xml':
         self.__convertToXml()
      elif ctype=='yaml':
         self.__convertToYaml()
      else:
         self.__automagickConversion()

   def __convertToJson(self):
      self.headers[HttpHeader.CONTENT_TYPE]=MediaType.APPLICATION_JSON
      self.response=Response(self.code, convertToJson(self.serialized), self.headers)

   def __convertToJsonp(self):
      self.headers[HttpHeader.CONTENT_TYPE]=MediaType.APPLICATION_JSON
      callback=""
      if 'callback' in self.request.args.keys():
         callback=self.request.args['callback'][0]
      self.response=Response(self.code, callback+"("+convertToJson(self.serialized)+")", self.headers)

   def __convertToXml(self):
      self.headers[HttpHeader.CONTENT_TYPE]=MediaType.APPLICATION_XML
      self.response=Response(self.code, generateXml(self.serialized), self.headers)

   def __convertToYaml(self):
      self.headers[HttpHeader.CONTENT_TYPE]=MediaType.TEXT_YAML
      self.response=Response(self.code, yaml.dump(self.serialized), self.headers)

   def __automagickConversion(self):
      if self.request.path.endswith('/json'):
         self. __convertToJson()
      elif self.request.path.endswith('/jsonp'):
         self. __convertToJsonp()
      elif self.request.path.endswith('/xml'):
         self. __convertToXml()
      elif self.request.path.endswith('/yaml'):
         self.__convertToYaml()
      else:
         if HttpHeader.ACCEPT in self.request.received_headers:
            accept = self.request.received_headers[HttpHeader.ACCEPT]
            if MediaType.APPLICATION_JSON in accept:
               self. __convertToJson()
            elif MediaType.TEXT_YAML in accept:
               self.__convertToYaml()
            elif MediaType.APPLICATION_XML in accept or MediaType.TEXT_XML in accept:
               self. __convertToXml()
            else:
               self. __convertToJson()
         else:
            self. __convertToJson()

   def getResponse(self):
      return self.response


def wrapResponse(f=None, uri=False, res_filter=None, *a, **kw):

   if f and not callable(f):
      uri=f
      f=None

   if f is None:
      return partial(wrapResponse, uri=uri, *a, **kw)

   def okResponse(res, u):
      if isinstance(res, ResponseConversion):
         entity=res.entity
         if res_filter and callable(res_filter):
            entity=res_filter(entity)
         elif res_filter and hasattr(res_filter, '__iter__'):
            for fil in res_filter:
               if callable(fil):
                  entity=fil(entity)
         entity={'result': 'succeed', 'data': entity, 'ts': time.time()}   
         if int(res.code) >= 400:
            entity['result']='fail'
         if uri:
            entity['uri']=uri
         elif u:
            entity['uri']=u
         r = ResponseConversion(res.request, res.code, entity, res.headers, res.ctype).getResponse()
      else:
         if res_filter and callable(res_filter):
            res=res_filter(res)
         elif res_filter and hasattr(res_filter, '__iter__'):
            for fil in res_filter:
               if callable(fil):
                  res=fil(res)
         r={'result': 'succeed', 'data': res, 'ts': time.time()}
         if uri:
            r['uri']=uri
         elif u:
            r['uri']=u
      return r

   def errorResponse(res, u):
      if isinstance(res, ResponseConversion):
         entity={'result': 'fail', 'data': res.entity, 'ts': time.time()}
         if uri:
            entity['uri']=uri
         elif u:
            entity['uri']=u
         r = ResponseConversion(res.request, res.code, entity, res.headers, res.ctype).getResponse()
      else:
         r={'result': 'fail', 'data': res, 'ts': time.time()}
         if uri:
            r['uri']=uri
         elif u:
            r['uri']=u
      return r

   @wraps(f)
   def decorate(*a, **kw):
      ruri=False
      if len(a) > 1 and isinstance(a[1], Request):
         ruri=a[1].uri
      ret=defer.maybeDeferred(f, *a, **kw)
      ret.addCallback(okResponse, ruri)
      ret.addErrback(errorResponse, ruri)
      return ret

   return decorate



class RestCore(object):
   path = ""

   def __init__(self, core, session):
      self.core = core
      self.session = session

   def callbackResponse(self, d, request, search=False):
      def okResponse(res):
         if (('__len__' in dir(res) and len(res)==0) or (not res and res!=0) ) and not search:
            return ResponseConversion(request, code=404, entity=res)
         else:
            return ResponseConversion(request, code=200, entity=res)
      def errorResponse(res):
         return ResponseConversion(request, code=500, entity='Server Error')
      return d.addCallbacks(okResponse, errorResponse)

   def positiveCallback(self, d, request, search=False):
      def okResponse(res):
         if (('__len__' in dir(res) and len(res)==0) or not res or (genutils.is_number(res) and res==0)) and not search:
            return ResponseConversion(request, code=404, entity=res)
         else:
            return ResponseConversion(request, code=200, entity=res)
      def errorResponse(res):
         return ResponseConversion(request, code=500, entity='Server Error')
      return d.addCallbacks(okResponse, errorResponse)  

   def _getRequestArgs(self, request):
      rargs={}
      for k in request.args.keys():
         rargs[k]=request.args[k][0]
      if len(rargs.keys())==0 and request.method=="PUT":
         if(request.content.getvalue()!=""):
            try:
               # NOTE: workaround for PUT empry args
               r = http.parse_qs(request.content.getvalue(), keep_blank_values=1)
               for k in r.keys():
                  rargs[k]=r[k][0]
            except:
               pass
      if request.method in (Http.POST,Http.PUT) and HttpHeader.CONTENT_TYPE in request.received_headers.keys():
         contentType = request.received_headers["content-type"]
         if contentType == MediaType.APPLICATION_JSON:
            try:
               r = dict(rargs.items() + request.json.items())
            except:
               r = request.json
         elif contentType in (MediaType.APPLICATION_XML,MediaType.TEXT_XML):
            try:
               r = dict(rargs.items() + request.xml.items())
            except:
               r = request.xml
         elif contentType == MediaType.TEXT_YAML:
            try:
               r = dict(rargs.items() + request.xml.yaml())
            except:
               r = request.xml.yaml
         else:
            r = rargs
      else:
         r = rargs
      return r
   



class BaseRest(RestCore):

   @route("/")
   def welcome(self, request, *a, **kw):
      return 'Welcome to the Domotika REST API v1.2'

   @route("/keepalive")
   @wrapResponse
   def keepAlive(self, request, *a, **kw):
      return {'time':time.time()}

   @route("/daemonstatus")
   @wrapResponse
   def daemonStatus(self, request, *a, **kw):
      return ResponseConversion(request, entity=self.core.getDaemonStatus())


class BoardRest(RestCore):

   path="boards"

   @route("/")
   def boardlist(self, request, *a, **kw):
      return 'boardlist'

   @route("/autodetect")
   @wrapResponse
   def boardAutodetect(self, request, *a, **kw):
      self.core.startAutoDetection()
      ResponseConversion(request, entity='OK')

   @route("/forceautodetect")
   @wrapResponse
   def boardForceAutodetect(self, request, *a, **kw):
      self.core.startAutoDetection(True)
      ResponseConversion(request, entity='OK')


class CronRest(RestCore):

   path="timers"

   @route("/")
   def timerlist(self, request, *a, **kw):
      return 'timerlist'

class UserRest(RestCore):

   path="users"

   @route("/")
   @wrapResponse
   def userlist(self, request, *a, **kw):
      return self.callbackResponse(self.core.getAllUsers(), request, search=True)

   @route("/userbyname/<username>/", Http.GET)
   @wrapResponse
   def userbyname(self, request=None, username='', *a, **kw):
      return self.callbackResponse(self.core.getUserFromName(username), request)

   @route("/me")
   @wrapResponse
   def getme(self, request=None,*a, **kw):
      return self.callbackResponse(self.core.getUserFromName(self.session.mind.perms.username), request)
   
   @route("/me", Http.PUT)
   @wrapResponse
   def setme(self, request=None,*a, **kw):
      def onOk(res):
         return self.callbackResponse(self.core.getUserFromName(self.session.mind.perms.username), request)
      def onError(res):
         return ResponseConversion(request, code=404, entity="User not found")
      r = self._getRequestArgs(request)
      pwd=False
      tts=False
      lang="it"
      slide=False
      webspeech="touch"
      speechlang="it-IT"
      if 'lang' in r.keys():
         lang=r['lang']
      if 'tts' in r.keys():
         tts=True
      if 'passwd' in r.keys() and r['passwd'] != "":
         pwd=r['passwd']
      if 'slide' in r.keys():
         slide=True
      if 'webspeech' in r.keys() and r['webspeech'] in ['no','touch','continuous']:
         webspeech=r['webspeech']
      if 'speechlang' in r.keys() and r['speechlang'] in ['it-IT','it-CH','en-US','en-GB']:
         speechlang=r['speechlang']
      if 'desktop_homepath' in r.keys() and 'mobile_homepath' in r.keys() and 'email' in r.keys():
         return self.core.updateUserData(self.session.mind.perms.username, pwd, 
                  r['email'], r['desktop_homepath'], r['mobile_homepath'], tts, lang, slide, webspeech, speechlang).addCallbacks(onOk, onError)
      return ResponseConversion(request, code=400, entity="Bad request - error in parameters")
      #return self.callbackResponse(self.core.updateUserFromName(self.session.mind.perms.username), request)  

class ActionRest(RestCore):
   
   path="actions"

   @route("/speech_text", Http.POST)
   @wrapResponse
   def speechText(self, request, *a, **kw):
      r = self._getRequestArgs(request)
      confidence = 1.0
      if 'confidence' in r.keys():
         confidence = float(r['confidence'])
      if 'text' in r.keys():
         return self.core.voiceReceived(r['text'], confidence).addCallback(
            lambda res: res)
      return ResponseConversion(request, code=500, entity="No text in request")

   @route("/setbyid/<int:aid>",(Http.GET,Http.POST))
   @wrapResponse
   def setById(self, request, aid, *a, **kw):
      return self.callbackResponse(self.core.setActionById(aid), request)


class NotifyRest(RestCore):

   path="notifications"

   @route("/", Http.GET)
   @wrapResponse
   def notificationList(self, request, *a, **kw):
      return self.callbackResponse(self.core.getNotifications(self.session.mind.perms.username), request, search=True)

   @route("/", Http.DELETE)
   @wrapResponse
   def markAllRead(self, request, *a, **kw):
      return self.callbackResponse(self.core.markReadNotifications(self.session.mind.perms.username, '*'), request, search=False)

   @route("/<int:nid>", Http.DELETE)
   @wrapResponse
   def markRead(self, request, nid=0, *a, **kw):
      return self.positiveCallback(self.core.markReadNotifications(self.session.mind.perms.username, nid), request, search=False)

   @route("/after/<float:fromts>",Http.GET)
   @wrapResponse
   def notificationsFromTime(self, request, fromts=0, *a, **kw):
      return self.callbackResponse(self.core.getNotifications(self.session.mind.perms.username, fromts), request, search=True)

   @route("/count",Http.GET)
   @wrapResponse
   def notificationCount(self, request, *a, **kw):
      return self.callbackResponse(self.core.getNotifications(self.session.mind.perms.username, usecount=True), request)

   @route("/after/<float:fromts>/count",Http.GET)
   @wrapResponse
   def notificationsFromTimeCount(self, request, fromts=0, *a, **kw):
      return self.callbackResponse(self.core.getNotifications(self.session.mind.perms.username, fromts, usecount=True), request)


class RelayRest(RestCore):
   path="relays"

   @route("/setbyid/<int:rid>",(Http.GET,Http.POST))
   @wrapResponse
   def setById(self, request, rid, *a, **kw):
      return self.callbackResponse(self.core.setRelayById(rid), request)

   @route("/setbyid/<int:rid>/on",(Http.GET,Http.POST))
   @wrapResponse
   def setOnById(self, request, rid, *a, **kw):
      return self.callbackResponse(self.core.setRelayById(rid, 'on'), request)

   @route("/setbyid/<int:rid>/off",(Http.GET,Http.POST))
   @wrapResponse
   def setOffById(self, request, rid, *a, **kw):
      return self.callbackResponse(self.core.setRelayById(rid, 'off'), request)

   @route("/setbyid/<int:rid>/change",(Http.GET,Http.POST))
   @wrapResponse
   def setChangeById(self, request, rid, *a, **kw):
      return self.callbackResponse(self.core.setRelayById(rid, 'change'), request)





RESTv12LIST=(
   UserRest,
   CronRest,
   BoardRest,
   BaseRest,
   ActionRest,
   NotifyRest,
   RelayRest,
)


class RestV12Pages(rend.Page):

   def child_(self, ctx):
      request = inevow.IRequest(ctx)
      request.setHeader("pragma", "no-cache")
      request.postpath=['/']
      return RESTResource((BaseRest(self.core, self.session),))

   def childFactory(self, ctx, name):
      request = inevow.IRequest(ctx)
      request.setHeader("pragma", "no-cache")
      request.postpath=['/',name]+request.postpath
      return RESTResource([x(self.core, self.session) for x in RESTv12LIST])




##############################################################
# 
# Old and bad rest api. Those functions 
# and all below this comment is now deprecated
# and will be removed soon.
#

import json
import dmjson as dmj


def dbrelay(dbobj):
   res=[]
   for ret in dbobj:
      res.append(ret.toHash(['id','board_name','board_ip','outnum','outtype','ctx','act','msgtype','dynamic','relnum','domain','websection','button_name','active','position']))
   return res

def dbaction(dbobj):
   res=[]
   for ret in dbobj:
      res.append(ret.toHash(['id','rcv_dst','rcv_msgtype','rcv_ctx','rcv_act','use_rcv_arg','rcv_arg','execute','command','ikapacket','ikap_src','ikap_dst','ikap_msgtype','ikap_ctx','ikap_act','ikap_arg','launch_sequence','launch_sequence_name','websection','button_name','local_only','active','position','ipdest']))
   return res

def dbinput(dbobj):
   res=[]
   for ret in dbobj:
      res.append(ret.toHash(['id','board_name','board_ip','inpnum','dynamic','websection','button_name','active','position','inpname']))
   return res

def relstatus(dbobj, ts=True, res=[]):
   if ts:
      res.append({'command': 'updatets', 'data':ts})
   if len(dbobj)>0:
      dbret={'command': 'updaterelays', 'data':[]}
      for ret in dbobj:
         dbret['data'].append(ret.toHash(['id', 'buttonid', 'board_name','board_ip','outnum','ctx','outtype','relnum','status','lastupdate']))
      res.append(dbret)
   return res

def inputstatus(dbobj, ts=True, res=[]):
   if ts:
      res.append({'command': 'updatets', 'data':ts})
   if len(dbobj)>0:
      dbret={'command': 'updateinputs', 'data':[]}
      for ret in dbobj:
         dbret['data'].append(ret.toHash(['id', 'buttonid', 'board_name','board_ip','inpnum','status','lastupdate']))
      res.append(dbret)
   return res




class RestV10Pages(rend.Page):

   def child_(self, ctx):
      return permissionDenied()

   def childFactory(self, ctx, name):
      log.debug("No child found (%s)" % name)
      return permissionDenied()

   def child_keepAlive(self, ctx):
      return str(time.time())

   def child_relayStatus(self, ctx):
      ret=[]
      wts=0
      ts=int(time.time())-1
      request = inevow.IRequest(ctx)
      request.setHeader("pragma", "no-cache")
      log.debug(request)
      log.debug(request.args)
      self.manageCommands(request)
      wts=0
      try:
         if 'ts' in request.args and unicode(request.args['ts'][0]).isnumeric():
            wts=int(request.args['ts'][0])
      except:
         pass

      rs = self.core.getRelays(wts)
      return rs.addCallback(relstatus, ts, ret).addCallback(dmj.jsonize)


   def child_inputStatus(self, ctx):
      ret=[]
      wts=0
      ts=int(time.time())-1
      request = inevow.IRequest(ctx)
      request.setHeader("pragma", "no-cache")
      log.debug(request)
      log.debug(request.args)
      self.manageCommands(request)
      try:
         if 'ts' in request.args and unicode(request.args['ts'][0]).isnumeric():
            wts=int(request.args['ts'][0])
      except:
         pass

      ist=self.core.getInputs(wts)
      return ist.addCallback(inputstatus, ts, ret).addCallback(dmj.jsonize)


   def _getIOStatus(self, d, ts):
      rs = self.core.getRelays(ts)
      rs.addCallback(relstatus, False, d)
      return rs.addCallback(dmj.jsonize)


   def child_getIOStatus(self, ctx):
      #ret=[]
      ret=self.core.getActionStatus()
      wts=0
      ts=int(time.time())-1
      request = inevow.IRequest(ctx)
      request.setHeader("pragma", "no-cache")
      log.debug(request)
      log.debug(request.args)
      self.manageCommands(request)
      try:
         if 'ts' in request.args and unicode(request.args['ts'][0]).isnumeric():
            wts=int(request.args['ts'][0])
      except:
         pass
      
      ist=self.core.getInputs(wts)
      ist.addCallback(inputstatus, ts, ret).addCallback(self._getIOStatus, wts)
      return ist

   def manageCommands(self,req):
      if 'command' in req.args:
         for cmd in req.args['command']:
            self.core.sendAction(cmd)

   def child_asteriskAction(self, ctx):
      request = inevow.IRequest(ctx)
      try:
        self.core.asteriskAction(
                  request.args['ext'][0],
                  request.args['context'][0])
      except:
         return 'Error'

   def child_asteriskAliases(self, ctx):
      request = inevow.IRequest(ctx)
      try:
         return self.core.asteriskAliases(
                  request.args['ext'][0],
                  request.args['context'][0])
      except:
         return 'Error'


   def child_speechAction(self, ctx):
      request = inevow.IRequest(ctx)
      confidence = 1.0
      if 'confidence' in request.args.keys():
         confidence = float(request.args['confidence'][0])
      try:
         return self.core.voiceReceived(request.args['text'][0], confidence).addCallback(lambda res: res[0])
      except:
         return 'Error'

   def child_motionDetection(self, ctx):
      request = inevow.IRequest(ctx)
      try:
         self.core.father.motionDetection(
               int(request.args['type'][0]),
               int(request.args['status'][0]),
               request.args['camera'][0],
               request.args['zone'][0]
               )
         return 'OK'
      except:
         return 'KO'

   def child_uiCommands(self, ctx):
      request = inevow.IRequest(ctx)
      if 'command' in request.args:
         res=self.core.uiCommand(request.args['command'])
      return dmj.jsonize({'result': res})

   def child_configuringStatus(self, ctx):
      return dmj.jsonize({'result': self.core.configuringStatus()})


   def child_getRelayList(self, ctx):
      rs = self.core.getRelayList()
      inevow.IRequest(ctx).setHeader("pragma", "no-cache")
      return rs.addCallback(dbrelay).addCallback(dmj.jsonize)

   def child_getActionList(self, ctx):
      rs = self.core.getActionList()
      inevow.IRequest(ctx).setHeader("pragma", "no-cache")
      return rs.addCallback(dbaction).addCallback(dmj.jsonize)

   def child_getInputList(self, ctx):
      rs = self.core.getInputList()
      inevow.IRequest(ctx).setHeader("pragma", "no-cache")
      return rs.addCallback(dbinput).addCallback(dmj.jsonize)


