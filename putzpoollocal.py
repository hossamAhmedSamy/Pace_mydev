#!/usr/bin/python3
import traceback, sys
import subprocess
from ast import literal_eval as mtuple
import socket

myip=sys.argv[1]
myhostorg=sys.argv[2]
leader=sys.argv[3]
msg='start new putzpoollocal \n'
with open('/root/putzpooltmp','w') as f:
 f.write(str(msg)+"\n")
myhost='run/'+myhostorg
localmyhost='localrun/'+myhostorg
#cmdline=['/bin/sleep','2']
#subprocess.run(cmdline,stdout=subprocess.PIPE)
msg='deleting old putzpools '
with open('/root/putzpooltmp','a') as f:
 f.write(str(msg)+"\n")
cmdline=['/pace/etcdget.py','run/'+leader,'--prefix']
runningzres=subprocess.run(cmdline,stdout=subprocess.PIPE)
cmdline=['/pace/etcddel.py','local'+myhost,'stub']
subprocess.run(cmdline,stdout=subprocess.PIPE)
cmdline=['/pace/etcddellocal.py',myip, myhost,'stub']
subprocess.run(cmdline,stdout=subprocess.PIPE)
cmdline=['/pace/etcddel.py','local'+myhost,'--prefix']
subprocess.run(cmdline,stdout=subprocess.PIPE)
cmdline=['/pace/etcddellocal.py',myip, myhost,'--prefix']
subprocess.run(cmdline,stdout=subprocess.PIPE)
msg='adding users '
with open('/root/putzpooltmp','a') as f:
 f.write(str(msg)+"\n")
