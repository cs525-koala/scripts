#!/bin/sh
# To be run on each nc that to be bounced...

# Figure out where we really are
DIR=`dirname $0`
DIR=`cd $DIR;pwd -P`
cd $DIR

# Setup environment variables
. ./setup_vars

# Stop any running NC
$EUCALYPTUS/etc/init.d/eucalyptus-nc stop

# Reconfigure and make sure permissions are peachy...
$EUCALYPTUS/usr/sbin/euca_conf -d $EUCALYPTUS --hypervisor kvm --instances /vm_images --user eucalyptus --setup --enable cloud --enable walrus --enable sc
chown eucalyptus -R $EUCALYPTUS
$EUCALYPTUS/usr/sbin/euca_conf -d $EUCALYPTUS --hypervisor kvm --instances /vm_images --user eucalyptus --setup --enable cloud --enable walrus --enable sc
$EUCALYPTUS/usr/sbin/euca_conf -d $EUCALYPTUS --setup

# Change 'xenbr0' to 'br0' in the config.
sed -i s/xenbr0/br0/ $EUCALYPTUS/etc/eucalyptus/eucalyptus.conf

# Finally, bounce the nc!
$EUCALYPTUS/etc/init.d/eucalyptus-nc start
