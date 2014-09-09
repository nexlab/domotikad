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

from twisted.internet.protocol import DatagramProtocol, ServerFactory
from twisted.protocols.basic import Int8StringReceiver
import time
from twisted.internet import reactor
import sys
from socket import SOL_SOCKET, SO_BROADCAST, AF_INET, SOCK_DGRAM, socket
import IN
import struct
from dmlib.dmcrypt import AES256
from dmlib import dmcrypt
import logging
from dmlib import constants as C
from dmlib import ikaprotocol as proto
from dmlib.utils.genutils import revlist, isTrue
import copy
from singleton import oldboards as oldb
from singleton import Singleton
from dmlib.utils import pwgen

log = logging.getLogger( 'IKAPServer' )

if not 'SO_BINDTODEVICE' in dir(IN):
   IN.SO_BINDTODEVICE = 25


class TCPClientRegistry(Singleton):

   clients={}
   
   def __init__(self, *args, **kwargs):
      Singleton.__init__( self )
      
   def add_client(self, key, client, port):
      if key in self.clients.keys():
         self.clients[key].append({'port': port, 'session': client, 'ip': key})
      else:
         self.clients[key]=[{'port': port, 'session': client, 'ip': key}]
      
   def del_client(self, key, port):
      if key in self.clients.keys():
         for c in self.clients[key]:
            if c['port']==port:
               self.clients[key].remove(c)
         if len(self.clients[key])==0:
            del self.clients[key]
         
   def get_clients(self, key=False):
      if key and key in self.clients.keys():
         return self.clients[key]
      elif not key:
         return [c for b in self.clients.values() for c in b]
      return []
      
      
TCPCLIENTREG=TCPClientRegistry.getInstance()



