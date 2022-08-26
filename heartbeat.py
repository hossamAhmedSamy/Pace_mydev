#!/bin/python3.6

import sys, os, subprocess
from etcdgetpy import etcdget as get
from socket import gethostname as hostname
from time import sleep
from zpooltoimport import zpooltoimport
from selectspare import spare2  
from addactive import addactive
from remknown import remknown

os.environ['ETCDCTL_API']= '3'

def heartbeat(leader,myhost,knowns):
 while True:
  sleep(1)
  knowns = get('known','--prefix')
  for known in [leader]+knowns:
   host = known[0].split('/')[1]
   hostip = known[1]
   port = '2379' if host in str(leader) else '2378'
   cmdline='nmap --max-rtt-timeout 2000ms -p '+port+' '+hostip 
   result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
   result =(host,'ok') if 'open' in result  else (host,'lost')
   print(result)
   if 'ok' not in str(result):
    leadern = leader[0].split('/')[1]
    remknown(leadern,myhost) 
    cmdline='/pace/iscsiwatchdog.sh'
    result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
    zpooltoimport(leadern, myhost)
    addactive(leadern,myhost)
    spare2(leadern, myhost)


 return 
 


if __name__=='__main__':
 if len(sys.argv) > 2: 
  leader = sys.argv[2]
  myhost = sys.argv[3]
  knowns = sys.argv[4]
 else:
  leader=get('leader','--prefix')[0]
  myhost = hostname()
  knowns = get('known','--prefix')
 heartbeat(leader,myhost,knowns)
