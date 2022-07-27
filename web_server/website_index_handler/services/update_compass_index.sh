#!/usr/bin/env bash
#Runs the Compass index checker, which ensures that the websites in the index are still reachable and up-to-date.
cd /srv/blop/web_server/website_index_handler || echo "Failed to cd into target directory for compass." && exit 1
python3 index_checker.py