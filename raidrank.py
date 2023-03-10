#!/usr/bin/python3
import sys, os
os.environ['ETCDCTL_API']= '3'
  
def getraidrank(raid, removedisk, adddisk):
 ####raidraink = (name, location(0 is best), size (0) is best)
 raidrank = (0,0) 
 raidhosts = set()
 raiddsksize = adddisk['size']
 sizerank = 0
 hostdic = dict()
 raidlist = raid['disklist']
 if removedisk['name'] != adddisk['name']:
  raidlist = raidlist + list([adddisk]) 
 for disk in raidlist:
  if disk['name'] == removedisk['name'] and disk['name'] != adddisk['name']:
   continue
  if ('F' or 'moved') in disk['changeop'] :
   continue
  if disk['host'] not in hostdic:
   hostdic[disk['host']] = 0
  hostdic[disk['host']] += 1
  #raidhosts.add(disk['host'])
  if raiddsksize != disk['size']:
   sizerank = 1
 print('##################')
 print('hostdic',hostdic)
 print('raidname',raid['name'])
 print('lenghts',len(raid['disklist']+list([adddisk])))
 print('##################')
 hostset = set()
 hostrank = 0  
 balance = 0
 for host in hostdic:
  balance += hostdic[host]*hostdic[host]
  hostset.add(hostdic[host]*hostdic[host])
 #balance = len(raid['disklist'])%len(hostdic) 
 print('balance',balance, len(raid['disklist']),len(hostdic))
 if balance == 0 and len(hostset) == 1 and len(hostdic) > 1:
  hostrank = 0
 else:
  hostrank = -1
 ###### ranking: no. of hosts differrence, and 1 for diff disk size found
 #hostrank = len(raidhosts)-len(raid['disklist'])
 #raid['raidrank'] = (hostrank, sizerank)
 raid['raidrank'] = (balance, sizerank)
 return raid 

  
 
 
if __name__=='__main__':
 getraidrank(*sys.argv[1:])
