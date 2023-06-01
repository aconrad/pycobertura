def test_extrapolate_coverage():
    from pycobertura.utils import extrapolate_coverage
    lines_w_status = [
        (1, "hit"),
        (4, "hit"),
        (7, "miss"),
        (9, "miss"),
    ]

    assert extrapolate_coverage(lines_w_status) == [
        (1, "hit"),
        (2, "hit"),
        (3, "hit"),
        (4, "hit"),
        (5, None),
        (6, None),
        (7, "miss"),
        (8, "miss"),
        (9, "miss"),
    ]
