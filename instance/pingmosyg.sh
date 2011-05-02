#!/bin/sh

# Fork off a thread that pings mosyg roughly every second.
# This keeps traffic FROM the node, so no matter where it is
# (say, after it just got migrated)
# the nc, the switch it's on, etc, all update accordingly.

# TODO: Be smarter and only do this kind of thing after
#       a migration, perhaps rig the nc to do it for us.
# TODO: It's possible libvirt/kvm/qemu does some of this already
#       (I didn't test extensively enough to find out)
(while [ 1 ];
do
  ping -c1 -s1 mosyg.cs.uiuc.edu
  sleep 1
done) 2>&1 > /dev/null &
