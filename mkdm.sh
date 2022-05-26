#!/bin/sh
echo $@ > /root/mkdm
raid=`echo $@ | awk '{print $1}'`
host=`echo $@ | awk '{print $2}'`
dmsetup create $raid  --table '0 195312500000000 zero'
dmsuff=`ls -lisah /dev/disk/by-id/dm-name-$raid | awk -F'/dm' '{print $NF}'`
echo $host and $raid and $dmsuff >> /root/mkdm
./etcdput.py dm/$host/$raid dm$dmsuff
./broadcasttolocal.py dm/$host/$raid dm$dmsuff
