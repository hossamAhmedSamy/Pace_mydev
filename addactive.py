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
cmdline='cat /pacedata/perfmon'
perfmon=str(subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout)
if '1' in perfmon:
 cmdline=['/TopStor/queuethis.sh','addknown.py','start','system']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
toactivate=get('toactivate','--prefix')
if toactivate != []:
 for x in toactivate:
  Active=get('ActivePartners','--prefix')
  if x[0].replace('toactivate','') in str(Active):
   etcddel('toactivate',x[0])
  put('known/'+x[0].replace('toactivate',''),x[1])
  put('nextlead',x[0].replace('toactivate','/')+x[1])
  etcddel('losthost/'+x[0].replace('toactivate',''))
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  frstnode=get('frstnode')
  if x[0].replace('possible','') not in frstnode[0]:
   newfrstnode=frstnode[0]+'/'+x[0].repalce('possible','')
  put('change/'+x[0].replace('toactivate','')+'/booted',x[1])
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
 print('toactivate is empty')
if '1' in perfmon:
 cmdline=['/TopStor/queuethis.sh','addknown.py','stop','system']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
