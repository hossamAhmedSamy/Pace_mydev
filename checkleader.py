#!/bin/python3.6
import subprocess,sys, os
import json
from time import sleep

def checkleader(key, prefix=''):
 os.environ['ETCDCTL_API']= '3'
 endpoints=''
 data=json.load(open('/pacedata/runningetcdnodes.txt'));
 for x in data['members']:
  endpoints=endpoints+str(x['clientURLs'])[2:][:-2]+','
 endpoints = endpoints[:-1]
 cmdline=['/bin/etcdctl','--user=root:YN-Password_123','--endpoints='+endpoints,'get',key,prefix]
 err = 2
 count = 0
 while count < 3: 
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  err = result.returncode
  if err == 2:
    count += 1
    sleep(1)
  else:
   return result 
 
 from etcdgetlocal import etcdget as getlocal
 from socket import gethostname as hostname
 cmdline='./getmyip.sh'
 myip=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode().replace('\n','')
 print('myip',myip)
 leaderinfo = getlocal(myip,'leader','--prefix')[0]
 leader = leaderinfo[0].replace('leader/','')
 leaderip = leaderinfo[1]
 myhost = hostname() 
 cmdline=['pgrep','-c','leaderlost']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 if result.returncode == '0':
  while err == 2: 
   sleep(1)
   endpoints=''
   data=json.load(open('/pacedata/runningetcdnodes.txt'));
   for x in data['members']:
    endpoints=endpoints+str(x['clientURLs'])[2:][:-2]+','
   endpoints = endpoints[:-1]
   cmdline=['/bin/etcdctl','--user=root:YN-Password_123','--endpoints='+endpoints,'get',key,prefix]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   err = result.returncode
 else:
  cmdline='./leaderlost.sh '+leader+' '+myhost+' '+leaderip+' '+myip
  result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
  endpoints=''
  data=json.load(open('/pacedata/runningetcdnodes.txt'));
  for x in data['members']:
   endpoints=endpoints+str(x['clientURLs'])[2:][:-2]+','
  endpoints = endpoints[:-1]
  cmdline=['/bin/etcdctl','--user=root:YN-Password_123','--endpoints='+endpoints,'get',key,prefix]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 return result 

if __name__=='__main__':
 checkleader(*sys.argv[1:])
