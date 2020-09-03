import mock
import pytest
import lxml.etree as ET

from .utils import make_cobertura


def test_parse_path():
    from pycobertura import Cobertura

    xml_path = 'tests/cobertura.xml'
    with mock.patch('pycobertura.cobertura.ET.parse') as mock_parse:
        cobertura = Cobertura(xml_path)

    assert cobertura.xml is mock_parse.return_value.getroot.return_value


def test_parse_file_object():
    from pycobertura import Cobertura

    xml_path = 'tests/cobertura.xml'
    with mock.patch('pycobertura.cobertura.ET.parse') as mock_parse:
        cobertura = Cobertura(open(xml_path))

    assert cobertura.xml is mock_parse.return_value.getroot.return_value


def test_parse_string():
    from pycobertura import Cobertura

    xml_path = 'tests/cobertura.xml'
    with open(xml_path) as f:
        xml_string = f.read()
    assert ET.tostring(Cobertura(xml_path).xml) == ET.tostring(Cobertura(xml_string).xml)


def test_invalid_coverage_report():
    from pycobertura import Cobertura

    xml_path = 'non-existent.xml'
    pytest.raises(Cobertura.InvalidCoverageReport, Cobertura, xml_path)


def test_version():
    cobertura = make_cobertura()
    assert cobertura.version == '1.9'


def test_line_rate():
    cobertura = make_cobertura()
    assert cobertura.line_rate() == 0.9


def test_line_rate_by_class_file():
    cobertura = make_cobertura()
    expected_line_rates = {
        'Main.java': 1.0,
        'search/BinarySearch.java': 0.9166666666666666,
        'search/ISortedArraySearch.java': 1.0,
        'search/LinearSearch.java': 0.7142857142857143,
    }

    for filename in cobertura.files():
        assert cobertura.line_rate(filename) == \
            expected_line_rates[filename]


def test_branch_rate():
    cobertura = make_cobertura()
    assert cobertura.branch_rate() == 0.75


def test_branch_rate_by_class_file():
    cobertura = make_cobertura()
    expected_branch_rates = {
        'Main.java': 1.0,
        'search/BinarySearch.java': 0.8333333333333334,
        'search/ISortedArraySearch.java': 1.0,
        'search/LinearSearch.java': 0.6666666666666666,
    }

    for filename in cobertura.files():
        assert cobertura.branch_rate(filename) == \
            expected_branch_rates[filename]


def test_missed_statements_by_class_file():
    cobertura = make_cobertura()
    expected_missed_statements = {
        'Main.java': [],
        'search/BinarySearch.java': [24],
        'search/ISortedArraySearch.java': [],
        'search/LinearSearch.java': [19, 24],
    }

    for filename in cobertura.files():
        assert cobertura.missed_statements(filename) == \
            expected_missed_statements[filename]


def test_list_packages():
    cobertura = make_cobertura()

    packages = cobertura.packages()
    assert packages == ['', 'search']


@pytest.mark.parametrize("report, expected", [
    ('tests/cobertura-generated-by-istanbul-from-coffeescript.xml', [
        'app.coffee'
    ]),
    ('tests/cobertura.xml', [
        'Main.java',
        'search/BinarySearch.java',
        'search/ISortedArraySearch.java',
        'search/LinearSearch.java'
    ])
])
def test_list_classes(report, expected):
    cobertura = make_cobertura(xml=report)

    classes = cobertura.files()
    assert classes == expected


def test_hit_lines__by_iterating_over_classes():
    cobertura = make_cobertura()

    expected_lines = {
        'Main.java': [10, 16, 17, 18, 19, 23, 25, 26, 28, 29, 30],
        'search/BinarySearch.java': [12, 16, 18, 20, 21, 23, 25, 26, 28, 29, 31],
        'search/ISortedArraySearch.java': [],
        'search/LinearSearch.java': [9, 13, 15, 16, 17],
    }

    for filename in cobertura.files():
        assert cobertura.hit_statements(filename) == expected_lines[filename]


def test_missed_lines():
    cobertura = make_cobertura()

    expected_lines = {
        'Main.java': [],
        'search/BinarySearch.java': [24],
        'search/ISortedArraySearch.java': [],
        'search/LinearSearch.java': [19, 20, 21, 22, 23, 24],
    }

    for filename in cobertura.files():
        assert cobertura.missed_lines(filename) == expected_lines[filename]


def test_total_statements():
    cobertura = make_cobertura()
    assert cobertura.total_statements() == 30


