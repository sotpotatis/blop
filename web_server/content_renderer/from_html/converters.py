import cssutils, logging, sys
from ..screen.interactive_elements import TextBox, Button
sys.path.append("...")
from const import HTML_COLOR_TO_TERMINAL_COLOR, HTML_COLOR_TO_TERMINAL_COLOR_BACKGROUND, TERMINAL_COLORS, TERMINAL_COLORS_BACKGROUND, TERMINAL_FONT_WEIGHT
from ..screen.scene import Event
from .const import DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT
from bs4 import Tag
from typing import List
#Logging
logger = logging.getLogger(__name__)

#Each converter should expose a converter()-class
#which takes an input of the BeautifulSoup tag to convert.
#The converter should then return an object that can be converted into a string.


def html_color_to_terminal_color(html_color, is_foreground=True, previous=""):
    '''Converts a HTML color string (like "red", "green", etc.) to
    a terminal ANSI color code.

    :param html_color: The source HTML color code (for example "red")

    :param is_foreground: True to return a foreground ANSI color code.
    False to return a background ANSI color code.

    :param previous: Any previous text.'''
    #Return mapping if exists. If not, return None.
    color_string = None # String for this time around
    if is_foreground and html_color in HTML_COLOR_TO_TERMINAL_COLOR:
        color_string = HTML_COLOR_TO_TERMINAL_COLOR[html_color]
    elif not is_foreground and html_color in HTML_COLOR_TO_TERMINAL_COLOR_BACKGROUND:
        color_string = HTML_COLOR_TO_TERMINAL_COLOR_BACKGROUND[html_color]
    if color_string != None:
        # Check if we have old colors to combine or not
        if len(previous) > 0:
            final = previous.strip("m") + ";" + color_string.strip("\x1b[")
            return final
        else:
            return color_string

    else:
        return None


def check_required_attributes(input, required_attributes):
    '''Shortcut function to validate if an input tag has required attributes.

    :param input: The input tag to check.

    :param required_attributes: A list of required attributes: ["data-example"].
    This list might also contain tuples. If so, the second argument should be a function
    to execute with the value of the attribute. If the function evaluates False, the whole check fails.

    :returns True if check is successful, False if any checks fail.'''
    logger.debug(f"Checking for required attributes in {input}...")
    evaluations = []
    for required_attribute in required_attributes:
        logger.debug(f"Evaluating {required_attribute}...")
        if type(required_attribute) == str: #str check - simple check
            evaluation = input.has_attr(required_attribute)
        elif type(required_attribute) == tuple: #tuple check - advanced check
            evaluation = input.has_attr(required_attribute[0]) and required_attribute[1](input[required_attribute[0]])
        logger.debug(f"Evaluated: {evaluation}")
        evaluations.append(evaluation)
    return all(evaluations)

def get_style_for(input):
    '''Parses a style for an input tag if a style has been set.'''
    if input.has_attr("style"): #If style attribute is set
        logger.debug(f"Found style for {input}.")
        try:
            parsed_style = cssutils.parseStyle(input["style"])
            logger.debug(f"Parsed style for {input}: {parsed_style.keys()}")
            return parsed_style
        except Exception as e:
            logger.debug(f"Failed to convert style for {input}! The exception {e} occurred.", exc_info=True)
            return
    else:
        return

def get_color_string_for(input, style=None):
    '''Checks if a text color has been applied to the current element and if so returns the color string to add to it.
    Also checks other styles, like bold etc.'''
    final_string = ""
    if style == None:
        parsed_style = get_style_for(input)
    else:
        parsed_style = style
    if parsed_style != None:
        if "color" in parsed_style:
            logger.debug(f"Converting color string for input {input}...")
            color_string = html_color_to_terminal_color(parsed_style.color, previous=final_string) #Perform conversion
            if color_string != None: #None is returned if the color string couldn't be converted
                final_string += color_string
        if "background" in parsed_style:
            logger.debug(f"Converting color background string for input {input}...")
            # Perform conversion
            color_string = html_color_to_terminal_color(parsed_style.background, is_foreground=False, previous=final_string)
            if color_string != None: # None is returned if the color string couldn't be converted
                final_string += color_string
        if "font-weight" in parsed_style:
            logger.debug(f"Converting font weight for input {input}...")
            if parsed_style["font-weight"] in ["bold", "700"]:
                logger.debug("Found bold font weight.")
                final_string += TERMINAL_FONT_WEIGHT.BOLD_TEXT
            else:
                logger.debug("Could not parse font weight.")
        if "font-style" in parsed_style:
            logger.debug(f"Converting font style for input {input}...")
            if parsed_style["font-style"] in ["bold", "700"]:
                logger.debug("Found bold font style.")
                final_string += TERMINAL_FONT_WEIGHT.BOLD_TEXT
            elif parsed_style["font-style"] in ["italic"]:
                logger.debug("Found italic font style.")
                final_string += TERMINAL_FONT_WEIGHT.ITALIC_TEXT
        if "text-decoration" in parsed_style:
            logger.debug(f"Converting text decoration for input {input}...")
            if parsed_style["text-decoration"] in ["line-through"]:
                logger.debug("Found strikethrough text.")
                final_string += TERMINAL_FONT_WEIGHT.STRIKETHROUGH_TEXT
            else:
                logger.debug("Could not parse text decoration.")
    if final_string == "":
        logger.debug(f"No or style string found for input {input}...")
    else:
        logger.debug(f"Parsed style string for {input}: {final_string}")
    return final_string #Return an empty string if no color string was found

