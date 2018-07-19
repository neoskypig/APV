import sys
import re

kaminoRegs = [
    ['Local Awake Time', 		re.compile('\[R2\].*?onVoiceEvent\.Comming')],
    ['Local Awake Light Lua Time', 	re.compile('\[lua.*?init\.lua.*?Perf_Light_Lua\] voice Coming')],
    ['Local Awake Light Native Time', 	re.compile('rkactivation-light:.*?\[Perf_Light_Native\] Performance Checking')],
    ['Local Awake Player LuaN Time', 	re.compile('\[lua\].*?\RKLuaPlayer.*?\[Perf_Player_LuaN_Play\]')],
    ['Local Awake Player Native Time', 	re.compile('\[lua\].*?\RKWavPlayer.*?\[Perf_Player_Native_Play\]')]
]

kaminoTimeTitle = [
    "LightLua",
    "LightC",
    "PlayerGlue",
    "PlayerC"
]

kaminoColor = [
    'green',
    'red',
    'skyblue',
    'blue'
]

meRegs = [
    ['key Time 0 you want', 	re.compile('xxx')],
    ['key Time 1 you want', 	re.compile('yyy')],
    ['key Time 2 you want', 	re.compile('zzz')],
    ['key Time 3 you want', 	re.compile('xxx')],
    ['key Time 4 you want', 	re.compile('yyy')]
]

meTimeTitle = [
    "xxx",
    "yyy",
    "zzz",
    "www"
]

meColor = [
    'green',
    'red',
    'skyblue',
    'blue'
]

def initTag(pdtType):
    if pdtType == "kamino":
        return kaminoRegs, kaminoTimeTitle, kaminoColor
    elif pdtType == "me":
        return meRegs, meTimeTitle, meColor
    else: # Add new product here
        return None, None, None
        
'''
if __name__ == '__main__':
	print "xxx:" + str(len(rkdaregs.gRegs))
	for id in range(len(rkdaregs.gRegs)):
		treg = rkdaregs.gRegs[id]
		print "xxx1:" + treg[0] + ":" + str(treg[1])
	for reg in rkdaregs.gRegs:
   		print "yyy:" + str(len(reg))
		for sub in reg:
			print "zzz:" + str(sub)
'''
