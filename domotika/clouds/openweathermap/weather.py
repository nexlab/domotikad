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

from twisted.internet import defer, reactor, task
from dmlib.utils import webutils as wu
import json
import logging
from domotika.db import dmdb


try:
   log = logging.getLogger('Core').getChild('Clouds.OpenWeatherMap.Weather')
except:
   log = logging.getLogger('Core')


class OWMWeather(object):

   usecity=False
   timer=False
   data = {}

   def __init__(self, lat=None, lon=None, city=None, owmid=0):
      if (not lat and not lon) and not city:
         raise Exception("You must specify at least one between lon/lat or city for OpenWeatherMap!")
      self.lon = lon
      self.lat = lat
      self.city = city
      self.owmid = owmid
      if self.city and self.city.lower() not in ['no','none','unknown','','n','0']:
         self.usecity=True
      self.timer = task.LoopingCall(self._getReport)
      self.timer.start(660)


   def _getReport(self):
      log.debug("Weather get report")
      if self.usecity:
         page="http://api.openweathermap.org/data/2.5/weather?q="+str(self.city)
      else:
         page="http://api.openweathermap.org/data/2.5/weather?lat="+str(self.lat)+"&lon="+str(self.lon)+"&mode=json"
      cb=wu.getPage(page, headers={'x-api-key': str(self.owmid)}).addCallbacks(self.onData, self.onError)

   def updateDatabase(self):
      for k in self.data.keys():
         dmdb.setUnique('owm.'+str(k), str(self.data[k]).replace(" ", "."))

   def onData(self, res):
      data = json.loads(res)
      log.info("OpenWeatherMap call resulted in "+str(data))
      try:
         self.data['clouds'] = data[u'clouds'][u'all']
      except:
         self.data['clouds'] = 'unknown'
      try:
         self.data['mmrain'] = data[u'rain'][u'3h']/3
      except:
         self.data['mmrain'] = 'unknown'
      try:
         self.data['pressure'] = data[u'main'][u'pressure']
      except:
         self.data['pressure'] = 'unknown'
      try:
         self.data['temp.min'] = data[u'main'][u'temp_min']-273.15
      except:
         self.data['temp.min'] = 'unknown'
      try:
         self.data['temp.max'] = data[u'main'][u'temp_max']-273.15
      except:
         self.data['temp.max'] = 'unknown'
      try:
         self.data['temp'] = data[u'main'][u'temp']-273.15
      except:
         self.data['temp'] = 'unknown'
      try:
         self.data['humidity'] = data[u'main'][u'humidity']
      except:
         self.data['humidity'] = 'unknown'
      try:
         self.data['wind.speed'] = data[u'wind'][u'speed']
      except:
         self.data['wind.speed'] = 'unknown'
      try:
         self.data['wind.direction '] = data[u'wind'][u'deg']
      except:
         self.data['wind.direction'] = 'unknown'
      try:
         self.data['weather'] = data[u'weather'][0][u'main'].lower()
      except:
         self.data['weather'] = 'unknown'
      try:
         self.data['weather.long'] = data[u'weather'][0][u'description'].lower()
      except:
         self.data['weather.long'] = 'unknown'
      try:
         self.data['mmsnow'] = data[u'snow'][u'3h']/3
      except:
         self.data['mmsnow'] = 'unknown'
      self.updateDatabase()

   def onError(self, res):
      log.warning("OpenWeatherMap Weather call failed!")
      self.data['clouds'] = 'unknown'
      self.data['mmrain'] = 'unknown'
      self.data['pressure'] = 'unknown'
      self.data['temp.min'] = 'unknown'
      self.data['temp.max'] = 'unknown'
      self.data['temp'] = 'unknown'
      self.data['humidity'] = 'unknown'
      self.data['wind.speed'] = 'unknown'
      self.data['wind.direction'] = 'unknown'
      self.data['weather'] = 'unknown'
      self.data['weather.long'] = 'unknown'
      self.data['mmsnow'] = 'unknown'
      self.updateDatabase()

      
