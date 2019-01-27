import os
import yaml

from modules.misc import merge_dicts, AttrDict


# Load in our secrets and config files
# config = configparser.ConfigParser()
def read_yaml(yaml_file):
    with open(yaml_file, 'r') as yfile:
        return yaml.load(yfile)


# TODO CLEANUP
def read_config():
    """
    Returns a nested config object for convenience

    Reads in ./config/secrets.yml in the format of config.yml for local dev env
    If ./config/secrets.yml is not present, they are pulled from env vars
    """
    file_config = read_yaml('./config/config.yaml')
    secrets_path = os.path.join(os.getcwd(), './config/secrets.yaml')
    print(f'Attempting to load secrets from: {secrets_path}')
    if os.path.isfile(secrets_path):
        print('Found secrets.yml, using local overrides...')
        secrets = read_yaml('./config/secrets.yaml')
    else:
        print('Local secrets.yml not found, pulling secrets from Env Vars...')
        secrets = {
            'Bungie': {
                'api_key': os.environ['BUNGIE_API_KEY'],
                'clan_group_id': os.environ['BUNGIE_CLAN_GROUP_ID'],
                'oauth_client_id': os.environ['BUNGIE_OAUTH_ID']
            },
            'Discord': {
                'api_key': os.environ['DISCORD_API_KEY']
            }}

    merged_config = merge_dicts(file_config, secrets)
    nested_config = AttrDict.from_nested_dict(merged_config)
    return nested_config


CONFIG = read_config()
CONFIG['app_cwd'] = os.path.abspath(os.getcwd())
