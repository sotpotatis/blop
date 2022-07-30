'''bumper.py
Utility code for bumping a website in a website index.
'''
import os, logging, requests, json, time
from argparse import ArgumentParser

#Set up command line arguments
parser = ArgumentParser()
parser.add_argument("website", help="The website to bump in the index", type=str)
parser.add_argument("--website_token", help="The token that belongs to the specific website", type=str, default="")
parser.add_argument("--title", help="The website title (optional)", type=str)
parser.add_argument("--description", help="The website description (optional)", type=str)
parser.add_argument("--new_website_url", help="If set, a new website URL to change the website in the index to.", type=str)
parser.add_argument("--website_index_server", help="The server where the compass website index is running.", type=str, default="http://compass.sweetpotato.online:1234")
parser.add_argument("--website_bump_threshold", default=3600, help="How often the website can be bumped. If the script is called too often, this value will stop the update.", type=int)

#Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger.info("Bumper updater code.")

#Parse arguments
logger.info("Parsing arguments...")
arguments = parser.parse_args()
website_url = arguments.website
website_token = arguments.website_token
title = arguments.title
description = arguments.description
website_index_server = arguments.website_index_server
website_bump_threshold = arguments.website_bump_threshold
new_website_url = arguments.new_website_url
logger.info("Arguments parsed.")

#Now, check if the requested website is accessible
try:
    logger.info("Verifying that website to bump is accessible...")
    request = requests.get(website_index_server)
    logger.info(f"Contacted {request} with response {request.status_code}.")
    if not request.ok:
        raise Exception("Request was not ok.")
except Exception as e:
    logger.critical(f"Failed to contact the website to bump. The bump will not be performed. Error: {e}.")
    exit(1)

#Check if the website was bumped recently
def write_json(file, json_data):
    '''Writes JSON to a file.

    :param file: The filepath to write data to.

    :param json_data: The JSON data to write.'''
    with open(file, "w") as json_file:
        json_file.write(json.dumps(json_data, indent=True))

def read_json(file):
    '''Reads JSON from a file.

    :param file: The filepath to read data from.'''
    return json.loads(open(file, "r").read())

WEBSITE_BUMP_TRACKING_FILE = os.path.join(os.getcwd(), ".website_bumps.json")
if not os.path.exists(WEBSITE_BUMP_TRACKING_FILE):
    logger.info("Creating website bump JSON file...")
    website_bump_data = {"websites": {}}
    write_json(WEBSITE_BUMP_TRACKING_FILE, website_bump_data)
else:
    logger.info("Reading website bump JSON file...")
    website_bump_data = read_json(WEBSITE_BUMP_TRACKING_FILE)
#Check if website has been bumped too recently or not
if website_url in website_bump_data["websites"]:
    time_since_website_bump = time.time()-website_bump_data["websites"][website_url]["last_bumped"]
    if time_since_website_bump < website_bump_threshold:
        logger.critical(f"Website has been bumped too recently! (is at {round(time_since_website_bump,1)} seconds since bump, limit is at least {website_bump_threshold} seconds.)")
        logger.info("Use the --website_bump_threshold argument to customize threshold.")
        exit(1)
    else:
        logger.info("Website has not been bumped too recently - all good.")
else:
    logger.info("Website has not been bumped before.")

#Send bump request
logger.info("Sending bump request...")
request_json = {
"website_url": website_url
}
try:
    #Detect first request
    first_request = website_token == ""
    headers = {"Authorization": f"Bearer {website_token}"} if not first_request else None
    if title is not None:
        if first_request:
            request_json["title"] = title
        else:
            request_json["new_title"] = title
    if description is not None:
        if first_request:
            request_json["description"] = description
        else:
            request_json["new_description"] = description
    if new_website_url is not None:
        request_json["new_url"] = new_website_url
    logger.info(f"Sending request to {website_index_server} with JSON {request_json} and headers {headers}")
    bump_request = requests.post(f"{website_index_server}/websites",
                                 json=request_json,
                                 headers=headers)
    if not bump_request.ok:
        logger.critical("Request to bump index was not ok!")
        raise Exception("Request was not ok.")
    bump_request_json = bump_request.json()
    if bump_request_json["status"] == "success":
        logger.info("Sent request. All good!")
        if first_request:
            logger.info(f"Use the following token when updating the website using this CLI: {bump_request_json['website']['token']}")
        else:
            logger.info(f"Here is a reminder of the website token: {bump_request_json['website']['token']}")
    else:
        logger.critical("Request was not ok. Status is not success!")
        raise Exception("Request was not ok. Status is not success!")
except Exception as e:
    try:
        request_json = bump_request.json()
    except Exception as sub_e:
        logger.debug(f"JSON not available from request ({sub_e})", exc_info=True)
        request_json = "JSON not available."
    logger.critical(f"Request to bump website failed. Error: {e}. JSON: {request_json}", exc_info=True)
    exit(1)
#If we get here, all good! So, update the website
website_bump_data["websites"][website_url] = {
    "last_bumped": time.time()
}
logger.debug("Updating website bumping tracking file...")
write_json(WEBSITE_BUMP_TRACKING_FILE, website_bump_data)
logger.debug("Updated website bumping track file.")
logger.info("Script finished.")