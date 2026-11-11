def _check_digit(digits: str, weights: tuple[int, ...]) -> int:
    return sum(int(d) * w for d, w in zip(digits, weights, strict=True)) % 11 % 10


def is_valid_inn(value: str) -> bool:
    """Validate Russian INN (10 digits for entities, 12 for individuals)."""
    if not value.isdigit():
        return False
    if len(value) == 10:
        return _check_digit(value[:9], (2, 4, 10, 3, 5, 9, 4, 6, 8)) == int(value[9])
    if len(value) == 12:
        d11 = _check_digit(value[:10], (7, 2, 4, 10, 3, 5, 9, 4, 6, 8))
        d12 = _check_digit(value[:11], (3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8))
        return d11 == int(value[10]) and d12 == int(value[11])
    return False
