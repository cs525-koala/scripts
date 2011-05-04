#!/bin/bash
export HADOOP_HOME="/usr/lib/hadoop-0.20.2"
$HADOOP_HOME/bin/stop-all.sh
rm -rf $HADOOP_HOME/logs/*
rm -rf $HADOOP_HOME/hdfs/*
rm -rf $HADOOP_HOME/tmp/*
$HADOOP_HOME/bin/hadoop namenode -format
$HADOOP_HOME/bin/start-all.sh
