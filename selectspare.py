#!/bin/python3.6
import subprocess,sys,socket
import json
from ast import literal_eval as mtuple
from collections import Counter
from etcdget import etcdget as get
from etcdput import etcdput as put
from etcddel import etcddel as dels 
from poolall import getall as getall
from sendhost import sendhost
#from syncpools import syncmypools
import logmsg
newop=[]
disksvalue=[]
usedfree=[]

def mustattach(cmdline,disksallowed,defdisk,myhost):
   print('################################################')
   if len(disksallowed) < 1 : 
    return 'na'
   print('helskdlskdkddlsldssd#######################')
   cmd=cmdline
   spare=disksallowed
   spareplsclear=get('clearplsdisk/'+spare['name'])
   spareiscleared=get('cleareddisk/'+spare['name']) 
   if spareiscleared[0] != spareplsclear[0]:
    put('clearplsdisk/'+spare['name'],spare['host'])
    dels('cleareddisk/'+spare['name']) 
    hostip=get('ready/'+spare['host'])
    z=['/TopStor/pump.sh','Zpoolclrrun',spare['name']]
    msg={'req': 'Zpool', 'reply':z}
    sendhost(hostip[0], str(msg),'recvreply',myhost)
    return spare['name']
   dels('clearplsdisk/'+spare['name']) 
   dels('cleareddisk/'+spare['name']) 
   if 'attach' in cmd:
    print('hi')
   else:
    if spare['pool']==defdisk['pool']:
     cmdline2=['/sbin/zpool', 'remove', defdisk['pool'],spare['name']]
     subprocess.run(cmdline2,stdout=subprocess.PIPE)
   if 'attach' in cmd:
    logmsg.sendlog('Dist6','info','system', spare['id'],defdisk['raid'],defdisk['pool'],myhost)
   else:
    logmsg.sendlog('Dist2','info','system', defdisk['id'],spare['id'],myhost)
   cmdline3=['/sbin/zpool', 'labelclear', spare['name']]
   subprocess.run(cmdline3,stdout=subprocess.PIPE)
   cmd.append(spare['name'])
   try: 
    subprocess.check_call(cmd)
    if 'attach' in cmd:
     logmsg.sendlog('Disu6','info','system', spare['id'],defdisk['raid'],defdisk['pool'],myhost)
    else:
     logmsg.sendlog('Disu2','info','system', defdisk['id'],spare['id'],myhost)
    #syncmypools('all')
    print('hihihi')
    return spare['name'] 
   except subprocess.CalledProcessError:
    if 'attach' in cmd:
     logmsg.sendlog('Difa6','warning','system', spare['id'],defdisk['raid'],defdisk['pool'],myhost)
    else:
     logmsg.sendlog('Difa2','warning','system', defdisk['id'],spare['id'],myhost)
    return 'fault' 
  
def norm(val):
 units={'B':1/1024**2,'K':1/1024, 'M': 1, 'G':1024 , 'T': 1024**2 }
 if type(val)==float:
  return val
 if val[-1] != 'B':
  return float(val) 
 else:
  if val[-2] in list(units.keys()):
   return float(val[:-2])*float(units[val[-2]])
  else:
   return float(val[:-1])*float(units['B'])



def getbalance(diskA,diskB,balancetype,hostcounts):
 global newop
 raidhosts=hostcounts
 w=0
 if diskB['size'] > diskA['size']:
  w=1000000
  return w
 if 'free' in diskA['changeop']:
  w=1
 if 'stripe' in diskB['raid']: # if stripe calcualte the 
  if 'useable' in balancetype:
   sizediff=10*(norm(diskA['size'])-norm(diskB['size'])) # tendency to same size
   w+=sizediff+int(diskA['host'] in diskB['host'])
  else:
   sizediff=(norm(diskA['size'])-norm(diskB['size']))
   w+=sizediff+10*int(diskA['host'] in diskB['host'])    # tendency to otherhost
 elif 'free' in diskA['changeop']: # getting weight of free disk inRaid 
  if 'useable' in balancetype:
   sizediff=10*(norm(diskA['size'])-norm(diskB['size'])) # tendency to same size
   if 'mirror' in diskB['raid']:    # useable type not to mirror large disks
    if diskA['size'] > diskB['size']:
     w=100002
     return w
    raidhosts[diskA['host']]+=1
    raidhosts[diskB['host']]-=1
    w+=sizediff+10*int(diskA['host'] in diskB['host'])
  else:
   sizediff=(norm(diskA['size'])-norm(diskB['size']))
   if 'mirror' in diskB['raid']:
    w+=sizediff+10*int(diskA['host'] in diskB['host'])
 elif diskB['raid'] in diskA['raid']: # getting weight of current disk inRaid 
  if 'useable' in balancetype:
   sizediff=10*(norm(diskA['size'])-norm(diskB['size'])) # tendency to same size
   if 'mirror' in diskB['raid']:
    w+=sizediff+10*int(diskA['host'] in diskB['host'])
  else:
   sizediff=(norm(diskA['size'])-norm(diskB['size']))
   if 'mirror' in diskB['raid']:
    w+=sizediff+10*int(diskA['host'] in diskB['host'])
 return w 
  
  
