import os
import yaml
import datetime

from modules.misc import merge_dicts, AttrDict


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
    If ./config/secrets.yml is not present, they are pulled from env vars
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
            },
        }

        voluspa_config = ['VOLUSPA_PREFIX', 'VOLUSPA_FEEDBACK_CHANNEL_ID']
        for ve in voluspa_config:
            if os.getenv(ve):
                secrets['Voluspa'] = {ve.split('_')[1].lower(): os.getenv(ve)}

    merged_config_2 = merge_dicts(merged_config_1, secrets)

    nested_config = AttrDict.from_nested_dict(merged_config_2)
    # Add resources from env
    # TODO Redo this flow...
    if not nested_config.Resources.image_bucket_root_url:
        nested_config.Resources.image_bucket_root_url = os.getenv('IMAGE_BUCKET_ROOT_URL', '')

    print(f'Voluspa merged config -- Resources:\n{nested_config.Resources}')
    print(f'Voluspa merged config -- Voluspa:\n{nested_config.Voluspa}')

    return nested_config


CONFIG = read_config()
