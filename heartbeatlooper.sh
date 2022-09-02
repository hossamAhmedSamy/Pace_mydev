#!/usr/bin/sh
hearbeat () {
cd /pace
/pace/hearbeat.py 
}
while true;
do
 heartbeat 
 sleep 1 
done

