"""Voluspa Dynamic Configuration"""

import os
import datetime

import yaml

# import functools
# @functools.lru_cache()

from modules.misc import merge_dicts, AttrDict, memoize
from config.cache_config import CACHE_CONFIG


# Load in our secrets and config files
# config = configparser.ConfigParser()
def read_yaml(yaml_file):
    """Reads the YAML config file and returns the yaml fully loaded"""
    with open(yaml_file, 'r', encoding=str) as yfile:
        return yaml.full_load(yfile)


def bool_converter(value):
    """Handles casting common string values for booleans"""
    if value.lower() in ['true', 1, 'yes', 'on', 'y']:
        return True
    if value.lower() in ['false', 0, 'no', 'off', 'n']:
        return False
    raise TypeError


def cast_to_native_type(value):
    """Attempts to cast values to native types"""
    if value is None:
        return value
    supported_types = [int, float, bool_converter]  # haha, bool() is too greedy
    for _type in supported_types:
        try:
            return _type(value)
        except (TypeError, ValueError):
            pass
    return value


def getenv_cast(env_var, default=None):
    """Gets the requested env var and attempts to cast it to native type"""
    return cast_to_native_type(os.getenv(env_var, default))


# TODO CLEANUP
def read_config():
    """
    Returns a nested config object for convenience

    Reads in ./config/secrets.yml in the format of config.yml for local dev env
    If ENV VARS are present, they will override secrets.yml
    """
    # TODO: This is convoluted...
    file_config = read_yaml('./config/config.yaml')

    print('Setting Voluspa boot settings...')
    voluspa_info = {
        'Voluspa': {
            'version': 'v0.0.13',
            'sha': os.getenv('SOURCE_VERSION')[:10] if os.getenv('SOURCE_VERSION') else 'Unknown (local?)',
            'app_cwd': os.path.abspath(os.getcwd()),
            'boot_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }

    merged_config_1 = merge_dicts(file_config, voluspa_info)
    # print(f'Merged Config:\n{merged_config_1}')

    secrets_path = os.path.join(os.getcwd(), './config/secrets.yaml')
    secrets_file = None
    print('Attempting to load secrets from file...')
    if os.path.isfile(secrets_path):
        print('Found secrets.yml loading...')
        secrets_file = read_yaml('./config/secrets.yaml')

    print('Pulling secrets from Env Vars...')
    env_secrets = {
        'Bungie': {
            'api_key': getenv_cast('BUNGIE_API_KEY'),
            'clan_group_id': getenv_cast('BUNGIE_CLAN_GROUP_ID'),
            'oauth_client_id': getenv_cast('BUNGIE_OAUTH_ID')
        },
        'Discord': {
            'api_key': getenv_cast('DISCORD_API_KEY')
        },
        'Github': {
            'token': getenv_cast('GITHUB_TOKEN'),
            'repo_name': getenv_cast('GITHUB_REPO_NAME')
        }
    }

    if secrets_file:
        secrets = merge_dicts(secrets_file, env_secrets, skip_none=True)
    else:
        secrets = env_secrets

    # Pick up Voluspa named Env Vars
    if 'Voluspa' not in secrets:
        secrets['Voluspa'] = {}
    voluspa_config = ['VOLUSPA_PREFIX', 'VOLUSPA_FEEDBACK_CHANNEL_ID', 'VOLUSPA_PRIVATE_GUILD_CHANNEL_ID']
    for vol_env in voluspa_config:
        if os.getenv(vol_env):
            secrets['Voluspa'][vol_env.split('_', maxsplit=1)[1].lower()] = getenv_cast(vol_env)

    # ADDITIONAL CONFIG
    # Handle cache
    secrets['Voluspa']['fancy_name'] = 'Völuspá'
    secrets['Voluspa']['cache'] = CACHE_CONFIG

    merged_config_2 = merge_dicts(merged_config_1, secrets)

    nested_config = AttrDict.from_nested_dict(merged_config_2)
    # Add resources from env
    # TODO Redo this flow...
    if not nested_config.Resources.image_bucket_root_url:
        nested_config.Resources.image_bucket_root_url = os.getenv('IMAGE_BUCKET_ROOT_URL', '')

    #print(f'Voluspa merged config -- Resources:\n{nested_config.Resources}')
    #print(f'Voluspa merged config -- Voluspa:\n{nested_config.Voluspa}')

    return nested_config


memozied_config = memoize(read_config)
CONFIG = memozied_config()
