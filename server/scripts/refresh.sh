#!/bin/bash

# Start processes
./startup_processes.sh

# Refresh browser
ps -ef | grep browser | grep -v grep | awk '{print $2}' | xargs kill -HUP
