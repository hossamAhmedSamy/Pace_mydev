#!/bin/python3.6
import subprocess,sys, os
import json
def etcdcmd(cmd,*args):
 os.environ['ETCDCTL_API']= '3'
 endpoints=''
 data=json.load(open('/pacedata/runningetcdnodes.txt'));
 for x in data['members']:
  endpoints=endpoints+str(x['clientURLs'])[2:][:-2]+','
 cmdline='/bin/etcdctl --endpoints='+endpoints+' '+cmd+' '+' '.join(args)
 result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
 print(result)


if __name__=='__main__':
 etcdcmd(*sys.argv[1:])
