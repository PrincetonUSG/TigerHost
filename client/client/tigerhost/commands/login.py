import click
import urlparse

from tigerhost import settings
from tigerhost.api_client import ApiClient, ApiClientAuthenticationError, ApiClientResponseError
from tigerhost.user import User, save_user
from tigerhost.utils import decorators


_api_key_url = urlparse.urljoin(settings.API_SERVER_URL, 'api/api_key/')


@click.command()
@click.pass_context
@click.option('--username', '-u', default=None, help='Your username (netID)', type=str)
@click.option('--api-key', '-a', default=None, help='The API key optained from {}'.format(_api_key_url), type=str)
@decorators.print_markers
@decorators.catch_exception(ApiClientResponseError)
def login(ctx, username, api_key):
    """Logs the user in by asking for username and api_key
    """
    if username is None:
        username = click.prompt('Username (netID)')
        click.echo()
    if api_key is None:
        click.echo('Please get your API key from ' +
                   click.style(_api_key_url, underline=True))
        api_key = click.prompt('API key')
        click.echo()
    click.echo('Checking your credentials...', nl=False)

    client = ApiClient(api_server_url=settings.API_SERVER_URL,
                       username=username, api_key=api_key)
    try:
        client.test_api_key()
    except ApiClientAuthenticationError:
        click.secho('invalid', bg='red', fg='black')
        ctx.fail('Please try again')
    else:
        click.secho('OK', bg='green', fg='black')
        user = User(username=username, api_key=api_key)
        save_user(user)
