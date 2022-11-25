#!/usr/bin/sh
leaderip=`echo $@ | awk '{print $1}'`
syncrequest() {
cd /pace
/pace/checksyncs.py syncrequest $leaderip  1>/root/syncreq.log 2>/root/syncreqerr.log 
}

while true 
do
 syncrequest
 sleep 2 
done

