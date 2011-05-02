#!/bin/sh

(while [ 1 ];
do
	ping -c1 -s1 mosyg.cs.uiuc.edu
	sleep 1
done) 2>&1 > /dev/null &
