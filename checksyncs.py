#!/bin/python3.6
import subprocess, sys
from logqueue import queuethis
from etcdgetpy import etcdget as get
from etcdput import etcdput as put 
from broadcasttolocal import broadcasttolocal
from etcdputlocal import etcdput as putlocal 
from etcdgetlocal import etcdget as getlocal 
from Evacuatelocal import setall
from etcddel import etcddel as dels
from deltolocal import deltolocal
from usersyncall import usersyncall
from groupsyncall import groupsyncall
from socket import gethostname as hostname

syncs = ['Partnernode','PartnerAdd','Snapperioddel','Snapperiod','ready','leader','alias', 'user','group','evacuatehost','dataip','tz','ntp','gw','hostipsubnet','dnsname','dnssearch', 'namespace', 'known', 'allowedPartners', 'activepool', 'ipaddr', 'pools', 'poolsnxt', 'namespace', 'volumes', 'dataip', 'localrun', 'logged','uplogged', 'uplogged', 'ActivePartners', 'config', 'Parnter', 'pool', 'nextlead', 'snapperiod']
collectedsyncs = ['alias']
myhost = hostname()
actives = get('ActivePartners','--prefix')
hostip = get('ActivePartners/'+myhost)[0]
allsyncs = get('sync','--prefix') 
leader = get('leader','--prefix')[0][0].replace('leader/','')

def checksync(myip='nothing'):
 global syncs, myhost, allsyncs, hostip, actives
 for sync in syncs:
#   gsyncs = [ x for x in allsyncs if sync in x[0] ] 
   gsyncs = [ x for x in allsyncs if sync in x[0] ] 
   if myhost == leader and  len(gsyncs) == 0:
    from time import time as timestamp
    stamp = int(timestamp() + 3600)
    put('sync/'+sync+'/'+leader,str(stamp)) 
   if myhost == leader and len(gsyncs) == 1:
     dels('modified',sync)
   if len(gsyncs) == 0:
    continue 
   if myip != 'nothing':
    hostip = myip
   maxgsync = max(gsyncs, key=lambda x: float(x[1]))
   mingsync = min(gsyncs, key=lambda x: float(x[1]))
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
    elif sync in ['dataip','tz','ntp','gw','dnsname','dnssearch','alias']:
     cmdline='/TopStor/pump.sh HostManualconfig'+sync+'local ll'
     result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
    elif 'Snapperioddel' in sync:
     partner=maxgsync[0].split('/')[1].split('_')[1]
     userreq=maxgsync[0].split('/')[1].split('_')[2]
     cmdline='/TopStor/pump.sh PartnerDel '+partner+' yes '+userreq 
     result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
    elif 'PartnerAdd' in sync:
     cmdline='/TopStor/pump.sh PartnerSync.py '+maxgsync[0].split('/')[1].split('_')[1] 
     result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
    elif 'repliPartnerDel' in sync:
     cmdline='/TopStor/pump.sh repliPartnerDel '+maxgsync[0].split('/')[1].split('_')[1]+' yes '+maxgsync[0].split('/')[1].split('_')[2]
     result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
     
    elif sync in [ 'hostipsubnet','Snapperiod','ready','leader','known', 'allowedPartners', 'activepool', 'ipaddr', 'pools', 'poolsnxt', 'namespace', 'volumes', 'dataip', 'localrun', 'logged','uplogged', 'uplogged', 'ActivePartners', 'config', 'Parnter', 'pool', 'nextlead', 'snapperiod']:
     print('normal known leader..etc')
     cmdline='/TopStor/pump.sh etcdsync.py '+hostip+' '+sync+' '+sync
     result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
      
    newsync=maxgsync[0].split('/')[1]
    put('sync/'+newsync+'/'+myhost, str(maxgsync[1]))
    broadcasttolocal('sync/'+newsync+'/'+myhost, str(maxgsync[1]))
  
      
 
if __name__=='__main__':
 checksync(*sys.argv[1:])
