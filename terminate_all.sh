#!/bin/sh

# Archiving the command I used to tell euc to nuke all instances, jic it's useful
python `which euca-describe-instances` |grep -o "i-[a-fA-F0-9]*"|xargs -n1 python `which euca-terminate-instances`
