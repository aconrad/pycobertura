from .utils import make_cobertura


def test_diff_class_source():
    from pycobertura.cobertura import CoberturaDiff
    from pycobertura.cobertura import Line

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')
    differ = CoberturaDiff(cobertura1, cobertura2)

    expected_sources = {
        'dummy/__init__.py': [],
        'dummy/dummy.py': [
            Line(1, u'def foo():\n', None, None),
            Line(2, u'    pass\n', None, None),
            Line(3, u'\n', None, None),
            Line(4, u'def bar():\n', None, None),
            Line(5, u"    a = 'a'\n", True, 'cov-up'),
            Line(6, u"    d = 'd'\n", True, 'line-edit')
        ],
        'dummy/dummy2.py': [
            Line(1, u'def baz():\n', None, None),
            Line(2, u"    c = 'c'\n", True, 'line-edit'),
            Line(3, u'\n', None, 'line-edit'),
            Line(4, u'def bat():\n', True, 'line-edit'),
            Line(5, u'    pass\n', False, 'cov-down')
        ],
        'dummy/dummy3.py': [
            Line(1, u'def foobar():\n', False, 'line-edit'),
            Line(2, u'    pass  # This is a very long comment that was purposefully written so we could test how HTML rendering looks like when the boundaries of the page are reached. And here is a non-ascii char: \u015e\n', False, 'line-edit')
        ],
    }

    for filename in cobertura2.files():
        assert differ.file_source(filename) == \
               expected_sources[filename]


def test_diff_total_misses():
    from pycobertura.cobertura import CoberturaDiff

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')
    differ = CoberturaDiff(cobertura1, cobertura2)

    assert differ.diff_total_misses() == 1


def test_diff_total_misses_by_class_file():
    from pycobertura.cobertura import CoberturaDiff

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')
    differ = CoberturaDiff(cobertura1, cobertura2)

    expected_sources = {
        'dummy/__init__.py': 0,
        'dummy/dummy.py': -2,
        'dummy/dummy2.py': 1,
        'dummy/dummy3.py': 2,
    }

    for filename in cobertura2.files():
        assert differ.diff_total_misses(filename) == \
            expected_sources[filename]


def test_diff_line_rate():
    from pycobertura.cobertura import CoberturaDiff

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')
    differ = CoberturaDiff(cobertura1, cobertura2)

    assert differ.diff_line_rate() == 0.31059999999999993


def test_diff_line_rate_by_class_file():
    from pycobertura.cobertura import CoberturaDiff

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')
    differ = CoberturaDiff(cobertura1, cobertura2)

    expected_sources = {
        'dummy/__init__.py': 0,
        'dummy/dummy.py': 0.4,
        'dummy/dummy2.py': -0.25,
        'dummy/dummy3.py': 0.0,
    }

    for filename in cobertura2.files():
        assert differ.diff_line_rate(filename) == \
            expected_sources[filename]


def test_diff_same_report_different_source_dirs():
    from pycobertura.cobertura import CoberturaDiff

    cobertura1 = make_cobertura('tests/dummy.uncovered.addcode/coverage.xml', source='tests/dummy.uncovered/dummy/')
    cobertura2 = make_cobertura('tests/dummy.uncovered.addcode/coverage.xml', source='tests/dummy.uncovered.addcode/dummy/')
    differ = CoberturaDiff(cobertura1, cobertura2)

    assert differ.diff_missed_lines('dummy.py') == [(2, False), (3, True)]


def test_diff_total_hits():
    from pycobertura.cobertura import CoberturaDiff

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')
    differ = CoberturaDiff(cobertura1, cobertura2)

    assert differ.diff_total_hits() == 3


def test_diff_total_hits_by_class_file():
    from pycobertura.cobertura import CoberturaDiff

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')
    differ = CoberturaDiff(cobertura1, cobertura2)

    expected_total_hits = {
        'dummy/__init__.py': 0,
        'dummy/dummy.py': 2,
        'dummy/dummy2.py': 1,
        'dummy/dummy3.py': 0,
    }

    for filename in cobertura2.files():
        assert differ.diff_total_hits(filename) == \
            expected_total_hits[filename]


def test_diff__has_all_changes_covered__some_changed_code_is_still_uncovered():
    from pycobertura.cobertura import Cobertura, CoberturaDiff

    cobertura1 = make_cobertura('tests/dummy.zeroexit1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.zeroexit2/coverage.xml')

    differ = CoberturaDiff(cobertura1, cobertura2)
    assert differ.has_all_changes_covered() is False


def test_diff__has_better_coverage():
    from pycobertura.cobertura import Cobertura, CoberturaDiff

    cobertura1 = Cobertura('tests/dummy.zeroexit1/coverage.xml')
    cobertura2 = Cobertura('tests/dummy.zeroexit2/coverage.xml')
    differ = CoberturaDiff(cobertura1, cobertura2)
    assert differ.has_better_coverage() is True


def test_diff__has_not_better_coverage():
    from pycobertura.cobertura import Cobertura, CoberturaDiff

    cobertura1 = Cobertura('tests/dummy.zeroexit2/coverage.xml')
    cobertura2 = Cobertura('tests/dummy.zeroexit1/coverage.xml')
    differ = CoberturaDiff(cobertura1, cobertura2)
    assert differ.has_better_coverage() is False
