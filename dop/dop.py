#!/usr/bin/env python3

import os

import time
import click
import digitalocean

import config

from formatters import droplet_formatter

SIZES = [
    '512mb',
    '1gb',
    '2gb',
    '4gb',
    '8gb',
    '16gb',
    '32gb',
    '48gb',
    '64gb'
]

REGIONS = [
    'nyc1',
    'nyc2',
    'nyc3',
    'ams1',
    'ams2',
    'ams3',
    'sfo1',
    'sgp1',
    'lon1'
]


DO_MANAGER = digitalocean.Manager(token=config.token)

def check_ssh_keys():
    if len(config.ssh_keys) < 1:
        click.echo("SSH key IDs should be configured. Please read README.MD to fix this issue", err=True)
        exit()


def format_node_name(number, prefix='node', suffix_length=2):
    assert suffix_length > 0
    assert number > 0
    return ("%s%0" + str(suffix_length) + "d") % (prefix, number)


def format_droplet_name_list(droplets):
    return ', '.join([d.name for d in droplets])


def format_droplet_progress_label(action):
    if action == 'create':
        return "Initiating droplet creation"
    elif action == 'destroy':
        return "Initiating droplet destroy"
    else:
        assert False


def format_droplet_confirmation_message_template(action):
    if action == 'create':
        return "Following droplets will be created:\n%s\nProceed?"
    elif action == 'destroy':
        return "Following droplets will be destroyed:\n%s\nProceed?"
    else:
        assert False


def format_droplet_confirmation_message(droplets, action):
    droplet_names = '\n'.join([d.name for d in droplets])
    return format_droplet_confirmation_message_template(action) % droplet_names


def perform_droplet_action(droplet, action):
    time.sleep(0.3)
    if action == 'create':
        droplet.create()
    elif action == 'destroy':
        droplet.destroy()


def perform_action_for_each_droplet(droplets, action, is_yes):

    if len(droplets) < 1:
        click.echo("Nothing to do.")
        return

    confirmation_message = format_droplet_confirmation_message(droplets, action)

    def proceed():
        with click.progressbar(
                droplets,
                label=format_droplet_progress_label(action)) as ds:
            for d in ds:
                perform_droplet_action(d, action)

    if is_yes:
        proceed()
    else:
        if click.confirm(confirmation_message):
            proceed()
        else:
            click.echo("Aborted.")


@click.group()
def cli():
    pass


@cli.group(short_help='droplet management')
def droplet():
    pass


@droplet.command(name='create', short_help='create given number of VMs')
@click.option('-f', '--user-data', 'user_data_file', type=click.Path(exists=True))
@click.option('-p', '--prefix', default='node')
@click.option('-c', '--count', default=1, help='number of VMs')
@click.option(
    '-s',
    '--size',
    default='2gb',
    help='type of VM',
    type=click.Choice(SIZES)
)
@click.option(
    '-r',
    '--region',
    default='ams3',
    help='region of VM',
    type=click.Choice(REGIONS)
)
@click.option(
    '-y',
    '--yes',
    'is_yes',
    is_flag=True,
    flag_value=True,
    help='answer yes for all confirmations')
def droplet_create(user_data_file, prefix, count, size, region, is_yes):
    check_ssh_keys()

    user_data = None

    if user_data_file:
        with open(user_data_file, "r") as user_data_file:
            user_data = user_data_file.read()

    def build_droplet(name):
        return digitalocean.Droplet(
            token=config.token,
            name=name,
            size_slug=size,
            image=config.image,
            region=region,
            ssh_keys=config.ssh_keys,
            private_networking=True,
            user_data=user_data)

    new_droplet_names = [format_node_name(number + 1, prefix) for number in range(count)]
    current_droplet_names = [d.name for d in DO_MANAGER.get_all_droplets()]
    duplicates = list(set(new_droplet_names).intersection(set(current_droplet_names)))
    duplicates.sort()

    if len(duplicates) > 0:
        click.echo("The droplets with following names already exist:\n%s\nAborted." % '\n'.join(duplicates))
        return

    droplets = [build_droplet(name) for name in new_droplet_names]

    perform_action_for_each_droplet(
        droplets,
        'create',
        is_yes)


@droplet.command(name='destroy', short_help='delete previously created VMs')
@click.argument(
    'names',
    nargs=-1,
    type=click.STRING)
@click.option(
    '-a',
    '--all',
    'is_all',
    is_flag=True,
    flag_value=True,
    help='destroy ALL droplets')
@click.option(
    '--id',
    'ids',
    multiple=True,
    type=click.INT,
    help='destroy droplet by id')
@click.option(
    '-p',
    '--prefix',
    'prefixes',
    multiple=True,
    type=click.STRING,
    help='destroy droplet by prefix')
@click.option(
    '-y',
    '--yes',
    'is_yes',
    is_flag=True,
    flag_value=True,
    help='answer yes for all confirmations')
def droplet_destroy(is_all, ids, names, prefixes, is_yes):

    droplets = [
        d
        for d in DO_MANAGER.get_all_droplets()
        if is_all
        or d.id in ids
        or d.name in names
        or any([d.name.startswith(p) for p in prefixes])
    ]
    perform_action_for_each_droplet(
        droplets,
        'destroy',
        is_yes)


@cli.command(name='ssh', help='ssh to droplet')
@click.argument('name', type=click.STRING)
@click.option('-u', '--user', default='root', type=click.STRING)
def droplet_ssh(name, user):
    matched_droplets = [d for d in DO_MANAGER.get_all_droplets() if d.name == name]

    if len(matched_droplets) == 1:
        d = matched_droplets[0]
        os.system("ssh %s@%s" % (user, d.ip_address))
    elif len(matched_droplets) < 1:
        click.echo("Droplet %s not found" % name)


@cli.group(name='list', short_help='various lists')
def list_group():
    pass

@list_group.command(name='droplets', short_help='Show current droplets')
@click.option(
    '-a',
    '--attribute',
    multiple=True,
    default=['name,status'],
    type=click.STRING,
    help='comma separated field list. Possible values: %s' %
         ', '.join(droplet_formatter.attributes))
@click.option(
    '-s',
    '--simple',
    'is_simple',
    is_flag=True,
    flag_value=True,
    type=click.STRING)
def list_droplets(attribute, is_simple):

    attribute_names = [a for line in attribute for a in line.split(',')]

    unknown_attributes = droplet_formatter.unknown_attributes(attribute_names)

    if len(unknown_attributes) > 0:
        click.echo("Unknown droplet attributes(s): %s" % ' '.join(unknown_attributes), err=True)
        return

    style = 'line' if is_simple else 'table'
    rows = [droplet_formatter.format(d, attribute_names, style) for d in DO_MANAGER.get_all_droplets()]

    if is_simple:
        flattened = [cell for row in rows for cell in row]
        click.echo(' '.join(flattened))
    else:
        for row in rows:
            click.echo(' '.join(row))


@list_group.command(name='keys', short_help='Show registered SSH keys')
def list_ssh_keys():
    for key in DO_MANAGER.get_all_sshkeys():
        click.echo("%s (%s)" % (key.name, key.id))

@list_group.command(name='sizes', short_help='Show supported VM sizes')
def list_sizes():
    for v in SIZES:
        click.echo("%s" % v)

@list_group.command(name='regions', short_help='Show supported regions')
def list_regions():
    for v in REGIONS:
        click.echo("%s" % v)


if __name__ == '__main__':
    cli()
