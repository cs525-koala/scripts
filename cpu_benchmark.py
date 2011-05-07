#!/usr/bin/python

#It is assumed that this script is run only on mosyg and only as root

import sys, re, time, subprocess, ping, socket, threading

run_without_eucalyptus = False

start_time_multiplier = 25
# start pos, [instance number, duration (exponent)]
cpu_task_values = dict(((0, [4,23]),
                        (1, [8,23]),
                        (2, [3,23]),
                        (3, [6,23]),
                        (4, [9,23]),
                        (5, [7,23]),
                        (6, [1,23]),
                        (7, [5,23]),
                        (8, [2,23])))
                        
def prettyTime():
    return time.strftime('%x: %X', time.gmtime())

def printOutput(proc):
    (proc_stdout, proc_stderr) = (proc.stdout, proc.stderr)
    for line in proc_stdout:
        print line
    for line in proc_stderr:
        print "error: ", line

def subprocWrapper(command):
    return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)

def cpu_task(instance_number, exponent):
    print "starting job with exponent", exponent, "on hadoop"+str(instance_number)
    cpu_task_cmd = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no hadoop" + str(instance_number) + " \"echo '2^2^" + str(exponent) + "' | bc >/dev/null\""
    if run_without_eucalyptus:
        print "debug mode, running: " + cpu_task_cmd
    else:
        cpu_task_proc = subprocWrapper(cpu_task_cmd)
        printOutput(cpu_task_proc)

# MAIN EXECUTION

#

# get time

start_eval_time = prettyTime()
print "\nstarting evaluation: ", start_eval_time

for start_time in cpu_task_values:
    #may need to ad an import for timer
    t = threading.Timer(start_time * start_time_multiplier , cpu_task, [cpu_task_values[start_time][0],cpu_task_values[start_time][1]])
    t.start()


