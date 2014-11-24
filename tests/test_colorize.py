import mock


@mock.patch('pycobertura.utils.sys.stdout.isatty', return_value=False)
def test_colorize__stdout_is_not_a_tty(mock_is_a_tty):
    from pycobertura.utils import colorize
    assert colorize('YAY!', 'green') == 'YAY!'


@mock.patch('pycobertura.utils.sys.stdout.isatty', return_value=True)
def test_colorize__stdout_is_a_tty(mock_is_a_tty):
    from pycobertura.utils import colorize
    assert colorize('YAY!', 'green') == '\x1b[32mYAY!\x1b[39m'
