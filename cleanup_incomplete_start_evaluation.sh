#!/bin/sh

# Run this after ctrl-C'ing start_evaluation.py 
cp /etc/hosts.bak /etc/hosts

python `which euca-describe-instances` |grep -o "i-[a-fA-F0-9]*"|xargs -n1 python `which euca-terminate-instances`


