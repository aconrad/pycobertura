import mock

import xml.etree.ElementTree as ET


SOURCE_FILE = 'tests/cobertura.xml'


def make_cobertura():
    from pycobertura import Cobertura
    cobertura = Cobertura(SOURCE_FILE)
    return cobertura


def test_parse_string():
    from pycobertura import Cobertura

    with open(SOURCE_FILE) as f:
        xml = f.read()

    cobertura = Cobertura(xml)
    assert isinstance(cobertura.xml, ET._Element)


def test_parse_fileobj():
    from pycobertura import Cobertura

    with open(SOURCE_FILE) as f:
        cobertura = Cobertura(f)
    assert isinstance(cobertura.xml, ET._Element)


def test_parse_path():
    from pycobertura import Cobertura

    xml_path = 'foo.xml'

    with mock.patch('pycobertura.cobertura.os.path.exists', return_value=True):
        with mock.patch('pycobertura.cobertura.ET.parse') as mock_parse:
            cobertura = Cobertura(xml_path)

    assert cobertura.xml is mock_parse.return_value.getroot.return_value


def test_version():
    cobertura = make_cobertura()
    assert cobertura.version == '1.9'


def test_line_rate():
    cobertura = make_cobertura()
    assert cobertura.line_rate() == 0.9


def test_line_rate_by_class():
    cobertura = make_cobertura()
    expected_line_rates = {
        'Main': 1.0,
        'search.BinarySearch': 0.9166666666666666,
        'search.LinearSearch': 0.7142857142857143,
    }

    for class_name in cobertura.classes():
        assert cobertura.line_rate(class_name) == \
            expected_line_rates[class_name]


def test_branch_rate():
    cobertura = make_cobertura()
    assert cobertura.branch_rate == 0.75


def test_list_packages():
    cobertura = make_cobertura()

    packages = cobertura.packages()
    assert packages == ['', 'search']


def test_list_classes():
    cobertura = make_cobertura()

    classes = cobertura.classes()
    assert classes == ['Main', 'search.BinarySearch', 'search.LinearSearch']


def test_line_hits__by_iterating_over_classes():
    cobertura = make_cobertura()

    expected_lines = {
        'Main': [10, 16, 17, 18, 19, 23, 25, 26, 28, 29, 30],
        'search.BinarySearch': [12, 16, 18, 20, 21, 23, 25, 26, 28, 29, 31],
        'search.LinearSearch': [9, 13, 15, 16, 17],
    }

    assert cobertura.line_hits('Main') == expected_lines['Main']
    assert cobertura.line_hits('search.BinarySearch') == \
        expected_lines['search.BinarySearch']
    assert cobertura.line_hits('search.LinearSearch') == \
        expected_lines['search.LinearSearch']


def test_line_hits_ranges():
    cobertura = make_cobertura()

    expected_ranges = {
        'Main': [(10, 10), (16, 19), (23, 23), (25, 26), (28, 30)],
        'search.BinarySearch': [
            (12, 12), (16, 16), (18, 18), (20, 21), (23, 23), (25, 26),
            (28, 29), (31, 31)],
        'search.LinearSearch': [(9, 9), (13, 13), (15, 17)],
    }

    for class_name in cobertura.classes():
        assert cobertura.line_hits_ranges(class_name) == \
            expected_ranges[class_name]


def test_line_misses():
    cobertura = make_cobertura()

    expected_lines = {
        'Main': [],
        'search.BinarySearch': [24],
        'search.LinearSearch': [19, 20, 24],
    }

    assert cobertura.line_misses('Main') == expected_lines['Main']
    assert cobertura.line_misses('search.BinarySearch') == \
        expected_lines['search.BinarySearch']
    assert cobertura.line_misses('search.LinearSearch') == \
        expected_lines['search.LinearSearch']


def test_line_misses__by_iterating_over_classes():
    cobertura = make_cobertura()

    expected_lines = {
        'Main': [],
        'search.BinarySearch': [24],
        'search.LinearSearch': [19, 20, 24],
    }

    for class_name in cobertura.classes():
        assert cobertura.line_misses(class_name) == expected_lines[class_name]


def test_line_misses_ranges():
    cobertura = make_cobertura()

    expected_ranges = {
        'Main': [],
        'search.BinarySearch': [(24, 24)],
        'search.LinearSearch': [(19, 20), (24, 24)],
    }

    for class_name in cobertura.classes():
        assert cobertura.line_misses_ranges(class_name) == \
            expected_ranges[class_name]


def test_total_lines():
    cobertura = make_cobertura()
    expected_total_lines = {
        'Main': 11,
        'search.BinarySearch': 12,
        'search.LinearSearch': 8,
    }
    for class_name in cobertura.classes():
        assert cobertura.total_lines(class_name) == \
            expected_total_lines[class_name]


def test_total_misses():
    cobertura = make_cobertura()
    expected_total_misses = {
        'Main': 0,
        'search.BinarySearch': 1,
        'search.LinearSearch': 3,
    }
    for class_name in cobertura.classes():
        assert cobertura.total_misses(class_name) == \
            expected_total_misses[class_name]


def test_total_hits():
    cobertura = make_cobertura()
    expected_total_misses = {
        'Main': 11,
        'search.BinarySearch': 11,
        'search.LinearSearch': 5,
    }
    for class_name in cobertura.classes():
        assert cobertura.total_hits(class_name) == \
            expected_total_misses[class_name]


def test_ranges_func__1():
    from pycobertura.cobertura import ranges

    assert ranges([1]) == [(1, 1)]


def test_ranges_func__1_2():
    from pycobertura.cobertura import ranges

    assert ranges([1, 2]) == [(1, 2)]


def test_ranges_func__1_2_3():
    from pycobertura.cobertura import ranges

    assert ranges([1, 2, 3]) == [(1, 3)]


def test_ranges_func__1_2_3_and_7():
    from pycobertura.cobertura import ranges

    assert ranges([1, 2, 3, 7]) == [(1, 3), (7, 7)]


def test_ranges_func__1_2_3_and_7_8():
    from pycobertura.cobertura import ranges

    assert ranges([1, 2, 3, 7, 8]) == [(1, 3), (7, 8)]


def test_ranges_func__1_2_3_and_7_8_9():
    from pycobertura.cobertura import ranges

    assert ranges([1, 2, 3, 7, 8, 9]) == [(1, 3), (7, 9)]


def test_ranges_func__1_and_7_8_9():
    from pycobertura.cobertura import ranges

    assert ranges([1, 7, 8, 9]) == [(1, 1), (7, 9)]


def test_ranges_func__1_2_and_7_8_9():
    from pycobertura.cobertura import ranges

    assert ranges([1, 2, 7, 8, 9]) == [(1, 2), (7, 9)]


def test_ranges_func__1_and_7():
    from pycobertura.cobertura import ranges

    assert ranges([1, 7]) == [(1, 1), (7, 7)]
