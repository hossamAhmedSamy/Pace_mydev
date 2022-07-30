#!/bin/python3.6
import socket, subprocess, logmsg
from etcddel import etcddel as etcddel
from deltolocal import deltolocal 
from logqueue import queuethis
from broadcast import broadcast as broadcast 
from time import time as stamp
from broadcasttolocal import broadcasttolocal as broadcasttolocal
from etcdget import etcdget as get
from etcdgetlocal import etcdget as getlocal
from etcdput import etcdput as put 
from etcdputlocal import etcdput as putlocal 

myhost=socket.gethostname()
possible=get('possible','--prefix')
active = get('Active','--prefix')
stampit = str(stamp())
for pos in possible:
 posname=pos[0].replace('possible','')
 if posname in str(active):
  print(posname)
  etcddel('lost',posname)
  etcddel('poss',posname)
  put('known/'+posname,pos[1])
  put('sync/known/Add_'+posname+'_'+pos[1]+'/request','known_'+'known_'+stampit)
  put('sync/known/Add_'+posname+'_'+pos[1]+'/request/'+myhost,'known_'+'known_'+stampit)
#  broadcasttolocal('known/'+posname,pos[1])
  aliast = getlocal(pos[1],'alias/'+posname)[0]
  print('pos',pos[1],posname,str(aliast))
  put('alias/'+posname,str(aliast))
  print('############')
  put('sync/alias/Add_'+posname+'_'+str(aliast).replace('_',':::').replace('/',':::')+'/request','alias_'+stampit)
  put('sync/alias/Add_'+posname+'_'+str(aliast).replace('_',':::').replace('/',':::')+'/request/'+myhost,'alias_'+stampit)
allow=get('allowedPartners')
if 'notallowed' in str(allow):
 exit()
with open('/pacedata/perfmon','r') as f:
 perfmon = f.readline() 
queuethis('addknown','start','system')
possible=get('possible','--prefix')
print('possible=',possible)
if possible != []:
 for x in possible:
  print('x=',x[0], x[1])
  if 'yestoall' not in str(allow):
   print(x[0].replace('possible',''))
   print(str(allow))
   if x[0].replace('possible','') not in str(allow):
    print('iamhere')
    Active=get('AcivePartners','--prefix')
    if x[0].replace('possible','') not in str(Active):
     print('imhere2')
     queuethis('addknown','stop','system')
     exit()
  knowns=get('known','--prefix')
  putlocal(x[1],'configured/'+myhost,'yes')
  frstnode=get('frstnode')
  if frstnode == [-1]:
   frstnode = [""] 
  if x[0].replace('possible','') not in frstnode[0]:
   newfrstnode=frstnode[0]+'/'+x[0].replace('possible','')
   put('frstnode',newfrstnode)
  put('known/'+x[0].replace('possible',''),x[1])
  put('sync/known/Add_'+x[0].replace('possible','')+'_'+x[1]+'/request','known_'+stampit)
  put('sync/known/Add_'+x[0].replace('possible','')+'_'+x[1]+'/request/'+myhost,'known_'+stampit)
  hostsubnet = getlocal(x[1],'hostipsubnet/'+x[0].replace('possible',''))[0]
  if hostsubnet == -1:
   hostsubnet = "24"
  etcddel('modified',x[0].replace('possible',''))
  deltolocal('modified',x[0].replace('possible',''))
  put('ActivePartners/'+x[0].replace('possible',''),x[1])
  put('sync/ActivePartners/Add_'+x[0].replace('possible','')+'_'+x[1]+'/request','ActivePartners_'+stampit)
  put('sync/ActivePartners/Add_'+x[0].replace('possible','')+'_'+x[1]+'/request/'+myhost,'ActivePartners_'+stampit)

  put('hostipsubnet/'+x[0].replace('possible',''),hostsubnet)
  put('sync/hostipsubnet/Add_'+x[0].replace('possible','')+'_'+x[1]+'/request/'+myhost,'hostipsubnet_'+stampit)
  put('sync/hostipsubnet/Add_'+x[0].replace('possible','')+'_'+x[1]+'/request','hostipsubnet_'+stampit)
  put('configured/'+x[0].replace('possible',''),'yes')
  put('sync/configured/Add_'+x[0].replace('possible','')+'_yes/request','configured_'+stampit)
  put('sync/configured/Add_'+x[0].replace('possible','')+'_yes/request/'+myhost,'configured_'+stampit)
  put('nextlead',x[0].replace('possible','')+'/'+x[1])
  put('sync/nextlead/Add_'+x[0].replace('possible','')+'_'+x[1]+'/request/'+myhost,'nextlead_'+stampit)
  put('sync/nextlead/Add_'+x[0].replace('possible','')+'_'+x[1]+'/request','nextlead_'+stampit)
  aliast = getlocal(x[1],'alias/'+x[0].replace('possible',''))[0]
  put('alias/'+x[0].replace('possible',''),str(aliast))
  put('sync/alias/Add_'+x[0].replace('possible','')+'_'+x[1].replace('_',':::').replace('/',':::')+'/request/'+myhost,'alias_'+stampit)
  put('sync/alias/Add_'+x[0].replace('possible','')+'_'+x[1].replace('_',':::').replace('/',':::')+'/request','alias_'+stampit)
  cmdline=['/sbin/rabbitmqctl','add_user','rabb_'+x[0].replace('possible',''),'YousefNadody']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  cmdline=['/sbin/rabbitmqctl','set_permissions','-p','/','rabb_'+x[0].replace('possible',''),'.*','.*','.*']
  etcddel('losthost/'+x[0].replace('possible',''))
  put('sync/cleanlost/Del_'+x[0].replace('possible','')+'_--prefix/request','cleanlost_'+stampit)
  put('sync/cleanlost/Del_'+x[0].replace('possible','')+'_--prefix/request/'+myhost,'cleanlost_'+stampit)
  put('change/'+x[0].replace('possible','')+'/booted',x[1])
#  put('tosync','yes')
#  broadcast('broadcast','/TopStor/pump.sh','syncnext.sh','nextlead','nextlead')
  if x[0].replace('possible','') in str(knowns):
   put('allowedPartners','notoall')
   put('sync/allowedPartners/Add_notoall_/request','allwedPartners_'+stampit)
   put('sync/allowedPartners/Add_notoall_/request/'+myhost,'allwedPartners_'+stampit)
   etcddel('possible',x[0])
   put('possible',x[0])
   logmsg.sendlog('AddHostsu01','info',arg[-1],name)
   queuethis('AddHost','stop',bargs[-1])
else:
 print('possible is empty')
queuethis('addknown.py','stop','system')
