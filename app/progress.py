def progress_fraction(current_end: float, total_duration: float) -> float:
    if total_duration <= 0:
        return 0.0
    fraction = current_end / total_duration
    return max(0.0, min(1.0, fraction))
