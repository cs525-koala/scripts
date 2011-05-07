#!/usr/bin/python

#It is assumed that this script is run only on mosyg and only as root

import sys, re, time, subprocess, ping, socket

run_without_eucalyptus = True

hadoop_home = "/usr/lib/hadoop"
hosts_working_temp_dir = "/tmp" #need somewhere to make a temp hosts file

# even though it is incorrect, we will accept numbers 256-999 for the sake of simplicity
ip_re = re.compile("(\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3})")
dfs_re = re.compile("Datanodes available: (\d+) [(]\d+ total, \d+ dead[)]")

# currently unused
# TODO fix this
second_job_start_time = 1800 #(30 min)
third_job_start_time = 3600 #(60 min)

vm_emi = "emi-DBEE158C"

hadoop_instance_count = 8
hadoop_instance_list = [] #"instance" as use here, refers to a unique instance id representing the instance
hadoop_ip_list = []

disk_instance_count = 8
disk_instance_list = [] #"instance" as use here, refers to a unique instance id representing the instance
disk_ip_list = []

cpu_instance_count = 8
cpu_instance_list = [] #"instance" as use here, refers to a unique instance id representing the instance
cpu_ip_list = []

global_instance_list = []
global_ip_list = [] #idk why, might as well track it

hostname_dict = {}

# 1/10th of start time, [instance number, duration (exponent)]
cpu_task_values = dict(((0, [4,23]),
                        (1, [8,23]),
                        (2, [3,23]),
                        (3, [6,23]),
                        (4, [0,23]),
                        (5, [7,23]),
                        (6, [1,23]),
                        (7, [5,23]),
                        (8, [2,23])))





def prettyTime():
    return time.strftime('%x: %X', time.gmtime())


def isPingable(address):
    try:
        delay = ping.do_one(address, timeout=1)
    except socket.error, e:
        print address, "not up"
        return False
    if delay > 0:
        return True
    else:
        print address, "not up"
        return False

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

def subprocWrapper(command):
    return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)


def getAllInstanceIds():
    new_instance_list = []
    ip_proc = subprocWrapper("euca-describe-instances")
    (proc_stdout, proc_stderr) = (ip_proc.stdout, ip_proc.stderr)
    for line in proc_stdout:
        word_list = line.split()
        if len(word_list) > 1 and word_list[0] == "INSTANCE":
            print "found instance: ", word_list[1] 
            new_instance_list.append(word_list[1])
        else:
            print "not an instance: ", line
    for line in proc_stderr:
        print "error: ", line
    return new_instance_list
    
def getIPs(instance_list):
    new_ip_list = []
    ip_proc = subprocWrapper("euca-describe-instances")
    (proc_stdout, proc_stderr) = (ip_proc.stdout, ip_proc.stderr)
    for line in proc_stdout:
        word_list = line.split()
        if len(word_list) > 1 and word_list[0] == "INSTANCE":
            print "ip: ", word_list[3], " found for instance: ", word_list[1] 
            if word_list[1] in instance_list:
                new_ip_list.append(word_list[3])
        else:
            print "not an instance: ", line
    for line in proc_stderr:
        print "error: ", line
    return new_ip_list

# must be called on the output of a subprocess.Popen of euca-run-instances
def getInstanceIds(proc):
    (proc_stdout, proc_stderr) = (proc.stdout, proc.stderr)
    new_instance_list = []
    for line in proc_stdout:
        word_list = line.split()
        if len(word_list) > 1 and word_list[0] == "INSTANCE":
            print "found id: ", word_list[1], " in: ", line
            new_instance_list.append(word_list[1])
        else:
            print "not an instance: ", line
    for line in proc_stderr:
        print line
    return new_instance_list

def hadoopInit():
    print "stopping everything"
    hadoop_stop_cmd = hadoop_home + "/bin/stop-all.sh"
    if run_without_eucalyptus:
        print "debug mode, running: " + hadoop_stop_cmd
    else:
        hadoop_stop_proc = subprocWrapper(hadoop_stop_cmd)
        printOutput(hadoop_stop_proc)
    
    print "clearing hdfs"
    hadoop_clear_hdfs_cmd = "rm -rf " + hadoop_home + "/hdfs/*"
    if run_without_eucalyptus:
        print "debug mode, running: " + hadoop_clear_hdfs_cmd
    else:
        hadoop_clear_hdfs_proc = subprocWrapper(hadoop_clear_hdfs_cmd)
        printOutput(hadoop_clear_hdfs_proc)

    print "clearing tmp"
    hadoop_clear_tmp_cmd = "rm -rf " + hadoop_home + "/tmp/*"
    if run_without_eucalyptus:
        print "debug mode, running: " + hadoop_clear_tmp_cmd
    else:
        hadoop_clear_tmp_proc = subprocWrapper(hadoop_clear_tmp_cmd)
        printOutput(hadoop_clear_tmp_proc)

    print "clearing logs"
    hadoop_clear_logs_cmd = "rm -rf " + hadoop_home + "/logs/*"
    if run_without_eucalyptus:
        print "debug mode, running: " + hadoop_clear_logs_cmd
    else:
        hadoop_clear_logs_proc = subprocWrapper(hadoop_clear_logs_cmd)
        printOutput(hadoop_clear_logs_proc)

    print "formatting namenode"
    hadoop_format_cmd = "echo 'Y' | " + hadoop_home + "/bin/hadoop namenode -format"
    if run_without_eucalyptus:
        print "debug mode, running: " + hadoop_format_cmd
    else:
        hadoop_format_proc = subprocWrapper(hadoop_format_cmd)
        printOutput(hadoop_format_proc)

    print "starting everything"
    hadoop_start_cmd = hadoop_home + "/bin/start-all.sh"
    if run_without_eucalyptus:
        print "debug mode, running: " + hadoop_start_cmd
    else:
        hadoop_start_proc = subprocWrapper(hadoop_start_cmd)
        printOutput(hadoop_start_proc)

