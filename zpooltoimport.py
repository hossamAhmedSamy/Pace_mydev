#!/usr/bin/python3
import subprocess, sys
from ioperf import ioperf
from logqueue import queuethis
from etcdput import etcdput as put
from etcdgetlocalpy import etcdget as get 
from etcdgetpy import etcdget as getp 
from etcddel import etcddel as dels
from poolstoimport import getpoolstoimport
from time import time as stamp
from ast import literal_eval as mtuple


#leader=get('leader','--prefix')[0][0].split('/')[1]
stamp = str(stamp())

leaderip = get('leaderip')[0]
def selecthost(minhost,hostname,hostpools):
 if len(hostpools) < minhost[1]:
  minhost = (hostname, len(hostpools))
 return minhost


def dosync(leader,sync, *args):
  dels(leaderip, sync)  
  put(leaderip, *args)
  put(leaderip, args[0]+'/'+leader,args[1])
  return 

def zpooltoimport(leader, myhost):
 needtoimport=get('poolsnxt', myhost) 
 cpools = get('pools/','--prefix')
 if myhost not in str(needtoimport):
  print('no need to import a pool here')
 else:
  for poolline in needtoimport:
   pool = poolline[0].replace('poolsnxt/','')
   if pool in str(cpools):
    continue
   ioperf()
   print('pool', pool)
   cmdline= '/usr/sbin/zpool import  '+pool
   result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
   cmdline= '/usr/sbin/zpool status  '
   result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
   if pool in result:
    put(leaderip, 'pools/'+pool,myhost)
    dosync(leader,'pools_', 'sync/pools/Add_'+pool+'_'+myhost+'/request','pools_'+stamp)
    #cmdline= 'systemctl restart zfs-zed  '
    #result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
   dels(leaderip, 'poolsnxt',pool)
    
 if myhost != leader:
  return

 knowns=get('ready','--prefix')
 hosts=getp(leaderip,'hosts','/current')
 pools = getpoolstoimport()
 needtoimport=get('poolsnxt', '--prefix') 
 for pool in pools:
  if pool not in str(needtoimport):
   minhost=(myhost,float('inf'))
   for host in hosts: 
    hostname = host[0].split('/')[1]
    hostpools=mtuple(host[1])
    minhost = selecthost(minhost,hostname,hostpools)
   put(leaderip, 'poolsnxt/'+pool,minhost[0])
 return
     
       
if __name__=='__main__':
 if len(sys.argv) > 1:
  leader = sys.argv[1]
  myhost = sys.argv[2]
 else:
  leader=get('leader')[1]
  myhost = get('clusternode') 

 #cmdline='cat /pacedata/perfmon'
 #perfmon=str(subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout)
 #if '1' in perfmon:
 # queuethis('zpooltoimport.py','start','system')
 zpooltoimport(leader, myhost)
 #if '1' in perfmon:
 # queuethis('zpooltoimport.py','stop','system')
