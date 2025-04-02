#!/bin/bash
echo "Killing all Python processes on ports 5000-5010 and 8080..."
for port in 5000 5001 5002 5003 5004 5005 5006 5007 5008 5009 5010 8080
do
    pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        echo "Killing process $pid on port $port"
        kill -9 $pid
    fi
done
echo "Done!"
