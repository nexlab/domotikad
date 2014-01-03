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

from zope.interface import Interface, Attribute
from zope.interface import implements
from twisted.python import reflect
import logging
from dmlib import constants as C


log = logging.getLogger( 'Core' )

class IMediaSource(Interface):
   """ Base plugin Interface """
   
   def getMediaSource(self, host, adminpwd):
      """
         Return a DMBoard object
      """


class IMediaSourcePlugin(Interface):
   """ Implement a MediaSourceice """
  

def context2section(ctx):
   if int(ctx) in C.SECTIONS.keys():
      section=C.SECTIONS[int(ctx)]
   else:
      section="none"

   return section

class BaseMediaSource(object):
   implements(IMediaSourcePlugin)

   upnp_location=False
   adminpwd='domotika'
   upnp_location = 'http://127.0.0.1/' 
  

   def setAdminPwd(self, adminpwd):
      self.adminpwd = adminpwd
         
   def setUPNPLocation(self, location):
      self.upnp_location = location

