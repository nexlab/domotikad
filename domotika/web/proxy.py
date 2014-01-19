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

from twisted.internet import reactor, protocol, ssl
from twisted.web import http, server
from twisted.web.proxy import Proxy, ProxyRequest, ReverseProxyRequest 
from twisted.web.proxy import ReverseProxyResource, ProxyClientFactory, ProxyClient
from nevow import inevow, rend, tags, loaders, flat, athena, stan, guard
from twisted.web import resource, static
from common import permissionDenied
from twisted.web.server import NOT_DONE_YET
from domotika.db import dmdb as dmdb
from dmlib.utils import webutils as wu
import urllib
from urlparse import urlsplit, urlparse
from urllib import quote as urlquote

import logging

log = logging.getLogger( 'Proxy' )

class WebProxyClient(ProxyClient):
   def handleHeader(self, key, value):
      if key.lower() == 'location':
         log.debug("Manage location header")
         uri=urlparse(value)
         value=uri.path
         if len(uri.query) > 0:
            value=value+"?"+uri.query
      #    value = self.proxymap.absoluteURLOf(value, self.host_header())
      log.debug("HANDLE HEADER: "+str(key)+" "+str(value))
      return ProxyClient.handleHeader(self, key, value)

   def handleStatus(self, version, code, message):
      log.debug("HANDLE STATUS: "+str(version)+" "+str(code)+" "+str(message))
      """
      if int(code)==304:
         log.debug("304 detected")
         self.father.transport.write(str(code)+" "+str(message)+" "+str(version))
         self.handleResponseEnd()
         self.father.transport.loseConnection()
         return
      else:
         return ProxyClient.handleStatus(self, version, code, message)
      """
      return ProxyClient.handleStatus(self, version, code, message)

   def host_header(self):
      host = self.father.getHeader("host")
      log.debug("HOST_CLIENT: "+str(host))       
      assert host is not None  # XXX there are other alternatives...
      return host

   def __init__(self, command, rest, version, headers, data, father, resource):
      father.notifyFinish().addErrback(self._clientfinished, father, resource)
      if "proxy-connection" in headers:
         del headers["proxy-connection"]
      headers["connection"] = "close"
      headers.pop('keep-alive', None)
      self.headers = headers
      log.debug("Proxy Client SEND headers: "+str(headers))
      ProxyClient.__init__(self,
                          command=command,
                          rest=rest,
                          version=version,
                          headers=headers,
                          data=data,
                          father=father)

   def _clientfinished(self, res, req, resource):
      log.debug("ApacheRequest finished!")
      self.handleResponseEnd()
      resource.reactor.disconnect()


class WebProxyClientFactory(ProxyClientFactory):
   def __init__(self, command, rest, version, headers, data, father, resource):
      self.resource = resource
      ProxyClientFactory.__init__(self,
                                  command=command,
                                  rest=rest,
                                  version=version,
                                  headers=headers,
                                  data=data,
                                  father=father)

   def buildProtocol(self, addr):
      return WebProxyClient(command=self.command,
                               rest=self.rest,
                               version=self.version,
                               headers=self.headers,
                               data=self.data,
                               father=self.father,
                               resource=self.resource)

def hostport(host, port, headerhost, defaultport=80):
   if headerhost:
      host=headerhost
   if port == defaultport: return host
   return '%s:%d' % (host, port)


