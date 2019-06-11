import json
import os
import sys

from blindspin import spinner
import click
import emoji

from .. import cli
from .. import api


def load_json(path):
    try:
        with open(os.path.expanduser(path)) as f:
            config = json.load(f)
    except (FileNotFoundError, IsADirectoryError):
        click.echo(
            click.style(f"The file {path} does not exist", fg='red'), err=True
        )
        sys.exit(1)
    except json.decoder.JSONDecodeError:
        click.echo(
            click.style(f"The file {path} is not valid JSON", fg='red'),
            err=True,
        )
        sys.exit(1)
    return config


@cli.cli.group()
def containers():
    """
    Manage the container configs used by the
    Storyscript platform for authorization
    """
    pass


@containers.command(name='list')
def list_command():
    """List all container configs that you have access to"""
    with spinner():
        res = api.ContainerConfig.list()
    if len(res) == 0:
        click.echo("No container configs found. Create a new one with")
        click.echo(click.style('$ story containers create', fg='magenta'))
    for config in res:
        click.echo(config['name'])


@containers.command()
@click.argument('name', nargs=1)
def get(name):
    """Get a container config by name"""
    with spinner():
        res = api.ContainerConfig.get(name)
    click.echo(json.dumps(res, indent=4))


@containers.command()
@click.argument('name', nargs=1)
@click.argument('path', nargs=1)
@click.option(
    '--team', type=str, help='Team name that owns this new container config'
)
def create(name, path, team):
    """Create a new container config"""
    config = load_json(path)
    with spinner():
        api.ContainerConfig.create(name, config)
    click.echo(
        click.style('\b' + emoji.emojize(':heavy_check_mark:'), fg='green')
        + f' Created container config - {name}'
    )


@containers.command()
@click.argument('name', nargs=1)
@click.argument('path', nargs=1)
def update(name, path):
    """Update a container config by name"""
    config = load_json(path)
    with spinner():
        api.ContainerConfig.update(name, config)
    click.echo(
        click.style('\b' + emoji.emojize(':heavy_check_mark:'), fg='green')
        + f' Updated container config - {name}'
    )


@containers.command()
@click.argument('name', nargs=1)
def delete(name):
    """Delete a container config by name"""
    with spinner():
        api.ContainerConfig.delete(name)
    click.echo(
        click.style('\b' + emoji.emojize(':heavy_check_mark:'), fg='green')
        + f' Deleted container config - {name}'
    )
