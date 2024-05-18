import pytest
from io import StringIO
from PyPlasmaFractal.mylib.config.dict_path import DictPath
import stat

@pytest.fixture
def initial_fs():
    return {
        '/': {
            'type': 'directory',
            'content': {
                'example.txt': {
                    'type': 'file',
                    'content': 'Hello, virtual file system!',
                    'metadata': {
                        'st_ctime': 1625097600.0,
                        'st_mtime': 1625097600.0,
                        'st_atime': 1625097600.0,
                    }
                },
                'dir1': {
                    'type': 'directory',
                    'content': {
                        'file1.txt': {
                            'type': 'file',
                            'content': 'Content of file1.txt',
                            'metadata': {
                                'st_ctime': 1625097600.0,
                                'st_mtime': 1625097600.0,
                                'st_atime': 1625097600.0,
                            }
                        },
                        'subdir1': {
                            'type': 'directory',
                            'content': {
                                'file2.txt': {
                                    'type': 'file',
                                    'content': 'Content of file2.txt',
                                    'metadata': {
                                        'st_ctime': 1625097600.0,
                                        'st_mtime': 1625097600.0,
                                        'st_atime': 1625097600.0,
                                    }
                                }
                            },
                            'metadata': {
                                'st_ctime': 1625097600.0,
                                'st_mtime': 1625097600.0,
                                'st_atime': 1625097600.0,
                            }
                        }
                    },
                    'metadata': {
                        'st_ctime': 1625097600.0,
                        'st_mtime': 1625097600.0,
                        'st_atime': 1625097600.0,
                    }
                }
            },
            'metadata': {
                'st_ctime': 1625097600.0,
                'st_mtime': 1625097600.0,
                'st_atime': 1625097600.0,
            }
        }
    }

def test_read_text(initial_fs):
    vpath = DictPath('/example.txt', filesystem=initial_fs)
    assert vpath.read_text() == 'Hello, virtual file system!'

def test_exists(initial_fs):
    vpath = DictPath('/example.txt', filesystem=initial_fs)
    assert vpath.exists()
    vpath_nonexistent = DictPath('/nonexistent.txt', filesystem=initial_fs)
    assert not vpath_nonexistent.exists()

def test_is_file(initial_fs):
    vpath = DictPath('/example.txt', filesystem=initial_fs)
    assert vpath.is_file()
    vpath_dir = DictPath('/dir1', filesystem=initial_fs)
    assert not vpath_dir.is_file()

def test_is_dir(initial_fs):
    vpath = DictPath('/dir1', filesystem=initial_fs)
    assert vpath.is_dir()
    vpath_file = DictPath('/example.txt', filesystem=initial_fs)
    assert not vpath_file.is_dir()

def test_iterdir(initial_fs):
    vpath_dir = DictPath('/dir1', filesystem=initial_fs)
    contents = list(vpath_dir.iterdir())
    expected_contents = [
        DictPath('/dir1/file1.txt', filesystem=initial_fs),
        DictPath('/dir1/subdir1', filesystem=initial_fs)
    ]
    assert contents == expected_contents

def test_stat(initial_fs):
    vpath = DictPath('/example.txt', filesystem=initial_fs)
    stat_result = vpath.stat()
    assert stat_result.st_size == len('Hello, virtual file system!')
    assert stat.S_ISREG(stat_result.st_mode)
    assert stat_result.st_mtime == 1625097600.0

    vpath_dir = DictPath('/dir1', filesystem=initial_fs)
    stat_result = vpath_dir.stat()
    assert stat_result.st_size == 0
    assert stat.S_ISDIR(stat_result.st_mode)
    assert stat_result.st_mtime == 1625097600.0

def test_open_read_text(initial_fs):
    vpath = DictPath('/example.txt', filesystem=initial_fs)
    with vpath.open('r') as f:
        content = f.read()
    assert content == 'Hello, virtual file system!'

def test_open_invalid_mode(initial_fs):
    vpath = DictPath('/example.txt', filesystem=initial_fs)
    with pytest.raises(ValueError, match="Only read access for text files is supported"):
        vpath.open('w')
    with pytest.raises(ValueError, match="Only read access for text files is supported"):
        vpath.open('a')
    with pytest.raises(ValueError, match="Only read access for text files is supported"):
        vpath.open('rb')
    with pytest.raises(ValueError, match="Only read access for text files is supported"):
        vpath.open('r+')

def test_open_not_a_text_file(initial_fs):
    vpath = DictPath('/dir1', filesystem=initial_fs)
    with pytest.raises(TypeError, match="'/dir1' is not a file"):
        vpath.open('r')
