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
      if(len(sys.argv)>7):
         self.transport.socket.setsockopt(SOL_SOCKET, IN.SO_BINDTODEVICE, sys.argv[7])
      else:
         self.transport.socket.setsockopt(SOL_SOCKET, IN.SO_BINDTODEVICE, "eth0")
      p=proto.IkaPacket()
      p.setSrc("USER.ON.Q")
      p.setDst(sys.argv[3]) 
      d=C.IKAP_BROADCAST
      
      p.setMsgType(int(sys.argv[4]))
      p.setCtx(int(sys.argv[5]))
      p.setAct(int(sys.argv[6]))
      if(str(sys.argv[2])=="0.0.0.0"):
         sys.argv[2]="255.255.255.255"

      self.transport.write(p.toSend(), (sys.argv[2], 6654))
      print 'SEND PACKET: %r' % p.cleanpacket()


      reactor.callLater(0.1, self.stop)

   def datagramReceived(self, data, (host, port)):
      print "%d -> received %r from %s:%d" % (time.time(), data, host, port)


   def stop(self):
      reactor.stop()

if __name__ == '__main__':
   if len(sys.argv) > 5:
      if os.path.isfile(sys.argv[1]):
   	   from twisted.internet import reactor
   	   reactor.listenUDP(0, DomIka())
   	   reactor.run()
   else:
      print './ikapacket_if_file.py <file> <ip dst> <dst> <msg type> <ctx> <act> [iface]'


