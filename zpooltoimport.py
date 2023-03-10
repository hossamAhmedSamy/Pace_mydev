#!/usr/bin/python3
import subprocess, sys
from ioperf import ioperf
from logqueue import queuethis, initqueue
from etcdput import etcdput as put
from etcdgetpy import etcdget as get 
from etcddel import etcddel as dels
from poolstoimport import getpoolstoimport
from time import time as stamp
from ast import literal_eval as mtuple


#leader=get('leader','--prefix')[0][0].split('/')[1]
stamp = str(stamp())

def selecthost(minhost,hostname,hostpools):
 if len(hostpools) < minhost[1]:
  minhost = (hostname, len(hostpools))
 return minhost


def dosync(leader,sync, *args):
  global leaderip, myhost
  dels(leaderip, sync)  
  put(leaderip, *args)
  put(leaderip, args[0]+'/'+leader,args[1])
  return 

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

 needtoimport=get(etcdip, 'poolsnxt', myhost) 
 cpools = get(etcdip, 'pools/','--prefix')
 if myhost not in str(needtoimport):
  print('no need to import a pool here')
 else:
  for poolline in needtoimport:
   pool = poolline[0].replace('poolsnxt/','')
   if pool in str(cpools):
    continue
   ioperf(leaderip, myhost)
   print('pool', pool)
   cmdline= '/usr/sbin/zpool import  '+pool
   result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
   cmdline= '/usr/sbin/zpool status  '
   result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
   if pool in result:
    put(leaderip, 'pools/'+pool,myhost)
    put(etcdip, 'dirty/volume','0')
    dosync(leader,'pools_', 'sync/pools/Add_'+pool+'_'+myhost+'/request','pools_'+stamp)
    #cmdline= 'systemctl restart zfs-zed  '
    #result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
   dels(leaderip, 'poolsnxt',pool)
    
 if myhost != leader:
  return

 knowns=get(etcdip, 'ready','--prefix')
 hosts=get(leaderip,'host','/current')
 pools = getpoolstoimport()
 print('pools',pools)
 needtoimport=get(etcdip, 'poolsnxt', '--prefix') 
 for pool in pools:
  print('found', pool)
  if pool not in str(needtoimport):
   minhost=(myhost,float('inf'))
   for host in hosts: 
    hostname = host[0].split('/')[1]
    hostpools=mtuple(host[1])
    minhost = selecthost(minhost,hostname,hostpools)
    put(leaderip, 'poolsnxt/'+pool,minhost[0])
    dosync(leader,'poolnxt_', 'sync/poolsnxt/Add_'+pool+'_'+minhost[0]+'/request','poolnxt_'+stamp)
 return
     
       
if __name__=='__main__':
    if len(sys.argv) > 1:
        leader = sys.argv[1]
        leaderip = sys.argv[2]
        myhost = sys.argv[3]
        myhostip = sys.argv[4]
        etcdip = sys.argv[5]
        

        zpooltoimport(*sys.argv)
 #cmdline='cat /pacedata/perfmon'
 #perfmon=str(subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout)
 #if '1' in perfmon:
 # queuethis('zpooltoimport.py','start','system')
 #if '1' in perfmon:
 # queuethis('zpooltoimport.py','stop','system')
