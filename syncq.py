#!/bin/python3.6
import sys, subprocess
from os import listdir
from sendhost import sendhost

def syncq(leaderip,myhost):
 files = listdir('/TopStordata')
 taskperf = [x for x in files if 'taskperf' in x]
 taskperf.sort()
 lastfile = taskperf[-1]
 msg={'req': 'syncq', 'reply':[lastfile]}
 print('hi',leaderip, myhost)
 sendhost(leaderip, str(msg),'recvreply',myhost)



if __name__=='__main__':
 syncq(*sys.argv[1:])
