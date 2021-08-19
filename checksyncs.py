#!/bin/python3.6
from logqueue import queuethis
from etcdgetpy import etcdget as get
from etcdput import etcdput as put 
from broadcasttolocal import broadcasttolocal
from etcdputlocal import etcdput as putlocal 
from usersyncall import usersyncall
from groupsyncall import groupsyncall
from socket import gethostname as hostname

syncs = ['user']
myhost = hostname()
hostip = get('ActivePartners/'+myhost)[0]
allsyncs = get('sync','--prefix') 
leader = get('leader','--prefix')[0][0].replace('leader/','')

def checksync():
 global syncs, myhost, allsyncs
 for sync in syncs:
   gsyncs = [ x for x in allsyncs if sync in x[0] ] 
   maxgsync = max(gsyncs, key=lambda x: float(x[1]))
   mysync = [x for x in gsyncs if myhost in str(x) ]
   if len(mysync) < 1:
    mysync = [(-1,-1)]
   mysync = float(mysync[0][1])
   if mysync != float(maxgsync[1]):
    print(mysync, float(maxgsync[1]))
    if sync == 'user':
     print('need sync',maxgsync,hostip)
     usersyncall(hostip)
     groupsyncall(hostip)
     adminuser = get('usershash/admin')[0]
     if myhost != leader:
      putlocal(hostip,'usershash/admin',adminuser)
     put('sync/'+sync+'/'+myhost, str(maxgsync[1]))
     broadcasttolocal('sync/'+sync+'/'+myhost, str(maxgsync[1]))
      
 
if __name__=='__main__':
 checksync()
