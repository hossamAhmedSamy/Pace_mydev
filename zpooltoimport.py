#!/usr/bin/python3
import subprocess, sys
from ioperf import ioperf
from logqueue import queuethis, initqueue
from etcdput import etcdput as put
from etcdgetpy import etcdget as get 
from etcddel import etcddel as dels
from poolstoimport import getpoolstoimport
from time import time as stamp
from time import sleep
from ast import literal_eval as mtuple


#leader=get('leader','--prefix')[0][0].split('/')[1]
stampi = str(stamp())

def selecthosting(minhost,hostname,hostpools):
 if len(hostpools) < minhost[1]:
  minhost = (hostname, len(hostpools))
 return minhost


def dosync(sync, *args):
  global leader, leaderip, myhost, myhostip, etcdip
  #dels(leaderip, sync)  
  put(leaderip, *args)
  put(leaderip, args[0]+'/'+leader,args[1])
  return 

def selecthost(pool,readies,cpools):
    selectedhost = [ 10000,'' ]
    print('cpools',cpools)
    for hostinfo in readies:
        print('hostinfo',readies)
        host = hostinfo[0].split('/')[1]
        counts = list(str(cpools)).count(host)
        if selectedhost[0] > counts:
            selectedhost =  [ counts, [ host ] ]
        elif selectedhost[0] == counts:
            selectedhost[1] = selectedhost[1] + [ host ]
    print('select host', selectedhost)
    return selectedhost[1]
        
def zpooltoimport(*args):
 global leader, leaderip, myhost, myhostip, etcdip
 if args[0]=='init':
     leader = args[1]
     leaderip = args[2]
     myhost = args[3]
     myhostip = args[4]
     etcdip = args[5]
     initqueue(leaderip, myhost) 
     return

 nextpools=get(leaderip, 'poolsnxt', '--prefix') 
 if 'not reachable' in str(nextpools):
        return
 needtoimport=[ x for x in nextpools if myhost in str(x)] 
 if 'not reachable' in str(needtoimport):
        return
 pools = get(leaderip, 'pools/','--prefix')
 if 'not reachable' in str(pools):
        return
 if myhost not in str(needtoimport):
  print('no need to import a pool here')
                  
 else:
  for poolline in needtoimport:
   pool = poolline[0].replace('poolsnxt/','')
   if pool in str(pools):
    continue
   ioperf(leaderip, myhost)
   print('pool to be imported now', pool)
   put(leaderip, 'pools/'+pool,myhost)
   cmdline= '/usr/sbin/zpool import  '+pool
   result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
   sleep(1)
   cmdline= '/usr/sbin/zpool status  '
   result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
   print('result',result)
   if pool in result:
    put(etcdip, 'dirty/volume','0')
    print('before sync')
    dosync('pools_', 'sync/pools/Add_'+pool+'_'+myhost+'/request','pools_'+str(stamp()))
    print('pools_', 'sync/pools/Add_'+pool+'_'+myhost+'/request','pools_'+str(stamp()))
    print('After sync')
    #cmdline= 'systemctl restart zfs-zed  '
    #result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
   else:
    dels(leaderip, 'pools/',pool)
        
   dels(leaderip, 'poolsnxt',pool)
    
 if myhost != leader:
  return

 hosts=get(leaderip,'host','/current')
 
 cpools = [poolinfo[0].split('/')[1]+'_'+poolinfo[1] for poolinfo in pools ]
 cpools = cpools + getpoolstoimport()
 print('with imported pools',cpools)
 readies=get(etcdip,'ready','--prefix')
 for poolinfo in cpools:
    pool = poolinfo.split('_')[0]
    if pool not in str(needtoimport):
        nxthosts=selecthost(pool,readies,cpools)
        poolsnxt=get(leaderip,'poolsnxt/'+pool)[0]
        if poolsnxt in str(nxthosts):
            continue 
        print('hihihih',nxthosts,pool)
        for nxthost in nxthosts:
            if nxthost not in str(poolinfo):
                hostnxtpools = [ x for x in nextpools if nxthost in str(x) ]
                print('hostnxtpools',hostnxtpools,pool)
                if pool not in str(hostnxtpools):
                    print('adding')
                    dels(leaderip,'poolsnxt/'+pool)
                    put(leaderip,'poolsnxt/'+pool,nxthost)
                    dosync('poolsnxt', 'sync/poolsnxt/Add_'+pool+'_'+nxthost+'/request','poolsnxt_'+str(stamp()))
                    break
 return
     
       
if __name__=='__main__':
    cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py leader'
    leader=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
    cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py leaderip'
    leaderip=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
    cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py clusternode'
    myhost=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
    cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py clusternodeip'
    myhostip=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
    if leader == myhost:
        etcdip = leaderip 
    else:
        etcdip = myhostip
    zpooltoimport('hi')
 #cmdline='cat /pacedata/perfmon'
 #perfmon=str(subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout)
 #if '1' in perfmon:
 # queuethis('zpooltoimport.py','start','system')
 #if '1' in perfmon:
 # queuethis('zpooltoimport.py','stop','system')
