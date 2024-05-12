import pytest
from enum import Enum, auto
from mylib.json_merge import MergePolicy, json_deep_merge

def test_dict_merge_no_extend():
    target = {'key1': 'value1'}
    source = {'key1': 'updated', 'key2': 'value2'}
    result = json_deep_merge(target, source)
    assert result == {'key1': 'updated'}

def test_dict_merge_with_extend_policy():
    target = {'key1': 'value1'}
    source = {'key2': 'value2'}
    result = json_deep_merge(target, source, merge_policies={'': MergePolicy.MERGE_EXTEND})
    assert result == {'key1': 'value1', 'key2': 'value2'}
    
def test_dict_merge_with_extend_policy_nested():
    target = {
        'outer': {
            'inner': {
                'key1': 'original'
            },
            'remain': 'untouched'
        }
    }
    source = {
        'outer': {
            'inner': {
                'key1': 'updated',
                'key2': 'added'
            },
            'new_inner': 'new value'
        }
    }
    
    # Applying MERGE_EXTEND only to the 'outer.inner' path
    merge_policies = {'outer.inner': MergePolicy.MERGE_EXTEND}
    result = json_deep_merge(target, source, merge_policies=merge_policies)

    # Expected: 'outer.inner' has 'key1' updated and 'key2' added, 'outer' should not have 'new_inner' added
    expected = {
        'outer': {
            'inner': {
                'key1': 'updated',
                'key2': 'added'
            },
            'remain': 'untouched'
        }
    }
    assert result == expected
    
def test_list_merge_no_extend():
    target = [1, 2, 3]
    source = [4, 5]
    result = json_deep_merge(target, source)
    assert result == [4, 5, 3]

def test_list_merge_with_extend():
    target = [1, 2, 3]
    source = [4, 5, 6, 7]
    result = json_deep_merge(target, source, default_merge_policy=MergePolicy.MERGE_EXTEND)
    assert result == [4, 5, 6, 7]

def test_scalar_conversion():
    target = 100
    source = '200'
    def convert_scalar(s, t):
        return int(s)
    result = json_deep_merge(target, source, convert_scalar=convert_scalar)
    assert result == 200

def test_nested_structure_merge():
    target = {'level1': {'key1': [1, 2], 'key2': 'value'}}
    source = {'level1': {'key1': [3], 'key2': 'new value'}}
    result = json_deep_merge(target, source)
    assert result == {'level1': {'key1': [3, 2], 'key2': 'new value'}}

def test_overwrite_policy():
    target = {'key1': 'value1'}
    source = {'key1': 'updated'}
    result = json_deep_merge(target, source, default_merge_policy=MergePolicy.OVERWRITE)
    assert result == {'key1': 'updated'}
    