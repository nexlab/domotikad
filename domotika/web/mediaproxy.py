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

from twisted.internet import reactor, protocol, ssl, defer
from twisted.web import http, server
from twisted.web.proxy import Proxy, ProxyRequest, ReverseProxyRequest 
from twisted.web.proxy import ReverseProxyResource, ProxyClientFactory, ProxyClient
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.conch.telnet import TelnetTransport, StatefulTelnetProtocol
from nevow import inevow, rend, tags, loaders, flat, athena, stan, guard
from twisted.web import resource, static
from common import permissionDenied
from twisted.web.server import NOT_DONE_YET
from dmlib.utils import webutils as wu
import urllib
from urlparse import urlsplit, urlparse
from urllib import quote as urlquote
import logging
from domotika.singleton import mediaclients as mclients
from domotika.singleton import mediaproducers as producers
import re
import multiprocessing

try:
   import hashlib
   md5 = hashlib
   md5.new = hashlib.md5
   sha1 = hashlib.sha1
except:
   import md5
   import sha1


log = logging.getLogger( 'Media' )


CPUNUM=multiprocessing.cpu_count()

CONTENT_TYPES = {
                  'm4v': 'video/x-m4v',
                  'flv': 'video/x-flv',
                  'ogv': 'video/ogg',
                  'webm': 'video/webm',
                  'h264': 'video/mp4',
                  'mpegts': 'video/x-mpeg2-ts'              
                }


VIDEO_RESOLUTIONS=[
   '160x120',
   '240x160',
   '320x240',
   '400x240',
   '640x480',
   '800x480',
   '854x480',
   '800x600',
   '960x640',
   '1024x600',
   '1024x768',
   '1280x768',
   '1920x1080'
   'sameres'  
]  

#duplicate{dst='transcode{vcodec=h264,vb=2000,vbv-maxrate=2500,vbv-bufsize=1350,fps=25,scale=0,width=1280,height=720,soverlay,sfilter=marq}:http{mux=ps,dst=:7080}',dst='transcode{vcodec=h264,vb=3000,vbv-maxrate=3500,vbv-bufsize=1600,fps=25,scale=0,width=1280,height=720,soverlay,sfilter=marq}:http{mux=ps,dst=:1234}'}

SOUTLINE='#duplicate{'
SOUTLINE+="dst='transcode{vcodec=h264,vb=100,scale=0,acodec=mpga,ab=96}:standard{access=http,mux=ts{use-key-frames},dst=:7080/[NAME]_h264_low}',"
#SOUTLINE+="dst='transcode{vcodec=VP80,vb=2000,width=800,acodec=vorb,ab=128,channels=2,samplerate=44100}:standard{access=http,mux=ffmpeg{mux=webm},dst=:7080/[NAME]}_webm_low',"
SOUTLINE+="dst='transcode{vcodec=h264,vb=8000,scale=0,acodec=mpga,ab=96}:standard{access=http,mux=ts{use-key-frames},dst=:7080/[NAME]_h264}'"#,"
#SOUTLINE+="dst='transcode{vcodec=VP80,vb=2000,width=800,acodec=vorb,ab=128,channels=2,samplerate=44100}:standard{access=http,mux=ffmpeg{mux=webm},dst=:7080/[NAME]_webm}'"
SOUTLINE+='}'


FFMPEG_ANDROID="""-b 384k 
-vcodec libx264 
-flags +loop+mv4 
-cmp 256 
-partitions +parti4x4+parti8x8+partp4x4+partp8x8 
-subq 6 
-trellis 0 
-refs 5 
-bf 0 
-coder 0 
-me_range 16 
-g 250 
-keyint_min 25 
-sc_threshold 40 
-i_qfactor 0.71 
-qmin 10 -qmax 51 
-qdiff 4 
-acodec libfaac 
-ac 1 
-ar 16000 
-r 13 
-ab 32000 
-aspect 3:2 """

#FFMPEG_HTML5_HLS="""ffmpeg -v verbose -f video4linux2 -vcodec mjpeg -s 640x480 -r 5 -i /dev/video0 -c:v libx264 -crf 18 -profile:v baseline -maxrate 400k -bufsize 1835k -pix_fmt yuv420p -flags -global_header -hls_time 10 -hls_list_size 6 -hls_wrap 10 -start_number 1 /var/www/live/mystream.m3u8"""

