#!/usr/bin/python3
import subprocess
import sys


def linewords(theline,lword):
 h=theline.split()
 lwordx=[c+" 0 "+h[h.index(c)+1] for c in h if lword in c]
 return lwordx[0]

host=sys.argv[1]
result=subprocess.run(['/sbin/zpool','status'], stdout=subprocess.PIPE)
linelist=result.stdout.splitlines();
buf=[]
buf=[ host+" /dev/sd_ "+linewords(str(c),str('scsi')) for c in linelist if 'scsi' in str(c) and 'ONLINE' not in str(c) and 'AVAIL' not in str(c) ]
print("\n".join(buf))
