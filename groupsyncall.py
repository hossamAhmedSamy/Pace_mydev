#!/usr/bin/python3
import subprocess,sys
from etcdgetpy import etcdget as get
from etcdput import etcdput as put
from ast import literal_eval as mtuple
from socket import gethostname as hostname

allusers= []
leader, leaderip, myhost, myhostip = '','','',''
def grpfninit(ldr,ldrip,hst,hstip):
 global allusers, leader ,leaderip, myhost, myhostip
 leader, leaderip, myhost, myhostip = ldr, ldrip, hst, hstip 
 return
#def thread_add(*user):

def thread_add(user):
 global allusers, leader ,leaderip, myhost, myhostip
 username=user[0].replace('usersigroup/','')
 if 'Everyone' == username:
  return
 groupusers=user[1].split('/')[2]
 if groupusers=='no':
  groupusers='users'
 else:
  groupusers='users'+groupusers
 with open('/root/sync2','a') as f:
  f.write(str(user)+' + '+str(username)+', groupusers:'+groupusers+'\n')
 userigroup=user[1].split(':')
 userid=userigroup[0]
 usergd=userigroup[1]
 cmdline=['/TopStor/UnixAddGroup_sync',username,userid,usergd,groupusers]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)

#def thread_del(*user):
def thread_del(user):
 global allusers, leader ,leaderip, myhost, myhostip
 username=user[0].replace('usersigroup/','')
 if 'Everyone' == username:
  return
 if username not in str(allusers):
  print(username,str(allusers))
  cmdline=['/TopStor/UnixDelGroup_sync',username,'system']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)

def groupsyncall(tosync='usrsigroup'):
 global allusers, leader ,leaderip, myhost, myhostip
 global myusers
 allusers=get(leaderip, 'usersigroup','--prefix')
 myusers=get(myhostip,'usersigroup','--prefix')
 if tosync != 'usrsigroup':
  groups = get(leaderip, 'modified','group')
  if '_1' in groups:
   print('groups',groups)
   return
  groups = [ x[0].split('/')[2] for x in groups if myhost not in str(x) ]
  allusers = [ x for x in allusers if x[0].replace('usersigroup/','') ]
  delgroups = []
  if myhost != leader:
   for group in groups:
    if group not in allusers:
     delgroups.append(group)
  myusers= [ x for x in myusers if x[0].replace('usersinfo/','') in delgroups ]
 print(';;;;;',myusers,allusers)
 threads=[]
 if '_1' in allusers:
  allusers=[]
 if '_1' in myusers:
  myusers=[]
 for user in myusers:
  if user in allusers:
   print(user,allusers)
  else:
   thread_del(user)

 for user in allusers:
  thread_add(user)
 if tosync != 'usrsigroup': 
  for group in groups:
   gethosts = get(leaderip, 'modified/group/'+group)[0]
   if myhost not in gethosts:
    put(leaderip, 'modified/group/'+group,gethosts+'/'+myhost)
 
 # thread_add(user)
#x=Thread(target=thread_add,name='addingusers',args=user)
#  x.start()
#  threads.append(x) 
#   x=Thread(target=thread_del,name='deletingusers',args=user)
#   x.start()
#   threads.append(x) 
# for tt in threads:
#  tt.join()
   
def onegroupsync(oper,usertosync):
 global allusers, leader ,leaderip, myhost, myhostip
 global myusers
 user=get(leaderip,'usersigroup', usertosync)[0]
 print('user',user)
 if oper == 'Add':
  thread_add(user)
 else:
  thread_del(user)
 
  
if __name__=='__main__':
 with open('/root/sync2','w') as f:
  f.write('Starting\n')

 cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py leader'
 leader=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
 cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py leaderip'
 leaderip=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
 cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py clusternode'
 myhost=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
 cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py clusternodeip'
 myhostip=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
 onegroupsync(*sys.argv[1:])
