#!/bin/python3.6
from etcdget import etcdget as get
from etcdput import etcdput as put 
from broadcasttolocal import broadcasttolocal 
from etcddel import etcddel as deli 
import poolall 
import socket, sys, subprocess,datetime
from broadcast import broadcast as broadcast 
from sendhost import sendhost
from ast import literal_eval as mtuple
#from zpooltoimport import zpooltoimport as importables
def electimport(myhost, allpools,*arg):
	knowns=get('known','--prefix')
	for poolpair in allpools:
		pool=poolpair[0].split('/')[1]
		chost=poolpair[1]
		nhost=str(get('poolsnxt/'+pool)[0])
		if nhost not in str(knowns) or nhost in chost:
			deli('poolsnxt',nhost)
			nhost='nothing'
		if nhost in str(knowns):
			continue
		hosts=poolall.getall(chost)['phosts']
		for host in hosts: 
			if host != chost:
				with open('/root/selecttmp','a') as f:
					f.write('\npoolpair:'+str(poolpair))
					f.write(' ,host: '+host)
					f.write(' ,chost:'+chost)
					f.write(' ,nhost:'+nhost)
                                if len(host) > 2 and len(pool) > 4:
				 put('poolsnxt/'+pool,host)
				 broadcasttolocal('poolsnxt/'+pool,host)
				break
	return

 
def importpls(myhost,allinfo,*args):
	if(len(allinfo) < 0):
		return
	pools={}
	for host in allinfo:
		if 'nothing' in host[1]:
			continue
		for pool in mtuple(host[1]):
			pools[pool[0]]=[]
	for host in allinfo:
		if 'nothing' in host[1]:
			continue
		for pool in mtuple(host[1]):
			pools[pool[0]].append((host[0].split('/')[1],pool[1],pool[2]))
	hosts=[]
	importedpools=['hi']
	for pool in pools.keys():
		hosts.append((pool,max(pools[pool],key=lambda x:x[1])[0])) 
	for hostpair in hosts:
		if hostpair[0] == 'nothing':
			continue
		owner=hostpair[1]
################# elect the host to import the pool ###############
		timestamp=int(datetime.datetime.now().timestamp())-5
		locked=get('lockedpools','--prefix')
		ownerstatus=get('cannotimport/'+owner)
		if hostpair[0] in ownerstatus:
			continue
		#if hostpair[0] in importedpools:
		#	continue
		if hostpair[0] in locked:
			print('in locked')
			lockinfo=get('lockedpools/'+hostpair[0])
			oldtimestamp=lockinfo[0].split('/')[1]
			lockhost=lockinfo[0].split('/')[0]
			lockhostip=get('leader/'+lockhost)
			if( '-1' in str(lockhostip)):
				lockhostip=get('known/'+lochost)
				if('-1' in str(lockhostip)):
					deli('lockedpools/'+pool)
					continue
			if int(timestamp) > int(oldtimestamp):
				put('lockedpools/'+pool,lockhost+'/'+str(timestamp))
				z=['/TopStor/pump.sh','ReleasePoolLock',pool]
				msg={'req': 'ReleasePoolLock', 'reply':z}
				sendhost(lockhostip[0], str(msg),'recvreply',myhost)

			continue
		#importedpools.append(hostpair[0])
		ownerip=get('leader',owner)
		if ownerip[0]== -1:
			ownerip=get('known',owner)
			if str(ownerip[0])== '-1':
				return
		put('lockedpools/'+hostpair[0],owner+'/'+str(timestamp))
#################### end of election
		z=['/TopStor/pump.sh','Zpool','import','-c','/TopStordata/'+hostpair[0],'-am']

		msg={'req': 'Zpoolimport', 'reply':z}
		sendhost(ownerip[0][1], str(msg),'recvreply',myhost)
		#z=['/TopStor/pump.sh','ClearCache',hostpair[0][1:]]
		#msg={'req': 'ClearCache', 'reply':z}
		#sendhost(ownerip[0][1], str(msg),'recvreply',myhost)
		deli('toimport',hostpair[0])
	return

if __name__=='__main__':
	myhost=socket.gethostname()
	allpools=get('pools/','--prefix')
	electimport(myhost,allpools,*sys.argv[1:])
	allinfo=get('to','--prefix')
	importpls(myhost,allinfo,*sys.argv[1:])
