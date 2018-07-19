#!/usr/bin/python
# -*- coding: utf-8 -*- 

import sys
import re
import datetime
import time
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.interpolate import spline

from stats import getStatsResult

from rktag import initTag

#绝对时间，字符串形式
gTagStartTList = []
gTagEndTList = []

gRegs = []
gTimeTitle = []
gColor = []


# Time conversion
def pTimeCov(timeStr):
	msBegin = timeStr.rfind(".") + 1
	msEnd   = len(timeStr)
	timeMs  = int(timeStr[msBegin:msEnd])
	nTimeStr = timeStr[0:msBegin - 1]
	mTimeS = int(time.mktime(time.strptime(nTimeStr, '%Y-%m-%d %H:%M:%S')))
	mTimeMS  = round(mTimeS * 1000) + timeMs;
	return mTimeMS

def pSub(beginStr, endStr):
	tmpPos = beginStr.find(".")
	timeBeginMsStr = beginStr[tmpPos + 1:len(beginStr)]
	tmpPos = endStr.find(".")
	timeEndMsStr = endStr[tmpPos + 1:len(endStr)]
	tbeginS = pTimeCov(beginStr)
	tendS   = pTimeCov(endStr)
	elapsedTime = (tendS * 1000 + int(timeEndMsStr)) - (tbeginS * 1000 + int(timeBeginMsStr))
	if elapsedTime < 0.0:
		print "Error::" + "Elapsed Time:" + str(elapsedTime) + "/ms :" + \
			timeBeginMsStr + ":" + timeEndMsStr + ":" + str(tbeginS) + ":" + str(tendS)
	return elapsedTime



def pParseTagTime(aline):
	#Tag Start Time
	timeStr = ""
	ret = None
	try:
		ret = re.search("(Perf_Start_\d+.*?,Time\:\d{2}-\d{2} \d{2}:\d{2}\:\d{2})", aline)
	except:
		ret = None
	if ret:
		begin = aline.find("Time:") + len("Time:")
		timeStr = "2018-" + aline[begin:ret.end()] + ".000"
		#timeMs  = pTimeCov(timeStr)
		#timeStr = timeStr + "->" + str(timeMs)
		#print "Tag Start:\t\t\t" + timeStr
		gTagStartTList.append(timeStr)
	#Tag End Time
	timeStr = ""
	ret = None
	try:
		ret = re.search("(Perf_End_\d+.*?,Time\:\d{2}-\d{2} \d{2}:\d{2}\:\d{2})", aline)
	except:
		ret = None
	if ret:
		begin = aline.find("Time:") + len("Time:")
		timeStr = "2018-" + aline[begin:ret.end()] + ".000"
		#timeMs  = pTimeCov(timeStr)
		#timeStr = timeStr + "->" + str(timeMs)
		#print "Tag End:\t\t\t" + timeStr
		if pTimeCov(timeStr) < gFirstTagStartTime:
			print "Error: " + str(sys._getframe().f_lineno) + ":" + aline
			return
		gTagEndTList.append(timeStr)

def pDumpTag():
    sLen = len(gTagStartTList)
    eLen = len(gTagEndTList)
    if sLen != eLen:
        print "\t\t !!!! Start Tag:" + str(sLen) + "->End Tag:" + str(eLen) + " !!!!"
    for id in range(min(sLen, eLen)):
        print "Tag: " + gTagStartTList[id] + "\t->\t" + gTagEndTList[id]

def pParseTime(aline, ats, tid, sTime, eTime):
    for reg in gRegs:
	try:
		ret = reg[1].search(aline)
	except:
		ret = None
	if ret:
		tstr = aline[ret.start():ret.end()]
		#print tstr
		#print tstr + "[" + str(ret.start()) + "->" + str(ret.end()) + "]"
		try:
			#print tstr
			ret = re.search("(\d{2}-\d{2} \d{2}:\d{2}\:\d{2}\.\d{3})", tstr)
		except:
			ret = None
		if ret:
			timeStr = "2018-" + ret.group(0)
			#tmp  = pTimeCov(timeStr)
			#timeStr = timeStr + "->" + str(timeMs)
                        rtime = pTimeCov(timeStr)
			if rtime >= sTime and rtime <= eTime:
			    #print "[" + str(tid) + "] " + reg[0] + ":\t\t" + timeStr
			    ats.append(timeStr)

def list_to_str(my_list):
    return ','.join('%s' % id for id in my_list)

def pWriteToCsv(rtlist):
        if len(rtlist) != len(gTimeTitle):
            print "ERROR: Not matched num[" + str(len(rtlist)) + "->" + str(len(gTimeTitle)) + "]"
            sys.exit()
	f=open(sys.argv[1].replace("clean", "csv"), "w")
        for idx in range(len(rtlist)):
            node = rtlist[idx]
            f.write(gTimeTitle[idx] + ":\t\t\t" + list_to_str(node) + "\n")

	f.write( ",max,min,avg,median\n")
        for idx in range(len(rtlist)):
            f.write(gTimeTitle[idx] + ":\t\t\t" + list_to_str(getStatsResult(rtlist[idx])) + "\n")
	f.close()

