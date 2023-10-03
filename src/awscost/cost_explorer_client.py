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

    def get_cost_and_usage(self, dimensions=[], tags=[]):
        """
        Execute cost explorer API
        """
        params = self._make_params(dimensions, tags)
        results = self.client.get_cost_and_usage(**params).get("ResultsByTime")
        self.logger.debug(results)
        return results

    def _make_params(self, dimensions, tags):
        params = dict(
            TimePeriod={"Start": self.start, "End": self.end},
            Granularity=self.granularity,
            Metrics=[self.metrics],
        )
        group_by = self._get_group_by(dimensions=dimensions, tags=tags)
        if group_by is not None:
            params["GroupBy"] = group_by
        if self.filter is not None:
            params["Filter"] = self.filter
        self.logger.debug(params)
        return params

    def _get_group_by(self, dimensions=[], tags=[]):
        """
        Convert from list to group-by structure
        """
        group_by = [{"Type": "DIMENSION", "Key": key} for key in dimensions]
        for tag in tags:
            group_by.append({"Type": "TAG", "Key": tag})
        return group_by
