import mock
import lxml.etree as ET

from .utils import make_cobertura


def test_parse_string():
    from pycobertura import Cobertura

    with open('tests/cobertura.xml') as f:
        xml = f.read()

    cobertura = Cobertura(xml)
    assert isinstance(cobertura.xml, ET._Element)


def test_parse_fileobj():
    from pycobertura import Cobertura

    with open('tests/cobertura.xml') as f:
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


def test_total_misses():
    cobertura = make_cobertura()
    assert cobertura.total_misses() == 3


def test_missed_statements_by_class_name():
    cobertura = make_cobertura()
    expected_missed_statements = {
        'Main': [],
        'search.BinarySearch': [24],
        'search.ISortedArraySearch': [],
        'search.LinearSearch': [19, 24],
    }

    for class_name in cobertura.classes():
        assert cobertura.missed_statements(class_name) == \
            expected_missed_statements[class_name]


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


def test_hit_lines__by_iterating_over_classes():
    cobertura = make_cobertura()

    expected_lines = {
        'Main': [10, 16, 17, 18, 19, 23, 25, 26, 28, 29, 30],
        'search.BinarySearch': [12, 16, 18, 20, 21, 23, 25, 26, 28, 29, 31],
        'search.ISortedArraySearch': [],
        'search.LinearSearch': [9, 13, 15, 16, 17],
    }

    for class_name in cobertura.classes():
        assert cobertura.hit_statements(class_name) == expected_lines[class_name]


def test_missed_lines():
    cobertura = make_cobertura()

    expected_lines = {
        'Main': [],
        'search.BinarySearch': [24],
        'search.ISortedArraySearch': [],
        'search.LinearSearch': [19, 24],
    }

    for class_name in cobertura.classes():
        assert cobertura.missed_lines(class_name) == expected_lines[class_name]


def test_total_statements():
    cobertura = make_cobertura()
    assert cobertura.total_statements() == 30


def test_total_statements_by_class():
    cobertura = make_cobertura()
    expected_total_statements = {
        'Main': 11,
        'search.BinarySearch': 12,
        'search.ISortedArraySearch': 0,
        'search.LinearSearch': 7,
    }
    for class_name in cobertura.classes():
        assert cobertura.total_statements(class_name) == \
            expected_total_statements[class_name]


def test_total_misses():
    cobertura = make_cobertura()
    assert cobertura.total_misses() == 3


def test_total_misses_by_class():
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


def test_filename():
    cobertura = make_cobertura()
    expected_filenames = {
        'Main': 'Main.java',
        'search.BinarySearch': 'search/BinarySearch.java',
        'search.ISortedArraySearch': 'search/ISortedArraySearch.java',
        'search.LinearSearch': 'search/LinearSearch.java',
    }
    for class_name in cobertura.classes():
        assert cobertura.filename(class_name) == \
            expected_filenames[class_name]


def test_filename__with_base_path():
    base_path = 'foo/bar/baz'
    cobertura = make_cobertura(base_path=base_path)
    expected_filenames = {
        'Main': 'foo/bar/baz/Main.java',
        'search.BinarySearch': 'foo/bar/baz/search/BinarySearch.java',
        'search.ISortedArraySearch': 'foo/bar/baz/search/ISortedArraySearch.java',
        'search.LinearSearch': 'foo/bar/baz/search/LinearSearch.java',
    }
    for class_name in cobertura.classes():
        assert cobertura.filename(class_name) == \
            expected_filenames[class_name]


def test_class_source__sources_not_found():
    cobertura = make_cobertura('tests/dummy.source1.xml')
    expected_sources = {
        'dummy/__init__': [(0, 'dummy/__init__.py not found', None)],
        'dummy/dummy': [(0, 'dummy/dummy.py not found', None)],
        'dummy/dummy2': [(0, 'dummy/dummy2.py not found', None)],
    }
    for class_name in cobertura.classes():
        assert cobertura.class_source(class_name) == expected_sources[class_name]


def test_line_statuses():
    cobertura = make_cobertura(
        'tests/dummy.source1.xml',
        base_path='tests/dummy.source1/'
    )
    expected_line_statuses = {
        'dummy/__init__': [],
        'dummy/dummy': [
            (1, True),
            (2, True),
            (4, True),
            (5, False),
            (6, False),
        ],
        'dummy/dummy2': [
            (1, True),
            (2, True)
        ],
    }
    for class_name in cobertura.classes():
        assert cobertura.line_statuses(class_name) == \
            expected_line_statuses[class_name]


def test_class_source__sources_found():
    cobertura = make_cobertura(
        'tests/dummy.source1.xml',
        base_path='tests/dummy.source1/'
    )
    expected_sources = {
        'dummy/__init__': [],
        'dummy/dummy': [
            (1, 'def foo():\n', True),
            (2, '    pass\n', True),
            (3, '\n', None),
            (4, 'def bar():\n', True),
            (5, "    a = 'a'\n", False),
            (6, "    b = 'b'\n", False),
        ],
        'dummy/dummy2': [
            (1, 'def baz():\n', True),
            (2, '    pass\n', True)
        ],
    }
    for class_name in cobertura.classes():
        assert cobertura.class_source(class_name) == \
            expected_sources[class_name]
