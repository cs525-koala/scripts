#!/usr/bin/python

#It is assumed that this script is run only on mosyg and only as root

import sys, re, time, subprocess, ping, socket

run_without_eucalyptus = False

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

hadoop_instance_count = 9
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

def start_instances(instance_count, instance_name, instance_type="m1.xlarge"):
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






# MAIN EXECUTION



# get time

script_start_time = prettyTime()
print "\nscript starting: ", script_start_time




# clear old slaves file & temp hosts file

clear_slaves_cmd = "echo -n '' > " + hadoop_home + "/conf/slaves"
clear_slaves_proc = subprocWrapper(clear_slaves_cmd)
printOutput(clear_slaves_proc)

clear_temp_hosts_cmd = "echo '128.174.241.209 mosyg' > " + hosts_working_temp_dir + "/hosts"
clear_temp_hosts_proc = subprocWrapper(clear_temp_hosts_cmd)
printOutput(clear_temp_hosts_proc)




# for sanity, check (and track) what if any instances are running on startup

global_instance_list = getAllInstanceIds()




# get time

start_time = prettyTime()
print "\nstarting eval: ", start_time




# start hadoop instances & record instance ids 

print "\nstarting ", hadoop_instance_count, " hadoop instances"
hadoop_instance_list = start_instances(hadoop_instance_count, "hadoop")
if not len(hadoop_instance_list) == hadoop_instance_count:
    print "error, only", len(hadoop_instance_list), "of", hadoop_instance_count, "hadoop instances started, quitting"
    sys.exit(-1)
global_instance_list.extend(hadoop_instance_list)




#  parse euca-describe-instances for hadoop ips

print "\ngetting hadoop_ips"
hadoop_ip_list = getInstanceIPs(hadoop_instance_list)
if not len(hadoop_instance_list) == len(hadoop_ip_list):
    print "error, only", len(hadoop_ip_list), "of", len(hadoop_instance_list), "hadoop ips found, quitting"
    sys.exit(-1)
global_ip_list.extend(hadoop_ip_list)




# wait for hadoop instances to start

#  first, sleep 
print "waiting for", hadoop_instance_count, "hadoop instances to come up"
wait_for_instances(hadoop_ip_list, hadoop_instance_count)




# get time

hadoop_instance_ready_time = prettyTime()
print "\nhadoop instances ready: ", hadoop_instance_ready_time




#  generate /etc/hosts and hadoop/conf/slaves files

print "\ngenerating slaves file from hadoop instances' ips"
hadoop_instance_number = 1
for ip in hadoop_ip_list:
    hostname = "hadoop" + str(hadoop_instance_number)
    print "adding: \"" + ip + " " + hostname + "\" to hosts"
    hosts_echo_cmd = "echo '" + ip + " " + hostname + "' >> " + hosts_working_temp_dir + "/hosts"
    hosts_echo_proc = subprocWrapper(hosts_echo_cmd)
    printOutput(hosts_echo_proc)

    print "adding: \"" + hostname + "\" to conf/slaves"
    slaves_echo_cmd = "echo '" + hostname + "' >> " + hadoop_home + "/conf/slaves"
    slaves_echo_proc = subprocWrapper(slaves_echo_cmd)
    printOutput(slaves_echo_proc)
    
    hostname_dict[ip] = hostname
    hadoop_instance_number += 1




# print these files for sanity 

print "\n\n**************** HOSTS FILE *****************"
cat_hosts_cmd = "cat " + hosts_working_temp_dir + "/hosts"
cat_hosts_proc = subprocWrapper(cat_hosts_cmd)
printOutput(cat_hosts_proc)

print "\n\n**************** SLAVES FILE *****************"
cat_slaves_cmd = "cat " + hadoop_home + "/conf/slaves"
cat_slaves_proc = subprocWrapper(cat_slaves_cmd)
printOutput(cat_slaves_proc)




# backup & generage  mosyg's hosts

print "backing up mosyg's hosts"
mosyg_backup_hosts_cmd = "cp /etc/hosts /etc/hosts.bak"
if not run_without_eucalyptus:
    mosyg_backup_hosts_proc = subprocWrapper(mosyg_backup_hosts_cmd)
    printOutput(mosyg_backup_hosts_proc)

print "adding hadoop nodes to mosyg's hosts"
mosyg_new_hosts_cmd = "cat " + hosts_working_temp_dir + "/hosts >> /etc/hosts"
if not run_without_eucalyptus:
    mosyg_new_hosts_proc = subprocWrapper(mosyg_new_hosts_cmd)
    printOutput(mosyg_new_hosts_proc)




# copy hosts & slaves files to the instances
# ALSO tell them their hostname 

print "\ncopying hosts and slaves files to instances"
for ip in hadoop_ip_list:
    print "\ncopying hosts file to: ", ip
    scp_hosts_cmd = "scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no " + hosts_working_temp_dir + "/hosts " + ip + ":" + "/etc/hosts"
    if run_without_eucalyptus:
        print "debug mode, running: " + scp_hosts_cmd
    else:
        scp_hosts_proc = subprocWrapper(scp_hosts_cmd)
        printOutput(scp_hosts_proc)
    print "setting hostname for: ", ip
    scp_hostname_cmd = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no " + ip + " hostname " + hostname_dict[ip]
    if run_without_eucalyptus:
        print "debug mode, running: " + scp_hostname_cmd
    else:
        scp_hostname_proc = subprocWrapper(scp_hostname_cmd)
        printOutput(scp_hostname_proc)
    print "copying slaves file to: ", ip
    scp_slave_cmd = "scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no " + hadoop_home + "/conf/slaves " + ip + ":" + hadoop_home + "/conf/slaves"
    if run_without_eucalyptus:
        print "debug mode, running: " + scp_slave_cmd
    else:
        scp_slave_proc = subprocWrapper(scp_slave_cmd)
        printOutput(scp_slave_proc)




# get time

hosts_ready_time = prettyTime()
print "\nhosts and slaves files for instances ready: ", hosts_ready_time

