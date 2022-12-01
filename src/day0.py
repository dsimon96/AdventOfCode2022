import click

import common


@click.command()
@common.common_options
def day0(part: int):
    print(f"Running part {part}")
