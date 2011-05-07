#!/bin/bash

# Grab the stats from the various machines

UPDATE_PERIOD=10

NCS="cn71 cn72 cn73"

STATFILE=/tmp/stats
OUTPUT=/tmp/monitor.config.testing
TMP=$OUTPUT.tmp

LOG=/tmp/get_stats.log
ERRLOG=$LOG.err

echo "Writing stdout to $LOG and stderr to $ERRLOG..."
exec > $LOG 2> $ERRLOG

function statfromhost() {
    HOST=$1
    RESULT=$(ssh root@$HOST "cat $STATFILE")

    echo $RESULT
}

function getipforinst() {
    INST=$1
    IP=$(python $(which euca-describe-instances) | grep $INST | cut -f4)

    echo $IP
}

while [ 1 ];
do
    # Get list of running instances...
    INSTIDS=$(python $(which euca-describe-instances) | grep i- | cut -f2)

    # Clear out our temporary file
    echo -n > $TMP

    let count=0
    for i in $INSTIDS;
    do
        IP=$(getipforinst $i)
        STAT=$(statfromhost $IP)

        echo Got $STAT for $i...
        echo test$STAT |grep "^test[.0-9]\+$"
        if [ "$?" -eq "0" ]; then
          echo "$i $STAT" >> $TMP
          echo $STAT
          let count=count+1
        fi
    done

    for n in $NCS;
    do
        STAT=$(statfromhost $n)

        echo Got $STAT for $n...
        echo test$STAT |grep "^test[.0-9]\+$"
        if [ "$?" -eq "0" ]; then
          echo "$n $STAT" >> $TMP
          let count=count+1
        fi
    done

    lines=$(wc -l $TMP | awk '{print $1}')
    if [ "$lines" -eq "$count" ];
    then
        echo "Updating stats to the following:"
        cat $TMP
        cp $TMP $OUTPUT
    else
        echo "Error getting stats ($lines vs $count), not updating $OUTPUT!"
    fi

    sleep $UPDATE_PERIOD;
done

