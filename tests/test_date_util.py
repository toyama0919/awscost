from datetime import datetime

import pytest

from awscost.date_util import DateUtil


def test_get_start_monthly_replaces_day_with_first():
    today = datetime(2020, 3, 15)
    # 30 * 2 = 60 days ago -> 2020-01-15, then day replaced with 1
    assert DateUtil.get_start("MONTHLY", 2, today=today) == "2020-01-01"


def test_get_start_daily_subtracts_point_days():
    today = datetime(2020, 3, 15)
    assert DateUtil.get_start("DAILY", 5, today=today) == "2020-03-10"


def test_get_start_daily_does_not_replace_day():
    today = datetime(2020, 3, 15)
    assert DateUtil.get_start("DAILY", 0, today=today) == "2020-03-15"


def test_get_start_defaults_today_to_now():
    # Without an explicit today it must still return a valid date string.
    value = DateUtil.get_start("MONTHLY", 1)
    datetime.strptime(value, "%Y-%m-%d")


def test_get_start_invalid_granularity_raises():
    with pytest.raises(ValueError):
        DateUtil.get_start("YEARLY", 1, today=datetime(2020, 3, 15))
