import logging, os
from flask import Flask
#Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

#Set up database
from flask_sqlalchemy import SQLAlchemy
database = SQLAlchemy()

def create_app():
    '''Creates an app by setting up a database etc.'''
    logger.info("Creating Veronica app...")
    app = Flask(__name__)
    BASE_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIRECTORY, "database.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    database.init_app(app)
    logger.debug("Database initialized.")
    from main_app import main_app
    app.register_blueprint(main_app)
    logger.debug("App imported.")
    logger.info("Veronica app was created!")
    return app