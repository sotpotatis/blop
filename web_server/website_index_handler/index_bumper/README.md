# index bumper

contains code that bumps up a website in the website index. useful for bumping up your own websites.

### usage

*installation*

`pip install -r requirements.txt`

*running*

**To register your website**

`python bumper.py "https://example.com" --title="Website title" --description="Website description."`

**To update your website**

use the token obtained from the output of running the registration script:

`python bumper.py "https://example.com" --token="<YOUR_TOKEN_HERE>" --title="Website title" --description="Website description."`

**For help**

run

`python bumper.py --help`

**Periodically running**

see the [services](services) directory for `systemd` services.