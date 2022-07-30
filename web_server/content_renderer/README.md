![skipper.png](skipper-logo.png)
### an HTML-like to raw string converter
skipper converts HTML-like documents to raw strings and/or classes that can be directly converted to raw strings.

this is done using a toolkit of converters as well as a "Screen" concept. 

skipper also includes a source loader that can load content from a filesystem or from HTTP/HTTPS.

##### small notes on subdirectories

* `from_html` includes the content renderer from HTML as well as the source loader mentioned above.
* `screen` includes classes with methods used for rendering text content. this includes custom code and classes for
buttons, scrollbars, a column system, and more.