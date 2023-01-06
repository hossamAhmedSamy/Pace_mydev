#!/usr/bin/sh
leaderip=`echo $@ | awk '{print $1}'`
myhost=`echo $@ | awk '{print $2}'`
rebootme() {
 /pace/rebootmepls.sh $leaderip $myhost 
}

while true;
do
 rebootme 
 sleep 3 
done

