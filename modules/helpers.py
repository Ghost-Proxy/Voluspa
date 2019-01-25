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
    """ Returns a nested config object for convenience """
    file_config = read_yaml('./config/config.yaml')
    if os.path.isfile(os.path.join(os.getcwd(), './secrets/secrets.yaml')):
        secrets = read_yaml('./secrets/secrets.yaml')
    else:
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
