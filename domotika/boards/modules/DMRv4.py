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

from domotika.boards import iboards
from domotika.boards.boardtype import BaseBoard, ANABoard, INPBoard, OUTBoard
from zope.interface import implements
from twisted.plugin import IPlugin


try:
   import hashlib
   md5 = hashlib
   md5.new = hashlib.md5
   sha1 = hashlib.sha1
except:
   import md5
   import sha1


class DMBoard(INPBoard, ANABoard, OUTBoard, BaseBoard):

   hasAnalogs = True
   hasOutputs = True
   hasInputs = True
   hasRelays = True
   hasAmperometers = True
   fwtype = 'relaymaster'

   firstAna = 13
   numAna = 8
   numInp = 12
   numOut = 6


class Board(object):
   implements(IPlugin, iboards.IDMBoards)

   def getBoard(self, host, port, pwd, lang):
      return DMBoard(self.core, host, port, pwd, lang)

board=Board()
