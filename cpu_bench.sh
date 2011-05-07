#!/bin/bash

echo -n "start time: " > /opt/cpu_bench_times
date >> /opt/cpu_bench_times
/opt/cpu_task.sh &
/opt/cpu_task.sh &