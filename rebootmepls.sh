#!/bin/sh
cd /pace/
export ETCDCTL_API=3
leaderip=`echo $@ | awk '{print $1}'`
myhost=`echo $@ | awk '{print $2}'`
iswait='isreboot'`/pace/etcdget.py $leaderip rebootwait/$myhost`
echo $isreboot | grep pls
if [ $? -ne 0 ];
then
	isreboot='isreboot'`/pace/etcdget.py $leaderip rebootme/$myhost`
	echo $isreboot | grep pls
	if [ $? -eq 0 ];
	then
 		configured=`/pace/etcdget.py $leaderip configured/$myhost`
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
