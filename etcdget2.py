#!/usr/bin/python3
import subprocess,sys, os
import json
from time import sleep

os.environ['ETCDCTL_API']= '3'

def etcdgetjson(*argv):
 key=argv[0]
 try:
  prefix=argv[1]
 except:
  prefix='nothing'
 endpoints = '--endpoints=http://etcd:2379'
 if 'nothing' in prefix: 
  cmdline=['etcdctl','--user=root:YN-Password_123',endpoints,'get',key]
  cmdline=['etcdctl',endpoints,'get',key]
 else: 
  cmdline=['etcdctl',endpoints,'get',key,prefix]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 err = result.returncode
 ilist=[]
 try:
  if(prefix !='nothing'):
   mylist=str(result.stdout.decode()).replace('\n\n','\n').split('\n')
   mylist=zip(mylist[0::2],mylist[1::2])
   hostid=0
   hosts=[]
   for x in mylist:
    ll=[]
    #xx=str(x[1]).replace('{','{"').replace('}','"}').replace(':','":"').repalce(',','","')
    xx=x[1]
    ll.append(xx)
    hostsdic={'id':str(hostid),'name':x[0],'prop':xx}
    hostid=hostid+1
    hosts.append(hostsdic)
    if 'prefix' not in prefix:
     hosts=[x for x in hosts if prefix in str(x)]
   #return str(hosts).replace('"','').replace("'",'"')
   #print(hosts)

   return hosts
   
  else:
   #print(dict(str(result.stdout).split(key)[1][2:][:-3].replace("'",'"')))

   return dict(str(result.stdout).split(key)[1][2:][:-3].replace("'",'"'))
 
 except:
  return dict([{'result':'_1'}]) 

if __name__=='__main__':
 etcdgetjson(*sys.argv[1:])
