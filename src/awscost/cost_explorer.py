from boto3.session import Session
from datetime import datetime
from .logger import get_logger


class CostExplorer:
    def __init__(self, profile=None, debug=False):
        self.client = Session(profile_name=profile).client('ce', region_name='us-east-1')
        self.logger = get_logger(debug=debug)

    def get_currencies_total_and_group_by(self, granularity, start, end, group_by=None):
        """
        startとendを指定してcostの時系列データを取得する
        """
        # totalを取得
        total = self.get_currencies_total(granularity, start, end)

        # group別を取得
        results = self.get_currencies_group_by(granularity, start, end, group_by=group_by)

        # totalとgroup byをmergeする
        merged = dict(total, **results)
        self.logger.debug(merged)
        return merged

    def get_currencies_group_by(self, granularity, start, end, group_by=None):
        """
        startとendを指定してcostの時系列データを取得する
        """
        group_by = [
            {
                'Type': 'DIMENSION',
                'Key': key
            }
            for key in group_by
        ]
        cost_and_usage_per_service = self._get_cost_and_usage(granularity, start, end, group_by=group_by)
        results = self._convert_results_group_by(cost_and_usage_per_service, granularity)
        self.logger.debug(results)
        return results

    def get_currencies_total(self, granularity, start, end):
        """
        startとendを指定してcostの時系列データを取得する
        """
        # totalを取得
        cost_and_usage = self._get_cost_and_usage(granularity, start, end)
        total = self._convert_results_total(cost_and_usage, granularity)
        self.logger.debug(total)
        return total

    def _convert_results_group_by(self, cost_and_usage_per_service, granularity):
        """
        group-byが指定されているデータ構造のparse
        """
        results = {}
        for result in cost_and_usage_per_service:
            start_period = result.get('TimePeriod').get('Start')
            time_key = self._convert_period(granularity, start_period)
            groups = result.get('Groups')
            for group in groups:
                group_by_key = ','.join(group.get('Keys'))
                if results.get(group_by_key) is None:
                    results[group_by_key] = {}
                else:
                    results[group_by_key] = results.get(group_by_key)
                metrics = group.get('Metrics')
                amount = metrics.get('UnblendedCost').get('Amount')
                results[group_by_key][time_key] = round(float(amount), 2)
        return results

    def _convert_results_total(self, cost_and_usage_per_service, granularity):
        """
        Totalのデータ構造のparse
        """
        results = {"Total": {}}
        for result in cost_and_usage_per_service:
            start_period = result.get('TimePeriod').get('Start')
            time_key = self._convert_period(granularity, start_period)
            metrics = result.get('Total')
            amount = metrics.get('UnblendedCost').get('Amount')
            results["Total"][time_key] = round(float(amount), 2)
        return results

    def _get_cost_and_usage(self, granularity, start, end, group_by=None):
        """
        datapointのscaleをmonth, week, dayで自動調節する
        """
        params = dict(
            TimePeriod={
                'Start': start,
                'End': end
            },
            Granularity=granularity,
            Metrics=[
                'UnblendedCost',
            ],
        )
        if group_by is not None:
            params["GroupBy"] = group_by
        self.logger.debug(params)
        response = self.client.get_cost_and_usage(**params)
        return response.get("ResultsByTime")

    def _convert_period(self, granularity, start_period):
        """
        datapointのscaleをmonth, week, dayで自動調節する
        """
        if granularity == "MONTHLY":
            return datetime.strptime(start_period, '%Y-%m-%d').strftime('%Y-%m')
        return start_period
