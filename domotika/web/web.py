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

from twisted.web import server, resource, static, client
from dmlib import dmcrypt
try:
   from twisted.web import http
except ImportError:
   from twisted.protocols import http

import random
import time
try:
   import hashlib
   md5 = hashlib
   md5.new = hashlib.md5
   sha1 = hashlib.sha1
except:
   import md5
   import sha1
import urllib
import logging
from dmlib.utils.blockingdefer import blockingDeferred
from dmlib.utils import genutils 
import cgi, logging
from zope.interface import implements
from twisted.cred import portal, checkers, credentials
from nevow import inevow, rend, tags, loaders, flat, stan, guard
from nevow import static as nstatic
import proxy, mediaproxy, rest
import os, sys
from twisted.python import reflect
from twisted import cred
import twisted.cred.portal
import twisted.cred.credentials
import twisted.cred.checkers
import twisted.cred.error
from twisted.internet import defer
from nevow import appserver
import time
import auth
from dmlib.utils.genutils import configFile
import phpserialize

log = logging.getLogger( 'Webgui' )

curdir=os.path.abspath(os.path.dirname(sys.argv[0]))
LOGINFILE=os.path.normpath("/".join([curdir, 'Web/resources/login.html']))

from common import uni, GzipRequest, StaticFile, codeOk, permissionDenied, RedirectToHome, PHPRunner, neededPermission
import ajax
import sse


WEB_SYSTEM_PATHS=[
   '/',
   '/__LOGOUT__/',
   '/__logout__/',
   '/__LOGOUT__',
   '/__logout__',
   '/__LOGIN__/',
   '/__login__/',
   '/__LOGIN__',
   '/__login__',
   '/favicon.ico',
]

server.version='DomotikaWeb/1.0'



