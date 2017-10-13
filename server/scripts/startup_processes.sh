#!/bin/bash

export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh

# Kill current running processes
pkill -ef "main.py"
pkill -ef "grunt"

# Pull latest from git
cd ~/itp/
git fetch --all
git reset --hard

# Start server
cd ~/itp/server/src
source venv/bin/activate
python -u main.py > ~/log/server.log 2>&1 &

# Start client
cd ~/itp/Client
grunt run > ~/log/client.log 2>&1 &

# Wait for client
up=0
while [ $up -eq 0 ]
do
  echo "Waiting for grunt..."
  sleep 1
  wget http://localhost:9002 -O - 2>/dev/null | grep "Grunt-Serve" > /dev/null && up=1
done
