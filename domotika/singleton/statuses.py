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

from dmlib.singleton import Singleton
import time


class StatusesRegistrySingleton(Singleton):

   """ This is a singleton registry 
       to mantain the status of all web statuscall
       with a default expire timeout to be removed
   """

   statuscall = {}

   def __init__(self, *args, **kwargs):
      Singleton.__init__( self )


   def update_status(self, statusid, obj):
      self.statuscall[statusid] = obj

   def add_status(self, statusid, obj):
      self.update_status(statusid, obj)

   def del_status(self, statusid):
      try:
         self.statuscall[statusid].stop()
      except:
         pass
      del self.statuscall[statusid]

   def get_status(self, statusid):
      if self.statusid_exists(statusid):
         return self.statuscall[statusid]
      return False

   def statusid_exists(self, statusid):
      if statusid in self.statuscall.keys():
         return True
      return False

   def getAll(self):
      return self.statuscall.values()

   def getAllKeys(self):
      return self.statuscall.keys()

def StatusesRegistry():
      return StatusesRegistrySingleton.getInstance()

