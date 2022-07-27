from bottle import route, post, run, request, template, redirect
from http import HTTPStatus
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

@route("/")
def index():
    '''Index page. Returns the test form.'''
    logger.info("Got a request to the index. Returning test form...")
    return template("index.html")

@post("/post_data")
def post_data():
    form_items = list(request.forms.items())
    logger.debug(f"Received posted form with data {form_items}.")
    if len(form_items) > 0:
        logger.info("Got posted data!")
        #Send to external URL to render since this is required by the template rendering spec
        redirect_url = f"http://localhost:8200/display_data?{'&'.join([f'{key}={value}' for key, value in form_items])}"
        return redirect(redirect_url)#, HTTPStatus.PERMANENT_REDIRECT)
    else:
        logger.info("No data was posted. Returning error...")
        return "Error! No form data was received."

@route("/display_data", method=["GET", "POST"])
def display_data():
    '''Displays form data.'''
    form_items = list(request.query.items())
    logger.debug(f"Received posted form data with items {form_items}.")
    if len(form_items) > 0:
        return template("results.html", form_data=form_items)
    else:
        logger.info("No data was posted. Returning error...")
        return "Error! No form data was received."

logger.info("Running bottle server...")
#Run on localhost on port 8200
run(host="localhost", port="8200")