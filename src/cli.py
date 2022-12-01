from glob import glob
from importlib import import_module
from os.path import dirname
from types import ModuleType
from typing import List

import click

# Dynamic imports are an ugly and unsafe hack, but this is for my use only. This
# matches day*.py files in the same directory as this file.
sol_modules: List[ModuleType] = []
for filename in glob("day*.py", root_dir=dirname(__file__)):
    sol_modules.append(import_module(filename[:-3]))


@click.group()
def cli():
    pass


# Programmatically discover and register click commands in the solution modules
for sol_module in sol_modules:
    for cls in sol_module.__dict__.values():
        if isinstance(cls, click.core.Command):
            cli.add_command(cls)
