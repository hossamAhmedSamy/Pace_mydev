#!/usr/bin/sh
cd /pace
myhost=`hostname`
myhostip=`docker exec etcdclient /TopStor/etcdgetlocal.py clusternodeip`
while true
do
	clusterip=`./etcdput.py 10.11.11.253 possible/$myhost $myhostip`
	#clusterip=`./etcdget.py 10.11.11.253 tojoin/$myhost`
	echo $clusterip | grep 'not reach'
	if [ $? -ne 0 ];
	then
		break
	fi
	echo ./etcdput.py 10.11.11.253 possible/$myhost $myhostip
	sleep 3
done
echo will join the cluster $clusterip
echo yes_fromsenddtarget > /root/nodeconfigured
nmcli conn mod mycluster ipv4.addresses $clusterip 
./etcddel.py 10.11.11.253 possible/$myhost
/TopStor/docker_setup.sh reboot
