#!/bin/sh
cd /pace
echo $@ `date` > /root/hostlost
#export PATH=/bin:/usr/bin:/sbin:/usr/sbin:/root
leader=`echo $@ | awk '{print $1}'`
leaderip=`echo $@ | awk '{print $2}'`
myhost=`echo $@ | awk '{print $3}'`
myhostip=`echo $@ | awk '{print $4}'`
thehost=`echo $@ | awk '{print $5}'`
echo $leader | grep $myhost
if [ $? -eq 0 ];
then
	etcdip=$leaderip
else
	etcdip=$myhostip
fi
echo /pace/etcdget.py $etcdip ready --prefix \| grep $thehost
/pace/etcdget.py $etcdip ready --prefix | grep $thehost
if [ $? -ne 0 ];
then
 echo slslslslslslsl
 #exit
fi
echo hihihihi
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
 ETCDCTL_API=3 /pace/changeop.py $leader $leaderip $etcdip $myhost $myhostip scsi-$l 
done
echo udpating database >> /root/hostlosttmp
/pace/etcddel.py $etcdip ready $thehost
