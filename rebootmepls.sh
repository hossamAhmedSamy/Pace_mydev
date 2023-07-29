#!/bin/sh
cd /pace/
export ETCDCTL_API=3
leaderip=`echo $@ | awk '{print $1}'`
myhost=`echo $@ | awk '{print $2}'`
myhostip=`docker exec etcdclient /TopStor/etcdgetlocal.py clusternodeip`
leader=`docker exec etcdclient /TopStor/etcdgetlocal.py leader`
iswait='isreboot'`/pace/etcdget.py $leaderip rebootwait/$myhost`
echo $isreboot | grep pls
if [ $? -ne 0 ];
then
	isreboot='isreboot'`/pace/etcdget.py $leaderip rebootme/$myhost`
	echo $myhost | grep $leader
	if [ $? -eq 0 ];
	then
		isrebootlocal='isreboot'`/pace/etcdget.py $myhostip rebootme/$myhost`
 		configuredlocal=`/pace/etcdget.py $myhostip configured/$myhost`
	fi
	echo ${isreboot}$isrebootlocal | grep pls
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
