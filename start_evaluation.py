#!/usr/bin/python

#It is assumed that this script is run only on mosyg and only as root

import sys, re, time, subprocess

run_without_eucalyptus = False

hadoop_home = "/usr/lib/hadoop"
hosts_working_temp_dir = "/tmp" #need somewhere to make a temp hosts file

#even though it is incorrect, we will accept numbers 256-999 for the sake of simplicity
ip_re = re.compile("(\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3})")

vm_startup_timeout = 300 #(5 min)
second_job_start_time = 1800 #(30 min)
third_job_start_time = 3600 #(60 min)

vm_emi = "emi-DBEE158C"

hadoop_instance_count = 2
#"instance" refers to a unique instance id representing the instance
hadoop_instance_list = [] 
hadoop_ip_list = []

global_instance_list = []


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

#must be called on the output of a subprocess.Popen of euca-run-instances
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



#MAIN EXECUTION


#clear old slaves file & temp hosts file

clear_slaves_cmd = "echo -n '' > " + hadoop_home + "/conf/slaves"
clear_slaves_proc = subprocWrapper(clear_slaves_cmd)
printOutput(clear_slaves_proc)

clear_temp_hosts_cmd = "echo '128.174.241.209 mosyg' > " + hosts_working_temp_dir + "/hosts"
clear_temp_hosts_proc = subprocWrapper(clear_temp_hosts_cmd)
printOutput(clear_temp_hosts_proc)





#for sanity, check (and track) what if any instances are running on startup

global_instance_list = getAllInstanceIds()





#get time

start_time = time.gmtime()




#start hadoop vm's & record instance ids 

print "starting ", hadoop_instance_count, " hadoop VMs"
hadoop_instance_start_cmd = "euca-run-instances -n " + str(hadoop_instance_count)+ " " + vm_emi + " -t c1.medium"
if run_without_eucalyptus:
    #DEBUG MODE 
    print "debug mode, would run: ", hadoop_instance_start_cmd
    print "adding fake instance ids to instance lists"
    for instance_number in range(hadoop_instance_count):
        hadoop_instance_list.append("hadoop_instance_" + str(instance_number))
else:
    print "running: ", hadoop_instance_start_cmd
    hadoop_start_proc = subprocWrapper(hadoop_instance_start_cmd)
    hadoop_instance_list = getInstanceIds(hadoop_start_proc)
global_instance_list.extend(hadoop_instance_list)



#collect ips for vm_startup_timeout time

#  first, sleep for that length
print "\nallowing vms ", vm_startup_timeout, " seconds to start"
time.sleep(vm_startup_timeout)



#  parse euca-describe-instances for new ips

print "\ngetting slave ips from euca-describe-instances"
if run_without_eucalyptus:
    print "debug mode, using fake ips"
    for instance_number in range(hadoop_instance_count):
        print "debug mode, adding ip: 1.1.1." + str(instance_number)
        hadoop_ip_list.append("1.1.1." + str(instance_number))
else:
    hadoop_ip_list = getIPs(hadoop_instance_list)
print "\nhadoop ips: "
print hadoop_ip_list



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
    
    hadoop_instance_number += 1

#TODO cleanly integrate this with mosygs hosts file

#print these files for sanity 

print "\n\n**************** HOSTS FILE *****************"
cat_hosts_cmd = "cat " + hosts_working_temp_dir + "/hosts"
cat_hosts_proc = subprocWrapper(cat_hosts_cmd)
printOutput(cat_hosts_proc)

print "\n\n**************** SLAVES FILE *****************"
cat_slaves_cmd = "cat " + hadoop_home + "/conf/slaves"
cat_slaves_proc = subprocWrapper(cat_slaves_cmd)
printOutput(cat_slaves_proc)



#  copy hosts & slaves files to the instances

print "\ncopying hosts and slaves files to instances"
for ip in hadoop_ip_list:
    print "\ncopying hosts file to: ", ip
    scp_hosts_cmd = "scp " + hosts_working_temp_dir + "/hosts " + ip + ":" + "/etc/hosts"
    if run_without_eucalyptus:
        print "debug mode, running: " + scp_hosts_cmd
    else:
        scp_hosts_proc = subprocWrapper(scp_hosts_cmd)
        printOutput(scp_hosts_proc)
    print "copying slaves file to: ", ip
    scp_slave_cmd = "scp " + hadoop_home + "/conf/slaves " + ip + ":" + hadoop_home + "/conf/slaves"
    if run_without_eucalyptus:
        print "debug mode, running: " + scp_slave_cmd
    else:
        scp_slave_proc = subprocWrapper(scp_slave_cmd)
        printOutput(scp_slave_proc)



#set up hadoop
print "initializing hadoop"
hadoopInit()

'''
#launch hadoop job
hadoop_randomwriter_job_string = hadoop_home + "/bin/hadoop jar " + hadoop_home + "/hadoop-0.20.2-examples.jar randomwriter random_data"
print "running hadoop job, with command: ", hadoop_randomwriter_job_string
hadoop_job_proc = subprocWrapper(hadoop_randomwriter_job_string)
printOutput(hadoop_job_proc)



#after second_job_start_time has elapsed, start second job


#after third_job_start_time has elapsed, start third job
'''

# dump useful information and clean up

print "\ninstance dump:"
print "\nhadoop instances:"
for instance in hadoop_instance_list:
    print instance

print "\nglobal instances:"
for instance in global_instance_list:
    print instance

print "\ncleaning up: killing instances"
for instance in hadoop_instance_list:
    print "killing instance: ", instance
    if run_without_eucalyptus:
        print "debug mode, killed instance: ", instance
    else:
        instance_kill_proc = subprocWrapper("euca-terminate-instances " + instance)
        printOutput(instance_kill_proc)

