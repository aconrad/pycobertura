SOURCE_FILE = 'tests/cobertura.xml'


def make_cobertura(xml_file=SOURCE_FILE):
    from pycobertura import Cobertura
    cobertura = Cobertura(xml_file)
    return cobertura


def test_report_row_by_class():
    from pycobertura.reports import TextReport

    cobertura = make_cobertura()
    report = TextReport(cobertura)

    expected_rows = {
        'Main': ['Main', 11, 0, 1, []],
        'search.BinarySearch': ['search.BinarySearch', 12, 1, 0.9166666666666666, [24]],
        'search.LinearSearch': ['search.LinearSearch', 8, 3, 0.7142857142857143, [19, 20, 24]],
    }

    for class_name in cobertura.classes():
        row = report.get_report_row_by_class(class_name)
        assert row == expected_rows[class_name]


def test_text_report():
    from pycobertura.reports import TextReport

    cobertura = make_cobertura()
    report = TextReport(cobertura)

    assert report.generate() == """\
Name                   Stmts    Miss  Cover    Missing
-------------------  -------  ------  -------  ---------
Main                      11       0  100.00%
search.BinarySearch       12       1  91.67%   24
search.LinearSearch        8       3  71.43%   19-20, 24
TOTAL                     31       4  90.00%"""


def test_text_report_delta__no_diff():
    from pycobertura.reports import TextReport, TextReportDelta

    cobertura1 = make_cobertura('tests/dummy.original.xml')
    cobertura2 = make_cobertura('tests/dummy.original.xml')

    report_delta = TextReportDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Name         Stmts    Miss    Cover    Missing
-----------  -------  ------  -------  ---------
dummy/dummy  -        -       -
TOTAL        -        -       -"""


def test_text_report_delta__improve_coverage():
    from pycobertura.reports import TextReport, TextReportDelta

    cobertura1 = make_cobertura('tests/dummy.original.xml')
    cobertura2 = make_cobertura('tests/dummy.original-better-cov.xml')

    report_delta = TextReportDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Name         Stmts      Miss  Cover    Missing
-----------  -------  ------  -------  ---------
dummy/dummy  -            -1  +25.00%  -2
TOTAL        -            -1  +25.00%"""


def test_text_report_delta__full_coverage():
    from pycobertura.reports import TextReport, TextReportDelta

    cobertura1 = make_cobertura('tests/dummy.original.xml')
    cobertura2 = make_cobertura('tests/dummy.original-full-cov.xml')

    report_delta = TextReportDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Name         Stmts      Miss  Cover    Missing
-----------  -------  ------  -------  ---------
dummy/dummy  -            -2  +50.00%  -2, -5
TOTAL        -            -2  +50.00%"""


def test_text_report_delta__worsen_coverage():
    from pycobertura.reports import TextReport, TextReportDelta

    cobertura1 = make_cobertura('tests/dummy.original-better-cov.xml')
    cobertura2 = make_cobertura('tests/dummy.original.xml')

    report_delta = TextReportDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Name         Stmts      Miss  Cover    Missing
-----------  -------  ------  -------  ---------
dummy/dummy  -            +1  -25.00%  +2
TOTAL        -            +1  -25.00%"""


def test_text_report_delta__new_dummy2_class_has_no_coverage():
    from pycobertura.reports import TextReportDelta

    cobertura1 = make_cobertura('tests/dummy.original-full-cov.xml')
    cobertura2 = make_cobertura('tests/dummy.with-dummy2-no-cov.xml')

    report_delta = TextReportDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Name          Stmts    Miss    Cover    Missing
------------  -------  ------  -------  ---------
dummy/dummy   -        -       -
dummy/dummy2  +2       +2      -        +1, +2
TOTAL         +2       +2      -33.33%"""


def test_text_report_delta__new_dummy2_class_has_improved_coverage():
    from pycobertura.reports import TextReportDelta

    cobertura1 = make_cobertura('tests/dummy.original-full-cov.xml')
    cobertura2 = make_cobertura('tests/dummy.with-dummy2-better-cov.xml')

    report_delta = TextReportDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Name          Stmts    Miss    Cover    Missing
------------  -------  ------  -------  ---------
dummy/dummy   -        -       -
dummy/dummy2  +2       +1      +50.00%  +2
TOTAL         +2       +1      -16.67%"""


def test_text_report_delta__new_dummy2_class_has_full_coverage():
    from pycobertura.reports import TextReportDelta

    cobertura1 = make_cobertura('tests/dummy.original-full-cov.xml')
    cobertura2 = make_cobertura('tests/dummy.with-dummy2-full-cov.xml')

    report_delta = TextReportDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Name          Stmts    Miss    Cover     Missing
------------  -------  ------  --------  ---------
dummy/dummy   -        -       -
dummy/dummy2  +2       -       +100.00%
TOTAL         +2       -       -"""


def test_text_report_delta__removed_dummy2_class():
    from pycobertura.reports import TextReportDelta

    cobertura1 = make_cobertura('tests/dummy.with-dummy2-full-cov.xml')
    cobertura2 = make_cobertura('tests/dummy.original-full-cov.xml')

    report_delta = TextReportDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Name          Stmts    Miss    Cover    Missing
------------  -------  ------  -------  ---------
dummy/dummy   -        -       -
dummy/dummy2  -2       -       -
TOTAL         -2       -       -"""


def test_text_report_delta__removed_dummy2_class_and_worsen_coverage():
    from pycobertura.reports import TextReportDelta

    cobertura1 = make_cobertura('tests/dummy.with-dummy2-full-cov.xml')
    cobertura2 = make_cobertura('tests/dummy.original-better-cov.xml')

    report_delta = TextReportDelta(cobertura1, cobertura2)

    assert report_delta.generate() == """\
Name          Stmts    Miss    Cover    Missing
------------  -------  ------  -------  ---------
dummy/dummy   -        +1      -25.00%  +5
dummy/dummy2  -2       -       -
TOTAL         -2       +1      -25.00%"""
