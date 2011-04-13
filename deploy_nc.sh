#!/bin/sh -e

#TODO: This should be run from the eucalyptus source tree!

# Figure out where we really are
CANON=`readlink -f $0`
DIR=`dirname $CANON`
cd $DIR

# Setup environment variables
. ./setup_vars

# Sanity checks
if [[ $UID -ne 0 ]]; then
  echo "`basename $0` must be run as root"
  exit 1
fi

SCRIPTS=$EUCALYPTUS/scripts

#make install

OTHERS=""
OTHERS="$OTHERS cn72.cloud.cs.illinois.edu"
OTHERS="$OTHERS cn73.cloud.cs.illinois.edu"
OTHERS="$OTHERS cn74.cloud.cs.illinois.edu"


# Rsync updated $EUCALYPTUS tree to other nodes
for host in $OTHERS; do
  rsync --progress -e ssh -av $EUCALYPTUS/ root@$host:$EUCALYPTUS/
done

# Okay now restart the nc's on those hosts...
for host in $OTHERS; do
  ssh eucalyptus@$host $SCRIPTS/restart_nc.sh
done

