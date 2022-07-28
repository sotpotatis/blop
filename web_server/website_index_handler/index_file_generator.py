'''index_file_generator.py
The index file generator uses the website index file to generate an HTML entry point that lists websites.
You should run this quite often to update the HTML file.
'''
from shared_helpers import WEBSITE_INDEX_TEMPLATE_FILEPATH_OUT, SERVER_DIRECTORY, get_website_index_file
from jinja2 import FileSystemLoader, Environment
import logging, datetime
logger = logging.getLogger(__name__)
logger.info("Starting the index file generator...")
#Read website index
website_index = get_website_index_file()
#Sort websites
def sort_websites(website_data):
    '''Function to sort websites based on their name.

    :returns the website name, for example i.albins.website.'''
    return website_data["url"].split("://")[1]
sorted_websites = sorted(website_index["websites"].values(), key=sort_websites)
logger.info("Websites sorted. Rendering HTML...")
#Render HTML
jinja_loader = FileSystemLoader(searchpath=SERVER_DIRECTORY)
jinja_environment = Environment(loader=jinja_loader)
template = jinja_environment.get_template("website_index.html")
logger.debug(f"Sorted data: {sorted_websites}.")
rendered_template = template.render(
    websites=sorted_websites,
    updated_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
logger.info(f"Rendered HTML. Output: {rendered_template}")
with open(WEBSITE_INDEX_TEMPLATE_FILEPATH_OUT, "w") as website_index_file:
    website_index_file.write(rendered_template)
logger.info("Changes written to file. All done!")
