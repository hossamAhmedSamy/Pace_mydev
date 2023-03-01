#!/usr/bin/python3
import subprocess, sys
from logqueue import queuethis
from etcdgetpy import etcdget as get
from etcdput import etcdput as put 
from Evacuatelocal import setall
from etcddel import etcddel as dels
from usersyncall import usersyncall
from groupsyncall import groupsyncall, grpfninit
from socket import gethostname as hostname
from etcdsync import synckeys
from time import time as timestamp
from etctocron import etctocron 

syncanitem = ['losthost','replipart','evacuatehost','Snapperiod', 'cron','UsrChange', 'GrpChange', 'user','group','ipaddr', 'namespace', 'tz','ntp','gw','dns','cf' ]
forReceivers = [ 'user', 'group' ]
special1 = [ 'passwd' ]
wholeetcd = [ 'Partnr', 'Snappreiod', 'running','volumes' ]
etcdonly = [ 'cleanlost','balancedtype','sizevol', 'ready','known','alias', 'hostipsubnet', 'leader','allowedPartners','activepool', 'poolsnxt','pools', 'localrun','logged','ActivePartners','configured','pool','nextlead']
syncs = etcdonly + syncanitem + special1 + wholeetcd
##### sync request etcdonly template: sync/Operation/ADD/Del_oper1_oper2_../request Operation_stamp###########
##### sync request syncanitem with bash script: sync/Operation/commandline_oper1_oper2_../request Operation_stamp###########
##### sync request syncanitem with python script: sync/Operation/syncfn_commandline_oper1_oper2_../request Operation_stamp###########
##### synced template for request sync[0]/+node stamp #####################
##### initial sync for known nodes : sync/Operation/initial Operation_stamp #######################
##### synced template for initial sync for known nodes : sync/Operation/initial/node Operation_stamp #######################
##### delete request of same sync if ActivePartners qty reached #######################

def initchecks(leader, leaderip, myhost, myhostip):
    if leader == myhost:
        return leaderip
    else:
        return myhostip

def checksync(hostip='request',*args):
 synctypes[hostip](*args)

def syncinit(leader,leaderip, myhost,myhostip):
 global syncs, syncanitem, forReceivers, etcdonly, allsyncs
 stamp = int(timestamp() + 3600)
 for sync in syncs:
  put(leaderip,'sync/'+sync+'/'+'initial/request',sync+'_'+str(stamp)) 
  put(leaderip,'sync/'+sync+'/'+'initial/request/'+myhost,sync+'_'+str(stamp)) 
 return

def doinitsync(leader,leaderip,myhost, myhostip, syncinfo):
 global syncs, syncanitem, forReceivers, etcdonly, allsyncs
 noinit = [ 'replipart' , 'evacuatehost' ]
 syncleft = syncinfo[0]
 stamp = syncinfo[1]
 sync = syncleft.split('/')[1]
 if sync in syncanitem and sync not in noinit:
    if 'Snapperiod'in sync:
     print('found etctocron')
     etctocron(leaderip)
    if sync in 'user':
     print('syncing all users')
     usersyncall(leader,leaderip,myhost,myhostip) 
    if sync in 'group':
     print('syncing all groups')
     grpfninit(leader,leaderip, myhost,myhostip)
     groupsyncall()
    if sync in ['ipaddr', 'namespace','tz','ntp','gw','dns', 'cf']: 
     cmdline='/TopStor/HostManualconfig'+sync.upper()+" "+" ".join([leader, leaderip, myhost, myhostip]) 
     print('cmd',cmdline)
     result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
 if sync in syncs:
  if sync == 'Partnr':
   synckeys(leaderip, myhostip, 'Partner','Partner')
  else:
   synckeys(leaderip, myhostip, sync,sync)
  print('sycs',sync, myhost)
     
 if sync not in syncs:
  print('there is a sync that is not defined:',sync)
  return 
 put(leaderip,syncleft+'/'+myhost, stamp)
 synckeys(leaderip,myhostip, syncleft, syncleft)

 return


def syncall(leader,leaderip,myhost, myhostip):
 global syncs, syncanitem, forReceivers, etcdonly, allsyncs
 allinitials = get(leaderip,'sync','initial')
 myinitials = [ x for x in allinitials if 'initial' in str(x)  and '/request/dhcp' not in str(x) ] 
 for syncinfo in myinitials:
   doinitsync(leader,leaderip,myhost,myhostip, syncinfo)

 allrequests = get(leaderip,'sync','--prefix')
 otherrequests = [ x for x in allrequests if '/request/dhcp' not in str(x) and 'initial' not in str(x) ] 
 
 for done in otherrequests:
      put(leaderip,done[0]+'/'+myhost,done[1])
      synckeys(leaderip,myhostip, done[0], done[0]) 


 return


