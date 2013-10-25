#!/bin/bash
CFILE="/home/domotika/conf/domotikad.conf"
DBNAME=`cat ${CFILE} | grep dmdbname | cut -f 2 -d ":" | sed -e"s/ //g"`
DBHOST=`cat ${CFILE} | grep dbhost | cut -f 2 -d ":" | sed -e"s/ //g"`
DBUSER=`cat ${CFILE} | grep dbuser | cut -f 2 -d ":" | sed -e"s/ //g"`
DBPASS=`cat ${CFILE} | grep dbpass | cut -f 2 -d ":" | sed -e"s/ //g"`


CMD="SYSTEM /home/domotika/scripts/start_stop_timer.sh"
query="select id from timers"
res=$(echo `mysql -u$DBUSER -p$DBPASS --batch --skip-column-names -e"$query" $DBNAME` )
if [ x"$res" != x"" ] ; then
   for timerid in $res ; do
      query="select timer_name from timers WHERE id='$timerid'"
      timer=$(echo `mysql -u$DBUSER -p$DBPASS --batch --skip-column-names -e"$query" $DBNAME` )
      query="insert into actions (execute,command,websection,button_name,status) 
      VALUES (1,'$CMD CHANGE $timerid','timers','$timer','$CMD STATUS $timerid')"
      echo $query
      ins=$(echo `mysql -u$DBUSER -p$DBPASS --batch --skip-column-names -e"$query" $DBNAME` )
      echo $timerid $timer
   done
fi

