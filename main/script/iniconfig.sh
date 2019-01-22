#!/bin/bash

joblog=`cat /usr/local/nginx/conf/sites-e*/joblog.conf | grep alias | grep -v "#"`
if [ $? != 0 ];then
    joblog=`cat /usr/local/nginx/conf/sites-a*/joblog.conf | grep alias | grep -v "#"`
fi
logpath=`echo $joblog | awk '{print $2}' | awk -F ";" '{print $1}' | sed 's/.$//'`
appname=$1
apppath="/root/gceasy/$appname"
gclogdir=$logpath/gclog/$appname
[ $gclogdir ] && mkdir -p $gclogdir
opts="JAVA_OPTS=\"-server -Xms2g -Xmx4g -XX:NewSize=1g -XX:MaxNewSize=1g -XX:PermSize=256m -XX:MaxPermSize=256m -XX:SurvivorRatio=1 -XX:+DisableExplicitGC -XX:+UseParNewGC -XX:+CMSParallelRemarkEnabled -XX:+UseConcMarkSweepGC -XX:-OmitStackTraceInFastThrow -Xloggc:$gclogdir/java-gc.log -XX:CMSInitiatingOccupancyFraction=70 -XX:+UseCMSInitiatingOccupancyOnly -XX:+UseCMSCompactAtFullCollection -XX:CMSFullGCsBeforeCompaction=1 -XX:+PrintGCDetails -XX:+PrintGCDateStamps -XX:+PrintGCApplicationStoppedTime -verbose:GC -XX:+PrintHeapAtGC -XX:+PrintTenuringDistribution\""

shpath="/usr/local/$appname/bin/catalina.sh"
if [[ -z `grep "Xloggc" $shpath` ]];then
    sed -i "3a\\$opts" $shpath
fi
gclogpath=`awk '/Xloggc/ {print}' $shpath | awk -F "-Xloggc:" '{print $2}' | awk '{print $1}'`
echo $gclogpath > $apppath/iniconfig.log

confpath="$apppath/logpath.conf"
if [[ -z `grep "path" $confpath` ]];then
    echo "path=$gclogpath" >> $confpath
else
    sed -i "s!^path.*!path=$gclogpath!" $confpath
fi

cat $confpath >> $apppath/iniconfig.log

echo "1 3 * * * /usr/bin/python $apppath/sendmail.py >> $apppath/crontab.log" >> /var/spool/cron/root
/etc/init.d/crond reload > /dev/null 2>&1