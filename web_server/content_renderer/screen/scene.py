import logging, requests, math, re, sys
from .element import Row
from typing import List
from .interactive_elements import InteractiveElement
sys.path.append("...")
from const import NAVIGATE, ARROW_KEY_CODES, ARROW_KEYS_REVERSED, ARROW_KEYS_LEFT_RIGHT, TERMINAL_COLORS
from .event import Event
from .rendering_helpers import true_length
class Cursor:
    '''Represents a cursor on the screen. Default position is top right.'''
    def __init__(self, position_x=0, position_y=0, max_x=80, max_y=24):
        '''Initializes a cursor.

        :param position_x: The cursors position in X direction (0 is left, max is parent scene width)

        :param position_y: The cursors position in X direction (0 is top, max is parent scene height)

        :param max_x: Max X position for the cursor.

        :param max_y: Max Y position for the cursor.

        '''
        self.position_x = position_x
        self.position_y = position_y
        self.max_x = max_x
        self.max_y = max_y
        self.logger = logging.getLogger(__name__)

    def navigate_to(self, x, y):
        '''Returns the necessary key combinations for navigating to a certain coordinate from the cursor's current position'''
        self.logger.debug(f"Navigating the cursor to {x}, {y} from {self.position_x}, {self.position_y}...")
        navigation_characters = ""
        #Get how many rows we have to go up or down
        if x == self.position_x and y == self.position_y:
            self.logger.debug("Do not have to move anywhere.")
            return ""
        self.logger.debug("I have to move somewhere.")
        navigation_characters += NAVIGATE.TO_COORDINATE.format(x,y)
        self.position_x = x
        self.position_y = y
        return navigation_characters

    def move(self, direction_string):
        '''Moves the cursor one step based on a string.

        :param direction_string: left, right, up, or down.'''
        if direction_string == "left" and self.position_x > 0:
                self.position_x -= 1
        elif direction_string == "right" and self.position_x < self.max_x:
            self.position_x += 1
        elif direction_string == "down" and self.position_y < self.max_y:
            self.position_y += 1
        elif direction_string == "up" and self.position_y < 0:
            self.position_y -= 1


