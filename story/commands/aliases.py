# -*- coding: utf-8 -*-
import os
import sys

from blindspin import spinner

import click

import emoji

from .. import api
from .. import awesome
from .. import cli

@cli.cli.command()
@click.argument('name', nargs=1, required=False)
@click.option(
    '--team', type=str, help='Team name that owns this new Application'
)
def create(name, team):
    """Create a new app."""
    create_helper(name, team)


def create_helper(name, team):
    cli.user()
    story_yaml = cli.find_story_yml()

    if story_yaml is not None:
        click.echo(
            click.style(
                'There appears to be an Storyscript Cloud project in '
                f'{story_yaml} already.\n',
                fg='red',
            )
        )
        click.echo(
            click.style(
                'Are you trying to deploy? ' 'Try the following:', fg='red'
            )
        )
        click.echo(click.style('$ story deploy', fg='magenta'))
        sys.exit(1)

    name = name or awesome.new()

    # Sanity check.
    if len(name) < 4:
        click.echo(
            click.style(
                'The name you specified is too short. \n'
                'Please use at least 4 characters in your app name.',
                fg='red',
            )
        )
        sys.exit(1)

    click.echo('Creating application… ', nl=False)

    with spinner():
        api.Apps.create(name=name, team=team)

    click.echo(
        '\b' + click.style(emoji.emojize(':heavy_check_mark:'), fg='green')
    )

    click.echo('Creating story.yml… ', nl=False)
    cli.settings_set(f'app_name: {name}\n', 'story.yml')

    click.echo(
        '\b' + click.style(emoji.emojize(':heavy_check_mark:'), fg='green')
    )

    click.echo('\nApp Name: ' + click.style(name, bold=True))
    click.echo(
        'App URL: '
        + click.style(f'https://{name}.storyscriptapp.com/', fg='blue')
        + '\n'
    )

    click.echo(
        'You are now ready to write your first Storyscript! '
        f'{emoji.emojize(":party_popper:")}'
    )
    click.echo()

    cli.track('App Created', {'App name': name})

    click.echo(' - [ ] Write a Story:')
    click.echo(
        '       $ '
        + click.style('story write http > http.story', fg='magenta')
    )
    click.echo()
    click.echo(' - [ ] Deploy to Storyscript Cloud:')
    click.echo('       $ ' + click.style('story deploy', fg='magenta'))
    click.echo()
    click.echo('We hope you enjoy your deployment experience!')