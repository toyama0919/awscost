from .logger import get_logger
from datetime import datetime
from dateutil.relativedelta import relativedelta
from boto3.session import Session


class Billing:
    def __init__(self, debug, profile):
        self.client = Session(profile_name=profile).client('cloudwatch', region_name='us-east-1')
        self.logger = get_logger(debug)
        response = self.client.list_metrics(
            Namespace='AWS/Billing'
        )
        self.metrics = response.get('Metrics')

    def get_currencies_per_service(self, scale_range, point):
        """
        直近のサービス別のcostの時系列データを取得する
        """
        dateformat, period, delta = self._get_scale(scale_range, point)
        start_time = datetime.today() - relativedelta(days=delta)
        end_time = datetime.today()
        result = []
        for metric in self.metrics:
            dimensions = metric.get('Dimensions')

            datapoints = self._get_datapoints(dimensions, period, start_time, end_time)
            last_timestamp = datapoints[-1].get('Timestamp').strftime(dateformat)

            service_name = self._get_service_name(dimensions)
            row = self._get_service_cost(datapoints, service_name, metric, dateformat)
            result.append(row)
        return sorted(result, key=lambda x: x.get(last_timestamp), reverse=True)

    def _get_datapoints(self, dimensions, period, start_time, end_time):
        """
        datapoints(サービス単位のcostの時系列データ)を取得する
        """
        response = self.client.get_metric_statistics(
            Namespace='AWS/Billing',
            MetricName='EstimatedCharges',
            Dimensions=dimensions,
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=['Maximum']
        )
        return sorted(response.get('Datapoints'), key=lambda x: x.get('Timestamp'))

    def _get_service_name(self, dimensions):
        """
        service名をdimensionsから取得する。
        service名がdimensionsに入っていない場合はTotalになる
        """
        services = [
            dimension
            for dimension in dimensions
            if dimension.get('Name') == "ServiceName"
        ]
        return services[0].get('Value') if len(services) != 0 else "Total"

    def _get_service_cost(self, datapoints, service_name, metric, dateformat):
        """
        サービスごとのcostを取得する
        """
        row = {"service_name": service_name}
        for datapoint in datapoints:
            timestamp = datapoint.get('Timestamp').strftime(dateformat)
            maximum = datapoint.get('Maximum')
            row[timestamp] = maximum
        return row

    def _get_scale(self, scale_range, point):
        """
        datapointのscaleをmonth, week, dayで自動調節する
        """
        if scale_range == "month":
            return '%y/%m', 60 * 60 * 24 * 30, 30 * point
        elif scale_range == "week":
            return '%m/%d', 60 * 60 * 24 * 7, 7 * point
        elif scale_range == "day":
            return '%m/%d', 60 * 60 * 24, 1 * point
        return '%m/%d', 86400, 1 * point