FFMPEG_HTML5_H264=""" -c:v libx264 -b:v 200K -vprofile baseline
-preset medium -x264opts level=41 -threads 4 -map 0:v
-map 0:a:0  -c:a libfaac -b:a 16000 -ac 2   -hls_time 10
-hls_list_size 6 -hls_wrap 18 -start_number 1 -f mp4"""

FFMPEG_HTML5_WEBM=" -cpu-used "+str(CPUNUM)+" -threads "+str(CPUNUM*2)+" -b:v 1500k -vcodec libvpx -acodec libvorbis -g 30 -f webm -s 640x480"

FFMPEG_MPEGTS=" -f mpegts"

FFMPEGCMD={
   'h264': FFMPEG_HTML5_H264,
   'webm': FFMPEG_HTML5_WEBM,
   'mpegts': FFMPEG_MPEGTS
}

class TelnetConnectionError(Exception):
    pass

class VLCClient(StatefulTelnetProtocol):
   output_buffer = []
   search_output = []

   def rawDataReceived(self,bytes):
      """The login and password prompt on some systems are not
      received in lineMode. Therefore we do the authentication in 
      raw mode and switch back to line mode when we decect the 
      shell prompt.

      TODO: Need to handle authentication failure
      """
      if self.factory.prompt.strip() == '$':
         self.re_prompt = re.compile('\$')
      else:
         self.re_prompt = re.compile(self.factory.prompt)

      log.debug('Received raw telnet data: %s' % repr(bytes))
      if re.search('([Ll]ogin:\s+$)', bytes):
         self.sendLine(self.factory.username)
      elif re.search('([Pp]assword:\s+$)', bytes):
         self.sendLine(str(self.factory.password))
      elif self.re_prompt.search(bytes) or re.search(self.factory.greeting, bytes):
         # Set our client 
         p=producers.VLCTelnet()
         p.setClient(self)

         log.info('VLC telnet client logged in. We are ready for commands')
         self.setLineMode()

   def connectionMade(self):
      """ Set rawMode since we do not receive the 
      login and password prompt in line mode. We return to default
      line mode when we detect the prompt in the received data stream
      """
      self.setRawMode()

   def lineReceived(self, line):
      log.debug('VLC Received telnet line: %s' % repr(line))
      if len(self.search_output) == 0:
         self.output_buffer.append(line)
         return

      re_expected = self.search_output[0][0]
      search_deferred = self.search_output[0][1]
      if not search_deferred.called:
         match = re_expected.search(line)
         if match:
            data = '\n'.join(self.output_buffer)
            data += '\n%s' % line[:match.end()]
            self.search_output.pop(0)
            # Start the timeout of the next epect message
            if len(self.search_output) > 0:
               re_expected = self.search_output[0][0]
               search_deferred = self.search_output[0][1]
               timeout = self.search_output[0][3]
               self.search_output[0][2] = self.getTimeoutDefer(timeout,
                                   search_deferred, re_expected)
            search_deferred.callback(data)
            log.debug('VLC clear telnet buffer in lineReceived. We have a match: %s' % line)
            self.clearBuffer()
            return

      self.output_buffer.append(line)

   def clearBuffer(self,to_line=-1):
      self.clearLineBuffer()
      if to_line == -1:
         self.output_buffer = []
      else:
         self.output_buffer = self.output_buffer[to_line:]

   def getTimeoutDefer(self,timeout,expect_deferred,re_expected):
      """ Create the cancel expect messages deffer that we use to 
      to timeout the expect deffer.
      """
      def expectTimedOut(expect_deferred):
         result = ''
         # we only test the buffer against the oldest wait. Therfore
         # do not clear the buffer if a older exoect still waits for
         # a messages. This should probaly rause an exceotion or somethine...

         if expect_deferred.called:
            log.error('VLC Expected message deferrer "%s" is already called. ' % expect_deferred)
            log.error('VLC This is a sign that something is wrong with the telnet client')
            return

         if self.search_output[0][1] == expect_deferred:
            # set the result since this is the current search
            result = '\n'.join(self.output_buffer)
            self.clearBuffer()
            self.search_output.pop(0)
            # Start the timeout of the next epect message
            if len(self.search_output) > 0:
               next_re_expected = self.search_output[0][0]
               next_search_deferred = self.search_output[0][1]
               next_timeout = self.search_output[0][3]
               self.search_output[0][2] = self.getTimeoutDefer(next_timeout,
                                   next_search_deferred, next_re_expected)
         else:
            msg = 'VLC Search for message "%s" timed ' % re_expected.pattern
            msg += 'out before the search started.'
            log.error(msg)
            msg = 'VLC We are currently searhing for: '
            msg += '"%s". ' % self.search_output[0][0].pattern
            log.error(msg)
            index = 1
            while index <= len(self.output_buffer):
               if self.search_output[index][1] == expect_deferred:
                  self.search_output.pop(index)
               index += 1

         expect_deferred.callback(result)

      cancel_deferred = reactor.callLater(timeout,expectTimedOut,expect_deferred)

      def cancelTimeout(result):
         if not cancel_deferred.cancelled and not cancel_deferred.called:
            cancel_deferred.cancel()
         return result

      expect_deferred.addCallback(cancelTimeout)
      return cancel_deferred

   def write(self,command):
      return self.sendLine(command)

   def expect(self,expected,timeout=5):
      re_expected = re.compile(expected)
      expect_deferred = defer.Deferred()

      if len(self.search_output) == 0:
         data = ''
         for line in self.output_buffer:
            match = re_expected.search(line)
            if match:
               data += line[:match.end()]
               log.debug('VLC Match "%s" found in (%s), clear buffer' % (expected,line))
               self.clearBuffer()
               expect_deferred.callback(data)
               break
            data += line + '\n'
      else:
         # We are not allow to start the timeout until we have started the search
         expect_deferred.pause()

      if not expect_deferred.called:
         cancel_deferred = None
         # Only create the cancel_deferred if this is current search.
         # if we are not we risk that the search times out before the search
         # started
         if len(self.search_output) == 0:
            cancel_deferred = self.getTimeoutDefer(timeout,expect_deferred,re_expected)
         self.search_output.append([re_expected,expect_deferred,cancel_deferred,timeout])

      return expect_deferred

   def streamOutputLine(self, streamname):
      return SOUTLINE.replace('[NAME]',streamname)

   def newBroadcast(self, streamname, streamuri):
      self.write('new '+streamname+' broadcast enabled')
      self.write('setup '+streamname+' input '+streamuri)
      self.write('setup '+streamname+' output '+self.streamOutputLine(streamname))


   def close(self):
      self.sendLine(self.factory.logout_command)
      self.factory.transport.loseConnection()
      return True

