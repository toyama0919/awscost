from datetime import timedelta
from datetime import datetime


class DateUtil:
    @staticmethod
    def get_start(granularity, point):
        """
        Automatic adjustment of datapoint scale by month, day
        """
        if granularity == "MONTHLY":
            days = 30 * point
        elif granularity == "DAILY":
            days = point

        start_datetime = datetime.today() - timedelta(days=days)
        if granularity == "MONTHLY":
            start_datetime = start_datetime.replace(day=1)
        return start_datetime.strftime("%Y-%m-%d")
