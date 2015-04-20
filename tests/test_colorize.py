def test_colorize():
    from pycobertura.utils import colorize
    assert colorize('YAY!', 'green') == '\x1b[32mYAY!\x1b[39m'
