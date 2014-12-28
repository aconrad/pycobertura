def test_reconcile_lines__identical():
    from pycobertura.utils import reconcile_lines

    lines1 = [
        'hello',  # 1
        'world',  # 2
    ]

    lines2 = [
        'hello',  # 1
        'world',  # 2
    ]

    assert reconcile_lines(lines1, lines2) == {1: 1, 2: 2}


def test_reconcile_lines__less_to_more():
    from pycobertura.utils import reconcile_lines

    lines1 = [
        'hello',  # 1
        'world',  # 2
    ]
    lines2 = [
        'dear all',   # 1
        'hello',      # 2
        'beautiful',  # 3
        'world',      # 4
        'of',         # 5
        'pain',       # 6
    ]

    assert reconcile_lines(lines1, lines2) == {1: 2, 2: 4}


def test_reconcile_lines__more_to_less():
    from pycobertura.utils import reconcile_lines

    lines1 = [
        'dear all',   # 1
        'hello',      # 2
        'beautiful',  # 3
        'world',      # 4
        'of',         # 5
        'pain',       # 6
    ]

    lines2 = [
        'hello',  # 1
        'world',  # 2
    ]

    assert reconcile_lines(lines1, lines2) == {2: 1, 4: 2}
