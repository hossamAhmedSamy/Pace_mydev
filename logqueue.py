#!/usr/bin/python3
import sys, datetime
from time import time
from etcdput import etcdput as put
from etcdgetlocalpy import etcdget as getlocal
from ast import literal_eval as mtuple
from sendhost import sendhost

leaderip = ''
myhost = ''
def initqueue(ldr,host):
    global leaderip, myhost
    leaderip = ldr
    myhost = host


def queuethis(*args):
 global leaderip, myhost
 z=[]
 put(leaderip,'request/'+args[0]+'/'+myhost,args[1])
 dt=datetime.datetime.now().strftime("%m/%d/%Y")
 tm=datetime.datetime.now().strftime("%H:%M:%S")
 z=['/TopStor/logqueue2.sh', dt, tm, myhost ]
 for arg in args:
  z.append(arg)
 z.append(int(time()*1000))
 with open('/root/logqueuetmp','w') as f:
  f.write(str(z))
 msg={'req': 'queue', 'reply':z}
 sendhost(leaderip, str(msg),'recvreply',myhost)
 
if __name__=='__main__':
 #queuethis('ddlrt.py','start','system')
 initqueue(getlocal('leaderip')[0], getlocal('clusternode')[0])
 queuethis(*sys.argv[1:])
