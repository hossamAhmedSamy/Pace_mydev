#!/bin/sh
export PATH=/bin:/usr/bin:/sbin:/usr/sbin:/root
myhost=`hostname -s `
thehost=`echo $@ | awk '{print $1}'`
#declare -a disks=(`lsscsi -i | grep $thehost | awk '{print $6" "$7}'`);
declare -a disks=`lsscsi -i | grep $thehost | awk '{print $6" "$7}'`;
echo "${disks[@]}"
echo $@ > /root/losthostparam
echo "${disks[@]}" > /root/losthost
echo pdisks=` echo "${disks[@]}" | awk '{print $1}' | awk -F'/' '{print $NF}' `
echo pdisks="${pdisks[@]}" >> /root/losthost
echo  "${disks[@]}" | while read l;
do
   dis=`echo $l | awk '{print $1}'  | awk -F'/' '{print $3}'`
   echo 1 > /sys/block/$dis/device/delete 2>/dev/null
   echo echo 1 \> /sys/block/$dis/device/delete >> /root/hostlost
done
echo disks="${disks[@]}" >> /root/hostlosttmp
echo "${disks[@]}" | awk '{print $2}'  | while read l;
do
 echo checking disk $l >> /root/hostlosttmp
 ETCDCTL_API=3 /pace/changeop.py $myhost scsi-$l 
done
echo udpating database >> /root/hostlosttmp
#ETCDCTL_API=3 /pace/etcdget.py pools --prefix | grep "\/$thehost" | grep "\/${myhost}" > /TopStordata/forlocalpools
ETCDCTL_API=3 /pace/etcddellocal.py known/$thehost  --prefix
ETCDCTL_API=3 /pace/importnxtlocalpools.py $myhost $thehost 
ETCDCTL_API=3 /pace/etcddellocal.py hosts/$thehost  --prefix
ETCDCTL_API=3 /pace/etcddellocal.py prop/$thehost
