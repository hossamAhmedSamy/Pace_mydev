#!/usr/bin/python3
import subprocess,sys, os
from etcdput import etcdput as put
from time import sleep

dev = 'enp0s8'
os.environ['ETCDCTL_API']= '3'

def getload(leaderip,myhost):
 cmdline='systemctl stop zfs-zed'
 subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
 cmdline=['uptime']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 loadfig = result.stdout.decode().split(',')[-3].split(' ')[-1]
 cmdline=['lscpu']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 cpus = result.stdout.decode().split('\n')
 cpus = [ x for x in cpus if 'CPU(s)' in x and '-' not in x][0].split(' ')[-1]
 print(float(loadfig),loadfig, float(cpus),cpus)
 zload = 100 * float(loadfig)/float(cpus)
 put(leaderip,'cpuperf/'+myhost,str(zload))
 print(zload)
 return zload 

if __name__=='__main__':
 getload(*sys.argv[1:])
