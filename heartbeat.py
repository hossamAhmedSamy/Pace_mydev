#!/bin/python3.6

import sys, os, subprocess
from etcdgetpy import etcdget as get
from etcdgetlocalpy import etcdget as getlocal
from socket import gethostname as hostname
from time import sleep
from time import time as stamp
from zpooltoimport import zpooltoimport
from selectspare import spare2  
from addactive import addactive
from remknown import remknown
from VolumeCheck import volumecheck

dev = 'enp0s8'
os.environ['ETCDCTL_API']= '3'

def etcdctl(ip,port,key,prefix):
 if port == '2379':
  result = get(key,prefix)
 else:
  result = getlocal(ip,key,prefix)
 return result 

def dosync(leader,*args):
  put(*args)
  put(args[0]+'/'+leader,args[1])
  return 




def getnextlead(myip,myport,leadern,leaderip):
 nextleadinfo =  etcdctl(myip,myport,'nextlead/er','')
 print(nextleadinfo)
 if len(str(nextleadinfo)) < 6:
  nextlead = leadern
  nextleadip = leaderip
 else:
  nextleadinfo =  nextleadinfo[0].split('/')
  nextlead = nextleadinfo[0]
  nextleadip = nextleadinfo[1]
 return nextlead , nextleadip


def heartbeat(*args):
 cmdline=['pcs','resource','show','--full']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE).stdout.decode()
 myport = '2379' if 'mgmtip' in result else '2378'
 result = result.split('\n')
 cmdline=['pcs','resource','show','CC']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE).stdout.decode()
 myip = [ x for x in result.split('\n') if dev in x][0].split('ip=')[1].split(' ')[0]
 leader =  etcdctl(myip,myport,'leader','--prefix')[0]
 leadern = leader[0].split('/')[1]
 leaderip = leader[1]
 myhost = hostname()
 knowns =  etcdctl(myip,myport,'known','--prefix')
 nextlead, nextleadip = getnextlead(myip,myport,leadern,leaderip)
 sleeping = 0 
 while True:
  sleep(sleeping)
  sleeping = 1
  knowns = etcdctl(myip, myport, 'known','--prefix')
  for known in [leader]+knowns:
   host = known[0].split('/')[1]
   hostip = known[1]
   port = '2379' if host in str(leadern) else '2378'
   cmdline='nmap --max-rtt-timeout 2000ms -p '+port+' '+hostip 
   result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
   result =(host,'ok') if 'open' in result  else (host,'lost')
   print(result)
   if 'ok' not in str(result):
    if host == leadern:
     print('leader lost. nextlead is ',nextlead, 'while my host',myhost)
     cmdline='/pace/leaderlost.sh '+leadern+' '+myhost+' '+leaderip+' '+myip+' '+nextlead+' '+nextleadip
     result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
     leader =  etcdctl(myip,myport,'leader','--prefix')[0]
     leadern = leader[0].split('/')[1]
     leaderip = leader[1]
     put('ready/'+myhost,myip)
     stampit = str(stamp())
     dosync(leadern,'sync/ready/Add_'+myhost+'_'+myip+'/request','ready_'+stampit)
     if myhost == nextlead:
      myport = '2379'
     nextlead, nextleadip = getnextlead(myip,myport, leadern, leaderip)
     
    print('myhost',myhost,myip,myport)
    #remknown(leadern,myhost) 
    cmdline='/pace/iscsiwatchdog.sh'
    result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
    zpooltoimport(leadern, myhost)
    etcds = etcdctl(myip,myport,'volumes','--prefix')
    replis = etcdctl(myip,myport, 'replivol','--prefix')
    cmdline = 'pcs resource'
    pcss = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8') 
    volumecheck(leader, myhost, etcds, replis, pcss)
    addactive(leadern,myhost)
    spare2(leadern, myhost)
    spare2(leadern, myhost)
    spare2(leadern, myhost)
   break


 return 
 


if __name__=='__main__':
 heartbeat(*sys.argv)