class DomIkaBaseProtocol(object):

   debugmode = False
   lastsettime=0 

   def __init__(self, core, *args, **kwargs):
      self.core = core
      self.initializated = False

   def retriveMemKey(self):
      if len(self.core.configGet('protocol', 'netpwd'))>4:
         memkey=dmcrypt.DMHash256(self.core.configGet('protocol', 'netpwd'))
         log.info("Protocol password is configured")
      else:
         log.info("Protocol password is DEFAULT")
         memkey=copy.deepcopy(proto.DEFKEY)
      return memkey
 
   def checkTimeLimits(self, epoch):
      # check if we are out of time limits
      now=int(time.time())
      if isTrue(self.core.configGet('protocol','timecheck')):
         tollerance=int(self.core.configGet('protocol','tollerance'))
         if(int(epoch)<now-tollerance or int(epoch)>now+tollerance):
            return False
      return True

   def initializeProtocol(self):
      self.memiv=copy.deepcopy(proto.DEFIV)
      self.memkey=self.retriveMemKey()
      if(self.memkey!=proto.DEFKEY):
         self.memiv=pwgen.generateIV128(self.memkey)

      self.aes=AES256(struct.unpack('<8L', self.memkey), struct.unpack('<4L', self.memiv))
      self.aesdata=AES256(struct.unpack('<8L', self.memkey), struct.unpack('<4L', self.memiv))

      self.debugmode=False
      if self.core.configGet('protocol','loglevel').lower()=='debug':
         self.debugmode=True

      self.ikahdr=proto.IkaPacketHeader()

   def invalidPacket(self):
      pass

   def createIkapPacket(self, command, ctx=False, act=False, arg=False, msgtype=False, src="Q.SERVER"):
      p=proto.IkaPacket(memkey=self.memkey, memiv=self.memiv)
      p.setSrc(src)
      p.setDst(str(command))
      if(ctx):
         p.setCtx(ctx)
      if(act):
         p.setAct(act)
      if(arg):
         try:
            if type(arg).__name__=='dict':
               if 'ip' in arg.keys():
                  arg=proto.dictToIkapArg(arg)
               else:
                  arg=proto.dictToIkapArg(arg, "0.0.0.0")
         except:
            import traceback
            traceback.print_exc(file=sys.stdout)
            pass
         p.setArg(arg)
      else:
         p.setArg(C.IKAP_BROADCAST)
      if(msgtype):
         p.setMsgType(msgtype)
      return p


   def ikapPacketReceived(self, data, (host, port), ptype='UDP4'):
      #log.info( "%r -> %s:%d, aes received %r" % (time.time(), host, port, data))
      log.info("%r -> %s:%d, received packet" % (time.time(), host, port))
      log.debug("raw data: %r" % data)
      #print struct.unpack('B', data[0])
      now=int(time.time())
      #NEXTIME
      
      if(struct.unpack('B', data[0])[0]==C.IKAP_STARTBYTE):
         self.aes.setEncryptData(data[1:33])
         try:
            self.ikahdr.formatHeader(self.aes.cleandata)
            log.debug( 'HEADER %s' % self.ikahdr)
            log.debug( 'CHECKSUM %s' % hex(self.ikahdr.chksum))
            log.debug('CALCULATED CHECKSUM: %s' % hex(self.ikahdr.calculateCheckSum()))
            log.debug('HEADER TIME: %d' % int(self.ikahdr.epoch))
            totlen=self.ikahdr.srclen+self.ikahdr.dstlen+self.ikahdr.arglen
            datalendiff=len(data[33:])-totlen
            offset=0
            self.aesdata.key=struct.unpack('<8L', self.memkey)
            self.aesdata.iv=self.ikahdr.key
            self.aesdata.setEncryptData(data[33:])
            if(self.ikahdr.srclen>0):
               log.info('SRC: %s' % self.aesdata.cleandata[offset:self.ikahdr.srclen])

            offset=self.ikahdr.srclen
            dstend=offset+self.ikahdr.dstlen
            src=""
            if(self.ikahdr.srclen>0):
               src=self.aesdata.cleandata[:self.ikahdr.srclen].rstrip()
            dst=""
            if(self.ikahdr.dstlen>0):
               dst=self.aesdata.cleandata[offset:dstend]
            log.info('DST: %s' % dst)

            if src=='Q.RELAYPROTO':
               return

            offset=dstend
            argend=offset+self.ikahdr.arglen
            epoch=struct.unpack('<L', self.aesdata.cleandata[argend:argend+4])[0]
         except:
            log.error("INVALID PACKET RECEIVED (CRYPTO) FROM "+str(host))
            return

         log.debug("EPOCH: %s" %str(epoch))
         if(epoch!=self.ikahdr.epoch):
            log.error("INVALID PACKET RECEIVED (CRYPTO) FROM "+str(host)+" (epoch doesn't match!)")
            return
         arg=False
         if(self.ikahdr.arglen>0):
            arg=self.aesdata.cleandata[offset:argend]
            if self.ikahdr.msgtype==C.IKAP_MSG_DEBUG:
               if dst.startswith("DEBUG.INPUT.CHANGED.TO") or dst.startswith("DEBUG.RELAY.CHANGED.TO"):
                  arg=struct.unpack('B', arg[0])[0]
            elif self.ikahdr.msgtype==C.IKAP_MSG_NOTIFY and dst.startswith("BOOTED."):
               self.core.broadcastTime(host)
               #self.sendCommand("SETTIME", arg=struct.pack("<L", int(time.time())), act=C.IKAP_ACT_BOARD, ctx=C.IKAP_CTX_SYSTEM, msgtype=C.IKAP_MSG_ACTION, ipdst=host)
            elif self.ikahdr.msgtype==C.IKAP_MSG_NOTIFY and self.ikahdr.ctx==C.IKAP_CTX_SYSTEM and dst=='RELAY.AMPERE.LIMIT':
               try:
                  log.info("Relay "+str(struct.unpack("<B", arg[1])[0])+" has gone in overrun at "+str(float(struct.unpack("<B", arg[0])[0])/10.0)+" Ampere")
               except:
                  pass
            elif self.ikahdr.ctx==C.IKAP_CTX_SYSTEM and self.ikahdr.msgtype==C.IKAP_MSG_NOTIFYCONF:
               if dst.startswith("NETWORK."):
                  astr=struct.unpack('<26B', arg[:26])
                  webport=80
                  if len(arg)>26:
                     webport=struct.unpack('<H', arg[26:28])[0]
                  
                  self.core.updateWebPort(src, host, webport, port, ptype)
                  arg="\n\tIP: "+".".join([str(x) for x in astr[0:4]])
                  arg+="\n\tNETMASK: "+".".join([str(x) for x in astr[4:8]])
                  arg+="\n\tGW: "+".".join([str(x) for x in astr[8:12]])
                  arg+="\n\tDNS1: "+".".join([str(x) for x in astr[12:16]])
                  arg+="\n\tDNS2: "+".".join([str(x) for x in astr[16:20]])
                  arg+="\n\tMAC: "+":".join([hex(x)[2:].zfill(2) for x in astr[20:26]])
                  arg+="\n\tWEBPORT: "+str(webport)

               elif dst.startswith("IOSTATUS.DEF"):
                  astr=struct.unpack('<'+str(len(arg))+'B', arg)
                  rel=list("".join(["".join(revlist(list(bin(x).replace("b", "").zfill(8)))) for x in astr[0:3]]))
                  rel=map(lambda x,y: "REL%d:%s" % (x,"ON" if int(y) else "OFF"), xrange(1,13) , rel[0:12])
                  for r in rel:
                     arg+="\n\t"+r

               elif dst.startswith("IOSTATUS.NOW") and self.checkTimeLimits(self.ikahdr.epoch):
                  def manageIOSTATUS(self, arg):
                     astr=struct.unpack('<'+str(len(arg))+'B', arg)
                     baseboard_type=struct.unpack('<H', arg[2:4])[0]
                     msg_fwtype=struct.unpack('<B', arg[0])[0]
               
                     # For compatibility with pre-5 firmware
                     o=oldb.OldBoards()
                     if host in o.get_boardlist():
                        log.info("OLDBOARD DETECTED FOR IP "+str(host))
                        msg_fwtype=0x02
                        baseboard_type=0x0001

                     if msg_fwtype==C.FWTYPE_RELAYMASTER:
                        rawio=list("".join(
                           ["".join(revlist(list(bin(x).replace("0b", "").zfill(8)))) for x in iter(astr[5:9])]))

                        # For compatibility with pre-5 firmware
                        if host in o.get_boardlist():
                           rawio=list("".join(
                              ["".join(revlist(list(bin(x).replace("0b", "").zfill(8)))) for x in iter(astr[0:4])]))

                        rawrel=rawio[0:12]
                        rawinp=rawio[16:28]
                        if baseboard_type==C.BOARD_WORKER_12R12I_v3:
                           self.core.setAnalogStatus(src, host, port, ptype, 1,
                              struct.unpack('<h', struct.pack('<2B', *astr[9:11]))[0])
                           self.core.setAnalogStatus(src, host, port, ptype, 2,
                              struct.unpack('<h', struct.pack('<2B', *astr[11:13]))[0])

                           rawamp=astr[13:25]
                        else:
                           rawamp=[0]*12

                        #map(lambda x,y: self.core.setRelayStatus(src, host, x, y, rawamp[x-1]), 
                        #   xrange(1,13) , iter(rawrel))
                        map(lambda x,y: reactor.callLater(0.01, 
                           self.core.setRelayStatus, src, host, port, ptype, x, y, rawamp[x-1]),
                           xrange(1,13), iter(rawrel))

                        #map(lambda x,y: self.core.setInputStatus(src, host, x, str(int(y))), 
                        #   xrange(1,13), iter(rawinp))
                        map(lambda x,y: reactor.callLater(0.05,
                           self.core.setInputStatus, src, host, port, ptype, x, str(int(y))),
                           xrange(1, 13), iter(rawinp))

                        larg=len(arg)
                     
                        self.core.updateBoardLastStatus(host, port, ptype, src)

                     if msg_fwtype==C.FWTYPE_RELAYMASTERANA:
                        rawio=list("".join(
                           ["".join(revlist(list(bin(x).replace("0b", "").zfill(8)))) for x in iter(astr[5:9])]))

                        # For compatibility with pre-5 firmware
                        if host in o.get_boardlist():
                           rawio=list("".join(
                              ["".join(revlist(list(bin(x).replace("0b", "").zfill(8)))) for x in iter(astr[0:4])]))

                        rawrel=rawio[0:6]
                        rawinp=rawio[16:28]
                        if baseboard_type==C.BOARD_WORKER_12R12I_v3:
                           anab=9
                           for an in xrange(1, 9):
                              self.core.setAnalogStatus(src, host, port, ptype, an,
                                 struct.unpack('<h', struct.pack('<2B', *astr[anab:anab+2]))[0])
                              anab+=2

                        rawamp=dst[13:19]

                        map(lambda x,y: reactor.callLater(0.01,
                           self.core.setRelayStatus, src, host, port, ptype, x, y, rawamp[x-1]),
                           xrange(1,7), iter(rawrel))

                        map(lambda x,y: reactor.callLater(0.05,
                           self.core.setInputStatus, src, host, port, ptype, x, str(int(y))),
                           xrange(1, 13), iter(rawinp))

                        larg=len(arg)

                        self.core.updateBoardLastStatus(host, port, ptype, src)

                  reactor.callLater(0.1, manageIOSTATUS, self, arg)

               elif dst.startswith("BOARDTYPE"):
                  # XXX Remove obsolete boards schema
                  if len(arg) > 9:
                     if str(arg[5:]) in ['DMRv3', 'DMRv1', 'DMSnt84','DMRv4']:
                        fwver=int(struct.unpack('<B', arg[4])[0])
                        self.core.addBoard(str(arg[5:]), fwver, src, host, 80, port, ptype)
                     elif str(arg[7:]) in ['DMRv3', 'DMRv1', 'DMSnt84','DMRv4']:
                        fwver=int(struct.unpack('<B', arg[4])[0])
                        webport=int(struct.unpack('<H', arg[5:7])[0])
                        self.core.addBoard(str(arg[7:]), fwver, src, host, webport, port, ptype)
                  else:
                     if str(arg[4:]) in ['DMRv3', 'DMRv1', 'DMSnt84','DMRv4']:
                        fwver=int(struct.unpack('<B', arg[3])[0])
                        self.core.addBoard(str(arg[4:]), fwver, src, host, 80, port, ptype)
               elif dst.startswith("RELAYSTATUS.CHANGE") and self.checkTimeLimits(self.ikahdr.epoch):
                  astr=struct.unpack('<'+str(len(arg))+'B', arg)
                  i=0
                  while i<=len(astr)-2:
                     if i>23:
                        break
                     else:
                        st=0
                        if(astr[i+1]!=0):
                           st=1
                        arg="RELAY: "+str(astr[i])+" CHANGED TO:"
                        arg+="%s"  % "ON" if st else "OFF"

                        self.core.setRelayStatus(src, host, port, ptype, astr[i], st)     
                     i+=2


            elif self.ikahdr.ctx==C.IKAP_CTX_SYSTEM and self.ikahdr.msgtype==C.IKAP_MSG_REQUESTCONF:
               if dst.startswith("NETWORK."):
                  astr=struct.unpack('<4B', arg)
                  arg=" "+".".join([str(x) for x in astr[0:4]])

               elif dst.startswith("IOSTATUS.NOW") and self.checkTimeLimits(self.ikahdr.epoch):
                  if self.ikahdr.msgtype==C.IKAP_MSG_REQUESTCONF:
                     if not self.core.isLocalSource(host, ptype):
                        self.core.updateLastStatusTime()

            elif dst.startswith("RELAY.CHANGED") and self.checkTimeLimits(self.ikahdr.epoch):
               astr=struct.unpack('<3B', arg[0:3])
               tmp=[str(x) for x in astr[0:3]]
               arg="RELAY: "+tmp[0]+" ACTION: "+C.RELAY_ACT[int(tmp[1])]+" STATUS: "
               arg+="%s"  % "ON" if int(tmp[2]) else "OFF"
               self.core.setRelayStatus(src, host, port, ptype, astr[0], astr[2])

            try:
               log.debug('ARG: %s' % str(arg))
               log.debug('RAWARG: %r' % self.aesdata.cleandata[offset:argend])
            except:
               log.debug('CANNOT WRITE ARGS')
            try:
               log.info('ARGDICT: '+str(proto.ikapArgtoDict(self.aesdata.cleandata[offset:argend])))
            except:
               log.info("NO ARGDICT IS FEASIBLE")


         argdict=proto.getDefaultDict()
         argdict['ip']=host
         argdict['raw']=arg
         try:
            #if self.ikahdr.msgtype==C.IKAP_MSG_ACTION:
            if self.ikahdr.ctx!=C.IKAP_CTX_SYSTEM:
               argdict=proto.ikapArgtoDict(self.aesdata.cleandata[offset:argend])
         except:
            pass
         offset=argend
         end=offset+4
         checkdate=struct.unpack("<L", self.aesdata.cleandata[offset:end])[0]
         log.debug('CHECKDATE: %s' % str(checkdate))
         # XXX CONTROLLARE!
         packet_isvalid=True
         #if self.ikahdr.msgtype!=C.IKAP_MSG_ACTION:
         #   argdict=False
         if packet_isvalid:
            if self.checkTimeLimits(self.ikahdr.epoch):
               self.core.manageIncomingPacket(self.ikahdr, src, dst, arg, host, port, ptype, argdict, data)
            else:
               log.error("INVALID PACKET TIME FROM "+str(host)+" - packet time: "+str(self.ikahdr.epoch)+" now: "+str(time.time()))
               now=int(time.time())
               if now-self.lastsettime>10:
                  self.core.broadcastTime()
               else:
                  self.core.broadcastTime(host)
               self.invalidPacket()
         else:
            log.error("INVALID PACKET (second check) FROM "+str(host))
            self.invalidPacket()
      else:
         log.error("INVALID PACKET (start) FROM "+str(host))
         self.invalidPacket()
      log.debug('-----------------------------')


