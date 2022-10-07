from pycobertura.utils import get_non_empty_non_commented_lines_from_file_in_ascii, get_filenames_that_do_not_match_regex

def test_read_ignore_regex_file():
    result = get_non_empty_non_commented_lines_from_file_in_ascii('tests/.testgitignore', '#')
    assert result == ['**/__pycache__','**/dummy*','*.xml']

def test_get_filenames_that_do_not_match_regex_given_file_path():
    filenames = ["tests/dummy/test_dummy.py", "tests/cobertura.xml", "tests/test_cli.py"]
    result = get_filenames_that_do_not_match_regex(filenames, "tests/.testgitignore")
    assert result == ["tests/test_cli.py"]

def test_get_filenames_that_do_not_match_regex_given_list_of_filenames():
    filenames = ["tests/dummy/test_dummy.py", "tests/cobertura.xml", "tests/test_cli.py"]
    regex_param = "^tests/dummy|(.*).xml$"
    result = get_filenames_that_do_not_match_regex(filenames, regex_param)
    assert result == ["tests/test_cli.py"]

