#!/bin/python3.6
import subprocess,sys, os
import json
from time import sleep

def etcdget(key, prefix=''):
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
   print('ok')
   return 'ok'
 print('dead')
 return 'dead'

if __name__=='__main__':
 etcdget(*sys.argv[1:])
