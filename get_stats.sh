#!/bin/bash

# Grab the stats from the various machines

UPDATE_PERIOD=5

NCS="172.22.28.81 172.22.28.82 172.22.28.83"

STATFILE=/tmp/stats
OUTPUT=/tmp/monitor.config
TMP=$OUTPUT.tmp

LOG=/tmp/get_stats.log
ERRLOG=$LOG.err

echo "Writing stdout to $LOG and stderr to $ERRLOG..."
exec 2> $ERRLOG | tee $LOG

function statfromhost() {
    HOST=$1
    SSH="ssh -q -q -o BatchMode=yes -o ConnectTimeout=10"
    RESULT=$($SSH root@$HOST "cat $STATFILE")

    echo $RESULT
}

function getipforinst() {
    INST=$1
    IP=$(cat /tmp/desc | grep $INST | cut -f4)

    echo $IP
}

function threshold_stat_inst() {
    STAT=$1
    THRESHOLD=10

    if [ "$STAT" -ge "$THRESHOLD" ];
    then
        STAT=100
    fi

    echo $STAT
}

while [ 1 ];
do
    # Get list of running instances...
    python $(which euca-describe-instances) > /tmp/desc
    INSTIDS=$(cat /tmp/desc | grep i- | cut -f2)

    # Clear out our temporary file
    echo -n > $TMP

    let count=0
    echo Running.... $(date)
    for i in $INSTIDS;
    do
        IP=$(getipforinst $i)
        echo -n "Getting info for $i ($IP)..."
        STAT=$(statfromhost $IP)

        echo test$STAT |grep "^test[.0-9]\+$" >& /dev/null
        if [ "$?" -eq "0" ]; then
          STATNEW=$(threshold_stat_inst $STAT)
          echo "$STAT ($STATNEW)"
          echo "$i $STATNEW" >> $TMP
        else
          echo "Error!"
        fi
        let count=count+1
    done

    for n in $NCS;
    do
        echo -n "Getting info for $n..."
        STAT=$(statfromhost $n)

        echo test$STAT |grep "^test[.0-9]\+$" >& /dev/null
        if [ "$?" -eq "0" ]; then
          echo $STAT
          echo "$n $STAT" >> $TMP
        else
          echo "Error!"
        fi
        let count=count+1
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

