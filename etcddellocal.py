#!/bin/python3.6
import subprocess,sys
import json

def etcddel(*args):
 if args[-1]=='--prefix':
  pointer=-1
 else:
  pointer=0
 endpoints=''
 data=json.load(open('/pacedata/runningetcdnodes.txt'));
 endpoints='http://'+args[0]+':2378'
 if len(args) > 2:
  cmdline=['etcdctl','--endpoints='+endpoints,'get',args[1],'--prefix']
 else:
  cmdline=['etcdctl','--endpoints='+endpoints,'get',args[1]]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 mylist=str(result.stdout)[2:][:-3].split('\\n')
 zipped=zip(mylist[0::2],mylist[1::2])
 if mylist==['']:
  print('-1')
  return '-1'
 if len(args) > 2 and args[2] !='--prefix':
  todel=[]
  args2=args[2:]
  for x in args2:
   for y in zipped:
    if x in str(y):
     todel.append(y[0])
 else:
  todel=mylist
 if todel == []:
  print('-1')
  return (-1)
 count=0
 for key in todel:
  cmdline=['etcdctl','--endpoints='+endpoints,'del',key]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  reslist=str(result.stdout)[2:][:-3]
  if '1' in reslist:
   count+=1
 print(count)
 

if __name__=='__main__':
 etcddel(*sys.argv[1:])
