#!/bin/bash

# Starts a load on the specified instance id(s)

INSTIDS=$@

function getipforinst() {
    INST=$1
    IP=$(python $(which euca-describe-instances) | grep $INST | cut -f4)

    echo $IP
}

for INST in $INSTIDS;
do
	IP=$(getipforinst $INST)	
	echo "Putting load on $INST ($IP)..."
	ssh $IP "nohup /opt/cpu_bench.sh >& /dev/null < /dev/null &"
done
