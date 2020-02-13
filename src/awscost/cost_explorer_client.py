from boto3.session import Session
from .logger import get_logger


class CostExplorerClient:
    def __init__(
        self,
        granularity,
        start,
        end,
        filter=None,
        metrics=None,
        aws_profile=None,
        debug=False,
    ):
        self.granularity = granularity
        self.start = start
        self.end = end
        self.filter = filter
        self.metrics = metrics
        self.client = Session(profile_name=aws_profile).client(
            "ce", region_name="us-east-1"
        )
        self.logger = get_logger(debug=debug)

    def get_cost_and_usage(self, dimensions=None):
        """
        cost explorerのAPIを実行
        """
        params = dict(
            TimePeriod={"Start": self.start, "End": self.end},
            Granularity=self.granularity,
            Metrics=[self.metrics],
        )
        group_by = self._get_group_by(dimensions)
        if group_by is not None:
            params["GroupBy"] = group_by
        if self.filter is not None:
            params["Filter"] = self.filter
        self.logger.debug(params)
        response = self.client.get_cost_and_usage(**params)
        return response.get("ResultsByTime")

    def _get_group_by(self, dimensions):
        """
        listからgroup-byの構造に変換
        """
        if dimensions is None:
            return None
        return [{"Type": "DIMENSION", "Key": key} for key in dimensions]
