def test_stringify_func__empty_bracket():
    from pycobertura.utils import stringify

    assert stringify([]) == ''


def test_stringify_func__1_2():
    from pycobertura.utils import stringify

    assert stringify([1, 2]) == '1-2'


def test_stringify_func__1_2_3():
    from pycobertura.utils import stringify

    assert stringify([1, 2, 3]) == '1-3'


def test_stringify_func__1_2_3_and_7():
    from pycobertura.utils import stringify

    assert stringify([1, 2, 3, 7]) == '1-3, 7'


def test_stringify_func__1_2_3_and_7_8():
    from pycobertura.utils import stringify

    assert stringify([1, 2, 3, 7, 8]) == '1-3, 7-8'


def test_stringify_func__1_2_3_and_7_8_9():
    from pycobertura.utils import stringify

    assert stringify([1, 2, 3, 7, 8, 9]) == '1-3, 7-9'


def test_stringify_func__1_and_7_8_9():
    from pycobertura.utils import stringify

    assert stringify([1, 7, 8, 9]) == '1, 7-9'


def test_stringify_func__1_2_and_7_8_9():
    from pycobertura.utils import stringify

    assert stringify([1, 2, 7, 8, 9]) == '1-2, 7-9'


def test_stringify_func__1_and_7():
    from pycobertura.utils import stringify

    assert stringify([1, 7]) == '1, 7'
