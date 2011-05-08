#!/bin/bash

PATTERN=$1

PIDS=`ps aux|grep $PATTERN|grep -v grep|awk '{print $2}'`

if [ "$PIDS" != "" ]
then
	#echo "Killing $PIDS that matched pattern $PATTERN..."
	kill -9 $PIDS
fi
