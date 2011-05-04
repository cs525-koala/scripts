#!/usr/bin/python

import sys, re, time, subprocess
hadoop_home = "/usr/lib/hadoop"

#even though it is incorrect, we will accept numbers 256-999 for the sake of simplicity
ip_re = re.compile("(\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3})")

vm_startup_timeout = 3#00 #(5 min)
second_job_start_time = 1800 #(30 min)
third_job_start_time = 3600 #(60 min)

hadoop_instance_count = 8
hadoop_instance_start_command = "echo 'starting hadoop instance'"

ip_list = []

def isIP(potential_ip):
    if None == ip_re.search(potential_ip):
        return False
    else: 
        return True

def getIPstring(potential_ip):
    match = ip_re.search(potential_ip)
    if match == None:
        return None
    else:
        return match.group(1)


def printOutput(proc):
    (proc_stdout, proc_stderr) = (proc.stdout, proc.stderr)
    for line in proc_stdout:
        print line
    for line in proc_stderr:
        print "error: ", line

def getIPs():
    current_ip_list = []
    ip_proc = subprocess.Popen("ls /opt/hadoop_slave_ips", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    (proc_stdout, proc_stderr) = (ip_proc.stdout, ip_proc.stderr)
    for line in proc_stdout:
        if isIP(line):
            current_ip_list.append(getIPstring(line))
            print "ip found: ", getIPstring(line)
        else:
            print "invalid ip: ", line
    for line in proc_stderr:
        print "error: ", line
    return current_ip_list


#MAIN EXECUTION

#clear old data
#  clear old ip files <disabled for testing>
#rm_ipfile_proc = subprocess.Popen("rm /opt/hadoop_slave_ips/*")
#  clear old slaves file
clear_proc = subprocess.Popen("echo '' > " + hadoop_home + "/hadoop/conf/slaves", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
printOutput(clear_proc)


#get time
start_time = time.gmtime()

#start hadoop vm's
for count in range(hadoop_instance_count):
    print "starting hadoop instance ", count
    hadoop_start_proc = subprocess.Popen(hadoop_instance_start_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    printOutput(hadoop_start_proc)


#collect ips for vm_startup_timeout time
#  first, sleep for that length
time.sleep(vm_startup_timeout)

#  note that the vms will copy a file with their ip address to /opt/hadoop_slave_ips
#  parse these and add the ips to a list
print "finding slave ips"
ip_list = getIPs()

#  put those ips in the hadoop_home/conf/slaves file
for ip in ip_list:
    ip_cat_proc = subprocess.Popen("echo '" + ip + "' >> " + hadoop_home + "/conf/slaves", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    printOutput(ip_cat_proc)

#  copy slaves file to the instances
for ip in ip_list:
    print "copying slaves file to: ", ip
    scp_slave_proc = subprocess.Popen("scp " + hadoop_home + "/conf/slaves " + ip + ":" + hadoop_home + "/conf/slaves", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    printOutput(scp_slave_proc)

#launch hadoop job
hadoop_init_proc = subprocess.Popen(hadoop_home + "/restart_stuff.sh", shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
hadoop_init_proc.communicate("Y")
printOutput(hadoop_init_proc)

hadoop_job_proc = subprocess.Popen(hadoop_home + "/bin/hadoop jar " + hadoop_home + "



#after second_job_start_time has elapsed, start second job


#after third_job_start_time has elapsed, start third job