def parse_width_height(input, is_width=False, return_default_if_unconvertible=False):
    '''Parses a width or height unit into a scale between 1 and 0.
    Supports multiple units such as percentage, px, rem, etc.

    :param input: The input string, such as "100%", "2vw"

    :param is_width: True if this parameter is a width parameter, False if it is height.

    :param return_default_if_unconvertible: Whether to return 1 as a scale if the value failed to convert.
    If False, None will be returned instead.
    '''
    logger.debug(f"Parsing width/height string {input}...")
    input = input.strip(";").strip() #Strip whitespace and line break if there
    try:
        if input.endswith("%"):
            logger.debug("Applying percentage parser...")
            input_number = int(input.strip("%"))
            return input_number / 100 #Return the percentage on the scale of 0-1.
        elif input.endswith("rem"):
            input_number = int(input.strip("rem"))
            #NOTE: 1rem is the font size of the document. Standard is often 16px, so we assume it here
            return (input_number / 100) * 16
        elif input.endswith("vw") or input.endswith("vh"):
            input_number = int(input.strip("vw").strip("vh"))
            return (input_number / 100) * (DEFAULT_SCREEN_WIDTH if is_width else DEFAULT_SCREEN_HEIGHT)
        elif input.endswith("px"):
            input_number = int(input.strip("px"))
            #NOTE: Let's assume that 1px is 1 character, since people wouldn't want to use px styling for a terminal interface anyways
            return input_number / DEFAULT_SCREEN_WIDTH
        else:
            logger.debug("Unknown unit.")
            raise Exception(f"Unparseable: {input} (unknown unit)")
    except Exception as e:
        logger.debug(f"Unparseable string. (exception {e} occurred. Returning error...", exc_info=True)
        return 1 if return_default_if_unconvertible else None

class ParsedTag:
    '''Represents a parsed tag.'''
    def __init__(self, original_tag:Tag, parsed_tags):
        '''Initializes a parsed tag.

        :param original_tag: The original tag from BeautifulSoup.

        :param parsed_tags: The parsed tags as in what has been returned from any of the converter functions below.
        The only requirements is that the parsed tag can be converted into a string.'''
        self.original_tag = original_tag
        self.parsed_tags = parsed_tags
        self.space_before = original_tag.name in TAGS_LINE_BREAKS_BEFORE
        self.space_after = original_tag.name in TAGS_LINE_BREAKS_AFTER
        self._index = 0

    def __iter__(self):
        '''Allows for iteration over the parsed tags.'''
        return self

    def __next__(self):
        '''Gets the next available parsed tag.'''
        self._index += 1
        if self._index > len(self.parsed_tags)-1:
            raise StopIteration
        else:
            return self.parsed_tags[self._index]

    def __str__(self):
        return f"{self.original_tag} parsed into {len(self.parsed_tags)} subtags."

class TextConverter:
    '''Converter for any text tags.'''
    def converter(self, input):
        #Get raw text
        raw_text = input.get_text()
        parsed_color_string = get_color_string_for(input)
        return f"{parsed_color_string}{raw_text}{TERMINAL_COLORS.RESET}" #Return pure text

class InputConverter:
    '''Converter for input elements.'''
    SUPPORTED_TYPES = ["text"] #Supported input types
    def converter(self, input):
        #Get the input type
        if not check_required_attributes(input, [("type", (lambda input_type: input_type.lower() in InputConverter.SUPPORTED_TYPES))]):
            logger.warning("Tag not missing input type or input type not parseable.")
            return None
        input_type = input["type"].lower()
        #Apply specific parsing depending on input type
        if input_type == "text":
            #Get initial value if any
            initial_content = input.value if input.value else ""
            #Get width if any
            width = 20 #Start with default value
            if input.style:
                parsed_style = cssutils.parseStyle(input.style)
                if "width" in parsed_style:
                    width = parsed_style.width
            parsed_color_string = get_color_string_for(input) #Get color if set
            return TextBox(width=width, initial_content=initial_content, color_string=parsed_color_string)
        else:
            return None

