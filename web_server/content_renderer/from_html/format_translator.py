'''format_translator.py
This package breaks a HTML-like text file down to a format in which it can be converted to
a terminal interface.
'''
import logging
from bs4 import BeautifulSoup
from .exceptions import *
from ..screen.element import Row, Column
from ..screen.scene import Scene
from .const import DEFAULT_SCREEN_WIDTH
from .converters import TAGS_LINE_BREAKS_AFTER, TAGS_LINE_BREAKS_BEFORE, parse_tag, parse_tags_in, \
HAS_INVIDIDUAL_PARSERS


class Translator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def break_down(self, html_content):
        '''The main function that breaks down its input.'''
        self.logger.debug("Translating HTML file...")
        soup = BeautifulSoup(html_content, "lxml")
        #Now, begin the translation.
        #Get head and body
        if soup.find("head"):
            head = soup.find("head")
        else:
            head = None
        if soup.find("body"):
            body = soup.find("body")
        else:
            raise ParsingException("Body tag does not exist in document.")
        rows = []
        columns = []
        #Parse head. The converter will return some magic ANSI escape codes.
        head_elements = []
        head_elements.extend(parse_tag(head))
        rows.append(Row(columns=[Column(elements=head_elements)]))
        #Parse body
        current_row_content_length = 0
        excluded_tags = []
        self.logger.debug(f"Parsing tag body...")
        parsed_body_tags = parse_tags_in(body, exclude=excluded_tags)
        self.logger.debug(f"Got {len(parsed_body_tags)} parsed tags back as a response.")
        for parsed_body_tag in parsed_body_tags: #for tag in body.findChildren(recursive=False):
            parsed_tags = parsed_body_tag.parsed_tags
            if parsed_body_tag.space_before:
                self.logger.debug(f"Inserting new row before tag {parsed_body_tag.original_tag.name}...")
                rows.append(Row(columns=columns))
                columns = []
            max_tag_row_content_length = max([max([len(row) for row in str(parsed_tag).split("\n")]) for parsed_tag in
                                              parsed_tags])  # Sorry about this... but I wanted to play around with oneliners
            if current_row_content_length + max_tag_row_content_length > DEFAULT_SCREEN_WIDTH:  # Move to new row if needed
                self.logger.debug("Resetting current row (max content length reached)...")
                rows.append(Row(columns=columns))
                columns = []
                current_row_content_length = 0
            else:
                current_row_content_length += max_tag_row_content_length
            columns.append(Column(elements=parsed_tags))
            #Check if a new row should be inserted after the column
            if parsed_body_tag.space_after:
                self.logger.debug(f"Inserting new row after tag {parsed_body_tag.original_tag.name}...")
                rows.append(Row(columns=columns))
                columns = []
        #If any columns haven't been added to a row yet, do so
        if len(columns) > 0:
            rows.append(Row(columns=columns))
        self.logger.debug(f"{len(rows)} rows added.")
        return rows

    def to_scene(self, content:str, *args, **kwargs):
        '''Converts raw content by calling the break_down function and then returns
        a Scene().'''
        return Scene(rows=self.break_down(content), *args, **kwargs)

