#!/bin/sh
cd /pace/
export ETCDCTL_API=3
leaderip=`echo $@ | awk '{print $1}'`
myhost=`echo $@ | awk '{print $2}'`
isreboot='isreboot'`/pace/etcdget.py $leaderip rebootme/$myhost`
echo $isreboot | grep pls
if [ $? -eq 0 ];
then
 flag=1
 while [ $flag -ne 0 ];
 do
	sleep 1
 	clusterch='isreboot'`/pace/etcdget.py $leaderip isinsync`
 	echo $clusterch | grep yes
 	flag=$?
 done
 echo $isreboot > /root/rebootmepls
 ./etcdput.py $leaderip rebootme/$myhost donot 
 sleep 5
 /TopStor/resetdocker.sh
 reboot
else
	echo $isreboot ____ no reboot
fi
#/sbin/reboot
