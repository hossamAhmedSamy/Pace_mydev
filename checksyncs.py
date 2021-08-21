#!/bin/python3.6
from logqueue import queuethis
from etcdgetpy import etcdget as get
from etcdput import etcdput as put 
from broadcasttolocal import broadcasttolocal
from etcdputlocal import etcdput as putlocal 
from usersyncall import usersyncall
from groupsyncall import groupsyncall
from socket import gethostname as hostname

syncs = ['user','group','evacuatehost']
myhost = hostname()
hostip = get('ActivePartners/'+myhost)[0]
allsyncs = get('sync','--prefix') 
leader = get('leader','--prefix')[0][0].replace('leader/','')

def checksync():
 global syncs, myhost, allsyncs
 for sync in syncs:
   gsyncs = [ x for x in allsyncs if sync in x[0] ] 
   if len(gsyncs) == 0:
    return
   maxgsync = max(gsyncs, key=lambda x: float(x[1]))
   mysync = [x for x in gsyncs if myhost in str(x) ]
   if len(mysync) < 1:
    mysync = [(-1,-1)]
   mysync = float(mysync[0][1])
   if mysync != float(maxgsync[1]):
    if sync == 'user':
     if mysync == -1:
      usersyncall(hostip)
     else:
      usersyncall(hostip,'check')
     adminuser = get('usershash/admin')[0]
     if myhost != leader:
      putlocal(hostip,'usershash/admin',adminuser)
    elif sync == 'group':
     if mysync == -1:
      groupsyncall(hostip)
     else: 
      groupsyncall(hostip,'check')
    elif sync == 'evacuatehost':
      hosts = get('modified','evacuatehost')
      for hostn in hosts:
       cmdline=['/pace/removetargetdisks.sh', hostn.split('/')[2], hostn[1]]
       result=subprocess.run(cmdline,stdout=subprocess.PIPE)
      
    put('sync/'+sync+'/'+myhost, str(maxgsync[1]))
    broadcasttolocal('sync/'+sync+'/'+myhost, str(maxgsync[1]))
      
 
if __name__=='__main__':
 checksync()
