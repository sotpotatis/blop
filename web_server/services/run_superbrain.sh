#!/usr/bin/bash
#Runs the Superbrain Telnet server for blop.
export TELNET_SERVER_HOST="0.0.0.0"
export TELNET_SERVER_PORT="23"
cd /srv/blop/web_server || echo "Failed to CD into working directory" && exit 1
echo "Running server..."
python3 server.py