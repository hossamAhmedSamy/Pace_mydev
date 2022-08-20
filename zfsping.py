#!/bin/python3.6
from checkleader import checkleader
from remknown import remknown
import subprocess,sys, logmsg
from logqueue import queuethis
from etcddel import etcddel as etcddel
from etcdgetpy import etcdget as get
from etcdgetlocalpy import etcdget as getlocal
from time import time as stamp
from etcdput import etcdput as put 
from socket import gethostname as hostname
from addknown import addknown
from putzpool import putzpool
from etcdputlocal import etcdput as putlocal 




myhost = hostname()
while True:
 leader = checkleader('leader','--prefix').stdout.decode('utf-8').split('\n')
 leadern = leader[0].split('/')[1]
 leaderip = leader[1]
 print('start remknown')
 remknown(leadern,myhost) 
 print('finish remknown')
 if myhost == leadern:
  addknown(leader,myhost)
 putzpool(leader,myhost)
