import click
from datetime import timedelta
from datetime import datetime
from .logger import get_logger
from .billing import Billing
from .cost_explorer import CostExplorer
from .util import Util
from .date_util import DateUtil
from .constants import DIMENSIONS


class Mash(object):
    pass


@click.group()
@click.option('--debug/--no-debug', default=False, help='enable debug logging')
@click.option('--profile', type=str, help='aws profile')
@click.pass_context
def cli(ctx, debug, profile):
    ctx.obj = Mash()
    ctx.obj.billing = Billing(debug, profile)
    ctx.obj.logger = get_logger(debug)
    ctx.obj.debug = debug
    ctx.obj.profile = profile


@cli.command(help='show cost explorer')
@click.option('--granularity', '-g', type=click.Choice(['DAILY', 'MONTHLY']), default="MONTHLY")
@click.option('--point', '-p', type=int, default=10, help='number of greetings')
@click.option('--start', type=str)
@click.option('--end', type=str)
@click.option('--tablefmt', '-t', type=str, default='simple')
@click.option('--group-by', type=click.Choice(DIMENSIONS), multiple=True, default=['SERVICE'])
@click.pass_context
def list_ce(ctx, granularity, point, start, end, tablefmt, group_by):
    cost_explorer = CostExplorer(
        debug=ctx.obj.debug,
        profile=ctx.obj.profile
    )
    currencies = cost_explorer.get_currencies_total_and_group_by(
        granularity,
        start or DateUtil.get_start(granularity, point),
        end or datetime.today().strftime("%Y-%m-%d"),
        group_by=group_by
    )
    Util.print_tabulate(currencies, tablefmt=tablefmt)


@cli.command(help='show cloudwatch billing')
@click.option('--range', '-r', type=click.Choice(['month', 'week', 'day']), required=True)
@click.option('--tablefmt', '-t', type=str, default='simple')
@click.option('--point', '-p', type=int, default=10, help='number of greetings')
@click.pass_context
def list_billing(ctx, range, tablefmt, point):
    currencies = ctx.obj.billing.get_currencies_per_service(range, point)
    print(currencies)


def main():
    cli(obj={})
