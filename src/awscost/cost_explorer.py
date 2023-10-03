import yaml
import os
from tabulate import tabulate
from datetime import datetime
from collections import OrderedDict
from .logger import get_logger
from .cost_explorer_client import CostExplorerClient
from . import constants
from .date_util import DateUtil


class CostExplorer:
    """
    convert responce data class.
    """

    def __init__(
        self,
        config=None,
        profile=None,
        granularity=None,
        point=None,
        start=None,
        end=None,
        dimensions=None,
        tags=None,
        filter=None,
        metrics=None,
        aws_profile=None,
        debug=None,
        total=None,
        threshold=None,
    ):
        # read profile
        profile = self._read_profile(config, profile)

        self.granularity = self.get_not_none_first(
            granularity, profile.get("granularity"), constants.DEFAULT_GRANULARITY
        )
        self.dimensions = self.get_not_none_first(
            dimensions, profile.get("dimensions"), constants.DEFAULT_DIMENSIONS
        )
        self.tags = self.get_not_none_first(tags, profile.get("tags"), [])
        self.metrics = self.get_not_none_first(
            metrics, profile.get("metrics"), constants.DEFAULT_METRICS
        )
        self.total = self.get_not_none_first(
            total, profile.get("total"), constants.DEFAULT_TOTAL
        )
        debug = self.get_not_none_first(
            debug, profile.get("debug"), constants.DEFAULT_DEBUG
        )
        self.logger = get_logger(debug=debug)
        self.threshold = self.get_not_none_first(
            threshold, profile.get("threshold"), constants.DEFAULT_THRESHOLD
        )

        aws_profile = self.get_not_none_first(aws_profile, profile.get("aws_profile"))
        filter = self.get_not_none_first(filter, profile.get("filter"))
        point = self.get_not_none_first(
            point, profile.get("point"), constants.DEFAULT_POINT
        )
        start = self.get_not_none_first(
            start, profile.get("start"), DateUtil.get_start(self.granularity, point)
        )
        end = self.get_not_none_first(
            end, profile.get("end"), datetime.today().strftime("%Y-%m-%d")
        )

        self.cost_explorer_client = CostExplorerClient(
            self.granularity,
            start,
            end,
            filter=filter,
            metrics=metrics,
            aws_profile=aws_profile,
            debug=debug,
        )

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
        Get cost time series data by specifying start and end, and merge total and group_by

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
        Get cost time series data by specifying start and end
        """
        # totalを取得
        cost_and_usage = self.cost_explorer_client.get_cost_and_usage()
        total = self._convert_results_total(cost_and_usage)
        return total

    def get_cost_and_usage_group_by(self):
        """
        Get cost time series data by specifying start and end
        """
        cost_and_usage_per_service = self.cost_explorer_client.get_cost_and_usage(
            dimensions=self.dimensions, tags=self.tags
        )
        results = self._convert_results_group_by(cost_and_usage_per_service)
        results = dict(
            filter(
                lambda item: max(list(item[1].values())) >= self.threshold,
                results.items(),
            )
        )
        return results

    def _convert_results_group_by(self, cost_and_usage_per_service):
        """
        Parse data structure for which group-by is specified
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
        Parse the data structure of Total
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
        Switching the date displayed in the header between monthly and daily
        """
        if self.granularity == "MONTHLY":
            return datetime.strptime(start_period, "%Y-%m-%d").strftime("%Y-%m")
        return datetime.strptime(start_period, "%Y-%m-%d").strftime("%m-%d")

    def _read_profile(self, config, profile_name):
        config = config or constants.DEFAULT_CONFIG
        profile_name = profile_name or constants.DEFAULT_PROFILE
        if config and os.path.exists(config):
            profile = yaml.safe_load(open(config, encoding="UTF-8").read()).get(
                profile_name
            )
            if profile is None:
                profile = {}
        else:
            profile = {}
        return profile

    @staticmethod
    def pad_zero(total, group_by_results):
        """
        Fill the value to zero
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

    def get_not_none_first(self, *args):
        for v in list(args):
            if v is not None:
                return v
        return None
