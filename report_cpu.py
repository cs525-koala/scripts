#!/usr/bin/env python

import time
from time import sleep
import subprocess

def subprocWrapper(command):
    return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)

def printOutput(proc):
    (proc_stdout, proc_stderr) = (proc.stdout, proc.stderr)
    for line in proc_stdout:
        print line
    for line in proc_stderr:
        print "error: ", line


cpu_utilization_list = []

cpu_count = 8 #TODO: replace with a scrape of /proc/cpuinfo

while True: #yup, only way out is kill
    ps_proc = subprocWrapper("ps -axo pcpu,cmd")
    (stdout,stderr) = (ps_proc.stdout,ps_proc.stderr)
    ps_cpu_sum = 0.0
    for line in stdout:
        words = line.split()
        if not words[1] == "/usr/bin/kvm" and not words[0] == "%CPU":
            ps_cpu_sum += float(words[0])
    if len(cpu_utilization_list) > 60:
        cpu_utilization_list.pop(0)
    cpu_utilization_list.append(ps_cpu_sum/8)

    total_sum = 0.0
    for cpu_sum in cpu_utilization_list:
        total_sum += cpu_sum
    avg_sum = total_sum/len(cpu_utilization_list)

    proc = subprocWrapper("echo '" + str(int(avg_sum)) + "' > /tmp/stats")
    printOutput(proc)
    sleep(1)

