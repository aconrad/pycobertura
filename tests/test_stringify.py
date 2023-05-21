import pytest


@pytest.mark.parametrize(
    "input, expected_output",
    [
        ([], ""),
        ([1, 2], "1-2"),
        ([1, 2, 3], "1-3"),
        ([1, 2, 3, 7], "1-3, 7"),
        ([1, 2, 3, 7, 8], "1-3, 7-8"),
        ([1, 2, 3, 7, 8, 9], "1-3, 7-9"),
        ([1, 7, 8, 9], "1, 7-9"),
        ([1, 2, 7, 8, 9], "1-2, 7-9"),
        ([1, 7], "1, 7"),
    ],
)
def test_stringify_func(input, expected_output):
    from pycobertura.utils import stringify

    assert stringify(input) == expected_output
