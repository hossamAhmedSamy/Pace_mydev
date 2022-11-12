#!/usr/bin/python3
from etcdgetpy import etcdget as get
import sys

def iscsiclients(mycluster):
    clients=get(mycluster, 'ActivePartners','--prefix')
    for c in clients:
        print('target/'+c[0].replace('ActivePartners/',''))

if __name__=='__main__':
 iscsiclients(*sys.argv[1:])
