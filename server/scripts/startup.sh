#!/bin/bash

# Show splash
feh -F ~/itp/server/src/resources/splash.png & feh_pid=$!
wait $feh_pid

# Run processes script
./startup_processes.sh

# Start the browser
~/kiosk-browser/browser http://localhost:9002/content/Startup/index.html & browser_pid=$!

sleep 2
kill -9 $feh_pid

wait $browser_pid
