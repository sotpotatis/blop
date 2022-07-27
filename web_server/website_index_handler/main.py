import logging, os, json, datetime, secrets
from flask import Flask, jsonify, request
from http import HTTPStatus
from shared_helpers import *

#Load some environment variables
APP_HOST = os.environ["WEBSITE_INDEX_HOST"]
APP_PORT = int(os.environ["WEBSITE_INDEX_PORT"])
RUN_APP = bool(os.environ["WEBSITE_INDEX_RUN_APP"])

app = Flask(__name__)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def generate_api_response(status, status_code, data=None):
    '''Function for generating an API status JSON.

    :param status: The status, such as "success" or "error".

    :param status_code: The status code that was returned from the API.

    :param data: Data that should be returned in JSON format.'''
    if data == None: #Create data if it doesn't exist
        data = {}
    data["status"] = status
    data["status_code"] = status_code
    logger.debug(f"Generated API response: {data}...")
    return data #Return data

def generate_api_error(error_message, status_code, data=None):
    '''Function to generate an API error response.

    :param error_message: A message describing the error

    :param status_code: The status code.

    :param data: Data, if any, to add to the response.'''
    if data == None:
        data = {}
    data["message"] = error_message
    return generate_api_response(
        "error", status_code, data=data
    )

def generate_api_success_response(message, data=None, status_code=200):
    '''Function to generate a success message.

    :param message: The message.

    :param status_code: The status code if not 200 which is the default.

    :param data: Data, if any, to provide'''
    if data == None:
        data = {}
    data["message"] = message
    return generate_api_response("success", status_code, data)
if not os.path.exists(WEBSITE_INDEX_FILE_PATH):
    logger.info("Creating website index file...")
    update_website_index({
        "websites": {}
    })

@app.route("/")
def index():
    '''Index route that returns information.'''
    logger.info("Got a request to the index route. Returning information...")
    return jsonify(generate_api_success_response("The website index handler server is active. Find information about how to use it in the docs."))

@app.route("/current_index")
def current_index():
    '''Gets the current website index and returns it.'''
    logger.info("Got a request to get the current website index. Returning response...")
    website_index = get_website_index_file()
    #Censor website tokens
    clean_website_index = {"websites": {}}
    for website_url, website_data in website_index["websites"].items():
        del website_data["token"]
        clean_website_index["websites"][website_url] = website_data
    logger.debug("Cleaning website index done.")
    response = generate_api_success_response({"website_index": clean_website_index})
    return jsonify(response)

