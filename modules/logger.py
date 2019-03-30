import os
import logging
from logging.handlers import RotatingFileHandler

from modules.config import CONFIG


def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s:  %(message)s')

    # TODO if on heroku, don't run file logger?
    log_file_path = os.path.join(CONFIG.Voluspa.app_cwd, 'logs/voluspa.log')
    print(f'Bootstrap - Setting logger path to: [{log_file_path}]')
    file_handler = RotatingFileHandler(
        filename=log_file_path,
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

    logger = logging.getLogger('voluspa')
    logger.info('Logging online!')
    logger.info(f'Log file [{"exists" if os.path.isfile(log_file_path) else "does NOT exist"}] at: [{log_file_path}]')
    return logger

