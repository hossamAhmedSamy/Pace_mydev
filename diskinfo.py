#!/usr/bin/python3
import sys,subprocess
import json

cmdline=['/pace/etcdgets.py',sys.argv[1],'--prefix']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
data=json.loads('{'+str(result.stdout)[2:][:-3].replace('\\','').replace("',","':").replace('[','').replace(']','').replace('"','').replace("'",'"')+'}');
if sys.argv[2] in 'getkey':
 for x in data:
  if sys.argv[3] in data[x]:
   print(x)
else:
 for x in data:
  if sys.argv[3] in x:
   print(data[x])

