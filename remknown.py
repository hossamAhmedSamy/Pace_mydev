#!/bin/python3.6
import subprocess,sys, logmsg
from logqueue import queuethis
from ast import literal_eval as mtuple
from etcddel import etcddel as etcddel
from broadcast import broadcast as broadcast 
from broadcasttolocal import broadcasttolocal as broadcasttolocal
from etcdget import etcdget as get
from etcdgetlocal import etcdget as getlocal
from time import time as stamp
from etcdput import etcdput as put 
import json
from socket import gethostname as hostname

myhost = hostname()

with open('/pacedata/perfmon','r') as f:
 perfmon = f.readline() 
if '1' in perfmon:
 queuethis('remknown.py','start','system')
known=get('known','--prefix')
ready=get('ready','--prefix')
leader=get('leader','--prefix')
knownchange = 0

def dosync(*args):
 if myhost in str(leader):
  put(*args)
 return 

stamp = str(stamp())
if len(ready) > len(known)+1:
 print('iamhere')
 for r in ready:
  if r[0].split('/')[1] not in ( str(known) and str(leader)) :
   put('known/'+r[0].split('/')[1],r[1])
   dosync('sync/known/Add_'+r[0].split('/')[1]+'_'+r[1]+'/request','known_'+stamp)
   dosync('sync/known/Add_'+r[0].split('/')[1]+'_'+r[1]+'/request/'+myhost,'known_'+stamp)
   knownchange = 1
if knownchange == 1:
 known=get('known','--prefix')
  
print(known)
nextone=get('nextlead/er')[0]
if str(nextone) != '-1':
 if str(nextone[1]).split('/')[0] not in  str(known):
  print('deleting nextlead')
  etcddel('nextlead/er')
 nextone=[]
if known != []:
 for kno in known:
  kn=kno 
  heart=getlocal(kn[1],'local','--prefix')
  print('heartbeat=',heart, kn[1])
  print(type(heart),heart)
  if( '-1' in str(heart) or len(heart) < 1) or (heart[0][1] not in kn[1]):
   thelost = kn[0].split('/')[1]
   print('the known',thelost,'is gone, notfound')
   etcddel(kn[0])
   etcddel('host',thelost)
   etcddel('list',thelost)
   print('thlost'+thelost)
   etcddel('sync/known','_'+thelost)
   dosync('sync/known/Del_known::'+thelost+'/request','known_'+stamp)
   dosync('sync/known/Del_known::'+thelost+'/request/'+myhost,'known_'+stamp)
   etcddel('sync/ready','_'+thelost)
   etcddel('sync/volumes','_'+thelost)
   etcddel('volumes',thelost)
   etcddel('pools',thelost)
   etcddel('sync/pools','_'+thelost)
   dosync('sync/poolsnxt/Del_poolsnxt_'+thelost+'/request','poolsnxt_'+stamp)
   dosync('sync/poolsnxt/Del_poolsnxt_'+thelost+'/request/'+myhost,'poolsnxt_'+stamp)
   dosync('sync/pools/Del_pools_'+thelost+'/request','pools_'+stamp)
   dosync('sync/pools/Del_pools_'+thelost+'/request/'+myhost,'pools_'+stamp)
   etcddel('sync/nextlead',thelost)
   if kn[1] in str(nextone):
    etcddel('nextlead/er')
    dosync('sync/nextlead/Del_nextlead_--prefix/request','nextlead_'+stamp)
    dosync('sync/nextlead/Del_nextlead_--prefix/request/'+myhost,'nextlead_'+stamp)
    #broadcasttolocal('nextlead','nothing')
   logmsg.sendlog('Partst02','warning','system', kn[0].replace('known/',''))
   etcddel('ready/'+kn[0].replace('known/',''))
   dosync('sync/ready/Del_ready::'+thelost+'/request','ready_'+stamp)
   dosync('sync/ready/Del_ready::'+thelost+'/request/'+myhost,'ready_'+stamp)
   etcddel('ipaddr',kn[0].replace('known/',''))
   print('hostlost ###########################################33333')
   #cmdline=['/pace/hostlost.sh',kn[0].replace('known/','')]
   #subprocess.run(cmdline,stdout=subprocess.PIPE)
   etcddel('localrun/'+str(kn[0]))
   #broadcast('broadcast','/pace/hostlostfromleader.sh',kn[0].replace('known/',''))
   #broadcast('broadcast','/TopStor/pump.sh','zpooltoimport.py','all')
   #broadcast('broadcast','/TopStor/pump.sh','zpooltoimport.py','all')
  else:
   if nextone == []:
    put('nextlead/er',kn[0].replace('known/','')+'/'+kn[1])
    dosync('sync/nextlead/Add_er_'+kn[0].split('/')[1]+'::'+kn[1]+'/request','nextlead_'+stamp)
    dosync('sync/nextlead/Add_er_'+kn[0].split('/')[1]+'::'+kn[1]+'/request/'+myhost,'nextlead_'+stamp)
    #etcddel('nextlead','--prefix')
   # broadcasttolocal('nextlead',kn[0].replace('known/','')+'/'+kn[1])
   # broadcast('broadcast','/TopStor/pump.sh','syncnext.sh','nextlead','nextlead')
poss = get('pos','--prefix')
if poss != []:
 for pos in poss:
  heart = getlocal(pos[1],'local','--prefix')
  print(type(heart),heart)
  if( '-1' in str(heart) or len(heart) < 1) or (heart[0][1] not in pos[1]):
   print(pos[0].replace('possible',''))
   etcddel('ready/'+pos[0].replace('possible',''))
   dosync('sync/ready/Del_ready::_'+pos[0].replace('possible','')+'/request','ready_'+stamp)
   dosync('sync/ready/Del_ready::_'+pos[0].replace('possible','')+'/request/'+myhost,'ready_'+stamp)
   etcddel(pos[0])
  
  
if '1' in perfmon:
 queuethis('remknown.py','stop','system')
