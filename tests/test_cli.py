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

def test_show__format_csv():
    from pycobertura.cli import show, ExitCodes

    runner = CliRunner()
    for opt in ('-f', '--format'):
        result = runner.invoke(
            show,
            ['tests/dummy.original.xml', opt, 'csv'],
            catch_exceptions=False
        )
        assert result.output == """\
Filename;Stmts;Miss;Cover;Missing
dummy/__init__.py;0;0;0.00%;
dummy/dummy.py;4;2;50.00%;2, 5
TOTAL;4;2;50.00%;
"""
    assert result.exit_code == ExitCodes.OK

def test_show__format_csv_delimiter_semicolon():
    from pycobertura.cli import show, ExitCodes

    runner = CliRunner()
    for opt in ('-f', '--format'):
        result = runner.invoke(
            show,
            ['tests/dummy.original.xml', opt, 'csv', '--delimiter', ';'],
            catch_exceptions=False
        )
        assert result.output == """\
Filename;Stmts;Miss;Cover;Missing
dummy/__init__.py;0;0;0.00%;
dummy/dummy.py;4;2;50.00%;2, 5
TOTAL;4;2;50.00%;
"""
    assert result.exit_code == ExitCodes.OK

def test_show__format_csv_delimiter_tab():
    from pycobertura.cli import show, ExitCodes

    runner = CliRunner()
    for opt in ('-f', '--format'):
        result = runner.invoke(
            show,
            ['tests/dummy.original.xml', opt, 'csv', '--delimiter', '\t'],
            catch_exceptions=False
        )
        assert result.output == """\
Filename\tStmts\tMiss\tCover\tMissing
dummy/__init__.py\t0\t0\t0.00%\t
dummy/dummy.py\t4\t2\t50.00%\t2, 5
TOTAL\t4\t2\t50.00%\t
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
    "files": [
        {
            "Filename": "dummy/__init__.py",
            "Stmts": 0,
            "Miss": 0,
            "Cover": "0.00%",
            "Missing": ""
        },
        {
            "Filename": "dummy/dummy.py",
            "Stmts": 4,
            "Miss": 2,
            "Cover": "50.00%",
            "Missing": "2, 5"
        }
    ],
    "total": {
        "Filename": "TOTAL",
        "Stmts": 4,
        "Miss": 2,
        "Cover": "50.00%"
    }
}
"""
    assert result.exit_code == ExitCodes.OK

def test_show__format_yaml():
    from pycobertura.cli import show, ExitCodes

    runner = CliRunner()
    for opt in ('-f', '--format'):
        result = runner.invoke(
            show,
            ['tests/dummy.original.xml', opt, 'yaml'],
            catch_exceptions=False
        )
        assert result.output == """\
files:
- Filename: dummy/__init__.py
  Stmts: 0
  Miss: 0
  Cover: 0.00%
  Missing: ''
- Filename: dummy/dummy.py
  Stmts: 4
  Miss: 2
  Cover: 50.00%
  Missing: 2, 5
total:
  Filename: TOTAL
  Stmts: 4
  Miss: 2
  Cover: 50.00%

"""
    assert result.exit_code == ExitCodes.OK

def test_show__format_github_annotation():
    from pycobertura.cli import show, ExitCodes

    runner = CliRunner()
    for opt in ("-f", "--format"):
        result = runner.invoke(
            show,
            ["tests/dummy.original.xml", opt, "github-annotation"],
            catch_exceptions=False,
        )
        assert (
            result.output
            == """\
::notice file=dummy/dummy.py,line=2,endLine=2,title=pycobertura::not covered
::notice file=dummy/dummy.py,line=5,endLine=5,title=pycobertura::not covered
"""
        )
    assert result.exit_code == ExitCodes.OK


