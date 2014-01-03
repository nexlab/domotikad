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

import logging
from dmlib import constants as C
from zope.interface import implements
import iboards

log = logging.getLogger( 'Core' )



def context2section(ctx):
   if int(ctx) in C.SECTIONS.keys():
      section=C.SECTIONS[int(ctx)]
   else:
      section="none"

   return section


class BaseBoard(object):
   """ """
   implements(iboards.IBoard)

   analist = False
   inplist = False
   rellist = False
   outlist = False
   hasAnalogs = False
   hasOutputs = False
   hasInputs = False
   hasPWMs = False
   hasRelays = False


class BoardAnalog(object):
   """ """
   implements(iboards.IBoardAnalog)

class BoardInput(object):
   """ """
   implements(iboards.IBoardInput)

class BoardOutput(object):
   """ """
   implements(iboards.IBoardOutput)

class BoardRelay(object):
   """ """
   implements(iboards.IBoardRelay)

class BoardPWM(object):
   """ """
   implements(iboards.IBoardPWM)  
