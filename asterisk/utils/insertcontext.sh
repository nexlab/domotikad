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

if [ x"$1" = x"" ] || [ x"$2" = x"" ] || [ ! -f $2 ]; then
   echo "syntax: $0 <context name> <file.dialplan>"
   exit 0
fi
CFILE="/home/domotika/conf/domotikad.conf"
DBNAME=`cat ${CFILE} | grep dmdbname | cut -f 2 -d ":" | sed -e"s/ //g"`
DBHOST=`cat ${CFILE} | grep dbhost | cut -f 2 -d ":" | sed -e"s/ //g"`
DBUSER=`cat ${CFILE} | grep dbuser | cut -f 2 -d ":" | sed -e"s/ //g"`
DBPASS=`cat ${CFILE} | grep dbpass | cut -f 2 -d ":" | sed -e"s/ //g"`
MYSQL="mysql --batch --raw --column-names=FALSE -u$DBUSER -p$DBPASS -h$DBHOST"
context=${1}
query="delete from voip_dialplan where context='$context'"
$MYSQL -e"$query" $DBNAME
#IFS="=>"
pos=1
while read -r extenline
do
   extencheck=`echo $extenline | awk -F '=>' '{print $1}'` 
   exten=`echo $extenline | awk -F '=>' '{print $2}'`
   check=`echo $extencheck | sed -e's/exten\ /exten/g'`
   ext=`echo $exten | sed -e's/^\ *//g'`
   if [ x"$check" = x"exten" ] ; then
      extension=`echo $ext | awk -F ',' '{print $1}'`
      priority=`echo $ext | awk -F ',' '{print $2}'`
      app=`echo $ext |cut -d',' -f 3-`
      query="insert into voip_dialplan  (position,context,extension,priority,astcommand)
               VALUES ('$pos','$context','$extension','$priority','$app')"
      mysql --batch --raw --column-names=FALSE -u$DBUSER -p$DBPASS -h$DBHOST -e"$query" $DBNAME
      pos=$(( $pos+1 ))
   fi
done < "${2}"
