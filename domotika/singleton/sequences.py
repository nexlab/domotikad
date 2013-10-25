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
import time


class SequencesRegistrySingleton(Singleton):

   """ This is a singleton registry 
       to mantain the status of all web callater
       with a default expire timeout to be removed
   """

   callater = {}

   def __init__(self, *args, **kwargs):
      Singleton.__init__( self )


   def update_sequence(self, seqid, obj):
      self.callater[seqid] = obj

   def add_sequence(self, seqid, obj):
      self.update_sequence(seqid, obj)

   def del_sequence(self, seqid):
      try:
         self.callater[seqid].cancel()
      except:
         pass
      del self.callater[seqid]

   def get_sequence(self, seqid):
      if self.seqid_exists(seqid):
         return self.callater[seqid]
      return False

   def seqid_exists(self, seqid):
      if seqid in self.callater.keys():
         return True
      return False

   def getAll(self):
      return self.callater.values()

def SequenceRegistry():
      return SequencesRegistrySingleton.getInstance()

