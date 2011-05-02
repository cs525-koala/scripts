#!/usr/bin/python

import sys, re, time, subprocess

#even though it is incorrect, we will accept numbers 256-999 for the sake of simplicity
ip_re = re.compile(".*(\d{1,3}:\d{1,3}:\d{1,3}:\d{1,3}).*")

vm_startup_timeout = 300 #(5 min)
second_job_start_time = 1800 #(30 min)
third_job_start_time = 3600 #(60 min)

hadoop_instance_count = 8
hadoop_instance_start_command = "echo 'starting hadoop instance'"

ip_list = []

def isIP(potential_ip):
    if None == ip_re.match(potential_ip):
        return False
    else: 
        return True

def getIP(potential_ip):
    match = ip_re.match(potential_ip)
    if match == None:
        return None
    else:
        return match.group(1)


#MAIN EXECUTION

#get time
start_time = time.gmtime()

#start hadoop vm's
for count in range(hadoop_instance_count):
    print "starting hadoop instance ", count
    hadoop_start_proc = subprocess.Popen(hadoop_instance_start_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    (sub_stdout, sub_stderr) = (hadoop_start_proc.stdout, hadoop_start_proc.stderr)
    for line in sub_stdout:
        print line
    for line in sub_stderr:
        print "error: ", line


#collect ips for vm_startup_timeout time
#  first, sleep for that length
time.sleep(vm_startup_timeout)

#  note that the vms will copy a file with their ip address to /opt/hadoop_slave_ips
#  parse these and add the ips to a list
ip_proc = subprocess.Popen("ls /opt/hadoop_slave_ips", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
(sub_stdout, sub_stderr) = (ip_proc.stdout, ip_proc.stderr)
for line in sub_stdout:
    if isIP(line):
        ip_list.append(getIP(line))
        print "ip found: ", getIP(line)
    else:
        print "invalid ip: ", line
for line in sub_stderr:
    print "error: ", line

#  clear old slaves file
clear_proc = subprocess.Popen("echo '' > /usr/lib/hadoop/conf/slaves")

#  put those ips in the /usr/lib/hadoop/conf/slaves file
for ip in ip_list:
    ip_cat_proc = subprocess.Popen("echo'" + ip + "' >> /usr/lib/hadoop/conf/slaves", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    (sub_stdout, sub_stderr) = (ip_cat_proc.stdout, ip_cat_proc.stderr)
    for line in sub_stdout:
        print line
    for line in sub_stderr:
        print "error: ", line



#launch hadoop job
#  first setup slave ips



#after second_job_start_time has elapsed, start second job


#after third_job_start_time has elapsed, start third job
