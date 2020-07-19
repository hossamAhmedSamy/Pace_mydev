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
toactive=get('toactive','--prefix')
if toactive != []:
 for x in toactive:
  Active=get('ActivePartners','--prefix')
  if x[0].replace('toactive','') in str(Active):
   etcddel('toactive',x[0])
  put('known/'+x[0].replace('toactive',''),x[1])
  put('nextlead',x[0].replace('toactive','/')+x[1])
  etcddel('losthost/'+x[0].replace('toactive',''))
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  put('change/'+x[0].replace('toactive','')+'/booted',x[1])
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
 print('toactive is empty')
if '1' in perfmon:
 cmdline=['/TopStor/queuethis.sh','addknown.py','stop','system']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