class DomIkaUDP(DatagramProtocol, DomIkaBaseProtocol):

   def retrivePort(self, msgtype):
      if msgtype in [C.IKAP_BROADCAST, C.IKAP_MSG_REQUEST, C.IKAP_MSG_REQUESTCONF,
                     C.IKAP_MSG_SETCONF, C.IKAP_MSG_ACK]:
         return int(self.core.configGet('ikapserver', 'port'))
      return int(self.core.configGet('ikapserver', 'notifyport'))


   def startProtocol(self):
      self.initializeProtocol()
      self.transport.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, True)
      try:
         self.transport.socket.setsockopt(SOL_SOCKET, IN.SO_BINDTODEVICE,
            self.core.configGet('ikapserver', 'ethdev'))
      except:
         self.transport.socket.setsockopt(SOL_SOCKET, IN.SO_BINDTODEVICE, "eth0")

   def sendRawData(self, data, msgtype, ipdst='255.255.255.255'):
      if not self.initializated:
         self.transport.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, True)
         try:
            self.transport.socket.setsockopt(SOL_SOCKET, IN.SO_BINDTODEVICE,
               self.core.configGet('ikapserver', 'ethdev'))
         except:
            self.transport.socket.setsockopt(SOL_SOCKET, IN.SO_BINDTODEVICE, "eth0")
         self.initializated = True
      self.transport.write(data, (ipdst, self.retrivePort(msgtype)))
   

   def sendCommand(self, command, ctx=False, act=False, arg=False, msgtype=False,
      src="Q.SERVER", ipdst="255.255.255.255" ):
      if not self.initializated:
         self.transport.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, True)
         try:
            self.transport.socket.setsockopt(SOL_SOCKET, IN.SO_BINDTODEVICE,
               self.core.configGet('ikapserver', 'ethdev'))
         except:
            self.transport.socket.setsockopt(SOL_SOCKET, IN.SO_BINDTODEVICE, "eth0")

         self.initializated = True

      p=self.createIkapPacket(command, ctx, act, arg, msgtype, src)
      self.sendRawData(p.toSend(), msgtype, ipdst)
      log.debug('SEND UDP PACKET: %r' % p.cleanpacket())

   def datagramReceived(self, data, (host, port)):
      return self.ikapPacketReceived(data, (host, int(self.core.configGet('ikapserver', 'port'))), 'UDP4')



