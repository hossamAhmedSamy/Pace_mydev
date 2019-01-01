#!/usr/bin/sh
cd /pace
export ETCDCTL_API=3
ETCDCTL_API=3
echo $$ > /var/run/zfsping.pid
targetcli clearconfig True
targetcli saveconfig
targetcli restoreconfig /pacedata/targetconfig
targetcli saveconfig
failddisks=''
isknown=0
leaderfail=0
isprimary=0
primtostd=4
toimport=-1
clocker=0
oldclocker=0
clockdiff=0
date=`date`
enpdev='enp0s8'
echo $date >> /root/zfspingstart
systemctl restart target
cd /pace
rm -rf /pacedata/addiscsitargets 2>/dev/null
rm -rf /pacedata/startzfsping 2>/dev/null
while [ ! -f /pacedata/startzfsping ];
do
 sleep 1;
 echo cannot run now > /root/zfspingtmp
done
echo startzfs run >> /root/zfspingtmp
/pace/startzfs.sh
leadername=` ./etcdget.py leader --prefix | awk -F'/' '{print $2}' | awk -F"'" '{print $1}'`
date=`date `
myhost=`hostname -s`
myip=`/sbin/pcs resource show CC | grep Attributes | awk -F'ip=' '{print $2}' | awk '{print $1}'`
echo starting in $date >> /root/zfspingtmp
while true;
do
 sleep 5
 needlocal=0
 runningcluster=0
 echo check if I primary etcd >> /root/zfspingtmp
 netstat -ant | grep 2379 | grep LISTEN &>/dev/null
 if [ $? -eq 0 ]; 
 then
  echo I am primary etcd,isprimary:$isprimary >> /root/zfspingtmp
  if [[ $isprimary -le 10 ]];
  then
   isprimary=$((isprimary+1))
  fi
  if [[ $primtostd -le 10 ]];
  then
   primtostd=$((primtostd+1))
  fi
  if [ $primtostd -eq 3 ];
  then
   /TopStor/logmsg.py Partsu05 info system $myhost
   primtostd=$((primtostd+1))
  fi
  if [ $isprimary -eq 3 ];
  then
   echo for $isprimary sending info Partsu03 booted with ip >> /root/zfspingtmp
   #targetcli clearconfig True
   #targetcli saveconfig
   #targetcli restoreconfig /pacedata/targetconfig
   /pace/etcdput.py ready/$myhost $myip
   touch /pacedata/addiscsitargets 
   pgrep putzpool 
   if [ $? -ne 0 ];
   then
    /pace/putzpool.py 1 $isprimary $primtostd  &
   fi
   ./etcddel.py toimport/$myhost
   toimport=2
  fi
  runningcluster=1
  echo checking leader record \(it should be me\)  >> /root/zfspingtmp
  leaderall=` ./etcdget.py leader --prefix 2>/dev/null`
  if [[ -z $leaderall ]]; 
  then
   echo no leader although I am primary node >> /root/zfspingtmp
   ./runningetcdnodes.py $myip 2>/dev/null
   ./etcddel.py leader --prefix 2>/dev/null &
   ./etcdput.py leader/$myhost $myip 2>/dev/null &
  fi
  echo adding known from list of possbiles >> /root/zfspingtmp
   pgrep  addknown 
   if [ $? -ne 0 ];
   then
    ./addknown.py 2>/dev/null & 
   fi
 else
  echo I am not a primary etcd.. heartbeating leader >> /root/zfspingtmp
  leaderall=` ./etcdget.py leader --prefix 2>&1`
  echo $leaderall | grep Error  &>/dev/null
  if [ $? -eq 0 ];
  then
   echo leader is dead..  >> /root/zfspingtmp
   leaderfail=1
   ./etcdgetlocal.py $myip known --prefix | wc -l | grep 1
   if [ $? -eq 0 ];
   then
    /TopStor/logmsg.py Partst05 info system $myhost &
    primtostd=0;
   fi
   ETCDCTL_API=3 /pace/etcdgetlocal.py $myip poolsnxt --prefix | grep ${myhost} > /TopStordata/forlocalpools
   #ETCDCTL_API=3 /TopStor/importlocalpools.py  &
   ETCDCTL_API=3 /TopStor/hostlostdeadleader.sh $leadername  &
   nextleadip=`ETCDCTL_API=3 ./etcdgetlocal.py $myip nextlead` 
   echo nextlead is $nextleadip  >> /root/zfspingtmp
   echo $nextleadip | grep $myip
   if [ $? -eq 0 ];
   then
    systemctl stop etcd 2>/dev/null
    clusterip=`cat /pacedata/clusterip`
    echo starting primary etcd with namespace >> /root/zfspingtmp
    ./etccluster.py 'new' $myip 2>/dev/null
    chmod +r /etc/etcd/etcd.conf.yml
    systemctl daemon-reload 2>/dev/null
    systemctl start etcd 2>/dev/null
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
   #./etcdput.py clusterip $clusterip 2>/dev/null
   #pcs resource create clusterip ocf:heartbeat:IPaddr nic="$enpdev" ip=$clusterip cidr_netmask=24 2>/dev/null
    echo adding me as a leader >> /root/zfspingtmp
    ./runningetcdnodes.py $myip 2>/dev/null
    ./etcddel.py leader 2>/dev/null &
    ./etcdput.py leader/$myhost $myip 2>/dev/null &
    /TopStor/logmsg.py Partst02 warning system $leaderall &
    echo creating namespaces >>/root/zfspingtmp
    ./setnamespace.py $enpdev &
    ./setdataip.py &
    echo created namespaces >>/root/zfspingtmp
   # systemctl restart smb 2>/dev/null &
    echo importing all pools >> /root/zfspingtmp
    ./etcddel.py toimport/$myhost &
    toimport=1
    #/sbin/zpool import -am &>/dev/null
    echo running putzpool and nfs >> /root/zfspingtmp
    pgrep putzpool 
    if [ $? -ne 0 ];
    then
     /pace/putzpool.py 2 $isprimary $primtostd  &
    fi
    systemctl status nfs 
    if [ $? -ne 0 ];
    then
     systemctl start nfs 2>/dev/null
    fi
    chgrp apache /var/www/html/des20/Data/* 2>/dev/null
    chmod g+r /var/www/html/des20/Data/* 2>/dev/null
    runningcluster=1
    leadername=$myhost
   else
    systemctl stop etcd 2>/dev/null 
    echo starting waiting for new leader run >> /root/zfspingtmp
    waiting=1
    result='nothing'
    while [ $waiting -eq 1 ]
    do
     echo still looping for new leader run >> /root/zfspingtmp
     echo $result | grep nothing 
     if [ $? -eq 0 ];
     then
      sleep 1 
      result=`ETCDCTL_API=3 ./nodesearch.py $myip 2>/dev/null`
     else
      echo found the new leader run $result >> /root/zfspingtmp
      waiting=0
     fi
    done 
    leadername=`./etcdget.py leader --prefix | awk -F'/' '{print $2}' | awk -F"'" '{print $1}'`
    continue
   fi
  else 
   echo I am not primary.. checking if I am local etcd>> /root/zfspingtmp
   netstat -ant | grep 2378 | grep $myip | grep LISTEN &>/dev/null
   if [ $? -ne 0 ];
   then
    echo I need to be local etcd .. no etcd is running>> /root/zfspingtmp
    needlocal=1
   else
    echo local etcd is already running>> /root/zfspingtmp
    needlocal=2
   fi
   echo checking if I am known host >> /root/zfspingtmp
   known=` ./etcdget.py known --prefix 2>/dev/null`
   echo $known | grep $myhost  &>/dev/null
   if [ $? -ne 0 ];
   then
    echo I am not a known adding me as possible >> /root/zfspingtmp
    ./etcdput.py possible$myhost $myip 2>/dev/null &
   else
    echo I am known so running all needed etcd task:boradcast,isknown:$isknown >> /root/zfspingtmp
    if [[ $isknown -eq 0 ]];
    then
     echo running sendhost.py $leaderip 'user' 'recvreq' $myhost >>/root/tmp2
     leaderall=` ./etcdget.py leader --prefix `
     leader=`echo $leaderall | awk -F'/' '{print $2}' | awk -F"'" '{print $1}'`
     leaderip=`echo $leaderall | awk -F"')" '{print $1}' | awk -F", '" '{print $2}'`
     #/pace/sendhost.py $leaderip 'user' 'recvreq' $myhost &
     /pace/etcdsync.py $myip pools pools 2>/dev/null
     /pace/etcdsync.py $myip poolsnxt poolsnext 2>/dev/null
     /pace/etcdsync.py $myip nextlead nextlead 2>/dev/null
     /pace/sendhost.py $leaderip 'cifs' 'recvreq' $myhost &
     /pace/sendhost.py $leaderip 'logall' 'recvreq' $myhost &
     isknown=$((isknown+1))
    fi
    if [[ $isknown -le 10 ]];
    then
     isknown=$((isknown+1))
    fi
    if [[ $isknown -eq 3 ]];
    then
     /pace/etcdput.py ready/$myhost $myip &
     #targetcli clearconfig True
     #targetcli saveconfig
     #targetcli restoreconfig /pacedata/targetconfig
     touch /pacedata/addiscsitargets 
   ./etcddel.py toimport/$myhost &
     toimport=1
    fi
    echo finish running tasks task:boradcast, log..etc >> /root/zfspingtmp
   fi
  fi 
 fi
 pgrep putzpool 
 if [ $? -ne 0 ];
 then
  /pace/putzpool.py 3 $isprimary $primtostd  &
 fi
 echo checking if I need to run local etcd >> /root/zfspingtmp
 if [[ $needlocal -eq 1 ]];
 then
  echo start the local etcd >> /root/zfspingtmp
  ./etccluster.py 'local' $myip 2>/dev/null
  chmod +r /etc/etcd/etcd.conf.yml
  systemctl daemon-reload
  systemctl stop etcd 2>/dev/null
  systemctl start etcd 2>/dev/null
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
  leaderall=` ./etcdget.py leader --prefix `
  leader=`echo $leaderall | awk -F'/' '{print $2}' | awk -F"'" '{print $1}'`
  leaderip=`echo $leaderall | awk -F"')" '{print $1}' | awk -F", '" '{print $2}'`
  ./etcdsync.py $myip primary primary 2>/dev/null &
  ./etcddellocal.py $myip known --prefix 2>/dev/null &
  ./etcddellocal.py $myip localrun --prefix 2>/dev/null &
  ./etcddellocal.py $myip run --prefix 2>/dev/null &
  ./etcdsync.py $myip known known 2>/dev/null &
  ./etcdsync.py $myip localrun localrun 2>/dev/null &
  ./etcdsync.py $myip leader known 2>/dev/null &
#   ./etcddellocal.py $myip known/$myhost --prefix 2>/dev/null
  echo done and exit >> /root/zfspingtmp
  continue 
 fi
 if [[ $needlocal -eq  2 ]];
 then
  echo I am already local etcd running iscsirefresh on $myip $myhost  >> /root/zfspingtmp
  pgrep iscsiwatchdog
  if [ $? -ne 0 ];
  then
   /pace/iscsiwatchdog.sh $myip $myhost $leader 2>/dev/null &
  fi
 fi
 echo checking if still in the start initcron is still running  >> /root/zfspingtmp
 if [ -f /pacedata/forzfsping ];
 then
  echo Yes. so I have to exit >> /root/zfspingtmp
  continue
 fi
 echo No. so checking  I am primary >> /root/zfspingtmp
 if [[ $runningcluster -eq 1 ]];
 then
  echo Yes I am primary so will check for known hosts >> /root/zfspingtmp
   pgrep  addknown 
   if [ $? -ne 0 ];
   then
    ./addknown.py 2>/dev/null & 
   fi
   pgrep  selectimport 
   if [ $? -ne 0 ];
   then
    /TopStor/selectimport.py $myhost &
   fi
 fi 
 echo toimport = $toimport >> /root/zfspingtmp
 
 if [ $toimport -gt 0 ];
 then
  ETCDCTL_API=3 /pace/etcdget.py toimport/$myhost 
  mytoimport=`ETCDCTL_API=3 /pace/etcdget.py toimport/$myhost`
  if [ $mytoimport == '-1' ]; then 
   echo Yes  I have no record in toimport/$myhost even no nothing=$mytoimport >> /root/zfspingtmp
  fi
  echo $mytoimport | grep nothing
  if [ $? -eq 0 ];
  then
   echo it is nothing , toimport=$toimport >> /root/zfspingtmp
   if [ $toimport -eq 1 ];
   then
    if [ $leaderfail -eq 0 ];
    then
     /TopStor/logmsg.py Partsu04 info system $myhost $myip &
     ./etcddel.py cann --prefix 2>/dev/null &
    else
     leaderfail=0
    fi
   fi
   if [ $toimport -eq 2 ];
   then
    if [ $leaderfail -eq 0 ];
    then
     /TopStor/logmsg.py Partsu03 info system $myhost $myip &
     ./etcddel.py cann --prefix 2>/dev/null &
    else
     leaderfail=0
    fi
     
   fi
   if [ $toimport -eq 3 ];
   then
    /TopStor/logmsg.py Partsu06 info system &
   fi
   toimport=0
   oldclocker=$clocker
  else
   echo checking zpool to import>> /root/zfspingtmp
   pgrep  zpooltoimport 
   if [ $? -ne 0 ];
   then
    /TopStor/zpooltoimport.py all &
   fi
  fi
 fi
 if [ $toimport -eq 0 ];
 then
  clocker=`date +%s`
  clockdiff=$((clocker-oldclocker))
 fi
 echo Clockdiff = $clockdiff >> /root/zfspingtmp
 if [ $clockdiff -ge 50 ];
 then
  ./etcddel.py toimport/$myhost &
  /TopStor/logmsg.py Partst06 info system  &
  toimport=3
  oldclocker=$clocker
  clockdiff=0
 fi
 pgrep iscsiwatchdog
 if [ $? -ne 0 ];
 then
  /pace/iscsiwatchdog.sh 2>/dev/null  &
 fi
  echo Collecting a change in system occured >> /root/zfspingtmp
 #/pace/changeop.py hosts/$myhost/current d
   pgrep  changeop 
   if [ $? -ne 0 ];
   then
    ETCDCTL_API=3 /pace/changeop.py $myhost &
   fi
   pgrep  selectspare 
   if [ $? -ne 0 ];
   then
    ETCDCTL_API=3 /pace/selectspare.py $myhost &
   fi
done
