#!/usr/bin/python3
from etcddel import etcddel as etcddel
from etcdput import etcdput as put 
from etcdgetpy import etcdget as get 
import sys, subprocess

def toonline(*args):
# myhostorg=socket.gethostname()
# myhost='run/'+myhostorg
 allinfo=get('run','--prefix')
 disks=[x for x in allinfo if 'uuid' in str(x)]
 free=[x for x in disks if 'free' in str(x) and '/-1/' not in str(x)]
 if len(free) < 1:
  return
 faulty=[(x[0].split('/')[5],x[1]) for x in disks if '/-1/' in str(x)]
 notfree=[(x[0].split('/')[5],x[1],x[0].split('/')[3]) for x in disks if 'free' not in str(x) and '/-1/' not in str(x)]
 if len(notfree) < 1:
  return
 status=[x[0].split('/')[5] for x in allinfo if 'DEGRADED' in str(x) and 'status' in str(x) and 'disk' not in str(x)]
 stripes=[x[0].split('/')[5] for x in allinfo if 'type' in str(x) and 'stripe' in str(x) and 'disk' not in str(x)]
 newstatus=stripes+status
 if len(newstatus) < 1:
  return
 degraded=[x for x in notfree if x[0] in status]
 striped=[x for x in notfree if x[0] in stripes]
 z=[]
 print('status=',status)
 if len(faulty) > 0:
  for sta in status:
   dinsta=[x for x in notfree if '/raid/'+str(sta) in str(x)]
   print('compare=',str(faulty), str(sta))
   fau=[x for x in faulty if str(x[0]) == str(sta) ]
   print('fau=',fau)
   if len(fau) < 1:
    continue;
   deg=[x for x in degraded if x[0]==fau[0][0]]
   z.append((fau[0][1],deg[0][1],free[0][1],deg[0][2]))
   print(z)
   print(len(z))
   del free[0]
   if len(free) < 1:
    break 
  for x in z:
   cmdline='/sbin/zpool detach '+x[3]+' '+x[0]
   subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
   print(cmdline)
   if len(dinsta)< 2:
    cmdline='/sbin/zpool labelclear /dev/disk/by-id/'+x[1]
    subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
    print(cmdline)
    cmdline='/sbin/zpool attach -f '+x[3]+' '+x[1]+' '+x[2]
    subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
    print(cmdline)
   print('###############')
 if len(free) < 1:
  return
 z2=[]
 for strdisk in striped:
  print('strdisk',strdisk)
  z2.append((strdisk[1],free[0][1],strdisk[2]))
  del free[0]
  if len(free) < 1:
   break 
 for x in z2:
  cmdline='/sbin/zpool labelclear /dev/disk/by-id/'+x[1]
  subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
  print(cmdline)
  cmdline='/sbin/zpool attach -f '+x[2]+' '+x[0]+' '+x[1]
  subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
  print(cmdline)
  print('###############')
  
  
  
 return
if __name__=='__main__':
 toonline(*sys.argv[1:])
#msg='no pools \n'
#with open('/root/putzpooltmp','a') as f:
# f.write(str(msg)+"\n")
