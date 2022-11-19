#!/usr/bin/python3
import subprocess,sys, datetime
import json
from etcdgetlocalpy import etcdget as get
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost
def broadcast(*args):
	dontsend=[x.replace('-d','') for x in args if '-d' in x]
	datainfo=[x for x in args if '-d' not in x]
	print('datainfo',datainfo)
	z=[]
	knowns=[]
	myhost=hostname()
	for arg in datainfo:
		z.append(arg)
	leaderinfo=get('leader','--prefix')
	knowninfo=get('known','--prefix')
	leaderip=leaderinfo[0][1]
	for k in knowninfo:
		knowns.append(k[1])
	print('leader',leaderip) 
	print('knowns',knowns) 
	msg={'req': z[0], 'reply':z[1:]}
	with open('/root/broadcast','w') as f:
		f.write('sending'+str(msg))
	if leaderinfo[0][0].split('/')[1] not in dontsend:
		with open('/root/broadcast','a') as f:
			f.write('\nsending to leader'+leaderip)
		print('sending', leaderip, str(msg),'recevreply',myhost)
		sendhost(leaderip, str(msg),'recvreply',myhost)
	for k in knowninfo:
		with open('/root/broadcast','a') as f:
			f.write('\nsending to known'+k[1])
		if k[0].split('/')[1] not in dontsend:
			print('sending', k[1], str(msg),'recevreply',myhost)
			sendhost(k[1], str(msg),'recvreply',myhost)

if __name__=='__main__':
 broadcast(*sys.argv[1:])
