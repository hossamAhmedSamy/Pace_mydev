#!/bin/sh
echo $@ > /root/mkdm
raid=`echo $@ | awk '{print $1}'`
host=`echo $@ | awk '{print $2}'`
dmname=${raid}$RANDOM
dmsetup create $dmname  --table '0 195312500000000 zero'
 
dmsuff=`ls -lisah /dev/disk/by-id/dm-name-$dmname | awk -F'/dm' '{print $NF}'`
echo $host and $raid and $dmsuff >> /root/mkdm
./etcdput.py dm/$host/$dmname dm$dmsuff
./broadcasttolocal.py dm/$host/$dmname dm$dmsuff
echo 'dm'$dmsuff
