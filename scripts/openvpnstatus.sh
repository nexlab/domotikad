#!/bin/bash
if [ x"$(pgrep -f 'openvpn.*.unixmedia')" != x"" ] ; then
   echo "1"
else 
   echo "0"
fi