class VLCClientFactory(ReconnectingClientFactory):
   logout_command = 'exit'
   factor=2
   maxDelay=2
   initialDelay=0.5

   def __init__(self,username='',password='admin',greeting='\nWelcome, Master\n> ',prompt='>'):
      self.username = username
      self.password = password
      self.prompt = prompt
      self.greeting = greeting
      self.transport = None

   def buildProtocol(self, addr):
      self.transport = TelnetTransport(VLCClient)
      self.transport.factory = self
      return self.transport

   def setLogoutCommand(self,cmd):
      self.exit_command = cmd
 
   def clientConnectionLost(self, connector, reason):
      log.error('Lost VLC telnet connection.  Reason: %s ' % reason)
      ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

   def clientConnectionFailed(self, connector, reason):
      log.error('VLC Telnet connection failed. Reason:%s ' % reason)
      ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                         reason)



class VLCProtocol(protocol.ProcessProtocol):

   def __init__(self, factory):
      self.factory = factory

   def childConnectionLost(self, reason):
      log.debug("VLC CLOSE FD "+str(reason))

   def processEnded(self, reason):
      self.connectionLost(reason)

   def connectionLost(self, reason):
      log.error("VLC IS GONE "+str(reason))
      self.factory.restart()

   def outReceived(self, data):
      log.info("VLC STDOUT: "+str(data))

   def errReceived(self, data):
      log.debug("VLC STDERR: "+str(data))


class VLCFactory(object):
   process = False

   def start(self):
      proto=VLCProtocol(self)
      log.info("Starting new VLC Instance")
      producers.MediaProducers().delall()
      self.process=reactor.spawnProcess(proto, 'vlc', uid=33, gid=33, args=['vlc','--intf', 'telnet', '--telnet-password', 'admin']) # --telnet-password antani

   def restart(self):
      self.stop()
      reactor.callLater(0.5, self.start)

   def stop(self):
      if self.process:
         try:
            self.process.loseConnection()
         except:
            pass


