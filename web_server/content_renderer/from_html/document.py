'''Represents a final converted document
that can be rendered using the terminal client.'''
from typing import List

class Document:
    def __init__(self, blocks:List[Block], title=None):
        self.blocks = blocks
        self.title = title
    
    def __str__(self):
        if self.title == None:
            string = "Title: [None]"
        else:
            string = f"Title: {self.title}"
        string += "Blocks:"
        for block in self.blocks:
            string += str(block) + "\n"
        return string