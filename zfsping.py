#!/usr/bin/python3
from checkleader import checkleader
from remknown import remknown
from poolall import getall as getall
from getload import getload
from sendhost import sendhost
import subprocess,sys, logmsg, os
from logqueue import queuethis
from etcddel import etcddel as etcddel
from etcdgetpy import etcdget as get
from etcdgetlocalpy import etcdget as getlocal
from time import time as stamp
from time import sleep
from etcdput import etcdput as put 
from addknown import addknown
from putzpool import putzpool
from etcdputlocal import etcdput as putlocal 
from activeusers import activeusers
from addactive import addactive
from selectimport import selectimport
from zpooltoimport import zpooltoimport
from selectspare import spare2  
from checksyncs import syncrequest, initchecks
from VolumeCheck import volumecheck
from multiprocessing import Process
from concurrent.futures import ProcessPoolExecutor
from heartbeat import heartbeat

os.environ['ETCDCTL_API']= '3'
ctask = 1
dirtydic = { 'pool': 0, 'volume': 0 } 
def heartbeatpls():
 global leader, myhost
 try:
  cleader = leader
  leader, leaderip = heartbeat()
  if leader != cleader:
   print('######################################################################### heartbeat')
   cleader = leader
   refreshall()
 except Exception as e:
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
  print(' in heartbeat:',e)
  with open('/root/pingerr','a') as f:
   f.write(e)
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
 

def dosync(leader,*args):
 put(*args)
 put(args[0]+'/'+leader,args[1])

def iscsiwatchdogproc():
 try:
  cmdline='/pace/iscsiwatchdog.sh'
  result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
 except Exception as e:
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
  print(' in iscsiwatchdogproc:',e)
  with open('/root/pingerr','a') as f:
   f.write(e)
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')

def fapiproc():
  cmdline='/pace/fapilooper.sh' 
  result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')

def putzpoolproc():
 global leader, myhost
 try:
  putzpool(leader,myhost)
 except Exception as e:
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
  print(' in putzpool:',e)
  with open('/root/pingerr','a') as f:
   f.write(e)
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')

def addactiveproc():
 global leader, myhost
 try:
  addactive(leader,myhost)
 except Exception as e:
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
  print(' in addactive:',e)
  with open('/root/pingerr','a') as f:
   f.write(e)
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')

def selectimportproc():
 global leader, myhost
 try:
  allpools=get('pools/','--prefix')
  selectimport(myhost,allpools,leader)
 except Exception as e:
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
  print(' in selectimport:',e)
  with open('/root/pingerr','a') as f:
   f.write(e)
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
   

def zpooltoimportproc():
 global leader, myhost, leaderip, myhostip, etcdip, dirtydic
 dirty = int(dirtydic['pool'])
 if int(dirtydic['pool']) >= 10:
  return
 dirty += 1 
 put(etcdip, 'dirty/pool', str(dirty))
 dirtydic['pool'] = dirty
 try:
  zpooltoimport(leader, leaderip, myhost, myhostip, etcdip)
 except Exception as e:
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
  print(' in zpooltoimport:',e)
  with open('/root/pingerr','a') as f:
   f.write(e)
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
 
def volumecheckproc():
 global leader, myhost, leaderip, myhostip, etcdip, dirty
 dirty = int(dirtydic['volume'])
 if dirty > 12  :
  return
 dirty += 1 
 put(etcdip, 'dirty/volume', str(dirty))
 dirtydic['volume'] = dirty
 try:
  etcds = get(etcdip, 'volumes','--prefix')
  replis = get(etcdip, 'replivol','--prefix')
  volumecheck(etcds, replis)
 except Exception as e:
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
  print(' in volumecheckproc:',e)
  with open('/root/pingerr','a') as f:
   f.write(e)
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')

def refreshall():
 global leader, myhost
 cmdline='/pace/iscsiwatchdog.sh'
 result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
 putzpool(leader,myhost)
 allpools=get('pools/','--prefix')
 selectimport(myhost,allpools,leader)
 zpooltoimport(leader, myhost)
 etcds = get('volumes','--prefix')
 replis = get('replivol','--prefix')
 cmdline = 'pcs resource'
 pcss = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8') 
 volumecheck(leader, myhost, etcds, replis, pcss)
 spare2(leader, myhost)
 spare2(leader, myhost)
 spare2(leader, myhost)
 spare2(leader, myhost)
 
def selectspareproc():
 global leader, myhost
 try:
  clsscsi = 'nothing'
  spare2(leader, myhost)
  spare2(leader, myhost)
  spare2(leader, myhost)
  cmdline='lsscsi -is'
  lsscsi=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
  if clsscsi != lsscsi:
   clsscsi = lsscsi
   refreshall()
 except Exception as e:
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
  print(' in selectspare:',e)
  with open('/root/pingerr','a') as f:
   f.write(e)
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')