class RootPage(rend.Page):


   addSlash = True
   logged = False
   childvars = {}
   isLeaf = False
   perms = False
   sse = False

   child_resources = StaticFile(curdir+'/Web/resources/')
   child_download = StaticFile(curdir+'/Web/download/')

   def __init__(self, avatarId=None, port=80):
      self.port = port
      log.debug("Root page initialized by " + str(avatarId))
      super(RootPage, self).__init__(self)
      self.avatarId=avatarId
      self.putChild('favicon.ico', static.File(curdir+'/Web/resources/img/favicon.ico'))
      self.putChild('crossdomain.xml', static.File(curdir+'/Web/resources/xml/crossdomain.xml'))

   def renderHTML(self, ctx):
      request = inevow.IRequest(ctx)
      return rend.Page.renderHTTP(self, ctx)

   def child_rest(self, ctx):
      if str(self.core.configGet('web', 'enablerestgui')).lower() in ['yes', '1', 'y','true']:
         self.rest = rest.RestPages()
         self.rest.core = self.core
         return self.rest
      return self.childFactory(ctx, 'rest')

   def child_sse(self, ctx):
      if str(self.core.configGet('web', 'enableajaxgui')).lower() in ['yes', '1', 'y','true']:
         session = inevow.ISession(ctx)
         if not 'sse' in dir(session) or session.sse == False:
            session.sse = sse.SseResource(self.core, session.mind.perms.username)
         return session.sse
      return self.childFactory(ctx, 'sse')

   def child_rawplugin(self, ctx):
      request = inevow.IRequest(ctx)
      pl=request.path.split("/")
      if len(pl)>2:
         pname=pl[2]
         pconf=os.path.normpath("/".join([curdir, 'plugins', pname, 'conf', pname+".conf" ]))
         log.debug("trying to read "+str(dconf))
         if os.path.isfile(dconf):
            try:
               pcfg=configFile(pconf)
               pcfg.readConfig()
               port=int(pcfg.get('web','port'))
            except:
               port=False
               log.debug("Cannot read config file for plugin "+pname)
            if port:
               self._sendProxySession(request, ctx)
               log.debug("Proxying to plugin path "+str(request.path))
               return proxy.WebProxyResource('localhost', port, path='/', remove=1)
         else:
            log.debug("Plugin hasn't a conf file to read")
      else:
         log.debug("no plugin name in request")
      return self.childFactory(ctx, 'rawplugin')

   def child_rawdaemon(self, ctx):
      request = inevow.IRequest(ctx)
      log.debug("Raw Daemon request for "+str(request.path))
      pl=request.path.split("/")
      if len(pl)>2:
         dname=pl[2]
         dconf=os.path.normpath("/".join([curdir, 'daemons', dname, 'conf', dname+".conf" ]))
         log.debug("trying to read "+str(dconf))
         if os.path.isfile(dconf):
            try:
               dcfg=configFile(dconf)
               dcfg.readConfig()
               port=int(dcfg.get('web','port'))
            except:
               port=False
               log.debug("Cannot read config file for daemon "+dname)
            if port:
               self._sendProxySession(request, ctx)
               log.debug("Proxying to daemon path "+str(request.path))
               return proxy.WebProxyResource('localhost', port, path='/', remove=1)
               
         else:
            log.debug("Daemon hasn't a conf file to read")
      else:
         log.debug("no daemon name in request")
      return self.childFactory(ctx, 'rawdaemon') 


   def child_mediaproxy(self, ctx):
      if str(self.core.configGet('web', 'enablemediagui')).lower() in ['yes', '1', 'y','true']:
         self.mediaproxy = mediaproxy.MediaStreamProxy()
         self.mediaproxy.core = self.core
         return self.mediaproxy
      return self.childFactory(ctx, 'mediaproxy')   

   def child_genproxy(self, ctx):
      return proxy.GenericProxy(self.core)

   def _addPermissions(self, ctx, name, session, request):
      def addPerms(dbres, ctx, name, session, request):
         try:
            log.info(dbres)
            if dbres and len(dbres)>0:
               session.dmpermissions[request.path]=dbres[0][0]
            if neededPermission(request.method) in session.dmpermissions[request.path]:
               log.info("PERMISSION DB OK, USER: "+session.mind.perms.username+" SESSION: "+str(session.uid)+" ARGS: "+str(request.args)+" REQ "+str(request))
               self.core.updateSession(session.uid, session, self)
               return rend.Page.locateChild(self, ctx, name)
         except:
            log.info("Error getting permission from DB USER: "+session.mind.perms.username+" SESSION: "+str(session.uid)+" ARGS: "+str(request.args)+" REQ "+str(request))
         log.info("PERMISSION DB DENIED, USER: "+session.mind.perms.username+" SESSION: "+str(session.uid)+" ARGS: "+str(request.args)+" REQ "+str(request))
         return permissionDenied(), ()
      if not 'sse' in dir(session):
         session.sse = False
      if not 'dmpermissions' in dir(session):
         session.dmpermissions={}
      if not request.path in session.dmpermissions.keys():
         session.dmpermissions[request.path] = 'none'
      return self.core.getPermissionForPath(session.mind.perms.username, request.path).addCallback(
         addPerms, ctx, name, session, request
      )

   def locateChild(self, ctx, name):
      session = inevow.ISession(ctx)
      request = inevow.IRequest(ctx)
      try:
         uname = session.mind.perms.username
      except:
         uname = 'guest'
      if not 'sse' in dir(session):
         session.sse = False
      if not 'dmpermissions' in dir(session):
         session.dmpermissions={}
      if request.path in WEB_SYSTEM_PATHS:
         log.info("WEB_SYSTEM_PATH: USER: "+uname+" SESSION: "+str(session.uid)+" ARGS: "+str(request.args)+" REQ "+str(request))
         return rend.Page.locateChild(self, ctx, name)
      if request.path in session.dmpermissions.keys():
         if neededPermission(request.method) in session.dmpermissions[request.path]:
            log.debug("PERMISSION OK, SESSION: "+str(session.uid)+" ARGS: "+str(request.args)+" REQ "+str(request))
            self.core.updateSession(session.uid, session, self)
            return rend.Page.locateChild(self, ctx, name)
      else:
         return self._addPermissions(ctx, name, session, request)
      log.debug("PERMISSION DENIED, SESSION: "+str(session.uid)+" ARGS: "+str(request.args)+" REQ "+str(request))
      #return rend.Page.locateChild(self, ctx, name)
      return permissionDenied(), ()
      


   def _sendProxySession(self, req, ctx):
      session = inevow.ISession(ctx)
      headers=req.requestHeaders
      if headers.hasHeader("DMSESSION"):
         headers.removeHeader("DMSESSION")
      headervalue = str(session.uid)
      cols=['username','passwd','id','homepath','email','tts','language','slide','webspeech','speechlang']
      try:
         headervalue = session.mind.perms.toHash(cols)
      except:
         headervalue={}
         headervalue['username'] = "guest"
         headervalue['passwd'] = ""
         headervalue['id'] = 0
         headervalue['homepath'] = '/'
         headervalue['email'] = ""
         headervalue['tts']= 0
         headervalue['language']="it"
         headervalue['slide'] = 0
         headervalue['webspeech'] = 'touch'
         headervalue['speechlang'] = 'it-IT'
      headervalue['sessionid'] = session.uid
      headervalue['logged'] = self.logged
      log.debug('DMSESSION SEND '+str(headervalue))
      headers.addRawHeader("DMSESSION", phpserialize.dumps(headervalue))
      return req

   def child_(self, ctx):
      if str(self.core.configGet('web', 'enableusergui')).lower() not in ['yes', '1', 'y','true']:
         return "Permission Denied"
      html = """
         Redirecting...
      """
      request = inevow.IRequest(ctx)
      host=request.getHeader('host')
      log.debug("HOST CALLED: "+str(host))
      #log.info("Request: "+str(request))
      if host and host in self.core.configGet('proxy', 'localproxyhosts').split(','):
         self._sendProxySession(request, ctx)
         return proxy.WebProxyResource('localhost', int(self.core.configGet('proxy', 'localproxyport')), path='/')
      else:
         if self.logged:
            if(len(self.perms.homepath)) > 0:
               request.setHeader('Location', self.perms.homepath);
            else:
               request.setHeader('Location', self.core.configGet('web', 'defaultpath'))
         else:
            request.setHeader('Location', self.core.configGet('web', 'defaultpath'))
         request.setResponseCode(302)
         return html

   def childFactory(self, ctx, name):
      #log.info("childFactory "+str(name))
      request = inevow.IRequest(ctx)
      #log.info("childFactory2 "+str(request))
      if name in self.core.configGet('proxy', 'localproxypaths').split(','):
         self._sendProxySession(request, ctx)
         return proxy.WebProxyResource('localhost', 80, path='/'+name)
      host=request.getHeader('host')
      log.debug("HOST CALLED: "+str(host))
      if host and host in self.core.configGet('proxy', 'localproxyhosts').split(','):
         self._sendProxySession(request, ctx)
         return proxy.WebProxyResource('localhost', 80, path='/'+name)
      log.debug("No child found (%s)" % name)
      return permissionDenied()




