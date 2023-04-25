"""Emoji Utilities Module"""

from emoji import emojize

def ri_alphabet(num):
    """Regional Indicator Emoji lookup"""
    if num < 1:
        num = 1
    elif num > 26:
        num = 26

    current_emoji = '\U0001f1e6' # Regional Indicator A
    i = 0
    while i < num:
        yield current_emoji

        current_emoji = chr(ord(current_emoji) + 1)
        i += 1

def ri_at_index(idx):
    """Regional Indicator at index i"""
    if idx < 0:
        idx = 0
    elif idx > 25:
        idx = 25
        
    regional_indicator_a = '\U0001f1e6'
    return chr(ord(regional_indicator_a) + idx)

def index_of_ri(regional_indicator):
    """Returns the index of the Regional Indicator"""
    return ord(regional_indicator) - ord('\U0001f1e6')

def normalize(name):
    """Normalize the name"""
    if name[0] != ':' and name[-1] != ':':
        temp = emojize(f':{name}:', language='alias')
        if temp != f':{name}:':
            name = f':{name}:'
    return name