class VideoProxyResource(ReverseProxyResource):

   def getChild(self, path, request):
      return self

   def _responseFailed(self, res, req, cfact):
      cfact.stop(req)
      log.debug("PROXY ResponseFailed "+str(res)+" "+str(req)+" "+str(cfact))

   def connectionLost(self, reason):
      log.debug("PROXY ConnectionLost "+str(reason))



class VideoProxy(rend.Page):

   addSlash = True

   def __init__(self, core):
      self.core = core
      super(VideoProxy, self).__init__(self)

   def childFactory(self, ctx, name):
      return permissionDenied()


class FFMpegProducer(protocol.ProcessProtocol):

   outstarted=False

   def __init__(self, cmd, father):
      log.info("FFMPEG PROCESS started: "+str(cmd))
      self.father = father
      self.cmd = cmd

   def outReceived(self, data):
      if not self.outstarted:
         self.outstarted=True
      log.debug("FFMPEG STDOUT "+str(len(data))+" bytes")
      self.father.progress(data)

   def errReceived(self, data):
      log.debug("FFMPEG STDERR RECEIVED: "+str(data))

   def connectionLost(self, reason):
      log.info("FFMPEG Connection Lost "+str(reason))
      try:
         self.loseConnection()
      except:
         pass
      reactor.callLater(3, self.father.restart)

   def outConnectionLost(self):
      self.connectionLost('FD1')


class FFMpegProducerFactory(ProxyClientFactory):

   protocol = FFMpegProducer
   proto = False
   client = False
   needsHeaders = True
   stoptry = False
   started = False

   def __init__(self, uri, core):
      self.uri = uri
      self.core = core

   def buildProtocol(self, req, vcodec, direct=False, ficodec=False, audiouri=False):
      self.client = req
      self.vcodec = vcodec
      self.direct = direct
      addinput=""
      addaudio=""
      if ficodec:
         addinput="-f "+str(ficodec)
      if audiouri:
         addaudio=" -i "+str(audiouri)+" -map 0:v:0 -map 1:a:0 "
      if vcodec in FFMPEGCMD.keys():
         fline=FFMPEGCMD[vcodec]
      else:
         fline=FFMPEG_MPEGTS
      cmd='ffmpeg '+addinput+' -i '+self.uri+addaudio+fline+" -"
      #if self.uri.startswith("http://") or self.uri.startswith("https://"):
      if vcodec!="mpegts" and not self.direct:
         cmd='ffmpeg '+addinput+' -i http://127.0.0.1:'+str(self.core.configGet('web','port'))+'/mediaproxy/raw/?uri='+urllib.quote(self.uri)+fline+" -"
      log.info("FFMPEG "+cmd)
      self.proto = reactor.spawnProcess(self.protocol(cmd, self), cmd.split()[0], args=cmd.split())
      reactor.callLater(15, self.checkStarted, req, vcodec)
      return self.proto

   def checkStarted(self, req, vcodec):
      if not self.started:
         if self.proto:
            try:
               self.proto.loseConnection()
               log.info("FFMPEG PRODUCER loseConnection in checkStarted for "+str(self.uri))
            except:
               pass
         if not self.stoptry:
            log.info("RESTART FFMPEG PRODUCER buildProtocol")
            #self.buildProtocol(req, vcodec)

   def restart(self):
      if not self.stoptry:
         self.started = False
         self.buildProtocol(self.client, self.vcodec, self.direct)
      

   def stop(self, req):
      self.stoptry = True
      log.info("FFMPEG PRODUCER STOP CALLED FOR "+str(self.uri))
      if self.proto:
         log.info("FFMPEG PRODUCER STOPPED")
         try:
            self.proto.signalProcess('KILL')
         except:
            pass

   def progress(self, data):
      log.debug("FFMPEG "+str(len(data))+" bytes of data received from "+str(self.uri))
      self.started=True
    
      client = self.client  
      if self.needsHeaders:
         log.debug("FFMPEG WRITING HEADER TO "+str(client))
         self.needsHeaders=False
         client.setHeader('server', 'Domotikad MediaProxy 1.0')
         client.setHeader('pragma','no-cache')
         client.setHeader('content-type',CONTENT_TYPES[self.vcodec])
         client.setHeader("X-Format-Requested", self.vcodec)
      log.debug('FFMPEG write to '+str(client.getClientIP()))
      client.write(data)



