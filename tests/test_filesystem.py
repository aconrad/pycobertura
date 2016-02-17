import mock


def test_filesystem_directory__file_not_found():
    from pycobertura.filesystem import DirectoryFileSystem

    fs = DirectoryFileSystem('foo/bar/baz')

    expected_filepaths = {
        'Main.java': 'foo/bar/baz/Main.java',
        'search/BinarySearch.java': 'foo/bar/baz/search/BinarySearch.java',
        'search/ISortedArraySearch.java': 'foo/bar/baz/search/ISortedArraySearch.java',
        'search/LinearSearch.java': 'foo/bar/baz/search/LinearSearch.java',
    }

    for filename in expected_filepaths:
        try:
            with fs.open(filename) as f:
                pass
        except DirectoryFileSystem.FileNotFound as fnf:
            assert fnf.path == expected_filepaths[filename]


def test_filesystem_directory__returns_fileobject():
    from pycobertura.filesystem import DirectoryFileSystem

    fs = DirectoryFileSystem('tests/dummy')

    expected_filepaths = {
        'dummy/dummy.py': 'dummy/dummy/dummy.py',
    }

    for filename in expected_filepaths:
        with fs.open(filename) as f:
            assert hasattr(f, 'read')


def test_filesystem_directory__with_source_prefix():
    from pycobertura.filesystem import DirectoryFileSystem

    fs = DirectoryFileSystem(
        'tests/',
        source_prefix='dummy'  # should resolve to tests/dummy/
    )

    expected_filepaths = {
        'dummy/dummy.py': 'dummy/dummy/dummy.py',
    }

    for filename in expected_filepaths:
        with fs.open(filename) as f:
            assert hasattr(f, 'read')


def test_filesystem_zip__file_not_found():
    from pycobertura.filesystem import ZipFileSystem

    fs = ZipFileSystem("tests/dummy/dummy.zip")

    dummy_source_file = 'foo/non-existent-file.py'
    try:
        with fs.open(dummy_source_file) as f:
            pass
    except ZipFileSystem.FileNotFound as fnf:
        assert fnf.path == dummy_source_file


def test_filesystem_zip__returns_fileobject():
    from pycobertura.filesystem import ZipFileSystem

    fs = ZipFileSystem("tests/dummy/dummy.zip")

    source_files_in_zip = [
        'dummy/dummy.py',
        'dummy/dummy2.py',
    ]

    for source_file in source_files_in_zip:
        with fs.open(source_file) as f:
            assert hasattr(f, 'read')


def test_filesystem_zip__with_source_prefix():
    from pycobertura.filesystem import ZipFileSystem

    fs = ZipFileSystem(
        "tests/dummy/dummy-with-prefix.zip",  # code zipped as dummy-with-prefix/dummy/dummy.py
        source_prefix="dummy-with-prefix",
    )

    source_files_in_zip = [
        'dummy/dummy.py',
        'dummy/dummy2.py',
    ]

    for source_file in source_files_in_zip:
        with fs.open(source_file) as f:
            assert hasattr(f, 'read')
