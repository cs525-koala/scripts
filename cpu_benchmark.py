#!/usr/bin/python

#It is assumed that this script is run only on mosyg and only as root

import sys, re, datetime, time, subprocess, ping, socket, threading

run_without_eucalyptus = False

start_time_multiplier = 5
# start time base, [instance number, duration (exponent)]
# start time base are randomly generated ints between 0 and 18 (random ints between 1 and 20 minus 2, so it starts immediately)
cpu_task_values = dict(((2, [1,24]),
                        (15, [2,24]),
                        (1, [3,24]),
                        (6, [4,24]),
                        (3, [5,24]),
                        (0, [6,24]),
                        (5, [7,24]),
                        (11, [8,24]),
                        (9, [9,24])))
                        
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
    cpu_task_cmd = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no hadoop" + str(instance_number) + " /opt/cpu_bench.sh"
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
    print "spawning a cpu benchmark task on hadoop" + str(cpu_task_values[start_time][0])", which will begin in", start_time * start_time_multiplier, "seconds"
    t.start()