class FFMpegProxyResource(VideoProxyResource):

   proxyClientFactoryClass=FFMpegProducerFactory

   def __init__(self, uri, vcodec, core, reqargs):
      self.uri = uri
      self.vcodec = vcodec
      self.core = core
      force_input_codec=False
      if 'icodec' in reqargs:
         force_input_codec=urllib.unquote(reqargs['icodec'][0])
      direct = False     
      if 'direct' in reqargs:
         if urllib.unquote(reqargs['direct'][0]).lower() in ['1','true','yes','y','si']:
            direct=True

      self.audiouri = False
      if 'audiouri' in reqargs:
          self.audiouri = urllib.unquote(reqargs['audiouri'][0])     
      self.direct = direct
      self.ficodec = force_input_codec

   def render(self, request):
      request.received_headers['uri']=self.uri
      request.setHeader("pragma", "no-cache")
      try:
         request.content.seek(0,0)
      except:
         log.debug("FFMPEG MEDIA PROXY FD CLOSED (YET)")
      #sn = sha1()
      #sn.update(self.vcodec+"|"+self.uri)
      #streamname = sn.hexdigest()
      #prods=producers.MediaFFProducers()
      #prod = prods.get(streamname)
      #if not prod:
      log.info("FFMPEG Create new producer for uri: "+str(self.uri)+" codec: "+str(self.vcodec)+" separate audio: "+str(self.audiouri))
      prod = self.proxyClientFactoryClass(self.uri, self.core)
      #prods.add(streamname, prod)
   
      prod.buildProtocol(request, self.vcodec, self.direct, self.ficodec, self.audiouri)
      request.notifyFinish().addErrback(self._responseFailed, request, prod)
      return NOT_DONE_YET

class FFMpegProxy(VideoProxy):

   def child_(self, ctx):
      if int(self.core.configGet('media', 'localtranscode')) > 0:
         request = inevow.IRequest(ctx)
         if 'uri' in request.args:
            uri = urllib.unquote(request.args['uri'][0])
            return FFMpegProxyResource(uri, self.vtype, self.core, request.args)
      return permissionDenied()


class FFWebMProxy(FFMpegProxy):
   vtype = 'webm'

class FFH264Proxy(FFMpegProxy):
   vtype = 'h264'


class VLCProducer(object):

   def __init__(self, uri, vcodec, father):
      log.debug("VLC Producer for "+str(uri)+" with codec "+str(vcodec)+" initialized")
      page="http://localhost:7080/"+str(uri)+"_"+str(vcodec)
      self.vcodec=vcodec
      self.father=father
      self.getPage(page)

   def getPage(self, page):
      self.started=False
      self.connector, cb = wu.getPage(page,  progress=self.progress, stream=True, headerscb=self.gotHeaders) #, stream=pagePart)
      reactor.callLater(3, self.checkStarted, page)

   def checkStarted(self, page):
      if not self.started and not self.father.factorystopped:
         log.debug("RESTART VLC PRODUCER getPage")
         self.connector.react.disconnect()
         self.getPage(page)

   def gotHeaders(self, headers):
      log.debug("VLC GOT HEADERS "+str(headers))
      #if 'server' in  self.headers.keys():
      self.headers = headers
      self.headers['server']=['Domotikad MediaProxy 1.0']
      self.headers['pragma']=['no-cache']
      if not self.vcodec in CONTENT_TYPES.keys():
         self.headers['content-type']=['application/octet-stream']
      else:
         self.headers['content-type']=[CONTENT_TYPES[self.vcodec]]
      for h in self.headers.keys():
         self.father.setHeader(h, self.headers[h][0])

   def progress(self, data, currentLength, totalLength):
      self.started=True
      log.debug("VLC RECEIVED "+str(len(data))+" BYTES for "+str(self.father.getClientIP()))
      self.father.write(data)



