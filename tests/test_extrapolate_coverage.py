def test_extrapolate_coverage():
    from pycobertura.utils import extrapolate_coverage
    lines_w_status = [
        (1, True),
        (4, True),
        (7, False),
        (9, False),
    ]

    assert extrapolate_coverage(lines_w_status) == [
        (1, True),
        (2, True),
        (3, True),
        (4, True),
        (5, None),
        (6, None),
        (7, False),
        (8, False),
        (9, False),
    ]
