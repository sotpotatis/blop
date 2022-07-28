import socketserver, logging, os
from const import SUPERBRAIN_LOGO_ASCII, LOGGING_LEVEL_STR_TO_LEVEL
from handler import RequestHandler
logger = logging.getLogger(__name__)
#Determine global logging level
if not os.getenv("SUPERBRAIN_LOG_LEVEL") in LOGGING_LEVEL_STR_TO_LEVEL:
    logging_level = logging.DEBUG
else:
    logging_level = LOGGING_LEVEL_STR_TO_LEVEL[os.getenv("SUPERBRAIN_LOG_LEVEL")]
logging.basicConfig(level=logging_level)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    '''Threaded server using documentation from https://docs.python.org/3/library/socketserver.html'''
    daemon_threads = True

if __name__ == "__main__":
    #Get server information
    SERVER_HOST = os.environ["TELNET_SERVER_HOST"]
    SERVER_PORT = int(os.environ["TELNET_SERVER_PORT"])
    logger.info(f"""
    {SUPERBRAIN_LOGO_ASCII}
    Ohoy, my lovely friends! This is the superbrain octopus! My lovely ship is about to sail ashore out to the internet...
    """)
    with ThreadedTCPServer((SERVER_HOST, SERVER_PORT), RequestHandler) as server:
        logger.info(f"Running Telnet server on {SERVER_HOST}:{SERVER_PORT} until close...")
        server.serve_forever()