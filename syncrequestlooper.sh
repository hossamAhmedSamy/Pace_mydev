#!/usr/bin/sh
leader=`echo $@ | awk '{print $1}'`
leaderip=`echo $@ | awk '{print $2}'`
myhost=`echo $@ | awk '{print $3}'`
myhostip=`echo $@ | awk '{print $4}'`
syncrequest() {
cd /TopStor
/TopStor/checksyncs.py syncrequest $leader $leaderip $myhost $myhostip 1>/root/syncreq.log 2>/root/syncreqerr.log 
}

while true;
do
 syncrequest() 
 sleep 3 
done