def test_total_statements_by_class_file():
    cobertura = make_cobertura()
    expected_total_statements = {
        'Main.java': 11,
        'search/BinarySearch.java': 12,
        'search/ISortedArraySearch.java': 0,
        'search/LinearSearch.java': 7,
    }
    for filename in cobertura.files():
        assert cobertura.total_statements(filename) == \
            expected_total_statements[filename]


def test_total_misses():
    cobertura = make_cobertura()
    assert cobertura.total_misses() == 3


def test_total_misses_by_class_file():
    cobertura = make_cobertura()
    expected_total_misses = {
        'Main.java': 0,
        'search/BinarySearch.java': 1,
        'search/ISortedArraySearch.java': 0,
        'search/LinearSearch.java': 2,
    }
    for filename in cobertura.files():
        assert cobertura.total_misses(filename) == \
            expected_total_misses[filename]


def test_total_hits():
    cobertura = make_cobertura()
    assert cobertura.total_hits() == 27


def test_total_hits_by_class_file():
    cobertura = make_cobertura()
    expected_total_misses = {
        'Main.java': 11,
        'search/BinarySearch.java': 11,
        'search/ISortedArraySearch.java': 0,
        'search/LinearSearch.java': 5,
    }
    for filename in cobertura.files():
        assert cobertura.total_hits(filename) == \
            expected_total_misses[filename]


def test_class_file_source__sources_not_found():
    from pycobertura.cobertura import Line
    cobertura = make_cobertura()
    expected_sources = {
        'Main.java': [Line(0, 'tests/Main.java not found', None, None)],
        'search/BinarySearch.java': [Line(0, 'tests/search/BinarySearch.java not found', None, None)],
        'search/ISortedArraySearch.java': [Line(0, 'tests/search/ISortedArraySearch.java not found', None, None)],
        'search/LinearSearch.java': [Line(0, 'tests/search/LinearSearch.java not found', None, None)],
    }
    for filename in cobertura.files():
        assert cobertura.file_source(filename) == expected_sources[filename]


def test_line_statuses():
    cobertura = make_cobertura('tests/dummy.source1/coverage.xml')
    expected_line_statuses = {
        'dummy/__init__.py': [],
        'dummy/dummy.py': [
            (1, True),
            (2, True),
            (4, True),
            (5, False),
            (6, False),
        ],
        'dummy/dummy2.py': [
            (1, True),
            (2, True),
        ],
        'dummy/dummy4.py': [
            (1, False),
            (2, False),
            (4, False),
            (5, False),
            (6, False)
        ],
    }
    for filename in cobertura.files():
        assert cobertura.line_statuses(filename) == \
            expected_line_statuses[filename]


@pytest.mark.parametrize("report, source, source_prefix", [
    ("tests/dummy.source1/coverage.xml", None, None),
    ("tests/dummy.source1/coverage.xml", "tests/", "dummy.source1/"),
])
def test_class_file_source__sources_found(report, source, source_prefix):
    from pycobertura.cobertura import Line
    cobertura = make_cobertura(report, source=source, source_prefix=source_prefix)
    expected_sources = {
    'dummy/__init__.py': [],
        'dummy/dummy.py': [
            Line(1, 'def foo():\n', True, None),
            Line(2, '    pass\n', True, None),
            Line(3, '\n', None, None),
            Line(4, 'def bar():\n', True, None),
            Line(5, "    a = 'a'\n", False, None),
            Line(6, "    b = 'b'\n", False, None),
        ],
        'dummy/dummy2.py': [
            Line(1, 'def baz():\n', True, None),
            Line(2, '    pass\n', True, None)
        ],
        'dummy/dummy4.py': [
            Line(1, 'def barbaz():\n', False, None),
            Line(2, '    pass\n', False, None),
            Line(3, '\n', None, None),
            Line(4, 'def foobarbaz():\n', False, None),
            Line(5, '    a = 1 + 3\n', False, None),
            Line(6, '    pass\n', False, None)
        ],
    }
    for filename in cobertura.files():
        assert cobertura.file_source(filename) == \
               expected_sources[filename]


def test_class_file_source__raises_when_no_filesystem():
    from pycobertura.cobertura import Cobertura
    cobertura = Cobertura('tests/cobertura.xml')
    for filename in cobertura.files():
        pytest.raises(
            Cobertura.MissingFileSystem,
            cobertura.file_source,
            filename
        )

def test_class_source_lines__raises_when_no_filesystem():
    from pycobertura.cobertura import Cobertura
    cobertura = Cobertura('tests/cobertura.xml')
    for filename in cobertura.files():
        pytest.raises(
            Cobertura.MissingFileSystem,
            cobertura.source_lines,
            filename
        )
