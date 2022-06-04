#!/bin/sh
echo $@ > /root/leaderlost
leader=`echo $@ | awk '{print $1}'`
myhost=`echo $@ | awk '{print $2}'`
leaderip=`echo $@ | awk '{print $3}'`
myip=`echo $@ | awk '{print $4}'`
echo leader is dead..  > /root/zfspingtmp2
leaderfail=1
./etcdgetlocal.py $myip known --prefix | wc -l | grep 1
if [ $? -eq 0 ];
then
 /TopStor/logmsglocal.py $myip Partst05 info system $myhost &
fi
echo getting my nextlead
nextleadip=`ETCDCTL_API=3 ./etcdgetlocal.py $myip nextlead` 
echo nextlead is $nextleadip  >> /root/zfspingtmp2
echo $nextleadip | grep $myip
if [ $? -eq 0 ];
then
 echo next lead is $nextleadip , $nextlead and this is me
 echo $perfmon | grep 1
 if [ $? -eq 0 ]; then
  /TopStor/logqueuelocal.py $myip AddingMePrimary start system 
 fi
 echo prepare the registry 
 stamp=`date +%s%N`
 ./etcddellocal.py $myip leader --prefix  
 ./etcdputlocal.py $myip leader/$myhost $myip 
 ./etcdputlocal.py $myip sync/leader/$myhost $stamp 
# ./broadcasttolocal.py sync/leader/$myhost $stamp 
 stamp=`date +%s%N`
 ./etcdputlocal.py $myip ready/$myhost $myip  
 ./etcddellocal.py $myip ready $leader  
 stamp=`date +%s%N`
 ./etcddellocal.py $myip known $myhost  
 /TopStor/logmsglocal.py $myip Partst02 warning system $leaderall 
 exit
 echo hostlostlocal getting all my pools from $leader >> /root/zfspingtmp2
 ETCDCTL_API=3 /pace/hostlostlocal.sh $leader $myip $leaderip
 systemctl stop etcd 2>/dev/null
 clusterip=`cat /pacedata/clusterip`
 echo starting primary etcd with namespace >> /root/zfspingtmp2
 ./etccluster.py 'new' $myip 2>/dev/null
 chmod +r /etc/etcd/etcd.conf.yml
 systemctl daemon-reload 2>/dev/null
 systemctl start etcd 2>/dev/null
 ionice -c2 -n0 -p `pgrep etcd`
 while true;
 do
  echo starting etcd=$?
  systemctl status etcd
  if [ $? -eq 0 ];
  then
   break
  else
   sleep 1
  fi
 done
 ./runningetcdnodes.py $myip 2>/dev/null
 ./etcdput.py sync/ready/$myhost $stamp 
 ./etcdput.py sync/known/$myhost $stamp 
 ./etcdput.py tosync/$myhost $myip  
 echo adding me as a leader >> /root/zfspingtmpa2
 rm -rf /etc/chrony.conf
 cp /TopStor/chrony.conf /etc/
 sed -i '/MASTERSERVER/,+1 d' /etc/chrony.conf
 echo creating namespaces >>/root/zfspingtmp2
 ./setnamespace.py $enpdev &
 ./setdataip.py &
 echo created namespaces >>/root/zfspingtmp2
 echo importing all pools >> /root/zfspingtmp2
 ./etcddel.py toimport/$myhost &
 toimport=1
 #/sbin/zpool import -am &>/dev/null
 echo running putzpool and nfs >> /root/zfspingtmp2
 pgrep putzpool 
 if [ $? -ne 0 ];
 then
  /pace/putzpool.py 2 $isprimary $primtostd  &
  /TopStor/HostgetIPs
 fi
 pgrep activeusers 
 if [ $? -ne 0 ];
 then
  /pace/activeusers.py   &
 fi
 chgrp apache /var/www/html/des20/Data/* 2>/dev/null
 chmod g+r /var/www/html/des20/Data/* 2>/dev/null
 runningcluster=1
 leader=$myhost
 echo $perfmon | grep 1
 if [ $? -eq 0 ]; then
  /TopStor/logqueue.py AddinMePrimary stop system 
 fi
else
 ETCDCTL_API=3 /pace/hostlostlocal.sh $leader $myip $leaderip
 systemctl stop etcd 2>/dev/null 
 echo starting waiting for new leader run >> /root/zfspingtmp2
 waiting=1
 result='nothing'
 while [ $waiting -eq 1 ]
 do
  echo still looping for new leader run >> /root/zfspingtmp2
  echo $result | grep nothing 
  if [ $? -eq 0 ];
  then
   sleep 1 
   result=`ETCDCTL_API=3 ./nodesearch.py $myip 2>/dev/null`
  else
   ./runningetcdnodes.py $myip 2>/dev/null
   echo $perfmon | grep 1
   if [ $? -eq 0 ]; then
    /TopStor/logqueue.py AddingtoOtherleader start system 
   fi
   echo found the new leader run $result >> /root/zfspingtmp2
   waiting=0
   /pace/syncthtistoleader.py $myip pools/ $myhost
   /pace/syncthtistoleader.py $myip volumes/ $myhost
   /pace/etcdput.py ready/$myhost $myip
   /pace/etcdput.py tosync/$myhost $myip
   /TopStor/broadcast.py SyncHosts /TopStor/pump.sh addhost.py 
   leaderall=` ./etcdget.py leader --prefix `
   leader=`echo $leaderall | awk -F'/' '{print $2}' | awk -F"'" '{print $1}'`
   leaderip=` ./etcdget.py leader/$leader `
   rm -rf /etc/chrony.conf
   cp /TopStor/chrony.conf /etc/
   sed -i "s/MASTERSERVER/$leaderip/g" /etc/chrony.conf
   systemctl restart chronyd
   echo $perfmon | grep 1
   if [ $? -eq 0 ]; then
    /TopStor/logqueue.py AddingtoOtherleader start system 
   fi
  fi
 done 
 leader=`./etcdget.py leader --prefix | awk -F'/' '{print $2}' | awk -F"'" '{print $1}'`
 continue
fi
 
