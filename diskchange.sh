#!/usr/bin/sh
mypid='/TopStordata/diskchange'
touch $mypid
mypidc=`cat $mypid`
stamp=`date `
echo $@ | grep remove
if [ $? -eq 0 ];
then
	echo $2 | grep dhcp 
	if [ $? -ne 0 ];
	then
		echo dev=$2
		dev=`echo $2 | sed 's/[0-9]*//g'`
		targetcli backstores/block delete $dev-$myhost
		if [ $? -eq 0 ];
		then
			actualdev=`lsscsi | grep $dev-$myhost | awk '{print $NF}' | sed 's/\/dev\///g'`
		else
			actualdev=$dev
		fi
	else
		dev=$2
		actualdev=`lsscsi | grep $dev | awk '{print $NF}' | sed 's/\/dev\///g'`
	fi	
	echo 1 > /sys/block/$actualdev/device/delete
fi
echo $mypidc | grep start
if [ $? -eq 0 ];
then
	echo hihihihi
	echo $1 $2 $3 $RANDOM > $mypid
	echo disk not running $@ $stamp >> /root/diskchange 
	exit
fi
echo sssssssssssssssssssssssssssssssss
oldpid=`echo $mypidc | awk '{print $4}'`
echo $@ | grep -w $oldpid
if [ $? -eq 0 ];
then 
	echo hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh $oldpid ,,,,,,,,,,,,$@
	mypidc='stop'
else
	echo $mypidc | grep stop
	if [ $? -ne 0 ];
	then
		exit
	fi
fi
echo $mypidc | grep stop
if [ $? -eq 0 ];
then
	echo start start start start > $mypid
	docker exec etcdclient ls
	if [ $? -eq 0 ];
	then
		echo disk start diskref $@ $stamp > /root/diskchange 
		leader=`docker exec etcdclient /TopStor/etcdgetlocal.py leader`
		leaderip=`docker exec etcdclient /TopStor/etcdgetlocal.py leaderip`
		myhost=`docker exec etcdclient /TopStor/etcdgetlocal.py clusternode`
		myhostip=`docker exec etcdclient /TopStor/etcdgetlocal.py clusternodeip`
			
		#echo $@ | grep remove
		#if [ $? -eq 0 ];
		#then
	#		echo $2 | grep dhcp 
#			if [ $? -ne 0 ];
#			then
#				echo dev=$2
#				dev=`echo $2 | sed 's/[0-9]*//g'`
#				targetcli backstores/block delete $dev-$myhost
#				if [ $? -eq 0 ];
#				then
#					actualdev=`lsscsi | grep $dev-$myhost | awk '{print $NF}' | sed 's/\/dev\///g'`
#				else
#					actualdev=$dev
#				fi
#			else
#				dev=$2
#				actualdev=`lsscsi | grep $dev | awk '{print $NF}' | sed 's/\/dev\///g'`
#			fi	
#			echo 1 > /sys/block/$actualdev/device/delete
#		fi
		/pace/diskref.sh $leader $leaderip $myhost $myhostip
		echo $@ |  grep -v checksync
		if [ $? -eq 0 ];
		then	
			stampi=`date +%s`
			/TopStor/etcdput.py $leaderip sync/diskref/${2}-${myhost}_${3}______/request diskref_$stampi
			/TopStor/etcdput.py $leaderip sync/diskref/${2}-${myhost}_${3}______/request/$myhost diskref_$stampi
		fi
	#/pace/diskref.sh $leader $leaderip $myhost $myhostip
	#else
		#echo disk change $@ $stamp >> /root/diskchange 
	fi
fi
mypidc=`cat $mypid`
echo $mypidc | grep start
if [ $? -eq 0 ];
then
	echo disk stopped $@ $stamp >> /root/diskchange 
	echo stop stop stop stop > $mypid
	exit
fi
echo $mypidc | grep stop
if [ $? -eq 0 ];
then
	echo disk found a stop, it is stopped $@ $stamp >> /root/diskchange 
	exit
fi

newpid=`echo $mypidc | awk '{print $4}'`
echo $@ | grep -w $newpid
if [ $? -eq 0 ];
then
	echo disk stopped $@ $stamp >> /root/diskchange 
	echo stop stop stop stop> $mypid
	exit
fi
echo /pace/diskchange.sh  $mypidc 
/pace/diskchange.sh  $mypidc 