def syncrequest(leader,leaderip,myhost, myhostip):
 global syncs, syncanitem, forReceivers, etcdonly,  allsyncs
 allsyncs = get(leaderip,'sync','request') 
 donerequests = [ x for x in allsyncs if '/request/dhcp' in str(x) ] 
 mysyncs = [ x[1] for x in allsyncs if '/request/'+myhost in str(x) or ('request/' and '/'+myhost) in str(x) ] 
 myrequests = [ x for x in allsyncs if x[1] not in mysyncs  and '/request/dhcp' not in x[0] ] 
 if len(myrequests) > 1:
    print(myrequests)
    myrequests.sort(key=lambda x: x[1].split('_')[1], reverse=False)
 print('myrequests', myrequests)
 for syncinfo in myrequests:
  if '/initial/' in str(syncinfo):
   if myhost != leader:
    print(leader,leaderip,myhost,myhostip, syncinfo)
    doinitsync(leader,leaderip,myhost,myhostip, syncinfo)
  else:
   syncleft = syncinfo[0]
   stamp = syncinfo[1]
   sync = syncleft.split('/')[1]
   opers= syncleft.split('/')[2].split('_')
   print('#########################################################################')
   print('the sync',sync)
   if sync in wholeetcd :
    if sync == 'Partnr':
      synckeys(leaderip, myhostip, 'Partner', 'Partner')
    else:
      synckeys(leaderip,myhostip, sync,sync)
   if sync in etcdonly and myhost != leader:
     if opers[0] == 'Add':
      if 'Split' in opers[1]:
       put(myhostip,sync,opers[2].replace(':::','_').replace('::','/'))
      else:
       put(myhostip,sync+'/'+opers[1].replace(':::','_').replace('::','/'),opers[2].replace(':::','_').replace('::','/'))
     else:
      print(sync,opers)
      dels(myhostip,opers[1].replace(':::','_').replace('::','/'),opers[2].replace(':::','_').replace('::','/'))
   if sync in syncanitem:
      if sync in 'Snapperiod' :
       etctocron(leaderip)
      elif 'syncfn' in opers[0]:
       print('opers',opers)
       globals()[opers[1]](*opers[2:])
      else:
       print('opers',opers)
       if sync in ['ipaddr', 'namespace','tz','ntp','gw','dns', 'cf']: 
        cmdline='/TopStor/HostManualconfig'+sync.upper()+" "+" ".join([leader, leaderip, myhost, myhostip]) 
       else:
        cmdline='/TopStor/'+opers[0]+" "+" ".join(opers)
       print('cmd',cmdline)
       result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
   if sync in special1 and myhost != leader :
      cmdline='/TopStor/'+opers[0]+' '+opers[1]+' '+opers[2]
      result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
      #cmdline='/TopStor/'+opers[0].split(':')[1]+' '+result+' '+opers[2] +' '+ opers[3]
      #result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
   if sync not in syncs:
    print('there is a sync that is not defined:',sync)
    return
   put(leaderip,syncleft+'/'+myhost, stamp)
   if myhost != leader:
    put(myhostip, syncleft+'/'+myhost, stamp)
    put(myhostip, syncleft, stamp)
 if myhost != leader:
  dones = get(leaderip,'sync','/request/dhcp')
  otherdones = [ x for x in dones if '/request/dhcp' in str(x) ] 
  localdones = get(myhostip, 'sync', '--prefix')
  for done in otherdones:
   if str(done) not in str(localdones):
    put(myhostip, done[0],done[1])
    put(myhostip, '/'.join(done[0].split('/')[:-1]), done[1])
  deleted = set()
  for done in localdones:
   if done[1] not in str(otherdones) and done[1] not in deleted:
    dels(myhostip, 'sync', done[1])
    deleted.add(done[1])
 else:
  print('hihihihi')
  actives = len(get(myhostip,'ActivePartners','--prefix')) + 1
  print('nononon')
  toprune = [ x for x in allsyncs if 'initial' not in x[0] ]
  toprunedic = dict()
  for prune in toprune:
   if prune[1] not in toprunedic:
    toprunedic[prune[1]] = [1,prune[0]]
   else:
    toprunedic[prune[1]][0] += 1
    toprunedic[prune[1]].append(prune[0])
  for prune in toprunedic:
   if toprunedic[prune][0] >= actives or 'request/'+leader not in str(toprunedic[prune]):
    dels(leaderip,'sync',prune) 
    #print(prune,toprunedic[prune])
  
 return     


runcmd={'Snapperiod':'etctocron'} 
synctypes={'syncinit':syncinit, 'syncrequest':syncrequest, 'syncall':syncall }
if __name__=='__main__':
    leaderip=sys.argv[2]
    myhost=sys.argv[3]
    print('hihih')
    leader = get(leaderip,'leader')[0]
    myhostip = get(leaderip,'ActivePartners/'+myhost)[0]
    if myhost == leader:
        myhostip = leaderip
 
    grpfninit(leader,leaderip, myhost,myhostip)
    synctypes[sys.argv[1]](leader,leaderip, myhost,myhostip)
