import os
import click

# Digital Ocean personal access token
token = os.environ.get('DIGITAL_OCEAN_TOKEN')

if not token:
    click.echo("The DO API token should be configured. Please read README.MD to fix this issue", err=True)
    exit()

# Digital Ocean SSH key ID (obtainable using DO API or checking source code of
# https://cloud.digitalocean.com/ssh_keys page)
ssh_keys = [
    int(key_id.strip())
    for key_id in os.environ.get('DIGITAL_OCEAN_SSH_KEYS', '').split(',')
    if key_id
]

# Delay between checks whether VMs have booted
delay = 5  # seconds

image = 'ubuntu-14-04-x64'
