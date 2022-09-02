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

def etcdctlheart(ip,port,key,prefix):
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
 nextleadinfo =  etcdctlheart(myip,myport,'nextlead/er','')
 if len(str(nextleadinfo)) < 6:
  nextlead = leadern
  nextleadip = leaderip
 else:
  nextleadinfo =  nextleadinfo[0].split('/')
  nextlead = nextleadinfo[0]
  nextleadip = nextleadinfo[1]
 return nextlead , nextleadip


def heartbeat(*args):
 sleep(1)
 cmdline=['pcs','resource','show','--full']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE).stdout.decode()
 myport = '2379' if 'mgmtip' in result else '2378'
 result = result.split('\n')
 cmdline=['pcs','resource','show','CC']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE).stdout.decode()
 myip = [ x for x in result.split('\n') if dev in x][0].split('ip=')[1].split(' ')[0]
 leader =  etcdctlheart(myip,myport,'leader','--prefix')[0]
 leadern = leader[0].split('/')[1]
 leaderip = leader[1]
 myhost = hostname()
 while True:
  nextlead, nextleadip = getnextlead(myip,myport,leadern,leaderip)
  knowns = [leader]
  if myhost == leadern:
   knowns = knowns + etcdctlheart(myip, myport, 'known','--prefix')
  for known in knowns:
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
     if myhost == nextlead:
      myport = '2379'
     leader =  etcdctlheart(myip,myport,'leader','--prefix')[0]
     leadern = leader[0].split('/')[1]
     leaderip = leader[1]
     nextlead, nextleadip = getnextlead(myip,myport, leadern, leaderip)
    print('myhost',myhost,myip,myport)
    dels('ready/'+host)
    dels('known/'+host)
    stampit = str(stamp())
    dosync(leadern,'sync/known/Del_known_'+host+'/request','known_'+stampit)
    dosync(leadern,'sync/known/Del_ready_'+host+'/request','ready_'+stampit)
    cmdline='/pace/iscsiwatchdog.sh'
    result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
    zpooltoimport(leadern, myhost)
    etcds = etcdctlheart(myip,myport,'volumes','--prefix')
    replis = etcdctlheart(myip,myport, 'replivol','--prefix')
    cmdline = 'pcs resource'
    pcss = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8') 
    volumecheck(leadern, myhost, etcds, replis, pcss)
    addactive(leadern,myhost)
    spare2(leadern, myhost)
    spare2(leadern, myhost)
    spare2(leadern, myhost)
    if myhost == leadern:
     remknown(leadern,myhost) 
    break
 


if __name__=='__main__':
 heartbeat(*sys.argv)
