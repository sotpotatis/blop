#!/usr/bin/env bash
#Runs the Compass server which handles the website index API that other people can interact with
cd /srv/blop/web_server/website_index_handler || (echo "Failed to cd into target directory for compass." && exit 1)
export WEBSITE_INDEX_HOST="0.0.0.0"
export WEBSITE_INDEX_PORT=80
export WEBSITE_INDEX_RUN_APP="False" #Because the app handling is being done by a WSGI server, in this case Gunicorn.
gunicorn main:app -b "$WEBSITE_INDEX_HOST:$WEBSITE_INDEX_PORT"