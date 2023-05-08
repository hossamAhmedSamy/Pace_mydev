#!/bin/sh
echo $@ > /root/leaderlost
cd /pace
leader=`echo $@ | awk '{print $1}'`
leaderip=`echo $@ | awk '{print $2}'`
myhost=`echo $@ | awk '{print $3}'`
myhostip=`echo $@ | awk '{print $4}'`
myip=$myhostip
nextlead=`echo $@ | awk '{print $5}'`
nextleadip=`echo $@ | awk '{print $6}'`
clusterip=`echo $@ | awk '{print $7}'`
losthost=`echo $@ | awk '{print $8}'`
enpdev='enp0s8'

rm -rf /etc/chrony.conf
cp /TopStor/chrony.conf /etc/
sed -i "s/MASTERSERVER/$nextleadip/g" /etc/chrony.conf
systemctl restart chronyd
echo $myhost | grep $nextlead 
if [ $? -ne 0 ];
then
  echo leader is dead but another process was in the way to fix.  >> /root/zfspingtmp2
  echo leader is dead but another process was in the way to fix.
  exit
fi
echo /TopStor/docker_primary.sh $leader $myhostip $leaderip $clusterip
/TopStor/docker_primary.sh $leader $myhostip $leaderip $clusterip
echo docker exec etcdclient /TopStor/logmsg.py Partst05 info system $myhost 
docker exec etcdclient /TopStor/logmsg.py Partst05 info system $myhost 
echo $perfmon | grep 1
if [ $? -eq 0 ]; then
 docker exec etcdclient /TopStor/logqueue.py AddingMePrimary start system 
fi
stamp=`date +%s%N`
docker exec etcdclient /TopStor/logmsg.py Partst02 warning system $losthost
/pace/etcddel.py $leaderip sync/leader/Add --prefix
/pace/etcdput.py $leaderip sync/leader/Add_${myhost}_$myip/request leader_$stamp
/pace/etcdput.py $leaderip sync/leader/Add_${myhost}_$myip/request/$myhost leader_$stamp
#/pace/etcddel.py $leaderip toimport/$myhost 
docker exec etcdclient /TopStor/etcdput.py etcd refreshdisown/$myhost yes
