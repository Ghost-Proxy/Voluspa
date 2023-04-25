"""Fun Module"""

import logging
import random
import re

import requests
import aiohttp

logger = logging.getLogger('voluspa.modules.fun')


async def get_latest_xkcd_comic():
    """Get and display the latest xkcd comic"""
    xkcd_index_url = 'https://xkcd.com/info.0.json'
    async with aiohttp.ClientSession() as session:
        async with session.get(xkcd_index_url) as resp:
            if resp.status == 200:
                latest_xkcd_comic = await resp.json()
                latest_xkcd_num = latest_xkcd_comic['num']
                return latest_xkcd_num, latest_xkcd_comic


async def get_xkcd_comic_num(num: int = 1):
    """Get the specific xkcd comic via request number"""
    xkcd_url = f'https://xkcd.com/{num}/info.0.json'
    async with aiohttp.ClientSession() as session:
        async with session.get(xkcd_url) as resp:
            if resp.status == 200:
                xkcd_comic = await resp.json()
                return xkcd_comic


async def get_xkcd_comic(latest=False):
    """Get an xkcd comic"""
    latest_xkcd_num, latest_xkcd_comic = await get_latest_xkcd_comic()

    # {
    #     "month": "12",
    #     "num": 2085,
    #     "link": "",
    #     "year": "2018",
    #     "news": "",
    #     "safe_title": "arXiv",
    #     "transcript": "",
    #     "alt": "Both arXiv and archive.org are invaluable projects which, if they didn't exist, we would dismiss as obviously ridiculous and unworkable.",
    #     "img": "https://imgs.xkcd.com/comics/arxiv.png",
    #     "title": "arXiv",
    #     "day": "14"
    # }

    if not latest:
        rand_idx = random.randint(1, latest_xkcd_num)
        original_xkcd_url = f'http://xkcd.com/{rand_idx}'
        xkcd_comic = await get_xkcd_comic_num(rand_idx)
    else:
        original_xkcd_url = f'http://xkcd.com/{latest_xkcd_num}'
        xkcd_comic = latest_xkcd_comic

    xkcd_comic['date'] = f'{xkcd_comic["year"]}/{xkcd_comic["month"]}/{xkcd_comic["day"]}'
    xkcd_comic['url'] = original_xkcd_url

    return xkcd_comic


# TODO: Break this out into a better means of handling... could just be functional...
class Quotes(object):
    """Quotes class"""
    def __init__(self):
        self.voluspa_quotes = {
            'greetings': [
                '<:awesome_smiley:455152593052762140> :wave: Hello there, %%USER%%!',
                '<:awesome_smiley:455152593052762140> :wave: Aloha %%USER%%!',
                '<:awesome_laughing:455157667812474890> :wave: Hiya %%USER%%!',
                '%%USER%% :cowboy: :wave: Howdy!',
                '<:awesome_smiley:455152593052762140> :wave: Salutations %%USER%%!',
                "%%USER%% S'up?",
                '%%USER%% :wave: Ciao!',
                '%%USER%% Eyes up, Guardian! <:ghost_proxy:455130405398380564>'
            ],
            'goodbyes': [
                '<:awesome_smiley:455152593052762140> :wave: Goodbye %%USER%%! For now...',
                '<:awesome_shades:455200240660643860> Hasta la vista, %%USER%%!',
                '<:awesome_smiley:455152593052762140> :wave: See ya! %%USER%%!',
                ':wave: Laterz %%USER%%! <:awesome_laughing:455157667812474890>',
                '<:awesome_smiley:455152593052762140> :wave: Ta-ta for now, %%USER%%!',
                ":robot: Bleep. Blorp. Goodbye Human... nah, I'm just messin' with ya. Bye, %%USER%%! :wave:",
                '%%USER%% Roger, safe travels Guardian! Until next time! :thumbsup:'
            ],
            'random': [
                '<:awesome_smiley:455152593052762140> SNARF!'
            ],
            'status': [
                'with solar!',
                'with void!',
                'with arc!',
                'with spoils from the void...',
                'find the other Warminds...',
                '\\\\ MIDNIGHT EXIGENT \\',
                'find the Traveller',
                '\\\\Classified...',
                'Subroutine IKELOS',
                '\\\\ DVALIN FORGE \\',
                'Test: DVALIN FORGE-2',
                'Destiny 2 with Char',
                'chat with Calus',
                'find Cayde-6.NNimg.bak',
                'ping the Warsats...',
                'ignite the Forges!',
                'trade with Spider.',
                'fight the curse!',
                'search for the Nine.',
                'with the shadows.',
                'learn new moves...',
                'help Eris Morn...',
                'analyzing Nightmares.',
                '\\\\ [REDACTED]',
                'consult with the Queen.',
                'find Pulled Pork!',
                'with Ghost Proxy!!',
                'poker with the Drifter.',
                'chess with Zavala.',
                'with the Colonel!',
                'MTG with Ikora...',
                'pew pew pew',
                'make Vex milkshakes.',
                'with timelines',
                'scanning EMF fields...',
                'with paracausal forces',
                'paradoxes with Saint-14',
                'with Braytech Databases...',
                "Char's Firewall",
                'neural net inhibitors...',
                'checkers with the Nine.',
                'find the Dredgen.',
                'with light and darkness.',
                '\\\\ Optimize Protocols \\',
                'gradient descent...',
                'distributed network training',

            ]
        }

    async def pick_quote(self, quote_type, user_mention=None):
        """Pick a random quote to use"""
        quotes = self.voluspa_quotes[quote_type]
        rand_idx = random.randint(0, len(quotes) - 1)
        logger.info('PICK QUOTE -- random quote: %s', rand_idx)
        quote = quotes[rand_idx]
        if user_mention:
            quote = re.sub(r'%%USER%%',
                           user_mention,
                           quote)
        logger.info('PICK QUOTE -- using quote: %s', quote)
        return quote


# TODO: Replace with async http....
class RandomQuotes(object):
    """Random Quotes class"""
    def __init__(self):
        self.quote_funcs = [
            # self.get_ron_swanson_quote,
            self.get_dad_joke,
            # self.get_inspirobot_quote,
            # self.get_chuck_norris_quote
        ]

    async def get_dad_joke(self):
        """Get a Dad joke"""
        # GET https://icanhazdadjoke.com/
        # GET https://icanhazdadjoke.com/j/<joke_id>.png
        req = requests.get('https://icanhazdadjoke.com/', headers={'Accept': 'application/json'}, timeout=20)
        dad_joke = req.json()['joke']
        return dad_joke

    async def get_ron_swanson_quote(self):
        """Get a Ron Swanson quote"""
        req = requests.get('https://ron-swanson-quotes.herokuapp.com/v2/quotes', timeout=20)
        ron_quote = '"{}" -Ron Swanson'.format(req.json()[0])
        return ron_quote

    async def get_inspirobot_quote(self):
        """Get an inspirobot quote"""
        req = requests.get('http://inspirobot.me/api?generate=true', timeout=20)
        return req.text

    async def get_chuck_norris_quote(self):
        """Get a Chuck Norris quote"""
        req = requests.get('http://api.icndb.com/jokes/random?limitTo=[nerdy]', timeout=20)
        return req.json()['value']['joke']

    async def get_random_quote(self):
        """Get a RANDOM quote"""
        rand_int = random.randint(0, len(self.quote_funcs) - 1)
        return await self.quote_funcs[rand_int]()
