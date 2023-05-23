import pytest


@pytest.mark.parametrize(
    "numbered_list, expected_output",
    [
        ([1], [(1, 1)]),
        ([1, 2], [(1, 2)]),
        ([1, 2, 3], [(1, 3)]),
        ([1, 2, 3, 7], [(1, 3), (7, 7)]),
        ([1, 2, 3, 7, 8], [(1, 3), (7, 8)]),
        ([1, 2, 3, 7, 8, 9], [(1, 3), (7, 9)]),
        ([1, 7, 8, 9], [(1, 1), (7, 9)]),
        ([1, 2, 7, 8, 9], [(1, 2), (7, 9)]),
        ([1, 7], [(1, 1), (7, 7)]),
        ([1, 2, 3, 5, 7, 8, 10, 11, 12, 15], [(1, 3), (5, 5), (7, 8), (10, 12), (15, 15)])
    ],
)
def test_rangify(numbered_list, expected_output):
    from pycobertura.utils import rangify

    assert rangify(numbered_list) == expected_output


@pytest.mark.parametrize(
    "line_statuses, expected_output",
    [
        ([(1, "hit")], [(1, 1, "hit")]),
        ([(1, "hit"), (2, "hit")], [(1, 2, "hit")]),
        ([(1, "hit"), (2, "hit"), (3, "hit")], [(1, 3, "hit")]),
        ([(1, "hit"), (3, "hit")], [(1, 1, "hit"), (3, 3, "hit")]),
        ([(1, "hit"), (2, "hit"), (3, "miss"), (4, "hit")], [(1, 2, "hit"), (3, 3, "miss"), (4, 4, "hit")]),
        ([(1, "hit"), (2, "partial"), (3, "miss"), (4, "hit")], [(1, 1, "hit"), (2, 2, "partial"), (3, 3, "miss"), (4, 4, "hit")]),
    ],
)
def test_rangify_by_status(line_statuses, expected_output):
    from pycobertura.utils import rangify_by_status

    assert rangify_by_status(line_statuses) == expected_output
