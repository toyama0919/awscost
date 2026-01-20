from datetime import datetime

import click


class Validator:
    @staticmethod
    def validate_dateformat(ctx, param, value):
        if value is None:
            return value

        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise click.BadParameter("please input dateformat parameter. ('%Y-%m-%d')")
        return value
