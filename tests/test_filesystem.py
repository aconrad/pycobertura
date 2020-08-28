import subprocess
from unittest.mock import patch, MagicMock


FIRST_PYCOBERTURA_COMMIT_SHA = "d1fe88da6b18340762b24bb1f89067a3439c4041"


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


def test_filesystem_git():
    import pycobertura.filesystem as fsm

    branch, folder, filename = "master", "tests/dummy", "test-file"

    with patch.object(fsm, "subprocess") as subprocess_mock:
        subprocess_mock.check_output = MagicMock(return_value=b"<file-content>")

        fs = fsm.GitFileSystem(folder, branch)

        with fs.open(filename) as f:
            assert hasattr(f, 'read')

        expected_git_filename = "master:tests/dummy/test-file"
        git_filename = fs.real_filename(filename)
        assert git_filename == expected_git_filename

        expected_command = ["git", "--no-pager", "show", git_filename]
        subprocess_mock.check_output.assert_called_with(expected_command, cwd=folder)


def test_filesystem_git_integration():
    from pycobertura.filesystem import GitFileSystem

    fs = GitFileSystem(".", FIRST_PYCOBERTURA_COMMIT_SHA)

    # Files included in pycobertura's first commit.
    source_files = [
        'README.md',
        '.gitignore',
    ]

    for source_file in source_files:
        with fs.open(source_file) as f:
            assert hasattr(f, 'read')


def test_filesystem_git_integration__not_found():
    from pycobertura.filesystem import GitFileSystem

    fs = GitFileSystem(".", FIRST_PYCOBERTURA_COMMIT_SHA)

    dummy_source_file = "CHANGES.md"

    try:
        with fs.open(dummy_source_file) as f:
            pass
    except GitFileSystem.FileNotFound as fnf:
        assert fnf.path == fs.real_filename(dummy_source_file)


def test_filesystem_git__git_not_found():
    import pycobertura.filesystem as fsm

    branch, folder, filename = "master", "tests/dummy", "test-file"

    error = subprocess.CalledProcessError
    with patch.object(fsm, "subprocess") as subprocess_mock:
        subprocess_mock.check_output = MagicMock(side_effect=OSError)
        subprocess_mock.CalledProcessError = error

        try:
            fs = fsm.GitFileSystem(folder, branch)
        except ValueError as e:
            assert folder in str(e)


def test_filesystem_git_integration():
    from pycobertura.filesystem import GitFileSystem

    fs = GitFileSystem(".", FIRST_PYCOBERTURA_COMMIT_SHA)

    # Files included in pycobertura's first commit.
    source_files = [
        "README.md",
        ".gitignore",
    ]

    for source_file in source_files:
        with fs.open(source_file) as f:
            assert hasattr(f, "read")


def test_filesystem_git_has_file_integration():
    from pycobertura.filesystem import GitFileSystem

    fs = GitFileSystem(".", FIRST_PYCOBERTURA_COMMIT_SHA)

    # Files included in pycobertura's first commit.
    source_files = [
        "README.md",
        ".gitignore",
    ]

    for source_file in source_files:
        assert fs.has_file(source_file), source_file


def test_filesystem_git_integration__not_found():
    from pycobertura.filesystem import GitFileSystem

    fs = GitFileSystem(".", FIRST_PYCOBERTURA_COMMIT_SHA)

    dummy_source_file = "CHANGES.md"

    try:
        with fs.open(dummy_source_file) as f:
            pass
    except GitFileSystem.FileNotFound as fnf:
        assert fnf.path == fs.real_filename(dummy_source_file)


def test_filesystem_git_has_file_integration__not_found():
    from pycobertura.filesystem import GitFileSystem

    fs = GitFileSystem(".", FIRST_PYCOBERTURA_COMMIT_SHA)

    dummy_source_file = "CHANGES.md"

    assert not fs.has_file(dummy_source_file)


def test_filesystem_factory():
    from pycobertura.filesystem import filesystem_factory, GitFileSystem

    fs = filesystem_factory(source=".", ref=FIRST_PYCOBERTURA_COMMIT_SHA)
    assert isinstance(fs, GitFileSystem)
