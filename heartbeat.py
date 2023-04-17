#!/usr/bin/python3

import sys, os, subprocess
from etcdget import etcdget as get
from etcdput import etcdput as put 
from etcddel import etcddel as dels 
from socket import gethostname as hostname
from time import sleep
from time import time as stamp
from zpooltoimport import zpooltoimport
from selectspare import spare2  
from addactive import addactive
from remknown import remknown
from VolumeCheck import volumecheck

leader, leaderip, myhost, myhostip = '','','',''
etcd = ''
dev = 'enp0s8'
os.environ['ETCDCTL_API']= '3'


def dosync(*args):
  global etcd, leader ,leaderip, myhost, myhostip
  put(leaderip, *args)
  put(leaderip, args[0]+'/'+leader,args[1])
  return 




def getnextlead():
 global etcd, leader ,leaderip, myhost, myhostip
 nextleader =  get(etcd,'nextlead/er')[0]
 if '_1' in str(nextleader):
  put(leaderip, 'nextlead/er',myhost)
  stampit = str(stamp())
  dels(leaderip,'sync/nextlead/Add_er','--prefix')
  dosync('sync/nextlead/Add_er_'+myhost+'/request','nextlead_'+stampit)
  nextleader = leader 
  nextleaderip = leaderip
 else:
  nextleadip = get(etcd,'ready/'+nextleader)[0]
 return nextleader , nextleadip


def heartbeat(*args):
    global etcd, leader ,leaderip, myhost, myhostip
    cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py leader'
    leader=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
    cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py leaderip'
    leaderip=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
    cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py clusternode'
    myhost=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
    cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py clusternodeip'
    myhostip=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
    nochange = 1
    port = myport = '2379'
    if myhost == leader:
        etcd = leaderip
    else:
        etcd = myhostip
    nextleader, nextleaderip = getnextlead()
    while True:
        print('looping')
        sleep(1)
        knowns = get(etcd, 'ready','--prefix')
        for known in knowns:
            host = known[0].split('/')[1]
            if host == myhost:
                continue
            if host == leader:
                hostip = leaderip
            else:
                hostip = known[1]
            print('nmapping')
            result = 'failed'
            tries = 0
            cmdline='nmap --max-rtt-timeout 100ms -n -p '+port+' '+hostip 
            while tries < 4:
                tries +=1
                result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
                result =(host,'ok') if 'open' in result  else (host,'lost')
                if 'ok' in str(result):
                    break
                sleep(1)
            print(result)
            if 'ok' not in str(result):
                if host == leader:
                    print('leader lost. nextleader is ',nextleader, 'while my host',myhost)
                    leader = nextleader 
                    put(myhostip,'leader',leader)
                    if myhost == nextleader:
                        cmdline='/pace/leaderlost.sh '+leader+' '+leaderip+' '+myhost+' '+myhostip+' '+nextleader+' '+nextleaderip+' '+leaderip+' '+host
                        result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
                        etcd = leaderip
                    else:
                        sleep(2)
                        result='failed'
                        while 'ok' not in str(result):
                            print('chceking new leader')
                            cmdline='nmap --max-rtt-timeout 100ms -n -p '+port+' '+leaderip 
                            result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
                            result =(host,'ok') if 'open' in result  else (host,'lost')
                    put(etcd,'refreshdisown','yes')
                dels(leaderip, 'sync/hostdown/'+host,'--prefix')
                stampit = str(stamp())
                put(leaderip,'sync/hostdown/'+host+'_/request','hostdown_0')
                put(leaderip,'sync/hostdown/'+host+'_/request/'+myhost,'hostdown_0')
                cmdline='/pace/hostlost.sh '+leader+' '+leaderip+' '+myhost+' '+myhostip+' '+host
                result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
                dels(leaderip,'ready/'+host)
                dels(leaderip, 'running/', host)
                dels(leaderip, 'host', host)
                dels(leaderip, 'known/'+host)
                dels(leaderip, 'pools',host)
                dels(leaderip, 'sync/hostdown',host)
                #dosync('sync/known/Del_known_'+host+'/request','known_'+stampit)
                dosync('sync/ready/Del_ready_'+host+'/request','ready_'+stampit)
                dosync('sync/running/____/request','running_'+stampit)
                dosync('sync/pools/Del_pools_'+host+'/request','pools_'+stampit)
                #cmdline='/pace/iscsiwatchdog.sh'
                #result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
                #zpooltoimport(leadern, myhost)
                #etcds = etcdctlheart(myip,myport,'volumes','--prefix')
                #replis = etcdctlheart(myip,myport, 'replivol','--prefix')
                #volumecheck(leadern, myhost, etcds, replis, pcss)
                #ddactive(leadern,myhost)
                #spare2(leadern, myhost)
                #spare2(leadern, myhost)
                #spare2(leadern, myhost)
                #if myhost == leadern:
                #remknown(leadern,myhost) 
                break
    print(leader ,leaderip, myhost, myhostip)
    return leader ,leaderip, myhost, myhostip
 


if __name__=='__main__':

 print(leader ,leaderip, myhost, myhostip)
 heartbeat(*sys.argv)
