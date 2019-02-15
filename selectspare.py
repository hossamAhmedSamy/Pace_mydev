#!/bin/python3.6
import subprocess,sys,socket
import json
from ast import literal_eval as mtuple
from etcdget import etcdget as get
from etcdput import etcdput as put
from etcddel import etcddel as dels 
from poolall import getall as getall
from sendhost import sendhost
#from syncpools import syncmypools
import logmsg
newop=[]
disksvalue=[]


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
    return ret
  
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


def diskreplace(myhost,defdisks,hosts,alldisks,replacelist,raids,pools,exclude,mindisksize):
 ret=0
 print('start replacing')
 if len(defdisks) < 1:
  print('no more defective disks checking for non-red host raids')
  if len(raids) < 1 :
   print('no raids too') 
   return
  raid=raids[0]
  raids.pop(0)
  if raid['name']=='free':
   return
  myhostpools=[pool['name'] for pool in pools if pool['host']==myhost ]
  disksinraid=[(disk['name'],disk['host'],disk['size']) for disk in alldisks if disk['raid'] == raid['name'] and disk['pool'] == raid['pool'] and disk['pool'] in myhostpools ]
  hcount=[]
  for host in hosts:
   hcount.append((host,str(disksinraid).count(host)))
  maxx=max(hcount,key=lambda x: x[1])
  nonblanced=[x for x in hcount if maxx[1] > x[1]]
  selectdisk=[]
  if len(nonblanced) > 0 and len(replacelist) > 0:
   selectdisk=[x for x in disksinraid if x[1]==maxx[0]]
   diskinfo=[x for x in alldisks if x['name']==selectdisk[0][0]]
   mindisksize=min(disksinraid,key=lambda x:norm(x[2]))
   mindisksize=mindisksize[2]
   mindisksize=norm(mindisksize)
   diskreplace(myhost,diskinfo,hosts,alldisks,replacelist,raids,pools,'limithost',mindisksize)
   return
  diskreplace(myhost,[],hosts,alldisks,replacelist,raids,pools,exclude,mindisksize)
  return
 defdisk=defdisks[0]
 dontuse=exclude
 if 'limithost' in exclude and len(hosts) > 1:
  dontuse=defdisk['host']
 disksinraid=[disk for disk in alldisks if disk['raid']==defdisk['raid'] and disk['name'] != defdisk['name'] and 'ONLI' in disk['changeop']]
 runninghosts=[disk['host'] for disk in alldisks if disk['raid']==defdisk['raid'] and disk['name'] != defdisk['name'] and 'ONLI' in disk['changeop'] and disk['host'] not in dontuse ]
 if mindisksize < 0 and len(disksinraid) > 0:
  mindisk=min(disksinraid,key=lambda x:norm(x['size']))
  mindisk=mindisk['size']
 else:
  mindisk=mindisksize
 disksvalues=[]
 for  rep in replacelist:
  diskvalue=float(0)
  if norm(rep['size']) == norm(mindisk) :
   diskvalue=diskvalue+1
  elif norm(rep['size']) > norm(mindisk): 
       diskvalue=diskvalue+float(1-(norm(rep['size']) - norm(mindisk))/norm(mindisk))
  else:
   diskvalue=-100000
  if dontuse in rep['host']:
   diskvalue=-100000
  if 'spare' in rep['raid']:
    diskvalue=diskvalue+10
  if rep['host'] not in runninghosts: 
   diskvalue=diskvalue+100
  disksvalues.append((rep,diskvalue)) 
 disksvalues=sorted(disksvalues,key=lambda x:x[1], reverse=True)
 if len(disksvalues) > 0:
  if disksvalues[0][1] < -10000:
   return
 if 'spare' in defdisk['raid'] :
  logmsg.sendlog('Dist3','info','system', defdisk['id'],defdisk['host'])
  cmdline=['/sbin/zpool', 'remove', defdisk['pool'],defdisk['name']]
  subprocess.run(cmdline,stdout=subprocess.PIPE)
  ret=replacelist
 elif 'logs' in defdisk['raid'] :
  cmdline=['/sbin/zpool', 'remove', defdisk['pool'],defdisk['name']]
  try:
   subprocess.check_call(cmdline)
   if spare['pool']==defdisk['pool']:
    cmdline=['/sbin/zpool', 'remove', defdisk['pool'],spare['name']]
    subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/sbin/zpool', 'add', faultdiskpool,'log']
   try: 
    ret=mustattach(cmdline,disksvalues,defdisk,myhost)
   except subprocess.CalledProcessError:
    pass
  except:
   pass 
 elif 'cache' in defdisk['raid'] :
  cmdline=['/sbin/zpool', 'remove', defdisk['pool'],defdisk['name']]
  try:
   subprocess.check_call(cmdline)
   cmdline=['/sbin/zpool', 'add', defdisk['pool'],'cache']
   try: 
    ret=mustattach(cmdline,disksvalues,defdisk,myhost)
   except subprocess.CalledProcessError:
    pass
  except:
   pass 
 elif 'stripe' in defdisk['raid'] :
  cmdline=['/sbin/zpool', 'attach','-f', defdisk['pool'],defdisk['name']]
  try: 
   ret=mustattach(cmdline,disksvalues,defdisk,myhost)
  except :
    pass
 elif 'mirror' in defdisk['raid']:
  cmdline=['/sbin/zpool', 'detach', defdisk['pool'],defdisk['name']]
  subprocess.run(cmdline,stdout=subprocess.PIPE)
  ret=replacelist
 else:
  cmdline=['/sbin/zpool', 'replace', '-f',defdisk['pool'],defdisk['name']]
  try:
   ret=mustattach(cmdline,disksvalues,defdisk,myhost)
  except subprocess.CalledProcessError:
   pass 
 replacelist=[x for x in replacelist if x['name']!=ret]
 defdisks.pop(0)
 diskreplace(myhost,defdisks,hosts,alldisks,replacelist,raids,pools,exclude,mindisksize)



