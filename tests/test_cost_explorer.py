from awscost.cost_explorer import CostExplorer


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
