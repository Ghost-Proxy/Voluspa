import os
import logging
from logging.handlers import RotatingFileHandler

from modules.config import CONFIG

# Logging
# TODO: Cleanup and consolidate / move to module...
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s:  %(message)s')

file_handler = RotatingFileHandler(
    filename=os.path.join(CONFIG.Voluspa.app_cwd, 'logs/voluspa.log'),
    encoding='utf-8',
    maxBytes=1024*1024*10,
    backupCount=10
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_formatter)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(log_formatter)

root_logger.addHandler(file_handler)
root_logger.addHandler(stream_handler)

LOGGER = logging.getLogger('voluspa')

