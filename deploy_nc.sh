#!/bin/sh -e

#TODO: Verify that EUCALYPTUS is set.
#TODO: Make sure the running user is root.
#TODO: This should be run from the eucalyptus source tree!

make install
$EUCALYPTUS/usr/sbin/euca_conf -d $EUCALYPTUS --hypervisor kvm --instances /vm_images --user eucalyptus --setup --enable cloud --enable walrus --enable sc
chown eucalyptus -R $EUCALYPTUS
$EUCALYPTUS/usr/sbin/euca_conf -d $EUCALYPTUS --hypervisor kvm --instances /vm_images --user eucalyptus --setup --enable cloud --enable walrus --enable sc
$EUCALYPTUS/usr/sbin/euca_conf -d $EUCALYPTUS --setup

# Change 'xenbr0' to 'br0' in the config.
sed -i s/xenbr0/br0/ $EUCALYPTUS/etc/eucalyptus/eucalyptus.conf

# Any other changes?
$EUCALYPTUS/etc/init.d/eucalyptus-nc restart