class ButtonConverter:
    '''Converter for buttons.
    This also counts in inline "buttons" (using the definition that buttons are stuff
    that you can click), so therefore, <a> elements are also supported in this converter.'''
    def converter(self, input):
        #Get button text
        button_text = input.get_text()
        parsed_style = get_style_for(input)
        #Try to look for specified widths. If not, use default width
        width = len(button_text)
        if parsed_style != None and "width" in parsed_style:
            try:
                width = int(parsed_style["width"])
            except:
                logger.debug(f"Invalid custom width set for button (unparseable: {parsed_style['width']})", exc_info=True)
        #Try to look for a hyperlink
        event = None
        if input.has_attr("data-link"):
            logger.debug("Button has a link. Creating bound element...")
            event = Event(Event.CHANGE_SOURCE, {"source": input["data-link"]})
        else:
            logger.debug("Button does not have a link attached.")
        color_string = get_color_string_for(input, parsed_style) #Get color string for element
        is_link_like = input.name == "a"
        logger.debug(f"Button is link-like: {is_link_like}")
        return Button(width, button_text, event, color_string, is_link_like)

class HeadConverter:
    '''Converter for the header tag. Adds ANSI commands for title etc.'''
    SET_WINDOW_TITLE = TERMINAL_FONT_WEIGHT.BOLD_TEXT + ">>>{}<<<" + TERMINAL_FONT_WEIGHT.RESET #TODO: I want this to be an ANSI command: \x1b]2;{}\x07 but Windows doesn't like it?
    def converter(self, input):
        output = ""
        if input.title is not None:
            logger.debug("Adding title...")
            output += HeadConverter.SET_WINDOW_TITLE.format(input.title.get_text())
        else:
            logger.debug(f"Head content {input} does not have a title.")
        return output

class FormConverter:
    '''Converts forms.'''
    def converter(self, input):
        #The server can send data if the form has an attribute called "data-send-from-terminal" set to "true"
        if input.has_attr("data-send-from-terminal") and input["data-send-from-terminal"].lower() == "true":
            if input.has_attr("method") and input.has_attr("action"):
                output = [get_color_string_for(input)] #Add color string for element
                logger.debug("Form has required attributes for sending to an external server.")
                #Get input(s) to post data from when sending to external server
                #(requirements: have "id" attr set to anything and "data-include-in-payload" set to "true"
                data_sources = input.find_all("input", attrs={"id": True, "data-include-in-payload": "true"})
                logger.debug(f"Found data sources: {data_sources}")
                if len(data_sources) == 0:
                    logger.debug("No data sources found. Returning nothing...")
                    return ""
                #Get button to post data when sending to external server
                button = input.find("button", {"type": "submit"})
                post_form_data_event = Event(Event.SEND_INPUT_TO, {"source_ids":  [data_source["id"] for data_source in data_sources], "send_to": input["action"], "method": input["method"]})
                logger.debug(f"Post form data event is: {post_form_data_event}")
                logger.debug(f"Button: {button}")
                if button == None:
                    logger.debug("No button found. Creating fallback...")
                    post_button = Button("Send", 25, attached_event=post_form_data_event)
                else:
                    logger.debug("Found a button belonging to posting the form.")
                    post_button = parse_tag(button).parsed_tags[0]
                    post_button.attached_event = post_form_data_event #Attach data sending event
                #Parse other elements in the form
                logger.debug("Parsing other form elements...")
                exclude = [button]
                parsed_other_tags = parse_tags_in(input, exclude=exclude)
                for parsed_other_tag in parsed_other_tags:
                    output.extend(parsed_other_tag.parsed_tags)
                output.append(post_button) #Add sending button to output
                output.append(TERMINAL_COLORS.RESET)
                return output
            else:
                logger.debug("Form is missing attributes for sending to an external server! (missing action and/or method)")
        else:
            logger.debug("Form is missing attributes for sending to an external server! (missing data attributes)")
        return parse_tag(input, enforce_converter=TextConverter()) #Use fallback converter

class ListConverter:
    '''Converts lists.'''
    def converter(self, input):
        content = get_color_string_for(input)
        logger.debug("Parsing list...")
        for element in input.find_all("li"):
            content += f"* {element.get_text()}\n"
        return content + TERMINAL_COLORS.RESET

