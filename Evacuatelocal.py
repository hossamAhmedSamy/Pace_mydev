#!/usr/bin/python3
import subprocess,sys, datetime
from etcddel import etcddel as deli 


def setall(hostn,hostip,leader):
 cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py clusternode'
 myhost=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
 cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py clusternodeip'
 myip=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
 if myhost in hostn:
  cmdline=['/TopStor/docker_setup.sh','reset']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 else:
    cmdline=['/pace/removetargetdisks.sh', hostn, hostip]
    result=subprocess.run(cmdline,stdout=subprocess.PIPE)
    deli(myip,"",hostn)

if __name__=='__main__':
 setall(*sys.argv[1:])
