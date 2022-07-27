![superbrain logo](superbrain-logo.png)

### a Telnet server for browsing and displaying an index of websites
combining the `skipper` translation engine and the `compass` website index into one.


#### run your own version

> **ℹ️ note:** for maximum compatibility with scripts, the easiest way to run your own version
> (if you want to use systemctl for example) is to clone the whole git repository to `/srv/blop`.

*set up superbrain*

requires:

* all the subfolders in this directory (including [skipper](content_renderer/README.md)) except for `example_servers` and `tests`.
`website_index_handler` is easiest to host at the same server as the superbrain, but techy people can
figure out how to run it somewhere else.

dependencies: 

`pip install -r requirements.txt`

**manually running**

environment variables:

* `TELNET_SERVER_HOST`: where to run the server. for example `localhost` or `0.0.0.0`
* `TELNET_SERVER_PORT`: what port to run the server on. for example `23`.

**systemctl**

* `cd web_server` from blop base directory
* `sudo mv services/run_superbrain.service /etc/systemd/system/run_superbrain.service` to copy service
* `sudo mv services/run_superbrain.sh /srv/run_superbrain.sh` to copy script
* `sudo nano /srv/run_superbrain.sh` and add environment variables (see "*manually running*")
* `sudo chmod +x /srv/run_superbrain.sh` to make script executable
* now, you probably want to install `compass` (under `website_index_handler`), see [compass readme](website_index_handler/README.md).
* `sudo systemctl start run_superbrain` to start server
* `sudo systemctl status run_superbrain` to check server status
* `sudo systemctl enable run_superbrain` to enable server on startup
