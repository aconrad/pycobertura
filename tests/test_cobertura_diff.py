from .utils import make_cobertura


def test_diff_class_source():
    from pycobertura.cobertura import CoberturaDiff

    cobertura1 = make_cobertura(
        'tests/dummy.source1.xml',
        base_path='tests/dummy.source1/'
    )
    cobertura2 = make_cobertura(
        'tests/dummy.source2.xml',
        base_path='tests/dummy.source2/'
    )
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
    }
    for class_name in cobertura2.classes():
        assert differ.class_source(class_name) == \
            expected_sources[class_name]
