#!/bin/bash

# Kill current running processes
pkill -ef "main.py"
pkill -ef "gulp"
pkill -ef "browser"

# Pull latest from git
cd ~/itp/
#git fetch --all
#git reset --hard

# Start server
source ~/itp/server/venv/bin/activate

cd ~/itp/server/src
python -u main.py > ~/log/server.log 2>&1 &

# Start client
cd ~/itp/content
gulp > ~/log/client.log 2>&1 &

sleep 2

# Wait for client
#up=0
#while [ $up -eq 0 ]
#do
#  echo "Waiting for gulp..."
#  sleep 1
#  wget http://localhost:9002 -O - 2>/dev/null | grep "Grunt-Serve" > /dev/null && up=1
#done
