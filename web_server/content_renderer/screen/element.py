from typing import List

class Justify:
    '''Justify a row with columns to a certain position'''
    CENTER = "center"
    START = "start"
    END = "end"
    
class Column:
    def __init__(self, elements:List):
        '''Inspired by the way HTML-websites have grids.
        Column elements will be placed in the same position vertically.

        :param elements: A list of elements in the row. The only requirement for an element
        is that it is a string or has a str()-convertible format.'''
        self.elements = elements
        self.id_to_element = {} #Mapping: ID (if element has one) to an element that belongs to the ID
        #Generate row string
        # Determine spacing between elements
        self.row_string = ""
        all_column_rows = []
        self.max_column_row_length = 0
        for element in self.elements: #Find biggest element
            element_rows = str(element).split("\n")
            all_column_rows.append(element_rows)
            if len(element_rows) > self.max_column_row_length:
                self.max_column_row_length = len(element_rows)
            if hasattr(element, "id"): #Add to element ID mapping
                self.id_to_element[element.id] = element

class Row:
    def __init__(self, columns:List[Column], screen_width:int=80, screen_height:int=64, justify_x:Justify=None, justify_y:Justify=None, scrollbar_width=1):
        '''Inspired by the way HTML-websites have grids.
        Row elements will be placed in the same position vertically.

        :param columns: A list of columns in the row.

        :param screen_width: Width of the row.

        :param screen_height: Height of the row.
        
        :param justify_x: Where to X-justify the row
        
        :param justify_y: Where to Y-justify the row

        :param scrollbar_width: Whether to make place for a scrollbar or not (scrollbar_width>0),
        and if true, how big (wide) the scrollbar should be.'''
        self.columns = columns
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.justify_x = justify_x
        self.justify_y = justify_y
        self.scrollbar_width = scrollbar_width

    def __str__(self):
        #Generate row string
        self.row_string = ""
        after = []
        all_column_rows = []
        self.max_column_row_length = 0
        # Determine spacing between elements
        if self.justify_x == Justify.CENTER:  # Add two blank columns
            self.columns.insert(0, Column([""]))
            self.columns.append(Column([""]))
        elif self.justify_x == Justify.END: #Add one blank column
            self.columns.insert(0, Column([""]))
        if len(self.columns) > 0:
            width_per_element = round((self.screen_width-self.scrollbar_width) / len(self.columns))
        else: #Prevent division by zero
            width_per_element = round(self.screen_width-self.scrollbar_width)
        for column in self.columns:
            column_rows = []
            for element in column.elements: #Find biggest element in the column
                element_str = str(element)
                element_rows = [] #Rows for the individual element
                for row in element_str.split("\n"):
                    #Split the element if it is too big
                    #...if we can, we don't want buttons to be able to do this because it'll look funky.
                    #So, determine what we can do here
                    if len(row) > width_per_element:
                        if not hasattr(element, "splittable") or element.splittable:
                            parsed_rows = []
                            i = 1
                            char_buffer = ""
                            for char in row:
                                if i < width_per_element and char != "\n":
                                    char_buffer += char
                                else:
                                    parsed_rows.append(char_buffer)
                                    char_buffer = char
                                    i = 1
                                i += 1
                            if i > 1: #Add remaining characters
                                parsed_rows.append(char_buffer)
                        else: #Clip the row
                            parsed_rows = [row[:width_per_element]]
                    else:
                        parsed_rows = [row]
                    element_rows.extend(parsed_rows)
                column_rows.extend(element_rows)
            #Check if max column length has been passed
            if len(column_rows) > self.max_column_row_length:
                self.max_column_row_length = len(column_rows)
            all_column_rows.append(column_rows)
        #Now, draw row content by iterating over the column content.
        for row_number in range(1, self.max_column_row_length+1):
            for column_rows in all_column_rows:
                #Check if column has a row for this row number, if not, fill with blank space
                if len(column_rows) >= row_number:
                    element = column_rows[row_number-1]
                    element_str = str(element)
                    #Add whitespace to fill other characters
                    if len(element_str) < width_per_element:
                        element_str += " "*(width_per_element - len(element_str))
                else: #Add empty space if element does not have content for the current row
                    element_str = " "*width_per_element
                self.row_string += element_str
            self.row_string += "\n"
        return self.row_string
            
