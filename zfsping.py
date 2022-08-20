#!/bin/python3.6
from checkleader import checkleader
from remknown import remknown
import subprocess,sys, logmsg
from logqueue import queuethis
from etcddel import etcddel as etcddel
from etcdgetpy import etcdget as get
from etcdgetlocalpy import etcdget as getlocal
from time import time as stamp
from time import sleep
from etcdput import etcdput as put 
from socket import gethostname as hostname
from addknown import addknown
from putzpool import putzpool
from etcdputlocal import etcdput as putlocal 
from activeusers import activeusers
from addactive import addactive
from selectimport import selectimport
from multiprocessing import Process

myhost = hostname()
leader = checkleader('leader','--prefix').stdout.decode('utf-8').split('\n')
leadern = leader[0].split('/')[1]
leaderip = leader[1]
 


def iscsiwatchdogproc():
  cmdline='/pace/iscsiwatchdoglooper.sh'
  result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')

def fapiproc():
  cmdline='/pace/fapilooper.sh' 
  result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')

def putzpoolproc():
  global leader, myhost
  putzpool(leader,myhost)
  sleep(5)

def addactive():
  global leader, myhost
  addactive(leader,myhost)
  sleep(5)

def selectimportproc():
  global leader, myhost
  allpools=get('pools/','--prefix')
  selectimport(myhost,allpools,leader)
  sleep(5)

def infinitproc():
 global leader, myhost
 while True:
  leader = checkleader('leader','--prefix').stdout.decode('utf-8').split('\n')
  leadern = leader[0].split('/')[1]
  leaderip = leader[1]
  print('start remknown')
  remknown(leadern,myhost) 
  print('finish remknown')
  if myhost == leadern:
   addknown(leader,myhost)
  activeusers(leader, myhost)

loopers = [ infinitproc, iscsiwatchdogproc, fapiproc, putzpoolproc, addactive, selectimport ]

if __name__=='__main__':
 fapi = Process(target=fapiproc)
 looper = Process(target=infinitproc)
 fapi.start()
 looper.start()
 fapi.join()
 looper.join()
