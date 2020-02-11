from tabulate import tabulate
from datetime import datetime
from collections import OrderedDict
from .logger import get_logger
from .cost_explorer_client import CostExplorerClient
from . import constants


class CostExplorer:
    """
    convert responce data class.
    """

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
        total=True,
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
        self.total = total
        self.logger = get_logger(debug=debug)

    def to_tabulate(self, tablefmt=None):
        """
        convert tabulate style.
        """
        data = self.get_cost_and_usage_total_and_group_by()
        converts = []
        for k, amounts in data.items():
            converts.append(dict({"key": k}, **amounts))
        last_time = list(converts[0].keys())[-1]
        converts = sorted(
            converts,
            key=lambda x: 0 if x.get(last_time) is None else x.get(last_time),
            reverse=True,
        )
        return tabulate(converts, headers="keys", tablefmt=tablefmt)

    def get_cost_and_usage_total_and_group_by(self):
        """
        startとendを指定してcostの時系列データを取得し、totalとgroup_byをmergeする
        """
        # totalを取得
        total = self.get_cost_and_usage_total()

        # group byしたデータを取得
        group_by_results = self.get_cost_and_usage_group_by()

        # totalと0埋めしたgroup byをmergeする
        group_by_results_pad_zero = self.__class__.pad_zero(total, group_by_results)
        if self.total:
            merged = OrderedDict(total, **group_by_results_pad_zero)
            return merged
        return group_by_results_pad_zero

    def get_cost_and_usage_total(self):
        """
        startとendを指定してcostの時系列データを取得する
        """
        # totalを取得
        cost_and_usage = self.cost_explorer_client.get_cost_and_usage()
        total = self._convert_results_total(cost_and_usage)
        return total

    def get_cost_and_usage_group_by(self):
        """
        startとendを指定してcostの時系列データを取得する
        """
        cost_and_usage_per_service = self.cost_explorer_client.get_cost_and_usage(
            dimensions=self.dimensions
        )
        results = self._convert_results_group_by(cost_and_usage_per_service)
        return results

    def _convert_results_group_by(self, cost_and_usage_per_service):
        """
        group-byが指定されているデータ構造のparse
        """
        results = OrderedDict()
        for result in cost_and_usage_per_service:
            start_period = result.get("TimePeriod").get("Start")
            time_key = self._convert_period(start_period)
            groups = result.get("Groups")
            for group in groups:
                group_by_key = ",".join(group.get("Keys"))
                if results.get(group_by_key) is None:
                    results[group_by_key] = OrderedDict()
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
        results = OrderedDict([("Total", OrderedDict())])
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

    @staticmethod
    def pad_zero(total, group_by_results):
        """
        値を0埋めする
        """
        # 0埋めするためのdictを作成
        pad_zero = OrderedDict()
        for k, v in total.get("Total").items():
            pad_zero[k] = 0

        group_by_results_pad_zero = OrderedDict()
        for k, v in group_by_results.items():
            merged = OrderedDict(pad_zero, **v)
            group_by_results_pad_zero[k] = merged
        return group_by_results_pad_zero
