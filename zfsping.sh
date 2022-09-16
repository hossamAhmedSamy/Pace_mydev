#!/usr/bin/sh
cd /pace
export ETCDCTL_API=3
ETCDCTL_API=3
echo $$ > /var/run/zfsping.pid
targetcli clearconfig True
targetcli saveconfig
#targetcli restoreconfig /pacedata/targetconfig
#targetcli iscsi/ delete iqn.2016-03.com.${myhost}:data
#targetcli saveconfig
touch /pacedata/perfmon
#/TopStor/logqueueheap.py &
failddisks=''
oldlsscsi='00'
isknown=0
leaderfail=0
ActivePartners=1
partnersync=0
readycount=1
isprimary=0
primtostd=4
toimport=-1
clocker=0
oldclocker=0
clockdiff=0
date=`date`
enpdev='enp0s8'
systemctl restart target
cd /pace
rm -rf /pacedata/addiscsitargets 2>/dev/null
rm -rf /pacedata/startzfsping 2>/dev/null
/pace/startzfs.sh
./fapilooper.sh &
./heartbeatlooper.sh &
zfspingpy(){
./zfsping.py >/root/zfspingpy 2>/root/zfspingpyerr
}
while true;
do
 ./zfsping.py >/root/zfspingpy 2>/root/zfspingpyerr
# zfspingpy
 sleep 1
done
