#!/usr/bin/python

import sys, re, time, subprocess
hadoop_home = "/usr/lib/hadoop"

#even though it is incorrect, we will accept numbers 256-999 for the sake of simplicity
ip_re = re.compile("(\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3})")

vm_startup_timeout = 3#00 #(5 min)
second_job_start_time = 1800 #(30 min)
third_job_start_time = 3600 #(60 min)

vm_emi = "emi-a8720fe6"

hadoop_instance_count = 1
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

#also updates global_instance_list
def getNewIPs():
    new_ip_list = []
    ip_proc = subprocWrapper("euca-describe-instances")
    (proc_stdout, proc_stderr) = (ip_proc.stdout, ip_proc.stderr)
    for line in proc_stdout:
        word_list = line.split()
        if len(word_list) > 1 and word_list[0] == "INSTANCE":
            print "ip: ", word_list[3], " found for instance: ", word_list[1] 
            if word_list[1] not in global_instance_list:
                new_ip_list.append(word_list[3])
                global_instance_list.append(word_list[1])
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
    hadoop_stop_cmd = hadoop_home + "/bin/stop-all.sh"
    hadoop_stop_proc = subprocWrapper(hadoop_stop_cmd)
    printOutput(hadoop_stop_proc)
    
    hadoop_clear_hdfs_cmd = "rm -rf " + hadoop_home + "/hdfs/*"
    hadoop_clear_hdfs_proc = subprocWrapper(hadoop_clear_hdfs_cmd)
    printOutput(hadoop_clear_hdfs_proc)

    hadoop_clear_tmp_cmd = "rm -rf " + hadoop_home + "/tmp/*"
    hadoop_clear_tmp_proc = subprocWrapper(hadoop_clear_tmp_cmd)
    printOutput(hadoop_clear_tmp_proc)

    hadoop_format_cmd = "echo 'Y' | " + hadoop_home + "/bin/hadoop namenode -format"
    hadoop_format_proc = subprocWrapper(hadoop_format_cmd)
    printOutput(hadoop_format_proc)

    hadoop_start_cmd = hadoop_home + "/bin/start-all.sh"
    hadoop_start_proc = subprocWrapper(hadoop_start_cmd)
    printOutput(hadoop_start_proc)



#MAIN EXECUTION

#clear old slaves file

clear_proc_command = "echo '' > " + hadoop_home + "/conf/slaves"
clear_proc = subprocWrapper(clear_proc_command)
printOutput(clear_proc)



#get time

start_time = time.gmtime()



#start hadoop vm's & record instance ids 

print "starting ", hadoop_instance_count, " hadoop VMs"
hadoop_instance_start_command = "euca-run-instances -n " + str(hadoop_instance_count)+ " " + vm_emi + " -t c1.medium"
print "running: ", hadoop_instance_start_command
hadoop_start_proc = subprocWrapper(hadoop_instance_start_command)
hadoop_instance_list = getInstanceIds(hadoop_start_proc)
global_instance_list.extend(hadoop_instance_list)



#collect ips for vm_startup_timeout time

#  first, sleep for that length
print "allowing vms ", vm_startup_timeout, " seconds to start"
time.sleep(vm_startup_timeout)



#  parse euca-describe-instances for new ips
print "getting slave ips from euca-describe-instances"
hadoop_ip_list = getNewIPs()
print hadoop_ip_list


#  put those ips in the hadoop_home/conf/slaves file
print "generating slaves file from hadoop instances' ips"
for ip in hadoop_ip_list:
    ip_cat_cmd = "echo '" + ip + "' >> " + hadoop_home + "/conf/slaves"
    ip_cat_proc = subprocWrapper(ip_cat_cmd)
    printOutput(ip_cat_proc)

print "hadoop instances:"
for instance in hadoop_instance_list:
    print instance

print "global instances:"
for instance in global_instance_list:
    print instance

for instance in hadoop_instance_list:
    print "killing instance: ", instance
    instance_kill_proc = subprocWrapper("euca-terminate-instances " + instance)
    printOutput(instance_kill_proc)
'''
#  copy slaves file to the instances
for ip in ip_list:
    print "copying slaves file to: ", ip
    scp_slave_cmd = "scp " + hadoop_home + "/conf/slaves " + ip + ":" + hadoop_home + "/conf/slaves"
    scp_slave_proc = subprocWrapper(scp_slave_cmd)
    printOutput(scp_slave_proc)

#set up hadoop
print "initializing hadoop"
hadoopInit()

#launch hadoop job
hadoop_randomwriter_job_string = hadoop_home + "/bin/hadoop jar " + hadoop_home + "/hadoop-0.20.2-examples.jar randomwriter random_data"
print "running hadoop job, with command: ", hadoop_randomwriter_job_string
hadoop_job_proc = subprocWrapper(hadoop_randomwriter_job_string)
printOutput(hadoop_job_proc)



#after second_job_start_time has elapsed, start second job


#after third_job_start_time has elapsed, start third job
'''
