#!/bin/bash
myhost=`docker exec etcdclient /TopStor/etcdgetlocal.py clusternode`
leader=`docker exec etcdclient /TopStor/etcdgetlocal.py leader`
echo $myhost | grep $leader  >/dev/null
if [ $? -eq 0 ];
then
	$@
fi