class WebProxyResource(ReverseProxyResource):
   """ Just to permit future modifications """
   clientFactory = WebProxyClientFactory
   remove = False

   def __init__(self, *arg, **kwarg):
      log.debug("WebProxy called")
      try:
         if 'remove' in kwarg.keys():
            self.remove=int(kwarg['remove'])
            del kwarg['remove']
      except:
         log.debug("error in remove")
      return ReverseProxyResource.__init__(self, *arg, **kwarg)


   def getChild(self, path, request):
      #log.debug("APACHE PROXY SEND HEADERS "+str(request.requestHeaders))
      #return ReverseProxyResource.getChild(self, path, request)
      return WebProxyResource(self.host, self.port, self.path+'/'+urlquote(path, safe=""), remove=self.remove)


   def render(self, request):
      # XXX too bad we had to copy and paste all this code due to
      # its poor factoring!

      # Copy 'headers' rather than modify it in place --- we may
      # need that 'Host:' header to correctly rewrite redirects
      # later on.
      headers = request.getAllHeaders().copy()
      headerhost=request.getHeader('host')
      headers['host'] = hostport(self.host, self.port, headerhost)
     
      log.debug("APACHE PROXY / SEND HEADERS "+str(request.requestHeaders))

      try:
         request.content.seek(0, 0)
         reqdata=request.content.read()
      except:
         log.debug("APACHE PROXY FD NOT OPEN (YET)")
         log.debug(request)
         reqdata=""


      qs = urlparse(request.uri)[4]
      if qs:
         rest = self.path + '?' + qs
      else:
         rest = self.path
      if rest.startswith("//"):
         rest=rest[1:]
 
      if self.remove:

         tmprest="/".join([x for x in rest.split("/") if x != ''][self.remove:])
         if rest.endswith('/'):
            tmprest+="/"
         rest="/"+tmprest
     
      log.debug("Proxying requesto to "+str(rest))
      clientFactory = self.clientFactory(command=request.method,
                                         rest=rest,
                                         version=request.clientproto,
                                         headers=headers,
                                         data=reqdata,
                                         father=request,
                                         resource=self)
      self.reactor = reactor.connectTCP(self.host, self.port, clientFactory)
      return server.NOT_DONE_YET


class DomikaProxyRequest(ProxyRequest):
   def process(self):
      log.debug("REQUEST: "+str(self.uri))
      if "www.unixmedia.it" not in self.uri:
         self.transport.write("HTTP/1.0 301 Moved\r\n")
         self.transport.write("Content-Type: text/html\r\n")
         self.transport.write("Location: http://www.unixmedia.it/\r\n")
         self.transport.write("\r\n")
         self.transport.write('''<H1>Redirecting to domotika...</H1>\r\n''')
         self.transport.loseConnection()
      else:
         ProxyRequest.process(self)
 
class DomikaProxy(Proxy):
    requestFactory = DomikaProxyRequest
 
DomProxy = http.HTTPFactory()
DomProxy.protocol = DomikaProxy


class GenericProxyClient(object):
   
   def __init__(self, uri, method, req):
      self.method = method
      self.uri = uri
      self.req = req
      wu.getPage(uri).addCallbacks(self.onOk, self.onError)

   def onOk(self, res):
      self.req.write(res)
      log.info("GENERIC PROXY OK ")
      self.req.finish()

   def onError(self, res):
      self.req.write(res)   
      log.info("GENERIC PROXY ERROR "+str(res))
      self.req.finish()

class GenericProxyClientFactory(ProxyClientFactory):

   protocol = GenericProxyClient
   proto = False

   def __init__(self, uri, method):
      self.uri = uri
      self.method = method

   def buildProtocol(self, req):
      if not self.proto:
         self.proto = self.protocol(self.uri, self.method, req)
      return self.proto

   def stop(self, req):
      log.info("GENERIC PROXY STOP CALLED FOR "+str(self.uri))
      if self.proto:
         self.proto.disconnect()


class GenericProxyResource(ReverseProxyResource):

   """ Just to permit future modifications """
   clientFactory = GenericProxyClientFactory

   def __init__(self, uri, method):
      self.uri = uri
      self.method = method

   def getChild(self, path, request):
      return self

   def _responseFailed(self, res, req, cfact):
      log.debug("GENERIC PROXY ResponseFailed "+str(res)+" "+str(req)+" "+str(cfact))

   def connectionLost(self, reason):
      log.debug("GENERIC PROXY ConnectionLost "+str(reason))

   def render(self, request):
      request.received_headers['uri']=self.uri
      request.setHeader("pragma", "no-cache")
      try:
         request.content.seek(0,0)
      except:
         log.debug("GENERIC PROXY FD CLOSED (YET)")
      prod = self.clientFactory(self.uri, self.method)
      prod.buildProtocol(request)
      request.notifyFinish().addErrback(self._responseFailed, request, prod)
      return NOT_DONE_YET



class GenericProxy(rend.Page):

   addSlash = True

   def __init__(self, core):
      self.core = core
      super(GenericProxy, self).__init__(self)

   def childFactory(self, ctx, name):
      return permissionDenied()

   def child_(self, ctx):
      request = inevow.IRequest(ctx)

      log.debug("COPY")
      if 'uri' in request.args:
         uri = urllib.unquote(request.args['uri'][0])
         return GenericProxyResource(uri, request.method)
      return permissionDenied()

