#!/bin/sh

disksphy=(`lsblk -nS -o name,serial,vendor | grep -v sr0 | grep -vw sda | grep -v LIO | awk '{print $1}'`)
diskLIO=(`lsscsi -i | grep -v sr0 | grep -vw sda | grep -w LIO | awk '{print $NF}'`)
diskFAULT=`./etcdget.py disks FAULT`
diskONLINE=`./etcdget.py disks ONLINE`
disktrans=`./etcdget.py disks transition`
for disk in "${disksphy[@]}"; do
 fdisk -l /dev/$disk >/dev/null 2>/dev/null
 if [ $? -eq 0 ];
 then
  echo $disk ok
 else
  echo $disk fault
  echo 1 >/sys/block/dev/$disk/device/delete 
 fi 
done
for disk in "${diskLIO[@]}"; do
 diskinfo=`lsscsi -i | grep -w $disk `
 diskname=`echo $diskinfo |  awk '{print $4}'`
 diskdev=`echo $diskinfo |  awk '{print $6}'`
 diskscsi=`echo $diskinfo |  awk '{print $7}'`
 phydisk=`echo $diskname | awk -F'-' '{print $1}'`
 itisok=1
 diskstatus=`./etcdget.py disks/FAULT/scsi-${diskscsi}`
 fdisk -l $diskdev >/dev/null 2>/dev/null
 if [ $? -ne 0 ];
 then
  echo wiwiwiwiwiwiw $diskdev
  itisok=0
 fi
 echo $diskLIO | grep -vw $diskname | grep $phydisk >/dev/null
 if [ $? -eq 0 ];
 then
  echo hihihihhihhi
  itisok=0
 fi
 
 if [ $itisok -eq 0 ];
 then
  echo $disk fault
  devname=`echo $diskdev | awk -F'/' '{print $3}'`
  echo faulty disk $diskname $devname
  targetcli backstores/block delete $diskname 
  echo 1 >/sys/block/$devname/device/delete 
  echo $diskFAULT | grep $diskscsi
  if [ $? -ne 0 ];
  then
  ./etcdput.py disks/scsi-${diskscsi} FAULT
  ./broadcasttolocal.py disks/scsi-${diskscsi} FAULT
  fi
  #systemctl restart iscsid
  #echo 1 >/sys/block/dev/$disk/device/delete 
 else
  echo $disk ok
  echo $diskONLINE | grep $diskscsi
  if [ $? -ne 0 ];
  then
   echo $disktrans | grep $diskscsi
   if [ $? -ne 0 ];
   then
    ./etcdput.py disks/scsi-${diskscsi} ONLINE
    ./broadcasttolocal.py disks/scsi-${diskscsi} ONLINE
   else
    echo $disktrans | grep $diskscsi | grep transition3
    if [ $? -eq 0 ];
    then
     ./etcdput.py disks/scsi-${diskscsi} ONLINE
     ./broadcasttolocal.py disks/scsi-${diskscsi} ONLINE
    else 
     echo $disktrans | grep $diskscsi | grep transition2
     if [ $? -eq 0 ];
     then
      ./etcdput.py disks/scsi-${diskscsi} transition3
      ./broadcasttolocal.py disks/scsi-${diskscsi} transition3 
     else
      ./etcdput.py disks/scsi-${diskscsi} transition2
      ./broadcasttolocal.py disks/scsi-${diskscsi} transition2 
       
     fi
    fi
   fi 
  fi
 fi
done




