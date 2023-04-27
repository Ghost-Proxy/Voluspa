"""Misc Module"""

import collections.abc
from copy import deepcopy
from typing import Any, List, Callable

NEW_LINE = "\n"
VOLUSPA_RAW_TXT_LOGO = '--\\\\\\\\´//--'
CACHE = {}

# {
#   <function read_and_build_config at 0x102bbba60>: {():[]}
#
#
# }


def memoize(func) -> Callable[..., Any]:
    """Memoize any function"""
    # Guarantees that the initial call to config is the same config over the lifetime of the app, in theory
    def memoized_func(*args):
        func_id = id(func)
        if func_id in CACHE:
            if args in CACHE[func_id]:
                return CACHE[func_id][args]
        result = func(*args)
        CACHE[func_id] = {args: result}
        return result
    return memoized_func


def chunk_list(chonk_list: List[Any], chunk_size: int = 1024):
    """Casts elements to str"""
    chunks = {}
    current_chunk = 0
    for item in chonk_list:
        item = str(item)
        if len(item) > chunk_size:
            # need to chunk item itself, naive
            new_chunks = [item[i:i + chunk_size] for i in range(0, len(item), chunk_size)]
            for chunk in new_chunks:
                current_chunk += 1
                chunks[current_chunk] = [chunk]
        elif len(str(item)) + len(''.join(chunks.get(current_chunk, ''))) > chunk_size:
            # need to make a new chunk
            current_chunk += 1
            chunks[current_chunk] = [item]
        else:
            # add to current chunk
            chunks.setdefault(current_chunk, []).append(item)
    return [v for k, v in chunks.items()]


# https://stackoverflow.com/questions/38034377/object-like-attribute-access-for-nested-dictionary
class AttrDict(dict):
    """ Dictionary subclass whose entries can be accessed by attributes
        (as well as normally).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

    @staticmethod
    def from_nested_dict(data):
        """ Construct nested AttrDicts from nested dictionaries. """
        if not isinstance(data, dict):
            return data

        return AttrDict({key: AttrDict.from_nested_dict(data[key]) for key in data})


# https://stackoverflow.com/questions/25833613/python-safe-method-to-get-value-of-nested-dictionary
class Hasher(dict):
    """Dictionary Hasher"""
    # https://stackoverflow.com/a/3405143/190597
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


# Added skip_none arg/func
# https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
def merge_dicts(dct, merge_dct, add_keys=True, skip_none=False) -> dict:
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
        merge_dct = {
            k: merge_dct[k]
            for k in set(dct).intersection(set(merge_dct))
        }
    for key, val in merge_dct.items():
        if val is None and skip_none:
            continue
        if isinstance(dct.get(key), dict) and isinstance(val, collections.abc.Mapping):
            dct[key] = merge_dicts(dct[key], val, add_keys=add_keys, skip_none=skip_none)
        # TODO: Ehh... kind of doesn't work with empty nested...
        # elif isinstance(v, dict):
        #     print(f'Nested Dict for new... k [{k}] v [{v}] ')
        #     dct[k] = merge_dicts(k, v, add_keys=add_keys, skip_none=skip_none)
        else:
            dct[key] = val
    return dct


def dict_merge(*args, add_keys=True):
    assert len(args) >= 2, "dict_merge requires at least two dicts to merge"
    rtn_dct = args[0].copy()
    dicts_to_merge = args[1:]
    for merge_dct in dicts_to_merge:
        if add_keys is False:
            merge_dct = {key: merge_dct[key] for key in set(rtn_dct).intersection(set(merge_dct))}
        for key, val in merge_dct.items():
            if not rtn_dct.get(key):
                rtn_dct[key] = val
            elif key in rtn_dct and isinstance(val, type(rtn_dct[key])):
                raise TypeError(f"Overlapping keys exist with different types: original is {type(rtn_dct[key])}, new value is {type(val)}")
            elif isinstance(rtn_dct[key], dict) and isinstance(merge_dct[key], collections.abc.Mapping):
                rtn_dct[key] = dict_merge(rtn_dct[key], merge_dct[key], add_keys=add_keys)
            elif isinstance(val, list):
                for list_value in val:
                    if list_value not in rtn_dct[key]:
                        rtn_dct[key].append(list_value)
            else:
                rtn_dct[key] = val
    return rtn_dct


def deep_merge(a: dict, b: dict) -> dict:
    result = deepcopy(a)
    for bk, bv in b.items():
        av = result.get(bk)
        if isinstance(av, dict) and isinstance(bv, dict):
            result[bk] = deep_merge(av, bv)
        else:
            result[bk] = deepcopy(bv)
    return result
