#!/usr/bin/python3
import subprocess,sys, os
import json
from time import sleep

dev = 'enp0s8'
os.environ['ETCDCTL_API']= '3'

def getload(*args):
 cmdline='systemctl stop zfs-zed'
 result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
 cmdline=['uptime']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 loadfig = result.stdout.decode().split(',')[-3].split(' ')[-1]
 cmdline=['lscpu']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 cpus = result.stdout.decode().split('\n')
 cpus = [ x for x in cpus if 'CPU(s)' in x and '-' not in x][0].split(' ')[-1]
 zload = 100 * float(loadfig)/float(cpus)
 print(zload)
 return zload 

if __name__=='__main__':
 getload(*sys.argv[1:])
