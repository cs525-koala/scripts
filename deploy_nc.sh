#!/bin/sh -e

#TODO: This should be run from the eucalyptus source tree!

# Figure out where we really are
SRC=$PWD
CANON=`readlink -f $0`
DIR=`dirname $CANON`
cd $DIR

SHARE=/project/IKB-341568/vm

# Setup environment variables
. ./setup_vars

# Sanity checks
if [[ $UID -ne 0 ]]; then
  echo "`basename $0` must be run as root"
  exit 1
fi

OTHERS=""
OTHERS="$OTHERS cn72.cloud.cs.illinois.edu"
OTHERS="$OTHERS cn73.cloud.cs.illinois.edu"
#OTHERS="$OTHERS cn74.cloud.cs.illinois.edu"

SCRIPTS=$EUCALYPTUS/scripts

make install -C $SRC

# Change 'xenbr0' to 'br0' in the config.
echo "Fixing xenbr0 -> br0 in eucalyptus.conf..."
sed -i "s/xenbr0/br0/" $EUCALYPTUS/etc/eucalyptus/eucalyptus.conf || echo "Search/Replace failed, probably already fixed..."

# Reconfigure and make sure permissions are peachy...
$EUCALYPTUS/usr/sbin/euca_conf -d $EUCALYPTUS --setup
$EUCALYPTUS/usr/sbin/euca_conf -d $EUCALYPTUS --hypervisor kvm --instances $SHARE --user eucalyptus --setup
chown eucalyptus -R $EUCALYPTUS
$EUCALYPTUS/usr/sbin/euca_conf -d $EUCALYPTUS --hypervisor kvm --instances $SHARE --user eucalyptus --setup

# Stop all the nc's
CMD="$EUCALYPTUS/etc/init.d/eucalyptus-nc stop"
for host in $OTHERS; do
  echo "Stopping NC on $host..."
  ssh root@$host $CMD || echo "Stopping failed, assuming because already stopped..."
done
# (Locally as well)
echo "Stopping local NC"
$CMD || echo "Stopping failed, assuming because already stopped..."

# Rsync updated $EUCALYPTUS tree to other nodes
for host in $OTHERS; do
  echo "Syncing with $host..."
  rsync --progress -e ssh -av $EUCALYPTUS/ root@$host:$EUCALYPTUS/ \
    --exclude var/log \
    --exclude var/run >& /tmp/$host.rsync.log || echo "Rsync failed, continuing anyway..."
done

# Okay now restart the nc's on those hosts...
CMD="$EUCALYPTUS/etc/init.d/eucalyptus-nc start"
for host in $OTHERS; do
  echo "Starting NC on $host..."
  ssh root@$host $CMD
done
# (Locally as well)
echo "Starting local NC"
$CMD

