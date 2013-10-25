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

from dmlib.singleton import Singleton


class OldBoardsRegister(Singleton):

   """ This is a singleton registry 
       to mantain the status of all web callater
       with a default expire timeout to be removed
   """
   ips = []

   def __init__(self, *args, **kwargs):
      Singleton.__init__( self )

   def add_board(self, ip):
      self.ips.append(ip)

   def get_boardlist(self):
      return self.ips

def OldBoards():
      return OldBoardsRegister.getInstance()

