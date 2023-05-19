#!/bin/sh
cd /pace/
export ETCDCTL_API=3
leaderip=`echo $@ | awk '{print $1}'`
myhost=`echo $@ | awk '{print $2}'`
isreboot=isreboot`/pace/etcdget.py $leaderip rebootme/$myhost`
echo $isreboot | grep pls
if [ $? -eq 0 ];
then
  echo $isreboot > /root/rebootmepls
 ./etcdput.py $leaderip rebootme/$myhost donot 
 sleep 5
 /TopStor/resetdocker.sh
 reboot
fi
#/sbin/reboot
