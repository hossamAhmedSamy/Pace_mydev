#!/usr/bin/python3
import sys
from etcdgetpy import etcdget as get
from etcdput import etcdput as put 
from etcddel import etcddel as dels 

def synckeys(fromhost, tohost, fromkey, tokey):
 fromlist=get(fromhost,fromkey,'--prefix')
 dels(tohost,tokey,'--prefix')
 if '-1' in fromlist:
  exit()
 for item in fromlist:
  lefti = item[0].replace(fromkey,tokey)
  righti = item[1]
  put(tohost, lefti, righti)

if __name__=='__main__':
 synckeys(*sys.argv[1:])
