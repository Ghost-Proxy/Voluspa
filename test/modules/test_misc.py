# pylint: disable=invalid-name
# pylint: disable=broad-exception-raised
"""Test Module"""

from unittest import TestCase

from modules.misc import merge_dicts


class DictMergeTestCase(TestCase):
    """Dictionary Merge Testing"""
    def test_merges_dicts(self):
        """Test merging dicts"""
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
