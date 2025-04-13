import pytest


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
