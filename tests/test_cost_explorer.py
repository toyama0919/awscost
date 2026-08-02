from collections import OrderedDict

from mock import patch

from awscost.cost_explorer import CostExplorer
from awscost.cost_explorer_client import CostExplorerClient

TOTAL_RESPONSE = [
    {
        "TimePeriod": {"Start": "2019-12-01", "End": "2020-01-01"},
        "Total": {"UnblendedCost": {"Amount": "10.0", "Unit": "USD"}},
        "Groups": [],
    },
    {
        "TimePeriod": {"Start": "2020-01-01", "End": "2020-02-01"},
        "Total": {"UnblendedCost": {"Amount": "20.0", "Unit": "USD"}},
        "Groups": [],
    },
]

GROUP_BY_RESPONSE = [
    {
        "TimePeriod": {"Start": "2019-12-01", "End": "2020-01-01"},
        "Total": {},
        "Groups": [
            {
                "Keys": ["EC2"],
                "Metrics": {"UnblendedCost": {"Amount": "8.0", "Unit": "USD"}},
            },
            {
                "Keys": ["S3"],
                "Metrics": {"UnblendedCost": {"Amount": "2.0", "Unit": "USD"}},
            },
        ],
    },
    {
        "TimePeriod": {"Start": "2020-01-01", "End": "2020-02-01"},
        "Total": {},
        "Groups": [
            {
                "Keys": ["EC2"],
                "Metrics": {"UnblendedCost": {"Amount": "18.0", "Unit": "USD"}},
            },
            {
                "Keys": ["S3"],
                "Metrics": {"UnblendedCost": {"Amount": "2.0", "Unit": "USD"}},
            },
        ],
    },
]


class FakeCostExplorerClient:
    """Returns total data when called without dimensions, group-by otherwise."""

    def __init__(self, total_response=None, group_by_response=None):
        self.total_response = total_response or TOTAL_RESPONSE
        self.group_by_response = group_by_response or GROUP_BY_RESPONSE

    def get_cost_and_usage(self, dimensions=None, tags=None):
        if dimensions:
            return self.group_by_response
        return self.total_response


def build_cost_explorer(**kwargs):
    kwargs.setdefault("cost_explorer_client", FakeCostExplorerClient())
    return CostExplorer(**kwargs)


class TestCostExplorer(object):
    def setup_method(self, method):
        pass

    def teardown_method(self, method):
        pass

    def test_get_not_none_first(self):
        cost_explorer = build_cost_explorer()
        assert cost_explorer.get_not_none_first(None, None, 3, 4) == 3
        assert cost_explorer.get_not_none_first(None, None) is None
        assert cost_explorer.get_not_none_first(0, 1) == 0

    def test_convert_period_monthly(self):
        cost_explorer = build_cost_explorer(granularity="MONTHLY")
        assert cost_explorer._convert_period("2020-01-15") == "2020-01"

    def test_convert_period_daily(self):
        cost_explorer = build_cost_explorer(granularity="DAILY")
        assert cost_explorer._convert_period("2020-01-15") == "01-15"

    def test_threshold_filters_group_by(self):
        # S3 max is 2.0; a threshold of 3.0 must drop it, keeping only EC2.
        cost_explorer = build_cost_explorer(threshold=3.0)
        result = cost_explorer.get_cost_and_usage_group_by()
        assert list(result.keys()) == ["EC2"]

    def test_total_and_group_by_merge_includes_total(self):
        cost_explorer = build_cost_explorer(total=True)
        result = cost_explorer.get_cost_and_usage_total_and_group_by()
        assert "Total" in result
        assert set(result.keys()) == {"Total", "EC2", "S3"}
        # group-by rows are zero-padded to the total's time keys
        assert result["S3"] == OrderedDict([("2019-12", 2.0), ("2020-01", 2.0)])

    def test_total_and_group_by_excludes_total_when_disabled(self):
        cost_explorer = build_cost_explorer(total=False)
        result = cost_explorer.get_cost_and_usage_total_and_group_by()
        assert "Total" not in result
        assert set(result.keys()) == {"EC2", "S3"}

    def test_to_tabulate_sorts_by_last_period_desc(self):
        cost_explorer = build_cost_explorer(total=False)
        output = cost_explorer.to_tabulate(tablefmt="plain")
        lines = output.splitlines()
        # EC2 (18.0 in last period) must sort above S3 (2.0).
        keys = [line.split()[0] for line in lines[1:]]
        assert keys == ["EC2", "S3"]

    def test_read_profile_missing_config_returns_empty(self):
        cost_explorer = build_cost_explorer()
        assert cost_explorer._read_profile("/no/such/file.yml", "default") == {}

    def test_read_profile_loads_named_profile(self, tmp_path):
        config = tmp_path / "config.yml"
        config.write_text("default:\n  granularity: DAILY\n  threshold: 5.0\n")
        cost_explorer = build_cost_explorer()
        profile = cost_explorer._read_profile(str(config), "default")
        assert profile == {"granularity": "DAILY", "threshold": 5.0}

    def test_read_profile_missing_named_profile_returns_empty(self, tmp_path):
        config = tmp_path / "config.yml"
        config.write_text("other:\n  granularity: DAILY\n")
        cost_explorer = build_cost_explorer()
        assert cost_explorer._read_profile(str(config), "default") == {}

    def test_profile_values_override_defaults(self, tmp_path):
        config = tmp_path / "config.yml"
        config.write_text("default:\n  granularity: DAILY\n  threshold: 5.0\n")
        cost_explorer = build_cost_explorer(config=str(config))
        assert cost_explorer.granularity == "DAILY"
        assert cost_explorer.threshold == 5.0

    def test_explicit_args_override_profile(self, tmp_path):
        config = tmp_path / "config.yml"
        config.write_text("default:\n  granularity: DAILY\n")
        cost_explorer = build_cost_explorer(config=str(config), granularity="MONTHLY")
        assert cost_explorer.granularity == "MONTHLY"

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
