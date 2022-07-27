from format_translator import Translator
import logging
logging.basicConfig(level=logging.DEBUG)
t = Translator()
html_content = open("../../html_content/example_file.html", "r")
broken_down_file = t.break_down(html_content)
print(broken_down_file)