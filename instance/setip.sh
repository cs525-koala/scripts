#!/bin/sh

for i in `cat /proc/cmdline`;
do
	export $i
done

ifconfig eth0 $MYIP

route add default gw 172.22.28.7

echo "search cloud.cs.illinois.edu" > /etc/resolv.conf
echo "nameserver 128.174.252.4" >> /etc/resolv.conf
echo "nameserver 128.174.252.5" >> /etc/resolv.conf
echo "nameserver 4.2.2.1" >> /etc/resolv.conf
