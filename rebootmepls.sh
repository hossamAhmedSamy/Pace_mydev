#!/bin/sh
cd /pace/
export ETCDCTL_API=3
leaderip=`echo $@ | awk '{print $1}'`
myhost=`echo $@ | awk '{print $2}'`
myhostip=`docker exec etcdclient /TopStor/etcdgetlocal.py clusternodeip`
leader=`docker exec etcdclient /TopStor/etcdgetlocal.py leader`
configuredlocal='S'
isrebootlocal='S'
echo $myhost | grep $leader
if [ $? -ne 0 ];
then
	isrebootlocal='S'`/pace/etcdget.py $myhostip rebootme/$myhost`
 	configuredlocal='S'`/pace/etcdget.py $myhostip configured/$myhost`
fi
isreboot=`/pace/etcdget.py $leaderip rebootme/$myhost`$isrebootlocal

echo $isreboot | grep pls
if [ $? -ne 0 ];
then
	echo S$isreboot | grep pls
	if [ $? -eq 0 ];
	then
 		configured=`/pace/etcdget.py $leaderip configured/$myhost`$configuredlocal
		echo S$configured  | egrep 'yes|reset'
		if [ $? -ne 0 ];
		then
			configured='no'
		fi
 		echo $configured > /root/nodeconfigured
 		./etcdput.py $leaderip rebootme/$myhost donot 
 		/TopStor/resetdocker.sh
 		reboot
	else
		echo $isreboot ____ no reboot
	fi
fi
#/sbin/reboot
