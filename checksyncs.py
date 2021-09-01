#!/bin/python3.6
import subprocess, sys
from logqueue import queuethis
from etcdgetpy import etcdget as get
from etcdput import etcdput as put 
from broadcasttolocal import broadcasttolocal
from etcdputlocal import etcdput as putlocal 
from Evacuatelocal import setall
from usersyncall import usersyncall
from groupsyncall import groupsyncall
from socket import gethostname as hostname

syncs = ['user','group','evacuatehost','dataip','tz','ntp','gw']
myhost = hostname()
hostip = get('ActivePartners/'+myhost)[0]
allsyncs = get('sync','--prefix') 
leader = get('leader','--prefix')[0][0].replace('leader/','')

def checksync(myip='nothing'):
 global syncs, myhost, allsyncs, hostip
 for sync in syncs:
   gsyncs = [ x for x in allsyncs if sync in x[0] ] 
   if len(gsyncs) == 0:
    return
   if myip != 'nothing':
    hostip = myip
    
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
       setall()
    elif sync in ['dataip','tz','ntp','gw']:
     cmdline='/TopStor/HostManualconfig'+sync+local  
     result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
      
    print('hi')
    put('sync/'+sync+'/'+myhost, str(maxgsync[1]))
    broadcasttolocal('sync/'+sync+'/'+myhost, str(maxgsync[1]))
      
 
if __name__=='__main__':
 checksync(*sys.argv[1:])
