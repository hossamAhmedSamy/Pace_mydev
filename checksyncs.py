#!/usr/bin/python3
import subprocess, sys
from logqueue import queuethis
from etcdgetpy import etcdget as get
from etcdput import etcdput as put 
from Evacuatelocal import setall
from etcddel import etcddel as dels
from usersyncall import usersyncall, usrfninit
from groupsyncall import groupsyncall, grpfninit
from socket import gethostname as hostname
from etcdsync import synckeys
from time import time as timestamp
from etctocron import etctocron 

dirtydic = { 'pool': 0, 'volume': 0 } 
syncanitem = [ 'cversion','priv','dirty','hostdown', 'diskref', 'replipart','evacuatehost','Snapperiod', 'cron','UsrChange', 'GrpChange', 'user','group','ipaddr', 'namespace', 'tz','ntp','gw','dns','cf' ]
forReceivers = [ 'user', 'group' ]
special1 = [ 'passwd' ]
wholeetcd = [ 'localrun','known','nmspce','gateway','deens','enteepe', 'teezee','ceecee', 'pool','pools','cversion', 'needtoreplace','Partnr', 'Snappreiod','leader', 'running','volumes' ]
etcdonly = [ 'cleanlost','balancedtype','sizevol', 'ActPool', 'alias', 'hostipsubnet', 'allowedPartners','activepool', 'poolnxt','pools', 'logged','ActivePartners','configured','ready', 'pool','nextlead']
restartetcd = wholeetcd + etcdonly
replisyncs = ['user','group']
syncs = etcdonly + syncanitem + special1 + wholeetcd
##### sync request etcdonly template: sync/Operation/ADD/Del_oper1_oper2_../request Operation_stamp###########
##### sync request syncanitem with bash script: sync/Operation/commandline_oper1_oper2_../request Operation_stamp###########
##### sync request syncanitem with python script: sync/Operation/syncfn_commandline_oper1_oper2_../request Operation_stamp###########
##### synced template for request sync[0]/+node stamp #####################
##### initial sync for known nodes : sync/Operation/initial Operation_stamp #######################
##### synced template for initial sync for known nodes : sync/Operation/initial/node Operation_stamp #######################
##### delete request of same sync if ActivePartners qty reached #######################
software = 'na'
def insync(leaderip, leader):
    print('checking in sync -------------------')
    isinsync = 1 
    if isinsync == 1:
        mycversion=get(leaderip,'cversion/'+leader)[0]
        allcversion=get(leaderip,'cversion','--prefix')
        readis = get(leaderip,'ready','--prefix')
        for cver in allcversion:
            if cver[1] != mycversion and cver[0].replace('cversion/','') in str(readis):
            #if cver[1] != mycversion and cver[0].replace('cversion/',''): 
                #stampi = str(timestamp())
                #put(leaderip,'sync/cversion/__checksy__/request','cversion_'+stampi)
                isinsync = 0
                break
        #if isinsync == 1:
        #    dels(leaderip,'sync/cversion','--prefix')
    
     
    if isinsync == 1:
        result = get(leaderip,'nodedirty','--prefix')
        if 'dhcp' in str(result):
            isinsync = 0 
    if isinsync == 1:
        allsyncs=get(leaderip,'sync','--prefix')
        allsyncs=[x for x in allsyncs if 'initial' not in x[0] ]
        for sync in allsyncs:
            syncgroup = [ x for x in allsyncs if sync[1] in x[1] and 'cversion' not in x[0] ]
            initrequest = [ x for x in syncgroup if 'request/dhcp' not in x[0] ]
            if len(syncgroup) > 0 and len(initrequest) == 0:
                print('to delete', sync)
                dels(leaderip,'sync',sync[1])
                isinsync = 0
                break
            if len(syncgroup) > 0:
                isinsync = 0 
                break
    if isinsync:
        print('the cluster is in sync')
        put(leaderip,'isinsync', 'yes')
    else:
        print('some nodes still syncing')
        put(leaderip,'isinsync', 'no')
        
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

