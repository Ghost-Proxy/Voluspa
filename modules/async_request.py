"""Async Request Module"""

import logging

import aiohttp

logger = logging.getLogger('voluspa.async_request_handler')


async def async_request_handler(base_url, target_endpoint, headers=None, params=None, response_handler=None):
    """Unified Async request handler"""
    _headers = headers if headers else {}
    _params = params if params else {}
    _url = f'{base_url}{target_endpoint}'
    logger.info('Attempting request for URL [params]: %s -- %s', _url, _params)
    async with aiohttp.ClientSession() as session:
        async with session.get(_url, headers=_headers, params=_params) as resp:
            if resp.status == 200:
                raw_json = await resp.json()
                if response_handler:
                    try:
                        response_handler(resp)
                    except Exception as exc:
                        raise exc
                else:
                    return {'status': resp.status, 'content': raw_json}
            else:
                logger.info('ERROR for %s\n'
                            'Response was: [status %s] %s', target_endpoint, resp.status, (await resp.text()))
                return {'status': resp.status, 'content': None}
