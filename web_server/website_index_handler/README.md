![compass logo](compass-logo.png)

### a website index handler

the start page of blop is a link directory to external websites that have
been registered.

compass is, as the name hints, an index handler that stores an index of websites
and constantly updates it to be up-to-date.


### using the api

to add a site to this directory, we expose an api.

**hosted version base url**

the hosted version is available at `compass.sweetpotato.online`. it controls the
index of `blop.sweetpotato.online`.

> **ℹ️ Note:** If you prefer looking at examples instead, see the "example_requests" directory in this folder.
> Those examples are intended to be imported in [Insomnia](https://insomnia.rest).
 
> **ℹ️ Note:** Examples available: There are scripts in the [index_bumper](index_bumper) directory to handle bumping your website
> in the index automatically (so you don't have to worry about it)

### how to add a website to the index

send a request to the server located at the `base url`:

##### [POST] /website data

(all examples below are POSTS to the same endpoint. simple and delicious!!!)

**add a website for the first time**

example payload:
```json
{"website url": "https://example com", "title":  "optional title", "description":  "optional description"}
```

you will receive a response like this:
```json
{"status":  "success", "token": "<token>"}
```

the `token` *must* be used to periodically update the website in the index.
if the website is not periodically updated, it will be removed from the index.
the limit depends on the server, but periodically pinging every day is enough for the hosted version.

**update a website**

your website must be periodically updated and the website url must be present in the payload
even if it hasn't changed.

example payload:
```json
{"website url":  "https://example com", "new_url":  "<New URL>", "new_title":  "<New Title>", "new_description":  "<New description>"}
```

> **ℹ️Note:** all the "new_something" parameters are optional.
 
authentication is required in form of an `authorization` header:

`Authorization: Bearer <token>`

the `token` is what you received when adding the website to the index.

**remove a website**

remove a website by setting the `new_url` parameter to an empty value.

example payload:
```json
{"website url":  "https://example com", "new_url":  ""}
```
authentication is required in form of an `Authorization` header:

`Authorization: Bearer <token>`

the `token` is what you received when adding the website to the index.

___

### hosting your own version of compass

*understanding what's needed*

compass uses two things: 1. the server that contains the API and 2. the index updating script
which keeps the index up to date by regularly going through the list of websites and pinging them
to see if any are down. it also updates the `website_index_out.html` file which also is the landing page
of `superbrain`.

*manual installation*

dependencies:

* `pip install -r requirements.txt`

environmental variables:
* Set `WEBSITE_INDEX_HOST` to the host to run the website on (for example `0.0.0.0`).
* Set `WEBSITE_INDEX_PORT` to the port to run the website on (for example `80`).
* Set `WEBSITE_INDEX_RUN_APP` to exactly `True` or `False`. This is whether to run the app using the default
debug WSGI server in Flask.

**manually running:**

* to run server in local environment (do not do this in production!): `sudo python3 main.py`
* to run server in production environment: `gunicorn main:app`
* queue `index_cheker.py` and `index_file_generator.py` to run periodically (suggestion: twice per day for the checker 
and every five minutes for the index file generator)

**systemctl**:

for running the server:

* `sudo mv services/run_compass_server.service /etc/system/systemd/run_compass_server.service`
* `sudo chmod +x run_compass_server.sh`

for updating the index files:
* `sudo mv services/update_compass_index.service /etc/system/systemd/update_compass_index.service`
* `sudo chmod +x update_compass_index.sh`