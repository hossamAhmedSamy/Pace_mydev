#!/bin/python3.6
import subprocess,sys
from etcdget import etcdget as get
from ast import literal_eval as mtuple
from etcdputlocal import etcdput as putlocal 
from etcddellocal import etcddel as dellocal 


thehost=sys.argv[1]
key=sys.argv[2]
tokey=sys.argv[3]
print('thehost',thehost,tokey)
mylist=get(key,'--prefix')
dellocal(thehost,tokey,'--prefix')

print('mylist:',mylist)
if '-1' in mylist:
 print('-1')
 exit()
for item in mylist:
 moditem=""
 restitem=""
 if '/' in item[0]:
  moditem=item[0].split('/')[0]
  restitem='/'+item[0].replace(moditem+'/','')
 putlocal(thehost, tokey+restitem, item[1])
 
