#!/usr/bin/env python
# coding: utf-8 -*-

"""
Commands for Anta CLI to execute EOS commands.
"""

import asyncio
import logging
import sys
from datetime import datetime

import click
from yaml import safe_load

from anta.cli.exec.utils import clear_counters_utils, collect_commands, collect_scheduled_show_tech
from anta.cli.utils import setup_logging
from anta.inventory import AntaInventory
from anta.inventory.models import DEFAULT_TAG

logger = logging.getLogger(__name__)


@click.command()
@click.pass_context
# Generic options
@click.option('--tags', '-t', default='all', help='List of tags using coma as separator: tag1,tag2,tag3', type=str)
# Debug stuf
@click.option('--log-level', '--log', help='Logging level of the command', default='info',
              type=click.Choice(['debug', 'info', 'warning', 'critical'], case_sensitive=False))
def clear_counters(ctx: click.Context, log_level: str, tags: str) -> None:
    """Clear counter statistics on EOS devices"""

    setup_logging(level=log_level)

    inventory_anta = AntaInventory(
        inventory_file=ctx.obj['inventory'],
        username=ctx.obj['username'],
        password=ctx.obj['password'],
        enable_password=ctx.obj['enable_password']
    )
    asyncio.run(clear_counters_utils(
        inventory_anta, ctx.obj['enable_password'], tags=tags.split(','))
        )


def _get_snapshot_dir(ctx: click.Context, param: click.Parameter, value: str) -> str:  # pylint: disable=unused-argument
    """Build directory name for command snapshots, including current time"""
    return f"{value}_{datetime.today().strftime('%Y-%m-%d_%H%M%S')}"


@click.command()
@click.pass_context
# Generic options
@click.option('--tags', '-t', default=DEFAULT_TAG, help='List of tags using coma as separator: tag1,tag2,tag3', type=str)
@click.option('--commands-list', '-c', show_envvar=True, type=click.Path(), help='File with list of commands to grab', required=True)
@click.option('--output-directory', '-output', '-o', show_envvar=True, type=click.Path(), help='Path where to save commands output',
              default='anta_snapshot', callback=_get_snapshot_dir)
# Debug stuf
@click.option('--log-level', '--log', help='Logging level of the command', default='info',
              type=click.Choice(['debug', 'info', 'warning', 'critical'], case_sensitive=False))
def snapshot(ctx: click.Context, commands_list: str, log_level: str, output_directory: str, tags: str) -> None:
    """Collect commands output from devices in inventory"""
    setup_logging(level=log_level)
    try:
        with open(commands_list, "r", encoding="UTF-8") as file:
            file_content = file.read()
            eos_commands = safe_load(file_content)
    except FileNotFoundError:
        logger.error(f"Error reading {commands_list}")
        sys.exit(1)
    inventory = AntaInventory(
        inventory_file=ctx.obj['inventory'],
        username=ctx.obj['username'],
        password=ctx.obj['password'],
        enable_password=ctx.obj['enable_password']
    )
    asyncio.run(collect_commands(inventory, ctx.obj['enable_password'],
                eos_commands, output_directory, tags=tags.split(',')))


@click.command()
@click.pass_context
@click.option('--output', '-o', default='./tech-support', help='Path for tests catalog', type=click.Path(), required=False)
@click.option('--ssh-port', '-ssh', default=22, help='SSH port to use for connection', type=int, required=False)
@click.option('--insecure/--secure', help='Disable SSH Host Key validation', default=False, required=False)
@click.option('--configure/--not-configure', help="Ensure device has 'aaa authorization exec default local' configured (required for SCP)", default=False,
              required=False)
@click.option('--tags', '-t', default=DEFAULT_TAG, help='List of tags using coma as separator: tag1,tag2,tag3', type=str, required=False)
# Debug stuf
@click.option('--log-level', '--log', help='Logging level of the command', default='info',
              type=click.Choice(['debug', 'info', 'warning', 'critical'], case_sensitive=False))
def collect_tech_support(ctx: click.Context, output: str, ssh_port: int, insecure: bool,  # pylint: disable=too-many-arguments
                         configure: bool, log_level: str, tags: str) -> bool:
    """Collect scheduled tech-support from eos devices."""
    setup_logging(level=log_level)
    inventory = AntaInventory(
        inventory_file=ctx.obj['inventory'],
        username=ctx.obj['username'],
        password=ctx.obj['password'],
        enable_password=ctx.obj['enable_password']
    )
    asyncio.run(collect_scheduled_show_tech(inventory, ctx.obj['enable_password'], output, tags.split(','),
                                            ssh_port, insecure, configure))
    return True
