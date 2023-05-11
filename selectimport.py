#!/usr/bin/python3
import sys
from etcdgetpy import etcdget as get
from logqueue import queuethis
from etcdput import etcdput as put 
from etcddel import etcddel as dels 
from time import time as stamp
from ast import literal_eval as mtuple
#from zpooltoimport import zpooltoimport as importables

  
def selecthost(minhost,hostname,hostpools):
	if len(hostpools) < minhost[1]:
		minhost = (hostname, len(hostpools))
	return minhost

def selectimport(*args):
    global leader, leaderip, myhost, myhostip, etcdip
    if args[0]=='init':
     leader = args[1]
     leaderip = args[2]
     myhost = args[3]
     myhostip = args[4]
     etcdip = args[5]
     return
    knowns=get(etcdip, 'ready','--prefix')
    allpools=get(etcdip, 'pools/','--prefix')
    knowns = [x[0].split('/')[1] for x in knowns ]
    for poolpair in allpools:
        if myhost not in poolpair[1]:
            continue
        pool=poolpair[0].split('/')[1]
        chost=poolpair[1]
        nhost=str(get(etcdip, 'poolnxt/'+pool)[0])
        if nhost in knowns and chost not in nhost:
            print('continue')
            continue
        stampit=str(int(stamp()))
        print('nohost',nhost,chost)
        print('knowns',knowns)
        #if nhost != '_1':
        #	put('sync/poolnxt/Del_poolnxt_'+nhost+'/request','poolnxt_'+str(stamp))
        #	put('sync/poolnxt/Del_poolnxt_'+nhost+'/request/'+leader,'poolnxt_'+str(stamp))
        hosts=get(leaderip, 'hosts','/current')
        if len(hosts) < 2:
            continue   # just to clean the poolnxt or otherwise it would be 'return'
        poolnxt = get(etcdip,'poolnxt/'+pool)
        if 'dhcp' not in str(poolnxt):
            minhost = ('',float('inf'))
            for host in hosts: 
                hostname = host[0].split('/')[1]
                print('hostname',hostname)
                if hostname == chost:
                    continue
                hostpools=mtuple(host[1])
                minhost = selecthost(minhost,hostname,hostpools)
                print('minhost',minhost)
            dels(leaderip, 'sync/poolnxt/', pool)
            put(leaderip, 'poolnxt/'+pool,minhost[0])
            put(leaderip, 'sync/poolnxt/Add_'+pool+'_'+minhost[0]+'/request','poolnxt_'+stampit)
            put(leaderip, 'sync/poolnxt/Add_'+pool+'_'+minhost[0]+'/request/'+leader,'poolnxt_'+stampit)
    return

 

if __name__=='__main__':
    leaderip = sys.argv[1]
    myhost = sys.argv[2]
    myhostip = get(leaderip, 'ready/'+myhost)[0]
    leader = get(leaderip, 'leader')[0]
    if leader == myhost:
        etcdip = leaderip
    else:
        etcdip = myhostip
    selectimport(leader, leaderip, myhost, myhostip)
    #cmdline='cat /pacedata/perfmon'
    #perfmon=str(subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout)

	#if '1' in perfmon:
	#	queuethis('selectimport.py','start','system')
	#if '1' in perfmon:
	#	queuethis('selectimport.py','stop','system')
