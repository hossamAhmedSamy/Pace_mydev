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
from etcddellocal import etcddel as dellocal
from deltolocal import deltolocal
from usersyncall import usersyncall, oneusersync
from groupsyncall import groupsyncall, onegroupsync
from socket import gethostname as hostname

syncanitem = ['Partner','Snapperiod','user','group','host','passwd']
forReceivers = [ 'user', 'group' ]
nodeprops =  ['dataip','tz','ntp','gw','dns']
etcdonly = ['sizevol','ready','alias', 'dataip','hostipsubnet', 'namespace','leader','allowedPartners','activepool','ipaddr','pools','poolnsnxt','volumes','localrun','logged','ActivePartners','config','pool','nextlead']
syncs = etcdonly + syncanitem + nodeprops
myhost = hostname()
actives = get('ActivePartners','--prefix')
Partners = get('Partners/','--prefix')
hostip = get('ActivePartners/'+myhost)[0]
allsyncs = get('sync','request') 
donerequests = [ x for x in allsyncs if '/request/dhcp' in str(x) ] 
mysyncs = [ x for x in allsyncs if '/request/'+myhost in str(x) ] 
myrequests = [ x for x in allsyncs if x not in mysyncs ] 
leader = get('leader','--prefix')[0][0].replace('leader/','')
##### sync request template: sync/Operation/commandline_op1_op2_../request Operation_stamp###########
##### synced template for request sync[0]/+node stamp #####################
##### initial sync for known nodes : sync/Operation/initial Operation_stamp #######################
##### synced template for initial sync for known nodes : sync/Operation/initial/node Operation_stamp #######################
##### delete request of same sync if ActivePartners qty reached #######################

def checksync(myip='nothing'):
 global syncs, syncanitem, forReceivers, nodeprops, etcdony, myhost, allsyncs, hostip, actives
 if myip='initial':
  for sync in syncs:
   from time import time as timestamp
   stamp = int(timestamp() + 3600)
   put('sync/'+sync+'/'+'initial',str(stamp)) 
   put('sync/'+sync+'/'+'initial/'+myhost,str(stamp)) 
  return
 for syncinfo in myrequests:
   syncleft = syncinfo[0]
   syncright = syncinfo[1]
   sync = syncleft.split('/')[1]
   cmdinfo = syncleft.split('/')(2).split('_')
   if sync == 'user':
     oneusersync(cmdinfo[0],cmdinfo[1])
   elif sync == 'group':
     onegroupsync(cmdinfo[0],cmdinfo[1])
   elif sync == 'evacuatehost':
    setall(cmdinfo[0],cmdinfo[1],cmdinfo[2])
   elif sync in nodeprops:
    cmdline='/TopStor/pump.sh HostManualconfig'+sync+'local '
    result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
   elif 'Snapperiod' in sync:
     from etctocron import etctocron
     if myhost != leader:
      if cmdline[0] == 'Add':
       syncitem=get('Snapperiod',cmdline[1])
       putlocal(myip,syncitem[0],syncitem[1])
      else:
       dellocal('Snapperiod',cmdline[1])
     etctocron()
    elif 'Partner' in sync:
     #cmdline='/TopStor/pump.sh PartnerSync.py '+maxgsync[0].split('/')[1].split('_')[1] 
     cmdline='/TopStor/pump.sh PartnerSync.py ' 
     result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
    elif 'PartnerDel' in sync:
     cmdline='/TopStor/pump.sh PartnerDel '+maxgsync[0].split('/')[1].split('_')[1]+' yes '+maxgsync[0].split('/')[1].split('_')[2]
     result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
     
    elif sync in etcdonly:
     cmdline='/TopStor/pump.sh etcdsync.py '+hostip+' '+sync+' '+sync
     result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
      
    newsync=maxgsync[0].split('/')[1]
    put('sync/'+newsync+'/'+myhost, str(maxgsync[1]))
    broadcasttolocal('sync/'+newsync+'/'+myhost, str(maxgsync[1]))
  
      
 
if __name__=='__main__':
 checksync(*sys.argv[1:])
