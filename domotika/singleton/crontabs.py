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


class CrontabsRegistrySingleton(Singleton):

   """ This is a singleton registry 
       to mantain the status of all web croncall
       with a default expire timeout to be removed
   """

   croncall = {}

   def __init__(self, *args, **kwargs):
      Singleton.__init__( self )


   def update_cron(self, cronid, obj):
      self.croncall[cronid] = obj

   def add_cron(self, cronid, obj):
      self.update_cron(cronid, obj)

   def del_cron(self, cronid):
      try:
         self.croncall[cronid].stop()
      except:
         pass
      del self.croncall[cronid]

   def get_cron(self, cronid):
      if self.cronid_exists(cronid):
         return self.croncall[cronid]
      return False

   def cronid_exists(self, cronid):
      if cronid in self.croncall.keys():
         return True
      return False

   def getAll(self):
      return self.croncall.values()

   def getAllKeys(self):
      return self.croncall.keys()

def CrontabsRegistry():
      return CrontabsRegistrySingleton.getInstance()

