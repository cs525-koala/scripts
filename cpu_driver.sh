#!/bin/bash

# Drive cpu_bench scripts...

# We make all kinds of assumptions about state/things working/etc :)
# Assume hadoop1 <-->hadoop15 are running, all set up, etc.

#TODO: Increase offset times in cpu_benchmark.py? (LATER!)

ITERS=2

INSTCOUNT=15
RESULTS_FILE=/opt/cpu_bench_times

RAEPCMD="nohup /opt/cpu_raep.sh >& /dev/null < /dev/null &"
BUNDLECMD="tar cvf $RESULTS_FILE.$UNIQ.tar $RESULTS_FILE.$UNIQ.*"

SSH_OPT="-o BatchMode=yes -o ConnectTimeout=60"
SSH_OPT="$SSH_OPT -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

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

    SSH="ssh -q -q $SSH_OPT"
    RESULT=$($SSH root@$HOST "$RUN $CMD")

    echo $RESULT
}

function remoterunall() {
    CMD=$1

    for i in `seq 1 $INSTCOUNT`
    do
        remoterun hadoop$i "$CMD"
    done
}

function getidforindex() {
    INDEX=$1

    IP=$(grep hadoop$INDEX$ /etc/hosts | cut -d" " -f1)
    INDEX_INST_ID=$(cat /tmp/desc_driver | grep $IP | cut -f2)

    echo $INDEX_INST_ID
}

function disable_scheduler() {
    echo "Disabling the scheduler..."
    echo -en "30\n0\n0" > /tmp/sched.config
}

function enable_scheduler() {
    echo "Enabling the scheduler..."
    echo -en "30\n4\n1" > /tmp/sched.config
}

function enable_manual_scheduler() {
    echo "Enabling the MANUAL scheduler..."
    echo -en "30\n5\n1" > /tmp/sched.config
}

function fix_instance_ordering() {
    # Here's some fun: use migration to fix the ordering to be the same at every run start!
    # So we have three nc's... 5 go to each.

    # For now just assume even number...
    let NCCOUNT=INSTCOUNT/3

    let CURINST=0

    python $(which euca-describe-instances) > /tmp/desc_driver
    INSTIDS=$(cat /tmp/desc_driver | grep i- | grep running | cut -f2)

    NCS="172.22.28.81 172.22.28.82 172.22.28.83"

    echo -n > /tmp/sched.manual

    for n in $NCS
    do
        for i in `seq 1 $NCCOUNT`
        do
            let CURINST=CURINST+1

            INSTID=$(getidforindex $CURINST)
            DEST=$n

            echo "Putting $INSTID ($CURINST) on $DEST..."
            echo "$INSTID $DEST" >> /tmp/sched.manual
        done
    done

    enable_manual_scheduler

    # Wait until scheduler informs us that it's done...
    DONE=0
    while [ $DONE -eq 0 ]
    do
        sleep 10
        # TODO: Check some output from the scheduler...
    done
}

# Main Execution

# Provision the hosts with our killgrep command...
echo "Provisioning the hosts with our killgrep helper..."
for i in `seq 1 $INSTCOUNT`
do
    scp $SSH_OPT $PWD/killgrep.sh root@hadoop$i: >& /dev/null
done
scp $SSH_OPT $PWD/killgrep.sh cn72: >& /dev/null
scp $SSH_OPT $PWD/killgrep.sh cn73: >& /dev/null

# Make sure no rape tasks are running on the nc's...
echo "Killing raep tasks on the nc's..."
remoterun cn72 "./killgrep.sh cpu_raep" > /dev/null
remoterun cn72 "./killgrep.sh bc" > /dev/null

remoterun cn73 "./killgrep.sh cpu_raep" > /dev/null
remoterun cn73 "./killgrep.sh bc" > /dev/null

# Make sure the instances are clean
echo "Killing load tasks on the instances..."
remoterunall "./killgrep.sh cpu_bench" > /dev/null
remoterunall "./killgrep.sh cpu_task" > /dev/null
remoterunall "./killgrep.sh bc" > /dev/null

# Ensure instances are where they should be...
disable_scheduler
sleep 5

fix_instance_ordering

exit 1

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
for i in `seq 1 $INSTCOUNT`
do
    mkdir -p $RES_DIR/$i
    scp hadoop$i:"$RESULTS_FILE.$UNIQ*" $RES_DIR/$i/
done

cd /opt/results
git add $RES_DIR
git commit -a -m "Automatic commit of eval-$UNIQ"
git push origin master
