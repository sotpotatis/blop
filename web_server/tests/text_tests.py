import time
from sys import stdout
TO_COORDINATE = "\x1b[{};{}H"  # (row, column)

stdout.write("".join([str(i) for i in range(100)]))
stdout.flush()
stdout.write((TO_COORDINATE.format(5, 50)))
stdout.flush()
#time.sleep(9999)

text = """Welcome to iviweb!                                                     

iviweb is an internet implementation - in your terminal!                    

Navigate pages using arrow keys. Fill input boxes by typing.                

Psst! More detailed documentation is available at https://github.com/sotpotatis/

Enter which website to navigate to:                                     

                                                                            
        ------------------                                                      
        |uuuuuuuuuuuuuuuuuuuu|                                                  
        ------------------                                                      
                                                                            
                                                                                

Press enter on your keyboard to go to the website.                          


"""
print(text[491:600])