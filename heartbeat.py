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
from VolumeCheck import volumecheck

leader, leaderip, myhost, myhostip, nextleader, nextleaderip = '','','','','',''
etcd = ''
dev = 'enp0s8'
os.environ['ETCDCTL_API']= '3'


def dosync(*args):
  global etcd, leader ,leaderip, myhost, myhostip, nextleader, nextleaderip
  put(leaderip, *args)
  put(leaderip, args[0]+'/'+leader,args[1])
  return 




def getnextlead():
 global etcd, leader ,leaderip, myhost, myhostip, nextleader, nextleaderip
 nextleader =  get(etcd,'nextlead/er')[0]
 if '_1' in str(nextleader):
  put(leaderip, 'nextlead/er',myhost)
  stampit = str(stamp())
  dels(leaderip,'sync/nextlead/Add_er','--prefix')
  dosync('sync/nextlead/Add_er_'+myhost+'/request','nextlead_'+stampit)
  nextleader = leader 
  nextleaderip = leaderip
 else:
  nextleaderip = get(etcd,'ready/'+nextleader)[0]
 return nextleader , nextleaderip

def hostlost(host, hostip):
                global etcd, leader ,leaderip, myhost, myhostip, nextleader, nextleaderip
                port = myport = '2379'
                clusterip = get(leaderip,'namespace/mgmtip')[0]
                if host == leader:
                    print('leader lost. nextleader is ',nextleader, 'while my host',myhost)
                    leader = nextleader 
                    put(myhostip,'leader',leader)
                    if myhost == nextleader:
                        cmdline='/pace/leaderlost.sh '+leader+' '+leaderip+' '+myhost+' '+myhostip+' '+nextleader+' '+nextleaderip+' '+clusterip+' '+host
                        result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
                        put(etcd,'refreshdisown','yes')
                        etcd = leaderip
                    sleep(2)
                    result='failed'
                    while 'ok' not in str(result):
                        print('chceking new leader')
                        cmdline='nmap --max-rtt-timeout 100ms -n -p '+port+' '+leaderip 
                        result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
                        if ('Host is up' or 'open' ) in result:
                            result = (host,'ok')
                        else:
                            result = (host,'lost')

                dels(leaderip, 'sync/hostdown/'+host,'--prefix')
                dels(leaderip, 'cpuperf/'+host)
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
                dosync('sync/ready/Del_ready_'+host+'/request','ready_'+stampit)
                dosync('sync/running/____/request','running_'+stampit)
                dosync('sync/pools/Del_pools_'+host+'/request','pools_'+stampit)


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
        tries = 0
        while tries < 3:
            knowns = get(etcd, 'ready','--prefix')
            if 'dhcp' in str(knowns):
                tries = 10
                break
            tries +=1
        if tries < 10: 
           hostlost(leader, leaderip)
        for known in knowns:
            host = known[0].split('/')[1]
            if host == myhost:
                continue
            if host != leader and myhost != leader:
                continue
            if host == leader:
                hostip = leaderip
            else:
                hostip = known[1]
            print('nmapping')
            result = 'failed'
            tries = 0
            cmdline='nmap --max-rtt-timeout 500ms -n -p '+port+' '+hostip 
            while tries < 4:
                tries +=1
                try:
                    result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
                except:
                    with open('/root/heartproblem','a') as f:
                        f.write('nmap:\n'+result)
                    result=(host,'doubt')
                if ('Host is up' or 'open' ) in result:
                    result = (host,'ok')
                else:
                    result = (host,'doubt')
                if 'doubt' in str(result):
                    print('ddddddddddddddddddddddddd')
                    cmdline='ping -w 1 '+hostip 
                    print(cmdline)
                    try:
                        subprocess.check_output(cmdline.split())
                    except subprocess.CalledProcessError as e:
                        result=(host,'lost')
                if 'ok' in str(result):
                    break
                sleep(1)
            print(result)
            if 'ok' not in str(result):
                hostlost(host, hostip)
                break
    print(leader ,leaderip, myhost, myhostip)
    return leader ,leaderip, myhost, myhostip

 


if __name__=='__main__':

 print(leader ,leaderip, myhost, myhostip)
 heartbeat(*sys.argv)
