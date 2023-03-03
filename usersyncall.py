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

def thread_add(user):
 global myusers
 global allusers, leader ,leaderip, myhost, myhostip
 username=user[0].replace('usersinfo/','')
 if 'NoUser' == username:
  return
 with open('/root/usersync2','w') as f:
  f.write(str(user)+' + '+str(username)+'\n')
 if username in str(myusers):
  userhashlocal=get(myhostip,'usershash/'+username)[0]
  userhash=get(leaderip,'usershash/'+username)[0]
  if userhashlocal not in userhash:
   userinfo=user[1].split(':')
   userid=userinfo[0]
   usergd=userinfo[1]
   userhome=userinfo[2]
   cmdline=['/TopStor/UnixAddUser_sync',username,userhash,userid,usergd,userhome]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 else:
  userinfo=user[1].split(':')
  userid=userinfo[0]
  usergd=userinfo[1]
  userhash=get(leaderip,'usershash/'+username)[0]
  userhome=userinfo[2]
  cmdline=['/TopStor/UnixAddUser_sync',username,userhash,userid,usergd,userhome]
  with open('/root/tmpusersync','w') as f:
   f.write('user: '+str(userhash))
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)

def thread_del(*user):
 global allusers, leader ,leaderip, myhost, myhostip
 global allusers
 username=user[0].replace('usersinfo/','')
 if 'NoUser' == username:
  return
 if username not in str(allusers):
  print(username,str(allusers))
  cmdline=['/TopStor/UnixDelUser_sync',username,'system']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)

def usersyncall(tosync='usersinfo'):
 global allusers, leader ,leaderip, myhost, myhostip
 global allusers
 global myusers
 allusers=get(leaderip,'usersinfo','--prefix')
 myusers=get(myhostip,'usersinfo','--prefix')
 print(';;;;;;;;;;;;;;;;',myusers)
 if tosync != 'usersinfo': 
  users=get(leaderip,'modified','user')
  users = [ x for x in users if myhost not in str(x) ]
  users = [ x[0].split('/')[2] for x in users ]
  allusers = [ x for x in allusers if x[0].replace('usersinfo/','') in users]
  delusers = []
  for user in users:
   if user not in str(allusers):
    delusers.append(user)
  myusers= [ x for x in myusers if x[0].replace('usersinfo/','') in delusers ]
 threads=[]
 if '-1' in allusers:
  allusers=[]
 if '-1' in myusers:
  myusers=[]
 for user in allusers:
  thread_add(user)
 leader=get(leaderip,'leader','--prefix')
 if myhost not in str(leader):
  for user in myusers:
   if user in allusers:
    print(user,allusers)
   else:
    thread_del(user)
 if tosync != 'usersinfo': 
  for user in users:
   gethosts = get(leaderip,'modified/user/'+user)[0]
   if myhost not in gethosts:
    put(leaderip,'modified/user/'+user,gethosts+'/'+myhost)
  #  broadcasttolocal('modified/user/'+user,gethosts+'/'+myhost)

def oneusersync(oper,usertosync):
 global allusers, leader ,leaderip, myhost, myhostip
 global allusers
 global myusers
 print('args',oper,usertosync)
 myusers=get(myhostip,'usersinfo','--prefix')
 user=get(leaderip,'usersinfo', usertosync)[0]
 if user == -1:
  return
 if oper == 'Add':
  thread_add(user)
 else:
  thread_del(user)
 
  
if __name__=='__main__':
# usersyncall(*sys.argv[1:])
 oneusersync(*sys.argv[1:])
