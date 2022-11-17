#!/usr/bin/python3
import subprocess,sys, os
from etcdgetlocal import etcdgetlocal as get
from etcdput import etcdput as put 

def broadcasttolocal(*args):
 os.environ['ETCDCTL_API']= '3'
 knowns=[]
 knowninfo=get('known','--prefix')
 for k in knowninfo:
  put(k[1],args[0],args[1])

if __name__=='__main__':
 broadcasttolocal(*sys.argv[1:])