### Authentication
class SessionWrapper(guard.SessionWrapper):

   def renderHTTP( self, ctx):
      request = inevow.IRequest(ctx)
      host=request.getHeader('host')
      log.info("USERNAME: "+str(request.getUser())+" "+str(request.getPassword()))
      log.debug("SessionWrapper HOST CALLED: "+str(host))
      if host and host in self.core.configGet('proxy', 'localproxyhostsnologin').split(','):
         log.debug("Proxy Bypass Host in SessionWrapper renderHTTP "+host)
         return proxy.WebProxyResource('localhost', int(self.core.configGet('proxy', 'localproxyport')), path='/')
      return guard.SessionWrapper.renderHTTP(self, ctx)


   def locateChild(self, ctx, segments):
      request = inevow.IRequest(ctx)
      name = "/".join(segments)
      if name=='':
         name="/"
      log.debug("SessionWrapper locateChild "+str(name)+" from IP:"+str(request.getClientIP()))
      if name: 
         if name.startswith('mediaproxy') and request.getClientIP()=='127.0.0.1':
            mp = mediaproxy.MediaStreamProxy()
            mp.core = self.core
            return (mp, segments[1:]) 
         for n in self.core.configGet('proxy', 'localproxypathsnologin').split(','):
            if n and name.startswith(n):
               log.info("Proxy Bypass localproxypathsnologin locateChild "+name)
               return (proxy.WebProxyResource('localhost', 80, path='/'+name), '')
         for n in self.core.configGet('web', 'nologinpaths').split(','):
            if n and name.startswith(n):
               if not ((name==n and n.endswith("/")) or (name[:-1]==n and name.endswith("/"))):
                  log.debug("Nologin path "+str(name))
                  return (StaticFile(curdir+'/Web/'+name), '')
      host=request.getHeader('host')
      log.debug("SessionWrapper HOST CALLED: "+str(host))
      for n in self.core.configGet('proxy', 'localproxyhostsnologin').split(','):
         if n and host==n:
            log.info("Proxy Bypass Host in SessionWrapper locateChild "+host)
            return (proxy.WebProxyResource('localhost', 80, path='/'+name), '')
      u = self.core.configGet('web', 'nologindefaultuser')
      p = self.core.configGet('web', 'nologindefaultpass')
      for n in self.core.configGet('web', 'nologinips').split(','):
         if ':' in n:
            nn = n.split(':')
            n = nn[0]
            if len(nn) > 1:
               u = nn[1]
            if len(nn) > 2:
               p = nn[2]
         if n and n!='no' and n!='':
            if genutils.isIp(n):
               if n==request.getClientIP():
                  log.info("IP "+str(request.getClientIP())+" permitted with user "+str(u)+" checking auth...")
                  request.args["username"] = [u]
                  request.args["password"] = [p]
                  request.getUser = lambda: u
                  request.getPassword = lambda: p
                  break

      if request.getUser() and request.getPassword():
         log.info("BASIC AUTH REQUESTED FOR USER "+str(request.getUser()))
         request.args["username"] = [request.getUser()]
         request.args["password"] = [request.getPassword()]

      log.debug("Calling Guard..."+str(request.args))
      return guard.SessionWrapper.locateChild(self, ctx, segments)
      

