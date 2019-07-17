# -*- coding: utf-8 -*-
import base64
import json
import os
import sys

from blindspin import spinner

import click

import emoji

from .. import api
from .. import cli


DOCKER_HUB_REGISTRY_URL = 'https://index.docker.io/v1/'


def load_json_file(path, kill=True):
    exception = False
    try:
        with open(os.path.expanduser(path)) as f:
            data = json.load(f)
    except (FileNotFoundError, IsADirectoryError):
        click.echo(click.style(
            f'The file {path} does not exist',
            fg='red'), err=True)
        exception = True
    except json.decoder.JSONDecodeError:
        click.echo(click.style(
            f'The file {path} is not valid JSON',
            fg='red'), err=True)
        exception = True
    finally:
        if exception:
            if kill:
                sys.exit(1)
            else:
                return None
    return data


def generate_config(registry_url, username, password):
    return {
        'auths': {
            registry_url: {
                'auth': base64.b64encode(
                    f'{username}:{password}'.encode()
                ).decode()
            }
        }
    }


def generate_docker_login_config():
    registry_url = click.prompt('Registry URL', type=str,
                                default=DOCKER_HUB_REGISTRY_URL)
    username = click.prompt('Username', type=str)
    password = click.prompt('Password', type=str, hide_input=True)
    return generate_config(registry_url, username, password)


def generate_gcr_config():
    hostname = click.prompt('Hostname', type=click.Choice([
        'gcr.io', 'us.gcr.io', 'eu.gcr.io', 'asia.gcr.io'
    ]))
    json_key = None
    while json_key is None:
        json_key_path = click.prompt('Path to service Account JSON key file',
                                     type=str)
        json_key = load_json_file(json_key_path, kill=False)

    return generate_config(f'https://{hostname}', '_json_key', json_key)


def get_config_interactive():
    click.echo("Use type 'docker_login' for "
               'registries that authenticate via `$ docker login`')
    click.echo()
    click.echo('Defaults are set to Docker Hub')
    click.echo()
    registry_type = click.prompt(
        'Registry Type',
        type=click.Choice(['docker_login', 'gcr']),
        default='docker_login'
    )
    if registry_type == 'docker_login':
        return generate_docker_login_config()
    elif registry_type == 'gcr':
        return generate_gcr_config()


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
    hidden=True
)
@click.option(
    '--team', type=str, help='Team name that owns this new registry config'
)
def create(name, file, team):
    """Create a new registry config"""

    if file:
        config = load_json_file(file)
    else:
        config = get_config_interactive()

    with spinner():
        api.Registry.create(name, config)
    click.echo()
    click.echo(click.style('\b' + emoji.emojize(':heavy_check_mark:'),
                           fg='green') + f' Created registry config - {name}')


@registry.command()
@click.option(
    '-n', '--name', type=str, help='Name of the registry config',
    required=True
)
@click.option(
    '-f', '--file', type=str, help='Path of the registry config json file',
    hidden=True
)
def update(name, file):
    """Update a registry config"""

    if file:
        config = load_json_file(file)
    else:
        config = get_config_interactive()

    with spinner():
        api.Registry.update(name, config)
    click.echo()
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
