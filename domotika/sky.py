import ephem
from datetime import datetime, date, timedelta
from datetime import time as dtime
import calendar, time

class DMSun(object):

   def __init__(self, lat, lon, elev):

      #Make an observer
      self.obs = ephem.Observer()
      self.setObsDate()
      
      self.obs.lon  = str(lon) #Note that lon should be in string format
      self.obs.lat  = str(lat)      #Note that lat should be in string format
      self.obs.elev = float(elev)

      #To get U.S. Naval Astronomical Almanac values, use these settings
      self.obs.pressure= 0

   def setObsDate(self):
      # detect utf offset
      diff = round((datetime.now()-datetime.utcnow()).total_seconds())
   
      self.today = date.today()
      # midnight of today
      utcmidnight = datetime.combine(date.today(), dtime(0,0,0))+timedelta(seconds=int(diff))
      self.obs.date =str(utcmidnight)

   def getReal(self):
      if self.today != date.today():
         self.setObsDate()
      now = time.time()
      self.obs.horizon = '-0:34'
      sunrise=self.obs.previous_rising(ephem.Sun()) #Sunrise
      sunrise_ts = calendar.timegm(sunrise.datetime().utctimetuple())
      sunset = self.obs.next_setting(ephem.Sun()) #Sunset
      sunset_ts = calendar.timegm(sunset.datetime().utctimetuple())
      dayreal = 0
      if now > sunrise_ts and now < sunset_ts:
         dayreal = 1
      return {'status':dayreal, 'start':(ephem.localtime(sunrise), sunrise_ts), 'stop':(ephem.localtime(sunset), sunset_ts)}

   def getMax(self):
      if self.today != date.today():
         self.setObsDate()
      now = time.time()
      self.obs.horizon = '-0:34'
      sunrise=self.obs.previous_rising(ephem.Sun()) #Sunrise
      sunrise_ts = calendar.timegm(sunrise.datetime().utctimetuple())
      noon   =self.obs.next_transit(ephem.Sun(), start=sunrise) #Solar noon
      daymax_ts = calendar.timegm(noon.datetime().utctimetuple())
      daymax = 0
      if now > daymax_ts-1800 and now < daymax_ts+1800:
         daymax = 1
      return {'status':daymax, 'start':(ephem.localtime(noon)-timedelta(seconds=1800), daymax_ts-1800), 
               'stop':(ephem.localtime(noon)+timedelta(seconds=1800), daymax_ts+1800)}

   def getCivil(self):
      if self.today != date.today():
         self.setObsDate()
      now = time.time()
      self.obs.horizon = '-6'
      beg_civil_twilight=self.obs.previous_rising(ephem.Sun(), use_center=True) #Begin civil twilight
      beg_civil_twilight_ts = calendar.timegm(beg_civil_twilight.datetime().utctimetuple())
      end_civil_twilight=self.obs.next_setting(ephem.Sun(), use_center=True) #End civil twilight
      end_civil_twilight_ts = calendar.timegm(end_civil_twilight.datetime().utctimetuple())
      daycivil = 0
      if now > beg_civil_twilight_ts and now < end_civil_twilight_ts:
         daycivil = 1
      return {'status':daycivil, 'start':(ephem.localtime(beg_civil_twilight), beg_civil_twilight_ts),  
               'stop':(ephem.localtime(end_civil_twilight), end_civil_twilight_ts)}


   def getAstro(self):
      if self.today != date.today():
         self.setObsDate()
      now = time.time()
      self.obs.horizon = '-18'
      beg_astro_twilight=self.obs.previous_rising(ephem.Sun(), use_center=True) #Begin civil twilight
      beg_astro_twilight_ts=calendar.timegm(beg_astro_twilight.datetime().utctimetuple())
      end_astro_twilight=self.obs.next_setting(ephem.Sun(), use_center=True) #End civil twilight
      end_astro_twilight_ts=calendar.timegm(end_astro_twilight.datetime().utctimetuple())
      dayastro = 0
      if now > beg_astro_twilight_ts and now < end_astro_twilight_ts:
         dayastro = 1

      return {'status':dayastro, 'start':(ephem.localtime(beg_astro_twilight), beg_astro_twilight_ts),  
               'stop':(ephem.localtime(end_astro_twilight), end_astro_twilight_ts)}


if __name__ == '__main__':
   d=DMSun('45.4636889', '9.1881408', 122.246513 )
   r=d.getReal()
   print 'REAL', r['status'], r['start'][0], '('+str(r['start'][1])+')', r['stop'][0], '('+str(r['stop'][1])+')'
   r=d.getMax()
   print 'MAX', r['status'], r['start'][0], '('+str(r['start'][1])+')', r['stop'][0], '('+str(r['stop'][1])+')'
   r=d.getCivil()
   print 'CIVIL', r['status'], r['start'][0], '('+str(r['start'][1])+')', r['stop'][0], '('+str(r['stop'][1])+')'
   r=d.getAstro()
   print 'ASTRO', r['status'], r['start'][0], '('+str(r['start'][1])+')', r['stop'][0], '('+str(r['stop'][1])+')'

