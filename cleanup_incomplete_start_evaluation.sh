#!/bin/sh

# Run this after ctrl-C'ing start_evaluation.py

# Where am I?
DIR=$(dirname $(readlink -f $0))

# Restore the hosts file
cp /etc/hosts.golden /etc/hosts

# Kill all instances
$DIR/terminate_all.sh
