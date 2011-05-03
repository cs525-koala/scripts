#!/bin/sh

# Go through the cmdlines (often taking form key=value)
# Exporting them to our environment, ignoring errors.
# TODO: Make this less hacky and actually parse out
# the 'MYIP=IP' part
# However, this works for now.
for i in `cat /proc/cmdline`;
do
  export $i
done

# Use the MYIP boot parameter to configure our network
ifconfig eth0 $MYIP

# Default gw on the CCT, from cn71
route add default gw 172.22.28.7

# Some DNS goodness to get us going, mostly from cn71
echo "search cloud.cs.illinois.edu" > /etc/resolv.conf
echo "nameserver 128.174.252.4" >> /etc/resolv.conf
echo "nameserver 128.174.252.5" >> /etc/resolv.conf
echo "nameserver 4.2.2.1" >> /etc/resolv.conf
