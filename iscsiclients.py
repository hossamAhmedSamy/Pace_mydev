#!/usr/bin/python3
from etcdget import etcdget as get
import socket

myhost=get('myhost')[0]
clients=get('ActivePartners','--prefix')
if myhost in str(clients):
 for c in clients:
  print('target/'+c[0].replace('ActivePartners/',''))
