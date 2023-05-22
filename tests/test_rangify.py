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
    ],
)
def test_rangify(numbered_list, expected_output):
    from pycobertura.utils import rangify

    assert rangify(numbered_list) == expected_output