def selectthedisk(freedisks,raid,allraids,allhosts,myhost):
 weights=[]
 finalw=[]
 hostcounts=allhosts
 balancetype=get('balancetype/'+raid['pool'])
 if 'stripe' not in raid['name'] and 'ONLINE' in raid['status'] :
  for disk in raid['disklist']:
   hostcounts[disk['host']]+=1
  for diskA in raid['disklist']:
   for diskB in raid['disklist']:
    if diskA['name'] not in diskB['name']:
     w=getbalance(diskA,diskB,balancetype,hostcounts)
     finalw.append({'newd':diskA,'oldd':diskB,'w':w})
  for diskA in freedisks:
   for diskB in raid['disklist']:
    if diskA['name'] not in diskB['name']:
     w=getbalance(diskA,diskB,balancetype,hostcounts)
     finalw.append({'newd':diskA,'oldd':diskB,'w':w})
 elif 'stripe' in raid['name']:
  for diskA in freedisks:
   for diskB in raid['disklist']: 
    w=getbalance(diskA,diskB,balancetype,hostcounts)
    finalw.append({'newd':diskA,'oldd':diskB,'w':w})
 finalw=sorted(finalw,key=lambda x:x['w'])
 return finalw[0] 


def solveonlineraids(onlineraids,freedisks,allraids,allhosts,myhost):
 global usedfree
 sparefit={}
 for disk in freedisks:
  sparefit[disk['name']]=[]
 for raid in onlineraids:
  sparelist=selectthedisk(freedisks,raid,allraids,allhosts,myhost)
  if len(sparelist) > 0:
   sparefit[sparelist['newd']['name']].append(sparelist)
 for k in sparefit:
  sparefit[k]=sorted(sparefit[k],key=lambda x:x['w'])
 for k in sparefit:
  oldd=sparefit[k][0]['oldd'] 
  newd=sparefit[k][0]['newd'] 
  olddpool=sparefit[k][0]['oldd']['pool'] 
  if 'mirror' in oldd['raid']:
   cmdline=['/sbin/zpool', 'attach','-f', olddpool,oldd['name']]
   ret=mustattach(cmdline,newd,oldd,myhost)
   if 'fault' not in ret:
    usedfree.append(ret)
    cmdline=['/sbin/zpool', 'detach', olddpool,oldd['name']]
    subprocess.run(cmdline,stdout=subprocess.PIPE)
    
 
def solvestriperaids(striperaids,freedisks,allraids,myhost):
 global usedfree
 sparefit={}
 for raid in striperaids:
  sparelist=selectthedisk(freedisks,raid,allraids,{},myhost)
  if len(sparelist) > 0:
   try:
    sparefit[sparelist['newd']['name']].append(sparelist)
   except:
    sparefit[sparelist['newd']['name']]=[]
    sparefit[sparelist['newd']['name']].append(sparelist)
 for k in sparefit:
  sparefit[k]=sorted(sparefit[k],key=lambda x:x['w'])
 for k in sparefit:
  oldd=sparefit[k][0]['oldd'] 
  newd=sparefit[k][0]['newd'] 
  olddpool=sparefit[k][0]['oldd']['pool'] 
 cmdline=['/sbin/zpool', 'attach','-f', olddpool,oldd['name']]
 ret=mustattach(cmdline,newd,oldd,myhost)
 if 'fault' not in ret:
  usedfree.append(ret)
 return
  
   
  
def spare2(*args):
 global newop
 global usedfree 
 freedisks=[]
 allraids=[]
 myhost=args[0]
 hosts=get('ready','--prefix')
 allhosts={}
 for host in hosts:
  allhosts[host[0].replace('ready/','')]=0
 newop=getall(myhost)
 striperaids=[]
 if newop==[-1]:
  return
 degradedpools=[x for x in newop['pools'] if myhost in x['host'] and  'DEGRADED' in x['changeop']]
 #strippools=[x for x in newop['pools'] if myhost in x['host']  and 'stripe' in str(x[raidlist])]
 for spool in newop['pools']:
  for sraid in spool['raidlist']:
   if 'ree' not in sraid['name']:
    allraids.append(sraid)
 striperaids=[x for x in allraids if 'stripe' in x['name']]
 onlineraids=[x for x in allraids if 'ONLINE' in x['changeop']]
 freedisks=[ x for x in newop['disks']  if 'free' in x['raid']]  
 disksfree=[x for x in freedisks if x['name'] not in str(usedfree)]
 if len(disksfree) > 0 and len(striperaids) > 0 : 
  solvestriperaids(striperaids, disksfree,allraids,myhost)
 disksfree=[x for x in freedisks if x['name'] not in str(usedfree)]
 if len(disksfree) > 0 and len(onlineraids) > 0 : 
  solveonlineraids(onlineraids, disksfree,allraids,allhosts,myhost)
 return
 
 
if __name__=='__main__':
 spare2(*sys.argv[1:])
