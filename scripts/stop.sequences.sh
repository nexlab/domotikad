#!/bin/bash
CFILE="/home/domotika/conf/domotikad.conf"

DBNAME=`cat ${CFILE} | grep dmdbname | cut -f 2 -d "=" | sed -e"s/ //g"`
DBHOST=`cat ${CFILE} | grep dbhost | cut -f 2 -d "=" | sed -e"s/ //g"`
DBUSER=`cat ${CFILE} | grep dbuser | cut -f 2 -d "=" | sed -e"s/ //g"`
DBPASS=`cat ${CFILE} | grep dbpass | cut -f 2 -d "=" | sed -e"s/ //g"`


if [ "$#" == "0" ] ; then
   echo "$0 <seq_id> [seq_id] [seq_id] ..."
   exit 0
fi

for seq in $@ 
do
   /usr/bin/mysql -u$DBUSER -p$DBPASS -e"UPDATE sequence_data SET step_done='1' WHERE seq_id='$seq'" $DBNAME
done
