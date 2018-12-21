#!/bin/sh
export ETCDCTL_API=3
cd /TopStor/
theone=` echo $@ | awk '{print $1}'`;
thetwo=` echo $@ | awk '{print $2}'`;
myip=`/sbin/pcs resource show CC | grep Attributes | awk -F'ip=' '{print $2}' | awk '{print $1}'`
./etcdsyncnext.py $myip $theone $thetwo 2>/dev/null