class DomIkaTCP(Int8StringReceiver, DomIkaBaseProtocol):

   disconnected=True

   def sendRawData(self, data, *a, **kw ):
      self.sendString(data)

   def sendCommand(self, command, ctx=False, act=False, arg=False, msgtype=False,
      src="Q.SERVER", ipdst="255.255.255.255" ):
      p=self.createIkapPacket(command, ctx, act, arg, msgtype, src)
      self.sendRawData(p.toSend())
      log.debug('SEND TCP PACKET: %r' % p.cleanpacket())

   def stringReceived(self, data):
      addr = self.transport.getPeer()
      host, port = addr.host, addr.port
      return self.ikapPacketReceived(data, (host, port), 'TCP4')
   
   def connectionLost(self, *a):
      self.disconnected=True
      addr = self.transport.getPeer()
      host, port = addr.host, addr.port
      TCPCLIENTREG.del_client(host, port)

   def connectionMade(self):
      #self.transport.setTcpNoDelay()
      #self.transport.setTcpKeepAlive()      

      self.disconnected=False
      self.sendCommand("IOSTATUS.NOW", arg=C.IKAP_BROADCAST, act=C.IKAP_ACT_BOARD,
          ctx=C.IKAP_CTX_SYSTEM, msgtype=C.IKAP_MSG_REQUESTCONF)
      self.sendCommand("SETTIME", arg=struct.pack("<L", int(time.time())), act=C.IKAP_ACT_BOARD, ctx=C.IKAP_CTX_SYSTEM, msgtype=C.IKAP_MSG_ACTION)
      #self.core.broadcastTime()

   def invalidPacket(self):
      try:
         self.transport.write("GO AWAY!")
      except:
         pass
      reactor.callLater(0.2, self.transport.abortConnection)

   

