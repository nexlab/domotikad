#!/bin/bash  
#
# ARGUMENTS:
#
# $1 -> start, update, stop
# $2 -> IP address of the domotikad daemon
# $3 -> type of event (motion only for the moment)
# $4 -> camera name
# $5 -> a string with camera name followed by a list of zones involved in the event, like
#       "CAM1: zone1, zone2", it take only the part after : and expect to find a list of
#       zone names separed by ", " (a comma and a space)
# $6 -> cam path (contain camera stream uri and other info like: rtsp://192.168.1.101/h264 -
# $7 -> monitor id
# $8 -> event id
#
# MYSQL CONFIGURATION:
#
# after using sudo to  permit root execution from the mysql user and add a regular shell
# to mysql user,
# 
# Add UDF sys_eval function to mysql and then:
#
# Add event to mysql zoneminder db with:
#
# delimiter EOF;;
# create trigger zmalarm_start after insert on Events
#    for each row
#       BEGIN
#          declare camname varchar(255);
#          declare campath varchar(255);
#          SELECT Name, Path INTO camname, campath FROM Monitors WHERE Id=NEW.MonitorId;
#          set @zmstart=sys_eval(
#           concat("sudo -u root /home/domotika/scripts/zm_event.sh start localhost ",
#           NEW.Cause, " '", camname, "' '", NEW.Notes, "' '", campath,
#           "' ", NEW.MonitorId, " ", NEW.Id, " ", 0, " ", 0, " ",
#           0, " ", 0, " ", 0, " ", NEW.Width,
#            " ",NEW.Height, " ", 0 ));
#       END;
# EOF;;
# create trigger zmalarm_update after update on Events
#    for each row
#       BEGIN
#         declare camname varchar(255);
#         declare campath varchar(255);
#         IF(NEW.Archived=OLD.Archived AND NEW.Videoed=OLD.Videoed AND NEW.Uploaded=OLD.Uploaded
#          AND NEW.Emailed=OLD.Emailed AND NEW.Messaged=OLD.Messaged AND NEW.Executed=OLD.Executed)
#         THEN
#             SELECT Name, Path INTO camname, campath FROM Monitors WHERE Id=NEW.MonitorId;
#             set @zmstart=sys_eval(
#              concat("sudo -u root /home/domotika/scripts/zm_event.sh update localhost ",
#              NEW.Cause, " '", camname, "' '", NEW.Notes, "' '", campath,
#              "' ", NEW.MonitorId, " ", NEW.Id, " ", NEW.AlarmFrames, " ", NEW.Frames, " ",
#              NEW.TotScore, " ", NEW.AvgScore, " ", NEW.MaxScore, " ", NEW.Width,
#               " ",NEW.Height, " ", NEW.Length ));
#          END IF;
#       END;
# EOF;;
# delimiter ;
#
#
# where localhost is the address of the domotika server that will manage the events
# and assuming that the path of this script is /home/domotika/scripts/
#
# Delete event with:
#
#    drop trigger zm.zmalarm_start;
#    drop trigger zm.zmalarm_update;
#

logger -t "[MOTION DETECTION]" "args: $@"

DBUSER="admin"
DBPASS="domotika"
WEBUSER="admin"
WEBPASS="domotika"

rawurlencode() {
  local string="${1}"
  local strlen=${#string}
  local encoded=""

  for (( pos=0 ; pos<strlen ; pos++ )); do
     c=${string:$pos:1}
     case "$c" in
        [-_.~a-zA-Z0-9] ) o="${c}" ;;
        * )               printf -v o '%%%02x' "'$c"
     esac
     encoded+="${o}"
  done
  echo "${encoded}" 
}

STATUS="${1}"
case ${STATUS} in
   start)
      STATUS=1
      ;;
   update)
      STATUS=2
      if [ x"$(zmu -m ${7} -s -U${DBUSER} -P${DBPASS})" = x"0" ] ; then
         STATUS=4
      fi
      ;;
   stop)
      STATUS=4
      ;;
   *)
      exit 0
esac

TYPE="$(echo ${3} | tr '[:upper:]' '[:lower:]')"
case ${TYPE} in
   motion)
      TYPE=1
      ;;
   *)
      exit 0
esac

CAMNAME="$(rawurlencode ${4})"
ZONES="$(echo ${5} | awk -F ': ' '{print $2}')"

CAMPATH="$(rawurlencode ${6})"
MONITORID=${7}
EVENTID=${8}
ALARMFRAMES=${9}
FRAMES=${10}
TOTSCORE=${11}
AVGSCORE=${12}
MAXSCORE=${13}
WIDTH=${14}
HEIGHT=${15}
LENGTH=${16}


DOMOTIKAD_ADDR="${2}"
if [ -f /usr/bin/screen ] ; then
   WGET="/usr/bin/screen -d -m"
fi
WGET="$WGET $(which wget) --timeout=5 --auth-no-challenge --no-check-certificate -O /dev/null"
WGET="${WGET} https://${WEBUSER}:${WEBPASS}@${DOMOTIKAD_ADDR}/rest/v1.0/motionDetection"
WGET="${WGET}?status=${STATUS}&type=${TYPE}&camera=${CAMNAME}"
WGET="${WGET}&monitorid=${MONITORID}&eventid=${EVENTID}&campath=${CAMPATH}"
WGET="${WGET}&af=${ALARMFRAMES}&f=${FRAMES}&sc=${TOTSCORE}&avg=${AVGSCORE}"
WGET="${WGET}&max=${MAXSCORE}&w=${WIDTH}&h=${HEIGHT}&l=${LENGTH}"


IFS=", "
for z in ${ZONES}
   do
      zone=$(rawurlencode $z)
      WGET="${WGET}&zone=${zone}"
      logger -t "[MOTION EVENT]" "${WGET}"
      ${WGET} >/dev/null 2>&1
   done

exit 0