def getbalance(diskA,diskB,balancetype):
 global newop
 w=0
 if diskB['size'] > diskA['size']:
  w=1000000
  return w
 if diskB['pool'] in diskA['pool'] and 'ree' not in diskA['pool']:
  w=1000001
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
 return w 
  
  
def selectthedisk(freedisks,raid,allraids,myhost):
 weights=[]
 finalw=[]
 balancetype=get('balancetype/'+raid['pool'])
 if 'stripe' not in raid['name']:
  for diskA in raid['disklist']:
   continue
 else:
   for diskA in raid['disklist']:
    for diskB in raid['disklist']:
     if diskA['name'] not in diskB['name']:
      finalw.append({'newd':diskA,'oldd':diskB,'w':0})
 for diskA in freedisks:
  for diskB in raid['disklist']: 
   w=getbalance(diskA,diskB,balancetype)
   finalw.append({'newd':diskA,'oldd':diskB,'w':w})
 finalw=sorted(finalw,key=lambda x:x['w'],reverse=True)
 return finalw[0] 
 
def solvestripepools(striperaids,freedisks,allraids,myhost):
 sparefit={}
 for disk in freedisks:
  sparefit[disk['name']]=[]
 for raid in striperaids:
  sparelist=selectthedisk(freedisks,raid,allraids,myhost)
  if len(sparelist) > 0:
   sparefit[sparelist['newd']['name']].append(sparelist)
 for k in sparefit:
  sparefit[k]=sorted(sparefit[k],key=lambda x:x['w'],reverse=True)
 for k in sparefit:
  oldd=sparefit[k][0]['oldd'] 
  newd=sparefit[k][0]['newd'] 
  olddpool=sparefit[k][0]['oldd']['pool'] 
 cmdline=['/sbin/zpool', 'attach','-f', olddpool,oldd['name']]
 try: 
  ret=mustattach(cmdline,newd,oldd,myhost)
 except:
  pass
 return
  
   
  
def spare2(*args):
 global newop
 allraids=[]
 myhost=args[0]
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
 freedisks=[ x for x in newop['disks']  if 'free' in x['raid']]  
 if len(freedisks) > 0 and len(striperaids) > 0 : 
  solvestripepools(striperaids, freedisks,allraids,myhost)
 exit()
 mypools=[x['name'] for x in newop['pools'] if myhost in x['host']]
 ready=get('ready','--prefix')
 possibles=get('possible','--prefix')
 toonline=[x for x in newop['disks'] if 'OFFLINE' in x['status'] and 'dhcp' in x['host'] and x['pool'] in mypools and (x['host'] in str(ready) or x['host'] in str(possibles))]
 for x in toonline:
  cmdline=['/sbin/zpool','online',x['pool'],x['name']]
  logmsg.sendlog('Dist7','info','system',x['id'],x['pool'])
  try:
   subprocess.check_call(cmdline)
   logmsg.sendlog('Disu7','info','system',x['id'],x['pool'])
   print('success')
  except:
   logmsg.sendlog('Difa7','info','system',x['id'],x['pool'])
   print('failed') 
 diskreplace(myhost,newop['defdisks'],newop['hosts'],newop['disks'],newop['freedisks']+newop['sparedisks'],newop['raids'],newop['pools'],'allowall',-1)
 return
 
 
if __name__=='__main__':
 spare2(*sys.argv[1:])
