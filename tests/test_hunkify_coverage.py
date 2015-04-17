def test_hunkify_coverage__top():
    from pycobertura.utils import hunkify_lines
    from pycobertura.cobertura import Line

    lines = [
        Line(1, 'a', True, None),
        Line(2, 'b', True, None),
        Line(3, 'c', None, None),
        Line(4, 'd', None, None),
        Line(5, 'e', None, None),
        Line(6, 'f', None, None),
        Line(7, 'g', None, None),
    ]

    hunks = hunkify_lines(lines)

    assert hunks == [
        [
            Line(1, 'a', True, None),
            Line(2, 'b', True, None),
            Line(3, 'c', None, None),
            Line(4, 'd', None, None),
            Line(5, 'e', None, None),
        ],
    ]


def test_hunkify_coverage__bottom():
    from pycobertura.utils import hunkify_lines
    from pycobertura.cobertura import Line

    lines = [
        Line(1, 'a', None, None),
        Line(2, 'b', None, None),
        Line(3, 'c', None, None),
        Line(4, 'd', None, None),
        Line(5, 'e', None, None),
        Line(6, 'f', True, None),
        Line(7, 'g', True, None),
    ]

    hunks = hunkify_lines(lines)

    assert hunks == [
        [
            Line(3, 'c', None, None),
            Line(4, 'd', None, None),
            Line(5, 'e', None, None),
            Line(6, 'f', True, None),
            Line(7, 'g', True, None),
        ],
    ]


def test_hunkify_coverage__middle():
    from pycobertura.utils import hunkify_lines
    from pycobertura.cobertura import Line

    lines = [
        Line(1, 'a', None, None),
        Line(2, 'b', None, None),
        Line(3, 'c', None, None),
        Line(4, 'd', False, None),
        Line(5, 'e', False, None),
        Line(6, 'f', None, None),
        Line(7, 'g', None, None),
        Line(8, 'h', None, None),
    ]

    hunks = hunkify_lines(lines)

    assert hunks == [
        [
            Line(1, 'a', None, None),
            Line(2, 'b', None, None),
            Line(3, 'c', None, None),
            Line(4, 'd', False, None),
            Line(5, 'e', False, None),
            Line(6, 'f', None, None),
            Line(7, 'g', None, None),
            Line(8, 'h', None, None),
        ],
    ]


def test_hunkify_coverage__overlapping():
    from pycobertura.utils import hunkify_lines
    from pycobertura.cobertura import Line

    lines = [
        Line(1, 'a', None, None),
        Line(2, 'b', True, None),
        Line(3, 'c', True, None),
        Line(4, 'd', None, None),
        Line(5, 'e', None, None),
        Line(6, 'f', True, None),
        Line(7, 'g', True, None),
        Line(8, 'h', None, None),
    ]

    hunks = hunkify_lines(lines)

    assert hunks == [
        [
            Line(1, 'a', None, None),
            Line(2, 'b', True, None),
            Line(3, 'c', True, None),
            Line(4, 'd', None, None),
            Line(5, 'e', None, None),
            Line(6, 'f', True, None),
            Line(7, 'g', True, None),
            Line(8, 'h', None, None),
        ],
    ]


def test_hunkify_coverage__2_contiguous_hunks_w_full_context_makes_1_hunk():
    from pycobertura.utils import hunkify_lines
    from pycobertura.cobertura import Line

    lines = [
        Line(1, 'a', None, None),  # context 1
        Line(2, 'b', None, None),  # context 1
        Line(3, 'c', None, None),  # context 1
        Line(4, 'd', True, None),
        Line(5, 'e', None, None),  # context 1
        Line(6, 'f', None, None),  # context 1
        Line(7, 'g', None, None),  # context 1
        Line(8, 'h', None, None),  # context 2
        Line(9, 'i', None, None),  # context 2
        Line(10, 'j', None, None),  # context 2
        Line(11, 'k', False, None),
        Line(12, 'l', None, None),  # context 2
        Line(13, 'm', None, None),  # context 2
        Line(14, 'n', None, None),  # context 2
    ]

    hunks = hunkify_lines(lines)

    assert hunks == [
        [
            Line(1, 'a', None, None),
            Line(2, 'b', None, None),
            Line(3, 'c', None, None),
            Line(4, 'd', True, None),
            Line(5, 'e', None, None),
            Line(6, 'f', None, None),
            Line(7, 'g', None, None),
            Line(8, 'h', None, None),
            Line(9, 'i', None, None),
            Line(10, 'j', None, None),
            Line(11, 'k', False, None),
            Line(12, 'l', None, None),
            Line(13, 'm', None, None),
            Line(14, 'n', None, None),
        ],
    ]


def test_hunkify_coverage__2_distant_hunks_w_full_context_makes_2_hunk():
    from pycobertura.utils import hunkify_lines
    from pycobertura.cobertura import Line

    lines = [
        Line(1, 'a', None, None),  # context 1
        Line(2, 'b', None, None),  # context 1
        Line(3, 'c', None, None),  # context 1
        Line(4, 'd', True, None),
        Line(5, 'e', None, None),  # context 1
        Line(6, 'f', None, None),  # context 1
        Line(7, 'g', None, None),  # context 1
        Line(8, 'h', None, None),
        Line(9, 'i', None, None),  # context 2
        Line(10, 'j', None, None),  # context 2
        Line(11, 'k', None, None),  # context 2
        Line(12, 'l', False, None),
        Line(13, 'm', None, None),  # context 2
        Line(14, 'n', None, None),  # context 2
        Line(15, 'o', None, None),  # context 2
    ]

    hunks = hunkify_lines(lines)

    assert hunks == [
        [
            Line(1, 'a', None, None),
            Line(2, 'b', None, None),
            Line(3, 'c', None, None),
            Line(4, 'd', True, None),
            Line(5, 'e', None, None),
            Line(6, 'f', None, None),
            Line(7, 'g', None, None),
        ], [
            Line(9, 'i', None, None),
            Line(10, 'j', None, None),
            Line(11, 'k', None, None),
            Line(12, 'l', False, None),
            Line(13, 'm', None, None),
            Line(14, 'n', None, None),
            Line(15, 'o', None, None),
        ],
    ]


def test_hunkify_coverage__no_valid_hunks_found():
    from pycobertura.utils import hunkify_lines
    from pycobertura.cobertura import Line

    lines = [
        Line(1, 'a', None, None),
        Line(2, 'b', None, None),
        Line(3, 'c', None, None),
        Line(4, 'd', None, None),
        Line(5, 'e', None, None),
        Line(6, 'f', None, None),
        Line(7, 'g', None, None),
        Line(8, 'h', None, None),
        Line(9, 'i', None, None),
    ]

    hunks = hunkify_lines(lines)

    assert hunks == []
