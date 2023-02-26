#!/usr/bin/sh
:q
cd /pace/
lsscsi=0
#dmesg -n 1
rabbitip=`echo $@ | awk '{print $1}'`
myhost=`echo $@ | awk '{print $2}'`
#echo start >> /root/iscsiwatch
targetn=0
initip=1
initstamp=`date +%s`
echo $initstamp > /TopStordata/initstamp
echo $initstamp 
/pace/syncrequestlooper.sh $rabbitip & disown
/pace/fapilooper.sh & disown
/pace/zfsping.py $rabbitip $myhost & disown
/pace/rebootmeplslooper.sh $rabbitip $myhost & disown
isinitn=`cat /root/nodeconfigured`'s'
echo $isinitn | grep 'yess'
if [ $? -ne 0 ];
then
 /pace/senddiscovery.sh & disown
fi
while true;
do
	lsscsinew=`lsscsi -is | wc -c `
	cd /pace
	if [ $lsscsinew -ne $lsscsi ];
	then
		lsscsi=$lsscsinew
		./addtargetdisks.sh $rabbitip
		./iscsirefresh.sh
		./listingtargets.sh $rabbitip
		/TopStor/etcdput.py $rabbitip dirty/pool 0
	fi
	cd /TopStor
	pgrep topstorrecvrep
	if [ $? -ne 0 ];
	then
 		./topstorrecvreply.py $rabbitip & disown
	fi
	targetnewn=`targetcli ls | wc -c`
	if [ $targetnewn -ne $targetn ];
	then
		targetn=$targetnewn
		lsscsi=0

	fi
        /pace/putzpool.py $rabbitip
	if [ $initip -eq 1 ];
	then
		stamp=`date +%s`
		stamp=$((stamp+300))
		nmcli conn mod cmynode +ipv4.addresses 10.11.11.254/24
		nmcli conn up cmynode
		./httpdflask.sh $rabbitip yes
		initip=2
	fi
	if [ $initip -eq 2 ];
	then
		stamp2=`date +%s`
		if [ $stamp2 -ge $stamp ];
		then
			nmcli conn mod cmynode -ipv4.addresses 10.11.11.254/24
			nmcli conn up cmynode
			./httpdflask.sh $rabbitip no 
			initip=0
		fi
	fi

	echo sleeeeeeeeeeeeeping
	sleep 2
	echo cyclingggggggggggggg
done
exit
#echo finished start of iscsirefresh  > /root/iscsiwatch
sh /pace/listingtargets.sh
   
#echo finished listingtargets >> /root/iscsiwatch
#echo updating iscsitargets >> /root/iscsiwatch
sh /pace/addtargetdisks.sh
sh /pace/disklost.sh
sh /pace/addtargetdisks.sh
ETCDCTL_API=3 /pace/putzpool.py 
lsscsi2=`lsscsi -is | wc -c `
/pace/selectspare.py

#pgrep checkfrstnode -a
#if [ $? -ne 0 ];
#then
# /pace/frstnodecheck.py
#fi
/usr/bin/chronyc -a makestep
rebootstatus='thestatus'`cat /TopStordata/rebootstatus`
echo $rebootstatus | grep finish >/dev/null
if [ $? -ne 0 ];
then
 /TopStor/rebootme `cat /TopStordata/rebootstatus`  2>/root/rebooterr
fi
