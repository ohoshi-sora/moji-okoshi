from app.progress import progress_fraction


def test_progress_fraction_midpoint():
    assert progress_fraction(30.0, 60.0) == 0.5


def test_progress_fraction_clamped_to_one():
    assert progress_fraction(90.0, 60.0) == 1.0


def test_progress_fraction_zero_duration_is_zero():
    assert progress_fraction(10.0, 0.0) == 0.0


def test_progress_fraction_negative_current_clamped_to_zero():
    assert progress_fraction(-5.0, 60.0) == 0.0
