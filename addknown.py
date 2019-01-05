#!/bin/python3.6
import subprocess,sys, logmsg
from ast import literal_eval as mtuple
from etcddel import etcddel as etcddel
from broadcast import broadcast as broadcast 
from etcdget import etcdget as get
from etcdgetlocal import etcdget as getlocal
from etcdput import etcdput as put 
import json
x=subprocess.check_output(['pgrep','addknown'])
x=str(x).replace("b'","").replace("'","").split('\\n')
x=[y for y in x if y != '']
if(len(x) > 1 ):
 print('process still running',len(x))
 exit()
possible=get('possible','--prefix')
print('possible=',possible)
if possible != []:
 for x in possible:
  print('x=',x[0], x[1])
  etcddel('possible',x[0])
  put('known/'+x[0].replace('possible',''),x[1])
  put('nextlead',x[0].replace('possible','')+'/'+x[1])
  cmdline=['/sbin/rabbitmqctl','add_user','rabb_'+x[0].replace('possible',''),'YousefNadody']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  cmdline=['/sbin/rabbitmqctl','set_permissions','-p','/','rabb_'+x[0].replace('possible',''),'.*','.*','.*']
  etcddel('losthost/'+x[0].replace('possible',''))
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  put('change/'+x[0].replace('possible','')+'/booted',x[1])
  broadcast('broadcast','/TopStor/pump.sh','syncnext.sh','nextlead','nextlead')
  #cmdline=['/pace/iscsiwatchdog.sh','2>/dev/null']
  #subprocess.run(cmdline,stdout=subprocess.PIPE)
#  cmdline=['/bin/sleep','5']
#  subprocess.run(cmdline,stdout=subprocess.PIPE)
#  cmdline=['/pace/iscsiwatchdog.sh','2>/dev/null']
#  subprocess.run(cmdline,stdout=subprocess.PIPE)
#  cmdline=['/bin/sleep','5']
#  subprocess.run(cmdline,stdout=subprocess.PIPE)
else:
 print('possible is empty')
known=get('known','--prefix')
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
  if( '-1' in str(heart) or len(heart) < 1):
   print('the known ',kn[0].replace('known/',''),' is gone, notfound')
   etcddel(kn[0])
   if kn[1] in str(nextone):
    etcddel('nextlead')
   logmsg.sendlog('Partst02','warning','system', kn[0].replace('known/',''))
   etcddel('ready/'+kn[0].replace('known/',''))
   etcddel('old','--prefix')
   cmdline=['/pace/hostlost.sh',kn[0].replace('known/','')]
   subprocess.run(cmdline,stdout=subprocess.PIPE)
   etcddel('localrun/'+str(kn[0]))
   broadcast('broadcast','/TopStor/pump.sh','zpooltoimport.py','all')
  elif (heart[0][1] not in kn[1]):
   if kn[1] in str(nextone):
    etcddel('nextlead')
   etcddel(kn[0])
   logmsg.sendlog('Partst02','warning','system', kn[0].replace('known/',''))
   print('the known ',kn[0],' is notworking, notfound')
   cmdline=['/pace/hostlost.sh',kn[0].replace('known/','')]
   subprocess.run(cmdline,stdout=subprocess.PIPE)
   etcddel('localrun/'+kn[0].replace('known/',''))
   broadcast('broadcast','/TopStor/pump.sh','zpooltoimport.py','all')
   cmdline=['/sbin/rabbitmqctl','delete_user','rabb_'+x[0].replace('possible'),'YousefNadody']
   subprocess.run(cmdline,stdout=subprocess.PIPE)
  else:
   if nextone == []:
    put('nextlead',kn[0].replace('known/','')+'/'+kn[1])
    broadcast('broadcast','/TopStor/pump.sh','syncnext.sh','nextlead','nextlead')
