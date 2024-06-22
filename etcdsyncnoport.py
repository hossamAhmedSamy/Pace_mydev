#!/usr/bin/python3
import sys
from etcdgetpy import etcdget as get
from etcdgetnoportpy import etcdget as getnoport
from etcdputnoport import etcdput as putnoport
from etcdput import etcdput as put 
from etcddel import etcddel as dels 

def synckeysnoport(fromhost, pport, tohost, fromkey, tokey):
 fromlist=get(fromhost, noport, fromkey,'--prefix')
 dels(tohost,tokey,'--prefix')
 if '_1' in fromlist:
  exit()
 for item in fromlist:
  lefti = item[0].replace(fromkey,tokey)
  righti = item[1]
  putnoport(fromhost, noport, tohost, lefti, righti)

if __name__=='__main__':
 synckeysnoport(*sys.argv[1:])
