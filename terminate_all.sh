#!/bin/sh

# Archiving the command I used to tell euc to nuke all instances, jic it's useful
python `which euca-describe-instances` |grep i-|cut -f2|xargs python `which euca-terminate-instances`
