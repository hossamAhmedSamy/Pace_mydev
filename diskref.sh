#!/usr/bin/sh
# needed the operands to be like : one:two:three:four
#
echo $@ > /root/diskref
leader=`echo $@ | awk '{print $1}'`
leaderip=`echo $@ | awk '{print $2}'`
myhost=`echo $@ | awk '{print $3}'`
myhostip=`echo $@ | awk '{print $4}'`
echo $leader | grep $myhost
if [ $? -eq 0 ];
then
	etcdip=$leaderip
else
	etcdip=$myhostip
fi
/pace/iscsirefresh.sh $etcdip $myhost
