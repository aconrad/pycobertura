from click.testing import CliRunner


def test_show__format_default():
    from pycobertura.cli import show

    runner = CliRunner()
    result = runner.invoke(show, ['tests/dummy.original.xml'])
    assert result.output == """\
Name           Stmts    Miss  Cover    Missing
-----------  -------  ------  -------  ---------
dummy/dummy        4       2  50.00%   2, 5
TOTAL              4       2  50.00%
"""


def test_show__format_text__long_option():
    from pycobertura.cli import show

    runner = CliRunner()
    result = runner.invoke(show, ['tests/dummy.original.xml', '--format', 'text'])
    assert result.output == """\
Name           Stmts    Miss  Cover    Missing
-----------  -------  ------  -------  ---------
dummy/dummy        4       2  50.00%   2, 5
TOTAL              4       2  50.00%
"""


def test_show__format_text__short_option():
    from pycobertura.cli import show

    runner = CliRunner()
    result = runner.invoke(show, ['tests/dummy.original.xml', '-f', 'text'])
    assert result.output == """\
Name           Stmts    Miss  Cover    Missing
-----------  -------  ------  -------  ---------
dummy/dummy        4       2  50.00%   2, 5
TOTAL              4       2  50.00%
"""


def test_show__format_html():
    from pycobertura.cli import show

    runner = CliRunner()
    result = runner.invoke(show, ['tests/dummy.original.xml', '--format', 'html'])
    assert result.output.startswith('<html>')


def test_diff():
    from pycobertura.cli import diff

    runner = CliRunner()
    result = runner.invoke(diff, [
        'tests/dummy.original.xml',
        'tests/dummy.with-dummy2-full-cov.xml'
    ])
    assert result.output == """\
Name          Stmts    Miss    Cover     Missing
------------  -------  ------  --------  ---------
dummy/dummy   -        -2      +50.00%   -2, -5
dummy/dummy2  +2       -       +100.00%
TOTAL         +2       -2      +50.00%
"""
