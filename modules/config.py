"""Voluspa Dynamic Configuration"""

import os
import datetime

import yaml

# import functools
# @functools.lru_cache()

from modules.misc import merge_dicts, memoize
from config.cache_config import CACHE_CONFIG

VOLUSPA_VERSION = 'v0.2.1'

# Load in our secrets and config files
# config = configparser.ConfigParser()
def read_yaml(yaml_file):
    """Reads the YAML config file and returns the yaml fully loaded"""
    with open(yaml_file, 'r', encoding='utf8') as yfile:
        return yaml.full_load(yfile)


def bool_converter(value) -> bool:
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
def read_and_build_config():
    """
    Returns a nested config object for convenience

    Reads in ./config/secrets.yml in the format of config.yml for local dev env
    If ENV VARS are present, they will override secrets.yml
    """
    # TODO: This is convoluted...
    file_config = read_yaml('./config/config.yaml')

    print('Setting Voluspa boot settings...')
    if sha:= os.getenv('SOURCE_VERSION'):
        sha = sha[:10]
    else:
        sha = 'Unknown (local?)'

    voluspa_info: dict[str, dict[str, str]] = {
        'Voluspa': {
            'version': VOLUSPA_VERSION,
            'sha': sha,
            'app_cwd': os.path.abspath(os.getcwd()),
            'boot_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }

    merged_config_1 = merge_dicts(file_config, voluspa_info)
    # merged_config_1a = file_config | voluspa_info

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

    secrets_path: str = os.path.join(os.getcwd(), './config/secrets.yaml')
    print('Attempting to load secrets from file...')
    if os.path.isfile(secrets_path):
        print('Found secrets.yml loading...')
        secrets_file = read_yaml('./config/secrets.yaml')
        secrets = merge_dicts(secrets_file, env_secrets, skip_none=True)
    else:
        secrets = env_secrets

    # Pick up Voluspa named Env Vars
    if 'Voluspa' not in secrets:
        secrets['Voluspa'] = {}
    voluspa_config: list[str] = ['VOLUSPA_PREFIX', 'VOLUSPA_FEEDBACK_CHANNEL_ID', 'VOLUSPA_PRIVATE_GUILD_CHANNEL_ID']
    for vol_env in voluspa_config:
        if os.getenv(vol_env):
            secrets['Voluspa'][vol_env.split('_', maxsplit=1)[1].lower()] = getenv_cast(vol_env)

    # ADDITIONAL CONFIG
    # Handle cache
    secrets['Voluspa']['fancy_name'] = 'Völuspá'
    secrets['Voluspa']['cache'] = CACHE_CONFIG

    merged_config_final = merge_dicts(merged_config_1, secrets)
    # merged_config_final2 = merged_config_1 | secrets

    if not merged_config_final['Resources']['image_bucket_root_url']:
        merged_config_final['Resources'] = {'image_bucket_root_url': os.getenv('IMAGE_BUCKET_ROOT_URL', '')}

    return merged_config_final

CONFIG = memoize(read_and_build_config)()