class Scene:
    '''A Scene represents the active scene on the screen.
    It contains rows which in turn contains columns which in turn contains elements.'''
    def __init__(self, rows:List[Row], width=80, height=24, current_scroll_position=0, periodically_update_every=0.5, source=None, scrolling_speed=0.25):
        '''Initializes a scene.

        :param elements: A list of rows that are on the screen.

        :param width: Scene width. Default is 80 characters (standard)

        :param height: Scene height. Default is 24 characters (standard)

        :param current_scroll_position: Row offset to apply for scrolling

        :param periodically_update_every: How often to periodically update the screen.

        :param source: The source URL or file that the screen content was loaded from.

        :param scrolling_speed: How fast to scroll the application per input - 0.5x means 1/2 of the total screen height
        '''
        self.rows = rows
        self.width = width
        self.height = height
        self.total_content_height = 0
        self.logger = logging.getLogger(__name__)
        self.current_scroll_position = current_scroll_position
        self.cursor_string = "" #Keycode buffer for what to write to move string
        self.source = source
        self.current_row_string = self.render()
        self.periodically_update_every = periodically_update_every
        self.force_reload = False #Whether to force reload of the next reload. Used for event handling.
        self.cursor = Cursor(position_y=height, max_x=width, max_y=height) #Initialize a cursor for the scene
        self.scrolling_speed = scrolling_speed
        #Iterate through interactive elements and try to find all elements that are interactive
        self.interactive_elements = []
        self.active_interactive_element_index = 0
        string_index = 0
        active_element_index = 0
        row_index = 0
        for row in self.rows:
            column_index = 0
            for column in row.columns:
                string_index += len(str(column))
                element_index = 0
                for element in column.elements:
                    if issubclass(type(element), InteractiveElement): #Check if element is derived from active element
                        # Set parent attributes on element
                        element.parent_row_index = row_index
                        element.parent_column_index = column_index
                        element.element_index = element_index
                        if active_element_index == self.active_interactive_element_index:
                            self.logger.debug(f"Made element {active_element_index} active.")
                            element.is_active = True
                        self.interactive_elements.append(element)
                        self.update_element_at(row_index, column_index, element_index, element)
                        active_element_index += 1
                    element_index += 1
                column_index += 1
            row_index += 1

    def update_element_at(self, row_index:int, column_index:int, element_index:int, new_element_data):
        '''Shortcut function to update an element at a certain position.

        :param row_index: Index of the row for the element

        :param column_index: Index of the column for the element

        :param element_index: Index of the element in the column

        :param new_element_data: New data for the element'''
        self.logger.debug(f"Updating element at index {row_index}, {column_index}, {element_index}")
        self.rows[row_index].columns[column_index].elements[element_index] = new_element_data

    def get_scrollbar_lines(self):
        '''Function to get content lines for the scrollbar.'''
        #Check if the screen should be scrolled
        self.logger.debug(f"Checking and potentially adding scrollbars for content height {self.total_content_height}, scene height {self.height}...")
        if self.total_content_height > self.height:
            self.logger.debug("Screen should be scrolled. Adding scrollbars...")
            #Add scrollbars for the whole screen
            scrollbar_lines = ["^"]
            percentage_of_screen_scrolled = self.current_scroll_position/self.total_content_height
            scrollbar_indicator_char_at = math.floor((self.total_content_height-2) * percentage_of_screen_scrolled)
            for i in range(self.total_content_height-2):
                scrollbar_lines.append("O" if i == scrollbar_indicator_char_at else ".")
            scrollbar_lines.append("V")
        else:
            self.logger.debug("Screen does not have to be scrolled.")
            scrollbar_lines = []
        self.logger.debug(f"Generated scrollbar lines: {scrollbar_lines}")
        return scrollbar_lines

    def render(self):
        '''Renders the screen to characters.'''
        self.scrollbar_lines = self.get_scrollbar_lines()
        self.current_row_string = ""
        all_individual_rows = []
        row_index = 0
        for row in self.rows:
            row_string = str(row)
            for individual_row in row_string.split("\n"):
                final_row = ""
                for character in individual_row:
                    final_row += character
                if len(self.scrollbar_lines)-1 >= row_index: #Add scrollbars if needed
                    scrollbar_line = self.scrollbar_lines[row_index] #Get scrollbar content for this row TODO: Fix colors - scrollbar is being affected by colors of other elements
                    if true_length(final_row)+len(scrollbar_line) < self.width:
                        final_row += " "*(self.width-len(scrollbar_line)-true_length(final_row))
                    #Add scrollbar line
                    final_row += scrollbar_line
                all_individual_rows.append(final_row)
                row_index += 1
        self.total_content_height = len(all_individual_rows)
        self.logger.debug(f"Scrolling offset: {self.current_scroll_position}.")
        individual_rows = all_individual_rows[self.current_scroll_position:] #Apply scrolling offset right away
        #If the text is too tall for the current height, clip it
        if len(individual_rows) > self.height:
            individual_rows = individual_rows[:self.height]
        #Join strings again and return
        self.current_row_string = "\n".join(individual_rows)
        #Add extra cursor moving characters
        self.current_row_string += self.cursor_string
        self.logger.debug(f"Added cursor string (which has a length of {len(self.cursor_string)})")
        return self.current_row_string

    def set_interactive_element(self, element, active):
        '''Function for setting if an interactive element is active or not.
        This function makes sure that the change is reflected in the main elements list.

        :param element: The element from the interactive_elements list.

        :param active: Whether to set the element to active or not.'''
        element.is_active = active
        self.update_element_at(element.parent_row_index, element.parent_column_index, element.element_index, element)

    def update(self, key=None, encoding=None):
        '''Function to update screen content.

        :param key: If not None, only update elements on keypress.

        :param encoding: The detected encoding of the data if any'''
        self.force_reload = False #Reset force_reload parameter
        #Iterate through everything and find things that has a handler that we should run
        #Arrow keys are reserved by the screen to change which element that is active. So check it
        self.cursor_string = ""
        if key in ARROW_KEYS_REVERSED:
            active_key_name = ARROW_KEYS_REVERSED[key]
            if key in ARROW_KEYS_LEFT_RIGHT: #Left or right key - Change which element that is active
                self.logger.debug(f"{active_key_name} was pressed - changing currently active element index.")
                # Bump active item
                self.set_interactive_element(self.interactive_elements[self.active_interactive_element_index], False)
                if active_key_name == "right": #Right - Go forward in active elements
                    if self.active_interactive_element_index < len(self.interactive_elements)-1:
                        self.active_interactive_element_index += 1
                    else:
                        self.active_interactive_element_index = 0
                elif active_key_name == "left": #Left - Go back in active elements
                    if self.active_interactive_element_index > 0:
                        self.active_interactive_element_index -= 1
                    else:
                        self.active_interactive_element_index = len(self.interactive_elements)-1
                self.logger.debug(f"New active element index: {self.active_interactive_element_index}")
                self.set_interactive_element(self.interactive_elements[self.active_interactive_element_index], True)
            else: #Up or down key - scroll
                self.logger.debug("Scrolling...")
                #Check if scrolling is allowed and then scroll.
                scroll_length = round(self.height * self.scrolling_speed)
                if active_key_name == "up" and self.current_scroll_position > 0:
                    self.logger.debug("Scrolling up...")
                    if self.current_scroll_position - scroll_length > 0:
                        self.current_scroll_position -= scroll_length #Scroll up
                    else:
                        self.current_scroll_position = 0 #Scroll up partly
                elif active_key_name == "down":
                    self.logger.debug("Scrolling down...")
                    if self.current_scroll_position + scroll_length < self.total_content_height:
                        self.current_scroll_position += scroll_length #Scroll down
                    else:
                        self.current_scroll_position = self.total_content_height #Scroll down partly
                self.logger.debug(f"Scrolled to position {self.current_scroll_position}.")
            #Move cursor since position on screen has changed in one way or another in this step
            self.logger.debug("Moving cursor between items.")
            self.cursor.move(active_key_name)
        row_index = 0
        self.logger.debug(f"Iterating over row {self.rows}...")
        for row in self.rows:
            self.logger.debug(f"Iterating over columns {row.columns}...")
            column_index = 0
            for column in row.columns:
                self.logger.debug(f"Iterating over elements {column.elements}...")
                element_index = 0
                for element in column.elements:
                    #Check and execute handlers depending on what is happening
                    self.logger.debug(f"{key} is arrow key: {key in ARROW_KEY_CODES} ({ARROW_KEY_CODES})")
                    if key is not None and key not in ARROW_KEY_CODES and hasattr(element, "on_keypress"):
                        self.logger.debug(f"Running keypress handler for {element}...")
                        # Provide a decoded version of the key
                        if type(key) != str:
                            if encoding != None:
                                decoded_key = key.decode(encoding=encoding)
                            else:
                                decoded_key = key.decode()
                        else:
                            decoded_key = key
                        updated_element_data = element.on_keypress(key, decoded_key)
                        #Keypress handler might return a list of events. Check that
                        if type(updated_element_data) == tuple:
                            self.logger.debug("Got event data from the handler.")
                            element = updated_element_data[0]
                            events = updated_element_data[1]
                            for event in events:
                                self.logger.debug(f"Sending event {event} over to handler...")
                                self.event_handler(event) #Handle the event
                                self.logger.debug("The event was handled.")
                        else:
                            self.logger.debug("No event was raised from the handler.")
                            element = updated_element_data
                    elif hasattr(element, "on_update"):
                        self.logger.debug(f"Running update handler for {element}...")
                        element = element.on_update()

                    #Make sure to move cursor to active element
                    if hasattr(element, "is_active") and element.is_active:
                        #Calculate where the element is on the screen and where it should be
                        element_search = str(element).strip("\n").split("\n")[0]
                        raw_element_index = self.current_row_string.find(element_search)
                        element_index_on_scene = raw_element_index-(len(self.current_row_string)-true_length(self.current_row_string)) #Get element index on scene. Subtract length for special color strings etc.
                        self.logger.debug(f"Element {element_search} has index {element_index_on_scene} in scene string.")
                        if raw_element_index == -1:
                            self.logger.debug(f"Could not find index of {element_search} in scene string! (is probably not scrolled to position)")
                        else:
                            #Get Y position (what row the element is at) and the X position (what column the element is at)
                            element_y_position = math.floor((element_index_on_scene / self.width)) #Y position can be retrieved by dividing row length (self.width)
                            element_x_position = element_index_on_scene - (element_y_position*self.width) #X position can be retrieved by subtracting number of characters to get to the current row
                            wanted_cursor_position_x = element_x_position + element.cursor_offset_from_first_character[0]
                            wanted_cursor_position_y = element_y_position + element.cursor_offset_from_first_character[1]
                            #Check if cursor should be moved
                            if self.cursor.position_x != wanted_cursor_position_x or self.cursor.position_y != wanted_cursor_position_y:
                                self.logger.debug(f"Moving cursor to X {wanted_cursor_position_x}, Y {wanted_cursor_position_y}.")
                                self.cursor_string = self.cursor.navigate_to(wanted_cursor_position_x, wanted_cursor_position_y)
                                self.logger.debug("Cursor was moved to the wanted position.")
                            else:
                                self.logger.debug(f"Cursor does not have to be moved (is already at wanted position X {wanted_cursor_position_x}, Y {wanted_cursor_position_y})")
                    self.logger.debug(f"Got an updated element: {element}")
                    self.update_element_at(row_index, column_index, element_index, element)
                    element_index += 1
                column_index += 1
            row_index += 1

    def __str__(self):
        return self.render()

    def __getitem__(self, item):
        '''Allows for retrieving an element based on its ID.

        :param item: The item's ID.'''
        #Find the element
        for row in self.rows:
            for column in row.columns:
                if item in column.id_to_element:
                    return column.id_to_element[item]
        raise KeyError("Could not find the requested ID.")

    def element_ids(self):
        '''Allows to list all the element IDs in the current scene.'''
        element_ids = []
        for row in self.rows:
            for column in row.columns:
                element_ids.extend(list(column.id_to_element))
        return element_ids #Return mapping

    def get_terminal_lines(self):
        '''Optimizes output for the terminal.'''
        terminal_lines = []
        rendered_content = self.render()
        for line in rendered_content.split("\n"):
            terminal_line = (line + "\r\n").encode()
            terminal_lines.append(terminal_line)
        return terminal_lines

    def get_dial_in_string(self):
        '''Get a string that can be used to dial in the terminal width the old-fashioned way!'''
        dial_in_string = """Resize your terminal window to just contain the content below for optimal performance: \n%s"""%(f"{'A'*self.width}\n"*(self.height-1))
        return dial_in_string

    def event_handler(self, event:Event):
        '''An event handler to handle any messages returned by elements as we run the on_update() or on_key() functions
        on them.'''
        #Get event type
        self.logger.debug(f"Handling event {event}...")
        if event.type == Event.CHANGE_SOURCE:
            self.logger.debug("Changing source...")
            self.source = event.data["source"]
        elif event.type == Event.SEND_INPUT_TO:
            self.logger.debug("Sending input to an external source...")
            #Get source element to get value from
            request_data = {}
            for source_element_id in event.data["source_ids"]:
                #Get where to send it
                send_to = event.data["send_to"]
                try:
                    source_element = self[source_element_id]
                except KeyError:
                    self.logger.warning(f"Requested input source element was not found. (available IDs: {self.element_ids()}, accessed: {source_element_id})")
                    continue
                #Get source element content. All inputs should have the content in a variable called "content"
                source_element_content = source_element.content
                self.logger.debug(f"Source element content: {source_element_content}. Adding...")
                request_data[source_element_id] = source_element_content
            #Sent requests will be POST requests with the parameters defined below (headers etc.)
            try:
                self.logger.debug(f"Sending request data to {send_to}...")
                request = requests.post(send_to, data=request_data,
                                        headers={"User-Agent": "Python/SceneServer",
                                                 "Content-Type": "application/x-www-form-urlencoded"},
                                        allow_redirects=True)
                self.logger.debug(f"Request finished with {request.status_code}, text {request.text}")
                if not request.ok:
                    self.logger.warning(f"Request sent to {send_to} might have failed (status code is not ok).")
                if request.url != self.source:
                    self.logger.debug("Updating request source to new URL...")
                    self.source = request.url
                self.force_reload = True #Force reload of source in case the content has updated.
            except Exception as e:
                self.logger.warning(f"Could not send request to external URL {send_to} (the exception {e} occurred).", exc_info=True)
        else:
            self.logger.warning("Scene handled an event it could not understand.")