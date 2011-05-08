#!/usr/bin/env python

import time, datetime, subprocess
from datetime import datetime
from time import strptime

#add other runs here with format below <NOTE> it won't print them in this order, and I didn't want to waste time investigating it
#                        name             numbers
run_names_dict = dict((("dynamic-0_4",   [0, 4]),
                       ("vanilla-0_4",   [0, 4]),
                       ("dynamic-6_8",   [6, 8]),
                       ("vanilla-6_8",   [6, 8]),
                       ("dynamic-10_12", [10,12]),
                       ("vanilla-10_12", [10,12]),
                       ("dynamic-11_13", [11,13]),
                       ("vanilla-11_13", [11,13])))




instance_count = 15
root_dir = "/opt/kevin_checkout_results/results/"

#number is cpu load tasks + 1"


def printOutput(proc):
    (proc_stdout, proc_stderr) = (proc.stdout, proc.stderr)
    for line in proc_stdout:
        print line
    for line in proc_stderr:
        print "error: ", line

def subprocWrapper(command):
    return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)

for run_name in run_names_dict:
    print "\nfor setup: " + run_name
    result_name = "eval-" + run_name 
    result_dir = root_dir + result_name
    for run_number in run_names_dict[run_name]:
        run_time_sum = 0
        for instance_number in range(1,instance_count + 1):
#            print run_name, "running with", instance_number, "instances and", run_number, "number"
            cat_proc = subprocWrapper("cat " + result_dir + "/" + str(instance_number) + "/cpu_bench_times." + result_name + "." + str(run_number))
            (cat_proc_stdout, cat_proc_stderr) = (cat_proc.stdout, cat_proc.stderr)

#            print "cat " + result_dir + "/" + str(instance_number) + "/cpu_bench_times." + result_name + "." + str(run_number)

            start_time_string = ""
            end_time_string = ""


            for line in cat_proc_stdout:
#                print line
                start_string = line[0:5]
                if start_string == "start":
                    start_time_string = line[12:31] + " " +line[36:40]
                else:
                    end_time_string = line[12:31] + " " + line[36:40]

            start_time = time.strptime(start_time_string)
            end_time = time.strptime(end_time_string)

            run_time_delta = datetime.fromtimestamp(time.mktime(start_time)) - datetime.fromtimestamp(time.mktime(end_time))

            run_time =  86400 - run_time_delta.seconds #yea, it has timedelta as day = -1, seconds = something
#            print "instance:", instance_number, "run:", run_number, "took", run_time, "seconds"


            run_time_sum += run_time
        run_time_average = float(run_time_sum)/instance_count
        print "with", run_number - 1, "load tasks, the average of", instance_count, "instances is", run_time_average, "seconds(", run_time_average/60, "minutes)"

