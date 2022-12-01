from typing import Callable, TypeVar

import click

T = TypeVar("T")


def common_options(f: Callable[..., T]) -> Callable[..., T]:
    f = click.option("-p", "--part", required=True, type=click.IntRange(min=1, max=2))(
        f
    )
    return f
