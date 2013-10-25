#!/bin/bash
CFILE="/home/domotika/conf/domotikad.conf"
DBNAME=`cat ${CFILE} | grep dmdbname | cut -f 2 -d ":" | sed -e"s/ //g"`
DBHOST=`cat ${CFILE} | grep dbhost | cut -f 2 -d ":" | sed -e"s/ //g"`
DBUSER=`cat ${CFILE} | grep dbuser | cut -f 2 -d ":" | sed -e"s/ //g"`
DBPASS=`cat ${CFILE} | grep dbpass | cut -f 2 -d ":" | sed -e"s/ //g"`

query="select distinct(inpname) from inpstatus WHERE status=0 and (inpname like 'contattofinestra%' or inpname like 'portablindata%')"
res=$(echo `mysql -u$DBUSER -p$DBPASS --batch --skip-column-names -e"$query" $DBNAME` )
if [ x"$res" != x"" ] ; then
   echo $res
fi

