import collections
from unittest import TestCase


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


# https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
def merge_dicts(dct, merge_dct, add_keys=True):
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

    Returns:
        dict: updated dict
    """
    dct = dct.copy()
    if not add_keys:
        merge_dct = {
            k: merge_dct[k]
            for k in set(dct).intersection(set(merge_dct))
        }

    for k, v in merge_dct.items():
        if isinstance(dct.get(k), dict) and isinstance(v, collections.Mapping):
            dct[k] = merge_dicts(dct[k], v, add_keys=add_keys)
        else:
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

        try:
            assert merge_dicts(a, b, add_keys=False)['b']['b3'] == 6
        except KeyError:
            pass
        else:
            raise Exception('New keys added when they should not be')