def noLogout():
   return None


class LogoutPage(rend.Page):

   addSlash = True

   def __init__(self, locpath):
      self.locpath=locpath.replace("/__LOGOUT__/","/__logout__/")

   def renderHTTP(self, ctx):
      request = inevow.IRequest(ctx)
      rmec=request.getCookie("Domotikad_rme")
      # XXX Come si fa a capire SE esiste? ritorna davvero None?
      if rmec:
         request.addCookie("Domotikad_rme", str(rmec), path="/", secure=True,
            expires=http.datetimeToString(time.time()))
      request.setHeader('Location', self.locpath)
      request.setResponseCode(302)
      log.debug("SPECIAL LOGOUT "+self.locpath)
      return 'Logging out...'

   def childFactory(self, ctx, data):
      return self



class RootAuthPage(RootPage):

   def __init__(self, avatarId=None, port=80, mind=None):
      RootPage.__init__(self, avatarId, port)
      self.logged=True
      self.mind = mind
      self.perms = avatarId[1]

   def logout(self):
      log.debug("LOGOUT CALLED")
      self.logged=False


   def locateChild(self, ctx, name):
      request = inevow.IRequest(ctx)
      if not self.mind.loginsaved:
         log.debug("LocateChild in RootAuthPage Ming Args: "+str(self.mind.args))
         self.mind.loginsaved = True
         self.mind.perms = self.perms
         if 'rememberMe' in self.mind.args:
            log.debug("Setting rememberMe cookie for avatar "+str(self.avatarId))
            #session = inevow.ISession(ctx)
            rme=dmcrypt.B64AESEncrypt(str(self.core.configGet('web', 'cookie_aeskey')), self.perms.passwd, 
                                       " ".join([self.perms.username, self.perms.loginpwd, self.perms.passwd]))
            try:
               expire=http.datetimeToString(time.time() + 3600*24*365*50)
            except:
               expire=http.datetimeToString(time.time() + 3600*24*365*10)

            request.addCookie("Domotikad_rme", str(self.perms.id)+':'+rme, 
               path="/", secure=True, expires=expire)
      return RootPage.locateChild(self, ctx, name)


   def childFactory(self, ctx, name):
      log.debug("RootAuth childFactory")
      request = inevow.IRequest(ctx)
      if request.path.startswith("/__LOGOUT__/"):
         log.debug("__LOGOUT__ CALLED")
         return LogoutPage(request.path)
      return RootPage.childFactory(self, ctx, name)



