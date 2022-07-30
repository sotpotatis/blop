import os
from create_app import database, create_app
print("This will create a database for the chat app.")
print("NOTE: Only run this once to avoid data loss!")
input("Press enter to continue:")
# Set temporary environment variable (required for importing the server but not taken into consideration)
os.environ["WEBSITE_BASE_URL"] = ""
database.create_all(app=create_app())
print("Done.")
