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

from twisted.web import client
from zope.interface import implements
from twisted import cred
import twisted.cred.portal
import twisted.cred.credentials
import twisted.cred.checkers
import twisted.cred.error
import logging
from twisted.internet import defer
try:
   import hashlib
   md5 = hashlib
   md5.new = hashlib.md5
   sha1 = hashlib.sha1
except:
   import md5
   import sha1

from dmlib.utils import genutils


log = logging.getLogger("Webgui")

class mindFactory(object):

   loginsaved = False

   def __init__(self, request, credential):
      self.request = request
      self.credential = credential
      self.args = self.request.args



class clientAuth(object):

   implements(cred.checkers.ICredentialsChecker)

   credentialInterfaces = (
      cred.credentials.IUsernamePassword,
   )

   def __init__(self):
      pass

   def checkAuth(self, usr, pwd):
      log.debug("CheckAuth for "+str(usr)+" "+str(pwd))
      return self.core.getAuth(usr, genutils.hashPwd(pwd))
      
   def getAuth(self, usr, pwd):
      log.debug("getAuth for "+str(usr)+" "+str(pwd))
      return self.checkAuth(usr, pwd).addCallback(self.getPerms, pwd)

   def getPerms(self, res, pwd):
      log.info("getPerms "+str(res))
      """
      if len(res) > 0:
         if res[0].admin == True:
            perms['admin'] = True
         return perms
      """
      if len(res) > 0:
         perms = res[0]
         perms.loginpwd = pwd
         return perms
      return False

   def requestAvatarId(self, c):
      log.debug('AUTH: '+str(c))
      return self.checkAuth(c.username, c.password).addCallback(
         self.getPerms, c.password).addCallback(
         self.AvatarResults, c)

   def AvatarResults(self, res, c):
      log.debug("AvatarResults "+str(res)+" "+str(c))
      if res:
         return defer.succeed([c, res])
      raise cred.error.UnauthorizedLogin()
