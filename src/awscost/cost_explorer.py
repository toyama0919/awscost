from datetime import datetime
from .logger import get_logger
from .cost_explorer_client import CostExplorerClient
from .tabulate_util import TabulateUtil
from . import constants


class CostExplorer:
    def __init__(
        self,
        granularity,
        start,
        end,
        dimensions=[],
        filter_dimensions=None,
        metrics=constants.DEFAULT_METRICS,
        profile=None,
        debug=False,
    ):
        self.cost_explorer_client = CostExplorerClient(
            granularity,
            start,
            end,
            filter_dimensions=filter_dimensions,
            metrics=metrics,
            profile=profile,
            debug=debug,
        )
        self.granularity = granularity
        self.dimensions = dimensions
        self.metrics = metrics
        self.logger = get_logger(debug=debug)

    def to_tabulate(self, data, tablefmt=None):
        """
        convert tabulate style.
        """
        return TabulateUtil.convert(data, tablefmt=tablefmt)

    def get_cost_and_usage_total_and_group_by(self):
        """
        startとendを指定してcostの時系列データを取得し、totalとgroup_byをmergeする
        """
        # totalを取得
        total = self.get_cost_and_usage_total()

        # group別を取得
        results = self.get_cost_and_usage_group_by()

        # totalとgroup byをmergeする
        merged = dict(total, **results)
        self.logger.debug(merged)
        return merged

    def get_cost_and_usage_total(self):
        """
        startとendを指定してcostの時系列データを取得する
        """
        # totalを取得
        cost_and_usage = self.cost_explorer_client.get_cost_and_usage()
        total = self._convert_results_total(cost_and_usage)
        self.logger.debug(total)
        return total

    def get_cost_and_usage_group_by(self):
        """
        startとendを指定してcostの時系列データを取得する
        """
        cost_and_usage_per_service = self.cost_explorer_client.get_cost_and_usage(
            dimensions=self.dimensions
        )
        results = self._convert_results_group_by(cost_and_usage_per_service)
        self.logger.debug(results)
        return results

    def _convert_results_group_by(self, cost_and_usage_per_service):
        """
        group-byが指定されているデータ構造のparse
        """
        results = {}
        for result in cost_and_usage_per_service:
            start_period = result.get("TimePeriod").get("Start")
            time_key = self._convert_period(start_period)
            groups = result.get("Groups")
            for group in groups:
                group_by_key = ",".join(group.get("Keys"))
                if results.get(group_by_key) is None:
                    results[group_by_key] = {}
                else:
                    results[group_by_key] = results.get(group_by_key)
                metrics = group.get("Metrics")
                amount = metrics.get(self.metrics).get("Amount")
                results[group_by_key][time_key] = round(float(amount), 2)
        return results

    def _convert_results_total(self, cost_and_usage_per_service):
        """
        Totalのデータ構造のparse
        """
        results = {"Total": {}}
        for result in cost_and_usage_per_service:
            start_period = result.get("TimePeriod").get("Start")
            time_key = self._convert_period(start_period)
            metrics = result.get("Total")
            amount = metrics.get(self.metrics).get("Amount")
            results["Total"][time_key] = round(float(amount), 2)
        return results

    def _convert_period(self, start_period):
        """
        headerに表示させる日付をmonthlyとdailyで切り替え
        """
        if self.granularity == "MONTHLY":
            return datetime.strptime(start_period, "%Y-%m-%d").strftime("%Y-%m")
        return datetime.strptime(start_period, "%Y-%m-%d").strftime("%m-%d")
