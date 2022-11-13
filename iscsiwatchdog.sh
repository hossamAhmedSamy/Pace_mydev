#!/usr/bin/sh
cd /pace/
lsscsi=0
#dmesg -n 1
rabbitip=`echo $@ | awk '{print $1}'`
#echo start >> /root/iscsiwatch
targetn=0
while true;
do
	lsscsinew=`lsscsi -is | wc -c `
	cd /pace
	if [ $lsscsinew -ne $lsscsi ];
	then
		lsscsi=$lsscsinew
		./addtargetdisks.sh 
		./iscsirefresh.sh
		./listingtargets.sh $rabbitip
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
