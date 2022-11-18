#!/usr/bin/python3
import subprocess,sys
from etcdgetpy import etcdget as get
from etcdput import etcdput as put 
import json
def setdataip(*args):
 nslist=get('dataip','--prefix')
 for x in nslist:
  name=x[0].replace('/dataip','')
  name=name.replace('/','')
  params=x[1].split('/')
  cmdline='/sbin/pcs resource create '+name+' ocf:heartbeat:IPaddr2 nic='+params[2]+' ip='+params[0]+' cidr_netmask='+params[1]+' op monitor on-fail=restart'
  subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
  
if __name__=='__main__':
 setdataip(*sys.argv[1:])
