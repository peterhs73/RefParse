#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Bese configuration and command-line interface"""


from refparse.gui import refparse_gui
from refparse.api import RefAPI
import logging
import sys
from shutil import copyfile
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
    root_logger.error(
        "Exception Occurred\n", exc_info=(exc_type, exc_value, exc_traceback)
    )


sys.excepthook = handle_exception


# Grab configuration templates

CURPATH = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(CURPATH, "config.yaml"), "r") as config:
    FORMAT_CONFIG = yaml.load(config, Loader=yaml.SafeLoader)

USR_DIR = os.path.expanduser("~/.refparse")
USR_PATH = os.path.join(USR_DIR, "user_config.yaml")


def load_user_config():
    """Load user configuration"""
    if os.path.isfile(USR_PATH):
        try:
            with open(USR_PATH, "r") as config:
                user_config = yaml.load(config, Loader=yaml.SafeLoader)
            user_config = user_config or {}
            FORMAT_CONFIG.update(user_config)
        except Exception as e:
            root_logger.warning(
                f"unable to load user configuration due to {str(e)}"
            )


load_user_config()
CONFIG_INSTR_PATH = os.path.join(CURPATH, "user_config.yaml")


# Commend ling options


@click.group()
@click.option(
    "-d/ ", "--debug/--no-debug", default=False, help="Toggle debug mode"
)
def cli(debug):
    """Command-line interface for RefParse"""
    if debug:
        click.echo("Debug mode on")
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)


@click.command()
def gui():
    """Initiate GUI for refparse"""
    refparse_gui(FORMAT_CONFIG)


@click.command()
@click.argument("editor", default="vim")
def config(editor):
    """Configure reference templates

    EDITOR defaults to vim, depends on the platform other editor can be
    used. e.g. nano. If no existing configuration file exists,
    a new file is created ~/.refparse/user_config.yaml
    """
    if not os.path.isfile(USR_PATH):
        os.makedirs(USR_DIR, exist_ok=True)
        copyfile(CONFIG_INSTR_PATH, USR_PATH)
    click.edit(editor=editor, extension=".yaml", filename=USR_PATH)
    load_user_config()


@click.command()
@click.argument("reference")
@click.option(
    "-f",
    "--formats",
    multiple=True,
    default=list(FORMAT_CONFIG.keys()),
    help="Output template format",
)
def parse(reference, formats):
    """Parse reference given target formats

    REFERENCE is doi or arXiv ID of intended article
    """

    for ref_format in formats:
        if ref_format not in FORMAT_CONFIG:
            cli_logger.error(f"{ref_format} not defined")
            return

    api = RefAPI(reference, FORMAT_CONFIG)
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
    fromats_ = " ".join(list(FORMAT_CONFIG.keys()))
    click.echo(f"available formats: {fromats_}")


# add commend the the commend line interface
cli.add_command(gui)
cli.add_command(parse)
cli.add_command(config)
cli.add_command(show_formats)
