cd /pace
iscsimapping='/pacedata/iscsimapping';
iscsitargets='/pacedata/iscsitargets';
declare -a iscsitargets=(`ETCDCTL_API=3 ./iscsiclients.py`);
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
   echo /sbin/iscsiadm -m discovery --portal $host --type sendtargets -o delete -o new 
   hostiqn=`/sbin/iscsiadm -m discovery --portal $host --type sendtargets 2>/root/iscsirefresh | awk '{print $2}'`
   echo hostiqn=$hostiqn
   echo /sbin/iscsiadm --mode node --targetname $hostiqn --portal $host:3260 -u 2>/dev/null
   echo /sbin/iscsiadm --mode node --targetname $hostiqn --portal $host:3260 --login
   /sbin/iscsiadm --mode node --targetname $hostiqn --portal $host --login
 fi
done
