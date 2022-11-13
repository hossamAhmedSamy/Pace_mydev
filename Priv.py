#!/usr/bin/python3
import sys,subprocess
import socket
myhost=socket.gethostname()
key='run/'+myhost+'/userpriv/'+sys.argv[2]+'/'+str(sys.argv[3::2]).replace(' ','').replace('[','').replace(']','').replace("'",'').replace(",",";")
val=str(sys.argv[4::2]).replace(' ','').replace('[','').replace(']','').replace("'",'').replace(",","/")
cmdline=['/pace/etcdput.py',key,val]
result=subprocess.run(cmdline,stdout=subprocess.PIPE)

