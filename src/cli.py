import logging
from importlib import import_module
from types import ModuleType
from typing import Callable, TextIO

import click


def get_mod(n: int) -> ModuleType:
    return import_module(f"day{n}")


def get_sol(day: int, part: int) -> Callable[[TextIO], int]:
    return getattr(get_mod(day), f"part{part}")


@click.command()
@click.option("-d", "--day", required=True, type=int)
@click.option("-p", "--part", required=True, type=int)
@click.option("-v", "--verbose", is_flag=True, type=bool)
@click.argument("input", type=click.File(mode="r"))
def cli(day: int, part: int, verbose: bool, input: TextIO):
    logging.basicConfig(level=logging.DEBUG if verbose else logging.WARNING)
    if verbose:
        logging.info("Enabling verbose logging")
    print(get_sol(day, part)(input))
