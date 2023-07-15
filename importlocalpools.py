#!/usr/bin/python3
import sys,subprocess
from threading import Thread
from etcdgetpy import etcdget as get

def thread_run(*args):
 with open('/root/importlocal2','a') as f:
  f.write('\nargs1: '+str(args))
 print('local2:',args[1])
 subprocess.run(args,stdout=subprocess.PIPE)
 
 return


def importpools(*args):
 leaderip=args[0]
 myhost=args[1]
 etcdip=args[2]
 thehost=args[3]
 threads=[]
 pool=""
 mypools=get(etcdip,'poolnxt',myhost)
# with open('/TopStordata/forlocalpools') as f:
#  for line in f:
 print('mypools',myhost,thehost,mypools)
 if(len(mypools) < 1):
  return
 for line in mypools:
  if '_1' in str(line):
   break
  with open('/root/importlocal','w') as f:
   f.write('poolline: '+str(pool)+'\n')
  pool=line[0].split('/')[1]
  with open('/root/importlocal','a') as f:
   f.write('poolname: '+str(pool)+'\n')
  print('line', line)
  cmdline='/pace/Zpool2deadhost '+leaderip+' '+etcdip+' '+thehost+' '+pool
  x=Thread(target=thread_run,name='importing-'+pool,args=cmdline.split(" "))
  x.start()
  threads.append(x) 
  for tt in threads:
   tt.join()
  
 return

if __name__ == "__main__":
 importpools(*sys.argv[1:])
 