def doinitsync(leader,leaderip,myhost, myhostip, syncinfo,pullsync):
 global syncs, syncanitem, forReceivers, etcdonly, allsyncs
 noinit = [ 'cversion', 'replipart' , 'evacuatehost','hostdown' ]
 syncleft = syncinfo[0]
 stamp = syncinfo[1]
 if 'pullsync' in pullsync:
    syncleft = syncleft.replace(pullsync,'')
 sync = syncleft.split('/')[1]
 flag = 1
 if sync in syncanitem and sync not in noinit:
    if 'Snapperiod'in sync:
     print('found etctocron')
     synckeys(leaderip,myhostip, sync,sync)
     etctocron(leaderip)
    if sync in 'user':
     print('syncing all users')
     usrfninit(leader,leaderip, myhost,myhostip)
     usersyncall(pullsync) 
     synckeys(leaderip, myhostip, pullsync+'user', 'user')
    if sync in 'group':
     print('syncing all groups')
     grpfninit(leader,leaderip, myhost,myhostip)
     groupsyncall(pullsync)
    if sync in ['tz','ntp','gw','dns']: 
     cmdline='/TopStor/HostManualconfig'+sync.upper()+" "+" ".join([leader, leaderip, myhost, myhostip]) 
     print('cmd',cmdline)
     result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
    if sync == 'priv':
        user=syncleft.split('/')[2]
        synckeys(leaderip, myhostip, 'usersinfo/'+user, 'usersinfo/'+user)
        newinfo = get(myhostip,'usersinfo/'+user)[0]
        oldinfo = get(leaderip, 'usersinfo/'+user)[0]
        if oldinfo != newinfo:
            flag = 0

 if sync in syncs:
  if sync == 'Partnr':
   synckeys(leaderip, myhostip, 'Partner','Partner')
  else:
   synckeys(leaderip, myhostip, pullsync+sync,sync)
  print('sycs',sync, myhost)
     
 if sync not in syncs:
  print('there is a sync that is not defined:',sync)
  return 
 if flag:
    put(leaderip,pullsync+syncleft+'/'+myhost, stamp)
 synckeys(leaderip,myhostip, pullsync+syncleft, syncleft)

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


