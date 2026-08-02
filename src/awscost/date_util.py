from datetime import datetime, timedelta


class DateUtil:
    @staticmethod
    def get_start(granularity, point, today=None):
        """
        Automatic adjustment of datapoint scale by month, day

        ``today`` can be injected for deterministic testing. Defaults to
        ``datetime.today()`` when omitted.
        """
        if granularity == "MONTHLY":
            days = 30 * point
        elif granularity == "DAILY":
            days = point
        else:
            raise ValueError(f"unsupported granularity: {granularity}")

        today = today or datetime.today()
        start_datetime = today - timedelta(days=days)
        if granularity == "MONTHLY":
            start_datetime = start_datetime.replace(day=1)
        return start_datetime.strftime("%Y-%m-%d")
