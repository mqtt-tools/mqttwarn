#!/bin/sh

. /home/pi/shell/alexa-remote-control/secrets.sh

# Example:
#   echo test from command line | ./announce_stdin -d Living_Room

read message
echo ${message}

env USE_ANNOUNCEMENT_FOR_SPEAK=1 /home/pi/shell/alexa-remote-control/alexa_remote_control.sh ${*} -e speak:"${message}"
