#!/bin/bash 
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

CFILE="/home/domotika/conf/domotikad.conf"
DBNAME=`cat ${CFILE} | grep dmdbname | cut -f 2 -d ":" | sed -e"s/ //g"`
DBHOST=`cat ${CFILE} | grep dbhost | cut -f 2 -d ":" | sed -e"s/ //g"`
DBUSER=`cat ${CFILE} | grep dbuser | cut -f 2 -d ":" | sed -e"s/ //g"`
DBPASS=`cat ${CFILE} | grep dbpass | cut -f 2 -d ":" | sed -e"s/ //g"`
EXTHOST=`cat ${CFILE} | grep sip_externhost | cut -f 2 -d ":" | sed -e"s/ //g"`
EXTADDR=`cat ${CFILE} | grep sip_externaddr | cut -f 2 -d ":" | sed -e"s/ //g"`
LOCALNET=`cat ${CFILE} | grep sip_localnet | cut -f 2 -d ":" | sed -e"s/ //g"`

if [ x"$EXTHOST" != x"" ] ; then
   echo "externhost=$EXTHOST"
fi
if [ x"$EXTADDR" != x"" ] ; then
   echo "externaddr=$EXTADDR"
fi
if [ x"$LOCALNET" != x"" ] ; then
   echo "localnet=$LOCALNET"
fi


