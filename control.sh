#!/bin/bash
# Cycle modelr-server with a rebuild of the project

#Check to see if at least one argument was specified
if [ $# -lt 1 ] ; then
   echo "You must specify at least 1 argument."
   exit 1
fi

#Process the arguments
while [ $# -gt 0 ]
do
   case "$1" in
      stop ) ps aux | grep "modelr-server -p " | grep -v "grep" | awk '{print $2}' | xargs kill -9
             echo Killed server
             break
        ;;
      clean ) python setup.py clean --all > modelr-server.log 2>&1
              echo Cleaned build
              break
        ;;
      start ) python setup.py clean --all > modelr-server.log 2>&1
              echo Cleaned build
              python setup.py install >> modelr-server.log 2>&1
              echo Compiled latest version
              nohup modelr-server -p 8081 >> modelr-server.log 2>&1 &
              echo Started server
              break
        ;;
      cycle ) ps aux | grep "modelr-server -p " | grep -v "grep" | awk '{print $2}' | xargs kill -9
              echo Killed server
              python setup.py clean --all > modelr-server.log 2>&1
              echo Cleaned build
              python setup.py install >> modelr-server.log 2>&1
              echo Compiled latest version
              nohup modelr-server -p 8081 >> modelr-server.log 2>&1 &
              echo Re-started server
              break
        ;;
      * ) echo "`basename ${0}`:usage: ./control.sh [start] | [stop] | [cycle] | [help]" 
          exit 1 # Command to come out of the program with status 1
        ;;
   esac
done
