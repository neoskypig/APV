#! /bin/bash

if [ $# -lt 2 ]; then
 	echo "Usage: sh dataCLean.sh raw.log new.log"
	exit 0
fi

cat $1 | egrep "Perf|onVoiceEvent\.Comming" > $2
