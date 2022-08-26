#!/bin/python3.6
import subprocess,sys, os
import json
from time import sleep
from checkleader import checkleader

dev = 'enp0s8'
os.environ['ETCDCTL_API']= '3'

def etcdctl(ip,port,key,prefix):
 if port == '2379':
  cmdline=['/bin/etcdctl','--user=root:YN-Password_123','--endpoints=http://'+ip+':'+port,'get',key,prefix]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  while result.returncode != 0:
   sleep(1)
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 else:
  returncode= 1
  while returncode != 0:
   endpoints=''
   data=json.load(open('/pacedata/runningetcdnodes.txt'));
   for x in data['members']:
    endpoints=endpoints+str(x['clientURLs'])[2:][:-2]+','
   cmdline=['/bin/etcdctl','--user=root:YN-Password_123','--endpoints='+endpoints,'get',key,prefix]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   returncode = int(result.returncode)
 return result 
 
def etcdget(key, prefix=''):
 cmdline=['pcs','resource','show','--full']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE).stdout.decode()
 port = '2379' if 'mgmtip' in result else '2378'
 result = result.split('\n')
 ip = [ x for x in result if dev in x][0].split('ip=')[1].split(' ')[0]
 result = etcdctl(ip,port,key,prefix)
 z=[]
 try:
  if(prefix =='--prefix'):
   mylist=str(result.stdout)[2:][:-3].split('\\n')
   zipped=zip(mylist[0::2],mylist[1::2])
   for x in zipped:
    z.append(x) 
  elif(prefix == ''):
   if len(str(result.stdout).split(key)) > 2 :	
    z.append(key.join(str(result.stdout).split(key)[1:])[2:][:-3])
   else:
    z.append((str(result.stdout).split(key)[1][2:][:-3]))
  else:
   result = etcdctl(ip,port,key,'--prefix')
   mylist=str(result.stdout)[2:][:-3].split('\\n')
   zipped=zip(mylist[0::2],mylist[1::2])
   for x in zipped:
    if prefix in str(x):
     z.append(x)
   if(len(z) == 0):
     z.append(-1)
 except:
  z.append(-1)
 return z
if __name__=='__main__':
 etcdget(*sys.argv[1:])
