#!/bin/sh /etc/rc.common
# Script to start mqttwarn as a daemon for OpenWRT

START=95
STOP=10

DIR="/overlay/mosquitto/"
BIN="/overlay/mosquitto/mqttwarn"
PIDFILE=/var/run/mqttwarn.pid
  
start() {        
    echo start
    cd $DIR
    start-stop-daemon -b -S -q -m -p $PIDFILE -x $BIN
}                
                   
stop() {          
    echo stop
    start-stop-daemon -K -q -p $PIDFILE
    rm -f $PIDFILE
}
