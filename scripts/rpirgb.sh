#!/bin/bash


if [ $# != "2" ] ; then
   echo "Usage:   $0 <hostname> <RGB CODE>"
   echo ""
   echo "Example: $0 localhost \"255,255,255,10\""
   echo "         $0 192.168.4.5 \"white\""
   echo "         $0 192.168.4.5 \"cycle\""
   echo ""
   echo "other than 4 number codes, where first 3 are RGB"
   echo "and 4th is from 0 to 6000 the time in dec of seconds,"
   echo "you can even specify one of those:"
   echo ""
   echo "red, green, blue, yellow, violet, azure, off, white, cycle"
   exit 0
fi

HOST=$1
RGB=$2

if [ -f /usr/bin/screen ] ; then
  WGET="/usr/bin/screen -d -m"
fi
WGET="$WGET $(which wget) --timeout=5 --no-check-certificate -O /dev/null"
WGET="$WGET http://$HOST:9980/?rgb=$RGB"

${WGET} >/dev/null 2>&1

