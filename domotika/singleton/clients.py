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


# XXX Make the client expire
#
class ClientRegistrySingleton(Singleton):

   """ This is a singleton registry 
       to mantain the status of all web clients
       with a default expire timeout to be removed
   """

   clients = {}
   cobj = {}
   sessions = {}

   def __init__(self, *args, **kwargs):
      Singleton.__init__( self )


   def update_session(self, suid, ses, obj):
      self.clients[suid] = {'obj': obj, 'time': time.time(), 'session': ses, 'suid': suid}
      self.cobj[suid] = obj
      self.sessions[suid] = ses
      

   def del_session(self, suid):
      if suid in self.clients.keys():
         del self.clients[suid]
      if suid in self.cobj.keys():
         del self.cobj[suid]
      if suid in self.sessions.keys():
         del self.sessions[suid]

   def get_cobj(self, suid):
      if self.session_exists(suid):
         return self.clients[suid]['obj']
      return False

   def get_session(self, suid):
      if self.session_exists(suid):
         return self.clients[suid]['session']
      return False

   def get_time(self, suid):
      if self.session_exists(suid):
         return self.clients[suid]['time']
      return False


   def session_esists(self, suid):
      if session in self.clients.keys():
         return True
      return False

   def getAll(self):
      return self.clients.values()

def ClientRegistry():
      return ClientRegistrySingleton.getInstance()


CLIENTREGISTRY=ClientRegistry()
