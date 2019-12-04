import click
from datetime import datetime


class Validator:

    @staticmethod
    def validate_dateformat(ctx, param, value):
        try:
            datetime.strptime(value, '%Y-%m-%d')
        except:
            raise click.BadParameter(f"please input dateformat parameter. ('%Y-%m-%d')")
        return value
