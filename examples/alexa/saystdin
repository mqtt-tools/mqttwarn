#!/bin/sh

. /home/pi/shell/alexa-remote-control/secrets.sh

# Example:
#   echo test from command line | ./saystdin -d Speaker_Group

read message
echo ${message}

/home/pi/shell/alexa-remote-control/alexa_remote_control_plain.sh ${*} -e speak:"${message}"
