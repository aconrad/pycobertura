from typing import Union
import pytest
from pycobertura.utils import calculate_line_rate, get_line_status


@pytest.mark.parametrize("total_statments, total_missing, expected_output", [
    (0, 0, 1),
    (100, 0, 1),
    (100, 1, 0.99),
    (100, 100, 0),
])
def test_calculate_line_rate(total_statments, total_missing, expected_output):
    assert calculate_line_rate(total_statments, total_missing) == expected_output
