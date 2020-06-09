def ri_alphabet(n):
    if n < 1:
        n = 1
    elif n > 26:
        n = 26

    current_emoji = '\U0001f1e6' # Regional Indicator A
    i = 0
    while i < n:
        yield current_emoji

        current_emoji = chr(ord(current_emoji) + 1)
        i += 1

def ri_at_index(i):
    if i < 0:
        i = 0
    elif i > 25:
        i = 25

    a = '\U0001f1e6'

    return chr(ord(a) + i)
