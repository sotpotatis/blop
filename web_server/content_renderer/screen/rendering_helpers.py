'''rendering_helpers.py
Helper functions for rendering content.
A good place to put code shared by different screen modules.'''
import re
def true_length(content):
    '''Retrieves the true length of content by ignoring special escape characters.

    (Thanks https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python for helping
    out with this one!)'''
    ansi_escapes_regex = re.compile("(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])")
    filtered_content = ansi_escapes_regex.sub("", content)
    return len(filtered_content)
