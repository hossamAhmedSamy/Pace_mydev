#!/bin/python3.6
import subprocess,sys, datetime
import json
from etcdget import etcdget as get
from etcdputlocal import etcdput as putlocal 
from etcddellocal import etcddel as deli 

def syncthis(*args):
 knowns=[]
 knowninfo=get('known','--prefix')
 for k in knowninfo:
  deli(k[1],args[0],args[1])
  etcdinfo=get(args[0],args[1])
  for item in etcdinfo:
   putlocal(k[1],item[0],item[1])

if __name__=='__main__':
 syncthis(*sys.argv[1:])
