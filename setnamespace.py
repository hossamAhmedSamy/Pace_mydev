#!/usr/bin/python3
import subprocess,sys
from etcdgetpy import etcdget as get
from etcdput import etcdput as put 
import json
def setnamespace(*args):
 nslist=get('namespace','--prefix')
 if 'mgmtip' not in str(nslist):
  put('namespace/mgmtip','192.168.43.7/24')
  nslist=get('namespace','--prefix')
 ns=(x for x in nslist)
 for arg in args:
  try: 
   nsn=next(ns)
  except: 
   return
  cmdline='/sbin/pcs resource create '+nsn[0].replace('namespace/','')+' ocf:heartbeat:IPaddr2 nic='+arg+' ip='+nsn[1].split('/')[0]+' cidr_netmask='+nsn[1].split('/')[1]+' op monitor on-fail=restart'
  subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
  cmdline='/sbin/pcs resource group add namespaces '+nsn[0].replace('namespace/','')
  subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
  
if __name__=='__main__':
 setnamespace(*sys.argv[1:])
