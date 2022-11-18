#!/usr/bin/python3
from etcdgetlocalpy import etcdget as get
from etcdgetpy import etcdget as getp
from logqueue import queuethis
from etcdput import etcdput as put 
from etcddel import etcddel as deli 
from sendhost import sendhost
from time import time as stamp
from ast import literal_eval as mtuple
#from zpooltoimport import zpooltoimport as importables

leaderip  = get('leaderip')[0]

def selecthost(minhost,hostname,hostpools):
	if len(hostpools) < minhost[1]:
		minhost = (hostname, len(hostpools))
	return minhost

def selectimport(myhost, allpools, leader, *arg):
    global leaderip
	knowns=get('ready','--prefix')
	knowns = [x[0].split('/')[1] for x in knowns ]
	for poolpair in allpools:
		if myhost not in poolpair[1]:
			continue
		pool=poolpair[0].split('/')[1]
		chost=poolpair[1]
		nhost=str(get('poolsnxt/'+pool)[0])
		if nhost in knowns and chost not in nhost:
			print('continue')
			continue
		stampit=str(int(stamp()))
		print('nohost',nhost,chost)
		print('knowns',knowns)
		#if nhost != '-1':
		#	deli('poolsnxt',nhost)
		#	put('sync/poolsnxt/Del_poolsnxt_'+nhost+'/request','poolsnxt_'+str(stamp))
		#	put('sync/poolsnxt/Del_poolsnxt_'+nhost+'/request/'+leader,'poolsnxt_'+str(stamp))
		hosts=getp(leaderip, 'hosts','/current')
		if len(hosts) < 2:
			continue   # just to clean the poolsnxt or otherwise it would be 'return'
		minhost = ('',float('inf'))
		for host in hosts: 
			hostname = host[0].split('/')[1]
			print('hostname',hostname)
			if hostname == chost:
				continue
			hostpools=mtuple(host[1])
			minhost = selecthost(minhost,hostname,hostpools)
			print('minhost',minhost)
		put(leaderip, 'poolsnxt/'+pool,minhost[0])
		put(leaderip, 'sync/poolsnxt/Add_'+pool+'_'+minhost[0]+'/request','poolsnxt_'+stampit)
		put(leaderip, 'sync/poolsnxt/Add_'+pool+'_'+minhost[0]+'/request/'+leader,'poolsnxt_'+stampit)
	return

 

if __name__=='__main__':
	myhost = get('clusternode')[0]
	leader=get('leader','--prefix')[0][0].replace('leader/','')
	allpools=get('pools/','--prefix')
	selectimport(myhost,allpools,leader, *sys.argv[1:])
	cmdline='cat /pacedata/perfmon'
	
	perfmon=str(subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout)

	#if '1' in perfmon:
	#	queuethis('selectimport.py','start','system')
	#if '1' in perfmon:
	#	queuethis('selectimport.py','stop','system')
