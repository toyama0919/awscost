import click
import pytest

from awscost.validator import Validator


def test_validate_dateformat_none_returns_none():
    assert Validator.validate_dateformat(None, None, None) is None


def test_validate_dateformat_valid_returns_value():
    assert Validator.validate_dateformat(None, None, "2020-01-01") == "2020-01-01"


def test_validate_dateformat_invalid_raises_bad_parameter():
    with pytest.raises(click.BadParameter):
        Validator.validate_dateformat(None, None, "2020/01/01")
