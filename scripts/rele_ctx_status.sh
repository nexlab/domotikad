#!/bin/bash 
CFILE="/home/domotika/conf/domotikad.conf"

DBNAME=`cat ${CFILE} | grep dmdbname | cut -f 2 -d ":" | sed -e"s/ //g"`
DBHOST=`cat ${CFILE} | grep dbhost | cut -f 2 -d ":" | sed -e"s/ //g"`
DBUSER=`cat ${CFILE} | grep dbuser | cut -f 2 -d ":" | sed -e"s/ //g"`
DBPASS=`cat ${CFILE} | grep dbpass | cut -f 2 -d ":" | sed -e"s/ //g"`
CTX="1"
MODE="ON"

if [ x"$1" = x"" ] ; then
   echo "Usage: $0 <ON|OFF> <ctx>"
   exit 0
fi

if [ x"$2" != x"" ] ; then
   CTX=$2
fi

if [ x"$1" = x"OFF" ] ; then
   MODE="OFF"
fi 

res=$(echo `mysql -u$DBUSER -p$DBPASS -e"SELECT COUNT(id) FROM relstatus WHERE ctx=$CTX AND status=1" $DBNAME`  | awk '{print $2}')
if [ x"$res" == x"0" ] ; then
   # sono spenti tutti i rele
   if [ "$MODE" = "ON" ] ; then
      echo "0"
   else
      echo "1"
   fi
else
   res2=$(echo `mysql -u$DBUSER -p$DBPASS -e"SELECT COUNT(id) FROM relstatus WHERE ctx=$CTX AND status=0" $DBNAME`  | awk '{print $2}')
   if [ x"$res2" == x"0" ] ; then
      # sono accesi tutti
      if [ "$MODE" = "ON" ] ; then
         echo "1"
      else
         echo "0"
      fi
   else
      echo "-1"
   fi
fi
