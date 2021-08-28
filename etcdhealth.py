#!/bin/python3.6
import subprocess,sys
import json

endpoints=''
data=json.load(open('/pacedata/runningetcdnodes.txt'));
for x in data['members']:
 endpoints=endpoints+str(x['clientURLs'])[2:][:-2]
cmdline=['etcdctl','--user=root:YN-Password_123','--endpoints='+endpoints,'endpoint','health']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
print('result',result.stdout)
# cmdline=['etcdctl','-w','json','--endpoints='+host['addresses']['ipv4']+':2379','member','list','2>/dev/null']

