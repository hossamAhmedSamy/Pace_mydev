#!/bin/sh
x=`pgrep iscsiwatchdog | grep -v $$ |  wc -l`
if [ $x -gt 1 ];
then
 exit
fi
dmesg -n 1
if [[ "$#" -eq 0 ]];
then
 islocal=0
else
 islocal=1
 myip=`echo $@ | awk '{print $1}'`
 myhost=`echo $@ | awk '{print $2}'`
 leader=`echo $@ | awk '{print $3}'`
fi

systemctl status etcd &>/dev/null
if [ $? -eq 0 ];
then
# systemctl restart target &>/dev/null
# systemctl restart iscsi &>/dev/null
 echo start >> /root/iscsiwatch
 if [ -f /pacedata/addiscsitargets ];
 then
  sh /pace/iscsirefresh.sh
  echo finished start of iscsirefresh  > /root/iscsiwatch
# sh /pace/listingtargets.sh
  echo finished listingtargets >> /root/iscsiwatch
  echo updating iscsitargets >> /root/iscsiwatch
  sh /pace/addtargetdisks.sh
  echo finished updtating iscsitargets >> /root/iscsiwatch
 else
  echo cannot add new iscsi targets at the moment >> /root/iscsiwatch
 fi
 if [[ $islocal -eq 0 ]];
 then
  echo putzpool to leader >> /root/zfspingtmp
  echo putzpool to leader hi="$#" >> /root/iscsiwatch
  ETCDCTL_API=3 /pace/putzpool.py isciwatchversion &
  echo finished putzpool to leader hi="$#" >> /root/iscsiwatch
 else
  echo putzpool local $myip $myhost $islocal >> /root/zfspingtmp
  echo putzpool local $myip $myhost $islocal >> /root/iscsiwatch
#  ETCDCTL_API=3 /pace/putzpoollocal.py $myip $myhost $leader
 fi
fi
