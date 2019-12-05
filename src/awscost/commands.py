import click
import json
from datetime import datetime
from .billing import Billing
from .cost_explorer import CostExplorer
from .util import Util
from .validator import Validator
from .date_util import DateUtil
from . import constants


class Mash(object):
    pass


@click.group(invoke_without_command=True)
@click.option('--debug/--no-debug', default=False, help='enable debug logging. (default: False)')
@click.option('--profile', type=str, help='aws profile name.')
@click.pass_context
def cli(ctx, debug, profile):
    ctx.obj = Mash()
    ctx.obj.debug = debug
    ctx.obj.profile = profile


@cli.command(help='list cost explorer')
@click.option('--granularity', '-g', type=click.Choice(['DAILY', 'MONTHLY']), default="MONTHLY", help='granularity. (default: MONTHLY)')
@click.option('--point', '-p', type=int, default=10, help='duration. if granularity is MONTHLY, 10 month ago start. if granularity is DAILY, 10 day ago start. (default: 10)')
@click.option('--start', callback=Validator.validate_dateformat, type=str, help='range of start day. default is 10 month ago.')
@click.option('--end', callback=Validator.validate_dateformat, type=str, default=datetime.today().strftime("%Y-%m-%d"), help='range of end day. default is now.')
@click.option('--tablefmt', '-t', type=str, default='simple', help='tabulate format. (default: simple)')
@click.option('--group-by', type=click.Choice(constants.AVAILABLE_DIMENSIONS), multiple=True, default=['SERVICE'], help='group by keys. (default: ["SERVICE"])')
@click.option('--filter', type=json.loads, help='filter of dimensions. default is no filter.')
@click.option('--metrics', type=click.Choice(constants.AVAILABLE_METRICS), default=constants.DEFAULT_METRICS, help='metrics. (default: UnblendedCost)')
@click.pass_context
def list_ce(ctx, granularity, point, start, end, tablefmt, group_by, filter, metrics):
    cost_explorer = CostExplorer(
        granularity,
        start or DateUtil.get_start(granularity, point),
        end,
        group_by=group_by,
        filter_dimensions=filter,
        metrics=metrics,
        debug=ctx.obj.debug,
        profile=ctx.obj.profile
    )
    currencies = cost_explorer.get_cost_and_usage_total_and_group_by()
    print(Util.convert_tabulate(currencies, tablefmt=tablefmt))


@cli.command(help='list cloudwatch billing')
@click.option('--range', '-r', type=click.Choice(['month', 'week', 'day']), required=True)
@click.option('--tablefmt', '-t', type=str, default='simple', help='tabulate format. (default: simple)')
@click.option('--point', '-p', type=int, default=10, help='number of data point. (default: 10)')
@click.pass_context
def list_billing(ctx, range, tablefmt, point):
    billing = Billing(ctx.obj.debug, ctx.obj.profile)
    currencies = billing.get_currencies_per_service(range, point)
    print(Util.convert_tabulate(currencies, tablefmt=tablefmt))


def main():
    cli(obj={})
