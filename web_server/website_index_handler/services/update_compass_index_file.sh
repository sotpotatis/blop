#!/usr/bin/env bash
#Updates the Compass index file, which is usually the start page of a blop implementation
cd /srv/blop/web_server/website_index_handler || (echo "Failed to cd into target directory for compass." && exit 1)
python3 index_file_generator.py