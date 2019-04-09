#!/bin/bash
source /etc/profile
DIR="/root/javamonitor"
JAR="client-0.0.3.RELEASE.jar"

case "$1" in
    start)
    echo "Starting ... "
    nohup java -jar $DIR/$JAR > $DIR/client.log 2>&1 &
    ;;
    stop)
    echo "Shutting down ... "
    /bin/ps -ef | grep $JAR | grep -v grep | awk '{print $2}' | xargs kill -9
    ;;
    restart)
    $0 stop
    sleep 3
    $0 start
    ;;
    *)
    echo "Usage: $0 {start|stop|restart}"
    exit 1
    ;;
esac