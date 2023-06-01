from typing import Union
import pytest
from pycobertura.utils import get_line_status

class FakeLine:
    def __init__(self, hits: str, condition_coverage: Union[str, None]):
        self.condition_coverage = condition_coverage
        self.hits = hits

    def get(self, attr: str):
        if attr == 'condition-coverage':
            return self.condition_coverage

        if attr == 'hits':
            return self.hits

        raise ValueError(f"FakeLine.get() received an unexpected attribute: {attr}")

@pytest.mark.parametrize("line, expected_output", [
    (FakeLine("0", None), "miss"),
    (FakeLine("1", None), "hit"),
    (FakeLine("1", "50% (1/2)"), "partial"),
    (FakeLine("1", "100% (2/2)"), "hit"),
    (FakeLine("0", "0% (0/2)"), "miss"),
])
def test_get_line_status(line, expected_output):
    assert get_line_status(line) == expected_output
