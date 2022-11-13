#!/usr/bin/python3
import subprocess
from ast import literal_eval as mtuple
import socket
from os import listdir
from os.path import isfile, join

myhost=socket.gethostname()
fpath='/var/www/html/des20/Data/'
#### exit if found me in confirmed
cmdline=['/pace/etcdget.py','broadcast/confirmed','--prefix']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
conf=str(result.stdout).replace('broadcast/confirmed/','')[2:][:-3].split('\\n')
print('conf==',str(conf))
if myhost in str(conf) or conf==['']:
 exit()
#############
cmdline=['/pace/etcdget.py','known','--prefix']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
known=str(result.stdout).replace('known/','')[2:][:-3].split('\\n')
cmdline=['/pace/etcdget.py','broadcast/response','--prefix']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
broad=str(result.stdout).replace('broadcast/response/','')[2:][:-3].split('\\n')
######## prepare times from files###########
onlyfiles = [f for f in listdir(fpath) if isfile(join(fpath, f)) and "TopStor.log." in f]
if onlyfiles==[''] or len(known) > len(onlyfiles):
 cmdline=['/pace/etcdput.py','broadcast/request/'+myhost, '1']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
preptimes=[]
mini=99999999999999999
for f in onlyfiles:
 with open(fpath+f) as ff:
  last=int(str(ff.readlines()[-1]).split(' ')[5])
  if last < mini: 
   mini=last
  mini+=1
  preptimes.append((f,last))
#################### get all responses
cmdline=['/pace/etcdget.py','broadcast/response','--prefix']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
broad=str(result.stdout).replace('broadcast/response/','')[2:][:-3].split('\\n')
cmdline=[]
counter=0
if broad==['']:
 cmdline=['/pace/etcdput.py','broadcast/request/'+myhost, str(mini) ]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 exit()
confirmed=False
for k in broad:
 k=k.replace('\\','')
 k=mtuple(k)
 host=k[0].split('/')[0]
 if host==myhost:
  continue
 cmdline=[]
 cmdline2=[]
 counter=0
############ update responses to file only if last time (in file) is less than first time in response
 if host in str(preptimes): 
  for s in preptimes:
   if host in s[0]:
    last=s[1]
 else:
   last=1
 first=9999999999999999
 with  open('/var/www/html/des20/Data/TopStor.log.'+host,'at') as f:
  a=str(k[1])
  h=mtuple(a)
  for m in h:
   ss=str(m).replace('[','').replace(']','').replace("'",'')
   ssfirst=int(ss.split(' ')[5])
   if first > ssfirst:
     first=ssfirst
   if first > last:
    cmdline.append(ss.replace(',','')+'\n')
  if len(cmdline) > 0:
   f.writelines(cmdline[::-1])
   confirmed=True;
if confirmed:
 cmdline=['/pace/etcdput.py','broadcast/confirmed/'+myhost, 'done']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
else:
 cmdline=['/pace/etcdput.py','broadcast/request/'+myhost, str(mini) ]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 print('no udpate')
