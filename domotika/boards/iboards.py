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


class IDMBoards(Interface):
   """ Base plugin Interface """
   
   def getBoard(self, host, port, pwd, lang):
      """
         Return a DMBoard object
      """
 

class IBoard(Interface):
   """ Implement a Board """
  
class IBoardAnalog(Interface):
   """ implement the Analog Device interface """

class IBoardInput(Interface):
   """ implement the Digital Input interface """

class IBoardOutput(Interface):
   """ implement an Output device """

class IBoardRelay(Interface):
   """ implement a relay interface """

class IBoardPWM(Interface):
   """ implement a PWM Interface """

def context2section(ctx):
   if int(ctx) in C.SECTIONS.keys():
      section=C.SECTIONS[int(ctx)]
   else:
      section="none"

   return section



