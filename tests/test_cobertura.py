import mock

import lxml.etree as ET


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
        'search.ISortedArraySearch': 1.0,
        'search.LinearSearch': 0.7142857142857143,
    }

    for class_name in cobertura.classes():
        assert cobertura.line_rate(class_name) == \
            expected_line_rates[class_name]


def test_branch_rate():
    cobertura = make_cobertura()
    assert cobertura.branch_rate() == 0.75


def test_branch_rate_by_class():
    cobertura = make_cobertura()
    expected_branch_rates = {
        'Main': 1.0,
        'search.BinarySearch': 0.8333333333333334,
        'search.ISortedArraySearch': 1.0,
        'search.LinearSearch': 0.6666666666666666,
    }

    for class_name in cobertura.classes():
        assert cobertura.branch_rate(class_name) == \
            expected_branch_rates[class_name]


def test_list_packages():
    cobertura = make_cobertura()

    packages = cobertura.packages()
    assert packages == ['', 'search']


def test_list_classes():
    cobertura = make_cobertura()

    classes = cobertura.classes()
    assert classes == [
        'Main',
        'search.BinarySearch',
        'search.ISortedArraySearch',
        'search.LinearSearch'
    ]


def test_line_hits__by_iterating_over_classes():
    cobertura = make_cobertura()

    expected_lines = {
        'Main': [10, 16, 17, 18, 19, 23, 25, 26, 28, 29, 30],
        'search.BinarySearch': [12, 16, 18, 20, 21, 23, 25, 26, 28, 29, 31],
        'search.ISortedArraySearch': [],
        'search.LinearSearch': [9, 13, 15, 16, 17],
    }

    for class_name in cobertura.classes():
        assert cobertura.line_hits(class_name) == expected_lines[class_name]


def test_line_misses():
    cobertura = make_cobertura()

    expected_lines = {
        'Main': [],
        'search.BinarySearch': [24],
        'search.ISortedArraySearch': [],
        'search.LinearSearch': [19, 24],
    }

    for class_name in cobertura.classes():
        assert cobertura.missed_lines(class_name) == expected_lines[class_name]


def test_total_lines():
    cobertura = make_cobertura()
    expected_total_lines = {
        'Main': 11,
        'search.BinarySearch': 12,
        'search.ISortedArraySearch': 0,
        'search.LinearSearch': 7,
    }
    for class_name in cobertura.classes():
        assert cobertura.total_lines(class_name) == \
            expected_total_lines[class_name]


def test_total_misses():
    cobertura = make_cobertura()
    expected_total_misses = {
        'Main': 0,
        'search.BinarySearch': 1,
        'search.ISortedArraySearch': 0,
        'search.LinearSearch': 2,
    }
    for class_name in cobertura.classes():
        assert cobertura.total_misses(class_name) == \
            expected_total_misses[class_name]


def test_total_hits():
    cobertura = make_cobertura()
    expected_total_misses = {
        'Main': 11,
        'search.BinarySearch': 11,
        'search.ISortedArraySearch': 0,
        'search.LinearSearch': 5,
    }
    for class_name in cobertura.classes():
        assert cobertura.total_hits(class_name) == \
            expected_total_misses[class_name]
