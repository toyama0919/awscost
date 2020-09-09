import click
import sys
import json
import awscost
from .cost_explorer import CostExplorer
from .validator import Validator
from . import constants


@click.command()
@click.option(
    "--debug/--no-debug", default=None, help="enable debug logging. (default: False)"
)
@click.option(
    "--version/--no-version", "-v", default=False, help="show version. (default: False)"
)
@click.option("--config", "-c", type=str, help="config file.")
@click.option("--profile", type=str, help="aws profile name.")
@click.option("--aws-profile", type=str, help="aws profile name.")
@click.option(
    "--granularity",
    "-g",
    type=click.Choice(["DAILY", "MONTHLY"]),
    help="granularity. (default: MONTHLY)",
)
@click.option(
    "--point",
    "-p",
    type=int,
    help=f"""duration.
if granularity is MONTHLY, {constants.DEFAULT_POINT} month ago start.
if granularity is DAILY, {constants.DEFAULT_POINT} day ago start.
(default: {constants.DEFAULT_POINT})""",
)
@click.option(
    "--start",
    callback=Validator.validate_dateformat,
    type=str,
    help=f"range of start day. default is {constants.DEFAULT_POINT} month ago.",
)
@click.option(
    "--end",
    callback=Validator.validate_dateformat,
    type=str,
    help="range of end day. default is now.",
)
@click.option(
    "--tablefmt",
    "-t",
    type=str,
    default="simple",
    help="tabulate format. (default: simple)",
)
@click.option(
    "--dimensions",
    "-d",
    type=click.Choice(constants.AVAILABLE_DIMENSIONS),
    multiple=True,
    help='group by dimensions. (default: ["SERVICE"])',
)
@click.option(
    "--filter", type=json.loads, help="filter of dimensions. default is no filter."
)
@click.option(
    "--metrics",
    type=click.Choice(constants.AVAILABLE_METRICS),
    default=constants.DEFAULT_METRICS,
    help="metrics. (default: UnblendedCost)",
)
@click.option(
    "--total/--no-total", default=True, help="include total cost. (default: True)"
)
@click.pass_context
def cli(
    ctx,
    debug,
    version,
    config,
    profile,
    aws_profile,
    granularity,
    point,
    start,
    end,
    tablefmt,
    dimensions,
    filter,
    metrics,
    total,
):
    if version:
        click.echo(awscost.VERSION)
        sys.exit()

    cost_explorer = CostExplorer(
        granularity=granularity,
        point=point,
        start=start,
        end=end,
        config=config,
        profile=profile,
        dimensions=dimensions,
        filter=filter,
        metrics=metrics,
        debug=debug,
        aws_profile=aws_profile,
        total=total,
    )
    click.echo(cost_explorer.to_tabulate(tablefmt=tablefmt))


def main():
    cli()
