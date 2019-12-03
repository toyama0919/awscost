import click


class Validator:

    @staticmethod
    def validate_suffix(ctx, param, value):
        if '-' in value:
            raise click.BadParameter('Do not include "-"')
        else:
            return value
