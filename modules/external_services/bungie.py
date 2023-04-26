"""External Services Module"""

import logging
from typing import Any

from modules.config import CONFIG
from modules.async_request import async_request_handler
from modules.exceptions import BungieAPIError, BungieAPIOffline

logger: logging.Logger = logging.getLogger('voluspa.bungie_requests')


async def async_bungie_request_handler(
        target_endpoint,
        request_url=None,
        params=None,
        response_handler=None) -> Any | None:
    """Unified Bungie request handler"""

    bungie_platform_url = 'https://www.bungie.net/Platform'
    _request_url: str = request_url if request_url else bungie_platform_url

    resp = await async_request_handler(
        _request_url,
        target_endpoint,
        headers={'X-API-Key': CONFIG['Bungie']['api_key']},
        params=params,
        response_handler=response_handler
        )

    if resp:
        if resp['status'] == 200:
            logger.info('Bungie request was successful!')
            logger.info('Bungie response: %s', resp["content"])
            return resp['content']

        if resp['status'] == 504:
            logger.info('Bungie API appears to be offline!')
            raise BungieAPIOffline

        logger.info('An unknown Bungie API occurred... ')
        raise BungieAPIError
