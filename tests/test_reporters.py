import mock


SOURCE_FILE = 'tests/cobertura.xml'


def make_cobertura(xml_file=SOURCE_FILE):
    from pycobertura import Cobertura
    cobertura = Cobertura(xml_file)
    return cobertura


def test_report_row_by_class():
    from pycobertura.reporters import TextReporter

    cobertura = make_cobertura()
    report = TextReporter(cobertura)

    expected_rows = {
        'Main': ['Main', 11, 0, 1, []],
        'search.BinarySearch': ['search.BinarySearch', 12, 1, 0.9166666666666666, [24]],
        'search.LinearSearch': ['search.LinearSearch', 8, 3, 0.7142857142857143, [19, 20, 24]],
    }

    for class_name in cobertura.classes():
        row = report.get_report_row_by_class(class_name)
        assert row == expected_rows[class_name]


def test_text_report():
    from pycobertura.reporters import TextReporter

    cobertura = make_cobertura()
    report = TextReporter(cobertura)

    assert report.generate() == """\
Name                   Stmts    Miss  Cover    Missing
-------------------  -------  ------  -------  ---------
Main                      11       0  100.00%
search.BinarySearch       12       1  91.67%   24
search.LinearSearch        8       3  71.43%   19-20, 24
TOTAL                     31       4  90.00%"""


