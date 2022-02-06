import os
import pytest
from click.testing import CliRunner


def test_exit_codes():
    # We shouldn't change exit codes so that clients can rely on them
    from pycobertura.cli import ExitCodes

    assert ExitCodes.OK == 0
    assert ExitCodes.EXCEPTION == 1
    assert ExitCodes.COVERAGE_WORSENED == 2
    assert ExitCodes.NOT_ALL_CHANGES_COVERED == 3


def test_show__format_default():
    from pycobertura.cli import show, ExitCodes

    runner = CliRunner()
    result = runner.invoke(
        show, ['tests/dummy.original.xml'], catch_exceptions=False
    )
    assert result.output == """\
Filename             Stmts    Miss  Cover    Missing
-----------------  -------  ------  -------  ---------
dummy/__init__.py        0       0  0.00%
dummy/dummy.py           4       2  50.00%   2, 5
TOTAL                    4       2  50.00%
"""
    assert result.exit_code == ExitCodes.OK


def test_show__format_text():
    from pycobertura.cli import show, ExitCodes

    runner = CliRunner()
    for opt in ('-f', '--format'):
        result = runner.invoke(
            show,
            ['tests/dummy.original.xml', opt, 'text'],
            catch_exceptions=False
        )
        assert result.output == """\
Filename             Stmts    Miss  Cover    Missing
-----------------  -------  ------  -------  ---------
dummy/__init__.py        0       0  0.00%
dummy/dummy.py           4       2  50.00%   2, 5
TOTAL                    4       2  50.00%
"""
    assert result.exit_code == ExitCodes.OK

def test_show__format_markdown():
    from pycobertura.cli import show, ExitCodes

    runner = CliRunner()
    for opt in ('-f', '--format'):
        result = runner.invoke(
            show,
            ['tests/dummy.original.xml', opt, 'markdown'],
            catch_exceptions=False
        )
        assert result.output == """\
| Filename          |   Stmts |   Miss | Cover   | Missing   |
|-------------------|---------|--------|---------|-----------|
| dummy/__init__.py |       0 |      0 | 0.00%   |           |
| dummy/dummy.py    |       4 |      2 | 50.00%  | 2, 5      |
| TOTAL             |       4 |      2 | 50.00%  |           |
"""
    assert result.exit_code == ExitCodes.OK


def test_show__format_html():
    from pycobertura.cli import show, ExitCodes

    runner = CliRunner()
    result = runner.invoke(show, [
        'tests/dummy.original.xml', '--format', 'html'
    ], catch_exceptions=False)
    assert result.output.startswith('<html>')
    assert result.output.endswith('</html>\n')
    assert result.exit_code == ExitCodes.OK


def test_show__format_json():
    from pycobertura.cli import show, ExitCodes

    runner = CliRunner()
    for opt in ('-f', '--format'):
        result = runner.invoke(
            show,
            ['tests/dummy.original.xml', opt, 'json'],
            catch_exceptions=False
        )
        assert result.output == """\
{
    "total": {
        "Filename": "TOTAL",
        "Stmts": 4,
        "Miss": 2,
        "Cover": "50.00%"
    },
    "files": {
        "Filename": [
            "dummy/__init__.py",
            "dummy/dummy.py"
        ],
        "Stmts": [
            0,
            4
        ],
        "Miss": [
            0,
            2
        ],
        "Cover": [
            "0.00%",
            "50.00%"
        ],
        "Missing": [
            "",
            "2, 5"
        ]
    }
}
"""
    assert result.exit_code == ExitCodes.OK


def test_show__output_to_file():
    from pycobertura.cli import show, ExitCodes

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
Filename                          Stmts    Miss  Cover    Missing
------------------------------  -------  ------  -------  ---------
Main.java                            15       0  100.00%
search/BinarySearch.java             12       1  91.67%   24
search/ISortedArraySearch.java        0       0  100.00%
search/LinearSearch.java              7       2  71.43%   19-24
TOTAL                                34       3  90.00%"""
    assert result.exit_code == ExitCodes.OK


def test_diff__format_default():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    result = runner.invoke(diff, [
        'tests/dummy.source1/coverage.xml',
        'tests/dummy.source2/coverage.xml',
    ], catch_exceptions=False)
    assert result.output == """\
