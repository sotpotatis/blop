#!/bin/bash
#Updates a website of your choice's bump status.
echo "Running script to bump website"
python3 /srv/blop/web_server/website_index_handler/index_bumper/bumper.py  "https://example.com" --token="<YOUR_TOKEN_HERE>" --title="Website title" --description="Website description."