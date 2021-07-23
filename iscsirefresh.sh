cd /pace
perfmon=`cat /pacedata/perfmon`
 echo $perfmon | grep 1
 if [ $? -eq 0 ]; then
/TopStor/logqueue.py Iscsirefresh start system 
fi
iscsimapping='/pacedata/iscsimapping';
iscsitargets='/pacedata/iscsitargets';
declare -a iscsitargets=(`ETCDCTL_API=3 ./iscsiclients.py | grep target | awk -F'/' '{print $2}'`);
systemctl status iscsid &>/dev/null
if [ $? -ne 0 ];
then
 systemctl start iscsid 
fi
systemctl status target &>/dev/null
if [ $? -ne 0 ];
then
 systemctl start target
fi
systemctl status iscsi &>/dev/null
if [ $? -ne 0 ];
then
 systemctl start iscsi 
fi

echo /sbin/iscsiadm -m session --rescan
/sbin/iscsiadm -m session --rescan &>/dev/null
if [ $? -ne 0 ];
then
 ff=`ls /var/lib/iscsi/nodes/* | awk '{print $NF}' | grep $myhost` 
 echo ff=$ff
 rm -rf /var/lib/iscsi/nodes/$ff 
fi
needrescan=0;
myhost=`hostname -s`
for hostline in "${iscsitargets[@]}"
do
 echo $myhost | grep $hostline
 host=` ETCDCTL_API=3 ./etcdgetip.py $hostline`
 echo hihi
 ping -c 1 -W 1 $host &>/dev/null
 if [ $? -eq 0 ]; then
  needrescan=1;
   echo firsthost=$host
   echo /sbin/iscsiadm -m discovery --portal $host:3266 --type sendtargets -o delete -o new 
   hostiqn=`/sbin/iscsiadm -m discovery --portal $host:3266 --type sendtargets 2>/root/iscsirefresh | grep ':t1' | awk '{print $2}'`
   echo hostiqn=$hostiqn
   echo /sbin/iscsiadm --mode node --targetname $hostiqn --portal $host:3266 -u 2>/dev/null
   echo /sbin/iscsiadm --mode node --targetname $hostiqn --portal $host:3266 --login
   /sbin/iscsiadm --mode node --targetname $hostiqn --portal $host:3266 --login
 fi
done
 echo $perfmon | grep 1
 if [ $? -eq 0 ]; then
/TopStor/logqueue.py Iscsirefresh stop system 
fi

dskperf=`ls -lisa /TopStordata/dskperfmon.txt | awk '{print -$2}'`
dskperflimit=$((8000000-dskperf))
echo $dskperflimit | grep '-'
if [ $? -eq 0 ];
then
 tail -n 60000 /TopStordata/dskperfmon.txt > /TopStordata/dskperfmon.txttmp
 cat /TopStordata/dskperfmon.txttmp > /TopStordata/dskperfmon.txt
 rm -rf /TopStordata/dskperfmon.txttmp
fi
