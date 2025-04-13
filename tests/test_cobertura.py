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


def test_no_branch_rate():
    from pycobertura import Cobertura

    assert Cobertura('tests/cobertura-no-branch-rate.xml').branch_rate() == None


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
        'search/BinarySearch.java': [23, 24],
        'search/ISortedArraySearch.java': [],
        'search/LinearSearch.java': [13, 17, 19, 24],
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
        'Main.java': [10, 16, 17, 18, 19, 23, 25, 26, 28, 29, 30, 31, 32, 33, 34],
        'search/BinarySearch.java': [12, 16, 18, 20, 21, 25, 26, 28, 29, 31],
        'search/ISortedArraySearch.java': [],
        'search/LinearSearch.java': [9, 15, 16],
    }

    for filename in cobertura.files():
        assert cobertura.hit_statements(filename) == expected_lines[filename]


def test_missed_lines():
    cobertura = make_cobertura()

    expected_lines = {
        'Main.java': [],
        'search/BinarySearch.java': [(23, 'partial'), (24, 'miss')],
        'search/ISortedArraySearch.java': [],
        'search/LinearSearch.java': [(13, "partial"), (17, "partial"), (19, "miss"), (20, "miss"), (21, "miss"), (22, "miss"), (23, "miss"), (24, "miss")],
    }

    for filename in cobertura.files():
        assert cobertura.missed_lines(filename) == expected_lines[filename]


def test_total_statements():
    cobertura = make_cobertura()
    assert cobertura.total_statements() == 34


def test_total_statements_by_class_file():
    cobertura = make_cobertura()
    expected_total_statements = {
        'Main.java': 15,
        'search/BinarySearch.java': 12,
        'search/ISortedArraySearch.java': 0,
        'search/LinearSearch.java': 7,
    }
    for filename in cobertura.files():
        assert cobertura.total_statements(filename) == \
            expected_total_statements[filename]


def test_total_misses():
    cobertura = make_cobertura()
    assert cobertura.total_misses() == 6


def test_total_misses_by_class_file():
    cobertura = make_cobertura()
    expected_total_misses = {
        'Main.java': 0,
        'search/BinarySearch.java': 2,
        'search/ISortedArraySearch.java': 0,
        'search/LinearSearch.java': 4,
    }
    for filename in cobertura.files():
        assert cobertura.total_misses(filename) == \
            expected_total_misses[filename]


def test_total_hits():
    cobertura = make_cobertura()
    assert cobertura.total_hits() == 28


def test_total_hits_by_class_file():
    cobertura = make_cobertura()
    expected_total_misses = {
        'Main.java': 15,
        'search/BinarySearch.java': 10,
        'search/ISortedArraySearch.java': 0,
        'search/LinearSearch.java': 3,
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


@pytest.mark.parametrize(
    "report, expected_line_statuses",
    [
        (
            "tests/dummy.source1/coverage.xml",
            {
                "dummy/__init__.py": [],
                "dummy/dummy.py": [
                    (1, "hit"),
                    (2, "hit"),
                    (4, "hit"),
                    (5, "miss"),
                    (6, "miss"),
                ],
                "dummy/dummy2.py": [
                    (1, "hit"),
                    (2, "hit"),
                ],
                "dummy/dummy4.py": [
                    (1, "miss"),
                    (2, "miss"),
                    (4, "miss"),
                    (5, "miss"),
                    (6, "miss"),
                ],
            },
        ),
        (
            "tests/cobertura.xml",
            {
                "Main.java": [
                    (10, "hit"),
                    (16, "hit"),
                    (17, "hit"),
                    (18, "hit"),
                    (19, "hit"),
                    (23, "hit"),
                    (25, "hit"),
                    (26, "hit"),
                    (28, "hit"),
                    (29, "hit"),
                    (30, "hit"),
                    (31, "hit"),
                    (32, "hit"),
                    (33, "hit"),
                    (34, "hit"),
                ],
                "search/BinarySearch.java": [
                    (12, "hit"),
                    (16, "hit"),
                    (18, "hit"),
                    (20, "hit"),
                    (21, "hit"),
                    (23, "partial"),
                    (24, "miss"),
                    (25, "hit"),
                    (26, "hit"),
                    (28, "hit"),
                    (29, "hit"),
                    (31, "hit"),
                ],
                "search/ISortedArraySearch.java": [],
                "search/LinearSearch.java": [(9, 'hit'), (13, 'partial'), (15, 'hit'), (16, 'hit'), (17, 'partial'), (19, 'miss'), (24, 'miss')],
            },
        ),
        (
            "tests/dummy.with-branch-condition/coverage.xml",
            {
                "__init__.py": [],
                "dummy.py": [(1, 'hit'), (2, 'partial'), (3, 'hit'), (5, 'miss')],
            },
        ),
    ],
)
def test_line_statuses(report, expected_line_statuses):
    cobertura = make_cobertura(report)
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
        "dummy/__init__.py": [],
        "dummy/dummy.py": [
            Line(1, "def foo():\n", "hit", None),
            Line(2, "    pass\n", "hit", None),
            Line(3, "\n", None, None),
            Line(4, "def bar():\n", "hit", None),
            Line(5, "    a = 'a'\n", "miss", None),
            Line(6, "    b = 'b'\n", "miss", None),
        ],
        "dummy/dummy2.py": [
            Line(1, "def baz():\n", "hit", None),
            Line(2, "    pass\n", "hit", None),
        ],
        "dummy/dummy4.py": [
            Line(1, "def barbaz():\n", "miss", None),
            Line(2, "    pass\n", "miss", None),
            Line(3, "\n", None, None),
            Line(4, "def foobarbaz():\n", "miss", None),
            Line(5, "    a = 1 + 3\n", "miss", None),
            Line(6, "    pass\n", "miss", None),
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
