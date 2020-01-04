import collections.abc

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

