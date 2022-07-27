'''models.py
Defines database models for the app.'''
from create_app import database
from sqlalchemy.sql import func

class Message(database.Model):
    '''Defines a sent user message.'''
    MESSAGE_MAX_LENGTH = 128  # Maximum length for message contentch
    id = database.Column(database.Integer, primary_key=True) #ID of the message
    content = database.Column(database.String(MESSAGE_MAX_LENGTH), nullable=False) #Message content
    channel = database.Column(database.String(28), nullable=False) #Where the message has been sent
    sent_at = database.Column(database.DateTime(timezone=True), server_default=func.now()) #When the message was sent