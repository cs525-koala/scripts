#!/bin/sh -e

# Assume EUCALYPTUS variable is set
# This is for the frontend.
# If we want the frontend running a nc, uncomment the commented out lines
# Should be run as root in the eucalyptus source directory!

make install

##echo "Fixing xenbr0 -> br0 in eucalyptus.conf..."
##sed -i "s/xenbr0/br0/" $EUCALYPTUS/etc/eucalyptus/eucalyptus.conf || echo "Search/Replace failed, probably already fixed..."

echo "Reconfiguring eucalyptus, and fixing permissions..."
$EUCALYPTUS/usr/sbin/euca_conf  -d $EUCALYPTUS --hypervisor kvm --instances /vm_instances/ --user eucalyptus --setup
chown eucalyptus $EUCALYPTUS -R
$EUCALYPTUS/usr/sbin/euca_conf  -d $EUCALYPTUS --hypervisor kvm --instances /vm_instances/ --user eucalyptus --setup

echo "Stopping services..."
$EUCALYPTUS/etc/init.d/eucalyptus-cloud stop
$EUCALYPTUS/etc/init.d/eucalyptus-cc stop
##$EUCALYPTUS/etc/init.d/eucalyptus-nc stop

echo "Removing CC's cached state..."
rm $EUCALYPTUS/var/lib/eucalyptus/CC/*Cache || echo "No cache found, ignoring..."

echo "Reconfiguring eucalyptus, and fixing permissions...(again)"
$EUCALYPTUS/usr/sbin/euca_conf  -d $EUCALYPTUS --hypervisor kvm --instances /vm_instances/ --user eucalyptus --setup
chown eucalyptus $EUCALYPTUS -R
$EUCALYPTUS/usr/sbin/euca_conf  -d $EUCALYPTUS --hypervisor kvm --instances /vm_instances/ --user eucalyptus --setup

echo "Starting services..."
$EUCALYPTUS/etc/init.d/eucalyptus-cloud start
$EUCALYPTUS/etc/init.d/eucalyptus-cc start
##$EUCALYPTUS/etc/init.d/eucalyptus-nc start