def test_text_report_delta__no_diff():
    from pycobertura.reporters import TextReporter, TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.original.xml')
    cobertura2 = make_cobertura('tests/dummy.original.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Name         Stmts    Miss    Cover    Missing
-----------  -------  ------  -------  ---------
dummy/dummy  -        -       -
TOTAL        -        -       -"""


def test_text_report_delta__improve_coverage():
    from pycobertura.reporters import TextReporter, TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.original.xml')
    cobertura2 = make_cobertura('tests/dummy.original-better-cov.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Name         Stmts      Miss  Cover    Missing
-----------  -------  ------  -------  ---------
dummy/dummy  -            -1  +25.00%  -2
TOTAL        -            -1  +25.00%"""


def test_text_report_delta__full_coverage():
    from pycobertura.reporters import TextReporter, TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.original.xml')
    cobertura2 = make_cobertura('tests/dummy.original-full-cov.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Name         Stmts      Miss  Cover    Missing
-----------  -------  ------  -------  ---------
dummy/dummy  -            -2  +50.00%  -2, -5
TOTAL        -            -2  +50.00%"""


def test_text_report_delta__worsen_coverage():
    from pycobertura.reporters import TextReporter, TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.original-better-cov.xml')
    cobertura2 = make_cobertura('tests/dummy.original.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Name         Stmts      Miss  Cover    Missing
-----------  -------  ------  -------  ---------
dummy/dummy  -            +1  -25.00%  +2
TOTAL        -            +1  -25.00%"""


def test_text_report_delta__new_dummy2_class_has_no_coverage():
    from pycobertura.reporters import TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.original-full-cov.xml')
    cobertura2 = make_cobertura('tests/dummy.with-dummy2-no-cov.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Name          Stmts    Miss    Cover    Missing
------------  -------  ------  -------  ---------
dummy/dummy   -        -       -
dummy/dummy2  +2       +2      -        +1, +2
TOTAL         +2       +2      -33.33%"""


def test_text_report_delta__new_dummy2_class_has_improved_coverage():
    from pycobertura.reporters import TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.original-full-cov.xml')
    cobertura2 = make_cobertura('tests/dummy.with-dummy2-better-cov.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Name          Stmts    Miss    Cover    Missing
------------  -------  ------  -------  ---------
dummy/dummy   -        -       -
dummy/dummy2  +2       +1      +50.00%  +2
TOTAL         +2       +1      -16.67%"""


def test_text_report_delta__new_dummy2_class_has_full_coverage():
    from pycobertura.reporters import TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.original-full-cov.xml')
    cobertura2 = make_cobertura('tests/dummy.with-dummy2-full-cov.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Name          Stmts    Miss    Cover     Missing
------------  -------  ------  --------  ---------
dummy/dummy   -        -       -
dummy/dummy2  +2       -       +100.00%
TOTAL         +2       -       -"""


def test_text_report_delta__removed_dummy2_class():
    from pycobertura.reporters import TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.with-dummy2-full-cov.xml')
    cobertura2 = make_cobertura('tests/dummy.original-full-cov.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Name          Stmts    Miss    Cover    Missing
------------  -------  ------  -------  ---------
dummy/dummy   -        -       -
dummy/dummy2  -2       -       -
TOTAL         -2       -       -"""


def test_text_report_delta__removed_dummy2_class_and_worsen_coverage():
    from pycobertura.reporters import TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.with-dummy2-full-cov.xml')
    cobertura2 = make_cobertura('tests/dummy.original-better-cov.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Name          Stmts    Miss    Cover    Missing
------------  -------  ------  -------  ---------
dummy/dummy   -        +1      -25.00%  +5
dummy/dummy2  -2       -       -
TOTAL         -2       +1      -25.00%"""


def test_text_report_delta__better_and_worse_coverage():
    from pycobertura.reporters import TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.with-dummy2-better-cov.xml')
    cobertura2 = make_cobertura('tests/dummy.with-dummy2-better-and-worse.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Name          Stmts    Miss    Cover    Missing
------------  -------  ------  -------  ---------
dummy/dummy   -        +1      -25.00%  +5
dummy/dummy2  -        -1      +50.00%  -2
TOTAL         -        -       -"""


@mock.patch('pycobertura.utils.sys.stdout.isatty', return_value=True)
def test_text_report_delta__colorize_for_tty(mock_tty):
    from pycobertura.reporters import TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.with-dummy2-better-cov.xml')
    cobertura2 = make_cobertura('tests/dummy.with-dummy2-better-and-worse.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Name          Stmts    Miss    Cover    Missing
------------  -------  ------  -------  ---------
dummy/dummy   -        +1      -25.00%  \x1b[31m+5\x1b[39m
dummy/dummy2  -        -1      +50.00%  \x1b[32m-2\x1b[39m
TOTAL         -        -       -"""


@mock.patch('pycobertura.utils.sys.stdout.isatty', return_value=False)
def test_text_report_delta__no_colorize_for_non_tty(mock_tty):
    from pycobertura.reporters import TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.with-dummy2-better-cov.xml')
    cobertura2 = make_cobertura('tests/dummy.with-dummy2-better-and-worse.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Name          Stmts    Miss    Cover    Missing
------------  -------  ------  -------  ---------
dummy/dummy   -        +1      -25.00%  +5
dummy/dummy2  -        -1      +50.00%  -2
TOTAL         -        -       -"""


@mock.patch('pycobertura.utils.sys.stdout.isatty', return_value=True)
def test_text_report_delta__force_colorize_when_tty_is_true(mock_tty):
    from pycobertura.reporters import TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.with-dummy2-better-cov.xml')
    cobertura2 = make_cobertura('tests/dummy.with-dummy2-better-and-worse.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2, color=True)

    assert report_delta.generate() == """\
Name          Stmts    Miss    Cover    Missing
------------  -------  ------  -------  ---------
dummy/dummy   -        +1      -25.00%  \x1b[31m+5\x1b[39m
dummy/dummy2  -        -1      +50.00%  \x1b[32m-2\x1b[39m
TOTAL         -        -       -"""


@mock.patch('pycobertura.utils.sys.stdout.isatty', return_value=False)
def test_text_report_delta__force_colorize_when_tty_is_false(mock_tty):
    from pycobertura.reporters import TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.with-dummy2-better-cov.xml')
    cobertura2 = make_cobertura('tests/dummy.with-dummy2-better-and-worse.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2, color=True)

    assert report_delta.generate() == """\
Name          Stmts    Miss    Cover    Missing
------------  -------  ------  -------  ---------
dummy/dummy   -        +1      -25.00%  \x1b[31m+5\x1b[39m
dummy/dummy2  -        -1      +50.00%  \x1b[32m-2\x1b[39m
TOTAL         -        -       -"""


@mock.patch('pycobertura.utils.sys.stdout.isatty', return_value=True)
def test_text_report_delta__force_no_colorize_when_tty_is_true(mock_tty):
    from pycobertura.reporters import TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.with-dummy2-better-cov.xml')
    cobertura2 = make_cobertura('tests/dummy.with-dummy2-better-and-worse.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2, color=False)

    assert report_delta.generate() == """\
Name          Stmts    Miss    Cover    Missing
------------  -------  ------  -------  ---------
dummy/dummy   -        +1      -25.00%  +5
dummy/dummy2  -        -1      +50.00%  -2
TOTAL         -        -       -"""


@mock.patch('pycobertura.utils.sys.stdout.isatty', return_value=False)
def test_text_report_delta__force_no_colorize_when_tty_is_false(mock_tty):
    from pycobertura.reporters import TextReporterDelta

    cobertura1 = make_cobertura('tests/dummy.with-dummy2-better-cov.xml')
    cobertura2 = make_cobertura('tests/dummy.with-dummy2-better-and-worse.xml')

    report_delta = TextReporterDelta(cobertura1, cobertura2, color=False)

    assert report_delta.generate() == """\
Name          Stmts    Miss    Cover    Missing
------------  -------  ------  -------  ---------
dummy/dummy   -        +1      -25.00%  +5
dummy/dummy2  -        -1      +50.00%  -2
TOTAL         -        -       -"""


def test_html_report():
    from pycobertura.reporters import HtmlReporter

    cobertura = make_cobertura()
    report = HtmlReporter(cobertura)

    assert report.generate() == """\
<html>
  <head>
    <title>pycobertura report</title>
    <meta charset="UTF-8">
  </head>
  <body>
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Stmts</th>
          <th>Miss</th>
          <th>Cover</th>
          <th>Missing</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Main</td>
          <td>11</td>
          <td>0</td>
          <td>100.00%</td>
          <td></td>
        </tr>
        <tr>
          <td>search.BinarySearch</td>
          <td>12</td>
          <td>1</td>
          <td>91.67%</td>
          <td>24</td>
        </tr>
        <tr>
          <td>search.LinearSearch</td>
          <td>8</td>
          <td>3</td>
          <td>71.43%</td>
          <td>19-20, 24</td>
        </tr>
      </tbody>
      <tfoot>
        <tr>
          <td>TOTAL</td>
          <td>31</td>
          <td>4</td>
          <td>90.00%</td>
          <td></td>
        </tr>
      </tfoot>
    </table>
  </body>
</html>"""


def test_html_report_delta():
    from pycobertura.reporters import HtmlReporterDelta

    cobertura1 = make_cobertura('tests/dummy.original-full-cov.xml')
    cobertura2 = make_cobertura('tests/dummy.with-dummy2-no-cov.xml')

    report_delta = HtmlReporterDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
<html>
  <head>
    <title>pycobertura report</title>
    <meta charset="UTF-8">
    <style>
.red {color: red}
.green {color: green}
    </style>
  </head>
  <body>
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Stmts</th>
          <th>Miss</th>
          <th>Cover</th>
          <th>Missing</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>dummy/dummy</td>
          <td>-</td>
          <td>-</td>
          <td>-</td>
          <td>
          </td>
        </tr>
        <tr>
          <td>dummy/dummy2</td>
          <td>+2</td>
          <td>+2</td>
          <td>-</td>
          <td><span class="red">+1</span>, <span class="red">+2</span>
          </td>
        </tr>
      </tbody>
      <tfoot>
        <tr>
          <td>TOTAL</td>
          <td>+2</td>
          <td>+2</td>
          <td>-33.33%</td>
          <td></td>
        </tr>
      </tfoot>
    </table>
  </body>
</html>"""
