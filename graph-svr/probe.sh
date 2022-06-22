#!/bin/bash

dte=date

# Readiness check
if [[ "$1" == "readiness" ]] ; then
    portopen=`curl -ks --get curl -f localhost:4000/'
    if [[ $? -eq 0 ]]; then
        echo "$dte  failed curl on port"
        exit 0
    fi
    exit 1
fi

# Liveness check
if [[ "$1" == "liveness" ]] ; then
    portopen=`ss -ltn | grep 4000`
    if [[ $? -eq 0 ]]; then
        echo "$dte  port not open"
        exit 0
    fi
    echo "$dte  all good"
    exit 1
fi