"""Pull a YellowAnt application's data into a file"""
import json, yaml
import click

from yacli.cli import pass_context
from yacli.constants import APP_FILENAME, DEVELOPER_APPLICATION_ENDPOINT, DEVELOPER_APPLICATION_PULL_ENDPOINT
from yacli.common import save_app_config, save_application_yaml, AppIdInvalid, AppDataCorrupt,\
FilePermissionError
from yacli.helpers.save_data_from_request import save_data_from_request




@click.command()
@click.argument('app')
@click.option("--filename", default=APP_FILENAME, type=click.Path())
@pass_context
def cli(ctx, app, filename):
    """Pull application data from host in JSON format. Either provide application id or invoke name as argument."""
    try:
        ctx.is_auth_valid()

        try:
            # check if integer ID of application is passed
            app = int(app)
            req = ctx.get(DEVELOPER_APPLICATION_ENDPOINT + str(app) + "/")
        except:
            # check if app invoke name is passed
            app = app
            print("invoke name")
            req = ctx.get(DEVELOPER_APPLICATION_PULL_ENDPOINT + "?app=" + app)

        save_data_from_request(req, ctx)
    except Exception as e:
        ctx.log(e)
