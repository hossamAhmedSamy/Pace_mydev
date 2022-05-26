#!/bin/python3.6
import subprocess,sys,socket, os
from socket import gethostname as hostname
from levelthis import levelthis
from logqueue import queuethis
import json
from ast import literal_eval as mtuple
from diskdata import diskdata
from broadcasttolocal import broadcasttolocal
from collections import Counter
from etcdgetpy import etcdget as get
from etcdput import etcdput as put
from etcddel import etcddel as dels 
from poolall import getall as getall
from sendhost import sendhost
#from syncpools import syncmypools
import logmsg
os.environ['ETCDCTL_API']= '3'
newop=[]
disksvalue=[]
usedfree=[]
myhost = hostname()
def mustattach(cmdline,disksallowed,defdisk,myhost):
   print('################################################')
   if len(disksallowed) < 1 : 
    return 'na'
   print('helskdlskdkddlsldssd#######################')
   cmd=cmdline.copy()
   spare=disksallowed
   print('spare',spare)
   print('###########################')
   spareplsclear=get('clearplsdisk/'+spare['actualdisk'])
   spareiscleared=get('cleareddisk/'+spare['actualdisk']) 
   if spareiscleared[0] != spareplsclear[0] or spareiscleared[0] == -1:
    print('asking to clear')
    put('clearplsdisk/'+spare['actualdisk'],spare['host'])
    dels('cleareddisk/'+spare['actualdisk']) 
    hostip=get('ready/'+spare['host'])
    z=['/TopStor/pump.sh','Zpoolclrrun',spare['actualdisk']]
    msg={'req': 'Zpool', 'reply':z}
    sendhost(hostip[0], str(msg),'recvreply',myhost)
    print('returning')
    offlinethis=['/sbin/zpool', 'clear', defdisk['pool'] ]
    subprocess.run(offlinethis,stdout=subprocess.PIPE)
    return 'wait' 
   dels('clearplsdisk/'+spare['actualdisk']) 
   dels('cleareddisk/'+spare['actualdisk']) 
   if 'replace' in cmd:
    #cmd = cmd+['/dev/'+spare['actualdisk'],'/dev/'+defdisk['actualdisk']] 
    if 'scsi' in defdisk['actualdisk']:
      defdisk['actualdisk'] = 'disk/by-id/'+defdisk['pool'] 
    offlinethis=['/sbin/zpool', 'clear', defdisk['pool'] ]
    subprocess.run(offlinethis,stdout=subprocess.PIPE)
    cmd = cmd+['/dev/'+defdisk['actualdisk'],'/dev/disk/by-id/'+spare['name']] 
    print('cmd', cmd)
    res = subprocess.run(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print('result', res.stderr.decode())    
   return
 
def mustattachold(cmdline,disksallowed,defdisk,myhost):
   print('################################################')
   if len(disksallowed) < 1 : 
    return 'na'
   print('helskdlskdkddlsldssd#######################')
   cmd=cmdline.copy()
   spare=disksallowed
   print('spare',spare)
   print('###########################')
   spareplsclear=get('clearplsdisk/'+spare['actualdisk'])
   spareiscleared=get('cleareddisk/'+spare['actualdisk']) 
   if spareiscleared[0] != spareplsclear[0] or spareiscleared[0] == -1:
    print('asking to clear')
    put('clearplsdisk/'+spare['actualdisk'],spare['host'])
    dels('cleareddisk/'+spare['actualdisk']) 
    hostip=get('ready/'+spare['host'])
    z=['/TopStor/pump.sh','Zpoolclrrun',spare['actualdisk']]
    msg={'req': 'Zpool', 'reply':z}
    sendhost(hostip[0], str(msg),'recvreply',myhost)
    print('returning')
    return 'wait' 
   dels('clearplsdisk/'+spare['actualdisk']) 
   dels('cleareddisk/'+spare['actualdisk']) 
   if 'attach' in cmd:
    print('attach in command')
   else:
    if spare['pool']==defdisk['pool']:
     cmdline2=['/sbin/zpool', 'remove', defdisk['pool'],spare['actualdisk']]
     subprocess.run(cmdline2,stdout=subprocess.PIPE)
   if 'attach' in cmd:
    logmsg.sendlog('Dist6','info','system', spare['id'],defdisk['raid'],defdisk['pool'],myhost)
   else:
    logmsg.sendlog('Dist2','info','system', defdisk['id'],spare['id'],myhost)
   cmdline3=['/sbin/zpool', 'labelclear', spare['actualdisk']]
   subprocess.run(cmdline3,stdout=subprocess.PIPE)
   cmd.append(defdisk['actualdisk'])
   cmd.append(spare['actualdisk'])
   try: 
    print('cmd',cmd)
    subprocess.check_call(cmd)
    if 'attach' in cmd:
     logmsg.sendlog('Disu6','info','system', spare['id'],defdisk['raid'],defdisk['pool'],myhost)
     put('fixpool/'+defdisk['pool'],'1')
    else:
     logmsg.sendlog('Disu2','info','system', defdisk['id'],spare['id'],myhost)
    #syncmypools('all')
    print('hihihi')
    return spare['actualdisk'] 
   except subprocess.CalledProcessError:
    return 'fault'
    cmd=cmdline.copy()
    cmd.append('/dev/'+defdisk['devname'])
    cmd.append(spare['actualdisk'])
    try: 
     subprocess.check_call(cmd)
     if 'attach' in cmd:
      logmsg.sendlog('Disu6','info','system', spare['id'],defdisk['raid'],defdisk['pool'],myhost)
      put('fixpool/'+defdisk['pool'],'1')
     else:
      logmsg.sendlog('Disu2','info','system', defdisk['id'],spare['id'],myhost)
    #syncmypools('all')
      print('hihihi')
     return spare['actualdisk'] 
    except subprocess.CalledProcessError:
     if 'attach' in cmd:
      logmsg.sendlog('Difa6','warning','system', spare['id'],defdisk['raid'],defdisk['pool'],myhost)
     else:
      logmsg.sendlog('Difa2','warning','system', defdisk['id'],spare['id'],myhost)
     return 'fault' 
   put('fixpool/'+defdisk['pool'],'1')
  
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



def getbalance(diskA,diskB,balancetype,hostcounts,onlinedisks=[]):
 global newop
 print('################################################################################33')
 print('diskB', diskB)
 print('diskA', diskA)
 raidhosts=hostcounts.copy()
 w=0
 if 'free' in diskA['changeop']:
  w=1
########## Stripe  DiskA free policy: Any###################################
 if 'stripe' in diskB['raid']: # if stripe calcualte the 
  print('spare1')
  if norm(diskB['size']) > norm(diskA['size']):
   print('spare1_1')
   w=1000000
   return w
########## Stripe  DiskA free policy: Useability###############################
  if 'useable' in balancetype:
   print('spare1_2')
   sizediff=10*(norm(diskA['size'])-norm(diskB['size'])) # tendency to same size
   w+=sizediff+int(diskA['host'] in diskB['host'])
   return w
########## Stripe  DiskA free policy: Availability##############################
  else:
   print('spare1_3')
   sizediff=(norm(diskA['size'])-norm(diskB['size']))
   w+=sizediff+10*int(diskA['host'] in diskB['host'])    # tendency to otherhost
   return w
######### RAID DiskB online DiskA free policy: useability #####################
 elif 'free' in diskA['changeop'] and 'ONLINE' in diskB['status']:# DiskB online
  print('spare2')
  if 'useable' in balancetype:
   print('spare2_1')
   sizediff=(norm(diskA['size'])-norm(diskB['size'])) # tendency to same size
 ########### Mirror and DiskB online diskA free policy: useability ############
   if 'mirror' in diskB['raid']:    # useable type not to mirror large disks
    print('spare2_2')
    if norm(diskA['size']) > norm(diskB['size']):
     print('spare2_3')
     w=100002
     return w
    print('spare2_4')
    w+=10*sizediff+int(diskA['host'] in diskB['host'])
    return w
 ########### RAID and DiskB online diskA free policy: Availability #########
  else:
   print('spare2_5')
   minB=min(onlinedisks,key=lambda x:norm(x['size']))
   if norm(minB['size']) > norm(diskA['size']):
    print('spare2_6')
    w=1000000
    return w
   print('spare2_7')
   raidhosts[diskA['host']]+=1
   raidhosts[diskB['host']]-=1
   if 'raidz' in diskB['raid']:
    print('spare2_8')
    sizediff=norm(diskA['size'])-norm(diskB['size']) 
    if diskA['host']==diskB['host'] and norm(diskA['size']) >= norm(diskB['size']) :
     print('spare2_9')
     w=2200000
     return w
   if 'raidz1' in diskB['raid']:
    print('spare2_10')
    if raidhosts[diskA['host']] > 1:
     print('spare2_11')
     w=2000000
     return w
    elif raidhosts[diskA['host']]==1 and raidhosts[diskB['host']]<1:
     print('spare2_12')
     w=2100000
     return w
    elif raidhosts[diskA['host']]<=1 and raidhosts[diskB['host']] >=raidhosts[diskA['host']]:
     print('spare2_13')
     w+=sizediff+10*int(raidhosts[diskA['host']]-raidhosts[diskB['host']])
     return w
    else:
      print('spare2_14')
      print('Error',raidhosts)

   elif 'raidz2' in diskB['raid']:
    print('spare2_15')
    if raidhosts[diskA['host']] > 2:
     print('spare2_16')
     w=2000000
     return w
    elif raidhosts[diskA['host']]==2 and raidhosts[diskB['host']]<2:
     print('spare2_17')
     w=2100000
     return w
    elif raidhosts[diskA['host']]==1 and raidhosts[diskB['host']]<0:
     print('spare2_18')
     w=2200000
     return w
    elif raidhosts[diskA['host']]<=2 and raidhosts[diskB['host']] >=raidhosts[diskA['host']]:
     print('spare2_19')
     w+=sizediff+10*int(raidhosts[diskA['host']]-raidhosts[diskB['host']])
     return w
    else:
      print('spare2_20')
      print('Error',raidhosts)
    
 ########### Mirror and DiskB online diskA free policy: Availability #########
   elif 'mirror' in diskB['raid']:
    print('spare2_21')
    if raidhosts[diskA['host']]==2:
     w=3100000
     return w
    print('spare2_22')
    sizediff=norm(diskA['size'])-norm(diskB['size']) 
    if sizediff >= 0 and hostcounts[diskB['host']]==1:
     print('spare2_23')
     w=3200000
     return w
    print('spare2_24')
    w+=sizediff+10*int(diskA['host'] in diskB['host'])
    return w
########### RAID and DiskB online diskA in Raid policy: Any #########
 elif diskB['raid'] in diskA['raid'] and 'ONLINE' in diskB['status']:  
  print('spare3')
  sizediff=norm(diskA['size'])-norm(diskB['size']) 
 ########### Mirror and DiskB online diskA in Raid policy: Useability #########
  if 'useable' in balancetype:  # tendency not to take the large size
   print('spare3_1')
   if 'mirror' in diskB['raid']:
    print('spare3_2')
    w+=10*sizediff+int(diskA['host'] in diskB['host'])
    return w
 ########### RAID and DiskB online diskA in Raid policy: Availability ########
  else:
   print('spare3_3')
   if 'raidz' in diskB['raid']:
    w=3000000
    return w
   elif 'mirror' in diskB['raid']:
    print('spare3_4')
    w=3000000
    #w+=sizediff+10*int(diskA['host'] in diskB['host'])
    return w 
########### RAID DiskB Failed diskA free policy: Any ########
 elif 'free' in diskA['changeop'] and 'ONLINE' not in diskB['status']:
  print('spare4')
  minB=min(onlinedisks,key=lambda x:norm(x['size']))
  sizediff=norm(diskA['size'])-norm(minB['size']) 
  minB=min(onlinedisks,key=lambda x:norm(x['size']))
########### RAIDZ DiskB Failed diskA free policy: Any ########
  if 'raidz' in diskB['raid']:
   print('spare4_1')
   try:
    print('spare4_2')
    raidhosts[diskA['host']]+=1
   except:
    print('spare4_3')
    raidhosts[diskA['host']]=1
   print('spare4_4')
   minB=min(onlinedisks,key=lambda x:norm(x['size']))
   if norm(minB['size']) > norm(diskA['size']):
    print('spare4_5')
    w=1000000
    return w
   print('spare4_6')
   sizediff=norm(diskA['size'])-norm(diskB['size']) 
 ########### RAID DiskB Failed diskA free policy: Useability ########
  if 'useable' in balancetype:
   print('spare4_7')
   if 'raidz1' in diskB['raid']:
    print('spare4_8')
    w+=10*sizediff+int(raidhosts[diskA['host']]-1)
    return w
   elif 'raidz2' in diskB['raid']:
    print('spare4_9')
    w+=10*sizediff+int(raidhosts[diskA['host']]-2)
    return w
 ########### Mirror DiskB Failed diskA free policy: Useability ########
   elif 'mirror' in diskB['raid']:    # useable type not to mirror large disks
    print('spare4_10')
    if norm(diskA['size']) > norm(minB['size']):
     w=100002
     return w
   else:
    print('spare4_11')
    w+=sizediff+10*int(diskA['host'] in diskB['host'])
    return w
 ########### RAID DiskB Failed diskA free policy: Availability ########
  else:
   print('spare4_12')
 ########### Raidz and DiskB Failed diskA free policy: Availability #########
   if 'raidz1' in diskB['raid']:
    print('spare4_13')
    w=sizediff+10*int(raidhosts[diskA['host']]-1)
    return w
   elif 'raidz2' in diskB['raid']:
    print('spare4_14')
    w=sizediff+10*int(raidhosts[diskA['host']]-2)
    return w
   elif 'raidz3' in diskB['raid']:
    print('spare4_15')
    w=sizediff+10*int(raidhosts[diskA['host']]-3)
    return w
 ########### Mirror and DiskB Failed diskA free policy: Availability #########
   elif 'mirror' in diskB['raid']:
    print('spare4_16')
    w+=sizediff+10*int(raidhosts[diskA['host']] -1)
    return w
  
def selectthedisk(freedisks,raid,allraids,allhosts,myhost):
 weights=[]
 finalw=[]
 hostcounts=allhosts.copy()
 balancetype=get('balancetype/'+raid['pool'])
 for disk in raid['disklist']:
  if 'ONLINE' in disk['status']:
   if disk['host'] in hostcounts.keys():
    hostcounts[disk['host']]+=1
   else:
    hostcounts[disk['host']]=1
 if 'stripe' not in raid['name'] and 'ONLINE' in raid['status']:
  for diskA in raid['disklist']:
   for diskB in raid['disklist']:
    if diskA['actualdisk'] not in diskB['actualdisk']:
     w=getbalance(diskA.copy(),diskB.copy(),balancetype,hostcounts.copy(),raid['disklist'].copy())
     finalw.append({'newd':diskA,'oldd':diskB,'w':w})
  for diskA in freedisks:
   for diskB in raid['disklist']:
    if diskA['actualdisk'] not in diskB['actualdisk']:
     w=getbalance(diskA,diskB,balancetype,hostcounts,raid['disklist'])
     finalw.append({'newd':diskA,'oldd':diskB,'w':w})
 elif 'stripe' in raid['name']:
  for diskA in freedisks:
   for diskB in raid['disklist']: 
    w=getbalance(diskA,diskB,balancetype,hostcounts)
    finalw.append({'newd':diskA,'oldd':diskB,'w':w})
 elif 'DEGRAD' in raid['status']:
  defdisks=[x for x in raid['disklist'] if 'ONLINE' not in x['status']]
  onlinedisks=[x for x in raid['disklist'] if 'ONLINE' in x['status']]
  for diskA in freedisks:
   for diskB in defdisks:
    #####################################################
    #I need to check why we are comparing a faulty disk instead of the others
    ######################################################
    w=getbalance(diskA,diskB,balancetype,hostcounts,onlinedisks)
    finalw.append({'newd':diskA,'oldd':diskB,'w':w})
 finalw=sorted(finalw,key=lambda x:x['w'])
 print('finalw',finalw[0])
 exit()
 return finalw[0] 

def solvedegradedraids(degradedraids, freedisks,allraids,allhosts,myhost):
 global usedfree
 sparefit={}
 for disk in freedisks:
  sparefit[disk['actualdisk']]=[]
  sparefit[disk['actualdisk']].append({'newd':disk['actualdisk'],'oldd':disk['actualdisk'],'w':100000000})
 for raid in degradedraids:
  sparelist=selectthedisk(freedisks,raid,allraids,allhosts,myhost)
  print('sparelist',sparelist)
  if len(sparelist) > 0:
   sparefit[sparelist['newd']['actualdisk']].append(sparelist)
 for k in sparefit:
  sparefit[k]=sorted(sparefit[k],key=lambda x:x['w'])
 for k in sparefit:
  if sparefit[k][0]['w'] > 100000:
   continue 
  oldd=sparefit[k][0]['oldd'] 
  newd=sparefit[k][0]['newd'] 
  olddpool=sparefit[k][0]['oldd']['pool'] 
  if 'raid' in oldd['raid']:
   cmdline=['/sbin/zpool', 'replace', '-f',olddpool]
   ret=mustattach(cmdline,newd,oldd,myhost)
  elif 'mirror' in oldd['raid']:
   cmd=['/sbin/zpool', 'detach', olddpool,oldd['actualdisk']]
   subprocess.check_call(cmd)
   cmdline=['/sbin/zpool', 'attach','-f', olddpool]
   ret=mustattach(cmdline,newd,oldd,myhost)
   if 'fault' not in ret and 'wait' not in ret:
    usedfree.append(ret)
 
def solveonlineraids(onlineraids,freedisks,allraids,allhosts,myhost):
 global usedfree
 sparefit={}
 for disk in freedisks:
  sparefit[disk['actualdisk']]=[]
 for raid in onlineraids:
  sparelist=selectthedisk(freedisks.copy(),raid.copy(),allraids.copy(),allhosts.copy(),myhost)
  if len(sparelist) > 0:
   if sparelist['newd']['actualdisk'] not in sparefit.keys():
    continue 
   else:
    sparefit[sparelist['newd']['actualdisk']].append(sparelist)
 for k in sparefit:
  sparefit[k]=sorted(sparefit[k],key=lambda x:x['w'])
 for k in sparefit:
  if len(sparefit[k]) < 1:
   continue 
  if sparefit[k][0]['w'] > 100000:
   continue 
  oldd=sparefit[k][0]['oldd'] 
  newd=sparefit[k][0]['newd'] 
  olddpool=sparefit[k][0]['oldd']['pool'] 
  if 'raid' in oldd['raid']:
   cmdline=['/sbin/zpool', 'replace', '-f',olddpool]
   ret=mustattach(cmdline,newd,oldd,myhost)
  elif 'mirror' in oldd['raid']:
   cmd=['/sbin/zpool', 'detach', olddpool,oldd['actualdisk']]
   subprocess.check_call(cmd)
   cmdline=['/sbin/zpool', 'attach','-f', olddpool]
   ret=mustattach(cmdline,newd,oldd,myhost)
   if 'fault' not in ret and 'wait' not in ret:
    usedfree.append(ret)
 
def solvestriperaids(striperaids,freedisks,allraids,myhost):
 global usedfree
 sparefit={}
 for raid in striperaids:
  sparelist=selectthedisk(freedisks,raid,allraids,{},myhost)
  if len(sparelist) > 0:
   try:
    sparefit[sparelist['newd']['actualdisk']].append(sparelist)
   except:
    sparefit[sparelist['newd']['actualdisk']]=[]
    sparefit[sparelist['newd']['actualdisk']].append(sparelist)
 for k in sparefit:
  sparefit[k]=sorted(sparefit[k],key=lambda x:x['w'])
 for k in sparefit:
  oldd=sparefit[k][0]['oldd'] 
  newd=sparefit[k][0]['newd'] 
  olddpool=sparefit[k][0]['oldd']['pool'] 
 cmdline=['/sbin/zpool', 'attach','-f', olddpool]
 ret=mustattach(cmdline,newd,oldd,myhost)
 if 'fault' not in ret:
  usedfree.append(ret)
 return
 
def solvedegradedraid(raid,disksfree):
 hosts=get('ready','--prefix')
 hosts=[host[0].split('/')[1] for host in hosts]
 raidhosts= set()
 defdisk = [] 
 disksample = ''
 sparedisk = []
 for disk in raid['disklist']:
  if 'ONLINE' in disk['changeop']:
   disksample=disk.copy()
   raidhosts.add(disk['host'])
  else:
   defdisk.append(disk['name'])
   cmddm= ['/pace/mkdm.sh', raid['name'], myhost ]
   subprocess.run(cmddm,stdout=subprocess.PIPE)
 
 if len(disksample) == 0 :
  return
 if len(defdisk):
  print('no def disk')
  return
################## put a wrapping condition after the next "for" line for every new feature (disk type, node load, AI analysis,..etc ##########
 for disk in disksfree:
  if levelthis(disk['size']) < levelthis(disksample['size']):
   continue
  if disk['host'] not in raidhosts:
   sparedisk.append([disk,10])
  else:
   sparedisk.append([disk,0])
  if levelthis(disk['size']) ==  levelthis(disksample['size']):
   sparedisk[-1] = [disk,sparedisk[-1][1]+10]
 if len(sparedisk) == 0:
  return
 print('##############################################') 
 print('sparedisk',sparedisk)  
 print('##############################################') 
 sparedisk = max(sparedisk,key=lambda x:x[1])[0]
 print('sparedisk',sparedisk)  
 print('##############################################') 
 cmdline=['/sbin/zpool', 'replace', '-f',raid['pool']]
 ret=mustattach(cmdline,sparedisk,defdisk,myhost)
   
  
def spare2(*args):
 global newop
 global usedfree 
 freedisks=[]
 allraids=[]
 freeraids=[]
 myhost=args[0]
 hosts=get('ready','--prefix')
 allhosts={}
 for host in hosts:
  allhosts[host[0].replace('ready/','')]=0
 newop=getall(myhost)
 striperaids=[]
 if newop==[-1]:
  return
 availability = get('balance','--prefix')
 degradedpools=[x for x in newop['pools'] if myhost in x['host'] and  'DEGRADED' in x['status']]
 for spool in newop['pools']:
  for sraid in spool['raidlist']:
   if len(availability) > 0:
    if 'ree' not in sraid['name'] and spool['name'] in str(availability):
     allraids.append(sraid)
   else:
    if 'ree' not in sraid['name']:
     allraids.append(sraid)
 print(allraids)
 striperaids=[x for x in allraids if 'stripe' in x['name']]
 onlineraids=[x for x in allraids if 'ONLINE' in x['changeop']]
 degradedraids=[x for x in allraids if 'DEGRADE' in x['status']]
 print('degraded',degradedraids)
 for raid in degradedraids:
  for disk in raid['disklist']:
   if 'ONLINE' not in disk['changeop']:
     cmdline2=['/sbin/zpool', 'detach', disk['pool'],disk['actualdisk']]
     subprocess.run(cmdline2,stdout=subprocess.PIPE)
     dels('disk',disk['actualdisk'])
 onlinedisks=get('disks','ONLINE')    
 errordisks=get('errdiskpool','--prefix')
 freedisks=[ x for x in newop['disks']  if 'free' in x['raid'] or (x['name'] in str(onlinedisks) and 'OFFLINED' not in x['status'] and 'ONLINE' not in x['changeop']) ]  
   
 ###################### return back a readded disk in the same slot ########################
 onlined = 0
 for disk in freedisks:
  if 'free' not in disk['pool'] and disk['name']+'/'+disk['pool'] not in str(errordisks):
   cmdline2=['/sbin/zpool', 'online', disk['pool'],disk['name']]
   onlinethis = subprocess.run(cmdline2,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   #print('the error is', onlinethis.stderr.decode(), onlinethis.returncode) 
   if onlinethis.returncode != 0:
    put('errdiskpool/'+disk['name']+'/'+disk['pool'], 'true')
   else:
    dels('errdiskpool/'+disk['name']+'/'+disk['pool'])
   
   put('disks/'+disk['name'],'transition1')
   onlined = 1
 if onlined == 1:
  return
 for disk in freedisks:
  if disk['changeop'] not in 'ONLINE' :
   diskinfo = diskdata(disk['name'])
   disk['actualdisk'] = diskinfo['actualdisk']
   disk['id'] = diskinfo['id']
   disk['host'] = diskinfo['host'] 
   disk['size'] = diskinfo['size'] 
   disk['devname'] = diskinfo['devname']

   
 #############################################################################################
 print('####################')
 print('freedisksprint', freedisks)
 print('####################')
 disksfree=[x for x in freedisks if x['actualdisk'] not in str(usedfree)]
 if len(disksfree) > 0 and len(degradedraids) > 0 : 
  print('degradedraids',degradedraids)
  print('disksfree',disksfree)
 for raid in degradedraids:
  disksfree = solvedegradedraid(raid, disksfree)
  #solvedegradedraids(degradedraids, disksfree,allraids,allhosts,myhost)
 exit()
 if len(disksfree) > 0 and len(striperaids) > 0 : 
  solvestriperaids(striperaids, disksfree,allraids,myhost)
 disksfree=[x for x in freedisks if x['actualdisk'] not in str(usedfree)]
 if len(disksfree) > 0 and len(onlineraids) > 0 : 
  solveonlineraids(onlineraids, disksfree,allraids,allhosts,myhost)
 return
 
 
if __name__=='__main__':
 with open('/pacedata/perfmon','r') as f:
  perfmon = f.readline() 
 if '1' in perfmon:
  queuethis('selectspare.py','start','system')
 if len(sys.argv)< 2:
  sys.argv.append(hostname())
 spare2(*sys.argv[1:])
 if '1' in perfmon:
  queuethis('selectspare.py','stop','system')
