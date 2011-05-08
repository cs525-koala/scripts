#!/usr/bin/python

#It is assumed that this script is run only on mosyg and only as root

import sys, re, datetime, time, subprocess, ping, socket, threading

run_without_eucalyptus = False

start_time_multiplier = 10
# start time base, [instance number, duration (exponent)]
# start time base are randomly generated ints between 1 and 20
# random order: seq 1 20 | sort -R
cpu_task_values = dict(((4,  [1, 24]),
                        (16, [2, 24]),
                        (11, [3, 24]),
                        (14, [4, 24]),
                        (15, [5, 24]),
                        (18, [6, 24]),
                        (7,  [7, 24]),
                        (12, [8, 24]),
                        (1,  [9, 24]),
                        (17, [10,24]),
                        (5,  [11,24]),
                        (9,  [12,24]),
                        (6,  [13,24]),
                        (2,  [14,24]),
                        (8,  [15,24])))

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
    task_start_time = prettyTime()
    print "\nAt ", task_start_time, "starting job with exponent", exponent, "on hadoop"+str(instance_number)
    cpu_task_cmd = "ssh -q -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no hadoop" + str(instance_number) + " \"/opt/cpu_bench.sh & \""
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
    print "spawning a cpu benchmark task on hadoop" + str(cpu_task_values[start_time][0]) + ", which will begin in", start_time * start_time_multiplier, "seconds"
    t.start()


