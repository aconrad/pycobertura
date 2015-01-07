from .utils import make_cobertura


def test_diff_class_source():
    from pycobertura.cobertura import CoberturaDiff

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura( 'tests/dummy.source2/coverage.xml')
    differ = CoberturaDiff(cobertura1, cobertura2)

    expected_sources = {
        'dummy/__init__': [],
        'dummy/dummy': [
            (1, 'def foo():\n', None),
            (2, '    pass\n', None),
            (3, '\n', None),
            (4, 'def bar():\n', None),
            (5, "    a = 'a'\n", True),
            (6, "    d = 'd'\n", True)
        ],
        'dummy/dummy2': [
            (1, 'def baz():\n', None),
            (2, "    c = 'c'\n", True),
            (3, '\n', None),
            (4, 'def bat():\n', True),
            (5, '    pass\n', False)
        ],
        'dummy/dummy3': [
            (1, 'def foobar():\n', False),
            (2, '    pass\n', False)
        ],
    }

    for class_name in cobertura2.classes():
        assert differ.class_source(class_name) == \
            expected_sources[class_name]


def test_diff_total_misses():
    from pycobertura.cobertura import CoberturaDiff

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')
    differ = CoberturaDiff(cobertura1, cobertura2)

    expected_sources = {
        'dummy/__init__': 0,
        'dummy/dummy': -2,
        'dummy/dummy2': 1,
        'dummy/dummy3': 2,
    }

    assert differ.diff_total_misses() == -4


def test_diff_total_misses_by_class():
    from pycobertura.cobertura import CoberturaDiff

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')
    differ = CoberturaDiff(cobertura1, cobertura2)

    expected_sources = {
        'dummy/__init__': 0,
        'dummy/dummy': -2,
        'dummy/dummy2': 1,
        'dummy/dummy3': 2,
    }

    for class_name in cobertura2.classes():
        assert differ.diff_total_misses(class_name) == \
            expected_sources[class_name]


def test_diff_line_rate():
    from pycobertura.cobertura import CoberturaDiff

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')
    differ = CoberturaDiff(cobertura1, cobertura2)

    assert differ.diff_line_rate() == 0.31059999999999993


def test_diff_line_rate_by_class():
    from pycobertura.cobertura import CoberturaDiff

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')
    differ = CoberturaDiff(cobertura1, cobertura2)

    expected_sources = {
        'dummy/__init__': 0,
        'dummy/dummy': 0.4,
        'dummy/dummy2': -0.25,
        'dummy/dummy3': 0.0,
    }

    for class_name in cobertura2.classes():
        assert differ.diff_line_rate(class_name) == \
            expected_sources[class_name]


def test_diff_total_hits():
    from pycobertura.cobertura import CoberturaDiff

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')
    differ = CoberturaDiff(cobertura1, cobertura2)

    assert differ.diff_total_hits() == 3


def test_diff_total_hits_by_class():
    from pycobertura.cobertura import CoberturaDiff

    cobertura1 = make_cobertura('tests/dummy.source1/coverage.xml')
    cobertura2 = make_cobertura('tests/dummy.source2/coverage.xml')
    differ = CoberturaDiff(cobertura1, cobertura2)

    expected_total_hits = {
        'dummy/__init__': 0,
        'dummy/dummy': 2,
        'dummy/dummy2': 1,
        'dummy/dummy3': 0,
    }

    for class_name in cobertura2.classes():
        assert differ.diff_total_hits(class_name) == \
            expected_total_hits[class_name]
