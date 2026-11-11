import pytest
from app.inn import is_valid_inn


@pytest.mark.parametrize("inn", [
    "7707083893",  # valid 10-digit INN
    "500100732259",  # valid 12-digit INN
])
def test_valid_inn(inn):
    assert is_valid_inn(inn)


@pytest.mark.parametrize("inn", [
    "7707083890",
    "500100732250",
    "123",
    "abcdefghij",
    " 7707083893",
    "770708389",
    "77070838930",
])
def test_invalid_inn(inn):
    assert not is_valid_inn(inn)
