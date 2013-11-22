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

from domotika.mediasources import ivideodev
from domotika.mediasources.ivideodev import context2section, BaseVideoDev
from domotika.db import dmdb
from domotika.lang import lang
from zope.interface import implements
from twisted.plugin import IPlugin
from dmlib.utils import webutils as wu
from twisted.internet import defer
from dmlib import constants as C
import logging

try:
   log = logging.getLogger('Core').getChild('Video.Sitecom.LN406')
except:
   log = logging.getLogger('Core')


try:
   import hashlib
   md5 = hashlib
   md5.new = hashlib.md5
   sha1 = hashlib.sha1
except:
   import md5
   import sha1


class VideoDevPlugin(BaseVideoDev):

   def __init__(self, host, adminpwd='domotika'):
      self.host = host
      self.adminpwd = adminpwd

   def addDevice(self):
      return dmdb.Videos.find(where=['ip=?', self.host], limit=1).addCallback(self.getSitecomName)
      
   def getSitecomName(self, res):
      wu.getPage("http://"+self.host+'/util/query.cgi',
         http_user="admin", http_password=self.adminpwd).addCallback(
            self.saveSitecom, res)

   def saveSitecom(self, wres, res):
      if not res:
         try:
            hname=wres.split("\n")[0].split("=")[1].replace(".", " ")
         except:
            hname=self.host

         c=dmdb.Videos()
         c.ip=self.host
         #c.videostream='rtsp://admin:'+self.adminpwd+'@'+host+'/img/media.sav'
         c.controlapi='http://admin:'+self.adminpwd+'@'+self.host+'/'
         c.videostream='http://admin:'+self.adminpwd+'@'+self.host+'/img/video.asf'
         c.mjpeg='http://admin:'+self.adminpwd+'@'+self.host+'/img/media.mjpeg'
         c.websection='camera'
         c.button_name='Telecamera '+hname
         c.position=1
         c.screenshot='http://admin:'+self.adminpwd+'@'+self.host+'/img/snapshot.cgi?size=3&quality=5'
         c.dynamic=1
         if self.upnp_location:
            c.upnp_location=self.upnp_location
         c.model='LN406'
         c.manufacturer='Sitecom'
         c.active=1
         c.save().addCallback(log.info)
         log.info("SITECOM LN406 "+self.host+" CAMERA ADDED")

class VideoDev(object):

   implements(IPlugin, ivideodev.IVideoDev)

   def getVideoDev(self, host, adminpwd):
      log.info("Found plugin for host "+str(host))
      return VideoDevPlugin(host, adminpwd)

videodev=VideoDev()

