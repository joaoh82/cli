# -*- coding: utf-8 -*-
import json
import os
import sys

from blindspin import spinner

import click

import emoji

from .. import api
from .. import cli


def load_json(path):
    try:
        with open(os.path.expanduser(path)) as f:
            config = json.load(f)
    except (FileNotFoundError, IsADirectoryError):
        click.echo(click.style(
            f'The file {path} does not exist',
            fg='red'), err=True)
        sys.exit(1)
    except json.decoder.JSONDecodeError:
        click.echo(click.style(
            f'The file {path} is not valid JSON',
            fg='red'), err=True)
        sys.exit(1)
    return config


@cli.cli.group()
def registry():
    """
    Manage the registry configs used by Storyscript Cloud
    """
    pass


@registry.command(name='list')
def list_command():
    """List all registry configs that you have access to"""
    with spinner():
        res = api.Registry.list()
    if len(res) == 0:
        click.echo('No registry configs found. Create a new one with')
        click.echo(click.style('$ story registry create', fg='magenta'))
    for config in res:
        click.echo(config['name'])


@registry.command()
@click.option(
    '-n', '--name', type=str, help='Name of the registry config',
    required=True
)
def get(name):
    """Get a registry config"""
    with spinner():
        res = api.Registry.get(name)
    click.echo(json.dumps(res, indent=4))


@registry.command()
@click.option(
    '-n', '--name', type=str, help='Name of the registry config',
    required=True
)
@click.option(
    '-f', '--file', type=str, help='Path of the registry config json file',
    required=True
)
@click.option(
    '--team', type=str, help='Team name that owns this new registry config'
)
def create(name, file, team):
    """Create a new registry config"""
    config = load_json(file)
    with spinner():
        api.Registry.create(name, config)
    click.echo(click.style('\b' + emoji.emojize(':heavy_check_mark:'),
                           fg='green') + f' Created registry config - {name}')


@registry.command()
@click.option(
    '-n', '--name', type=str, help='Name of the registry config',
    required=True
)
@click.option(
    '-f', '--file', type=str, help='Path of the registry config json file',
    required=True
)
def update(name, file):
    """Update a registry config"""
    config = load_json(file)
    with spinner():
        api.Registry.update(name, config)
    click.echo(click.style('\b' + emoji.emojize(':heavy_check_mark:'),
                           fg='green') + f' Updated registry config - {name}')


@registry.command()
@click.option(
    '-n', '--name', type=str, help='Name of the registry config',
    required=True
)
def delete(name):
    """Delete a registry config"""
    with spinner():
        api.Registry.delete(name)
    click.echo(click.style('\b' + emoji.emojize(':heavy_check_mark:'),
                           fg='green') + f' Deleted registry config - {name}')
