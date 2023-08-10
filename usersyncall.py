#!/usr/bin/python3
import subprocess,sys
from etcdgetpy import etcdget as get
from etcdput import etcdput as put
from ast import literal_eval as mtuple

leader, leaderip, myhost, myhostip = '','','',''
def usrfninit(ldr,ldrip,hst,hstip):
 global allusers, leader ,leaderip, myhost, myhostip
 leader, leaderip, myhost, myhostip = ldr, ldrip, hst, hstip
 return
allusers = []

def thread_add(user,tosync):
 global myusers
 global allusers, leader ,leaderip, myhost, myhostip
 username=user[0].replace(tosync+'usersinfo/','')
 if 'NoUser' == username:
  return
 with open('/root/usersync2','w') as f:
  f.write(str(user)+' + '+str(username)+'\n')
 userhash=get(leaderip,tosync+'usershash/'+username)[0]
 userinfo=user[1].split(':')
 userid=userinfo[0]
 usergd=userinfo[1]
 userhome=userinfo[2]
 cmdline=['/TopStor/UnixAddUser_sync',leader, leaderip, myhost, myhostip, username,userhash,userid,usergd,userhome]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)

def thread_del(user,pullsync='normal'):
 global allusers, leader ,leaderip, myhost, myhostip
 global allusers
 username=user[0].replace('usersinfo/','')
 if 'admin' == username or 'NoUser' == username:
  return
 if username not in str(allusers):
  print(username,str(allusers))
  cmdline=['/TopStor/UnixDelUser',leaderip, username,'system',pullsync]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)

def usersyncall(tosync=''):
 global allusers, leader ,leaderip, myhost, myhostip
 global allusers
 global myusers
 allusers=get(leaderip,tosync+'usersinfo','--prefix')
 if 'pullsync' in tosync:
    syncip = leaderip
 else:
    syncip = myhostip
 myusers=get(syncip,'usersinfo','--prefix')
 myusers = [ x for x in musers if 'admin' ==  x[0].split('/')[-1] ]
 print(';;;;;;;;;;;;;;;;',myusers)
 threads=[]
 if '_1' in allusers:
  allusers=[]
 if '_1' in myusers:
  myusers=[]
 for user in allusers:
  thread_add(user,tosync)
 leader=get(leaderip,'leader','--prefix')
 if myhost not in str(leader) or 'pullsync' in tosync:
  for user in myusers:
   if user in allusers:
    print(user,allusers)
   else:
    if 'admin' not in str(user):
     thread_del(user,tosync)

def oneusersync(oper,usertosync):
 global allusers, leader ,leaderip, myhost, myhostip
 global allusers
 global myusers
 print('args',oper,usertosync)
 myusers=get(myhostip,'usersinfo','--prefix')
 user=get(leaderip,'usersinfo', usertosync)[0]
 if user == '_1':
  return
 if oper == 'Add':
  thread_add(user)
 else:
  if 'admin' not in str(user):
   thread_del(user)
 
  
if __name__=='__main__':
 cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py leader'
 leader=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
 cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py leaderip'
 leaderip=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
 cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py clusternode'
 myhost=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
 cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py clusternodeip'
 myhostip=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
 if len(sys.argv[1:]) < 2:
    print(' syncing all users')
    usersyncall(*sys.argv[1:])
 else:
    oneusersync(*sys.argv[1:])
