#!/usr/bin/python3
import traceback, hashlib
import subprocess
from ast import literal_eval as mtuple
from etcddel import etcddel as etcddel
from etcdput import etcdput as put 
import socket
msg='start new putzpool '
with open('/root/putzpooltmp','a') as f:
 f.write(str(msg)+"\n")
myhostorg=socket.gethostname()
myhost='run/'+myhostorg
mod=0
msg='getting lsscsi '
with open('/root/putzpooltmp','a') as f:
 f.write(str(msg)+"\n")
cmdline=['/pace/etcdget.py','known','--prefix']
known=str(subprocess.run(cmdline,stdout=subprocess.PIPE).stdout)
#cmdline=['/pace/etcdget.py','possible','--prefix']
#possible=str(subprocess.run(cmdline,stdout=subprocess.PIPE).stdout)
cmdline=['lsscsi','-i','--size']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
lsscsi=[x for x in str(result.stdout)[2:][:-3].split('\\n') if 'LIO' in x]
ata=[x for x in str(result.stdout)[2:][:-3].split('\\n') if 'LIO' not in x]
mlsscsi=hashlib.md5()
mlsscsi.update(str(lsscsi).encode('utf-8'))
mlsscsi=mlsscsi.hexdigest()
cmdline=['/pace/etcdget.py','md'+myhost+'/lsscsi']
modlsscsi=str(subprocess.run(cmdline,stdout=subprocess.PIPE).stdout)
if mlsscsi not in modlsscsi:
 mod=1
 msg='lsscsi changed '
 with open('/root/putzpooltmp','a') as f:
  f.write(str(msg)+"\n")
msg='getting zpool status \n'
with open('/root/putzpooltmp','a') as f:
 f.write(str(msg)+"\n")
cmdline=['/sbin/zpool','status']
zpoolres=subprocess.run(cmdline,stdout=subprocess.PIPE)
mzpool=hashlib.md5()
mzpool.update(str(zpoolres.stdout).encode('utf-8'))
mzpool=mzpool.hexdigest()
cmdline=['/pace/etcdget.py','md'+myhost+'/zpool']
modzpool=str(subprocess.run(cmdline,stdout=subprocess.PIPE).stdout)
if mzpool not in modzpool:
 mod=1
 msg='zpool changed '
 with open('/root/putzpooltmp','a') as f:
  f.write(str(msg)+"\n")

msg='getting users '
with open('/root/putzpooltmp','a') as f:
 f.write(str(msg)+"\n")
userf=''
with open('/etc/passwd','r') as f:
 line=f.readline()
 if 'TopStor' in line:
  userf+=line
muser=hashlib.md5()
muser.update(str(userf).encode('utf-8'))
muser=muser.hexdigest()
cmdline=['/pace/etcdget.py','md'+myhost+'/userhash']
moduser=str(subprocess.run(cmdline,stdout=subprocess.PIPE).stdout)
if muser not in moduser or '-1' in moduser:
 mod=1
 msg='user changed '
 with open('/root/putzpooltmp','a') as f:
  f.write(str(msg)+"\n")
if mod==0:
 msg='nothing changed exiting '
 with open('/root/putzpooltmp','a') as f:
  f.write(str(msg)+"\n")
 exit() 
msg='deleting old putzpool '
with open('/root/putzpooltmp','a') as f:
 f.write(str(msg)+"\n")
#cmdline=['/pace/etcddel.py','run','stub']
#subprocess.run(cmdline,stdout=subprocess.PIPE)
etcddel('run','stub')
etcddel('run','--prefix')
etcddel('md','--prefix')
msg='deleted old putzpool \n'
#with open('/root/putzpooltmp','a') as f:
# f.write(str(msg)+"\n")
#cmdline=['sleep','4']
#subprocess.run(cmdline,stdout=subprocess.PIPE)
msg='adding users '
with open('/root/putzpooltmp','a') as f:
 f.write(str(msg)+"\n")
with open('/etc/passwd') as f:
 for fline in f:
  if 'TopStor' in fline:
   y=fline.split(":")
   put(myhost+'/user/'+y[0],y[2])
msg='filtering lsscsi '
with open('/root/putzpooltmp','a') as f:
 f.write(str(msg)+"\n")
pscsi=lsscsi
for x in pscsi:
 for y in pscsi:
  if (x != y):
   if(x.split()[3] == y.split()[3]):
    if (len(x.split()[6]) > 3):
     lsscsi.remove(y)
    else:
     lsscsi.remove(x)
msg='processing zpool results \n'
with open('/root/putzpooltmp','a') as f:
 f.write(str(msg)+"\n")
