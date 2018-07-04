#!/bin/bash

# Disable screen blanking and screen saver
xset s off
xset s noblank
xset -dpms

# Show splash
feh -F ~/itp/server/src/resources/splash.png & feh_pid=$!

# Roll logs
cp ~/log/client.log.1 ~/log/client.log.2
cp ~/log/client.log ~/log/client.log.1

cp ~/log/server.log.1 ~/log/server.log.2
cp ~/log/server.log ~/log/server.log.1

# Change camera settings
v4l2-ctl -c focus_auto=0
v4l2-ctl -c focus_absolute=0

#v4l2-ctl -c white_balance_temperature_auto=0
#v4l2-ctl -c white_balance_temperature=7500

#v4l2-ctl -c exposure_auto=1
#v4l2-ctl -c exposure_auto_priority=0
#v4l2-ctl -c exposure_absolute=200

# Run processes script
~/itp/server/scripts/startup_processes.sh

# Start the browser
export LD_LIBRARY_PATH=/home/infodisplay/Qt/5.10.0/gcc_64/lib:$LD_LIBRARY_PATH

~/kiosk-browser/browser http://localhost:9002/index.html & browser_pid=$!

# Hide mouse cursor when inactive
sleep 2
unclutter -idle 1 &

# Hide splash
kill -9 $feh_pid

# Activate browser window
xdotool mousemove 50 50 click 1

# Wait for browser to quit
echo "OK!"

wait $browser_pid
