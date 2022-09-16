#!/bin/python3.6
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
 print(hostdic)
 print(raid['name'])
 print(len(raid['disklist']+list([adddisk])))
 print('##################')
 hostrank = 0  
 for host in hostdic:
  if hostrank == 0:
   hostrank = hostdic[host]  
  if hostrank != hostdic[host]:
   hostrank = -1
   break
 if hostrank != -1:
  hostrank = 0
 ###### ranking: no. of hosts differrence, and 1 for diff disk size found
 #hostrank = len(raidhosts)-len(raid['disklist'])
 raid['raidrank'] = (hostrank, sizerank)
 return raid 

  
 
 
if __name__=='__main__':
 getraidrank(*sys.argv[1:])
