#!/bin/sh
cd /pace
echo $@ > /root/hostdown

host=`echo $@ | awk '{print $1}'`
leader=`docker exec etcdclient /TopStor/etcdgetlocal.py leader`
leaderip=`docker exec etcdclient /TopStor/etcdgetlocal.py leaderip`
myhost=`docker exec etcdclient /TopStor/etcdgetlocal.py clusternode`
myhostip=`docker exec etcdclient /TopStor/etcdgetlocal.py clusternodeip`
/pace/hostlost.sh $leader $leaderip $myhost $myhostip $host
