from click.testing import CliRunner
from mock import patch
import pytest

import awscost
from awscost import commands
from awscost.cost_explorer_client import CostExplorerClient


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


def _api_response(dimensions=None, tags=None):
    if dimensions:
        return [
            {
                "TimePeriod": {"Start": "2020-01-01", "End": "2020-02-01"},
                "Total": {},
                "Groups": [
                    {
                        "Keys": ["EC2"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "18.0", "Unit": "USD"}
                        },
                    }
                ],
            }
        ]
    return [
        {
            "TimePeriod": {"Start": "2020-01-01", "End": "2020-02-01"},
            "Total": {"UnblendedCost": {"Amount": "20.0", "Unit": "USD"}},
            "Groups": [],
        }
    ]


def test_show_version(runner):
    result = runner.invoke(commands.cli, ["-v"])
    assert result.exit_code == 0
    assert result.output.strip() == awscost.VERSION


def test_cli_outputs_table(runner):
    with patch.object(
        CostExplorerClient, "get_cost_and_usage", side_effect=_api_response
    ):
        result = runner.invoke(commands.cli, [])
    assert result.exit_code == 0
    assert "Total" in result.output
    assert "EC2" in result.output


def test_cli_invalid_start_date_fails(runner):
    result = runner.invoke(commands.cli, ["--start", "2020/01/01"])
    assert result.exit_code != 0
    assert "dateformat" in result.output


def test_cli_no_total(runner):
    with patch.object(
        CostExplorerClient, "get_cost_and_usage", side_effect=_api_response
    ):
        result = runner.invoke(commands.cli, ["--no-total"])
    assert result.exit_code == 0
    assert "Total" not in result.output
    assert "EC2" in result.output
