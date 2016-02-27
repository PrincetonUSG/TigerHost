import click

from tigerhost import settings
from tigerhost.api_client import ApiClientResponseError
from tigerhost.utils import decorators


@click.command()
@decorators.print_markers
@decorators.catch_exception(ApiClientResponseError)
@decorators.store_api_client
@click.pass_context
def list_apps(ctx):
    """List apps for this user

    @type api_client: tigerhost.api_client.ApiClient
    """
    api_client = ctx.obj['api_client']
    apps = api_client.get_all_applications()
    for app in apps:
        click.echo(app)


@click.command()
@click.argument('name')
@decorators.print_markers
@decorators.catch_exception(ApiClientResponseError)
@decorators.store_api_client
@decorators.store_vcs
@click.pass_context
def create_app(ctx, name):
    """Create a new app with the specified NAME.
    """
    vcs = ctx.obj['vcs']
    api_client = ctx.obj['api_client']
    api_client.create_application(name)
    click.echo('App {} created.'.format(name))
    click.echo()
    if vcs is not None:
        try:
            remote = api_client.get_application_git_remote(name)
        except ApiClientResponseError:
            click.echo('''Cannot connect to the server to retrieve git remote URL. To add git remote to your project manually, run the following command:

    {app_name} git:remote --app {name}'''.format(
                app_name=settings.APP_NAME, name=name))
            return
        cur_remotes = vcs.get_remotes()
        if settings.APP_NAME in cur_remotes:
            click.echo('''An existing git remote named {app_name} already exists:

    {url}

This can happen if you created multiple {app_name} apps for your project.'''.format(app_name=settings.APP_NAME, url=cur_remotes[settings.APP_NAME]))
            if not click.confirm('Replace?'):
                click.echo('''To add git remote to your project manually, run the following command:

    {app_name} git:remote --app {name} --remote REMOTE_NAME'''.format(app_name=settings.APP_NAME, name=name))
                return
            else:
                vcs.remove_remote(settings.APP_NAME)
        vcs.add_remote(settings.APP_NAME, remote)
        click.echo('Successfully set remote {app_name} to {url}'.format(
            app_name=settings.APP_NAME, url=remote))
    else:
        click.echo('''Not in a git repository. To add git remote to your project manually, run the following command inside your project repository.

    {app_name} git:remote --app {name}'''.format(
            app_name=settings.APP_NAME, name=name))


@click.command()
@decorators.print_markers
@decorators.catch_exception(ApiClientResponseError)
@decorators.store_api_client
@decorators.store_app
@click.pass_context
def destroy_app(ctx):
    """Delete the current application.
    """
    app = ctx.obj['app']
    api_client = ctx.obj['api_client']
    api_client.delete_application(app)
    click.echo('App {} destroyed.'.format(app))
