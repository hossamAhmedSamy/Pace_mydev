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
#declare -a disks=(`lsscsi -i | grep $thehost | awk '{print $6" "$7}'`);
#/pace/etcddel.py $etcdip pool $thehost
#/pace/etcddel.py $etcdip vol $thehost
#/pace/etcddel.py $etcdip need $thehost
#/pace/etcddel.py $etcdip hosts $thehost
#/pace/etcddel.py $etcdip lists $thehost
#/pace/etcddel.py $etcdip next $thehost
#/pace/etcdput.py $etcdip tosync yes 
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
#ETCDCTL_API=3 /pace/etcdget.py pools --prefix | grep "\/$thehost" | grep "\/${myhost}" > /TopStordata/forlocalpools
#ETCDCTL_API=3 /pace/etcddel.py $etcdip ipaddr $thehost 
#ETCDCTL_API=3 /pace/importlocalpools.py $leaderip $myhost $etcdip $thehost 
#ETCDCTL_API=3 /pace/etcddel.py $leaderip hosts/$thehost  --prefix
#ETCDCTL_API=3 /pace/etcddel.py $leaderip prop/$thehost
#ETCDCTL_API=3 /pace/etcdput.py $leaderip losthost/$thehost `date +%s` 
#ETCDCTL_API=3 /pace/etcddel.py $leaderip cannot  --prefix
#ETCDCTL_API=3 /pace/etcddel.py $leaderip oldhosts/$thehost  --prefix
#ETCDCTL_API=3 /pace/putzpool.py 
#stamp=`date +%s`
#/pace/etcddel.py $leaderip sync/ready _${thehost}
# /pace/etcdput.py $leaderip sync/ready/Del_${thehost}_--prefix/request ready_$stamp
# /pace/etcdput.py $leaderip sync/ready/Del_${thehost}_--prefix/request/$myhost ready_$stamp
 #/pace/etcdput.py $leaderip sync/hostdown/hostdown.sh_${thehost}_--prefix/request hostdown_$stamp
 #/pace/etcdput.py $leaderip sync/hostdown/hostdown.sh_${thehost}_--prefix/request/$myhost hostdown_$stamp
# /pace/etcddel.py $leaderip sync/volumes _${thehost}
# /pace/etcdput.py $leaderip sync/volumes/Del_${thehost}_--prefix/request/$myhost volumes_$stamp
# /pace/etcdput.py $leaderip sync/volumes/Del_${thehost}_--prefix/request volumes_$stamp
# /pace/etcddel.py $leaderip sync/pools _${thehost}
# /pace/etcdput.py $leaderip sync/pools/Del_${thehost}_--prefix/request/$myhost pools_$stamp
# /pace/etcdput.py $leaderip sync/pools/Del_${thehost}_--prefix/request pools_$stamp
# /pace/etcddel.py $leaderip sync/poolnxt _${thehost}
# /pace/etcdput.py $leaderip sync/poolnxt/Del_${thehost}_--prefix/request/$myhost poolnxt_$stamp
# /pace/etcdput.py $leaderip sync/poolnxt/Del_${thehost}_--prefix/request poolnxt_$stamp

#echo  it is done >> /root/ostlosttmp
#ETCDCTL_API=3 /pace/etcddel.py $leaderip sync/ready $thehost 
#ETCDCTL_API=3 /pace/etcddel.py $etcdip ready $thehost 
#/pace/etcddel.py $leaderip sync/dirty --prefix
#/pace/etcdput.py $leaderip sync/dirty/____/request  dirty_$stamp
