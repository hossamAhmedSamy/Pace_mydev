#!/usr/bin/python3
import subprocess,sys, os
from etcdgetpy import etcdget as get
from etcdput import etcdput as put 
#from broadcasttolocal import broadcasttolocal 
from time import time as stamp


#leader=get('leader','--prefix')[0][0].split('/')[1]

def dosync(*args):
  global leaderip, leader
  put(leaderip, *args)
  put(leaderip, args[0]+'/'+leader,args[1])
  return 

def getippos(vtype):
    if ('cifs' or 'home') in vtype:
        return 7
    else: 
        return 0
def getdirtyvols(vtype, etcds, replis, dockers):
    global leader, leaderip, myhost, myhostip, etcdip
    cmdline = '/TopStor/getvols.sh '+vtype
    result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
    result = [x for x in result if 'pdhc' in x]
    resultdisabled = [ x for x in result if 'disable' in str(x) ]
    resultactive = [ x for x in result if 'active' in str(x) ]
    etcddisabled= [ x for x in etcds if 'disable' in str(x) ]
    etcdactive= [ x for x in etcds if 'active' in str(x) ]
    dirtyset = set()
    ipset = set()
    print('###############3')
    for res in result:
        reslist=res.split('/')
        ippos = getippos(vtype)
        if reslist[-1] == 'active':
            if reslist[1] in str(etcddisabled):
                dirtyset.add(res)
        else:
            if reslist[1] in str(etcdactive):
                dirtyset.add(res)
        if reslist[1] not in str(etcds):
            dirtyset.add(res)
        for dckr in dockers.split('\n'):
            if reslist[7] in dckr and reslist[-1] =='active':
                dckrname=dckr.split(' ')[-1]
                cmdline = 'docker inspect '+dckrname
                result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
                print(dckrname, reslist[1],reslist)
                if reslist[1] not in str(result):
                    print('not in')
                    dirtyset.add(res)
        if reslist[7] not in dockers:
            dirtyset.add(res)
    return dirtyset

    
def cifs( etcds, replis, dockers):
 global leader, leaderip, myhost, myhostip, etcdip
 dirtyset = getdirtyvols('cifs', etcds, replis, dockers)
 print(dirtyset)
 for res in dirtyset:
   reslist=res.split('/')
   print('update',reslist[1])
   cmdline = '/TopStor/undockerthis.sh '+reslist[7]
   result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
   if 'DOMAIN' in str(res):
    left='volumes/CIFS_'+reslist[9]+'/'+myhost+'/'+'/'.join(reslist[0:2])
   else:
    left='volumes/CIFS/'+myhost+'/'+'/'.join(reslist[0:2])
   put(leaderip, left,res)
   dosync('sync/volumes/_'+myhost+'/request','volumes_'+str(stamp()))
   #broadcasttolocal(left,res)
   if 'DOMAIN' in str(res):
     #cmdline='/TopStor/cifsmember.sh '+leaderip+' '+reslist[0]+' '+reslist[1]+' '+reslist[7]+' '+reslist[8]+' cifs '+' '.join(reslist[9:])
     cmdline='/TopStor/cifs.py '+leader+' '+leaderip+' '+myhost+' '+myhostip+' '+etcdip+' '+reslist[0]+' '+reslist[1]+' '+reslist[7]+' '+reslist[8]+' CIFS_'+reslist[9]+' '+' '.join(reslist[9:])
     print('cmdline',cmdline)

     #cmdline='/TopStor/VolumeActivateCIFSdom '+leaderip+' vol='+reslist[1]+' user=system'
   else:
     cmdline='/TopStor/cifs.py '+leader+' '+leaderip+' '+myhost+' '+myhostip+' '+etcdip+' '+reslist[0]+' '+reslist[1]+' '+reslist[7]+' '+reslist[8]+' CIFS '+' '.join(reslist[9:])
    #cmdline='/TopStor/VolumeActivateCIFS '+leaderip+' vol='+reslist[1]+' user=system'
   result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
   print(result)
   put(etcdip,'dirty/volume','0')

def homes(etcds, replis, dockers):
  global leader, leaderip, myhost, myhostip, etcdip
  cmdline = '/TopStor/getvols.sh home'
  result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
  result = [x for x in result if 'pdhc' in x]
  print('###############3')
  for res in result:
   reslist=res.split('/')
   if reslist[1] not in str(etcds):
    left='volumes/HOME/'+myhost+'/'+'/'.join(reslist[0:2])
    put(leaderip, left,res)
    dosync('sync/volumes/_'+myhost+'/request','volumes_'+str(stamp()))
    #broadcasttolocal(left,res)
   if reslist[7] not in dockers:
    print(reslist)
    cmdline='/TopStor/cifs.sh '+leader+' '+leaderip+' '+myhost+' '+myhostip+' '+etcdip+' '+reslist[0]+' '+reslist[1]+' '+reslist[7]+' '+reslist[8]+' cifs'
    cmdline='/TopStor/VolumeActivateHome '+leaderip+' vol='+reslist[1]+' user=system'
    print(cmdline)
    result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
    print(result)
    
   
def iscsi(etcds, replis):
 global leader, leaderip, myhost, myhostip, etcdip
 cmdline = 'targetcli ls '
 targets = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8') 
 cmdline = '/TopStor/getvols.sh iscsi'
 result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
 result = [x for x in result if 'pdhc' in x]
 print('###############3')
 for res in result:
  reslist=res.split('/')
  if reslist[1] not in str(etcds):
   left='volumes/ISCSI/'+myhost+'/'+'/'.join(reslist[0:2])
   put(leaderip, left,res)
   dosync('sync/volumes/_'+myhost+'/request','volumes_'+str(stamp()))
   #broadcasttolocal(left,res)
  if reslist[1] not in targets:
   print(reslist)
   #cmdline='/TopStor/iscsi.sh '+leaderip+' '+reslist[0]+' '+reslist[1]+' '+reslist[2]+' '+reslist[3]+' '+ \
   #        reslist[4]+' '+reslist[5]+' '+reslist[6]+' '+reslist[7]
   cmdline='/TopStor/VolumeActivateISCSI '+leaderip+' vol='+reslist[1]+' user=system'
   result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
   print(cmdline)


def volumecheck(etcds, replis, *args):
 global leader, leaderip, myhost, myhostip, etcdip
 if str(etcds)=='init':
     leader = replis 
     leaderip = args[0]
     myhost = args[1]
     myhostip = args[2]
     etcdip = args[3]
     return

 cmdline = 'docker ps'
 dockers = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8') 
 
 cifs(etcds, replis, dockers)
 homes(etcds, replis, dockers)
 iscsi(etcds, replis)
  
   
if __name__=='__main__':
  leaderip = sys.argv[1]
  myhost = sys.argv[2]
  leader=get(leaderip, 'leader')[0]
  myhostip=get(leaderip,'ready/'+myhost)[0] 
  if myhost == leader:
   etcdip = leaderip
  else:
   etcdip = myhostip
   
 
  etcds = get(etcdip, 'volumes','--prefix')
  replis = get(etcdip, 'replivol','--prefix')
  volumecheck(etcds, replis)
