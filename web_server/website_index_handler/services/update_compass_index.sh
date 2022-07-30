#!/usr/bin/env bash
#Runs the Compass index checker, which ensures that the websites in the index are still reachable and up-to-date.
export INVALID_RESPONSE_REMOVE_LIMIT=576 #How many failed access attempts to allow before removing a website from the index
export WEBSITE_UPDATE_REMOVE_LIMIT=1440 #How often a website must be updated before being removed from the index (in minutes)
cd /srv/blop/web_server/website_index_handler || (echo "Failed to cd into target directory for compass." && exit 1)
python3 index_checker.py