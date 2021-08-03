#!/bin/sh
result='nothing'
n=1
ipbase=''
for x in $( echo $1 | sed 's/\./ /g')
do
 n=$((n+1))
 if [ $n -gt 4 ]
 then
  break
 fi
 ipbase=${ipbase}$x'.' 
done
for x in {3..254}
do
 ip=${ipbase}$x
 checking=`nmap --max-rtt-timeout 20ms -p 2378 $ip `
 echo $checking | grep open 1>/dev/null
 if [ $? -eq 0 ];
 then
  result=$ipbase`echo $checking | awk -F"$ipbase" '{print $2}' | awk -F')' '{print $1}'`
  break
 fi
done
echo $result
