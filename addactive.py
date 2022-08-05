#!/bin/python3.6
import subprocess,sys, logmsg, socket
from logqueue import queuethis
from ast import literal_eval as mtuple
from etcddel import etcddel as etcddel
from broadcast import broadcast as broadcast 
from time import time as stamp
from broadcasttolocal import broadcasttolocal as broadcasttolocal
from etcdget import etcdget as get
from etcdgetlocal import etcdget as getlocal
from etcdput import etcdput as put 
from etcdputlocal import etcdput as putlocal 
import json


myhost=socket.gethostname()
with open('/pacedata/perfmon','r') as f:
 perfmon = f.readline() 
if '1' in perfmon:
 queuethis('addknown.py','start','system')
toactivate=get('toactivate','--prefix')
if toactivate != []:
 for x in toactivate:
  Active=get('ActivePartners','--prefix')
  if x[0].replace('toactivate','') in str(Active):
   etcddel('toactivate',x[0])
  put('known/'+x[0].replace('toactivate',''),x[1])
  put('sync/known/Add_'+x[0].replace('toactivate','')+'_'+x[1]+'/request','known_'+str(stamp()))
  put('sync/known/Add_'+x[0].replace('toactivate','')+'_'+x[1]+'/request/'+myhost,'known_'+str(stamp()))
  put('nextlead',x[0].replace('toactivate','')+'/'+x[1])
  put('sync/nextlead/Add_'+x[0].replace('toactivate','')+'_'+x[1]+'/request','nextlead_'+str(stamp()))
  put('sync/nextlead/Add_'+x[0].replace('toactivate','')+'_'+x[1]+'/request/'+myhost,'nextlead_'+str(stamp()))
  etcddel('losthost/'+x[0].replace('toactivate',''))
  put('sync/losthost/Del_'+x[0].replace('toactivate','')+'_--prefix/request','losthost_'+str(stamp()))
  put('sync/losthost/Del_'+x[0].replace('toactivate','')+'_--prefix/requesti/'+myhost,'losthost_'+str(stamp()))
  frstnode=get('frstnode')
  print('frst',frstnode[0])
  if x[0].replace('toactivate','') not in frstnode[0]:
   newfrstnode=frstnode[0]+'/'+x[0].replace('toactivate','')
   put('frstnode',newfrstnode)
  put('change/'+x[0].replace('toactivate','')+'/booted',x[1])
  put('tosync','yes')
  #broadcast('broadcast','/TopStor/pump.sh','syncnext.sh','nextlead','nextlead')
else:
 print('toactivate is empty')
if '1' in perfmon:
 queuethis('addknown.py','stop','system')
