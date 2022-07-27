print("This will create a database for the chat app.")
print("NOTE: Only run this once to avoid data loss!")
input("Press enter to continue:")
from create_app import database, create_app
database.create_all(app=create_app())
print("Done.")