class DomIkaServerFactory(ServerFactory):
   protocol=DomIkaTCP

   def __init__(self, core, *a, **kw):
      self.core = core

   def buildProtocol(self, addr):
      p = self.protocol(self.core)
      p.factory = self
      TCPCLIENTREG.add_client(addr.host, p, addr.port)
      return p

   def sendRawData(self, data, msgtype, ipdst='255.255.255.255'):
      if ipdst in ['255.255.255.255','0.0.0.0']:
         cs=TCPCLIENTREG.get_clients()
      else:
         cs=TCPCLIENTREG.get_clients(str(ipdst))
      for c in cs:
         try:
            c['session'].sendRawData(data, msgtype, ipdst)
         except:
            TCPCLIENTREG.del_client(cs['ip'], cs['port'])


   def sendCommand(self, command, ctx=False, act=False, arg=False, msgtype=False,
      src="Q.SERVER", ipdst="255.255.255.255" ):
      if ipdst in ['255.255.255.255','0.0.0.0']:
         cs=TCPCLIENTREG.get_clients()
      else:
         cs=TCPCLIENTREG.get_clients(str(ipdst))
      for c in cs:
         try:
            c['session'].sendCommand(command,ctx,act,arg,msgtype,src)
         except:
            TCPCLIENTREG.del_client(cs['ip'], cs['port'])


if __name__ == '__main__':
   from twisted.internet import reactor
   reactor.listenUDP(6654, DomIkaUDP(), self.core.configGet('ikapserver', 'interface'))
   reactor.run()

