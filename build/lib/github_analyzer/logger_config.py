import logging
import sys


def setup_logger(debug_mode: bool = False, log_to_file: bool = False):
    log_level = logging.DEBUG if debug_mode else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    handler = logging.FileHandler('app.log') if log_to_file else logging.StreamHandler(stream=sys.stdout)
    logging.basicConfig(level=log_level,
                        format=log_format,
                        handlers=[handler])
