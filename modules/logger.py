import os
import logging
from logging.handlers import RotatingFileHandler

from modules.config import CONFIG


def log_to_channel(log_channel, log_msg):
    """For logging messages to a Discord channel also... WIP"""
    pass


def _setup_logging(log_level=logging.INFO):
    logging.getLogger().handlers.clear()
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s:  %(message)s')

    # TODO if on heroku, don't run file logger?
    log_file_path = os.path.join(CONFIG.Voluspa.app_cwd, 'logs/root.log')
    print(f'Bootstrap - Setting logger path to: [{log_file_path}]')
    file_handler = RotatingFileHandler(
        filename=log_file_path,
        encoding='utf-8',
        maxBytes=1024*1024*10,
        backupCount=10
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(log_formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(log_formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(log_level)
    discord_log_file_path = os.path.join(CONFIG.Voluspa.app_cwd, 'logs/discord.log')
    discord_file_handler = RotatingFileHandler(
        filename=discord_log_file_path,
        encoding='utf-8',
        maxBytes=1024*1024*10,
        backupCount=10
    )
    discord_file_handler.setFormatter(log_formatter)
    discord_logger.addHandler(discord_file_handler)

    voluspa_logger = logging.getLogger('voluspa')
    voluspa_log_file_path = os.path.join(CONFIG.Voluspa.app_cwd, 'logs/voluspa.log')
    voluspa_file_handler = RotatingFileHandler(
        filename=voluspa_log_file_path,
        encoding='utf-8',
        maxBytes=1024*1024*10,
        backupCount=10
    )
    voluspa_file_handler.setLevel(log_level)
    voluspa_file_handler.setFormatter(log_formatter)

    voluspa_logger.info('Logging online!')
    voluspa_logger.info(f'Log file [{"exists" if os.path.isfile(log_file_path) else "does NOT exist"}] at: [{log_file_path}]')
    voluspa_logger.info(f'Log file [{"exists" if os.path.isfile(discord_log_file_path) else "does NOT exist"}] at: [{discord_log_file_path}]')
    voluspa_logger.info(f'Log file [{"exists" if os.path.isfile(voluspa_log_file_path) else "does NOT exist"}] at: [{voluspa_log_file_path}]')
    return voluspa_logger


class Archivist(object):
    logger = _setup_logging()

    def __init__(self):
        self.logger = Archivist.logger

    def get_logger(self):
        return self.logger
