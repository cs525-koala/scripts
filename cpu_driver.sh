#!/bin/sh

# Drive cpu_bench scripts...

# We make all kinds of assumptions about state/things working/etc :)
# Assume hadoop1 <-->hadoop9 are running, all set up, etc.

#TODO: Increase offset times in cpu_benchmark.py? (LATER!)

ITERS=12

RESULTS_FILE=/opt/cpu_bench_times

# Runs the requested command on the requested host, 'safely'
function remoterun() {
    HOST=$1
    CMD=$2

    SSH="ssh -q -q -o BatchMode=yes -o ConnectTimeout=30"
    RESULT=$($SSH root@$HOST "$CMD")

    echo $RESULT
}

function remoterunall() {
    CMD=$1

    for i in `seq 1 9`
    do
        remoterun hadoop$i "$CMD"
    done
}

# Make sure no rape tasks are running on the nc's...
KILL_RAEP_CMD="ps aux|grep raep|awk '{print $2}'|xargs kill -9"
remoterun cn72 "$KILL_RAEP_CMD"
remoterun cn73 "$KILL_RAEP_CMD"

RAEPCMD="nohup /opt/cpu_raep.sh >& /dev/null < /dev/null &"

UNIQ="CPU$$"

echo "This run's uniq identifier is **$UNIQ**"

# Main loop
# Run each iteration of the eval, copy over the output
# And increase the number of raep processes on the nc's
for i in `seq 1 $ITERS`
do
    # Kick off the tasks
    ./cpu_benchmark.py

    # Copy results to file for this iteration...
    remoterunall "cp $RESULTS_FILE $RESULTS_FILE.$UNIQ.$i"

    # Done! Now run another raeps...
    remoterun cn72 $RAEPCMD
    remoterun cn73 $RAEPCMD
done

# Bundle up the results for easier scp'ing later.
remoterunall "tar cvf $RESULTS_FILE.$UNIQ.tar $RESULTS_FILE.$UNIQ.*"