def syncrequest(leader,leaderip,myhost, myhostip,pullsync=''):
 global syncs, syncanitem, forReceivers, etcdonly,  allsyncs
 if 'pullsync' in pullsync:
    print('***************************************************************************')
    print('syncing replication data')
    print('***************************************************************************')

 flag=1
 if leader == myhost:
    etcdip = leaderip
    if 'pullsync' in pullsync:
        clusterhost = leaderip
    else:
        clusterhost = myhost
 else:
    etcdip = myhostip
 allsyncs = get(leaderip,pullsync+'sync','request') 
 print("get("+leaderip+",pullsync+sync','request')")
 print('pallysncs',pullsync, allsyncs)
 donerequests = [ x for x in allsyncs if '/request/dhcp' in str(x) ] 
 mysyncs = [ x[1] for x in allsyncs if '/request/'+myhost in str(x) or ('request/' and '/'+clusterhost) in str(x) ] 
 myrequests = [ x for x in allsyncs if x[1] not in mysyncs  and '/request/dhcp' not in x[0] ] 
 if len(myrequests) > 1:
    print('multiple requests',myrequests)
    myrequests.sort(key=lambda x: x[1].split('_')[1], reverse=False)
 print('myrequests', myrequests)
 rebootflag = 0
 if 'sync/namespace' in str(myrequests) and 'sync/ipaddr' in str(myrequests):
  rebootflag = 2
  put(leaderip,'rebootwait/'+myhost,'pls')
 for syncinfo in myrequests:
  flag = 1
  if  len(syncinfo[0]) == 1:
    continue
  if '/initial/' in str(syncinfo):
   if myhost != leader or 'pullsync' in pullsync:
    print(leader,leaderip,myhost,myhostip, syncinfo)
    doinitsync(leader,leaderip,myhost,myhostip, syncinfo,pullsync)
   elif myhost != leader:
    syncinit(leader,leaderip, myhost,myhostip)
  else:
   syncleft = syncinfo[0]
   stamp = syncinfo[1]
   print('syncleft',syncleft)
   if 'pullsync' in pullsync:
    syncleft = syncleft.replace(pullsync,'')
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
       print('oper', opers, sync)
       put(myhostip,sync+'/'+opers[1].replace(':::','_').replace('::','/'),opers[2].replace(':::','_').replace('::','/'))
     else:
      print(sync,opers)
      if 'ready' not in sync:
        dels(myhostip,opers[1].replace(':::','_').replace('::','/'),opers[2].replace(':::','_').replace('::','/'))
   if sync in syncanitem:
      if sync in 'cversion':
        cmdline='/TopStor/systempull.sh '+opers[1]
        result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
      elif sync in 'Snapperiod' :
       synckeys(leaderip,myhostip, sync,sync)
       etctocron(leaderip)
      elif sync in 'diskref':
        cmdline='/pace/diskchange.sh '+' checksync'+' '+opers[0]+' '+opers[1]
        print('diskref',cmdline)
        result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
      elif sync in 'hostdown':
        cmdline='/pace/hostdown.sh '+opers[0]
        result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
      elif sync in 'dirty':
        for dirt in dirtydic:
            put(etcdip, 'dirty/'+dirt, str(dirtydic[dirt]))
      elif 'syncfn' in opers[0]:
       print('opers',opers)
       globals()[opers[1]](*opers[2:])
      elif sync == 'priv':
        user=syncleft.split('/')[2]
        synckeys(leaderip, myhostip, 'usersinfo/'+user, 'usersinfo/'+user)
        newinfo = get(myhostip,'usersinfo/'+user)[0]
        oldinfo = get(leaderip, 'usersinfo/'+user)[0]
        if oldinfo != newinfo:
            flag = 0
 
      else:
       print('opers',opers)
       if sync in ['ipaddr', 'namespace','tz','ntp','gw','dns', 'cf']: 
        if sync in [ 'namespace', 'ipaddr' ]:
         rebootflag -=rebootflag
         if rebootflag == 0:
            dels(leaderip,'rebootwait/'+myhost)
        cmdline='/TopStor/HostManualconfig'+sync.upper()+" "+" ".join([leader, leaderip, myhost, myhostip]) 
        print('cmdline',cmdline)
       else:
        cmdline='/TopStor/'+opers[0]+" "+" ".join(opers[1:])
       print('cmd',cmdline)
       result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
   #if sync in special1 and myhost != leader :
   if sync in special1 :
      cmdline='/TopStor/'+opers[0]+' '+opers[1]+' '+opers[2]
      result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
      #cmdline='/TopStor/'+opers[0].split(':')[1]+' '+result+' '+opers[2] +' '+ opers[3]
      #result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
   if sync not in syncs:
    print('there is a sync that is not defined:',sync)
    return
   if flag:
    put(leaderip,pullsync+syncleft+'/'+myhost, stamp)
   if myhost != leader:
    put(myhostip, syncleft+'/'+myhost, stamp)
    put(myhostip, syncleft, stamp)
   elif myhsot == leader and 'pullsync' in pullsync:
    put(leaderip,pullsync+syncleft+'/'+myhost, stamp)
     
 cmdline = '/TopStor/getcversion.sh '+leaderip+' '+leader+' '+myhost+' '+'checksync'
 subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT)
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
  actives = len(get(myhostip,'ActivePartners','--prefix')) 
  readis = len(get(leaderip,'ready','--prefix')) 
  readisonly = ('leader','next','ActivePartners', 'alias','nextlead', 'hostdown','pool','volume', '/dirty', 'running','/ready/', 'diskref', '/add')
  print('pruuuuuuuuuuuuuuuuuuuuuning')
  toprune = [ x for x in allsyncs if 'initial' not in x[0] ]
  dhcps = [x[1] for x in allsyncs if 'request/dhcp' in x[0] ]
  requests = [ x[1] for x in allsyncs if 'request/dhcp' not in x[0] ]
  notrights = [ x for x in dhcps if x not in requests ]
  print('ddddddddddddddddddddddddddddddddddddddddddddddddddd')
  print(notrights)
  for notr  in notrights:
    dels(leaderip, 'sync', notr)
  print('ddddddddddddddddddddddddddddddddddddddddddddddddddd')
  toprunedic = dict()
  for prune in toprune:
   if prune[1] not in toprunedic:
    toprunedic[prune[1]] = [1,prune[0]]
   else:
    toprunedic[prune[1]][0] += 1
    toprunedic[prune[1]].append(prune[0])
  print('toproune check',toprunedic)
  for prune in toprunedic:
   isinreadis = [ x for x in readisonly if x in str(toprunedic[prune][1:]) ]
   #if toprunedic[prune][0] >= actives or 'request/'+leader not in str(toprunedic[prune]):
   #print('actives:',actives,'prune',prunex, 'ready/Del' in str(toprunedic[prune][1:]))
   #if toprunedic[prune][0] > actives or ((('ready' in str(toprunedic[prune][1:])) or ('Del' in str(toprunedic[prune][1:])) or ('hostdown' in str(toprunedic[prune][1:]))) and toprunedic[prune][0] > readis):
   if toprunedic[prune][0] > actives or ( len(isinreadis) > 0 and toprunedic[prune][0] > readis):
    dels(leaderip,'sync',prune) 
  insync(leaderip, leader) 
    #print(prune,toprunedic[prune])
 if myhost == leader and 'pullsync' not in pullsync:
    syncrequest(leader,leaderip,myhost, myhostip,pullsync='pullsync/')
 return     

def restetcd(leader,leaderip, myhost,myhostip):
    if myhost == leader:
        return
    for sync in wholeetcd :
        if sync == 'Partnr':
            synckeys(leaderip, myhostip, 'Partner', 'Partner')
        else:
            synckeys(leaderip,myhostip, sync,sync)
 
runcmd={'Snapperiod':'etctocron'} 
synctypes={'syncinit':syncinit, 'syncrequest':syncrequest, 'syncall':syncall , 'restetcd': restetcd}
if __name__=='__main__':
    leaderip=sys.argv[2]
    myhost=sys.argv[3]
    leader = get(leaderip,'leader')[0]
    myhostip = get(leaderip,'ActivePartners/'+myhost)[0]
    if myhost == leader:
        myhostip = leaderip
 
    grpfninit(leader,leaderip, myhost,myhostip)
    usrfninit(leader,leaderip, myhost,myhostip)
    synctypes[sys.argv[1]](leader,leaderip, myhost,myhostip)
