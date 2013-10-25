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

CFILE="/home/domotika/conf/domotikad.conf"
DBNAME=`cat ${CFILE} | grep dmdbname | cut -f 2 -d ":" | sed -e"s/ //g"`
DBHOST=`cat ${CFILE} | grep dbhost | cut -f 2 -d ":" | sed -e"s/ //g"`
DBUSER=`cat ${CFILE} | grep dbuser | cut -f 2 -d ":" | sed -e"s/ //g"`
DBPASS=`cat ${CFILE} | grep dbpass | cut -f 2 -d ":" | sed -e"s/ //g"`

QUERY="SELECT * FROM voip_trunks WHERE active=1\G"
mysql --batch --raw --column-names=TRUE -u$DBUSER -p$DBPASS -h$DBHOST -e"$QUERY" $DBNAME | while IFS= read -r ROW
do
   res=`echo $ROW | sed -e 's/: /=/g' | grep -v NULL`
   for i in $res
   do
      name=`echo $i | awk -F '=' '{print $1}'`
      val=`echo $i | awk -F '=' '{print $2}'`
      if [ x"$name" = x"allow" ] || [ x"$name" = x"disallow" ] ; then
         for a in `echo $val | cut -f 1- --output-delimiter=" "  -d ","`
         do
            echo $name=$a
         done
      elif [ x"$name" = x"name" ] ; then
         echo
         echo "[$val]"
      elif [ x"$name" != x"id" ] && [ x"$val" != x"" ] && [ x"$name" != x"active" ] ; then
         echo $name=$val 
      fi

   done
   #echo $res
done
