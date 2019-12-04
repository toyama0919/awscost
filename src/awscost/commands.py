import click
import json
from datetime import datetime
from .billing import Billing
from .cost_explorer import CostExplorer
from .util import Util
from .date_util import DateUtil
from .constants import DIMENSIONS


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
@click.option('--point', '-p', type=int, default=10, help='number of data point. (default: 10)')
@click.option('--start', type=str, help='range of start day. default is 10 month ago.')
@click.option('--end', type=str, help='range of end day. default is now.')
@click.option('--tablefmt', '-t', type=str, default='simple', help='tabulate format. (default: simple)')
@click.option('--group-by', type=click.Choice(DIMENSIONS), multiple=True, default=['SERVICE'], help='group by keys. (default: ["SERVICE"])')
@click.option('--filter', type=json.loads, help='filter of dimensions. default is no filter.')
@click.pass_context
def list_ce(ctx, granularity, point, start, end, tablefmt, group_by, filter):
    cost_explorer = CostExplorer(
        debug=ctx.obj.debug,
        profile=ctx.obj.profile
    )
    currencies = cost_explorer.get_currencies_total_and_group_by(
        granularity,
        start or DateUtil.get_start(granularity, point),
        end or datetime.today().strftime("%Y-%m-%d"),
        group_by=group_by,
        filter_dimensions=filter
    )
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
