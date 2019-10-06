import logging
from typing import Any, List, Dict, Tuple, Sequence, Iterable

import aiohttp

logger = logging.getLogger('voluspa.async_request_handler')


async def async_request_handler(base_url, target_endpoint, headers=None, params=None, response_handler=None):
    _headers = headers if headers else {}
    _params = params if params else {}
    _url = f'{base_url}{target_endpoint}'
    logger.info(f'Attempting request for URL [params]: {_url} -- [{_params}]')
    async with aiohttp.ClientSession() as session:
        async with session.get(_url, headers=_headers, params=_params) as r:
            if r.status == 200:
                raw_json = await r.json()
                if response_handler:
                    try:
                        response_handler(r)
                    except Exception as e:
                        raise e
                else:
                    return {'status': r.status, 'content': raw_json}
            else:
                logger.info(f'ERROR for {target_endpoint}\n'
                            f'Response was: [status {r.status}] {await r.text()}')
                return {'status': r.status, 'content': None}
