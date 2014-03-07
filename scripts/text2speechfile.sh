#!/bin/bash
#cd `dirname $0`/../domotika/clouds/google

if [[ $# < "3" ]] ; then
   echo "Usage:   $0 <destination file> <language> '<text>'"
   echo ""
   echo "Example: $0 foo.wav it 'prova di trasmissione'"
   echo ""
   exit 0
fi



python `dirname $0`/../domotika/clouds/google/tts.py $1 $2 "${3}"
