#!/usr/bin/python3
import subprocess, socket
from etcdput import etcdput as put
myhost=socket.gethostname()
cmdline='/sbin/zpool status'
result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout
y=str(result)[2:][:-3].replace('\\t','').split('\\n')
#with open("tmp") as f:
# y=f.read()
#y=y.split('\n')
#with open("zfslist.txt") as f:
# zfslist=f.read()
#zfslist2=zfslist.split('\n')
cmdline='/bin/lsscsi -is'
result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout
lsscsi=[x for x in str(result)[2:][:-3].replace('\\t','').split('\\n') if 'LIO' in x ]
freepool=[x for x in str(result)[2:][:-3].replace('\\t','').split('\\n') if 'LIO' in x ]
raidtypes=['mirror','raidz','stripe']
raid2=['log','cache','spare']
zpool=[]
stripecount=0
spaces=-2
raidlist=[]
disklist=[]
for a in y:
 b=a.split()
 if "pdhc" in a and  'pool' not in a:
  raidlist=[]
  volumelist=[]
  zdict={}
  cmdline=['/sbin/zfs','list','-t','snapshot,filesystem','-o','name,creation,used,quota,usedbysnapshots,refcompressratio,prot:kind','-H']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  zfslist=str(result.stdout)[2:][:-3].split('\\t')
  cmdline=['/sbin/zpool','list','-H']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  zlist=str(result.stdout)[2:][:-3].split('\\t')
  cmdline=['/sbin/zfs','get','compressratio','-H']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  zlist2=str(result.stdout)[2:][:-3].split('\\t')
  zdict={ 'name':b[0], 'status':b[1], 'size':str(zfslist[2]), 'alloc': str(zlist[2]), 'empty': zlist[3], 'dedup': zlist[7], 'compressratio': zlist2[2], 'raidlist': raidlist ,'volumes':volumelist}
  zpool.append(zdict)
 # for vol in zfslist2:
  for vol in zfslist:
   if b[0]+'/' in vol and '@' not in vol and b[0] in vol:
    volume=vol.split()
    volname=volume[0].split('/')[1]
    snaplist=[]
    zdict={'fullname':volume[0],'name':volname, 'pool': b[0], 'host':myhost, 'creation':' '.join(volume[1:4]+volume[5:6]),'time':volume[4], 'used':volume[6], 'quota':volume[7], 'usedbysnapshots':volume[8], 'refcompressratio':volume[9], 'prot':volume[10],'snapshots':snaplist}
    volumelist.append(zdict)
   elif '@' in vol and b[0] in vol:
    snapshot=vol.split()
    snapname=snapshot[0].split('@')[1]
    zdict={'fullname':snapshot[0],'name':snapname, 'volume':volname, 'pool': b[0], 'host':myhost, 'creation':' '.join(snapshot[1:4]+volume[5:6]), 'time':snapshot[4], 'used':snapshot[6], 'quota':snapshot[7], 'usedbysnapshots':snapshot[8], 'refcompressratio':snapshot[9], 'prot':snapshot[10]}
    snaplist.append(zdict)
    
 elif any(raid in a for raid in raidtypes):
  spaces=len(a.split(a.split()[0])[0])
  disklist=[]
  zdict={ 'name':b[0], 'status':b[1],'disklist':disklist }
  raidlist.append(zdict)
 elif any(raid in a for raid in raid2):
  spaces=len(a.split(a.split()[0])[0])
  disklist=[]
  zdict={ 'name':b[0], 'status':'NA','disklist':disklist }
  raidlist.append(zdict)
 elif 'scsi' in a:
   diskid='-1'
   host='-1'
   size='-1' 
   if  len(a.split('scsi')[0]) < (spaces+2) or (len(raidlist) < 1 and len(zpool)> 0):
    print(spaces,len(a.split('scsi')[0]))
    disklist=[]
    zdict={ 'name':'stripe-'+str(stripecount), 'status':'NA','disklist':disklist }
    raidlist.append(zdict)
    stripecount+=1
   for lss in lsscsi:
    z=lss.split()
    if z[6] in b[0]:
     diskid=lsscsi.index(lss)
     host=z[3].split('-')[1]
     size=z[7]
     print('diskid',diskid,z[6],b[0])
     freepool.remove(lss)
     break
   zdict={'name':b[0], 'status':b[1],'id': str(diskid), 'host':host, 'size':size}
   disklist.append(zdict)
 else:
   zdict={'name':'na','status':a}
if len(freepool) > 0:
 raidlist=[]
 zdict={ 'name':'free', 'status':'free', 'size':'0', 'alloc': '0', 'empty': '0', 'dedup': '0', 'compressratio': '0', 'raidlist': raidlist, 'volumes':[]}
 zpool.append(zdict)
 disklist=[]
 zdict={ 'name':'free', 'status':'free','disklist':disklist }
 raidlist.append(zdict)
 for lss in freepool:
  z=lss.split()
  diskid=lsscsi.index(lss)
  host=z[3].split('-')[1]
  size=z[7]
  zdict={'name':'scsi-'+z[6], 'status':'free','id': str(diskid), 'host':host, 'size':size}
  disklist.append(zdict)
print(zpool)
put('hosts/'+myhost+'/current',str(zpool))
#put('hosts/dhcp31481/current',str(zpool))
