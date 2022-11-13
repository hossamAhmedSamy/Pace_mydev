#!/usr/bin/sh
cd /pace
sessions='sessions'`/sbin/iscsiadm -m session --rescan `
needrescan=0;
myhost=`hostname -s`
mycluster=`nmcli conn show mycluster | grep ipv4.addresses | awk '{print $2}' | awk -F'/' '{print $1}'`
hosts=`docker exec etcdclient /TopStor/etcdget.py $mycluster ready --prefix | awk -F"', " '{print $2}' | awk -F"'" '{print $2}'`
for host in $hosts ; do
 echo $sessions  | grep $host
 if [ $? -ne 0 ]; then
  echo sessions=$sessions
  needrescan=1;
  #hostpath=`ls /var/lib/iscsi/nodes/ | grep "$host"`;
  echo /sbin/iscsiadm -m discovery --portal ${host}:3266 --type sendtargets \| grep $myhost \| awk \'{print \$2}\'
  hostiqn=`/sbin/iscsiadm -m discovery --portal ${host}:3266 --type sendtargets | grep $myhost | awk '{print $2}'`
  echo hostiqn=$hostiqn
  /sbin/iscsiadm -m node --targetname $hostiqn --portal ${host}:3266 -u
  echo /sbin/iscsiadm -m node --targetname $hostiqn --portal ${host}:3266 -l
  /sbin/iscsiadm -m node --targetname $hostiqn --portal ${host}:3266 -l
  fi
done
sleep 2
