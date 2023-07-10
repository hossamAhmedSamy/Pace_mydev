#!/bin/sh
cd /pace/
export ETCDCTL_API=3
leaderip=`echo $@ | awk '{print $1}'`
myhost=`echo $@ | awk '{print $2}'`
isreboot='isreboot'`/pace/etcdget.py $leaderip rebootme/$myhost`
echo $isreboot | grep pls
if [ $? -eq 0 ];
then
 configured=`/pace/etcdget.py $leaderip configured/$myhost`
 echo $configured > /root/nodeconfigured
 ./etcdput.py $leaderip rebootme/$myhost donot 
 sleep 5
 /TopStor/resetdocker.sh
 reboot
else
	echo $isreboot ____ no reboot
fi
#/sbin/reboot
