

'''index_checker.py
The index checker iterates through the websites in the index to check for any
dead links etc. How many retries that are allowed can be set using the INVALID_RESPONSE_REMOVE_LIMIT.
How often a website should be updated is set using the WEBSITE_UPDATE_REMOVE_LIMIT.
That value is in MINUTES.'''
import datetime
import logging, requests
from shared_helpers import *
from bs4 import BeautifulSoup
INVALID_RESPONSE_REMOVE_LIMIT = int(os.environ["INVALID_RESPONSE_REMOVE_LIMIT"])
WEBSITE_UPDATE_REMOVE_LIMIT = int(os.environ["WEBSITE_UPDATE_REMOVE_LIMIT"])
logger = logging.getLogger(__name__)
logger.info("Running index checker...")
logger.info(f"Settings: websites will be removed after {INVALID_RESPONSE_REMOVE_LIMIT} failed retries and {WEBSITE_UPDATE_REMOVE_LIMIT} hours after receiving no ping.")
updated_websites_data = websites_data = get_website_index_file()
for website_url, website_data in websites_data["websites"].items():
    remove_from_index = False
    #Check if website has been bumped recently
    website_last_updated = website_data["updated_at"]
    update_difference_hours = (datetime.datetime.now() - datetime.datetime.fromisoformat(website_last_updated)).total_seconds() / 60
    logger.info(f"Website {website_url} was last updated in the index {round(update_difference_hours, 1)} hours ago.")
    if update_difference_hours > WEBSITE_UPDATE_REMOVE_LIMIT:
        logger.warning(f"Website {website_url} has not been updated within the allowed time limit. It will be removed from the index!")
        remove_from_index = True
    else:
        #Check if website is accessible
        logger.info(f"Trying to access {website_url}...")
        try:
            request = requests.get(website_url)
            if not str(request.status_code)[0] == "2" or request.text == "": #No content or invalid status code
                raise Exception("Website returned invalid status code or no text.")
            else:
                logger.info(f"{website_url} is accessible. Trying to convert HTML and get title...")
                soup = BeautifulSoup(request.text, "lxml")
                if soup.has_attr("title"):
                    logger.info(f"Added title for {website_url}.")
                    updated_websites_data["websites"][website_url]["website_title"] = soup["title"]
        except Exception as e:
            logger.warning(f"Failed to access indexed website {website_url} (the error {e} occurred)", exc_info=True)
            #Add error information
            if "registered_errors" not in website_data:
                website_data["registered_errors"] = 0
            website_data["registered_errors"] += 1
            if website_data["registered_errors"] > INVALID_RESPONSE_REMOVE_LIMIT:
                remove_from_index = True
    if remove_from_index:
        logger.warning(f"{website_url} will be removed from the index!")
        del updated_websites_data["websites"][website_url]
    else:
        logger.info(f"The website {website_url} will not be removed from the index")
update_website_index(updated_websites_data)
logger.info("Websites were updated.")