#!/usr/bin/sh
######################
#exit
##########################
cd /pace
etcdip=`echo $@ | awk '{print $1}'`
myhost=`echo $@ | awk '{print $2}'`
actives=`/pace/etcdget.py $etcdip Active --prefix`
change=0
#declare -a iscsitargets=(`cat /pacedata/iscsitargets | awk '{print $2}' `);
myip=`docker exec etcdclient /TopStor/etcdgetlocal.py clusternodeip`
mycluster=`nmcli conn show mycluster | grep ipv4.addresses | awk '{print $2}' | awk -F'/' '{print $1}'`
declare -a iscsitargets=(`docker exec etcdclient /pace/iscsiclients.py $etcdip | grep target | awk -F'/' '{print $2}'`);
currentdisks=`targetcli ls /iscsi`
disks=(`lsblk -nS -o name,serial,vendor | grep -v sr0 |  grep -v LIO | awk '{print $1}'`)
diskids=`lsblk -nS -o name,serial,vendor | grep -v sr0 | grep -v LIO | awk '{print $1" "$2}'`
mappedhosts=`targetcli ls /iscsi | grep Mapped`;
targets=`targetcli ls backstores/block | grep -v deactivated |  grep dev | awk -F'[' '{print $2}' | awk '{print $1}'`
blocks=`targetcli ls backstores/block `
echo targets $blocks
for ddisk in  "${disks[@]}"; do
	echo $blocks | grep $ddisk
	if [ $? -ne 0 ];
	then
		echo $ddisk not a part in the targets
		scsidisk=`ls -l /dev/disk/by-id/ | grep $ddisk | grep -v part | grep scsi | head -1 | awk '{print $9}'`
  		targetcli backstores/block create ${ddisk}-${myhost} /dev/disk/by-id/$scsidisk
		
	else
		echo $ddisk is a part in the targets
	fi
done
declare -a newdisks=();
targetcli ls iscsi/ | grep ".$myhost:t1" &>/dev/null
if [ $? -ne 0 ]; then

 targetcli iscsi/ create iqn.2016-03.com.${myhost}:t1 &>/dev/null
 targetcli iscsi/iqn.2016-03.com.$myhost:t1/tpg1/portals delete 0.0.0.0 3260
 targetcli iscsi/iqn.2016-03.com.$myhost:t1/tpg1/portals create $myip 3266
 change=1
fi

targetcli ls iscsi/iqn.2016-03.com.$myhost:t1/tpg1/portals | grep $myip &>/dev/null
if [ $? -ne 0 ]; then
 targetcli iscsi/iqn.2016-03.com.${myhost}:t1/tpg1/portals ls | grep 3266 | awk -F'o-' '{print $2}' | awk -F':' '{print $1}'
 oldip=`targetcli iscsi/iqn.2016-03.com.${myhost}:t1/tpg1/portals ls | grep 3266 | awk -F'o-' '{print $2}' | awk -F':' '{print $1}'`
 echo oldip=$oldip
 targetcli iscsi/iqn.2016-03.com.${myhost}:t1/tpg1/portals delete$olidp 3266
 targetcli iscsi/iqn.2016-03.com.$myhost:t1/tpg1/portals create $myip 3266
fi
targetcli /iscsi/iqn.2016-03.com.${myhost}:t1 set global auto_add_mapped_luns=true
i=0;
for ddisk in "${disks[@]}"; do
 devdisk=$ddisk 
 echo ddisk===$ddisk
 idisk=`echo "$diskids" | grep -w $ddisk | awk '{print $2}'`
 echo compare devdisk-ddisk=$ddisk $idisk
 echo $currentdisks | grep $idisk &>/dev/null
 if [ $? -ne 0 ]; then
  echo Imhere
  pdisk=`ls /dev/disk/by-id/ | grep $idisk | grep -v part | grep scsi | head -1`
  targetcli backstores/block create ${devdisk}-${myhost} /dev/disk/by-id/$pdisk
  change=1
  echo currentdisks $currentdisks
  tpgs=(`targetcli ls /iscsi | grep iqn | grep TPG | grep ':t1' | awk -F'iqn' '{print $2}' | awk '{print $1}'`)
  for iqn in "${tpgs[@]}"; do
   echo iqn= $iqn devdisk=$devdisk-${myhost}
   ################################targetcli iscsi/iqn${iqn}/tpg1/luns/ create /backstores/block/${devdisk}-${myhost}  
   change=1
  done
 fi
done;
for target in "${iscsitargets[@]}"; do
 echo $mappedhosts | grep $target &>/dev/null
 if [ $? -ne 0 ]; then
  ############################targetcli iscsi/iqn.2016-03.com.${myhost}:t1/tpg1/acls/ create iqn.1994-05.com.redhat:$target
  
  #targetcli iscsi/iqn.2016-03.com.${myhost}:t1/tpg1 demo_mode_write_protect=0 
  #targetcli iscsi/iqn.2016-03.com.${myhost}:t1/tpg1 generate_node_acls=1 
  #targetcli iscsi/iqn.2016-03.com.${myhost}:t1/tpg1 set attribute authentication=1
  #targetcli iscsi/iqn.2016-03.com.${myhost}:t1/tpg1 set auth userid=MoatazNegm 
  #targetcli iscsi/iqn.2016-03.com.${myhost}:t1/tpg1 set auth password=YNPassword121 

  change=1
 fi
done
targetcli /iscsi/iqn.2016-03.com.${myhost}:t1 set global auto_add_mapped_luns=true
tpgs=(`targetcli ls /iscsi | grep iqn | grep TPG | grep ':t1' | awk -F'iqn' '{print $2}' | awk '{print $1}'`)

for iqn in "${tpgs[@]}"; do
	node=`echo $iqn | awk -F'.' '{print $4}' | awk -F':' '{print $1}'`
echo '##############################################################'
echo $node
echo $actives
echo '##############################################################'
	echo $actives | grep $node
	if [ $? -ne 0 ];
	then
		
		targetcli /iscsi delete iqn$iqn
	fi
done	
for ddisk in "${disks[@]}"; do
	for iqn in "${tpgs[@]}"; do
 		devdisk=`echo $ddisk | awk '{print $1}'`
 		targetcli iscsi/iqn${iqn}/tpg1/luns/ ls | grep  ${devdisk}-${myhost}  
		if [ $? -eq 0 ];
		then
			echo iqn$iqn has a map for $devdisk
		else
			echo iqn$iqn is not mapped to  $devdisk
  			targetcli iscsi/iqn${iqn}/tpg1/acls/ create iqn.1994-05.com.redhat:$myhost
   			targetcli iscsi/iqn${iqn}/tpg1/luns/ create /backstores/block/${devdisk}-${myhost}  
		fi
	done
done
targetcli /iscsi/iqn.2016-03.com.${myhost}:t1 set global auto_add_mapped_luns=false

targetcli saveconfig
#if [ $change -eq 1 ];
#then
# targetcli saveconfig /pacedata/targetconfig
# sleep 1 
#fi
