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
for pos in possible:
 posname=pos[0].replace('possible','')
 if posname in str(active):
  print(posname)
  etcddel('lost',posname)
  etcddel('poss',posname)
  put('known/'+posname,pos[1])
  put('sync/known/'+posname+'_'+pos[1]+'/request','known_'+'known_'+str(stamp()))
  put('sync/known/'+posname+'_'+pos[1]+'/request/'+myhost,'known_'+'known_'+str(stamp()))
#  broadcasttolocal('known/'+posname,pos[1])
  aliast = getlocal(pos[1],'alias/'+posname)[0]
  print('pos',pos[1],posname,str(aliast))
  put('alias/'+posname,str(aliast))
  print('############')
  put('sync/alias/'+posname+'_'+str(aliast)+'/request','alias_'+str(stamp()))
  put('sync/alias/'+posname+'_'+str(aliast)+'/request/'+myhost,'alias_'+str(stamp()))
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
  put('sync/known/'+x[0].replace('possible','')+'_'+x[1]+'/request','known_'+str(stamp()))
  put('sync/known/'+x[0].replace('possible','')+'_'+x[1]+'/request/'+myhost,'known_'+str(stamp()))
#  broadcasttolocal('known/'+x[0].replace('possible',''),x[1])
  hostsubnet = getlocal(x[1],'hostipsubnet/'+x[0].replace('possible',''))[0]
  if hostsubnet == -1:
   hostsubnet = "24"
  #etcddel('sync',x[0].replace('possible',''))
  etcddel('modified',x[0].replace('possible',''))
  #deltolocal('sync',x[0].replace('possible',''))
  deltolocal('modified',x[0].replace('possible',''))
  put('ActivePartners/'+x[0].replace('possible',''),x[1])
  put('sync/ActivePartners/'+x[0].replace('possible','')+'_'+x[1]+'/request','ActivePartners_'+str(stamp()))
  put('sync/ActivePartners/'+x[0].replace('possible','')+'_'+x[1]+'/request/'+myhost,'ActivePartners_'+str(stamp()))

  put('hostipsubnet/'+x[0].replace('possible',''),hostsubnet)
  put('sync/hostipsubnet/'+x[0].replace('possible','')+'_'+x[1]+'/request/'+myhost,'hostipsubnet_'+str(stamp()))
  put('sync/hostipsubnet/'+x[0].replace('possible','')+'_'+x[1]+'/request','hostipsubnet_'+str(stamp()))
  put('configured/'+x[0].replace('possible',''),'yes')
  put('sync/configured/'+x[0].replace('possible','')+'_yes/request','configured_'+str(stamp()))
  put('sync/configured/'+x[0].replace('possible','')+'_yes/request/'+myhost,'configured_'+str(stamp()))
#  broadcasttolocal('hostipsubnet/'+x[0].replace('possible',''),hostsubnet)
#  broadcasttolocal('ActivePartners/'+x[0].replace('possible',''),x[1])
#  broadcasttolocal('configured/'+x[0].replace('possible',''),'yes')
  put('nextlead',x[0].replace('possible','')+'/'+x[1])
  put('sync/nextlead/'+x[0].replace('possible','')+'_'+x[1]+'/request/'+myhost,'nextlead_'+str(stamp()))
  put('sync/nextlead/'+x[0].replace('possible','')+'_'+x[1]+'/request','nextlead_'+str(stamp()))
  aliast = getlocal(x[1],'alias/'+x[0].replace('possible',''))[0]
  put('alias/'+x[0].replace('possible',''),str(aliast))
  put('sync/alias/'+x[0].replace('possible','')+'_'+x[1]+'/request/'+myhost,'alias_'+str(stamp()))
  put('sync/alias/'+x[0].replace('possible','')+'_'+x[1]+'/request','alias_'+str(stamp()))
#  broadcasttolocal('nextlead',x[0].replace('possible','')+'/'+x[1])
  cmdline=['/sbin/rabbitmqctl','add_user','rabb_'+x[0].replace('possible',''),'YousefNadody']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  cmdline=['/sbin/rabbitmqctl','set_permissions','-p','/','rabb_'+x[0].replace('possible',''),'.*','.*','.*']
  etcddel('losthost/'+x[0].replace('possible',''))
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  put('change/'+x[0].replace('possible','')+'/booted',x[1])
#  put('tosync','yes')
#  broadcast('broadcast','/TopStor/pump.sh','syncnext.sh','nextlead','nextlead')
  if x[0].replace('possible','') in str(knowns):
   put('allowedPartners','notoall')
   etcddel('possible',x[0])
   logmsg.sendlog('AddHostsu01','info',arg[-1],name)
   queuethis('AddHost','stop',bargs[-1])
else:
 print('possible is empty')
queuethis('addknown.py','stop','system')
