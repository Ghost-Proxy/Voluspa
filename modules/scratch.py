"""Random scratch module"""

import random


async def random_item(item_list):
    """Pick a random index for an item from a list"""
    _rand_idx = random.randint(0, len(item_list) - 1)
