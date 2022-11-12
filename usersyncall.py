#!/bin/python3.6
import subprocess,sys
from etcdgetpy import etcdget as get
from etcdput import etcdput as put
from broadcasttolocal import broadcasttolocal
from ast import literal_eval as mtuple
from socket import gethostname as hostname

myip = '0'

allusers = []
def thread_add(leader, myip, user):
 global myusers
 username=user[0].replace('usersinfo/','')
 if 'NoUser' == username:
  return
 with open('/root/usersync2','w') as f:
  f.write(str(user)+' + '+str(username)+'\n')
 if username in str(myusers):
  userhashlocal=get(myip,'usershash/'+username)[0]
  userhash=get(leader,'usershash/'+username)[0]
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
  userhash=get(leader,'usershash/'+username)[0]
  userhome=userinfo[2]
  cmdline=['/TopStor/UnixAddUser_sync',username,userhash,userid,usergd,userhome]
  with open('/root/tmpusersync','w') as f:
   f.write('user: '+str(userhash))
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)

def thread_del(leader,myip, *user):
 global allusers
 username=user[0].replace('usersinfo/','')
 if 'NoUser' == username:
  return
 if username not in str(allusers):
  print(username,str(allusers))
  cmdline=['/TopStor/UnixDelUser_sync',username,'system']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)

def usersyncall(leader, hostip,tosync='usersinfo'):
 global allusers
 global myusers
 global myip 
 myip = hostip
 allusers=get(leader,'usersinfo','--prefix')
 myusers=get(myip,'usersinfo','--prefix')
 print(';;;;;;;;;;;;;;;;',myusers)
 if tosync != 'usersinfo': 
  users=get(leader,'modified','user')
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
  thread_add(leader,myip, user)
 leader=get(leader,'leader','--prefix')
 if myhost not in str(leader):
  for user in myusers:
   if user in allusers:
    print(user,allusers)
   else:
    thread_del(leader,myip, user)
 if tosync != 'usersinfo': 
  for user in users:
   gethosts = get(leader,'modified/user/'+user)[0]
   if myhost not in gethosts:
    put(leader,'modified/user/'+user,gethosts+'/'+myhost)
  #  broadcasttolocal('modified/user/'+user,gethosts+'/'+myhost)

def oneusersync(leader, oper,usertosync):
 global allusers
 global myusers
 global myip
 print('args',oper,usertosync)
 myusers=get(myip,'usersinfo','--prefix')
 user=get(leader,'usersinfo', usertosync)[0]
 if user == -1:
  return
 if oper == 'Add':
  thread_add(leader,myip, user)
 else:
  thread_del(leader,myip, user)
 
  
if __name__=='__main__':
# usersyncall(*sys.argv[1:])
 oneusersync(*sys.argv[1:])
