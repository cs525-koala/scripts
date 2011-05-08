#!/bin/bash

# Drive cpu_bench scripts...

# We make all kinds of assumptions about state/things working/etc :)
# Assume hadoop1 <-->hadoop9 are running, all set up, etc.

#TODO: Increase offset times in cpu_benchmark.py? (LATER!)

ITERS=2

RESULTS_FILE=/opt/cpu_bench_times

RAEPCMD="nohup /opt/cpu_raep.sh >& /dev/null < /dev/null &"
BUNDLECMD="tar cvf $RESULTS_FILE.$UNIQ.tar $RESULTS_FILE.$UNIQ.*"

if [ "$1" = "" ]
then
    echo "Usage: $0 <identifier>"
    exit 1
fi
UNIQ="eval-$1"

echo "This run's uniq identifier is **$UNIQ**"

# Comment this out to actually execute commands
#RUN=echo

# Runs the requested command on the requested host, 'safely'
function remoterun() {
    HOST=$1
    CMD=$2

    SSH="ssh -q -q -o BatchMode=yes -o ConnectTimeout=60"
    RESULT=$($SSH root@$HOST "$RUN $CMD")

    echo $RESULT
}

function remoterunall() {
    CMD=$1

    for i in `seq 1 9`
    do
        remoterun hadoop$i "$CMD"
    done
}

# Main Execution

# Provision the hosts with our killgrep command...
for i in `seq 1 9`
do
    scp $PWD/killgrep.sh root@hadoop$i: >& /dev/null
done
scp $PWD/killgrep.sh cn72: >& /dev/null
scp $PWD/killgrep.sh cn73: >& /dev/null

# Make sure no rape tasks are running on the nc's...
remoterun cn72 "./killgrep.sh cpu_raep" > /dev/null
remoterun cn72 "./killgrep.sh bc" > /dev/null

remoterun cn73 "./killgrep.sh cpu_raep" > /dev/null
remoterun cn73 "./killgrep.sh bc" > /dev/null


# Main loop
# Run each iteration of the eval, copy over the output
# And increase the number of raep processes on the nc's
for ITER in `seq 1 $ITERS`
do
    echo "ITERATION $ITER..."

    # Make sure the instances are clean
    remoterunall "./killgrep.sh cpu_bench" > /dev/null
    remoterunall "./killgrep.sh cpu_task" > /dev/null
    remoterunall "./killgrep.sh bc" > /dev/null

    # Kick off the tasks
    $RUN ./cpu_benchmark.py

    # Copy results to file for this iteration...
    remoterunall "cp $RESULTS_FILE $RESULTS_FILE.$UNIQ.$ITER" > /dev/null

    # Done! Now run another raeps...
    remoterun cn72 "$RAEPCMD" > /dev/null
    remoterun cn73 "$RAEPCMD" > /dev/null
done

# Bundle up the results for easier scp'ing later.
#remoterunall $BUNDLECMD

# Copy results and commit them.
RES_DIR=/opt/results/eval-$UNIQ/
mkdir -p $RES_DIR
for i in `seq 1 9`
do
    mkdir -p $RES_DIR/$i
    scp hadoop$i:"$RESULTS_FILE.$UNIQ*" $RES_DIR/$i/
done

cd /opt/results
git add $RES_DIR
git commit -a -m "Automatic commit of eval-$UNIQ"
git push origin master