Filename         Stmts      Miss  Cover    Missing
---------------  -------  ------  -------  ----------
dummy/dummy.py   -            \x1b[32m-2\x1b[39m  +40.00%  \x1b[32m-5\x1b[39m, \x1b[32m-6\x1b[39m
dummy/dummy2.py  +2           \x1b[31m+1\x1b[39m  -25.00%  \x1b[32m-2\x1b[39m, \x1b[32m-4\x1b[39m, \x1b[31m+5\x1b[39m
dummy/dummy3.py  +2           \x1b[31m+2\x1b[39m  -        \x1b[31m+1\x1b[39m, \x1b[31m+2\x1b[39m
TOTAL            +4           \x1b[31m+1\x1b[39m  +31.06%
"""
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED


def test_diff__format_text():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    for opt in ('-f', '--format'):
        result = runner.invoke(diff, [
            opt, 'text',
            'tests/dummy.source1/coverage.xml',
            'tests/dummy.source2/coverage.xml',
        ], catch_exceptions=False)
        assert result.output == """\
Filename         Stmts      Miss  Cover    Missing
---------------  -------  ------  -------  ----------
dummy/dummy.py   -            \x1b[32m-2\x1b[39m  +40.00%  \x1b[32m-5\x1b[39m, \x1b[32m-6\x1b[39m
dummy/dummy2.py  +2           \x1b[31m+1\x1b[39m  -25.00%  \x1b[32m-2\x1b[39m, \x1b[32m-4\x1b[39m, \x1b[31m+5\x1b[39m
dummy/dummy3.py  +2           \x1b[31m+2\x1b[39m  -        \x1b[31m+1\x1b[39m, \x1b[31m+2\x1b[39m
TOTAL            +4           \x1b[31m+1\x1b[39m  +31.06%
"""
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED

def test_diff__format_markdown():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    for opt in ('-f', '--format'):
        result = runner.invoke(diff, [
            opt, 'markdown',
            'tests/dummy.source1/coverage.xml',
            'tests/dummy.source2/coverage.xml',
        ], catch_exceptions=False)
    assert result.output == """\
| Filename        | Stmts   |   Miss | Cover   | Missing    |
|-----------------|---------|--------|---------|------------|
| dummy/dummy.py  | -       |     \x1b[32m-2\x1b[39m | +40.00% | \x1b[32m-5\x1b[39m, \x1b[32m-6\x1b[39m     |
| dummy/dummy2.py | +2      |     \x1b[31m+1\x1b[39m | -25.00% | \x1b[32m-2\x1b[39m, \x1b[32m-4\x1b[39m, \x1b[31m+5\x1b[39m |
| dummy/dummy3.py | +2      |     \x1b[31m+2\x1b[39m | -       | \x1b[31m+1\x1b[39m, \x1b[31m+2\x1b[39m     |
| TOTAL           | +4      |     \x1b[31m+1\x1b[39m | +31.06% |            |
"""
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED


def test_diff__format_json():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    for opt in ('-f', '--format'):
        result = runner.invoke(diff, [
            opt, 'json',
            'tests/dummy.source1/coverage.xml',
            'tests/dummy.source2/coverage.xml',
        ], catch_exceptions=False)
        assert result.output == """\
{
    "total": {
        "Filename": "TOTAL",
        "Stmts": "+4",
        "Miss": "\u001b[31m+1\u001b[39m",
        "Cover": "+31.06%"
    },
    "files": {
        "Filename": [
            "dummy/dummy.py",
            "dummy/dummy2.py",
            "dummy/dummy3.py"
        ],
        "Stmts": [
            null,
            "+2",
            "+2"
        ],
        "Miss": [
            "\u001b[32m-2\u001b[39m",
            "\u001b[31m+1\u001b[39m",
            "\u001b[31m+2\u001b[39m"
        ],
        "Cover": [
            "+40.00%",
            "-25.00%",
            null
        ],
        "Missing": [
            "\u001b[32m-5\u001b[39m, \u001b[32m-6\u001b[39m",
            "\u001b[32m-2\u001b[39m, \u001b[32m-4\u001b[39m, \u001b[31m+5\u001b[39m",
            "\u001b[31m+1\u001b[39m, \u001b[31m+2\u001b[39m"
        ]
    }
}
"""
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED


def test_diff__output_to_file():
    from pycobertura.cli import diff, ExitCodes

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
Filename         Stmts      Miss  Cover    Missing
---------------  -------  ------  -------  ----------
dummy/dummy.py   -            -2  +40.00%  -5, -6
dummy/dummy2.py  +2           +1  -25.00%  -2, -4, +5
dummy/dummy3.py  +2           +2  -        +1, +2
TOTAL            +4           +1  +31.06%"""
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED


def test_diff__output_to_file__force_color():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()

    result = runner.invoke(diff, [
        'tests/dummy.source1/coverage.xml',
        'tests/dummy.source2/coverage.xml',
        '--color', '--output', 'report.out'
    ], catch_exceptions=False)
    with open('report.out') as f:
        report = f.read()
    os.remove('report.out')
    assert result.output == ""
    assert report == """\
Filename         Stmts      Miss  Cover    Missing
---------------  -------  ------  -------  ----------
dummy/dummy.py   -            \x1b[32m-2\x1b[39m  +40.00%  \x1b[32m-5\x1b[39m, \x1b[32m-6\x1b[39m
dummy/dummy2.py  +2           \x1b[31m+1\x1b[39m  -25.00%  \x1b[32m-2\x1b[39m, \x1b[32m-4\x1b[39m, \x1b[31m+5\x1b[39m
dummy/dummy3.py  +2           \x1b[31m+2\x1b[39m  -        \x1b[31m+1\x1b[39m, \x1b[31m+2\x1b[39m
TOTAL            +4           \x1b[31m+1\x1b[39m  +31.06%"""
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED


def test_diff__format_text__with_color():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    result = runner.invoke(diff, [
        '--color',
        'tests/dummy.source1/coverage.xml',
        'tests/dummy.source2/coverage.xml',
    ], catch_exceptions=False)
    assert result.output == """\
Filename         Stmts      Miss  Cover    Missing
---------------  -------  ------  -------  ----------
dummy/dummy.py   -            \x1b[32m-2\x1b[39m  +40.00%  \x1b[32m-5\x1b[39m, \x1b[32m-6\x1b[39m
dummy/dummy2.py  +2           \x1b[31m+1\x1b[39m  -25.00%  \x1b[32m-2\x1b[39m, \x1b[32m-4\x1b[39m, \x1b[31m+5\x1b[39m
dummy/dummy3.py  +2           \x1b[31m+2\x1b[39m  -        \x1b[31m+1\x1b[39m, \x1b[31m+2\x1b[39m
TOTAL            +4           \x1b[31m+1\x1b[39m  +31.06%
"""
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED


def test_diff__format_text__with_no_color():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    result = runner.invoke(diff, [
        '--no-color',
        'tests/dummy.source1/coverage.xml',
        'tests/dummy.source2/coverage.xml',
    ], catch_exceptions=False)
    assert result.output == """\
Filename         Stmts      Miss  Cover    Missing
---------------  -------  ------  -------  ----------
dummy/dummy.py   -            -2  +40.00%  -5, -6
dummy/dummy2.py  +2           +1  -25.00%  -2, -4, +5
dummy/dummy3.py  +2           +2  -        +1, +2
TOTAL            +4           +1  +31.06%
"""
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED

def test_diff__format_markdown__with_color():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    result = runner.invoke(diff, [
        '--color',
        'tests/dummy.source1/coverage.xml',
        'tests/dummy.source2/coverage.xml',
        '--format',
        'markdown',
    ], catch_exceptions=False)
    assert result.output == """\
| Filename        | Stmts   |   Miss | Cover   | Missing    |
|-----------------|---------|--------|---------|------------|
| dummy/dummy.py  | -       |     \x1b[32m-2\x1b[39m | +40.00% | \x1b[32m-5\x1b[39m, \x1b[32m-6\x1b[39m     |
| dummy/dummy2.py | +2      |     \x1b[31m+1\x1b[39m | -25.00% | \x1b[32m-2\x1b[39m, \x1b[32m-4\x1b[39m, \x1b[31m+5\x1b[39m |
| dummy/dummy3.py | +2      |     \x1b[31m+2\x1b[39m | -       | \x1b[31m+1\x1b[39m, \x1b[31m+2\x1b[39m     |
| TOTAL           | +4      |     \x1b[31m+1\x1b[39m | +31.06% |            |
"""
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED

def test_diff__format_markdown__with_no_color():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    result = runner.invoke(diff, [
        '--no-color',
        'tests/dummy.source1/coverage.xml',
        'tests/dummy.source2/coverage.xml',
        '--format',
        'markdown',
    ], catch_exceptions=False)
    assert result.output == """\
| Filename        | Stmts   |   Miss | Cover   | Missing    |
|-----------------|---------|--------|---------|------------|
| dummy/dummy.py  | -       |     -2 | +40.00% | -5, -6     |
| dummy/dummy2.py | +2      |     +1 | -25.00% | -2, -4, +5 |
| dummy/dummy3.py | +2      |     +2 | -       | +1, +2     |
| TOTAL           | +4      |     +1 | +31.06% |            |
"""
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED


def test_diff__format_json__with_color():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    result = runner.invoke(diff, [
        '--color',
        'tests/dummy.source1/coverage.xml',
        'tests/dummy.source2/coverage.xml',
        '--format',
        'json'
    ], catch_exceptions=False)
    assert result.output == """\
{
    "total": {
        "Filename": "TOTAL",
        "Stmts": "+4",
        "Miss": "\u001b[31m+1\u001b[39m",
        "Cover": "+31.06%"
    },
    "files": {
        "Filename": [
            "dummy/dummy.py",
            "dummy/dummy2.py",
            "dummy/dummy3.py"
        ],
        "Stmts": [
            null,
            "+2",
            "+2"
        ],
        "Miss": [
            "\u001b[32m-2\u001b[39m",
            "\u001b[31m+1\u001b[39m",
            "\u001b[31m+2\u001b[39m"
        ],
        "Cover": [
            "+40.00%",
            "-25.00%",
            null
        ],
        "Missing": [
            "\u001b[32m-5\u001b[39m, \u001b[32m-6\u001b[39m",
            "\u001b[32m-2\u001b[39m, \u001b[32m-4\u001b[39m, \u001b[31m+5\u001b[39m",
            "\u001b[31m+1\u001b[39m, \u001b[31m+2\u001b[39m"
        ]
    }
}
"""
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED


def test_diff__format_json__with_no_color():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    result = runner.invoke(diff, [
        '--no-color',
        'tests/dummy.source1/coverage.xml',
        'tests/dummy.source2/coverage.xml',
        '--format',
        'json'
    ], catch_exceptions=False)
    assert result.output == """\
{
    "total": {
        "Filename": "TOTAL",
        "Stmts": "+4",
        "Miss": "+1",
        "Cover": "+31.06%"
    },
    "files": {
        "Filename": [
            "dummy/dummy.py",
            "dummy/dummy2.py",
            "dummy/dummy3.py"
        ],
        "Stmts": [
            null,
            "+2",
            "+2"
        ],
        "Miss": [
            "-2",
            "+1",
            "+2"
        ],
        "Cover": [
            "+40.00%",
            "-25.00%",
            null
        ],
        "Missing": [
            "-5, -6",
            "-2, -4, +5",
            "+1, +2"
        ]
    }
}
"""
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED


def test_diff__format_html__no_source_on_disk():
    from pycobertura.cli import diff
    from pycobertura.filesystem import FileSystem

    runner = CliRunner()
    pytest.raises(FileSystem.FileNotFound, runner.invoke, diff, [
        '--format', 'html',
        'tests/dummy.with-dummy2-better-cov.xml',
        'tests/dummy.with-dummy2-better-and-worse.xml',
    ], catch_exceptions=False)


@pytest.mark.parametrize("source1, source2, prefix1, prefix2", [
    ("tests/", "tests/dummy", "dummy/", ""),
    ("tests/dummy", "tests/", "", "dummy/"),
    ("tests/dummy/dummy.zip", "tests/dummy/dummy.zip", "", ""),
    ("tests/dummy/dummy-with-prefix.zip", "tests/dummy", "dummy-with-prefix", ""),
    ("tests/dummy/dummy-with-prefix.zip", "tests/dummy/dummy.zip", "dummy-with-prefix", ""),
])
def test_diff__format_html__with_source_prefix(source1, source2, prefix1, prefix2):
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    result = runner.invoke(diff, [
        '--format', 'html',
        '--source1', source1,
        '--source2', source2,
        '--source-prefix1', prefix1,
        '--source-prefix2', prefix2,
        'tests/dummy.with-dummy2-better-cov.xml',
        'tests/dummy.with-dummy2-better-and-worse.xml',
    ], catch_exceptions=False)
    assert result.output.startswith('<html>')
    assert result.output.endswith('</html>\n')
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED


@pytest.mark.parametrize("source1, source2", [
    ("tests/dummy", "tests/dummy"),
    ("tests/dummy/dummy.zip", "tests/dummy/dummy.zip"),
])
def test_diff__format_html__with_source(source1, source2):
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    result = runner.invoke(diff, [
        '--format', 'html',
        '--source1', source1,
        '--source2', source2,
        'tests/dummy.with-dummy2-better-cov.xml',
        'tests/dummy.with-dummy2-better-and-worse.xml',
    ], catch_exceptions=False)
    assert result.output.startswith('<html>')
    assert result.output.endswith('</html>\n')
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED


def test_diff__format_html__source():
    from pycobertura.cli import diff, ExitCodes

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
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED


def test_diff__format_html__source_is_default():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    result = runner.invoke(diff, [
        '--format', 'html',
        'tests/dummy.source1/coverage.xml',
        'tests/dummy.source2/coverage.xml',
    ], catch_exceptions=False)
    assert 'Missing' in result.output
    assert result.output.startswith('<html>')
    assert result.output.endswith('</html>\n')
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED


def test_diff__format_html__no_source():
    from pycobertura.cli import diff, ExitCodes

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
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED


def test_diff__same_coverage_has_exit_status_of_zero():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    result = runner.invoke(diff, [
        'tests/dummy.source1/coverage.xml',
        'tests/dummy.source1/coverage.xml',
    ], catch_exceptions=False)
    assert result.exit_code == ExitCodes.OK


def test_diff__better_coverage_has_exit_status_of_zero():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    result = runner.invoke(diff, [
        'tests/dummy.original.xml',
        'tests/dummy.original-full-cov.xml',  # has no uncovered lines
        '--no-source',
    ], catch_exceptions=False)
    assert result.exit_code == ExitCodes.OK


def test_diff__worse_coverage_exit_status():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    result = runner.invoke(diff, [
        'tests/dummy.with-dummy2-no-cov.xml',
        'tests/dummy.with-dummy2-better-and-worse.xml',  # has covered AND uncovered lines
        '--no-source',
    ], catch_exceptions=False)
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED


def test_diff__changes_uncovered_but_with_better_coverage_exit_status():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    result = runner.invoke(diff, [
        'tests/dummy.zeroexit1/coverage.xml',
        'tests/dummy.zeroexit2/coverage.xml',  # has uncovered changes
    ], catch_exceptions=False)
    assert result.exit_code == ExitCodes.NOT_ALL_CHANGES_COVERED


def test_diff__line_status():
    from pycobertura.cli import diff

    runner = CliRunner()
    runner.invoke(diff, [
        'tests/dummy.linestatus/test1.xml',
        'tests/dummy.linestatus/test2.xml',
    ], catch_exceptions=False)
    assert True
