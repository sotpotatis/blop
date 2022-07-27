# website creation guide
how to create a website for blop.

> **techincal note:** since i call the rendering code for the platform for "skipper",
> this is technically a documentation of skipper's capabilities.

### the basics

#### intro
websites are written using HTML and they are also accessed like "regular" HTTP/HTTPS sites.
this makes it technically possible to convert already existing websites to work with blop - 
however, backwards-compatibility with web standards is not the main intent and therefore the
selection of styles is limited.

#### writing your HTML content
first of all - if you know HTML, you know how to create websites that skipper and blop understands. 
period. 

when writing content, you have to be *limited*. this is for the terminal, and therefore there are no
fancy javascript processing, and **css stylesheets (style sheets) are not currently supported.**
**use inline styles (more below)***

##### tags
below is a full list of supported tags:

**in body:**

| Tag name        | Supported features     | Example                                                      |
|-----------------|------------------------|--------------------------------------------------------------|
| p               | text coloring          | `<p style="color: blue">Hello</p>`                           |
| span            | text coloring          | `<span style="color: blue">Hello</p>`                        |
| h1, h2, ..., h6 | text coloring          | `<p style="color: blue">Hello</p>`                           |
| hr              | coloring, width        | `<p style="color: blue">Hello</p>`                           |
| a               | coloring, width        | `<button data-link="https://example.com">Click me!</button>` |
| button          | coloring, width, linking | `<a data-link="https://example.com">Click me!</a>`           |
| ul, li          | coloring          | `<ul><li>List item</li></ul>`                                |
| input           | coloring, width        | `<p style="color: blue">Hello</p>`                           |
| form            | coloring, width        | See [Form input](#forms)                                     |
| label           | coloring, width        | `<label for="some_id" style="color: blue">Input:</p>`        |

**in head:**

| Tag name | Supported features | Example                        |
|----------|--------------------|--------------------------------|
| title    | N/A*               | `<title>Website title</title>` |
<small>*=no special features (styling etc.) apart from rendering the title (of course)</small>

##### styling

**use styles as in inline CSS for styling your content.
styling with external stylesheets nor by classes, ids, or selectors
are not currently supported.**

here is an example of proper styling:

```html
<p style="color:blue;">This text will be blue in the terminal</p>
```

the tags that are supported all across the different tags are color tags, but width tags are supported
in most tags too.

##### list references for styling

###### list of supported colors

the color set is limited to the colors of a 16-color-terminal:
* black
* red
* green
* yellow
* blue
* magenta
* cyan
* white

###### list of other supported text styling

> **Note:** Some of these might not be supported in all terminals.

*strikethrough*
* use `text-decoration: line-through;` for strikethrough text 

*bold text*
* use `font-weight: bold;`, `font-style: bold;`, or `font-weight: 700;` for bold text.

*italic text*
* use `font-style: italic;` for italic text

<a name="forms"></a>
##### receiving user input data

blop supports sending data via *forms*. this is showcased in the example [Veronica chat app](web_server/example_servers/chat_app).

let's begin with a basic example of a supported form:

```html
<form action="https://example.com/data" method="post" data-send-from-terminal="true">
    <label for="input_text">Write something:</label>
    <input id="input_text" type="text" data-include-in-payload="true">
    <button type="submit">Send!</button>
</form>
```
as you can see in the example, a form for sending data looks really like a conventional HTML form, but there are some differences:
* first of all, the form has to include a `data-send-from-terminal` attribute set to exactly `true` *directly* on the form tag.
* and also, *each* data source you want included  in the payload must have the `data-include-in-payload` attribute set to exactly `true`.
* all input forms you want to include in the data sent must have a unique id. a name is preferred too since some servers
use that for handling.
* do not return data when the form has been posted, either:
  * return an OK response and make sure any content on the base URL updates.
    (if the website posted to the page `/form` from `/index.html` for example, you return `200`
  and this will make the content loader re-query `/index.html` again, where you can provide updated content)
  * return a redirect to where the server can find the updated content instead.
  the returned URL will be retrieved after posting the form.
* relative paths in the "action" field of the form is not supported yet - include the base URL (do: `method="https://example.com/data"`, don't `method="/data"`).
* **important:** if the criteria above are not true, the form will not be sent to your server!

data will be sent to the server as a *url encoded form*.
you can (and should) validate the user agent. it's
`Python/SceneServer`.

so, **a checklist for writing a receiving server is something like:**
 
[] create a template that fulfills the requirements above

[] respond to post requests at the same URL as in the form's `method` parameter (required)

[] validate that the `User-Agent` is `Python/SceneServer` (recommended)

[] get the form data and do stuff with it (required)

[] do one of the following:
  * return an OK response but note that the client will ignore any content sent and re-query the base URL.
  * return a `301 Moved Permanentely`, `303 See Other`, or `307 Temporary Redirect` to a resource where updated content can be found.

**example request**

for helping you with form implementation, here is a [httpbin](https://httpbin.org) response when posting the default form in
[form testing server](web_server/example_servers/form_testing_server/index.html).
```json
{
  "args": {}, 
  "data": "", 
  "files": {}, 
  "form": {
    "text_1": "", 
    "text_2": "", 
    "text_3": ""
  }, 
  "headers": {
    "Accept": "*/*", 
    "Accept-Encoding": "gzip, deflate", 
    "Content-Length": "23", 
    "Content-Type": "application/x-www-form-urlencoded", 
    "Host": "httpbin.org", 
    "User-Agent": "Python/SceneServer", 
    "X-Amzn-Trace-Id": "Root=1-62e03ac5-2e0eed1767acbd764f6XXXXX"
  }, 
  "json": null, 
  "origin": "XX.XXX.XXX.XX", 
  "url": "http://httpbin.org/post"
}
```
#### when your website is done

after you have created your website, you have to register it in the [website index](web_server/website_index_handler/README.md) to make it appear
in the blop start page. this is also the easiest way to test your website. don't worry, registration is easy and there
are even example code with minimal set up required available, see the instructions [here](web_server/website_index_handler/README.md).

if you want to test your website locally, you can also try running blop locally. there are some instructions available in [README.md](README.md).

#### best practises

here are some best practises when creating a website.
it's recommended that you follow these or at least take note
of them to build a great user experience.

* **include instructions to the user on how to navigate the website.**
write out clear instructions like "type your text and hit enter to fill this textbox".
you will see this represented in the default pages used by blop. while there is a guide at the beginning,
the navigation concept might be difficult to grasp at first.
* even though skipper can handle this, **it's recommended to keep the terminal sizing
of width 60 and height 80 (characters)** in mind. the height is scrollable, but not the width.
* **use the supported tags to as great extent as possible.** other tags will just be rendered by
extracting the pure text from them, which can risk your content to look weird. and also, since that is the case,
you could just use the supported `<span>` tag.

#### also see

see the [example websites](web_server/example_servers) for lot of example HTML files for styling content.