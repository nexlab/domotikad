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

from dmlib import constants as c

IT_REMOVE=[
   "il","la","per","favore","mi","le","tiri","del","della","dell","dei","di","delle","degli","d","de"
]

IT_ACTIONS={
   "su":c.IKAP_ACT_UP, 
   "giu":c.IKAP_ACT_DOWN,
   "apri":c.IKAP_ACT_OPEN,
   "aprire":c.IKAP_ACT_OPEN,
   "aprimi":c.IKAP_ACT_OPEN,
   "chiudi":c.IKAP_ACT_CLOSE,
   "chiudere":c.IKAP_ACT_CLOSE,
   "chiudimi":c.IKAP_ACT_CLOSE,
   "alza":c.IKAP_ACT_UP,
   "alzare":c.IKAP_ACT_UP,
   "alzami":c.IKAP_ACT_UP,
   "abbassa":c.IKAP_ACT_DOWN,
   "abbassare":c.IKAP_ACT_DOWN,
   "abbassami":c.IKAP_ACT_DOWN,
   "accendi":c.IKAP_ACT_ON,
   "accendere":c.IKAP_ACT_ON,
   "spegni":c.IKAP_ACT_OFF,
   "spegnere":c.IKAP_ACT_OFF,
   "accendimi":c.IKAP_ACT_ON,
   "spegnimi":c.IKAP_ACT_OFF,
   "off":c.IKAP_ACT_OFF,
   "on":c.IKAP_ACT_ON,
   "dimmi":c.IKAP_ACT_ASK,
   "dire":c.IKAP_ACT_ASK,
   "stato":c.IKAP_ACT_ASK,
   "attiva":c.IKAP_ACT_ON,
   "attivare":c.IKAP_ACT_ON,
   "disattiva":c.IKAP_ACT_OFF,
   "disattivare":c.IKAP_ACT_OFF,
   "attivami":c.IKAP_ACT_ON,
   "disattivami":c.IKAP_ACT_OFF,
   "esegui":c.IKAP_ACT_START,
   "eseguimi":c.IKAP_ACT_START
}


EN_REMOVE=[

]

EN_ACTIONS=[

]


REMOVE = {
   "it":IT_REMOVE,
   "en":EN_REMOVE
}
ACTIONS = {
   "it":IT_ACTIONS,
   "en":EN_ACTIONS
}
