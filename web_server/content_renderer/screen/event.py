class Event:
    '''Simple event for event handling. See the functions under Screen for more information.'''
    #Event IDs
    CHANGE_SOURCE = "change_source" #Change the source of the scene
    SEND_INPUT_TO = "send_input_to" #Send input of an element ID to somewhere
    def __init__(self, type, data):
        '''Initializes an Event.

        :param type: The event type, see above.

        :param data: Any data belonging to the element.'''
        self.type = type
        self.data = data

    def __str__(self):
        return f"Type: {self.type}, data: {self.data}"