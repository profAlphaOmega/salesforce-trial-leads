#!/bin/sh


# Get configs
ENV=${ENV:-"dev"}
cd conf
source ./base.env
cd -
echo "Env variables:"
env | sort

# Start flask web application
twistd -n web --wsgi src.main.app --port tcp:8080