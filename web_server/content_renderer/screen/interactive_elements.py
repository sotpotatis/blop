'''interactive_elements.py
Interactive column elements for placing into a column.'''
import string, logging, sys
sys.path.append("...")
from const import TERMINAL_COLORS, KEY_ENTER
from .event import Event


class InteractiveElement:
    def __init__(self):
        self.is_active = False
        #When the interactive element is active, we want to move the cursor to it.
        #However, we implement an offset in case it's something like someone is typing
        #and the cursor should be moved to the current character.
        self.cursor_offset_from_first_character = (0,0)
        #At which index in the screen the interactive element starts at
        self.element_index_in_row = None
        self.element_index_on_screen = None
        self.logger = logging.getLogger(__name__)


class TextBox(InteractiveElement):
    def __init__(self, width, initial_content="", color_string=""):
        '''Creates a basic text box.

        :param width: The width of the textbox.

        :param initial_content: If specified, the initial content to have in the textbox.

        :param color_string: Terminal color data to add to the beginning of the textbox string.'''
        super().__init__()
        self.content = initial_content
        self.width = width
        self.color_string = color_string
        self.last_changed = 0

    def __str__(self):
        filled_out_content = self.content
        if len(filled_out_content) > self.width-2: #Clip content if too much text
            filled_out_content = filled_out_content[-self.width-2:]
        elif len(filled_out_content) < self.width-2: #Add spacing
            filled_out_content = filled_out_content + " "*(self.width-len(filled_out_content)-4)
        #Render a final textbox
        return f"""{self.color_string}
        {"-"*(self.width-2)}       
        {">" if self.is_active else "|"}{filled_out_content}|
        {"-"*(self.width-2)}
         {TERMINAL_COLORS.RESET}
        """

    def on_keypress(self, key):
        '''Handler for when a key is pressed'''
        #If keypress is a letter key and I am focused, add input to textbox content
        self.logger.debug(f"Handling keypress for textbox (pressed keys: {key})...")
        if type(key) == bytes: #TODO: This looks hacky, make sure key parameters are persistent
            key = key.decode()
        if self.is_active and all(char in string.ascii_letters for char in key):
            self.logger.debug(f"Adding content to textbox: {key}.")
            self.content += key
        else:
            self.logger.debug(f"Content will not be added to textbox. (focused: {self.is_active})")
        return self

class Button(InteractiveElement):
    def __init__(self, width, text, attached_event:Event=None, color_string:str="", is_link_like=False):
        '''Initializes a button.

        :param width: Width of the button

        :param text. Text of the button

        :param attached_event: An event to dispatch when the button has been clicked.

        :param color_string: Terminal color string for changing button color.

        :param is_link_like: Whether the button is supposed to render as a link rather than as a button.'''
        self.width = width
        self.text = text
        self.attached_event = attached_event
        self.color_string = color_string
        self.is_link_like = is_link_like
        super().__init__()

    def on_update(self):
        '''Handler for every time the screen updates'''
        return self

    def on_keypress(self, key):
        '''Handles a keypress. If active and if the event key is pressed,
        an event will be dispatched.'''
        self.logger.debug(f"Checking button keypress (active: {self.is_active}).")
        if self.is_active and key == KEY_ENTER:
            self.logger.debug(f"Dispatching button element... ({self.attached_event})")
            return self, [self.attached_event]
        return self

    def __str__(self):
        filled_out_content = self.text
        if len(filled_out_content) > self.width-2: #Clip content if too large
            filled_out_content = filled_out_content[-self.width-2:]
        elif len(filled_out_content) < self.width-2: #Add spacing if too small
            filled_out_content += " "*(self.width-len(filled_out_content)-2)
        if not self.is_link_like:
            border = ("." if self.is_active else "=")*(self.width+2)
        else:
            border = ""
        return f"""
        {self.color_string}{border}
        {'>' if self.is_active else '|'}{filled_out_content}|
        {border}{TERMINAL_COLORS.RESET}
        """

