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


with open('/pacedata/perfmon','r') as f:
 perfmon = f.readline() 
if '1' in perfmon:
 queuethis('remknown.py','start','system')
known=get('known','--prefix')
ready=get('ready','--prefix')
leader=get('leader','--prefix')
knownchange = 0

def dosync(*args):
 if myhost in string(leader):
  put(*args)
 return 


if len(ready) > len(known)+1:
 print('iamhere')
 for r in ready:
  if r[0].split('/')[1] not in ( str(known) and str(leader)) :
   put('known/'+r[0].split('/')[1],r[1])
   dosync('sync/known/Add_'+r[0].split('/')+'_'+r[1]+'/request',str(stamp()))
   dosync('sync/known/Add_'+r[0].split('/')[1]+'_'+r[1]+'/request/'+myhost,str(stamp()))
   knownchange = 1
if knownchange == 1:
 known=get('known','--prefix')
  
print(known)
nextone=get('nextlead')
if str(nextone[0]).split('/')[0] not in  str(known):
 print('deleting nextlead')
 etcddel('nextlead')
 nextone=[]
if known != []:
 for kno in known:
  kn=kno 
  heart=getlocal(kn[1],'local','--prefix')
  print('heartbeat=',heart, kn[1])
  print(type(heart),heart)
  if( '-1' in str(heart) or len(heart) < 1) or (heart[0][1] not in kn[1]):
   print('the known ',kn[0].replace('known/',''),' is gone, notfound')
   etcddel(kn[0])
   etcddel('host',kn[0].replace('known',''))
   etcddel('list',kn[0].replace('known',''))
   if kn[1] in str(nextone):
    etcddel('nextlead')
    broadcasttolocal('nextlead','nothing')
   logmsg.sendlog('Partst02','warning','system', kn[0].replace('known/',''))
   etcddel('ready/'+kn[0].replace('known/',''))
   dosync('sync/ready/Del_'+kn[0].split('/')[1]+'_'+kn[1]+'/request',str(stamp()))
   dosync('sync/ready/Del_'+kn[0].split('/')[1]+'_'+kn[1]+'/request/'+myhost,str(stamp()))

   etcddel('ipaddr',kn[0].replace('known/',''))

   cmdline=['/pace/hostlost.sh',kn[0].replace('known/','')]
   subprocess.run(cmdline,stdout=subprocess.PIPE)
   etcddel('localrun/'+str(kn[0]))
   broadcast('broadcast','/pace/hostlostfromleader.sh',kn[0].replace('known/',''))
   broadcast('broadcast','/TopStor/pump.sh','zpooltoimport.py','all')
   broadcast('broadcast','/TopStor/pump.sh','zpooltoimport.py','all')
  else:
   if nextone == []:
    put('nextlead',kn[0].replace('known/','')+'/'+kn[1])
    dosync('sync/nextlead/Add_Split_'+kn[0].split('/')[1]+'::'+kn[1]+'/request',str(stamp()))
    dosync('sync/nextlead/Add_Split_'+kn[0].split('/')[1]+'::'+kn[1]+'/request/'+myhost,str(stamp()))
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
   dosync('sync/ready/Del_'+pos[0].replace('possible','')+'_'+'--prefix'+'/request',str(stamp()))
   dosync('sync/ready/Del_'+pos[0].replace('possible','')+'_'+'--prefix'+'/request/'+myhost,str(stamp()))
   etcddel(pos[0])
  
  
if '1' in perfmon:
 queuethis('remknown.py','stop','system')
