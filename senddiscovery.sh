#!/usr/bin/sh
cd /pace
myhost=`hostname`
myhostip=`docker exec etcdclient /TopStor/etcdgetlocal.py clusternodeip`
while true
do
	./etcdput.py 10.11.11.253 possible/$myhost $myhostip 2>/dev/null
	echo ./etcdput.py 10.11.11.253 possible/$myhost $myhostip
	sleep 3
done