class LoginPage(rend.Page):

   addSlash = True

   html="""<html><head>
<title>Domotika By Unixmedia</title>
@SCRIPT@
</head>
<form method="post" name="loginform" action="@PATH@">
<fieldset id="form"><legend>Login</legend>
<p>Username: <input type="text" name="username" size="20" value="@USERNAME@" /></p>
<p>Password: <input type="password" name="password" size="20" value="@PASSWORD@" /></p>
<p>Remember me: <input type="checkbox" name="rememberMe" value="Yes" @CHECKED@ /></p>
<p align="center"><input type="submit" value="Login" /></p>
</fieldset>
</form>
</body></html>
   """

   child_img = StaticFile(curdir+'/Web/resources/img/')

   def __init__(self, *a, **kw):
      self.putChild('favicon.ico', static.File(curdir+'/Web/resources/img/favicon.ico'))
      if os.path.isfile(LOGINFILE):
         try:
            lf = open(LOGINFILE, "r")
            self.html = lf.read()
            lf.close()
         except:
            pass

      rend.Page.__init__(self, *a, **kw)

   def renderHTTP( self, ctx):
      rme=False

      request = inevow.IRequest(ctx)
      host=request.getHeader('host')
      log.debug("LOGIN HOST CALLED: "+str(host))
      cookies=request.getHeader('cookie')
      if cookies:
         cookies=cookies.replace(" ","").split(';')
         for cookie in cookies:
            cookiename = cookie.split("=")[0]
            if cookiename.startswith('Domotikad_session'):
               log.debug("REMOVE COOKIE: "+str(request.getCookie(cookie.split("=")[0])))
               # XXX This won't work as expected if user is logging in with path != from "/"
               # Also, is cookie secure even for http requests?
               request.addCookie(cookiename, cookie.split("=")[1],  expires=http.datetimeToString(time.time()), path="/", secure=True)
            elif cookiename.startswith('Domotikad_rme'):
               rmec=str(request.getCookie("Domotikad_rme"))
               log.debug("RememberMe COOKIE FOUND: "+rmec)
               rmecl = rmec.split(':')
               try:
                  if len(rmecl) > 1:
                     uid = str(int(rmecl[0]))
                     rme = self.core.getUserFromID(uid)
                  #request.setHeader('Location', '/'+self.resolution+'/home')
                  #request.setResponseCode(302)
               except:
                  pass

         
      if request.path.startswith("/rest/") and '/keepalive' in request.path:
         request.setHeader('content-type', 'application/json')
         return '{"data": "SLOGGEDOUT", "uri": "'+request.path+'", "ts": '+str(time.time())+', "result": "succeed"}'

      if not rme:
         log.info("LOGIN FORM FOR PATH "+request.path)
         return self.getStandardHTML(request.path)
      else:
         log.debug("LOGIN FROM COOKIE FOR PATH "+request.path)
         return rme.addCallback(self.rmelogin, request, rmec)


   def getStandardHTML(self, path):
      html = self.html.replace("@PATH@", '/__login__'+path)
      html = html.replace("@USERNAME@", '')
      html = html.replace("@PASSWORD@", '')
      html = html.replace("@SCRIPT@", "")
      html = html.replace("@CHECKED@", "")
      return html

   def getScript(self, path):
      return '<script> window.onload=function(){ document.loginform.submit(); };</script>'

   def rmelogin(self, res, req, has):
      if res and (('__len__' in dir(res) and len(res) > 0) or res!=None ) and len(has.split(":", 1)) > 1:
         if '__len__' in dir(res):
            user=res[0]
         else:
            user=res

         rme=dmcrypt.B64AESDecrypt(str(self.core.configGet('web', 'cookie_aeskey')), user.passwd, has.split(":", 1)[1])
         if len(rme.split()) == 3:
            u, lp, p = rme.split()
            if user.username == u and user.passwd == p:
               log.debug("Cookie login succeed for user "+user.username)
               try:
                  expire=http.datetimeToString(time.time() + 3600*24*365*50)
               except:
                  expire=http.datetimeToString(time.time() + 3600*24*365*10)

               req.addCookie("Domotikad_rme", has,
                  path="/", secure=True, expires=expire)

               html = self.html.replace("@PATH@", '/__login__'+req.path)
               html = html.replace("@USERNAME@", str(user.username))
               html = html.replace("@PASSWORD@", str(lp))
               html = html.replace("@CHECKED@", "checked")
               html = html.replace("@SCRIPT@", str(self.getScript(req.path)))
               log.debug("login html")
               return html

      req.addCookie("Domotikad_rme", has, path="/", secure=True, expires=http.datetimeToString(time.time()))
      return self.getStandardHTML(req.path)

   def childFactory(self, ctx, name):
      return self


