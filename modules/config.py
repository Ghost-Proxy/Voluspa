import os
import yaml
import datetime
# import functools
# @functools.lru_cache()

from modules.misc import merge_dicts, AttrDict
from config.cache_config import CACHE_CONFIG


# Load in our secrets and config files
# config = configparser.ConfigParser()
def read_yaml(yaml_file):
    with open(yaml_file, 'r') as yfile:
        return yaml.full_load(yfile)


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
            'sha': os.getenv('SOURCE_VERSION', 'Unknown'),
            'app_cwd': os.path.abspath(os.getcwd()),
            'boot_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }

    merged_config_1 = merge_dicts(file_config, voluspa_info)
    print(f'Merged Config:\n{merged_config_1}')

    secrets_path = os.path.join(os.getcwd(), './config/secrets.yaml')
    print(f'Attempting to load secrets from: {secrets_path}')
    if os.path.isfile(secrets_path):
        print('Found secrets.yml loading...')
        secrets_file = read_yaml('./config/secrets.yaml')

    print('Pulling secrets from Env Vars...')
    env_secrets = {
        'Bungie': {
            'api_key': os.environ['BUNGIE_API_KEY'],
            'clan_group_id': os.environ['BUNGIE_CLAN_GROUP_ID'],
            'oauth_client_id': os.environ['BUNGIE_OAUTH_ID']
        },
        'Discord': {
            'api_key': os.environ['DISCORD_API_KEY']
        },
    }

    secrets = merge_dicts(secrets_file, env_secrets, skip_none=True)

    # Pick up Voluspa named Env Vars
    voluspa_config = ['VOLUSPA_PREFIX']
    for ve in voluspa_config:
        if os.getenv(ve):
            secrets['Voluspa'] = {ve.split('_')[1].lower(): os.getenv(ve)}

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

    print(f'Voluspa merged config -- Resources:\n{nested_config.Resources}')
    print(f'Voluspa merged config -- Voluspa:\n{nested_config.Voluspa}')

    return nested_config


def memoize(func):
    # Guarantees that the initial call to config is the same config over the lifetime of the app, in theory
    cache = dict()

    def memoized_func(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result

    return memoized_func


memozied_config = memoize(read_config)
CONFIG = memozied_config()
