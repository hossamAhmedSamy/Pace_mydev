#!/usr/bin/sh
cd /pace
myhost=`hostname`
myhostip=`docker exec etcdclient /TopStor/etcdgetlocal.py clusternodeip`
while true
do
	./etcdput.py 10.11.11.253 possible/$myhost $myhostip 2>/dev/null
	clusterip=`./etcdget.py 10.11.11.253 tojoin/$myhost`
	clusteripn=`echo $clusterip | wc -c`
	if [ $clusteripn -ge 6 ];
	then
		break
	fi
	echo ./etcdput.py 10.11.11.253 possible/$myhost $myhostip
	sleep 3
done
echo will join the cluster $clusterip
echo yes > /root/nodeconfigured
nmcli conn mod mycluster ipv4.addresses $clusterip 
./etcddel.py 10.11.11.253 possible/$myhost
/TopStor/docker_setup.sh reboot
