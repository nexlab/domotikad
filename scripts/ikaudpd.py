#!/usr/bin/env python
from twisted.internet.protocol import DatagramProtocol
import time
from twisted.internet import reactor
import sys, os, IN                    
from socket import SOL_SOCKET, SO_BROADCAST
import struct
sys.path.append(os.path.dirname(sys.argv[0])+'/../domotika')

from dmlib.dmcrypt import BTEABlock
from dmlib import constants as C
#import pprint
from dmlib import ikaprotocol as proto
from dmlib.utils.genutils import revlist


class DomIka(DatagramProtocol):
 

   def startProtocol(self):
      #self.memkey=struct.pack('<LLLL', *DEFKEY)
      self.memkey=proto.DEFKEY
      self.btea=BTEABlock(self.memkey)
      self.bteadata=BTEABlock(self.memkey)
      self.ikahdr=proto.IkaPacketHeader()
      self.transport.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, True)
      try:
         self.transport.socket.setsockopt(SOL_SOCKET, IN.SO_BINDTODEVICE, "br0")
      except:
         self.transport.socket.setsockopt(SOL_SOCKET, IN.SO_BINDTODEVICE, "eth0")

   def datagramReceived(self, data, (host, port)):
      
      print "%r -> %s:%d, received %r" % (time.time(), host, port, data)
      #print struct.unpack('B', data[0])

      if(struct.unpack('B', data[0])[0]==C.IKAP_STARTBYTE):
         self.btea.setEncryptData(data[1:33])
         self.ikahdr.formatHeader(self.btea.cleandata)
         print 'HEADER', self.ikahdr
         print 'CHECKSUM', hex(self.ikahdr.chksum)
         print 'CALCULATED CHECKSUM:', hex(self.ikahdr.calculateCheckSum())

         totlen=self.ikahdr.srclen+self.ikahdr.dstlen+self.ikahdr.arglen
         datalendiff=len(data[33:])-totlen

         offset=0
         self.bteadata.key=self.ikahdr.key
         self.bteadata.setEncryptData(data[33:])
         if(self.ikahdr.srclen>0):
            print 'SRC:', self.bteadata.cleandata[offset:self.ikahdr.srclen]

         offset=self.ikahdr.srclen
         dstend=offset+self.ikahdr.dstlen
         if(self.ikahdr.dstlen>0):
            dst = self.bteadata.cleandata[offset:dstend]
            print 'DST:', dst

         offset=dstend
         argend=offset+self.ikahdr.arglen
         arg=False
         if(self.ikahdr.arglen>0):
            arg=self.bteadata.cleandata[offset:argend]
            if self.ikahdr.msgtype==C.IKAP_MSG_DEBUG:
               if dst.startswith("DEBUG.INPUT.CHANGED.TO") or dst.startswith("DEBUG.RELAY.CHANGED.TO"):
                  arg=struct.unpack('B', arg[0])[0]
            elif self.ikahdr.ctx==C.IKAP_CTX_SYSTEM and self.ikahdr.msgtype==C.IKAP_MSG_NOTIFYCONF:
               if dst.startswith("NETWORK."):
                  astr=struct.unpack('<26B', arg)
                  arg="\n\tIP: "+".".join([str(x) for x in astr[0:4]])
                  arg+="\n\tNETMASK: "+".".join([str(x) for x in astr[4:8]])
                  arg+="\n\tGW: "+".".join([str(x) for x in astr[8:12]])
                  arg+="\n\tDNS1: "+".".join([str(x) for x in astr[12:16]])
                  arg+="\n\tDNS2: "+".".join([str(x) for x in astr[16:20]])
                  arg+="\n\tMAC: "+":".join([hex(x)[2:].zfill(2) for x in astr[20:26]])
               elif dst.startswith("IOSTATUS.DEF"):
                  astr=struct.unpack('<5B', arg)
                  rel=list("".join(["".join(revlist(list(bin(x).replace("b", "").zfill(8)))) for x in astr[0:3]]))
                  if int(astr[3]):
                     rel=map(lambda x,y: "REL%d:%s" % (x,"ON" if int(y) else "OFF"), range(1,25) , rel[0:24])
                  else:
                     rel=map(lambda x,y: "REL%d:%s" % (x,"ON" if int(y) else "OFF"), range(1,13) , rel[0:12])
                  arg=" SERIAL: "
                  arg+="%s"  % "YES" if int(astr[3]) else "NO"
                  arg+=" AUTOSAVE: "
                  arg+="%s"  % "YES" if int(astr[4]) else "NO"
                  for r in rel:
                     arg+="\n\t"+r
               elif dst.startswith("IOSTATUS.NOW"):
                  #print len(arg)
                  astr=struct.unpack('<'+str(len(arg))+'B', arg)
                  rel=list("".join(["".join(revlist(list(bin(x).replace("0b", "").zfill(8)))) for x in astr[0:3]]))
                  if int(astr[6]):
                     rel=map(lambda x,y: "REL%d:%s" % (x,"ON" if int(y) else "OFF"), range(1,25) , rel[0:24])
                  else:
                     rel=map(lambda x,y: "REL%d:%s" % (x,"ON" if int(y) else "OFF"), range(1,13) , rel[0:12])

                  inp=list("".join(["".join(revlist(list(bin(x).replace("0b", "").zfill(8)))) for x in astr[3:6]]))
                  if int(astr[6]):
                     inp=map(lambda x,y: "INP%d:%s" % (x,"OFF" if int(y) else "ON"), range(1,25) , inp[0:24])
                  else:
                     inp=map(lambda x,y: "INP%d:%s" % (x,"OFF" if int(y) else "ON"), range(1,13) , inp[0:12])

                  larg=len(arg)
                  arg=" SERIAL: "
                  arg+="%s"  % "YES" if int(astr[6]) else "NO"
                  if(larg>7):
                     arg+=" AUTOSAVE: "
                     arg+="%s"  % "YES" if int(astr[7]) else "NO"
                  for r in rel:
                     arg+="\n\t"+r
                  for ist in inp:
                     arg+="\n\t"+ist

            elif self.ikahdr.ctx==C.IKAP_CTX_SYSTEM and self.ikahdr.msgtype==C.IKAP_MSG_REQUESTCONF:
               if dst.startswith("NETWORK."):
                  astr=struct.unpack('<4B', arg)
                  arg=" "+".".join([str(x) for x in astr[0:4]])
            elif dst.startswith("RELAY.CHANGED"):
               astr=struct.unpack('<3B', arg[0:3])
               tmp=[str(x) for x in astr[0:3]]
               arg="RELAY: "+tmp[0]+" ACTION: "+C.RELAY_ACT[int(tmp[1])]+" STATUS: "
               arg+="%s"  % "ON" if int(tmp[2]) else "OFF"


            print 'ARGS:', arg

         offset=argend
         end=offset+4
         checkdate=struct.unpack("<L", self.bteadata.cleandata[offset:end])[0]
         print 'CHECKDATE:', checkdate

         #packet=self.btea.cleandata[:-datalendiff]
         #print 'PACKET', self.btea.cleandata[:-datalendiff]

      print '-----------------------------'



   def stop(self):
      reactor.stop()

if __name__ == '__main__':
   from twisted.internet import reactor
   reactor.listenUDP(12081, DomIka())
   reactor.run()