class VLCProducerFactory(ProxyClientFactory):

   protocol = VLCProducer
   clients = 0

   def __init__(self, uri, streamname):
      self.uri = uri
      self.streamname = streamname

   def buildProtocol(self, req, vcodec):
      req.factorystopped=False
      log.debug("VLC PRODUCER BUILDPROTOCOL")
      if self.clients==0:
         p=producers.VLCTelnet()
         vlct = p.getClient()
         vlct.write("control "+self.streamname+" play")
      self.clients=self.clients+1
      self.proto = self.protocol(self.streamname, vcodec, req)
      return self.proto

   def stop(self, req):
      req.factorystopped=True
      if self.clients>0:
         self.clients=self.clients-1
         log.info("VLC PRODUCER stop called (remaining clients: "+str(self.clients)+")")
      if self.clients==0:
         log.debug("VLC PRODUCER STOPPED")
         p=producers.VLCTelnet()
         vlct = p.getClient()
         vlct.write("control "+self.streamname+" stop")
         vlct.write("del "+self.streamname)
         prods=producers.MediaProducers()
         prod = prods.delete(self.uri)



class VLCProxyResource(VideoProxyResource):

   proxyClientFactoryClass=VLCProducerFactory

   def __init__(self, uri, vcodec, core, reqargs):
      self.uri = uri
      self.vcodec = vcodec
      self.core = core
      direct=False
      if 'direct' in reqargs:
         if urllib.unquote(reqargs['direct'][0]).lower() in ['1','true','yes','y','si']:
            direct=True
      self.direct = direct

   def render(self, request):
      request.received_headers['uri']=self.uri
      request.setHeader("pragma", "no-cache")
      try:
         request.content.seek(0,0)
      except:
         log.debug("VLC MEDIA PROXY FD CLOSED (YET)")
      prods=producers.MediaProducers()
      prod = prods.get(self.uri)
      sn = sha1()
      sn.update(self.uri)
      streamname = sn.hexdigest()
      streamuri = self.uri
      if streamuri.startswith("http://") or streamuri.startswith("https://") and not self.direct:
         streamuri="http://127.0.0.1:"+str(self.core.configGet('web','port'))+"/mediaproxy/raw/?uri="+str(urllib.quote(self.uri))

      if not prod:
         log.info("Create new vlc producer for uri "+str(self.uri))

         p=producers.VLCTelnet()
         vlct = p.getClient()
         if not vlct:
            return permissionDenied()
         vlct.newBroadcast(streamname, streamuri)

         prod = self.proxyClientFactoryClass(self.uri, streamname)
         prods.add(self.uri, prod)

      prod.buildProtocol(request, self.vcodec)
      request.notifyFinish().addErrback(self._responseFailed, request, prod)
      return NOT_DONE_YET


class VLCProxy(VideoProxy):

   def child_(self, ctx):
      if int(self.core.configGet('media', 'localtranscode')) > 0:
         request = inevow.IRequest(ctx)
         if 'uri' in request.args:
            uri = urllib.unquote(request.args['uri'][0])
            return VLCProxyResource(uri, self.vtype, self.core, reqargs)
      return permissionDenied()



class VLCWebMProxy(VLCProxy):
   vtype = 'webm'

class VLCH264Proxy(VLCProxy):
   vtype = 'h264'


