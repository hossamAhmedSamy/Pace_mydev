#!/bin/python3.6
import subprocess,sys
from etcdget import etcdget as get
from threading import Thread
from etcdgetlocal import etcdget as getlocal
from ast import literal_eval as mtuple
from socket import gethostname as hostname

myip=sys.argv[1]
allusers=get('usersinfo','--prefix')
myusers=getlocal(myip,'usersinfo','--prefix')

def thread_add(*user):
 username=user[0].replace('usersinfo/','')
 if username in str(myusers):
  userhashlocal=getlocal(myip,'usershash/'+username)[0]
  userhash=get('usershash/'+username)[0]
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
  userhash=get('usershash/'+username)[0]
  userhome=userinfo[2]
  cmdline=['/TopStor/UnixAddUser_sync',username,userhash,userid,usergd,userhome]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)

def thread_del(*user):
 username=user[0].replace('usersinfo/','')
 if username not in str(allusers):
  print(username,str(allusers))
  cmdline=['/TopStor/UnixDelUser_sync',username,'system']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)

def usersyncall(*args):
 global allusers
 global myusers
 global myip 
 threads=[]
 if '-1' in allusers:
  allusers=[]
 if '-1' in myusers:
  myusers=[]
 for user in allusers:
 # thread_add(user)
  x=Thread(target=thread_add,name='addingusers',args=user)
  x.start()
  threads.append(x) 
 for user in myusers:
  if user in allusers:
   print(user,allusers)
  else:
 #  thread_del(user)
   x=Thread(target=thread_del,name='deletingusers',args=user)
   x.start()
   threads.append(x) 
 for tt in threads:
  tt.join()
   
  
if __name__=='__main__':
 usersyncall(*sys.argv[1:])
