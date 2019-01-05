#!/bin/python3.6
import subprocess,sys, datetime
import json
from etcdget import etcdget as get
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from etcddellocal import etcddel as dellocal 

def delbroadcastlocal(*args):
 knowns=[]
 knowninfo=get('known','--prefix')
 for k in knowninfo:
  dellocal(k[1],args[0],args[1])

if __name__=='__main__':
 delbroadcastlocal(*sys.argv[1:])