class DomotikaAuthRealm(object):
   """A simple implementor of cred's IRealm.
      For web, this gives us the LoggedIn page.
   """
   implements(portal.IRealm)

   def __init__(self, port):
      self.port = port

   def requestAvatar(self, authres, mind, *interfaces):
      avatarId = authres

      log.debug("Avatar is: "+str(avatarId)+' and mind + interfaces '+str(mind)+' '+str(interfaces))
      for iface in interfaces:
         if iface is inevow.IResource:
            # do web stuff
            if avatarId is checkers.ANONYMOUS:
               resc = LoginPage()
               resc.realm = self
               resc.core = self.core
               return (inevow.IResource, resc, noLogout)
            else:
               # Qui dovrebbe arrivare in caso di autenticazione
               # avatarId dovrebbe contenere il ritorno al checkauth
               resc = RootAuthPage(avatarId, self.port, mind)
               resc.realm = self
               resc.core = self.core
               if str(self.core.configGet('web', 'enableajaxgui')).lower() in ['yes', '1', 'y','true']:
                  resc.putChild('autobahn', ajax.getAutoBahn(self.core, resc.port))
                  resc.putChild('sockjs', ajax.getSocketJSResource(self.core))
               return (inevow.IResource, resc, resc.logout)
      raise NotImplementedError("Can't support that interface.")


def getAuthResource(core):
   realm = DomotikaAuthRealm(core.configGet('web', 'sslport'))
   realm.core = core
   porta = portal.Portal(realm)
   mycheck=auth.clientAuth()
   mycheck.core = core
   porta.registerChecker(checkers.AllowAnonymousAccess(), credentials.IAnonymous)
   porta.registerChecker(mycheck)
   site = SessionWrapper(porta, 'Domotikad_session', mindFactory=auth.mindFactory)
   site.core = core
   return site