def smoothLine(x,y, switch=True): 
        if switch:
                T = np.array(x)
                power = np.array(y)

                xnew = np.linspace(T.min(),T.max(),30*len(x)) #300 represents number of points to make between T.min and T.max 
                power_smooth = spline(T,power,xnew)
                return xnew, power_smooth
        else:
                return x, y

def pDrawLineGraph(rtlist):
    x = range(len(rtlist))
    print x
    plt.title("Awake Performance Analysis (Robin@ROKID)")
    plt.xlabel("Number")
    plt.ylabel("Time Duaration/ms")

    smooth=False # [warning] Forced fitting curve may lead to distortion
    for idx in range(len(rtlist)):
        node = rtlist[idx]
        print node
        ret=smoothLine(x, node, smooth)
        plt.plot(ret[0], ret[1],   color=gColor[idx], label=gTimeTitle[idx])
        plt.xticks(ret[0])
    plt.legend()

    plt.show()

def pTimeSort(atlist):
    #print "\nSorting..." + str(len(atlist))
    mslen = len(gTagStartTList) #awake count, x
    mreglen = len(gRegs) #sample count, y
    mrealcnt = 0
    rtlist = []
    for idx in range(mslen):
        tmp = atlist[idx]
        if len(tmp) == mreglen + 2:# 2 = start tag + end tag
            node = []
            pos = len(tmp) - 2 # start position
            while (pos > 1):
                #print "DEBUG:[" + str(pos) + "] " + tmp[pos] + "->[" + str(pos - 1) + "] " + tmp[pos - 1]
                #node.append(int(pTimeCov(tmp[pos]) - pTimeCov(tmp[pos - 1])))
                node.append(int(pTimeCov(tmp[pos]) - pTimeCov(tmp[1])))
                pos -= 1
            node.reverse()
            mrealcnt += 1
            #print "xxxx---"
            #print node
            #print "xxxx***"
            rtlist.append(node)
        else:
            print "ERROR: Ignore it[" + str(len(tmp)) + "->" + str(mreglen + 2) + "]\n"

    trtlist = []
    for idx in range(len(gColor)):
        node = []
        for idy in range(mrealcnt):
            node.append(rtlist[idy][idx])
        trtlist.append(node)

    return trtlist
 
def pDataDump(atlist, rtlist):
        print "Result: \n\n"
        for node in atlist:
            print "xxxx"
            print node
            print "yyyy"
        for idx in range(len(rtlist)):
            print "\nID:" + str(idx)
            for idy in range(len(rtlist[idx])):
                print rtlist[idx][idy]
            print "\n"
	
if __name__ == '__main__':
	
	print "\n\t>>>Rokid AI Performance Offline Analysis<<<"

	if (len(sys.argv) < 3):
		print ">>>Usage Help..."
		print ">>>python ./dataAnalysis.py log.clean pdtType"
		print ">>>Any issue, @tianyang.zhu@rokid.com"
		sys.exit()

	# print "\nExpect Interaction Num: " + sys.argv[2]

	gFirstTagStartTime = 0
        pdType = sys.argv[2]
        if pdType != 'me' and pdType != 'kamino':
            print "ERROR: Don't support this Product " + pdType
            sys.exit()
        gRegs, gTimeTitle, gColor = initTag(pdType)

	logFileName = sys.argv[1]

	logFile = open(logFileName)
	for eline in logFile:
	        pParseTagTime(eline)
        sLen = len(gTagStartTList)
        eLen = len(gTagEndTList)
        if sLen != eLen:
            print "\t\t ERROR: Start Tag:" + str(sLen) + "->End Tag:" + str(eLen) + " !!!!"
            sys.exit()
        pDumpTag()
        
        #atlist = [[]] * sLen 
        #print "0712:" + str(len(atlist))
        atlist = []

        for tid in range(len(gTagStartTList)):
            node = []
            #print "\n\n[" + str(tid) + "] Tag ID Start\t\t" + gTagEndTList[tid]
            sTime = pTimeCov(gTagStartTList[tid])
            eTime = pTimeCov(gTagEndTList[tid])
            logFile.seek(0)
            node.append(gTagStartTList[tid])
            for eline in logFile:
                pParseTime(eline, node, tid, sTime, eTime)
            node.append(gTagEndTList[tid])
            #print "[" + str(tid) + "] Tag ID End\t\t" + gTagEndTList[tid]
            node.sort()
            #print node
            atlist.append(node)
            #Lowering CPU workload
            time.sleep(0.5)
        logFile.close()

        rtlist = pTimeSort(atlist)
        #pDataDump(atlist, rtlist)
        print "\nThe Total num is ", sLen

        pWriteToCsv(rtlist)

        pDrawLineGraph(rtlist)

	print "\n\n"
