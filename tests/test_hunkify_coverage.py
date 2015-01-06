def test_hunkify_coverage__top():
    from pycobertura.utils import hunkify_lines
    lines = [
        (1, 'a', True),
        (2, 'b', True),
        (3, 'c', None),
        (4, 'd', None),
        (5, 'e', None),
        (6, 'f', None),
        (7, 'g', None),
    ]

    hunks = hunkify_lines(lines)

    assert hunks == [
        [
            (1, 'a', True),
            (2, 'b', True),
            (3, 'c', None),
            (4, 'd', None),
            (5, 'e', None),
        ],
    ]


def test_hunkify_coverage__bottom():
    from pycobertura.utils import hunkify_lines
    lines = [
        (1, 'a', None),
        (2, 'b', None),
        (3, 'c', None),
        (4, 'd', None),
        (5, 'e', None),
        (6, 'f', True),
        (7, 'g', True),
    ]

    hunks = hunkify_lines(lines)

    assert hunks == [
        [
            (3, 'c', None),
            (4, 'd', None),
            (5, 'e', None),
            (6, 'f', True),
            (7, 'g', True),
        ],
    ]


def test_hunkify_coverage__middle():
    from pycobertura.utils import hunkify_lines
    lines = [
        (1, 'a', None),
        (2, 'b', None),
        (3, 'c', None),
        (4, 'd', False),
        (5, 'e', False),
        (6, 'f', None),
        (7, 'g', None),
        (8, 'h', None),
    ]

    hunks = hunkify_lines(lines)

    assert hunks == [
        [
            (1, 'a', None),
            (2, 'b', None),
            (3, 'c', None),
            (4, 'd', False),
            (5, 'e', False),
            (6, 'f', None),
            (7, 'g', None),
            (8, 'h', None),
        ],
    ]


def test_hunkify_coverage__overlapping():
    from pycobertura.utils import hunkify_lines
    lines = [
        (1, 'a', None),
        (2, 'b', True),
        (3, 'c', True),
        (4, 'd', None),
        (5, 'e', None),
        (6, 'f', True),
        (7, 'g', True),
        (8, 'h', None),
    ]

    hunks = hunkify_lines(lines)

    assert hunks == [
        [
            (1, 'a', None),
            (2, 'b', True),
            (3, 'c', True),
            (4, 'd', None),
            (5, 'e', None),
            (6, 'f', True),
            (7, 'g', True),
            (8, 'h', None),
        ],
    ]


def test_hunkify_coverage__2_contiguous_hunks_w_full_context_makes_1_hunk():
    from pycobertura.utils import hunkify_lines
    lines = [
        (1, 'a', None),  # context 1
        (2, 'b', None),  # context 1
        (3, 'c', None),  # context 1
        (4, 'd', True),
        (5, 'e', None),  # context 1
        (6, 'f', None),  # context 1
        (7, 'g', None),  # context 1
        (8, 'h', None),  # context 2
        (9, 'i', None),  # context 2
        (10, 'j', None),  # context 2
        (11, 'k', False),
        (12, 'l', None),  # context 2
        (13, 'm', None),  # context 2
        (14, 'n', None),  # context 2
    ]

    hunks = hunkify_lines(lines)

    assert hunks == [
        [
            (1, 'a', None),
            (2, 'b', None),
            (3, 'c', None),
            (4, 'd', True),
            (5, 'e', None),
            (6, 'f', None),
            (7, 'g', None),
            (8, 'h', None),
            (9, 'i', None),
            (10, 'j', None),
            (11, 'k', False),
            (12, 'l', None),
            (13, 'm', None),
            (14, 'n', None),
        ],
    ]


def test_hunkify_coverage__2_distant_hunks_w_full_context_makes_2_hunk():
    from pycobertura.utils import hunkify_lines
    lines = [
        (1, 'a', None),  # context 1
        (2, 'b', None),  # context 1
        (3, 'c', None),  # context 1
        (4, 'd', True),
        (5, 'e', None),  # context 1
        (6, 'f', None),  # context 1
        (7, 'g', None),  # context 1
        (8, 'h', None),
        (9, 'i', None),  # context 2
        (10, 'j', None),  # context 2
        (11, 'k', None),  # context 2
        (12, 'l', False),
        (13, 'm', None),  # context 2
        (14, 'n', None),  # context 2
        (15, 'o', None),  # context 2
    ]

    hunks = hunkify_lines(lines)

    assert hunks == [
        [
            (1, 'a', None),
            (2, 'b', None),
            (3, 'c', None),
            (4, 'd', True),
            (5, 'e', None),
            (6, 'f', None),
            (7, 'g', None),
        ], [
            (9, 'i', None),
            (10, 'j', None),
            (11, 'k', None),
            (12, 'l', False),
            (13, 'm', None),
            (14, 'n', None),
            (15, 'o', None),
        ],
    ]


def test_hunkify_coverage__no_valid_hunks_found():
    from pycobertura.utils import hunkify_lines
    lines = [
        (1, 'a', None),
        (2, 'b', None),
        (3, 'c', None),
        (4, 'd', None),
        (5, 'e', None),
        (6, 'f', None),
        (7, 'g', None),
        (8, 'h', None),
        (9, 'i', None),
    ]

    hunks = hunkify_lines(lines)

    assert hunks == []
