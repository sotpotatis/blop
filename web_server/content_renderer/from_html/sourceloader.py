'''sourceloader.py
Loads an HTML-style source file from directory or from the web.'''
import logging
import os, requests, re, ntpath
from typing import List
from .format_translator import Translator

IS_URL_REGEX = re.compile("https*:\/\/([A-Za-z].)+.[A-Za-z]+(:[0-9]{1,5})?(\/.+)*") #Regex to match URLs

class SourceLoader():
    def __init__(self, load_from_files:bool, load_from_urls:bool, trusted_directories:List[os.PathLike], trusted_urls:List[str], restrict_filepaths:bool=True, restrict_urls:bool=False):
        '''Initializes an HTML source loader.

        :param load_from_files: Whether to load sources from file storage or not.

        :param load_from_urls: Whether to load sources from external URLs or not.

        :param trusted_directories: Which directories to trust data from.

        :param trusted_urls: Which URLs to trust data from.

        :param restrict_filepaths: If True, the trusted_directories values will be applied for directories to trust.

        :param restrict_urls: If True, the trusted_urls values will be applied for URLs to trust.
        '''
        self.load_from_files = load_from_files
        self.load_from_urls = load_from_urls
        self.trusted_directories = trusted_directories
        self.trusted_urls = trusted_urls
        self.restrict_filepaths = restrict_filepaths
        self.restrict_urls = restrict_urls
        self.logger = logging.getLogger(__name__)

    def load_source_content(self, source_string):
        '''Loads a source's content.

        :param source_string: A source: This could be a file path or a URL.'''
        self.logger.info(f"Loading content from: {source_string}...")
        if IS_URL_REGEX.fullmatch(source_string):
            self.logger.debug("Source is URL. Validating source...")
            if self.load_from_urls and not (self.restrict_urls and source_string not in self.trusted_urls):
                self.logger.info("Source URL is valid. Loading from it...")
                try:
                    return requests.get(source_string, headers={"User-Agent": "Python/SourceFileContentLoader"}).text
                except Exception as e:
                    self.logger.warning(f"Can not load source from {source_string} - Request to {source_string} failed. ({e})", exc_info=True)
            else:
                self.logger.warning(f"Can not load source from {source_string} - restricted by security settings.")
        else:
            self.logger.debug("Source is file. Checking path validity...")
            if os.path.exists(source_string):
                #Get directory name
                source_path = os.path.normpath(source_string)
                directory_name = os.path.dirname(source_string)
                if self.load_from_files and not (self.restrict_filepaths and directory_name not in self.trusted_directories):
                    self.logger.info("Source filepath is valid. Loading from it...")
                    try:
                        return open(source_path, "r").read()
                    except Exception as e:
                        self.logger.warning(f"Can not load from {source_string} - exception occurred ({e})", exc_info=True)
                else:
                    self.logger.warning(f"Can not load source from {source_string} - is restricted by security settings.")
            else:
                self.logger.warning(f"Can not load {source_string} - path does not exist.")
        return

    def load_source_into_scene(self, source):
        '''Executes load_source_content() and then tries to load that content
        into a Scene()'''
        self.logger.debug(f"Loading {source} into a scene...")
        content = self.load_source_content(source)
        self.format_translator = Translator()
        if content != None:
            try:
                return self.format_translator.to_scene(content, source=source)
            except Exception as e:
                self.logger.warning(f"Failed loading {source} into a scene - the exception {e} occurred.", exc_info=True)
        else:
            self.logger.warning("Got None as content response.")