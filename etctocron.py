#!/usr/bin/python3
import subprocess,sys, datetime
from etcdgetpy import etcdget as get

def etctocron(leaderip, period='--prefix'):
 cmdline='/bin/crontab -l'
 crons=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout
 crons=str(crons).replace("b'","").split('\\n')
 crons=[x for x in crons if 'nowhost' not in x and len(x) > 5 ]
 cronstr=''
 for x in crons:
  cronstr+=x+'\n'
 etccron=get(leaderip,'Snapperiod',period)
 for x in etccron:
  y=x[1].replace('%',' ')
  cronstr+=y+'\n'
 print(cronstr)
 with open('/TopStordata/crons','w') as f:
  f.write(cronstr)
 cmdline='/bin/crontab /TopStordata/crons'
 subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout

if __name__=='__main__':
 etctocron(*sys.argv[1:])