def test_show__format_github_annotation_custom_annotation_input():
    from pycobertura.cli import show, ExitCodes

    runner = CliRunner()
    for opt in ("-f", "--format"):
        result = runner.invoke(
            show,
            [
                "tests/dummy.original.xml",
                opt,
                "github-annotation",
                "--annotation-title=coverage.py",
                "--annotation-level=error",
                "--annotation-message=missing coverage",
            ],
            catch_exceptions=False,
        )
        assert (
            result.output
            == """\
::error file=dummy/dummy.py,line=2,endLine=2,title=coverage.py::missing coverage
::error file=dummy/dummy.py,line=5,endLine=5,title=coverage.py::missing coverage
"""
        )
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
Filename           Stmts    Miss  Cover     Missing
---------------  -------  ------  --------  ---------
dummy/dummy.py         0      \x1b[32m-2\x1b[39m  +40.00%
dummy/dummy2.py       +2      \x1b[31m+1\x1b[39m  -25.00%   \x1b[31m5\x1b[39m
dummy/dummy3.py       +2      \x1b[31m+2\x1b[39m  +100.00%  \x1b[31m1\x1b[39m, \x1b[31m2\x1b[39m
dummy/dummy4.py       -5      \x1b[32m-5\x1b[39m  +100.00%
TOTAL                 -1      \x1b[32m-4\x1b[39m  +31.06%
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
Filename           Stmts    Miss  Cover     Missing
---------------  -------  ------  --------  ---------
dummy/dummy.py         0      \x1b[32m-2\x1b[39m  +40.00%
dummy/dummy2.py       +2      \x1b[31m+1\x1b[39m  -25.00%   \x1b[31m5\x1b[39m
dummy/dummy3.py       +2      \x1b[31m+2\x1b[39m  +100.00%  \x1b[31m1\x1b[39m, \x1b[31m2\x1b[39m
dummy/dummy4.py       -5      \x1b[32m-5\x1b[39m  +100.00%
TOTAL                 -1      \x1b[32m-4\x1b[39m  +31.06%
"""
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED

def test_diff__format_csv():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    for opt in ('-f', '--format'):
        result = runner.invoke(diff, [
            opt, 'csv',
            'tests/dummy.source1/coverage.xml',
            'tests/dummy.source2/coverage.xml',
        ], catch_exceptions=False)
        assert result.output == """\
Filename;Stmts;Miss;Cover;Missing
dummy/dummy.py;0;\x1b[32m-2\x1b[39m;+40.00%;[]
dummy/dummy2.py;+2;\x1b[31m+1\x1b[39m;-25.00%;['\x1b[31m5\x1b[39m']
dummy/dummy3.py;+2;\x1b[31m+2\x1b[39m;+100.00%;['\x1b[31m1\x1b[39m', '\x1b[31m2\x1b[39m']
dummy/dummy4.py;-5;\x1b[32m-5\x1b[39m;+100.00%;[]
TOTAL;-1;\x1b[32m-4\x1b[39m;+31.06%;[]
"""
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED

def test_diff__format_csv_delimiter_semicolon():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    for delim_opt in ('-delim', '--delimiter'):
        for opt in ('-f', '--format'):
            result = runner.invoke(diff, [
                opt, 'csv',
                'tests/dummy.source1/coverage.xml',
                'tests/dummy.source2/coverage.xml',
                delim_opt, ';',
        ], catch_exceptions=False)
        assert result.output == """\
Filename;Stmts;Miss;Cover;Missing
dummy/dummy.py;0;\x1b[32m-2\x1b[39m;+40.00%;[]
dummy/dummy2.py;+2;\x1b[31m+1\x1b[39m;-25.00%;['\x1b[31m5\x1b[39m']
dummy/dummy3.py;+2;\x1b[31m+2\x1b[39m;+100.00%;['\x1b[31m1\x1b[39m', '\x1b[31m2\x1b[39m']
dummy/dummy4.py;-5;\x1b[32m-5\x1b[39m;+100.00%;[]
TOTAL;-1;\x1b[32m-4\x1b[39m;+31.06%;[]
"""
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED

def test_diff__format_csv_delimiter_tab():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    for delim_opt in ('-delim', '--delimiter'):
        for opt in ('-f', '--format'):
            result = runner.invoke(diff, [
                opt, 'csv',
                'tests/dummy.source1/coverage.xml',
                'tests/dummy.source2/coverage.xml',
                delim_opt, '\t'
            ], catch_exceptions=False)
        assert result.output == """\
Filename\tStmts\tMiss\tCover\tMissing
dummy/dummy.py\t0\t\x1b[32m-2\x1b[39m\t+40.00%\t[]
dummy/dummy2.py\t+2\t\x1b[31m+1\x1b[39m\t-25.00%\t['\x1b[31m5\x1b[39m']
dummy/dummy3.py\t+2\t\x1b[31m+2\x1b[39m\t+100.00%\t['\x1b[31m1\x1b[39m', '\x1b[31m2\x1b[39m']
dummy/dummy4.py\t-5\t\x1b[32m-5\x1b[39m\t+100.00%\t[]
TOTAL\t-1\t\x1b[32m-4\x1b[39m\t+31.06%\t[]
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
| Filename        |   Stmts |   Miss | Cover    | Missing   |
|-----------------|---------|--------|----------|-----------|
| dummy/dummy.py  |       0 |     \x1b[32m-2\x1b[39m | +40.00%  |           |
| dummy/dummy2.py |      +2 |     \x1b[31m+1\x1b[39m | -25.00%  | \x1b[31m5\x1b[39m         |
| dummy/dummy3.py |      +2 |     \x1b[31m+2\x1b[39m | +100.00% | \x1b[31m1\x1b[39m, \x1b[31m2\x1b[39m      |
| dummy/dummy4.py |      -5 |     \x1b[32m-5\x1b[39m | +100.00% |           |
| TOTAL           |      -1 |     \x1b[32m-4\x1b[39m | +31.06%  |           |
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
    "files": [
        {
            "Filename": "dummy/dummy.py",
            "Stmts": "0",
            "Miss": "\u001b[32m-2\x1b[39m",
            "Cover": "+40.00%",
            "Missing": ""
        },
        {
            "Filename": "dummy/dummy2.py",
            "Stmts": "+2",
            "Miss": "\u001b[31m+1\u001b[39m",
            "Cover": "-25.00%",
            "Missing": "\u001b[31m5\u001b[39m"
        },
        {
            "Filename": "dummy/dummy3.py",
            "Stmts": "+2",
            "Miss": "\u001b[31m+2\u001b[39m",
            "Cover": "+100.00%",
            "Missing": "\u001b[31m1\u001b[39m, \u001b[31m2\u001b[39m"
        },
        {
            "Filename": "dummy/dummy4.py",
            "Stmts": "-5",
            "Miss": "\u001b[32m-5\u001b[39m",
            "Cover": "+100.00%",
            "Missing": ""
        }
    ],
    "total": {
        "Filename": "TOTAL",
        "Stmts": "-1",
        "Miss": "\u001b[32m-4\u001b[39m",
        "Cover": "+31.06%"
    }
}
"""
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED

def test_diff__format_yaml():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    for opt in ('-f', '--format'):
        result = runner.invoke(diff, [
            opt, 'yaml',
            'tests/dummy.source1/coverage.xml',
            'tests/dummy.source2/coverage.xml',
        ], catch_exceptions=False)
        assert result.output == """\
files:
- Filename: dummy/dummy.py
  Stmts: '0'
  Miss: "\x1b[32m-2\x1b[39m"
  Cover: +40.00%
  Missing: ''
- Filename: dummy/dummy2.py
  Stmts: '+2'
  Miss: "\x1b[31m+1\x1b[39m"
  Cover: -25.00%
  Missing: "\x1b[31m5\x1b[39m"
- Filename: dummy/dummy3.py
  Stmts: '+2'
  Miss: "\x1b[31m+2\x1b[39m"
  Cover: +100.00%
  Missing: "\x1b[31m1\x1b[39m, \x1b[31m2\x1b[39m"
- Filename: dummy/dummy4.py
  Stmts: '-5'
  Miss: "\x1b[32m-5\x1b[39m"
  Cover: +100.00%
  Missing: ''
total:
  Filename: TOTAL
  Stmts: '-1'
  Miss: "\x1b[32m-4\x1b[39m"
  Cover: +31.06%

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
Filename           Stmts    Miss  Cover     Missing
---------------  -------  ------  --------  ---------
dummy/dummy.py         0      -2  +40.00%
dummy/dummy2.py       +2      +1  -25.00%   5
dummy/dummy3.py       +2      +2  +100.00%  1, 2
dummy/dummy4.py       -5      -5  +100.00%
TOTAL                 -1      -4  +31.06%"""
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
Filename           Stmts    Miss  Cover     Missing
---------------  -------  ------  --------  ---------
dummy/dummy.py         0      \x1b[32m-2\x1b[39m  +40.00%
dummy/dummy2.py       +2      \x1b[31m+1\x1b[39m  -25.00%   \x1b[31m5\x1b[39m
dummy/dummy3.py       +2      \x1b[31m+2\x1b[39m  +100.00%  \x1b[31m1\x1b[39m, \x1b[31m2\x1b[39m
dummy/dummy4.py       -5      \x1b[32m-5\x1b[39m  +100.00%
TOTAL                 -1      \x1b[32m-4\x1b[39m  +31.06%"""
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
Filename           Stmts    Miss  Cover     Missing
---------------  -------  ------  --------  ---------
dummy/dummy.py         0      \x1b[32m-2\x1b[39m  +40.00%
dummy/dummy2.py       +2      \x1b[31m+1\x1b[39m  -25.00%   \x1b[31m5\x1b[39m
dummy/dummy3.py       +2      \x1b[31m+2\x1b[39m  +100.00%  \x1b[31m1\x1b[39m, \x1b[31m2\x1b[39m
dummy/dummy4.py       -5      \x1b[32m-5\x1b[39m  +100.00%
TOTAL                 -1      \x1b[32m-4\x1b[39m  +31.06%
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
Filename           Stmts    Miss  Cover     Missing
---------------  -------  ------  --------  ---------
dummy/dummy.py         0      -2  +40.00%
dummy/dummy2.py       +2      +1  -25.00%   5
dummy/dummy3.py       +2      +2  +100.00%  1, 2
dummy/dummy4.py       -5      -5  +100.00%
TOTAL                 -1      -4  +31.06%
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
| Filename        |   Stmts |   Miss | Cover    | Missing   |
|-----------------|---------|--------|----------|-----------|
| dummy/dummy.py  |       0 |     \x1b[32m-2\x1b[39m | +40.00%  |           |
| dummy/dummy2.py |      +2 |     \x1b[31m+1\x1b[39m | -25.00%  | \x1b[31m5\x1b[39m         |
| dummy/dummy3.py |      +2 |     \x1b[31m+2\x1b[39m | +100.00% | \x1b[31m1\x1b[39m, \x1b[31m2\x1b[39m      |
| dummy/dummy4.py |      -5 |     \x1b[32m-5\x1b[39m | +100.00% |           |
| TOTAL           |      -1 |     \x1b[32m-4\x1b[39m | +31.06%  |           |
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
| Filename        |   Stmts |   Miss | Cover    | Missing   |
|-----------------|---------|--------|----------|-----------|
| dummy/dummy.py  |       0 |     -2 | +40.00%  |           |
| dummy/dummy2.py |      +2 |     +1 | -25.00%  | 5         |
| dummy/dummy3.py |      +2 |     +2 | +100.00% | 1, 2      |
| dummy/dummy4.py |      -5 |     -5 | +100.00% |           |
| TOTAL           |      -1 |     -4 | +31.06%  |           |
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
    "files": [
        {
            "Filename": "dummy/dummy.py",
            "Stmts": "0",
            "Miss": "\u001b[32m-2\x1b[39m",
            "Cover": "+40.00%",
            "Missing": ""
        },
        {
            "Filename": "dummy/dummy2.py",
            "Stmts": "+2",
            "Miss": "\u001b[31m+1\u001b[39m",
            "Cover": "-25.00%",
            "Missing": "\u001b[31m5\u001b[39m"
        },
        {
            "Filename": "dummy/dummy3.py",
            "Stmts": "+2",
            "Miss": "\u001b[31m+2\u001b[39m",
            "Cover": "+100.00%",
            "Missing": "\u001b[31m1\u001b[39m, \u001b[31m2\u001b[39m"
        },
        {
            "Filename": "dummy/dummy4.py",
            "Stmts": "-5",
            "Miss": "\u001b[32m-5\u001b[39m",
            "Cover": "+100.00%",
            "Missing": ""
        }
    ],
    "total": {
        "Filename": "TOTAL",
        "Stmts": "-1",
        "Miss": "\u001b[32m-4\u001b[39m",
        "Cover": "+31.06%"
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
    "files": [
        {
            "Filename": "dummy/dummy.py",
            "Stmts": "0",
            "Miss": "-2",
            "Cover": "+40.00%",
            "Missing": ""
        },
        {
            "Filename": "dummy/dummy2.py",
            "Stmts": "+2",
            "Miss": "+1",
            "Cover": "-25.00%",
            "Missing": "5"
        },
        {
            "Filename": "dummy/dummy3.py",
            "Stmts": "+2",
            "Miss": "+2",
            "Cover": "+100.00%",
            "Missing": "1, 2"
        },
        {
            "Filename": "dummy/dummy4.py",
            "Stmts": "-5",
            "Miss": "-5",
            "Cover": "+100.00%",
            "Missing": ""
        }
    ],
    "total": {
        "Filename": "TOTAL",
        "Stmts": "-1",
        "Miss": "-4",
        "Cover": "+31.06%"
    }
}
"""
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED

def test_diff__format_yaml_with_color():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    for opt in ('-f', '--format'):
        result = runner.invoke(diff, [
            '--color',
            opt, 'yaml',
            'tests/dummy.source1/coverage.xml',
            'tests/dummy.source2/coverage.xml',
        ], catch_exceptions=False)
        assert result.output == """\
files:
- Filename: dummy/dummy.py
  Stmts: '0'
  Miss: "\x1b[32m-2\x1b[39m"
  Cover: +40.00%
  Missing: ''
- Filename: dummy/dummy2.py
  Stmts: '+2'
  Miss: "\x1b[31m+1\x1b[39m"
  Cover: -25.00%
  Missing: "\x1b[31m5\x1b[39m"
- Filename: dummy/dummy3.py
  Stmts: '+2'
  Miss: "\x1b[31m+2\x1b[39m"
  Cover: +100.00%
  Missing: "\x1b[31m1\x1b[39m, \x1b[31m2\x1b[39m"
- Filename: dummy/dummy4.py
  Stmts: '-5'
  Miss: "\x1b[32m-5\x1b[39m"
  Cover: +100.00%
  Missing: ''
total:
  Filename: TOTAL
  Stmts: '-1'
  Miss: "\x1b[32m-4\x1b[39m"
  Cover: +31.06%

"""
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED

def test_diff__format_yaml_with_no_color():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    for opt in ('-f', '--format'):
        result = runner.invoke(diff, [
            '--no-color',
            opt, 'yaml',
            'tests/dummy.source1/coverage.xml',
            'tests/dummy.source2/coverage.xml',
        ], catch_exceptions=False)
        assert result.output == """\
files:
- Filename: dummy/dummy.py
  Stmts: '0'
  Miss: '-2'
  Cover: +40.00%
  Missing: ''
- Filename: dummy/dummy2.py
  Stmts: '+2'
  Miss: '+1'
  Cover: -25.00%
  Missing: '5'
- Filename: dummy/dummy3.py
  Stmts: '+2'
  Miss: '+2'
  Cover: +100.00%
  Missing: 1, 2
- Filename: dummy/dummy4.py
  Stmts: '-5'
  Miss: '-5'
  Cover: +100.00%
  Missing: ''
total:
  Filename: TOTAL
  Stmts: '-1'
  Miss: '-4'
  Cover: +31.06%

"""
    assert result.exit_code == ExitCodes.COVERAGE_WORSENED


def test_diff__format_github_annotation():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    for opt in ('-f', '--format'):
        result = runner.invoke(diff, [
            opt, 'github-annotation',
            'tests/dummy.source1/coverage.xml',
            'tests/dummy.source2/coverage.xml',
        ], catch_exceptions=False)
        assert result.output == """\
::notice file=dummy/dummy2.py,line=5,endLine=5,title=pycobertura::not covered
::notice file=dummy/dummy3.py,line=1,endLine=2,title=pycobertura::not covered
"""
        assert result.exit_code == ExitCodes.COVERAGE_WORSENED


def test_diff__format_github_annotation_custom_annotation_input():
    from pycobertura.cli import diff, ExitCodes

    runner = CliRunner()
    for opt in ('-f', '--format'):
        result = runner.invoke(diff, [
            opt, 'github-annotation',
            'tests/dummy.source1/coverage.xml',
            'tests/dummy.source2/coverage.xml',
            "--annotation-title=coverage.py",
            "--annotation-level=error",
            "--annotation-message=missing coverage",
        ], catch_exceptions=False)
        assert result.output == """\
::error file=dummy/dummy2.py,line=5,endLine=5,title=coverage.py::missing coverage
::error file=dummy/dummy3.py,line=1,endLine=2,title=coverage.py::missing coverage
"""
        assert result.exit_code == ExitCodes.COVERAGE_WORSENED

def test_diff__format_html__no_source_on_disk():
    from pycobertura.cli import diff
    from pycobertura.filesystem import FileSystem
    runner = CliRunner()
    import sys
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
