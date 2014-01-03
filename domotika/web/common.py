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

import struct
import zlib
from twisted.web import http, server, resource, static, client
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
import logging
from dmlib.utils.blockingdefer import blockingDeferred
import cgi, logging
from zope.interface import implements
from twisted.cred import portal, checkers, credentials
import cgi, logging
from nevow import inevow, rend, tags, loaders, flat, athena, stan, guard
import os, sys
from twisted.python import reflect
from twisted import cred
import twisted.cred.portal
import twisted.cred.credentials
import twisted.cred.checkers
import twisted.cred.error
from twisted.internet import defer
from nevow import appserver
from twisted.web.twcgi import CGIScript, FilteredScript



log = logging.getLogger( 'Webgui' )
curdir=os.path.abspath(os.path.dirname(sys.argv[0]))


class GzipRequest(object):
    """Wrapper for a request that applies a gzip content encoding"""

    def __init__(self, request, compressLevel=6):
        self.request = request
        self.request.setHeader('Content-Encoding', 'gzip')
        # Borrowed from twisted.web2 gzip filter
        self.compress = zlib.compressobj(compressLevel, zlib.DEFLATED,
                                         -zlib.MAX_WBITS, zlib.DEF_MEM_LEVEL,0)
      
    def __getattr__(self, attr):
        if 'request' in self.__dict__:
            return getattr(self.request, attr)
        else:
            raise AttributeError, attr

    def __setattr__(self, attr, value):
        if 'request' in self.__dict__:
            return setattr(self.request, attr, value)
        else:
            self.__dict__[attr] = value

    def write(self, data):
        if not self.request.startedWriting:
            self.crc = zlib.crc32('')
            self.size = self.csize = 0
            # XXX: Zap any length for now since we don't know final size
            if 'content-length' in self.request.headers:
                del self.request.headers['content-length']
            # Borrow header information from twisted.web2 gzip filter
            self.request.write('\037\213\010\000' '\0\0\0\0' '\002\377')
        self.crc = zlib.crc32(data, self.crc)
        self.size += len(data)
        cdata = self.compress.compress(data)
        self.csize += len(cdata)
        if cdata:
            self.request.write(cdata)
        elif self.request.producer:
            # Simulate another pull even though it hasn't really made it
            # out to the consumer yet.
            self.request.producer.resumeProducing()

    def finish(self):
        remain = self.compress.flush()
        self.csize += len(remain)
        if remain:
            self.request.write(remain)
        self.request.write(struct.pack('<LL',
                                       self.crc & 0xFFFFFFFFL,
                                       self.size & 0xFFFFFFFFL))
        self.request.finish()


class StaticFile(static.File):

   def render(self, request):
      # Some flash file ( flowplayer.. ) needs
      # to be server without gzip compression or
      # they will not work sometime...
      if self.basename().endswith('.swf'):
         return static.File.render(self, request)
      accept_encoding = request.getHeader('accept-encoding')
      if accept_encoding:
         encodings = accept_encoding.split(',')
         for encoding in encodings:
            name = encoding.split(';')[0].strip()
            if name == 'gzip':
               request = GzipRequest(request)
               break
      return static.File.render(self, request)

class codeOk(rend.Page):

   addSlash = True
   content = 'OK'

   def renderHTTP( self, ctx):
      request = inevow.IRequest(ctx)
      #request.setHeader('Location', '/')
      request.setResponseCode(200)
      return self.content

   def setContent(self, cont):
      self.content = str(cont)

   def childFactory(self, ctx, data):
      return self


class permissionDenied(rend.Page):

   addSlash = True

   def renderHTTP( self, ctx):
      log.debug("Rendering Permission Denied")
      request = inevow.IRequest(ctx)
      #request.setHeader('Location', '/')
      #request.setResponseCode(302)
      request.setResponseCode(403)
      html = '<html><head><title>Domotika GUI</title></head>'
      html = html+"<h3>I'm so sorry!</h3>"
      html = html+"<p>you can't do that.</p>"
      html = html+"<p><a href=\"/\">Go Home</a></p>"
      html = html+'</body></html>'
      return html

   def childFactory(self, ctx, data):
      return self

class RedirectToHome(rend.Page):

   addSlash = True

   def renderHTTP( self, ctx):
      request = inevow.IRequest(ctx)
      request.setHeader('Location', '/')
      request.setResponseCode(302)
      return 'Redirecting...'


   def childFactory(self, ctx, data):
      return self


class PHPRunner(FilteredScript):
   filter = "/usr/bin/php5-cgi"
      
   def runProcess(self, env, *a, **kw):
      env['REDIRECT_STATUS'] = '200'
      env['SCRIPT_NAME']=env['SCRIPT_FILENAME'].replace(curdir+'/Web/resources', '')
      env['PATH_INFO']=''
      env['HTTPS']='on'
      env['HTTPS_SCHEME']='https'
      return FilteredScript.runProcess(self, env, *a, **kw)



def uni(s):
   if isinstance(s, str):
      #return s.decode('utf-8', "replace")
      return s.decode('latin-1', "replace")
   elif isinstance(s, unicode):
      #return s.encode('utf-8', "replace")
      return s.encode('latin-1', "replace")
   else:
      return s



      
class Caller(object):

   def __init__(self, skobj):
      self.domotika = skobj
      self.missing_method_name = None # Hack!
      
   def __getattribute__(self, name):
      sk = object.__getattribute__(self, 'domotika')
      try: 
         return object.__getattribute__(sk, name)
      except:
         self.missing_method_name = name
         log.debug("Missing  Method: "+str(name))
         return object.__getattribute__(self, '__methodmissing__')
         
   def __methodmissing__(self, *args, **kwargs):
      log.debug("Missing Client method %s called (args = %s) and (kwargs = %s)" % (object.__getattribute__(self, 'missing_method_name'), str(args), str(kwargs)))


def neededPermission(method):
   if method in ['GET','OPTIONS','HEAD','REPORT','CHECKOUT','SEARCH']:
      return 'r'
   else:
      return 'w'

