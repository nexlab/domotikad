###########################################################################
# Copyright (c) 2011-2013 Unixmedia S.r.l. <info@unixmedia.it>
# Copyright (c) 2011-2013 Franco (nextime) Lanza <franco@unixmedia.it>
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

#from xbee.zigbee import ZigBee
from xbee.ieee import XBee as ZigBee
from xbee.base import XBeeBase
from xbee.frame import APIFrame

from twisted.protocols.basic import LineReceiver

class ZigBeeProtocol(LineReceiver, ZigBee):
   def __init__(self, escaped=True):
      self._escaped = escaped
      self.frame = APIFrame(escaped=self._escaped)
                
      self.setRawMode()

   def rawDataReceived(self, data):
      print "received from ", self.transport.getPeer(), ": ", repr(data)
      data=data[1:][:-1]
      return getattr(self, "handle_packet", None)(self._split_response(data))

   def _write(self, data):
      frame = APIFrame(data, self._escaped).output()
      self.transport.write(frame)
