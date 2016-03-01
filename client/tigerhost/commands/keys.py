import click
import os

from tigerhost.api_client import ApiClientResponseError
from tigerhost.utils import decorators


@click.command()
@click.argument('name')
@click.argument('path', default='~/.ssh/id_rsa.pub')
@click.option('--provider', '-p', required=True, help='The provider to add this key to.')
@decorators.print_markers
@decorators.catch_exception(ApiClientResponseError)
@decorators.catch_exception(IOError)
@decorators.store_api_client
@click.pass_context
def add_key(ctx, name, path, provider):
    """Add a public key. The NAME is the human readable label to attach
    to this key. PATH is the path to the public key, defaulting to
    ~/.ssh/id_rsa.pub.
    """
    api_client = ctx.obj['api_client']
    path = os.path.expanduser(path)
    with open(path, 'r') as f:
        key = f.read()
    api_client.add_key(name, key, provider)
    click.echo('Added key {} to {}.'.format(name, provider))


def _truncate(text):
    length = 20
    dots = '...'
    if len(text) > length * 2 + len(dots):
        return text[:length] + dots + text[-length:]
    else:
        return text


@click.command()
@decorators.print_markers
@decorators.catch_exception(ApiClientResponseError)
@decorators.store_api_client
@click.pass_context
def list_keys(ctx):
    """Show the list of keys for this user.
    """
    api_client = ctx.obj['api_client']
    first = True
    for provider, keys in api_client.get_keys().iteritems():
        if first:
            first = False
        else:
            click.echo()
        click.echo('Provider: {}'.format(provider))
        content = '\n'.join(
            ['{}\n{}'.format(key['key_name'], key['key']) for key in keys])
        click.echo(content)


@click.command()
@click.argument('name')
@click.option('--provider', '-p', required=True, help='The provider to remove this key from.')
@decorators.print_markers
@decorators.catch_exception(ApiClientResponseError)
@decorators.catch_exception(IOError)
@decorators.store_api_client
@click.pass_context
def remove_key(ctx, name, provider):
    """Removes the key with label NAME.
    """
    api_client = ctx.obj['api_client']
    api_client.remove_key(name, provider)
    click.echo('Key {} removed from {}.'.format(name, provider))