def syncrequestproc():
 global leader, myhost
 try:
  syncrequest(leader, myhost)
 except Exception as e:
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
  print(' in syncrequest:',e)
  with open('/root/pingerr','a') as f:
   f.write(e)
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')

def remknownproc():
 global leader, myhost
 try:
  remknown(leader,myhost) 
 except Exception as e:
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
  print(' in remknown:',e)
  with open('/root/pingerr','a') as f:
   f.write(e)
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')

def addknownproc():
 global leader, myhost
 try:
  if myhost == leader:
   addknown(leader,myhost)
 except Exception as e:
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
  print(' in addknown:',e)
  with open('/root/pingerr','a') as f:
   f.write(e)
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')

def activeusersproc():
 global leader, myhost
 try:
  activeusers(leader, myhost)
 except Exception as e:
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
  print(' in activeusers:',e)
  with open('/root/pingerr','a') as f:
   f.write(e)
  print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')




#loopers = [ addknownproc, remknownproc, activeusersproc, iscsiwatchdogproc, putzpoolproc, addactiveproc, selectimportproc, zpooltoimportproc , volumecheckproc, selectspareproc , syncrequestproc ]
loopers = [ zpooltoimportproc, volumecheckproc, selectspareproc ]

def CommonTask(task):
 print("''''''''' task started",task,"'''''''''''''''''''''''''''''''''''''''")
 #if 'selectspare' in str(task):
 # print('############################thisis the task will fail')
 # task()
 task()
 #sleep(2)
 print("''''''''' task ended",task,"'''''''''''''''''''''''''''''''''''''''",flush=True)

i = 0
def lazyloop():
 global i
 while True:
  resyyult = loopers[i % len(loopers)]
  yield result 
  i = i + 1
 return next() 


def lazylooper():
    x = 0
    while True:
        yield loopers[x]
        x = x + 1
        if x == len(loopers):
         x = 0

def zfspinginit():
    global etcdip, leader, leaderip, myhost, myhostip
    myhostip = get(leaderip, 'ready/'+myhost)[0]
    leader = get(leaderip, 'leader')[0]
    #leaderinfo = checkleader('leader','--prefix').stdout.decode('utf-8').split('\n')
    #leader = leaderinfo[0].split('/')[1]
    #leaderip = leaderinfo[1]
    #cleader = leader
    if myhost == leader:
        etcdip = leaderip
    else:
        etcdip = myhostip
    selectimport('init', leader, leaderip, myhost, myhostip, etcdip)
    spare2('init', leader, leaderip, myhost, myhostip, etcdip)
    remknown('init', leader, leaderip, myhost, myhostip, etcdip)
    zpooltoimport('init', leader, leaderip, myhost, myhostip, etcdip)
    volumecheck('init', leader, leaderip, myhost, myhostip, etcdip)
   

if __name__=='__main__':
 print('hihihih')
 leaderip = sys.argv[1]
 myhost = sys.argv[2]
 zfspinginit()
 dirty = get(etcdip, 'dirty','--prefix')
 for dic in dirtydic:
  if dic not in str(dirty):
   print('dic',dic)
   put(etcdip, 'dirty/'+dic,'1000')
 print('etcd',etcdip)
 #if myhost != leader:
 # getready = str(get('ready','--prefix'))
 # while leader not in getready:
 #  sleep(1)
 #  getready = str(get('ready','--prefix'))
 #myip = get('ActivePartners/'+myhost)[0]
 #myalias = get('alias/'+myhost)[0]
 #put('ready/'+myhost,myip)
 #put('nextlead/er',myhost+'/'+myip)
 #stampit = str(stamp())
 #dosync(leader,'sync/ready/Add_'+myhost+'_'+myip+'/request','ready_'+stampit)
 #dosync(leader,'sync/nextlead/Add_er_'+myhost+'::'+myip+'/request','next_'+stampit)
 #if myhost == cleader:
 # logmsg.sendlog('Partsu03','info','system',myalias,myip)
 #else:
 # logmsg.sendlog('Partsu04','info','system',myalias,myip)
 #refreshall() 
 #infloop = lazyloop()
 while True:
  zfspinginit()
  zload = getload()
  counter = 0
  while zload > 65:
   sleep(2)
   counter += 1
   if counter > 10:
    zload = 0
   else:
    zload = getload()
    print('still load high',zload,'counter',counter)
  print('load ok', zload)
  with ProcessPoolExecutor(4) as e:
    for i in range(len(loopers)*2):
     args = loopers[i % len(loopers)]
     res = e.submit(CommonTask,args)
     dirty = get(etcdip, 'dirty','--prefix')
     for dirt in dirty:
      dirtydic[dirt[0].split('/')[1]] = dirt[1]
     print('---------dirty------',dirty)
    sleep(2)
 exit()

