#!/bin/python3.6
import subprocess,sys, logmsg
from ast import literal_eval as mtuple
from etcddel import etcddel as etcddel
from broadcast import broadcast as broadcast 
from broadcasttolocal import broadcasttolocal as broadcasttolocal
from etcdget import etcdget as get
from etcdgetlocal import etcdget as getlocal
from etcdput import etcdput as put 
from etcdputlocal import etcdput as putlocal 
import json
allow=get('allowedPartners')
if 'notallowed' in str(allow):
 exit()
cmdline='cat /pacedata/perfmon'
perfmon=str(subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout)
if '1' in perfmon:
 cmdline=['/TopStor/queuethis.sh','addknown.py','start','system']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
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
     exit()
  knowns=get('known','--prefix')
  if x[0].replace('possible','') in str(knowns):
   put('allowedPartners','notoall')
   etcddel('possible',x[0])
  putlocal(x[1],'configured','yes')
  put('known/'+x[0].replace('possible',''),x[1])
  put('ActivePartners/'+x[0].replace('possible',''),x[1])
  broadcasttolocal('ActivePartners/'+x[0].replace('possible',''),x[1])
  put('nextlead',x[0].replace('possible','')+'/'+x[1])
  cmdline=['/sbin/rabbitmqctl','add_user','rabb_'+x[0].replace('possible',''),'YousefNadody']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  cmdline=['/sbin/rabbitmqctl','set_permissions','-p','/','rabb_'+x[0].replace('possible',''),'.*','.*','.*']
  etcddel('losthost/'+x[0].replace('possible',''))
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  put('change/'+x[0].replace('possible','')+'/booted',x[1])
  put('tosync','yes')
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
if '1' in perfmon:
 cmdline=['/TopStor/queuethis.sh','addknown.py','stop','system']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
