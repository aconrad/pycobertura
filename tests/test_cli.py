from click.testing import CliRunner
import sys

PY2 = sys.version_info[0] == 2


def test_show__format_default():
    from pycobertura.cli import show

    runner = CliRunner()
    result = runner.invoke(show,
        ['tests/dummy.original.xml'],
        catch_exceptions=False
    )
    assert result.output == """\
Name           Stmts    Miss  Cover    Missing
-----------  -------  ------  -------  ---------
dummy/dummy        4       2  50.00%   2, 5
TOTAL              4       2  50.00%
"""


def test_show__format_text():
    from pycobertura.cli import show

    runner = CliRunner()
    for opt in ('-f', '--format'):
        result = runner.invoke(
            show,
            ['tests/dummy.original.xml', opt, 'text'],
            catch_exceptions=False
        )
        assert result.output == """\
Name           Stmts    Miss  Cover    Missing
-----------  -------  ------  -------  ---------
dummy/dummy        4       2  50.00%   2, 5
TOTAL              4       2  50.00%
"""


def test_show__format_html():
    from pycobertura.cli import show

    runner = CliRunner()
    result = runner.invoke(show, [
        'tests/dummy.original.xml', '--format', 'html'
    ], catch_exceptions=False)
    assert result.output.startswith('<html>')
    assert result.output.endswith('</html>\n')


def test_show__output_to_file():
    from pycobertura.cli import show

    with open('tests/dummy.original.xml') as f:
        cobertura_content = f.read()

    runner = CliRunner()
    for opt in ('-o', '--output'):
        with runner.isolated_filesystem():
            with open('cobertura.xml', 'w') as f:
                f.write(cobertura_content)
            result = runner.invoke(show, [
                'cobertura.xml', opt, 'report.out'
            ], catch_exceptions=False)
            with open('report.out') as f:
                report = f.read()
            assert result.output == ""
            assert report == """\
Name           Stmts    Miss  Cover    Missing
-----------  -------  ------  -------  ---------
dummy/dummy        4       2  50.00%   2, 5
TOTAL              4       2  50.00%"""


def test_diff__format_default():
    from pycobertura.cli import diff

    runner = CliRunner()
    result = runner.invoke(diff, [
        'tests/dummy.with-dummy2-better-cov.xml',
        'tests/dummy.with-dummy2-better-and-worse.xml',
    ], catch_exceptions=False)
    # FIXME: Fails in PY2, requires click>=4.x to pass
    if not PY2:
        assert result.output == """\
Name          Stmts    Miss    Cover    Missing
------------  -------  ------  -------  ---------
dummy/dummy   -        +1      -25.00%  \x1b[31m+5\x1b[39m
dummy/dummy2  -        -1      +50.00%  \x1b[32m-2\x1b[39m
TOTAL         -        -       -
"""
    else:
        assert result.output == """\
Name          Stmts    Miss    Cover    Missing
------------  -------  ------  -------  ---------
dummy/dummy   -        +1      -25.00%  +5
dummy/dummy2  -        -1      +50.00%  -2
TOTAL         -        -       -
"""


def test_diff__format_text():
    from pycobertura.cli import diff

    runner = CliRunner()
    for opt in ('-f', '--format'):
        result = runner.invoke(diff, [
            opt, 'text',
            'tests/dummy.with-dummy2-better-cov.xml',
            'tests/dummy.with-dummy2-better-and-worse.xml',
        ], catch_exceptions=False)
        # FIXME: Fails in PY2, requires click>=4.x to pass
        if not PY2:
            assert result.output == """\
Name          Stmts    Miss    Cover    Missing
------------  -------  ------  -------  ---------
dummy/dummy   -        +1      -25.00%  \x1b[31m+5\x1b[39m
dummy/dummy2  -        -1      +50.00%  \x1b[32m-2\x1b[39m
TOTAL         -        -       -
"""
        else:
            assert result.output == """\
Name          Stmts    Miss    Cover    Missing
------------  -------  ------  -------  ---------
dummy/dummy   -        +1      -25.00%  +5
dummy/dummy2  -        -1      +50.00%  -2
TOTAL         -        -       -
"""


def test_diff__output_to_file():
    from pycobertura.cli import diff

    with open('tests/dummy.with-dummy2-better-cov.xml') as f:
        cobertura1_content = f.read()

    with open('tests/dummy.with-dummy2-better-and-worse.xml') as f:
        cobertura2_content = f.read()

    runner = CliRunner()

    for opt in ('-o', '--output'):
        with runner.isolated_filesystem():

            with open('cobertura1.xml', 'w') as f:
                f.write(cobertura1_content)

            with open('cobertura2.xml', 'w') as f:
                f.write(cobertura2_content)

            result = runner.invoke(diff, [
                'cobertura1.xml',
                'cobertura2.xml',
                opt, 'report.out'
            ], catch_exceptions=False)
            with open('report.out') as f:
                report = f.read()
            assert result.output == ""
            assert report == """\
Name          Stmts    Miss    Cover    Missing
------------  -------  ------  -------  ---------
dummy/dummy   -        +1      -25.00%  +5
dummy/dummy2  -        -1      +50.00%  -2
TOTAL         -        -       -"""


# FIXME: when Click 4 is available, uncomment this.
#def test_diff__format_text__with_color():
#    from pycobertura.cli import diff
#
#    runner = CliRunner()
#    result = runner.invoke(diff, [
#        '--color',
#        'tests/dummy.with-dummy2-better-cov.xml',
#        'tests/dummy.with-dummy2-better-and-worse.xml',
#    ], catch_exceptions=False)
#    assert result.output == """\
#Name          Stmts    Miss    Cover    Missing
#------------  -------  ------  -------  ---------
#dummy/dummy   -        +1      -25.00%  \x1b[31m+5\x1b[39m
#dummy/dummy2  -        -1      +50.00%  \x1b[32m-2\x1b[39m
#TOTAL         -        -       -
#"""


def test_diff__format_html():
    from pycobertura.cli import diff

    runner = CliRunner()
    result = runner.invoke(diff, [
        '--format', 'html',
        'tests/dummy.with-dummy2-better-cov.xml',
        'tests/dummy.with-dummy2-better-and-worse.xml',
    ], catch_exceptions=False)
    assert result.output.startswith('<html>')
    assert result.output.endswith('</html>\n')
