#!/bin/python3.6
import subprocess,sys, datetime
from logqueue import queuethis
from etcdput import etcdput as put 
from time import sleep
from etcdputlocal import etcdput as putlocal
from etcdget import etcdget as get 
from etcddel import etcddel as deli 
from socket import gethostname as hostname
import logmsg
def setall(*bargs):
 with open('/pacedata/perfmon','r') as f:
  perfmon = f.readline()
 if '1' in perfmon:
  queuethis('Evacuate','running','system')
 thehosts=get('modified','evacuatehost')
 if thehosts[0]==-1:
  if '1' in perfmon:
   queuethis('Evacuate','stop_cancel','system')
  return
 leader=get('leader','--prefix')[0][0].replace('leader/','')
 myhost=hostname()
 myip=get('ready',myhost)[0][1]
 for host in thehosts:
  hostn=host[0].split('/')[2]
  hostip=host[1]
  print('iiiiiiiiiiiiiiiii',hostn,myhost, hostip)
  if myhost in hostn:
   if myhost in leader:
    cmdline=['/TopStor/Converttolocal.sh',myip]
    result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/TopStor/resettarget.sh',myhost]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   while True:
    cmdline=['/TopStor/rebootme','reset']
    result=subprocess.run(cmdline,stdout=subprocess.PIPE)
    sleep(10)
  if myhost not in hostn : 
     print('iam here', hostn, hostip)
     cmdline=['/pace/removetargetdisks.sh', hostn, hostip]
     result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  logmsg.sendlog('Evacuaesu01','info','system',hostn)
 if '1' in perfmon:
  queuethis('Evacuate','stop','system')
 return

if __name__=='__main__':
 setall(*sys.argv[1:])
