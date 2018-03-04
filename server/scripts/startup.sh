#!/bin/bash

# Disable screen blanking and screen saver
xset s off
xset s noblank
xset -dpms

# Show splash
feh -F ~/itp/server/src/resources/splash.png & feh_pid=$!

# Run processes script
~/itp/server/scripts/startup_processes.sh

# Start the browser
export LD_LIBRARY_PATH=/home/infodisplay/Qt/5.10.0/gcc_64/lib:$LD_LIBRARY_PATH

~/kiosk-browser/browser http://localhost:9002/index.html & browser_pid=$!

sleep 2
kill -9 $feh_pid

wait $browser_pid
