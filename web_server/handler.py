import socketserver, logging, socket, os
from content_renderer.from_html.format_translator import Translator
from web_server.const import *
from content_renderer.from_html.sourceloader import SourceLoader


class RequestHandler(socketserver.StreamRequestHandler):
    '''Handles a request that has been received by a client'''
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)
    translator = Translator()
    source_loader = SourceLoader(
        load_from_files=True,
        load_from_urls=True,
        trusted_directories=[HTML_CONTENT_DIRECTORY, WEBSITE_INDEX_HANDLER_DIRECTORY], #Only trust paths that are in the working directory
        trusted_urls=[] #Trust all
    )

    #Open a scene for reading
    START_FILE = os.path.join(WEBSITE_INDEX_HANDLER_DIRECTORY, "website_index_out.html")
    ERROR_INFO_FILE = os.path.join(HTML_CONTENT_DIRECTORY, "error_occurred.html") #File to print from in case of an error
    LOADING_FILE = os.path.join(HTML_CONTENT_DIRECTORY, "loading.html") #File to print from when content is loading
    ROOT_ERROR_FILE = os.path.join(HTML_CONTENT_DIRECTORY, "root_error.html") #File to print from in case of an internal error
    #Load some scenes that are used when the server is processing stuff or have other things to tell the user
    loading_screen_scene = source_loader.load_source_into_scene(LOADING_FILE)
    error_screen_scene = source_loader.load_source_into_scene(ERROR_INFO_FILE)
    root_error_scene = source_loader.load_source_into_scene(ROOT_ERROR_FILE)

    def handle(self):
        RequestHandler.logger.info("Received a request from a client!")
        #Load the start file
        self.scene = RequestHandler.source_loader.load_source_into_scene(RequestHandler.START_FILE)
        if self.scene == None:
            RequestHandler.logger.critical("Failed to load start file! An error will be returned.")
            self.scene = RequestHandler.root_error_scene
            self.current_loaded_source = RequestHandler.ROOT_ERROR_FILE
        else:
            self.current_loaded_source = RequestHandler.START_FILE

        #Wait for client input
        while True: #Run until further notice
            try:
                self.logger.info("Clearing screen...")
                self.wfile.write(CLEAR_SCREEN.encode()) #Clear the screen
                if self.current_loaded_source != self.scene.source or self.scene.force_reload:
                    self.logger.info("Updating scene to new source.")
                    #Show loading screen
                    self.wfile.writelines(RequestHandler.loading_screen_scene.get_terminal_lines())
                    try:
                        self.logger.info(f"Loading source from {self.scene.source}")
                        self.scene = RequestHandler.source_loader.load_source_into_scene(self.scene.source)
                        if self.scene == None:
                            raise Exception("Scene failed to be loaded.")
                        self.current_loaded_source = self.scene.source
                        self.logger.info("New scene loaded.")
                    except Exception as e:
                        self.logger.warning(f"Failed to load new file (the error {e} occurred). Displaying error...", exc_info=True)
                        self.scene = RequestHandler.error_screen_scene
                        self.current_loaded_source = RequestHandler.ERROR_INFO_FILE
                    continue
                image = self.scene.get_terminal_lines()
                self.logger.debug(f"New image: {image}")
                self.logger.info("Redrawing image...")
                self.wfile.writelines(self.scene.get_terminal_lines())
                #Wait for client input or image change
                encoded_data = self.rfile.readline().strip()
                received_data = encoded_data.decode()
                RequestHandler.logger.info(f"Received data: {received_data} (length {len(received_data)}) (unencoded: {encoded_data}).")
                if received_data == "":  # Translate to enter key
                    RequestHandler.logger.info("Translated empty data to enter key.")
                    encoded_data = KEY_ENTER
                if KEY_COMBINATION_CTRL_C in received_data: #Change source on Ctrl+C
                    RequestHandler.logger.info("Found Ctrl+C. Resetting scene...")
                    self.scene.source = RequestHandler.START_FILE #Reset source to the original landing page.
                    continue
                if KEY_ESCAPE == received_data or KEY_COMBINATION_CTRL_Q in received_data: #Close connection on escape or Ctrl + Q
                    RequestHandler.logger.info("Received escape key. Closing connection....")
                    break
                if len(encoded_data.split()) != 0: #Split encoded data if we can
                   encoded_data = encoded_data.split()
                for received_key in encoded_data:
                    #Update image according to client input
                    self.scene.update(received_key)
            except socket.error:
                RequestHandler.logger.info("Client disconnected.")
                break
