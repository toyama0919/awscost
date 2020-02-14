from awscost.cost_explorer import CostExplorer
from awscost.cost_explorer_client import CostExplorerClient
from mock import patch
from collections import OrderedDict


class TestCostExplorer(object):
    def setup_method(self, method):
        pass

    def teardown_method(self, method):
        pass

    def test_pad_zero(self):
        total = {"Total": {"2020-01": 1.5, "2020-02": 1.5, "2020-03": 1.5}}
        group_by_results = {
            "EC2 - Other": {"2020-02": 1.5},
            "Amazon Simple Storage Service": {"2020-01": 2.5},
        }
        group_by_results_pad_zero = CostExplorer.pad_zero(total, group_by_results)

        ec2 = group_by_results_pad_zero.get("EC2 - Other")
        assert ec2.get("2020-01") == 0
        assert ec2.get("2020-02") == 1.5
        assert ec2.get("2020-03") == 0

        s3 = group_by_results_pad_zero.get("Amazon Simple Storage Service")
        assert s3.get("2020-01") == 2.5
        assert s3.get("2020-02") == 0
        assert s3.get("2020-03") == 0

    def test_get_cost_and_usage_group_by(self):
        cost_explorer = CostExplorer()
        with patch.object(CostExplorerClient, "get_cost_and_usage") as mock_foo:
            mock_foo.return_value = [
                {
                    "TimePeriod": {"Start": "2019-12-01", "End": "2020-01-01"},
                    "Total": {},
                    "Groups": [
                        {
                            "Keys": ["AWS CloudTrail"],
                            "Metrics": {
                                "UnblendedCost": {"Amount": "4.380886", "Unit": "USD"}
                            },
                        },
                    ],
                    "Estimated": False,
                },
                {
                    "TimePeriod": {"Start": "2020-01-01", "End": "2020-02-01"},
                    "Total": {},
                    "Groups": [
                        {
                            "Keys": ["AWS CloudTrail"],
                            "Metrics": {
                                "UnblendedCost": {"Amount": "4.380886", "Unit": "USD"}
                            },
                        },
                        {
                            "Keys": ["AWS Cost Explorer"],
                            "Metrics": {
                                "UnblendedCost": {"Amount": "0.02", "Unit": "USD"}
                            },
                        },
                        {
                            "Keys": ["AWS Key Management Service"],
                            "Metrics": {
                                "UnblendedCost": {
                                    "Amount": "4.002411936",
                                    "Unit": "USD",
                                }
                            },
                        },
                        {
                            "Keys": ["AWS Lambda"],
                            "Metrics": {
                                "UnblendedCost": {
                                    "Amount": "0.0010751459",
                                    "Unit": "USD",
                                }
                            },
                        },
                    ],
                    "Estimated": False,
                },
            ]
            assert cost_explorer.get_cost_and_usage_group_by() == OrderedDict(
                [
                    (
                        "AWS CloudTrail",
                        OrderedDict([("2019-12", 4.38), ("2020-01", 4.38)]),
                    ),
                    ("AWS Cost Explorer", OrderedDict([("2020-01", 0.02)])),
                    ("AWS Key Management Service", OrderedDict([("2020-01", 4.0)])),
                    ("AWS Lambda", OrderedDict([("2020-01", 0.0)])),
                ]
            )

    def test_get_cost_and_usage_total(self):
        cost_explorer = CostExplorer()
        with patch.object(CostExplorerClient, "get_cost_and_usage") as mock_foo:
            mock_foo.return_value = [
                {
                    "TimePeriod": {"Start": "2019-12-01", "End": "2020-01-01"},
                    "Total": {
                        "UnblendedCost": {"Amount": "72.2197813571", "Unit": "USD"}
                    },
                    "Groups": [],
                    "Estimated": False,
                },
                {
                    "TimePeriod": {"Start": "2020-01-01", "End": "2020-02-01"},
                    "Total": {
                        "UnblendedCost": {"Amount": "68.0906860747", "Unit": "USD"}
                    },
                    "Groups": [],
                    "Estimated": False,
                },
                {
                    "TimePeriod": {"Start": "2020-02-01", "End": "2020-02-14"},
                    "Total": {
                        "UnblendedCost": {"Amount": "32.2073391037", "Unit": "USD"}
                    },
                    "Groups": [],
                    "Estimated": True,
                },
            ]
            print(cost_explorer.get_cost_and_usage_total())
            assert cost_explorer.get_cost_and_usage_total() == OrderedDict(
                [
                    (
                        "Total",
                        OrderedDict(
                            [("2019-12", 72.22), ("2020-01", 68.09), ("2020-02", 32.21)]
                        ),
                    )
                ]
            )