class HrConverter:
    '''Converts horizontal rulers.'''
    def converter(self, input):
        #Check if element has style
        style = get_style_for(input)
        if style != None and "width" in style:
            logger.debug("Custom width defined for hr. Converting...")
            raw_width = style["width"]
            width_scale = parse_width_height(raw_width, is_width=True, return_default_if_unconvertible=True)
        else:
            logger.debug("No custom width defined for hr. Using default value...")
            width_scale = 1
        return get_color_string_for(input) + ("-"*round(DEFAULT_SCREEN_WIDTH*width_scale)) + TERMINAL_COLORS.RESET

TAG_CONVERTERS = {
    "p": TextConverter,
    "span": TextConverter,
    "h1": TextConverter,
    "h2": TextConverter,
    "h3": TextConverter,
    "h4": TextConverter,
    "h5": TextConverter,
    "h6": TextConverter,
    "hr": HrConverter,
    "a": ButtonConverter,
    "ul": ListConverter,
    "head": HeadConverter,
    "input": InputConverter,
    "form": FormConverter,
    "button": ButtonConverter,
    "label": TextConverter,
    "fallback": TextConverter
}

TAGS_LINE_BREAKS_BEFORE = [ #Tags to add line breaks before
    "hr",
    "form",
    "input"
]
TAGS_LINE_BREAKS_AFTER = [ #Tags to add line breaks after (new row)
    "p",
    "br",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "form",
    "input",
]

def parse_tag(tag, enforce_converter=None):
    '''Forwards a tag for further parsing.

    :returns: A list of the tag parsed into one or multiple elements'''
    # Get tag name (a, p, etc.)
    tag_name = tag.name
    logger.debug(f"Parsing tag {tag}...")
    if enforce_converter != None:
        tag_converter = enforce_converter
    else:
        if tag_name not in TAG_CONVERTERS:
            logger.debug("Using fallback converter for tag...")
            tag_name = "fallback"
        tag_converter = TAG_CONVERTERS[tag_name]()
    #Execute converter function and return output
    parsed = tag_converter.converter(tag)
    logger.debug(f"Tag {tag_name} parsed into: {parsed}")
    if type(parsed) != list:
        #If we get one element returned, check if the element has an id set and if so set it
        if tag.has_attr("id") and type(parsed) != str:
            logger.debug(f"Setting ID on input tag {tag}...")
            parsed.id = tag["id"]
        parsed = [parsed] #Turn into list
    return ParsedTag(tag,parsed)


def parse_tags_in(parent_tag, exclude=None, previous=None)->List[ParsedTag]:
    '''Function to parse subtags in a parent tag.

    :param parent_tag: The parent to iterate over.

    :param exclude: Any tags to exclude

    :param previous: Any previous tags to include in the final tags'''
    if previous is None:
        previous = []
    if exclude is None:
        exclude = []
    logger.debug(f"Parsing tags in parent {parent_tag} with {len(exclude)} exclusions and {len(previous)} previous tags...")
    parsed_tags = previous
    for tag in parent_tag.findChildren(recursive=False):
        tag_children = tag.findChildren(recursive=False)
        number_of_children = len(tag_children)
        logger.debug(f"{tag} has {number_of_children} children.")
        #Ignore excluded tags
        if tag in exclude:
            logger.debug("Ignoring tag from parsing - has been excluded.")
            continue
        if number_of_children > 0 and tag.name not in HAS_INVIDIDUAL_PARSERS:
            logger.debug(f"Recursively parsing tag {tag}...")
            parsed_subtags = parse_tags_in(tag) #Use recursion magic if subtags were found again
            #Check if there is content within the parent tag that weren't covered by the recursive search, and if so, fix it
            for tag_child in tag_children:
                tag_child.decompose()
            if len(tag.get_text().strip()) > 0:
                logger.debug(f"Tag {tag} has text after decomposing.")
                parsed_tags.append(parse_tag(tag))
            parsed_tags.extend(parsed_subtags)
        else:
            logger.debug(f"Individually parsing tag {tag}")
            parsed_subtags = parse_tag(tag)
            parsed_tags.append(parsed_subtags)
    logger.debug(f"Finished with {len(parsed_tags)} parsed tags: {[str(parsed_tag) for parsed_tag in parsed_tags]}.")
    return parsed_tags

HAS_INVIDIDUAL_PARSERS = ["form", "ul", "li"] #List of tags that should not be parsed recursively by format_translator.py because they have their own recursive parsers.