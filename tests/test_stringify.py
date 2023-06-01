import pytest


@pytest.mark.parametrize(
    "input, expected_output",
    [
        ([], ""),
        ([(1, "miss"), (2, "miss")], "1-2"),
        ([(1, "miss"), (2, "partial")], "1, ~2"),
        ([(1, "miss"), (2, "miss"), (3, "miss")], "1-3"),
        ([(1, "miss"), (2, "partial"), (3, "miss")], "1, ~2, 3"),
        ([(1, "miss"), (2, "partial"), (3, "partial")], "1, ~2-3"),
        ([(1, "miss"), (2, "partial"), (3, "partial"), (4, "miss")], "1, ~2-3, 4"),
        ([(1, "miss"), (2, "miss"), (3, "partial"), (4, "partial")], "1-2, ~3-4"),
        ([(1, "partial"), (2, "partial"), (3, "miss"), (4, "miss")], "~1-2, 3-4"),
        ([(1, "miss"), (2, "miss"), (3, "miss"), (7, "miss")], "1-3, 7"),
        ([(1, "miss"), (2, "miss"), (3, "miss"), (7, "miss"), (8, "miss")], "1-3, 7-8"),
        ([(1, "miss"), (2, "miss"), (3, "miss"), (7, "miss"), (8, "miss"), (9, "miss")], "1-3, 7-9"),
        ([(1, "miss"), (7, "miss"), (8, "miss"), (9, "miss")], "1, 7-9"),
        ([(1, "miss"), (2, "miss"), (7, "miss"), (8, "miss"), (9, "miss")], "1-2, 7-9"),
        ([(1, "miss"), (7, "miss")], "1, 7"),
    ],
)
def test_stringify_func(input, expected_output):
    from pycobertura.utils import stringify

    assert stringify(input) == expected_output
