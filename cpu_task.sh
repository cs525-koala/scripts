#!/bin/sh
echo '2^2^24' | bc > /dev/null
echo -n "completed at" >> /opt/cpu_bench_times
date >> /opt/cpu_bench_times