with open('/etc/passwd') as f:
 for fline in f:
  if 'TopStor' in fline:
   y=fline.split(":")
   cmdline=['/pace/etcdput.py','local'+myhost+'/user/'+y[0],y[2]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/pace/etcdputlocal.py',myip, myhost+'/user/'+y[0],y[2]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
msg='getting lsscsi and filtering it '
with open('/root/putzpooltmp','a') as f:
 f.write(str(msg)+"\n")
cmdline=['lsscsi','-i','--size']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
lsscsi=[x for x in str(result.stdout)[2:][:-3].split('\\n') if 'LIO' in x]
pscsi=lsscsi
for x in pscsi:
 for y in pscsi:
  if (x != y):
   if(x.split()[3] == y.split()[3]):
    if (len(x.split()[6]) > 3):
     lsscsi.remove(y)
    else:
     lsscsi.remove(x)
ata=[x for x in str(result.stdout)[2:][:-3].split('\\n') if 'LIO' not in x]
msg='getting zpool status '
with open('/root/putzpooltmp','a') as f:
 f.write(str(msg)+"\n")
cmdline=['/sbin/zpool','status']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
try:
 zpool=str(result.stdout)[2:][:-3].split('\\n')
 with open('/root/putzpooltmp','a') as f:
  f.write(str(zpool))
 z=[]
 zoth=[]
 if zpool==['']:
  msg='no pools \n'
  with open('/root/putzpooltmp','a') as f:
   f.write(str(msg)+"\n")
  zpool=[':nopool',':nopool',':nopool','nopool','nopool','nopool','nopool','nopool']
 else:
  poolname=zpool[0].split(':')[1].replace(' ','')
  msg='found pool '+poolname
  with open('/root/putzpooltmp','a') as f:
   f.write(str(msg)+"\n")
  z.append((myhost+'/pool/'+poolname+'/name',poolname))
  z.append((myhost+'/pool/'+poolname+'/state',zpool[1].split(':')[1].replace(' ','')))
  z.append((myhost+'/pool/'+poolname+'/scan',zpool[2].split(':')[1]))
  msg='pool appended z status and now listing'
  with open('/root/putzpooltmp','a') as f:
   f.write(str(msg)+"\n")
  cmdline=['/sbin/zfs','list','-t','snapshot,filesystem','-o','name,creation,used,quota,usedbysnapshots,refcompressratio,prot:kind','-H']
  vollist=subprocess.run(cmdline,stdout=subprocess.PIPE)
  vollist=[x.split('\\t') for x in str(vollist.stdout)[2:][:-3].split('\\n')]
  snap=[]
  for y in vollist:
   try:
    msg='looping on vollist to record its snapshots'
    with open('/root/putzpooltmp','a') as f:
      f.write(str(msg)+"\n")
    names=y[0].split('/')
    snap=y[0].split('@')[1]
    thisvol='/pool/'+names[0]+'/vol/'+names[1].split('@')[0]+'/snapshot/'+names[1].split('@')[1]
    thisvolvalue=y[1]+'/'+y[2]+'/'+y[5]
    print(thisvol, thisvolvalue)
    print('is a snapshot')
   except:
    try:
     msg='this vol has no snaps'
     with open('/root/putzpooltmp','a') as f:
      f.write(str(msg)+"\n")
     names=y[0].split('/')
     thisvol='/pool/'+names[0]+'/vol/'+names[1]+'/'+y[6]
     thisvolvalue=y[3]+'/'+y[2]+'/'+y[4]+'/'+y[5]
     print('is a vol')
    except:
     msg='no volume found'
     with open('/root/putzpooltmp','a') as f:
      f.write(str(msg)+"\n")
     continue 
     #thisvol='/pool/'
     #thisvolvalue=y[3]+'/'+y[2]+'/'+y[4]+'/'+y[5]
     #print('is a pool')
   z.append((myhost+thisvol,thisvolvalue))
  msg='recording pool props '+poolname
  with open('/root/putzpooltmp','a') as f:
   f.write(str(msg)+"\n")
  cmdline=['/sbin/zpool','list','-H']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  zlist=str(result.stdout)[2:][:-3].split('\\t')
  z.append((myhost+'/pool/'+poolname+'/size',zlist[1]))
  z.append((myhost+'/pool/'+poolname+'/alloc',zlist[2]))
  z.append((myhost+'/pool/'+poolname+'/empty',zlist[3]))
  z.append((myhost+'/pool/'+poolname+'/dedup',zlist[7]))
  cmdline=['/sbin/zfs','get','compressratio','-H']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  zlist=str(result.stdout)[2:][:-3].split('\\t')
  z.append((myhost+'/pool/'+poolname+'/compressratio',zlist[2]))
  raid='stripe'
  count=0
  diskc=0
  tmpc=6
  for c in zpool[7:-1]:
   if c.replace(' ','')=='':
    continue
   if 'scsi' not in c:
    count+=1
    cc=c.split()
    cc.append(cc[0].replace('\\t','').replace('\\',''))
    cc.append('ONLINE/AVAIL')
    raid=cc[1]
    raidstat=cc[2]
    msg='recording pool raidtype '+raid
    with open('/root/putzpooltmp','a') as f:
     f.write(str(msg)+"\n")
    z.append((myhost+'/pool/'+poolname+'/raid/'+str(count)+'/type',raid))
    z.append((myhost+'/pool/'+poolname+'/raid/'+str(count)+'/status',raidstat))
    diskc=0
   else:
    msg='recording pool as stripe '
    with open('/root/putzpooltmp','a') as f:
     f.write(str(msg)+"\n")
    if count==0:
     count+=1
     z.append((myhost+'/pool/'+poolname+'/raid/'+str(count)+'/type','stripe'))
     raidstat=zpool[1].split(':')[1].replace(' ','')
     z.append((myhost+'/pool/'+poolname+'/raid/'+str(count)+'/status',raidstat))
    msg='looping on lsscsi to add to get every diskc '
    with open('/root/putzpooltmp','a') as f:
     f.write(str(msg)+"\n")
    for l in lsscsi:
     ll=l.split()
     if ll[6] in c.split()[1] and len(ll[6]) > 3:
      diskc=lsscsi.index(l)
      msg='found diskc '+str(diskc)
      with open('/root/putzpooltmp','a') as f:
       f.write(str(msg)+"\n")
      if ll[3].split('-')[0] not in str(ata) or ll[7]=='-':
       status='FAULT'
       msg='status of disk is FAULT'
       with open('/root/putzpooltmp','a') as f:
        f.write(str(msg)+"\n")
      else:
       status=c.split()[2]
       msg='recording status of disk '+status
       with open('/root/putzpooltmp','a') as f:
        f.write(str(msg)+"\n")
      msg='breaking the lsscsi loop as diskc is found '
      with open('/root/putzpooltmp','a') as f:
       f.write(str(msg)+"\n")
      break;
    msg='recording disk as the diskc '+str(diskc)
    with open('/root/putzpooltmp','a') as f:
     f.write(str(msg)+"\n")
    z.append((myhost+'/pool/'+poolname+'/raid/'+str(count)+'/disk/'+str(diskc)+'/uuid',c.split()[1]))
    z.append((myhost+'/pool/'+poolname+'/raid/'+str(count)+'/disk/'+str(diskc)+'/fromhost',ll[3]))
    z.append((myhost+'/pool/'+poolname+'/raid/'+str(count)+'/disk/'+str(diskc)+'/size',ll[7]))
    z.append((myhost+'/pool/'+poolname+'/raid/'+str(count)+'/disk/'+str(diskc)+'/status',status))
  if count==0 and diskc > 0:
   z.append((myhost+'/pool/'+poolname+'/raid/'+str(count)+'/type',raid))
   
  for c in z:
   msg='adding z in the etcd'+str(c)
   with open('/root/putzpooltmp','a') as f:
    f.write(str(msg)+"\n")
   cmdline=['/pace/etcdput.py','local'+c[0],c[1]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/pace/etcdputlocal.py',myip,c[0],c[1]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)

 msg='checking crontab'
 with open('/root/putzpooltmp','a') as f:
  f.write(str(msg)+"\n")
 cmdline=['crontab','-l']
 crons=subprocess.run(cmdline,stdout=subprocess.PIPE)
 autosnap=[x for x in str(crons.stdout)[2:][:-3].split('\\n') if 'Snapshotnowhost' in x]
 h=[]
 for x in autosnap:
  y=x.split()
  msg='adding crons into etcd'+str(y)
  with open('/root/putzpooltmp','a') as f:
   f.write(str(msg)+"\n")
  cmdline=['/pace/etcdput.py','local'+myhost+'/pool/'+poolname+'/snapperiod/'+y[-1],y[-2].split('.')[0]+'/'+y[-3].split('/')[-1]+'/'+y[-2].split('.')[1]+'/'+y[-2].split('.')[2]+'/'+y[-2].split('.')[3]+'/'+y[-2].split('.')[4]+'/'+y[0].replace('/','::')+'/'+y[1].replace('/','::')+'/'+y[2].replace('/','::')+'/'+y[3].replace('/','::')+'/'+y[4].replace('/','::')]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  cmdline=['/pace/etcdputlocal.py',myip, myhost+'/pool/'+poolname+'/snapperiod/'+y[-1],y[-2].split('.')[0]+'/'+y[-3].split('/')[-1]+'/'+y[-2].split('.')[1]+'/'+y[-2].split('.')[2]+'/'+y[-2].split('.')[3]+'/'+y[-2].split('.')[4]+'/'+y[0].replace('/','::')+'/'+y[1].replace('/','::')+'/'+y[2].replace('/','::')+'/'+y[3].replace('/','::')+'/'+y[4].replace('/','::')]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)

 
except Exception as e:
 traceback.print_exc()
 msg='severe exception'+str(traceback.print_exc())
 with open('/root/putzpooltmp','a') as f:
  f.write(str(msg)+"\n")
 pass  
diskc=0
msg='looping lsscsi again for free disks'
with open('/root/putzpooltmp','a') as f:
 f.write(str(msg)+"\n")
for cc in lsscsi:
  c=cc.split()
  if len(c[6]) < 3 or c[6] not in str(z) or c[6] not in str(runningzres):
   msg='found free disk'+str(c[6])
   with open('/root/putzpooltmp','a') as f:
    f.write(str(msg)+"\n")
   diskc=lsscsi.index(cc)
   msg='adding free disk to etcd'+str(diskc)
   with open('/root/putzpooltmp','a') as f:
    f.write(str(msg)+"\n")
   cmdline=['/pace/etcdput.py','local'+myhost+'/free/disk/'+str(diskc)+'/uuid','scsi-'+c[6]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/pace/etcdputlocal.py',myip,myhost+'/free/disk/'+str(diskc)+'/uuid','scsi-'+c[6]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/pace/etcdput.py','local'+myhost+'/free/disk/'+str(diskc)+'/fromhost',c[3]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/pace/etcdputlocal.py',myip, myhost+'/free/disk/'+str(diskc)+'/fromhost',c[3]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/pace/etcdput.py','local'+myhost+'/free/disk/'+str(diskc)+'/size',c[7]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/pace/etcdputlocal.py',myip,myhost+'/free/disk/'+str(diskc)+'/size',c[7]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   status='AVAIL'
   if c[6]=='-':
    status='FAULT'
   cmdline=['/pace/etcdput.py','local'+myhost+'/free/disk/'+str(diskc)+'/status',status]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/pace/etcdputlocal.py',myip, myhost+'/free/disk/'+str(diskc)+'/status',status]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)

msg='adding stub'
with open('/root/putzpooltmp','a') as f:
 f.write(str(msg)+"\n")
cmdline=['/pace/etcdput.py','local'+myhost+'/stub/stub/stub/stub','stub']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
cmdline=['/pace/etcdputlocal.py',myip,myhost+'/stub/stub/stub/stub','stub']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
cmdline=['/pace/verdef.sh']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
vers=str(result.stdout)[2:][:-3]
curver=vers.split()[0]
cmdline=['/pace/etcdput.py','local'+myhost+'/hostfw/'+curver,vers.replace(" ","/")]
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
cmdline=['/pace/etcdputlocal.py',myip,myhost+'/hostfw/'+curver,vers.replace(" ","/")]
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
msg='exiting after verdef and stub'
with open('/root/putzpooltmp','a') as f:
 f.write(str(msg)+"\n")
