#!/bin/python3.6
from checkleader import checkleader
from socket import gethostname as hostname

myhost = hostname()
leader = checkleader('leader','--prefix').stdout.decode('utf-8').split('\n')
leadern = leader[0].split('/')[1]
leaderip = leader[1]
while True:
 if myhost == leadern:
  remknown(leadern,myhost) 
