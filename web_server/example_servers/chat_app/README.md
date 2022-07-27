![veronica logo](veronica-logo.png)
## a simple chat app for the terminal*
with support for different channels

**=when using together with the superbrain Telnet client*

### hosted version
available at `telnetchat.albins.website`

### screenshots

### host your own

*manual install*
* `pip install -r requirements.txt`
* `python3 create_database.py`
* local web server (do not use in production!!!): `python3 serve_app.py`
* production wsgi server: `gunicorn create_app:create_app()`

*systemctl*
* follow steps 1-2 under "manual install"
* `sudo mv services/run_veronica.service /etc/systemd/system/run_veronica.service`
* `sudo mv services/run_veronica.sh /srv/run_veronica.sh`
* `sudo chmod +x /srv/run_veronica.sh`
* `sudo systemctl start run_veronica` to start server
* `sudo systemctl status run_veronica` to check server status
* `sudo systemctl enable run_veronica` to enable server on startup
