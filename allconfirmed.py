#!/usr/bin/python3
import subprocess
from ast import literal_eval as mtuple
import socket

myhost=socket.gethostname()
cmdline=['/pace/etcdget.py','known','--prefix']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
known=str(result.stdout).replace('known/','')[2:][:-3].split('\\n')
if known==['']:
 exit();
lenknown=len(known)
cmdline=['/pace/etcdget.py','confirmed','--prefix']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
confirmed=str(result.stdout).replace('confirmed/','')[2:][:-3].split('\\n')
if confirmed==['']:
 exit()
lenconf=len(confirmed)
cmdline=['/pace/etcdget.py','change','--prefix']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
change=str(result.stdout).replace('change/','')[2:][:-3].split('\\n')
if change==['']:
 exit()
lench=len(change)

for c in change:
 ch=mtuple(c)
 yy=[y for y in confirmed if ch[0] in y]
 if len(yy)>=len(known):
  cmdline=['/pace/etcddel.py','change/'+ch[0],'--prefix']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  cmdline=['/pace/etcddel.py','confirmed/',ch[0],]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
