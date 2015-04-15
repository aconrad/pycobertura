import os
import sys
import pytest
from click.testing import CliRunner

PY2 = sys.version_info[0] == 2


def test_show__format_default():
    from pycobertura.cli import show

    runner = CliRunner()
    result = runner.invoke(show,
        ['tests/dummy.original.xml'],
        catch_exceptions=False
    )
    assert result.output == """\
Name              Stmts    Miss  Cover    Missing
--------------  -------  ------  -------  ---------
dummy/__init__        0       0  0.00%
dummy/dummy           4       2  50.00%   2, 5
TOTAL                 4       2  50.00%
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
Name              Stmts    Miss  Cover    Missing
--------------  -------  ------  -------  ---------
dummy/__init__        0       0  0.00%
dummy/dummy           4       2  50.00%   2, 5
TOTAL                 4       2  50.00%
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

    runner = CliRunner()
    for opt in ('-o', '--output'):
        result = runner.invoke(show, [
            'tests/cobertura.xml', opt, 'report.out'
        ], catch_exceptions=False)
        with open('report.out') as f:
            report = f.read()
        os.remove('report.out')
        assert result.output == ""
        assert report == """\
Name                         Stmts    Miss  Cover    Missing
-------------------------  -------  ------  -------  ---------
Main                            11       0  100.00%
search.BinarySearch             12       1  91.67%   24
search.ISortedArraySearch        0       0  100.00%
search.LinearSearch              7       2  71.43%   19-24
TOTAL                           30       3  90.00%"""


def test_diff__format_default():
    from pycobertura.cli import diff

    runner = CliRunner()
    result = runner.invoke(diff, [
        'tests/dummy.source1/coverage.xml',
        'tests/dummy.source2/coverage.xml',
    ], catch_exceptions=False)
    assert result.output == """\
Name          Stmts      Miss  Cover    Missing
------------  -------  ------  -------  ----------
dummy/dummy   -            \x1b[32m-2\x1b[39m  +40.00%  \x1b[32m-5\x1b[39m, \x1b[32m-6\x1b[39m
dummy/dummy2  +2           \x1b[31m+1\x1b[39m  -25.00%  \x1b[32m-2\x1b[39m, \x1b[32m-4\x1b[39m, \x1b[31m+5\x1b[39m
dummy/dummy3  +2           \x1b[31m+2\x1b[39m  -        \x1b[31m+1\x1b[39m, \x1b[31m+2\x1b[39m
TOTAL         +4           \x1b[31m+1\x1b[39m  +15.00%
"""


def test_diff__format_text():
    from pycobertura.cli import diff

    runner = CliRunner()
    for opt in ('-f', '--format'):
        result = runner.invoke(diff, [
            opt, 'text',
            'tests/dummy.source1/coverage.xml',
            'tests/dummy.source2/coverage.xml',
        ], catch_exceptions=False)
        assert result.output == """\
Name          Stmts      Miss  Cover    Missing
------------  -------  ------  -------  ----------
dummy/dummy   -            \x1b[32m-2\x1b[39m  +40.00%  \x1b[32m-5\x1b[39m, \x1b[32m-6\x1b[39m
dummy/dummy2  +2           \x1b[31m+1\x1b[39m  -25.00%  \x1b[32m-2\x1b[39m, \x1b[32m-4\x1b[39m, \x1b[31m+5\x1b[39m
dummy/dummy3  +2           \x1b[31m+2\x1b[39m  -        \x1b[31m+1\x1b[39m, \x1b[31m+2\x1b[39m
TOTAL         +4           \x1b[31m+1\x1b[39m  +15.00%
"""


def test_diff__output_to_file():
    from pycobertura.cli import diff

    runner = CliRunner()

    for opt in ('-o', '--output'):
        result = runner.invoke(diff, [
            'tests/dummy.source1/coverage.xml',
            'tests/dummy.source2/coverage.xml',
            opt, 'report.out'
        ], catch_exceptions=False)
        with open('report.out') as f:
            report = f.read()
        os.remove('report.out')
        assert result.output == ""
        assert report == """\
Name          Stmts      Miss  Cover    Missing
------------  -------  ------  -------  ----------
dummy/dummy   -            -2  +40.00%  -5, -6
dummy/dummy2  +2           +1  -25.00%  -2, -4, +5
dummy/dummy3  +2           +2  -        +1, +2
TOTAL         +4           +1  +15.00%"""


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


def test_diff__format_html__no_source():
    from pycobertura.cli import diff

    runner = CliRunner()
    pytest.raises(IOError, runner.invoke, diff, [
        '--format', 'html',
        'tests/dummy.with-dummy2-better-cov.xml',
        'tests/dummy.with-dummy2-better-and-worse.xml',
    ], catch_exceptions=False)


def test_diff__format_html__with_source():
    from pycobertura.cli import diff

    runner = CliRunner()
    result = runner.invoke(diff, [
        '--format', 'html',
        '--source1', 'tests/dummy',
        '--source2', 'tests/dummy',
        'tests/dummy.with-dummy2-better-cov.xml',
        'tests/dummy.with-dummy2-better-and-worse.xml',
    ], catch_exceptions=False)
    assert result.output.startswith('<html>')
    assert result.output.endswith('</html>\n')


def test_diff__format_html__source():
    from pycobertura.cli import diff

    runner = CliRunner()
    result = runner.invoke(diff, [
        '--format', 'html',
        '--source',
        'tests/dummy.source1/coverage.xml',
        'tests/dummy.source2/coverage.xml',
    ], catch_exceptions=False)
    assert 'Missing' in result.output
    assert result.output.startswith('<html>')
    assert result.output.endswith('</html>\n')


def test_diff__format_html__source_is_default():
    from pycobertura.cli import diff

    runner = CliRunner()
    result = runner.invoke(diff, [
        '--format', 'html',
        'tests/dummy.source1/coverage.xml',
        'tests/dummy.source2/coverage.xml',
    ], catch_exceptions=False)
    assert 'Missing' in result.output
    assert result.output.startswith('<html>')
    assert result.output.endswith('</html>\n')


def test_diff__format_html__no_source():
    from pycobertura.cli import diff

    runner = CliRunner()
    result = runner.invoke(diff, [
        '--format', 'html',
        '--no-source',
        'tests/dummy.source1/coverage.xml',
        'tests/dummy.source2/coverage.xml',
    ], catch_exceptions=False)
    assert 'Missing' not in result.output
    assert result.output.startswith('<html>')
    assert result.output.endswith('</html>\n')


def test_diff__same_coverage_has_exit_status_of_zero():
    from pycobertura.cli import diff

    runner = CliRunner()
    result = runner.invoke(diff, [
        'tests/dummy.source1/coverage.xml',
        'tests/dummy.source1/coverage.xml',
    ], catch_exceptions=False)
    assert result.exit_code == 0


def test_diff__all_changes_covered_has_exit_status_of_zero():
    from pycobertura.cli import diff

    runner = CliRunner()
    result = runner.invoke(diff, [
        'tests/dummy.original.xml',
        'tests/dummy.original-full-cov.xml',  # has no uncovered lines
        '--no-source',
    ], catch_exceptions=False)
    assert result.exit_code == 0


def test_diff__not_all_changes_covered_has_exit_status_of_one():
    from pycobertura.cli import diff

    runner = CliRunner()
    result = runner.invoke(diff, [
        'tests/dummy.with-dummy2-no-cov.xml',
        'tests/dummy.with-dummy2-better-and-worse.xml',  # has covered AND uncovered lines
        '--no-source',
    ], catch_exceptions=False)
    assert result.exit_code == 1
