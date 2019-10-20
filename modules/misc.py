import collections.abc
from unittest import TestCase

new_line = "\n"
voluspa_raw_txt_logo = '--\\\\\\\\´//--'


def memoize(func):
    # Guarantees that the initial call to config is the same config over the lifetime of the app, in theory
    cache = dict()

    def memoized_func(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result

    return memoized_func


# https://stackoverflow.com/questions/38034377/object-like-attribute-access-for-nested-dictionary
class AttrDict(dict):
    """ Dictionary subclass whose entries can be accessed by attributes
        (as well as normally).
    """
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    @staticmethod
    def from_nested_dict(data):
        """ Construct nested AttrDicts from nested dictionaries. """
        if not isinstance(data, dict):
            return data
        else:
            return AttrDict({key: AttrDict.from_nested_dict(data[key]) for key in data})


# https://stackoverflow.com/questions/25833613/python-safe-method-to-get-value-of-nested-dictionary
class Hasher(dict):
    # https://stackoverflow.com/a/3405143/190597
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


# Added skip_none arg/func
# https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
def merge_dicts(dct, merge_dct, add_keys=True, skip_none=False):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, merge_dicts recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.

    This version will return a copy of the dictionary and leave the original
    arguments untouched.

    The optional argument ``add_keys``, determines whether keys which are
    present in ``merge_dict`` but not ``dct`` should be included in the
    new dict.

    Args:
        dct (dict) onto which the merge is executed
        merge_dct (dict): dct merged into dct
        add_keys (bool): whether to add new keys
        skip_none (bool): whether keys with values of None are merged

    Returns:
        dict: updated dict
    """
    dct = dct.copy()
    if not add_keys:
        # print(f'NOT ADD_KEYS -- {set(dct).intersection(set(merge_dct))}')
        merge_dct = {
            k: merge_dct[k]
            for k in set(dct).intersection(set(merge_dct))
        }

    for k, v in merge_dct.items():
        # print(f'Merge processing -- key [{k}] with value [{v}]')
        if v is None and skip_none:
            # print(f'Hit NONE value with k [{k}]')
            continue
        if isinstance(dct.get(k), dict) and isinstance(v, collections.abc.Mapping):
            # print(f'Nested Dict for both... k [{k}] v [{v}] -- other: [{dct[k]}]')
            dct[k] = merge_dicts(dct[k], v, add_keys=add_keys, skip_none=skip_none)
        # TODO: Ehh... kind of doesn't work with empty nested...
        # elif isinstance(v, dict):
        #     print(f'Nested Dict for new... k [{k}] v [{v}] ')
        #     dct[k] = merge_dicts(k, v, add_keys=add_keys, skip_none=skip_none)
        else:
            # print(f'Normal else, key: [{k}] and value: [{v}]')
            dct[k] = v

    return dct


class DictMergeTestCase(TestCase):
    def test_merges_dicts(self):
        a = {
            'a': 1,
            'b': {
                'b1': 2,
                'b2': 3,
            },
        }
        b = {
            'a': 1,
            'b': {
                'b1': 4,
            },
        }

        assert merge_dicts(a, b)['a'] == 1
        assert merge_dicts(a, b)['b']['b2'] == 3
        assert merge_dicts(a, b)['b']['b1'] == 4

    def test_inserts_new_keys(self):
        """Will it insert new keys by default?"""
        a = {
            'a': 1,
            'b': {
                'b1': 2,
                'b2': 3,
            },
        }
        b = {
            'a': 1,
            'b': {
                'b1': 4,
                'b3': 5
            },
            'c': 6,
        }

        assert merge_dicts(a, b)['a'] == 1
        assert merge_dicts(a, b)['b']['b2'] == 3
        assert merge_dicts(a, b)['b']['b1'] == 4
        assert merge_dicts(a, b)['b']['b3'] == 5
        assert merge_dicts(a, b)['c'] == 6

    def test_does_not_insert_None_when_skip_none(self):
        """Will skip keys merging keys that have none values"""
        a = {
            'a': 1,
            'b': {
                'b1': 2,
                'b2': 3,
            },
            'c': 4
        }
        b = {
            'a': 1,
            'b': {
                'b1': 4,
                'b2': None,
            },
            'c': None,
            'd': None,
            'e': {
                'e1': None
            }

        }

        print(merge_dicts(a, b, skip_none=True))

        assert merge_dicts(a, b, skip_none=True)['a'] == 1
        assert merge_dicts(a, b, skip_none=True)['b']['b1'] == 4
        assert merge_dicts(a, b, skip_none=True)['b']['b2'] == 3
        assert merge_dicts(a, b, skip_none=True)['c'] == 4
        try:
            assert merge_dicts(a, b, skip_none=True)['d'] is None
        except KeyError:
            pass
        else:
            raise Exception('None value was added when it should not have been')

    def test_does_not_insert_new_keys(self):
        """Will it avoid inserting new keys when required?"""
        a = {
            'a': 1,
            'b': {
                'b1': 2,
                'b2': 3,
            },
        }
        b = {
            'a': 1,
            'b': {
                'b1': 4,
                'b3': 5,
            },
            'c': 6,
        }

        assert merge_dicts(a, b, add_keys=False)['a'] == 1
        assert merge_dicts(a, b, add_keys=False)['b']['b2'] == 3
        assert merge_dicts(a, b, add_keys=False)['b']['b1'] == 4
        try:
            assert merge_dicts(a, b, add_keys=False)['b']['b3'] == 5
        except KeyError:
            pass
        else:
            raise Exception('New keys added when they should not be')

    def test_does_not_insert_None_when_skip_none_or_add_new_keys(self):
        """Will skip keys merging keys that have none values"""
        a = {
            'a': 1,
            'b': {
                'b1': 2,
                'b2': 3,
            },
            'c': 4
        }
        b = {
            'a': 1,
            'b': {
                'b1': 4,
                'b2': None,
                'b3': 5,
            },
            'c': None,
            'd': None,
            'e': {
                'e1': None
            }

        }

        print(merge_dicts(a, b, add_keys=False, skip_none=True))

        assert merge_dicts(a, b, add_keys=False, skip_none=True)['a'] == 1
        assert merge_dicts(a, b, add_keys=False, skip_none=True)['b']['b1'] == 4
        assert merge_dicts(a, b, add_keys=False, skip_none=True)['b']['b2'] == 3
        assert merge_dicts(a, b, add_keys=False, skip_none=True)['c'] == 4
        try:
            assert merge_dicts(a, b, add_keys=False, skip_none=True)['d'] is None
        except KeyError:
            pass
        else:
            raise Exception('None value was added when it should not have been')
        try:
            assert merge_dicts(a, b, add_keys=False, skip_none=True)['b']['b3'] == 5
        except KeyError:
            pass
        else:
            raise Exception('New keys added when they should not be')
