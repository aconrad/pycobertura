SOURCE_FILE = 'tests/cobertura.xml'


def make_cobertura():
    from pycobertura import Cobertura
    cobertura = Cobertura(SOURCE_FILE)
    return cobertura


def test_report_row_by_class():
    from pycobertura.reports import TextReport

    cobertura = make_cobertura()
    report = TextReport(cobertura)

    expected_rows = {
        'Main': ['Main', 11, 0, 1, []],
        'search.BinarySearch': ['search.BinarySearch', 12, 1, 0.9166666666666666, [(24, 24)]],
        'search.LinearSearch': ['search.LinearSearch', 8, 3, 0.7142857142857143, [(19, 20), (24, 24)]],
    }

    for class_name in cobertura.classes():
        row = report.get_report_row_by_class(class_name)
        assert row == expected_rows[class_name]


def test_format_row__no_uncovered_lines():
    from pycobertura.reports import format_row

    row = ['Main', 11, 0, 1, []]
    expected_row = ['Main', 11, 0, '100.00%', '']
    assert format_row(row) == expected_row


def test_format_row__uncovered_lines():
    from pycobertura.reports import format_row

    row = ['search.LinearSearch', 8, 3, 0.7142857142857143, [(19, 20), (24, 24)]]
    expected_row = ['search.LinearSearch', 8, 3, '71.43%', '19-20, 24']
    assert format_row(row) == expected_row


def test_make_footer_row():
    from pycobertura.reports import make_footer_row

    lines = [
        ['Main', 11, 0, 1, []],
        ['search.BinarySearch', 12, 1, 0.9166666666666666, [(24, 24)]],
        ['search.LinearSearch', 8, 3, 0.7142857142857143, [(19, 20), (24, 24)]],
    ]
    expected_footer = ['TOTAL', 31, 4, 0.876984126984127, []]

    footer = make_footer_row(lines)
    assert footer == expected_footer


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
TOTAL                     31       4  87.70%"""
