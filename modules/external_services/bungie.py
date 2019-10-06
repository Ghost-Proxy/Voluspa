import logging
from typing import Any, List, Dict, Tuple, Sequence, Iterable

from modules.config import CONFIG
from modules.async_request import async_request_handler
from modules.exceptions import BungieAPIError, BungieAPIOffline

logger = logging.getLogger('voluspa.bungie_requests')


async def async_bungie_request_handler(target_endpoint, request_url=None, params=None, response_handler=None):
    bungie_platform_url = 'https://www.bungie.net/platform'
    _request_url = f'{request_url}{target_endpoint}' if request_url else f'{bungie_platform_url}{target_endpoint}'
    resp = await async_request_handler(_request_url,
                                       target_endpoint,
                                       headers={'X-API-Key': CONFIG.Bungie.api_key},
                                       params=params,
                                       response_handler=response_handler
                                       )
    if resp['status'] == 200:
        logger.info('Bungie request was successful!')
        logger.info(f'Bungie response: {resp["content"]}')  # TODO: Remove
        return resp['content']
    elif resp['status'] == 504:
        logger.info('Bungie API appears to be offline!')
        raise BungieAPIOffline
    else:
        logger.info('An unknown Bungie API occurred... ')
        raise BungieAPIError
