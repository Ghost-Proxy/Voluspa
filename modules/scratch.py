import random


async def random_item(item_list):
    rand_idx = random.randint(0, len(item_list) - 1)