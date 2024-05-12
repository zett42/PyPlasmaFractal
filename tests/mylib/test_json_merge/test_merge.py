import pytest
from enum import Enum, auto
from mylib.json_merge import MergePolicy, json_deep_merge

def test_dict_merge_with_default_policy():
    target = {'key1': 'value1'}
    source = {'key2': 'value2'}
    result = json_deep_merge(target, source)
    assert result == {'key1': 'value1', 'key2': 'value2'}

def test_dict_merge_no_extend():
    target = {'key1': 'value1'}
    source = {'key1': 'updated', 'key2': 'value2'}
    result = json_deep_merge(target, source, default_merge_policy=MergePolicy.MERGE_EXISTING)
    assert result == {'key1': 'updated'}
    
def test_dict_merge_with_no_extend_policy_nested():
    target = {
        'outer': {
            'inner1': {
                'key1': 'original'
            },
            'inner2': 'original'
        }
    }
    source = {
        'outer': {
            'inner1': {
                'key1': 'updated',
                'key2': 'added'
            },
            'new_inner': 'new value'
        }
    }
    
    # Applying MERGE_EXTEND only to the 'outer.inner' path
    merge_policies = {'outer.inner1': MergePolicy.MERGE_EXISTING}
    result = json_deep_merge(target, source, merge_policies=merge_policies)

    # Expected: 'outer.inner' has 'key1' updated and 'key2' discarded, 'outer' should have 'new_inner' added
    expected = {
        'outer': {
            'inner1': {
                'key1': 'updated'
            },
            'inner2': 'original',
            'new_inner': 'new value'
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

def test_type_mismatch_unhandled():
    target = 100
    source = '200'
    with pytest.raises(TypeError):
        json_deep_merge(target, source)
        
def test_complex_type_mismatch_unhandled():
    target = {'key1': [1, 2, 3]}
    source = {'key1': {'new_key': 'new_value'}}
    with pytest.raises(TypeError):
        json_deep_merge(target, source)      
    
def test_type_mismatch_handler():
    target = 100
    source = '200'
    def handle_type_mismatch(target, source):
        return int(source)
    result = json_deep_merge(target, source, handle_type_mismatch=handle_type_mismatch)
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
    
def test_deeply_nested_mixed_types():
    target = {'level1': {'key1': [1, {'key2': 'value2'}], 'key3': 'value3'}}
    source = {'level1': {'key1': [2, {'key2': 'updated'}], 'key4': 'new'}}
    result = json_deep_merge(target, source)
    assert result == {'level1': {'key1': [2, {'key2': 'updated'}], 'key3': 'value3', 'key4': 'new'}}

def test_merge_empty_source():
    target = {'key1': 'value1'}
    source = {}
    result = json_deep_merge(target, source)
    assert result == {'key1': 'value1'}

def test_merge_empty_target():
    target = {}
    source = {'key1': 'value1'}
    result = json_deep_merge(target, source)
    assert result == {'key1': 'value1'}

def test_multi_level_policy():
    target = {'level1': {'level2': {'key1': 'value1'}}}
    source = {'level1': {'level2': {'key1': 'new_value', 'key2': 'value2'}}}
    merge_policies = {'level1.level2': MergePolicy.MERGE_EXTEND}
    result = json_deep_merge(target, source, merge_policies=merge_policies)
    assert result == {'level1': {'level2': {'key1': 'new_value', 'key2': 'value2'}}}

def test_invalid_policy_specification():
    target = {'key1': 'value1'}
    source = {'key1': 'updated'}
    with pytest.raises(ValueError):
        json_deep_merge(target, source, merge_policies={'key1': 'invalid_policy'})
