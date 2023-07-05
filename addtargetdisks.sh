#!/usr/bin/sh
######################
#exit
##########################
echo $@ > /root/addtargets
cd /pace
etcdip=`echo $@ | awk '{print $1}'`
myhost=`echo $@ | awk '{print $2}'`
actives=`/pace/etcdget.py $etcdip Active --prefix`
change=0
#echo hi1 $myhost>> /root/targetadd
#declare -a iscsitargets=(`cat /pacedata/iscsitargets | awk '{print $2}' `);
initialtarget=`targetcli ls | wc -l`
myip=`docker exec etcdclient /TopStor/etcdgetlocal.py clusternodeip`
mycluster=`nmcli conn show mycluster | grep ipv4.addresses | awk '{print $2}' | awk -F'/' '{print $1}'`
declare -a iscsitargets=(`docker exec etcdclient /pace/iscsiclients.py $etcdip | grep target | awk -F'/' '{print $2}'`);
currentdisks=`targetcli ls /iscsi`
disks=(`lsblk -nS -o name,serial,vendor | grep -v sr0 |  grep -v LIO | awk '{print $1}'`)
nodes=(`docker exec etcdclient /TopStor/etcdgetlocal.py Active --prefix | awk -F'Partners/' '{print $2}' | awk -F"'" '{print $1}'`)
diskids=`lsblk -nS -o name,serial,vendor | grep -v sr0 | grep -v LIO | awk '{print $1" "$2}'`
mappedhosts=`targetcli ls /iscsi | grep Mapped`;
targets=`targetcli ls backstores/block | grep -v deactivated |  grep dev | awk -F'[' '{print $2}' | awk '{print $1}'`
blocks=`targetcli ls backstores/block `
#echo hi2 $myhost >> /root/targetadd
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

#echo hi3 >> /root/targetadd
declare -a newdisks=();
#for node in "${nodes[@]}"; do
# echo $mappedhosts | grep $node
# if [ $? -ne 0 ];
# then
  #nodeip=`docker exec etcdclient /TopStor/etcdgetlocalpy ready/$node`
#  targetcli iscsi/ create iqn.2016-03.com.${node}:t1 
#  targetcli iscsi/iqn.2016-03.com.${node}:t1/tpg1/portals delete 0.0.0.0 3260
#  targetcli iscsi/iqn.2016-03.com.${node}:t1/tpg1/portals create $myip 3266
# fi
#done
targetcli ls iscsi/ | grep ".$myhost:t1" &>/dev/null
if [ $? -ne 0 ]; then
 echo hicreate $myhost >> /root/targetadd

 targetcli iscsi/ create iqn.2016-03.com.${myhost}:t1 
 targetcli iscsi/iqn.2016-03.com.${myhost}:t1/tpg1/portals delete 0.0.0.0 3260
 targetcli iscsi/iqn.2016-03.com.${myhost}:t1/tpg1/portals create $myip 3266
 change=1
fi
echo `targetcli /iscsi ls` >> /root/targetadd
tpgs1=(`targetcli ls /iscsi | grep iqn`) 
#echo hi$tpgs1 >> /root/targetadd
#echo hi4 >> /root/targetadd
targetcli ls iscsi/iqn.2016-03.com.$myhost:t1/tpg1/portals | grep $myip &>/dev/null
if [ $? -ne 0 ]; then
 targetcli iscsi/iqn.2016-03.com.${myhost}:t1/tpg1/portals ls | grep 3266 | awk -F'o-' '{print $2}' | awk -F':' '{print $1}'
 oldip=`targetcli iscsi/iqn.2016-03.com.${myhost}:t1/tpg1/portals ls | grep 3266 | awk -F'o-' '{print $2}' | awk -F':' '{print $1}'`
 echo oldip=$oldip
 #targetcli iscsi/iqn.2016-03.com.${myhost}:t1/tpg1/portals delete$olidp 3266
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

#echo hi5 >> /root/targetadd
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
tpgs1=(`targetcli ls /iscsi | grep iqn | grep TPG | grep ':t1'`)
tpgs=(`targetcli ls /iscsi | grep iqn | grep TPG | grep ':t1' | awk -F'iqn' '{print $2}' | awk '{print $1}'`)

#echo hi6.5 >> /root/targetadd
for iqn in "${tpgs[@]}"; do
	node=`echo $iqn | awk -F'.' '{print $4}' | awk -F':' '{print $1}'`
#echo hi6 >> /root/targetadd
	echo $actives | grep $node
	if [ $? -ne 0 ];
	then
#echo '##############################################################'>> /root/targetadd
#echo hi$tpgs1 >> /root/targetadd
#echo hi$iqn >> /root/targetadd
#echo hi$node >> /root/targetadd
#echo hi$actives >> /root/targetadd
#echo '##############################################################' >> /root/targetadd
		echo hidelete >> /root/targetadd
			
		#targetcli /iscsi delete iqn$iqn
	fi
done	

#echo hi7 >> /root/targetadd
for node in "${nodes[@]}"; do
 for ddisk in "${disks[@]}"; do
	for iqn in "${tpgs[@]}"; do
 		devdisk=`echo $ddisk | awk '{print $1}'`
 		targetcli iscsi/iqn${iqn}/tpg1/luns/ ls | grep  ${devdisk}-${myhost}  
		if [ $? -eq 0 ];
		then
			echo iqn$iqn has a map for $devdisk
		else
			echo iqn$iqn is not mapped to  $devdisk
  			targetcli iscsi/iqn${iqn}/tpg1/acls/ create iqn.1994-05.com.redhat:$node
   			targetcli iscsi/iqn${iqn}/tpg1/luns/ create /backstores/block/${devdisk}-${myhost}  
		fi
	done
 done
done
#echo hi8 >> /root/targetadd
targetcli /iscsi/iqn.2016-03.com.${myhost}:t1 set global auto_add_mapped_luns=false

#echo hi9 >> /root/targetadd
targetcli saveconfig

endingtarget=`targetcli ls | wc -l`
if [[ $initialtarget != $endingtarget ]];
then
  stamp=`date +%s%N`
  #/TopStor/etcdput.py $mycluster sync/diskref/______/request diskref_$stamp
fi
#if [ $change -eq 1 ];
#then
# targetcli saveconfig /pacedata/targetconfig
# sleep 1 
#:wq
#fi
