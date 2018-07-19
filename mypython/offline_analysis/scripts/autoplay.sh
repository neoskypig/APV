#! /bin/sh
trap "echo break && break" 2  

# mode
# run
if [[ $1 =~ ^[0-9]*$ ]]
then
	echo "输入为数字:" $1
else
	if [  -d $1 ];then
		echo "输入为文件目录:" $1
	else
		echo 文件目录 $1 不存在
		exit
	fi
fi

if [ $2 != "kamino" ] && [ $2 != "me"]; then
	echo "Please Set Product Type rightly, now we support Kamino and Me"
	exit
fi

echo "---Log Start---"
logFilePrefix=$(date +%y-%m-%d-%H-%M)
rawlog=${logFilePrefix}".raw"
cleanlog=${logFilePrefix}".clean"

echo "Raw Log: "$rawlog"->Clean Log: "$cleanlog

adb shell logread -f  > $rawlog &
# PID=$!

function input_num(){
	for num in `seq $1`
	do
		adb shell echo "...Play[$num]..."
		kwfile="ruoqi_M069.wav"
		starT=$(adb shell "date +%m-%d' '%T")
		if [ $num -eq 1 ]; then
			echo "Start Test Time: $starT"
		fi
		#echo $starT
		adb shell echo "Perf_Start_$num,Time:$starT,Test $kwfile" | adb shell logger
		#adb shell echo "ruoqi_M069.wav Index:$num" | adb shell logger -t "perfTag"
		sleep 2
		./../kw_audio/sox-14.4.2/play ./../kw_audio/ruoqi/ruoqi_M069.wav
		#Change this sleep time according to audio wav file playback duration
		sleep 5
		endT=$(adb shell "date +%m-%d' '%T")
		#echo $endT
		adb shell echo "Perf_End_$num,Time:$endT,Test $kwfile" | adb shell logger
		#adb shell echo "Test Index:$num" | adb shell logger -t "perfTag"
		# sleep 5
		let num+=1
	done
	adb shell echo "Test Total Num is $1" | adb shell logger -t "perfTag"

}

function input_dir(){
	num=0
	for file in `find $1 -name "*.wav"`
	do
		let num+=1
		adb shell echo "...Play[$num]..."
		#kwfile="ruoqi_M069.wav"
		starT=$(adb shell "date +%m-%d' '%T")
		if [ $num -eq 1 ]; then
			echo "Start Test Time: $starT"
		fi
		adb shell echo "Perf_Start_$num,Time:$starT,Test $file" | adb shell logger
		sleep 2
		./../kw_audio/sox-14.4.2/play $file
		sleep 5
		endT=$(adb shell "date +%m-%d' '%T")
		adb shell echo "Perf_End_$num,Time:$endT,Test $file" | adb shell logger

	done
	adb shell echo "Test Total Num is $num" | adb shell logger -t "perfTag"

}

# run
if [[ $1 =~ ^[0-9]*$ ]]
then
	input_num $1
else
	if [  -d $1 ];then
		input_dir $1	
	fi
fi
#make sure the log is captured as much as possible
sleep 20

adb shell killall logread
echo "---Log End---"
# echo $PID|xargs kill -15

echo "---Log Preprocess Begin---"

if [ $2 == "kamino"]; then
	cat $rawlog | egrep "Perf|onVoiceEvent\.Comming" > $cleanlog
else if [ $2 == "me"]; then
	echo "Don't forget to add Log Filter for log preprocessing"
fi

echo "---Log Preprocess End---"

python dataAnalysis.py $cleanlog $2
