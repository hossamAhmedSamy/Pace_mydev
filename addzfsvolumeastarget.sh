#!/bin/sh
######################
#exit
##########################
cd /pace
chapuser='iqn.1991-05.com.microsoft:desktop-jckvhk3'
chapuser='MoatazNegm'
chappass='MezoPass1234'
myhost=`hostname -s`;
change=0
#declare -a iscsitargets=(`cat /pacedata/iscsitargets | awk '{print $2}' `;
target='iqn.1991-05.com.microsoft:desktop-jckvhk3'
#target='iqn.1994-05.com.redhat:dhcp13038'
disk='zd0'
diskids='QuicStor-zd0'
iqn='.2016-03.com.'$myhost':data'
targetcli ls iscsi/ | grep ".$myhost:data" &>/dev/null
if [ $? -ne 0 ]; then
 targetcli iscsi/ create iqn.2016-03.com.${myhost}:data &>/dev/null
 change=1
fi
pdisk=`targetcli ls backstores/block`
echo $pdisk | grep $disk 
if [ $? -ne 0 ];
then 
 targetcli backstores/block create ${disk}-${myhost} /dev/$disk
fi
targetcli iscsi/iqn${iqn}/tpg1/luns/ create /backstores/block/${disk}-${myhost}  
targetcli iscsi/iqn${iqn}/tpg1/acls/ create $target
targetcli iscsi/iqn${iqn}/tpg1 set attribute demo_mode_write_protect=0 
targetcli iscsi/iqn${iqn}/tpg1 set attribute cache_dynamic_acls=1
targetcli iscsi/iqn${iqn}/tpg1 set attribute generate_node_acls=1 
targetcli iscsi/iqn${iqn}/tpg1 set attribute authentication=0
targetcli iscsi/iqn${iqn}/tpg1 set auth userid=$chapuser 
targetcli iscsi/iqn${iqn}/tpg1 set auth password=$chappass
targetcli saveconfig
 #targetcli saveconfig /pacedata/targetconfig