class RAWHTTPProducer(object):

   # NOTE: one for every client on the same url!

   clients=[]
   headers={}
   needsHeaders=[]
   fheader=""
   connector = False
   stoptry=False

   def __init__(self, uri):
      log.debug("HTTP RAW Producer for "+str(uri)+" initialized")
      self.uri = uri

   def addClient(self, client):
      if not client in self.clients:
         log.info("RAW HTTP ADD CLIENT for uri "+str(self.uri))
         self.clients.append(client)
         self.needsHeaders.append(client)
      if not self.connector:
         self.getPage(self.uri)

   def getPage(self, page):
      self.started=False
      self.connector, cb = wu.getPage(page,  progress=self.progress, stream=True, headerscb=self.gotHeaders) #, stream=pagePart)
      reactor.callLater(1, self.checkStarted, page)

   def checkStarted(self, page):
      if not self.started:
         log.debug("RESTART RAW HTTP PRODUCER getPage")
         if self.connector:
            self.connector.react.disconnect()
         if not self.stoptry:
            self.getPage(page)


   def delClient(self, client):
      if client in self.clients:
         log.info("RAW HTTP DELETE CLIENT for uri "+str(self.uri))
         self.clients.remove(client)
      if len(self.clients)==0:
         log.info("RAW HTTP CLIENT STOPPED FOR URI "+str(self.uri))
         self.disconnect()
         self.stoptry=True
         

   def gotHeaders(self, headers):
      #if 'server' in  self.headers.keys():
      log.debug("RAW gotHeaders "+str(headers))
      self.headers = headers
      self.headers['server']=['Domotikad MediaProxy 1.0']
      self.headers['pragma']=['no-cache']
      if not 'content-type' in self.headers.keys():
         self.headers['content-type']=['application/octet-stream']
      log.debug("RAW final headers "+str(self.headers))
    
  

   def progress(self, data, currentLength, totalLength):
      log.debug("RAW "+str(len(data))+" bytes of data received from "+str(self.uri))
      self.started=True
      if len(self.fheader)<1024:
         if 'content-type' in self.headers.keys() and self.headers['content-type'][0]=='application/octet-stream':
            log.debug("RAW SAVING STREAM HEADER...")
            self.fheader+=data

      for client in self.clients:
         if client in self.needsHeaders:
            for h in self.headers.keys():
               client.setHeader(h, self.headers[h][0])
            self.needsHeaders.remove(client)
            client.write(self.fheader)
         log.debug('RAW write to '+str(client.getClientIP()))
         client.write(data)

   def disconnect(self):
      if self.connector:
         self.connector.react.disconnect()
         self.fheader=''
         self.connector=False
         prods=producers.MediaRAWProducers()
         prod = prods.delete(self.uri)



class RAWHTTPProducerFactory(ProxyClientFactory):
   
   # NOTE: one for every url!

   protocol = RAWHTTPProducer
   proto = False

   def __init__(self, uri):
      self.uri = uri

   def buildProtocol(self, req):
      if not self.proto:
         self.proto = self.protocol(self.uri)
      self.proto.addClient(req)
      return self.proto

   def stop(self, req):
      log.info("RAW STOP CALLED FOR "+str(self.uri))
      if self.proto:
         self.proto.delClient(req)


class RAWHTTPProxyResource(VideoProxyResource):
   
   proxyClientFactoryClass=RAWHTTPProducerFactory

   def __init__(self, uri):
      self.uri = uri

   def render(self, request):
      request.received_headers['uri']=self.uri
      request.setHeader("pragma", "no-cache")
      try:
         request.content.seek(0,0)
      except:
         log.debug("RAW HTTP MEDIA PROXY FD CLOSED (YET)")
      prods=producers.MediaRAWProducers()
      prod = prods.get(self.uri)
      if not prod:
         log.info("RAW Create new producer for uri "+str(self.uri))
         prod = self.proxyClientFactoryClass(self.uri)
         prods.add(self.uri, prod)
      prod.buildProtocol(request)
      request.notifyFinish().addErrback(self._responseFailed, request, prod)
      return NOT_DONE_YET



class RAWProxy(VideoProxy):

   def child_(self, ctx):
      request = inevow.IRequest(ctx)

      log.debug("COPY")
      if 'uri' in request.args:
         uri = urllib.unquote(request.args['uri'][0])
         if uri.startswith('http://') or uri.startswith('https://'):
            return RAWHTTPProxyResource(uri)
         else:
            log.debug("RAW NON HTTP REQUESTED")
            if str(self.core.configGet('media','transcode_raw')) in ['vlc','VLC']:
               return VLCProxyResource(uri, 'h264', self.core)
            return FFMpegProxyResource(uri, 'mpegts', self.core)
      return permissionDenied()


class MediaStreamProxy(rend.Page):

   addSlash = True

   def child_(self, ctx):
      return permissionDenied()

   def childFactory(self, ctx, name):
      return permissionDenied()
   
   def child_webm(self, ctx):
      if str(self.core.configGet('media','transcode_webm')) in ['vlc','VLC']:
         return VLCWebMProxy(self.core)
      return FFWebMProxy(self.core)

   def child_h264(self, ctx):
      if str(self.core.configGet('media','transcode_h264')) in ['vlc','VLC']:
         return VLCH264Proxy(self.core)
      return FFH264Proxy(self.core)

   def child_raw(self, ctx):
      return RAWProxy(self.core)


