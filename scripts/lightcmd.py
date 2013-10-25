#!/usr/bin/env python
from twisted.internet.protocol import DatagramProtocol
import time
from twisted.internet import reactor
import sys                    
from socket import SOL_SOCKET, SO_BROADCAST
import IN, os
sys.path.append(os.path.dirname(sys.argv[0])+'/../domotika')
from dmlib import ikaprotocol as proto
from dmlib import constants as C
import struct
if not 'SO_BINDTODEVICE' in dir(IN):
   IN.SO_BINDTODEVICE = 25


class DomIka(DatagramProtocol):
 

   def startProtocol(self):
      self.transport.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, True)
      if(len(sys.argv)>4):
         self.transport.socket.setsockopt(SOL_SOCKET, IN.SO_BINDTODEVICE, sys.argv[4])
      else:
         self.transport.socket.setsockopt(SOL_SOCKET, IN.SO_BINDTODEVICE, "eth0")
      p=proto.IkaPacket()
      p.setSrc("USER.ON.Q")
      p.setDst(sys.argv[2]) 
      d=C.IKAP_BROADCAST
      if(len(sys.argv) > 3):
         d=sys.argv[3]
         p.setArg("".join([struct.pack("<B",i ) for i in [int(x) for x in d.split(".")]]))
      else:
         p.setArg(d)
      
      if(len(sys.argv) > 5):
         newarg=p.arg.ljust(10, "\x00")
         print "%r" %newarg
         if sys.argv[5].startswith("PRESET:"):
            newarg+="\x02"
            dim=sys.argv[5].split(":")
            newarg+=chr(int(dim[1]))
         elif sys.argv[5].startswith("DIMMER:"):
            newarg+="\x03"
            dim=sys.argv[5].split(":")
            rgb=dim[1].split(",")
            for c in rgb:
               newarg+=chr(int(c))

         elif sys.argv[5].startswith("RGB:"):
            newarg+="\x01"
            dim=sys.argv[5].split(":")
            rgb=dim[1].split(",")
            for c in rgb:
               newarg+=chr(int(c))
         newarg=newarg.ljust(20, "\x00")
         p.setArg(newarg)

      p.setMsgType(C.IKAP_MSG_ACTION)
      p.setCtx(C.IKAP_CTX_LIGHT)
      p.setAct(C.IKAP_ACT_CHANGE)
      self.transport.write(p.toSend(), (sys.argv[1], 6654))
      print 'SEND PACKET: %r' % p.cleanpacket()


      reactor.callLater(0.1, self.stop)

   def datagramReceived(self, data, (host, port)):
      print "%d -> received %r from %s:%d" % (time.time(), data, host, port)


   def stop(self):
      reactor.stop()

if __name__ == '__main__':
   if len(sys.argv) > 2:
   	from twisted.internet import reactor
   	reactor.listenUDP(0, DomIka())
   	reactor.run()


