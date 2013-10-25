#!/bin/bash 
CFILE="/home/domotika/conf/domotikad.conf"
DBNAME=`cat ${CFILE} | grep dmdbname | cut -f 2 -d ":" | sed -e"s/ //g"`
DBHOST=`cat ${CFILE} | grep dbhost | cut -f 2 -d ":" | sed -e"s/ //g"`
DBUSER=`cat ${CFILE} | grep dbuser | cut -f 2 -d ":" | sed -e"s/ //g"`
DBPASS=`cat ${CFILE} | grep dbpass | cut -f 2 -d ":" | sed -e"s/ //g"`
TIMERID="1"
MODE="STATUS"

if [ x"$1" = x"" ] ; then
   echo "Usage: $0 <ON|OFF|CHANGE|STATUS> <timerid>"
   exit 0
fi 
if [ x"$2" != x"" ] ; then
   TIMERID=$2 
fi 
MODE=$1
case "$MODE" in
   "ON")
      res=$(echo `mysql -u$DBUSER -p$DBPASS -e"UPDATE timers SET active=1 WHERE id=$TIMERID" $DBNAME`)
      ;;
   "OFF")
      res=$(echo `mysql -u$DBUSER -p$DBPASS -e"UPDATE timers SET active=0 WHERE id=$TIMERID" $DBNAME`)
      ;;
   "STATUS")
      res=$(echo `mysql -u$DBUSER -p$DBPASS -e"SELECT active FROM timers WHERE id=$TIMERID" $DBNAME` | awk '{print $2}')
      if [ x"$res" == x"1" ] ; then
         echo "1"
      else
         echo "0"
      fi 
      ;; 
   "CHANGE")
     res=$(echo `mysql -u$DBUSER -p$DBPASS -e"SELECT active FROM timers WHERE id=$TIMERID" $DBNAME` | awk '{print $2}')
     if [ x"$res" == x"1" ] ; then
        res=$(echo `mysql -u$DBUSER -p$DBPASS -e"UPDATE timers SET active=0 WHERE id=$TIMERID" $DBNAME`)
     else
        res=$(echo `mysql -u$DBUSER -p$DBPASS -e"UPDATE timers SET active=1 WHERE id=$TIMERID" $DBNAME`)
     fi 
     ;; 
   *)
      echo "Usage: $0 <ON|OFF|CHANGE|STATUS> <timerid>"
      exit 0
esac  

