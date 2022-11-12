#!/usr/bin/python3
import subprocess
from ast import literal_eval as mtuple
import socket

myhost=socket.gethostname()
cmdline=['/pace/etcdget.py','change','--prefix']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
mylist=str(result.stdout)[2:][:-3].split('\\n')
print(mylist)
if mylist==['']:
 exit()
for x in mylist:
 y=mtuple(x)
 z=y[0].replace('change/','')
# if 'booted' in z:
#  cmdline=['/pace/iscsiwatchdog.sh']
#  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 if 'stub' in z :
  with open('/pacedata/'+z,'w') as f:
   f.write(y[1])
 cmdline=['/pace/etcdput.py','confirmed/'+myhost+'/'+z, y[1]]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 
