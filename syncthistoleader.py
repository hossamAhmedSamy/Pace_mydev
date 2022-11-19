#!/usr/bin/python3
import subprocess,sys, datetime
import json
from etcdgetlocalpy import etcdget as getlocal
from etcdgetpy import etcdget as get
from etcdput import etcdput as put 
from etcddel import etcddel as deli 

def syncthis(*args):
 leaderip=get('leader','--prefix')[0][1]
 deli(args[1],args[2])
 etcdinfo=getlocal(args[0],args[1],args[2])
 for item in etcdinfo:
   put(item[0],item[1])

if __name__=='__main__':
 syncthis(*sys.argv[1:])