def fix_mosyg_hosts():
    print "restoring mosyg's hosts"
    mosyg_rest_hosts_cmd = "cp /etc/hosts.bak /etc/hosts"
    if not run_without_eucalyptus:
        mosyg_rest_hosts_proc = subprocWrapper(mosyg_rest_hosts_cmd)
        printOutput(mosyg_rest_hosts_proc)

def kill_instances(instance_list, instance_type):
    print "\ncleaning up: killing " + instance_type + " instances"
    for instance in instance_list:
        print "killing instance: ", instance
        if run_without_eucalyptus:
            print "debug mode, killed instance: ", instance
        else:
            instance_kill_proc = subprocWrapper("euca-terminate-instances " + instance)
            printOutput(instance_kill_proc)

def wait_for_instances(ip_list, instance_number):
    if not run_without_eucalyptus:
        print "\nallowing instances 30 seconds to start"
        time.sleep(30)
        instances_ready = False
        loop_count = 0
        while(not instances_ready):
            instance_ready_count = 0
            for ip in ip_list:
                if isPingable(ip):
                    instance_ready_count += 1
            if instance_ready_count == instance_number:
                print "instances ready"
                instances_ready = True
            else:
                loop_count += 1
                print "after " + str(loop_count * 30) + " seconds, instances not ready, sleeping another 30 seconds"
                time.sleep(30)

def wait_for_dfs_nodes(number):
    if not run_without_eucalyptus:
        print "\nallowing dfs 30 seconds to start"
        time.sleep(30)
        dfs_ready = False
        loop_count = 0
        while(not dfs_ready):
            dfs_count = -1
            check_dfs_cmd = "/usr/lib/hadoop/bin/hadoop dfsadmin -report"
            check_dfs_proc = subprocWrapper(check_dfs_cmd)
            (proc_stdout, proc_stderr) = (check_dfs_proc.stdout, check_dfs_proc.stderr)
            for line in proc_stdout:
                match = dfs_re.search(line)
                if not match == None:
                    dfs_count = int(match.group(1))
                    if number == dfs_count:
                        print str(dfs_count) + " of " + str(number) + " dfs nodes ready"
                        dfs_ready = True
            if(dfs_count == -1):
                print "bad regex"
            if(not dfs_ready):
                loop_count += 1
                print "after " + str(loop_count * 30) + " seconds, " + str(number - dfs_count) + " dfs nodes not ready, sleeping another 30 seconds"
                time.sleep(30)
    else:
        print "debug mode: nodes are ready"

def start_instances(instance_count, instance_name, instance_type="c1.medium"):
    instance_list = []
    instance_start_cmd = "euca-run-instances -n " + str(instance_count)+ " " + vm_emi + " -t " + instance_type
    if run_without_eucalyptus:
        print "debug mode, would run: ", instance_start_cmd
        print "adding fake instance ids to instance lists"
        for instance_number in range(instance_count):
            instance_list.append(instance_name + "_instance_" + str(instance_number))
    else:
        print "running: ", instance_start_cmd
        start_proc = subprocWrapper(instance_start_cmd)
        instance_list = getInstanceIds(start_proc)
    return instance_list

def getInstanceIPs(instance_list):
    #first sleep
    print "\ngiving koala 10 sec to start instances"
    if not run_without_eucalyptus:
        time.sleep(10)

    #scrape describe instances
    ip_list = []
    print "\ngetting ips from euca-describe-instances"
    if run_without_eucalyptus:
        print "debug mode, using fake ips"
        for instance_number in range(len(instance_list)):
            print "debug mode, adding ip: 1.1.1." + str(instance_number)
            ip_list.append("1.1.1." + str(instance_number))
    else:
        ip_list = getIPs(instance_list)
        print "\n ips: "
        print ip_list
    return ip_list

def cpu_task(instance_number, exponent):
    print "starting job with exponent", exponent, "on hadoop"+str(instance_number)
    cpu_task_cmd = "ssh hadoop" + str(instance_number) + " echo '2^2^" + str(exponent) + "' | bc >/dev/null"
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
    t = Timer(start_time * 10, cpu_task(task_values[0],task_values[1]))
    t.start()