#Validation functions for websites (returns True if valid)
validate_website_title = lambda title: type(title) == str and len(title) <= 24
validate_website_description = lambda description: type(description) == str and len(description) < 128
@app.route("/websites", methods=["POST"])
def websites():
    '''Endpoint to handle websites. There are several different functions this endpoint
    serves as - see the readme for more information.'''
    logger.info("Got a request to the websites endpoint!")
    #Check for the required parameter "website_url". It must be supplied with every request no matter the intention.
    request_json = request.get_json()
    if request_json == None:
        logger.info("No JSON supplied. Returning API error...")
        return jsonify(generate_api_error("No JSON was supplied with your request", HTTPStatus.BAD_REQUEST)), HTTPStatus.BAD_REQUEST
    elif "website_url" not in request_json:
        logger.info("Website URL not in request. Returning API error...")
        return jsonify(generate_api_error("website_url parameter is missing in request. This must be set.", HTTPStatus.BAD_REQUEST)), HTTPStatus.BAD_REQUEST
    elif "title" in request_json and (type(request_json["title"]) != str or len(request_json["title"]) > 24):
        logger.info("Title is too long. Returning error...")
        return jsonify(generate_api_error("Title provided is too long or of the invalid type.", HTTPStatus.BAD_REQUEST)), HTTPStatus.BAD_REQUEST
    elif "description" in request_json and (type(request_json["description"]) != str or len(request_json["description"]) > 128):
        logger.info("Description is too long. Returning error...")
        return jsonify(generate_api_error("Description provided is too long or of the invalid type.", HTTPStatus.BAD_REQUEST)), HTTPStatus.BAD_REQUEST
    title = request_json["title"] if "title" in request_json else None
    description = request_json["description"] if "description" in request_json else None
    logger.info("All wanted parameters are in the request.")
    #Now, detect whether we are updating or removing a website
    previous_websites = get_website_index_file()["websites"]
    authorization = None if not "Authorization" in request.headers else request.headers["Authorization"].replace("Bearer ", "")
    logger.info(f"Authorization: {authorization}")
    website_url = request_json["website_url"]
    if authorization == None: #Check - new website?
        if website_url not in previous_websites:
            logger.info("New website. Adding...")
            website_token = secrets.token_hex(8)
            previous_websites[website_url] = {
                "url": website_url,
                "token": website_token,
                "title": title,
                "description": description,
                "updated_at": str(datetime.datetime.now())
            }
            update_website_index({"websites": previous_websites})
            logger.info("Website has been added.")
            return jsonify(generate_api_success_response(
                "The website has been added to the index. SAVE THE TOKEN! DO NOT LOSE IT!",
                data={"website": previous_websites[website_url]}
            ))
        else:
            logger.info("Website is not new, but missing authentication.")
            return jsonify(
                generate_api_error("Missing authentication. To perform any actions to this website, authenticate with the TOKEN from the original request.",
                                   HTTPStatus.FORBIDDEN)
            ), HTTPStatus.FORBIDDEN
    #If we get here, a previous website is being requested
    #Check - does the website exist?
    if website_url not in previous_websites:
        logger.info("Requested a website not found.")
        return jsonify(generate_api_error(
            "The requested website was not found in the index. You could try adding it again.",
            HTTPStatus.NOT_FOUND)), HTTPStatus.NOT_FOUND
    else:
        logger.info("Requested website found. Checking token...")
        website_data = previous_websites[website_url]
        if website_data["token"] != authorization:
            logger.info("Invalid authorization token. Returning error.")
            return jsonify(
                generate_api_error(
                    "Invalid authentication. To perform any actions to this website, authenticate with the TOKEN from the original request.",
                HTTPStatus.FORBIDDEN)
            ), HTTPStatus.FORBIDDEN
        else:
            logger.info("Authorization token was valid. Updating website...")
            website_data["updated_at"] = str(datetime.datetime.now())
            if "new_url" in request_json:
                if request_json["new_url"] not in website_data:
                    logger.info("Changing URL...")
                    del previous_websites[website_url]
                    if request_json["new_url"] == "": #Use an empty URL to delete the website
                        update_website_index({"websites": previous_websites})
                        logger.info("Website was deleted.")
                        return jsonify(generate_api_success_response("The website was successfully deleted."))
                    else:
                        website_url = request_json["new_url"]
                        website_data["url"] = website_data
                        previous_websites[website_url] = website_data
            if "new_title" in request_json:
                if not validate_website_title(request_json["new_title"]):
                    logger.info("Title is not valid. Returning error...")
                    return jsonify(generate_api_error("The new title is not valid (invalid type or too long)",
                                                      HTTPStatus.BAD_REQUEST)), HTTPStatus.BAD_REQUEST
                logger.info("Adding new title.")
                website_data["title"] = request_json["new_title"]
            if "new_description" in request_json:
                if not validate_website_title(request_json["new_description"]):
                    logger.info("Description is not valid. Returning error...")
                    return jsonify(generate_api_error("The new description is not valid (invalid type or too long)",
                                                      HTTPStatus.BAD_REQUEST)), HTTPStatus.BAD_REQUEST
                logger.info("Adding new description.")
                website_data["description"] = request_json["new_description"]
            update_website_index({"websites": previous_websites})
            logger.info("Updated.")
            return jsonify(generate_api_success_response("The website was successfully updated.", {"website": previous_websites[website_url]}))
logger.info(f"""{COMPASS_LOGO_ASCII}
Every seaman needs a trusty ol' compass! The compass server was just initialized.
""")
if __name__ == "__main__" and RUN_APP:
    logger.info("Running app...")
    app.run(host=APP_HOST, port=APP_PORT)