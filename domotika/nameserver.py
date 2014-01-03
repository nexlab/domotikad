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


import socket
 
from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor
from twisted.names import dns
from twisted.names import client, server
import netifaces
 
CHANGE = 'example.com'
TO = '127.0.0.1'
TTL = 60
 
class DNSServerFactory(server.DNSServerFactory):
    def gotResolverResponse(self, (ans, auth, add), protocol, message, address):
        qname = message.queries[0].name.name
        if self.dmhost in qname:
            for answer in ans:
                if answer.type != dns.A:
                    continue
                if not answer.name.name.endswith(self.dmhost):
                    continue
                
                to=self.dmip
                if self.dmip=='auto':
                   try:
                      to=netifaces.ifaddresses(self.dmiface)[2][0]['addr']
                   except:
                      try:
                         to=netifaces.ifaddresses(self.dmiface+':0')[2][0]['addr']
                      except:
                         to='10.224.207.1'
                answer.payload.address = socket.inet_aton(to)
                answer.payload.ttl = TTL
 
        args = (self, (ans, auth, add), protocol, message, address)
        return server.DNSServerFactory.gotResolverResponse(*args)
 
 
def startDNS(host="q.unixmedia.net", ip="auto", iface="eth0", servers=[('8.8.8.8', 53)]):
   verbosity = 0
   resolver = client.Resolver(servers=servers)
   factory = DNSServerFactory(clients=[resolver], verbose=verbosity)
   factory.dmhost = host
   factory.dmip = ip
   factory.dmiface = iface
   protocol = dns.DNSDatagramProtocol(factory)
   factory.noisy = protocol.noisy = verbosity
 
   reactor.listenUDP(53, protocol)
   reactor.listenTCP(53, factory)


if __name__ == '__main__':
   startDNS('q.unixmedia.net', 'auto')
   reactor.run()
