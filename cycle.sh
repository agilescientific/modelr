#!/bin/bash
# Cycle modelr-server with a rebuild of the project

# Stop the server
ps aux | grep "modelr-server -p " | grep -v "grep" | awk '{print $2}' | xargs kill -9
echo Killed server process

# Clean the build
python setup.py clean --all > modelr-server.log 2>&1
echo Cleaned previous build

# Rebuild
python setup.py install >> modelr-server.log 2>&1
echo Built project

# Restart the server
nohup modelr-server -p 8081 >> modelr-server.log 2>&1 &
echo Starting server on port 8081