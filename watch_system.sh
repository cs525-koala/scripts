#!/bin/bash

# virt-monitor-like output, using CCclient, euca-describe-intances, and our perf mon
# Run in watch probably

CCINST_CMD=" /tmp/CCclient_full localhost:8774 describeInstances"

NCS="cn71 cn72 cn73"

# Get list of running instances...
python $(which euca-describe-instances) > /tmp/desc
INSTIDS=$(cat /tmp/desc | grep i- | grep running | cut -f2)

$CCINST_CMD >& /tmp/ccinst

for n in $NCS;
do
    echo -n "$n:	"

    NIP=$(nslookup $n.cloud.cs.illinois.edu | grep Address | tail -n 1 | cut -d " " -f 2)
    grep $NIP /tmp/monitor.config

    for i in $INSTIDS;
    do
        grep $i /tmp/ccinst | grep $n >& /dev/null && (echo -n "	"; grep $i /tmp/monitor.config)
    done
done