try:
 zpool=str(zpoolres.stdout)[2:][:-3].split('\\n')
 with open('/root/putzpooltmp','a') as f:
  f.write(str(zpool))
 z=[]
 if zpool==['']:
  msg='no pools \n'
  with open('/root/putzpooltmp','a') as f:
   f.write(str(msg)+"\n")
  zpool=[':nopool',':nopool',':nopool','nopool','nopool','nopool','nopool','nopool']
 else:
  poolname=zpool[0].split(':')[1].replace(' ','')
  msg='found pool '+poolname+'\n'
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
  cmdline=['/sbin/zfs','list','-H']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  zfslist=str(result.stdout)[2:][:-3].split('\\t')
  cmdline=['/sbin/zpool','list','-H']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  zlist=str(result.stdout)[2:][:-3].split('\\t')
  z.append((myhost+'/pool/'+poolname+'/size',zfslist[2]))
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
########### recroding raids and disks for every pool ##########
  raidc=0  
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
    print(str(count),raid,raidstat)
    diskc=0
   else:
    isstripe=len(c.split('scsi')[0])
    msg='recording pool as stripe '
    with open('/root/putzpooltmp','a') as f:
     f.write(str(msg)+"\n")
    if isstripe < 6:
     count+=1
     raid='stripe'
     z.append((myhost+'/pool/'+poolname+'/raid/'+str(count)+'/type','stripe-'+str(raidc)))
     raidstat=zpool[1].split(':')[1].replace(' ','')
     raidc+=1
     z.append((myhost+'/pool/'+poolname+'/raid/'+str(count)+'/status',raidstat))
    msg='looping on lsscsi to add to get every diskc '
    with open('/root/putzpooltmp','a') as f:
     f.write(str(msg)+"\n")
    print('in c=',c.split()[1].split('-')[1])
    if c.split()[1].split('-')[1] not in str(lsscsi):
     msg='found diskc in zpool and is not in lsscsi'+str(diskc)
     with open('/root/putzpooltmp','a') as f:
      f.write(str(msg)+"\n")
     diskc=-1
     fromhost='nohost'
     size='-'
     status=c.split()[2]
    else:
     msg='found diskc in zpool and lsscsi'+str(diskc)
     with open('/root/putzpooltmp','a') as f:
      f.write(str(msg)+"\n")
     diskc=[i for i, x in enumerate(lsscsi) if c.split()[1].split('-')[1] in x ]
     diskc=diskc[0] 
     ll=lsscsi[diskc].split()
     fromhost=ll[3]
     size=ll[7]
     status=c.split()[2]
    z.append((myhost+'/pool/'+poolname+'/raid/'+str(count)+'/disk/'+str(diskc)+'/uuid',c.split()[1]))
    z.append((myhost+'/pool/'+poolname+'/raid/'+str(count)+'/disk/'+str(diskc)+'/fromhost',fromhost))
    z.append((myhost+'/pool/'+poolname+'/raid/'+str(count)+'/disk/'+str(diskc)+'/size',size))
    z.append((myhost+'/pool/'+poolname+'/raid/'+str(count)+'/disk/'+str(diskc)+'/status',status))
  for l in lsscsi:
   ll=l.split()
   if ll[6] not in str(zpool):
    diskc=lsscsi.index(l)
    msg='found free disk '+str(diskc)+' '+l[6]
    with open('/root/putzpooltmp','a') as f:
     f.write(str(msg)+"\n")
    status='free'
    ll=l.split()
    uuid='scsi-'+ll[6]
    msg='adding free disk to etcd'+str(diskc)+' '+ll[6]
    with open('/root/putzpooltmp','a') as f:
     f.write(str(msg)+"\n")
    if ll[6]=='-':
     status='FAULT'
    put(myhost+'/free/disk/'+str(diskc)+'/uuid',uuid)
    put(myhost+'/free/disk/'+str(diskc)+'/fromhost',ll[3])
    put(myhost+'/free/disk/'+str(diskc)+'/size',ll[7])
    put(myhost+'/free/disk/'+str(diskc)+'/status',status)
  if count==0 and diskc > 0:
   z.append((myhost+'/pool/'+poolname+'/raid/'+str(count)+'/type',raid))
  msg='adding z in the etcd'
  with open('/root/putzpooltmp','a') as f:
   f.write(str(msg)+"\n")
  for c in z:
   put(c[0],c[1])
 msg='checking crontab'
 with open('/root/putzpooltmp','a') as f:
  f.write(str(msg)+"\n")
 cmdline=['crontab','-l']
 crons=subprocess.run(cmdline,stdout=subprocess.PIPE)
 autosnap=[x for x in str(crons.stdout)[2:][:-3].split('\\n') if 'Snapshotnowhost' in x]
 h=[]
 msg='adding crons into etcd'+str(autosnap)
 with open('/root/putzpooltmp','a') as f:
  f.write(str(msg)+"\n")
 for x in autosnap:
  y=x.split()
  put(myhost+'/pool/'+poolname+'/snapperiod/'+y[-1],y[-2].split('.')[0]+'/'+y[-3].split('/')[-1]+'/'+y[-2].split('.')[1]+'/'+y[-2].split('.')[2]+'/'+y[-2].split('.')[3]+'/'+y[-2].split('.')[4]+'/'+y[0].replace('/','::')+'/'+y[1].replace('/','::')+'/'+y[2].replace('/','::')+'/'+y[3].replace('/','::')+'/'+y[4].replace('/','::'))
except Exception as e:
 traceback.print_exc()
 msg='severe exception'+str(traceback.print_exc())
 with open('/root/putzpooltmp','a') as f:
  f.write(str(msg)+"\n")
 exit() 

msg='adding stub'
with open('/root/putzpooltmp','a') as f:
 f.write(str(msg)+"\n")
put(myhost+'/stub/stub/stub/stub','stub')
cmdline=['/pace/verdef.sh']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
vers=str(result.stdout)[2:][:-3]
curver=vers.split()[0]
put(myhost+'/hostfw/'+curver,vers.replace(" ","/"))
msg='exiting after verdef and stub'
with open('/root/putzpooltmp','a') as f:
 f.write(str(msg)+"\n")
put('md'+myhost+'/lsscsi',mlsscsi)
put('md'+myhost+'/zpool',mzpool)
put('md'+myhost+'/userhash',muser)
