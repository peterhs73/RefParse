#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Bese configuration and command-line interface"""


from refparse.gui import refparse_gui
from refparse.api import RefAPI
import logging
import sys

import click
import yaml
import os

root_logger = logging.getLogger()
cli_logger = logging.getLogger("CLI")

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("[%(levelname)s] %(name)s - %(message)s")
handler.setFormatter(formatter)
root_logger.addHandler(handler)


def handle_exception(exc_type, exc_value, exc_traceback):
    """Track uncaught exception to debug mode"""
    root_logger.debug(
        "Exception Occurred\n", exc_info=(exc_type, exc_value, exc_traceback)
    )


sys.excepthook = handle_exception


# Grab configuration templates

curpath = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(curpath, "config.yaml"), "r") as config:
    format_config = yaml.load(config, Loader=yaml.SafeLoader)
format_list = list(format_config.keys())


# Commend ling options


@click.group()
@click.option(
    "-d/ ", "--debug/--no-debug", default=False, help="toggle debug mode"
)
def cli(debug):
    """Add debug mode"""
    if debug:
        click.echo("Debug Mode")
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)


@click.command()
def gui():
    refparse_gui(format_config)


@click.command()
@click.argument("reference")
@click.option("-f", "--formats", multiple=True, default=format_list)
def parse(reference, formats):
    """Parse reference given target formats

    For multiple formats, use -f tag multiple times
    :param reference string: reference to parse
    :param reference list: list of formats
    """

    for ref_format in formats:
        if ref_format not in format_config:
            cli_logger.error(f"{ref_format} not defined")
            return

    api = RefAPI(reference, format_config)
    results = []
    if api.status:
        for ref_format in formats:
            results.append((ref_format, api.render(ref_format)))

        click.echo("\n--- Output reference --- \n")
        for ref_format, result in results:
            click.echo(f"--- {ref_format}\n")
            click.echo(result)


@click.command()
def show_formats():
    """Show available formats"""
    fromats_ = " ".join(format_list)
    click.echo(f"available formats: {fromats_}")


# add commend the the commend line interface
cli.add_command(gui)
cli.add_command(parse)
cli.add_command(show_formats)
