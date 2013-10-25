#!/bin/bash  


if [ x"$1" = x"stop" ] ; then
   /etc/init.d/zoneminder stop >/dev/null 2>&1
elif [ x"$1" = x"start" ] ; then
   if [ x"$(pgrep -f 'perl.*.zm')" = x"" ] ; then
      kill -9 $(pgrep -f 'perl.*.zm')
   fi
   /etc/init.d/zoneminder start >/dev/null 2>&1
elif [ x"$1" = x"change" ] ; then
   if [ x"$(pgrep -f 'perl.*.zm')" = x"" ] ; then
      /etc/init.d/zoneminder start >/dev/null 2>&1 
   else
      /etc/init.d/zoneminder stop >/dev/null 2>&1
      if [ x"$(pgrep -f 'perl.*.zm')" = x"" ] ; then
         kill -9 $(pgrep -f 'perl.*.zm')
      fi
   fi

fi

chk=$(pgrep -f "perl.*.zm")
if [ x"$chk" != x"" ] ; then
   STATUS="1"
else
   STATUS="0"
fi
echo $STATUS > /home/domotika/Web/resources/zmstatus.txt
