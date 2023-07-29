#!/usr/bin/python3
import subprocess,sys, datetime
from etcddel import etcddel as deli 
from etcdput import etcdput as put 


def setall(hostn,leader):

 cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py clusternode'
 myhost=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
 print('hihihih')
 cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py clusternodeip'
 myip=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
 cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py ActivePartners/'+hostn
 hostip=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
 cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py leaderip'
 leaderip=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
 if myhost in hostn:
  put(leaderip, 'configured/'+hostn,'reset')
  put(myip, 'configured/'+hostn,'reset')
  put(leaderip, 'rebootme/'+hostn,'pls_fromevacuate')
  cmdline=['/TopStor/docker_setup.sh','reset']
  #result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 else:
    cmdline=['/pace/removetargetdisks.sh', hostn, hostip]
    result=subprocess.run(cmdline,stdout=subprocess.PIPE)
    cmdline=['/pace/hostlost.sh',leader, leaderip, myhost, myip, hostn]
    result=subprocess.run(cmdline,stdout=subprocess.PIPE)
    deli(myip,"",hostn)

if __name__=='__main__':
 setall(*sys.argv[1:])
