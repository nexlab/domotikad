#!/bin/bash
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

### BEGIN INIT INFO
# Provides:          domotikad
# Required-Start:    $syslog $remote_fs mysql
# Required-Stop:     $syslog $remote_fs
# X-Interactive:  yes
# Should-Start:      $network 
# Should-Stop:       $network 
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start and stop Domotika
# Description:       Domotika is an home automation system
### END INIT INFO

#if [ -f /usr/lib/bindhack.so ] ; then
#   export LD_PRELOAD=/usr/lib/bindhack.so
#   export BIND_SRC=192.168.181.1
#fi

cd /home/domotika
./domotikad $@ 
if [ x"$1" = x"stop" ] ; then
   chk=$(pgrep "domotikad")
   if [ x"$chk" != x"" ] ; then
      kill -9 $chk >/dev/null 2>&1 
   fi
fi
exit 0