#!/usr/bin/python3
import subprocess,sys, os
import json
from ast import literal_eval as mtuple
from time import sleep

def space(etcd):
 os.environ['ETCDCTL_API']= '3'
 endpoints=''
 #cmdline=['/bin/etcdctl','--user=root:YN-Password_123','--endpoints='+endpoints,'--write-out=table','endpoint','status']
 #cmdline=['etcdctl','--user=root:YN-Password_123','--endpoints=http://'+etcd+':2379','get',key,prefix]
 cmdline=['etcdctl','--endpoints=http://'+etcd+':2379','--write-out=table','endpoint','status']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 print(result.stdout.decode())
 cmdline=['etcdctl','--endpoints=http://'+etcd+':2379','--write-out=json','endpoint','status']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 print(result.stdout.decode())
 res = mtuple(result.stdout.decode())[0]
 print(res['Status']['header']['revision'])
 #cmdline=['/bin/etcdctl','--user=root:YN-Password_123','--endpoints='+endpoints,'compact',str(res['Status']['header']['revision'])]
 cmdline=['etcdctl','--endpoints=http://'+etcd+':2379','compact',str(res['Status']['header']['revision'])]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 print(result.stdout.decode())
 #cmdline=['/bin/etcdctl','--user=root:YN-Password_123','--endpoints='+endpoints,'defrag']
 cmdline=['etcdctl','--endpoints=http://'+etcd+':2379','defrag']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 print(result.stdout.decode())
 #cmdline=['/bin/etcdctl','--user=root:YN-Password_123','--endpoints='+endpoints,'--write-out=table','endpoint','status']
 cmdline=['etcdctl','--endpoints=http://'+etcd+':2379','--write-out=table','endpoint','status']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 print(result.stdout.decode())
 return 
if __name__=='__main__':
 space(*sys.argv[1:])
