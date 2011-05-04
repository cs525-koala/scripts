#!/bin/sh

# Run this like 'watch -n2 ./virsh_monitor.sh' to monitor the VM's and where they actually are.
# Assumes public-key ssh access as root to the hosts.

HOSTS="cn71 cn72 cn73 cn74"
for i in $HOSTS;
do
  (ssh root@$i virsh list) | grep -v "Not running" | grep -v "\-\-\-" | grep -v "Id Name" |grep -v "^$" | awk "{printf \"($i): %s\n\", \$0}"
done

