#!/bin/python3.6
import subprocess
from ast import literal_eval as mtuple
from etcdget import etcdget as get
import socket
from os import listdir
from os.path import isfile, join

clients=get('ActivePartners','--prefix')
for c in clients:
  print('target/'+c[0].replace('ActivePartners/',''))
