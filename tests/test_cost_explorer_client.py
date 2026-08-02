from awscost.cost_explorer_client import CostExplorerClient


class FakeClient:
    def __init__(self, response=None):
        self.response = response or {"ResultsByTime": []}
        self.called_params = None

    def get_cost_and_usage(self, **params):
        self.called_params = params
        return self.response


def build_client(**kwargs):
    return CostExplorerClient(
        kwargs.pop("granularity", "MONTHLY"),
        kwargs.pop("start", "2020-01-01"),
        kwargs.pop("end", "2020-02-01"),
        metrics=kwargs.pop("metrics", "UnblendedCost"),
        client=kwargs.pop("client", FakeClient()),
        **kwargs,
    )


def test_get_group_by_dimensions_and_tags():
    client = build_client()
    group_by = client._get_group_by(dimensions=["SERVICE"], tags=["Name"])
    assert group_by == [
        {"Type": "DIMENSION", "Key": "SERVICE"},
        {"Type": "TAG", "Key": "Name"},
    ]


def test_get_group_by_empty():
    client = build_client()
    assert client._get_group_by() == []


def test_make_params_basic():
    client = build_client()
    params = client._make_params([], [])
    assert params["TimePeriod"] == {"Start": "2020-01-01", "End": "2020-02-01"}
    assert params["Granularity"] == "MONTHLY"
    assert params["Metrics"] == ["UnblendedCost"]
    # No group-by keys -> empty GroupBy list, and no filter set.
    assert params["GroupBy"] == []
    assert "Filter" not in params


def test_make_params_with_group_by_and_filter():
    filter_ = {"Dimensions": {"Key": "REGION", "Values": ["us-east-1"]}}
    client = build_client(filter=filter_)
    params = client._make_params(["SERVICE"], [])
    assert params["GroupBy"] == [{"Type": "DIMENSION", "Key": "SERVICE"}]
    assert params["Filter"] == filter_


def test_get_cost_and_usage_passes_params_and_returns_results():
    fake = FakeClient(
        response={"ResultsByTime": [{"TimePeriod": {"Start": "2020-01-01"}}]}
    )
    client = build_client(client=fake)
    results = client.get_cost_and_usage(dimensions=["SERVICE"])
    assert results == [{"TimePeriod": {"Start": "2020-01-01"}}]
    assert fake.called_params["GroupBy"] == [{"Type": "DIMENSION", "Key": "SERVICE"}]
