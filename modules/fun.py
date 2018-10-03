import logging
import re
import asyncio
import requests
import random

logger = logging.getLogger('discord')


async def get_xckd_comic():
    req = requests.get('https://xkcd.com/info.0.json')
    latest_xkcd = req.json()
    latest_xkcd_num = latest_xkcd['num']
    rand_idx = random.randint(1, latest_xkcd_num)
    req2 = requests.get('http://xkcd.com/{}/info.0.json'.format(rand_idx))
    rand_xkcd = req2.json()
    rand_xkcd_img = rand_xkcd['img']
    rand_xkcd_title = rand_xkcd['safe_title']
    rand_xkcd_alt = rand_xkcd['alt']
    return '**{}**\n_{}_\n{}'.format(
        rand_xkcd_title,
        rand_xkcd_alt,
        rand_xkcd_img
    )


class Quotes(object):
    def __init__(self):
        self.Voluspa_quotes = {
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
                'with fire!',
                'with spoils from the void...',
                'find the other Warminds...',
                '\\\\ MIDNIGHT EXIGENT \\',
                'find the Traveller',
                'mind games... hehe',
                'Subroutine IKELOS',
                '\\\\ DVALIN FORGE \\',
                'Test: DVALIN FORGE-2',
                'Destiny 2 with Char',
                'with Charlemagne!'
            ]
        }

    async def pick_quote(self, quote_type, user_mention=None):
        quotes = self.Voluspa_quotes[quote_type]
        rand_idx = random.randint(0, len(quotes) - 1)
        logger.info('PICK QUOTE -- random quote: {}'.format(rand_idx))
        quote = quotes[rand_idx]
        if user_mention:
            quote = re.sub(r'%%USER%%',
                           user_mention,
                           quote)
        logger.info('PICK QUOTE -- using quote: {}'.format(quote))
        return quote #return self._pick_quote(quote_type, user_mention

    def _pick_quote(self, quote_type, user_mention=None):
        quotes = self.Voluspa_quotes[quote_type]
        rand_idx = random.randint(0, len(quotes) - 1)
        logger.info('PICK QUOTE -- random quote: {}'.format(rand_idx))
        quote = quotes[rand_idx]
        if user_mention:
            quote = re.sub(r'%%USER%%',
                           user_mention,
                           quote)
        logger.info('PICK QUOTE -- using quote: {}'.format(quote))
        return quote


class RandomQuotes(object):
    def __init__(self):
        self.quote_funcs = [
            # self.get_ron_swanson_quote,
            self.get_dad_joke,
            # self.get_inspirobot_quote,
            # self.get_chuck_norris_quote
        ]

    async def get_dad_joke(self):
        # GET https://icanhazdadjoke.com/
        # GET https://icanhazdadjoke.com/j/<joke_id>.png
        req = requests.get('https://icanhazdadjoke.com/', headers={'Accept': 'application/json'})
        dad_joke = req.json()['joke']
        return dad_joke

    async def get_ron_swanson_quote(self):
        req = requests.get('https://ron-swanson-quotes.herokuapp.com/v2/quotes')
        ron_quote = '"{}" -Ron Swanson'.format(req.json()[0])
        return ron_quote

    async def get_inspirobot_quote(self):
        req = requests.get('http://inspirobot.me/api?generate=true')
        return req.text

    async def get_chuck_norris_quote(self):
        req = requests.get('http://api.icndb.com/jokes/random?limitTo=[nerdy]')
        return req.json()['value']['joke']

    async def get_random_quote(self):
        rand_int = random.randint(0, len(self.quote_funcs) - 1)
        return await self.quote_funcs[rand_int]()
