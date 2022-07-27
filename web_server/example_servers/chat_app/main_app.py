import logging, os
from flask import Blueprint, request, redirect, render_template
from models import Message
from create_app import database
from http import HTTPStatus
#Set up logging and other stuff
logger = logging.getLogger(__name__)
main_app = Blueprint("main_app", __name__)
BASE_URL = os.environ["WEBSITE_BASE_URL"].strip("/") #Use the base URL parameter because the sourceloader can not understand relative URLs
ALLOWED_CHANNEL_IDS = ["general",
                       "jokes",
                       "bots-allowed",
                       "international"]
@main_app.route("/")
def index():
    '''Index. Returns links to different channels.'''
    logger.info("Got a request to the index! Returning...")
    return render_template("index.html", channel_ids=ALLOWED_CHANNEL_IDS, base_path=BASE_URL)

@main_app.route("/<string:channel_id>/new_message", methods=["POST"])
def new_message(channel_id):
    '''Function to create a new message.'''
    logger.info("Got a request to create a message. Validating parameters...")
    #Required parameters: correct channel ID + message parameter as multipart form
    if channel_id not in ALLOWED_CHANNEL_IDS:
        logger.info("Invalid channel ID! Returning error...")
        return f"Invalid channel ID. Allowed channels are: {ALLOWED_CHANNEL_IDS}", HTTPStatus.FORBIDDEN
    logger.info("Check! Channel ID is valid.")
    #Get form and (hopefully) message
    logger.debug(f"Form: {request.form}")
    if "message" not in request.form or len(request.form["message"]) >= Message.MESSAGE_MAX_LENGTH:
        logger.info("Too long message or nonexistent! Returning error...")
        return f"Your message is too long (the character limit is {Message.MESSAGE_MAX_LENGTH}).", HTTPStatus.BAD_GATEWAY
    logger.info("Check! Message is valid!")
    message_content = request.form["message"]
    message = Message(channel=channel_id, content=message_content)
    logger.debug("Adding message to session...")
    database.session.add(message)
    logger.debug("Committing session...")
    database.session.commit()
    logger.info("Message added to database. Returning redirect...")
    return redirect(f"/{channel_id}/messages")

@main_app.route("/<string:channel_id>/messages")
def channel_messages(channel_id):
    '''Returns messages in a channel.'''
    logger.info(f"Got a request to get messages for channel {channel_id}!")
    if channel_id not in ALLOWED_CHANNEL_IDS:
        logger.info("Invalid channel ID - returning error.")
        return "The channel ID is not available.", HTTPStatus.NOT_FOUND
    #Get messages
    message_query = Message.query.filter_by(channel=channel_id).all()
    logger.debug(f"Found messages: {message_query}. Returning...")
    return render_template("messages.html", messages=message_query, channel_id=channel_id, base_path=BASE_URL)
