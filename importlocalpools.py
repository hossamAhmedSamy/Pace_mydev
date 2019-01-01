#!/bin/python3.6
import sys,subprocess
from threading import Thread
from ast import literal_eval as mtuple

def thread_run(*args):
 with open('/root/importlocal2','a') as f:
  f.write('\nargs1: '+str(args))
 print('hi')
 subprocess.run(args,stdout=subprocess.PIPE)
 return

def importpools(*args):
 print('hihihi')
 threads=[]
 with open('/TopStordata/forlocalpools') as f:
  for line in f:
   print('===============')
   with open('/root/importlocal','a') as f:
    f.write('poolline: '+line)
   pool=mtuple(line)[0].split('/')[1]
   with open('/root/importlocal','a') as f:
    f.write('poolname: '+str(pool)+'\n')
   print('line', line)
   cmdline='/TopStor/Zpool2deadhost import '+pool
   x=Thread(target=thread_run,name='importing-'+pool,args=cmdline.split(" "))
   x.start()
   threads.append(x) 
  for tt in threads:
   tt.join()
   
 return

if __name__ == "__main__":
 print('starting')
 importpools(*sys.argv[1:])
 
