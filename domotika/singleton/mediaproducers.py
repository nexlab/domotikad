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


class MediaProducersRegister(Singleton):

   producers={}

   def __init__(self, *args, **kwargs):
      Singleton.__init__( self )

   def add(self, url, obj):
      if not url in self.producers.keys():
         self.producers[url] = obj

   def get(self, url):
      if url in self.producers.keys():
         return self.producers[url]
   
   def delete(self, url):
      if url in self.producers.keys():
         try:
            self.producers[url].stopProducing()
         except:
            pass
         try:
            del self.producers[url]
         except:
            pass

   def delall(self):
      for u in self.producers.keys():
         try:
            self.producers[u].stopProducing()
         except:
            pass
      self.producers={}


def MediaProducers():
      return MediaProducersRegister.getInstance()


class MediaRAWProducersRegister(Singleton):

   producers={}

   def __init__(self, *args, **kwargs):
      Singleton.__init__( self )

   def add(self, url, obj):
      if not url in self.producers.keys():
         self.producers[url] = obj

   def get(self, url):
      if url in self.producers.keys():
         return self.producers[url]
  
   def delete(self, url):
      if url in self.producers.keys():
         try:
            self.producers[url].stopProducing()
         except:
            pass
         try:
            del self.producers[url]
         except:
            pass
   


def MediaRAWProducers():
      return MediaRAWProducersRegister.getInstance()


class VLCTelnetSingleton(Singleton):

   client=False

   def __init__(self, *args, **kwargs):
      Singleton.__init__( self )

   def setClient(self, client):
      self.client = client

   def getClient(self):
      return self.client

def VLCTelnet():
   return VLCTelnetSingleton.getInstance()
