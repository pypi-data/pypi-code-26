"""Pull a YellowAnt application's data into a file"""
import json, yaml
import click

from yacli.cli import pass_context
from yacli.constants import APP_FILENAME, DEVELOPER_APPLICATION_ENDPOINT
from yacli.common import save_app_config, read_app_id_from_config, save_application_yaml, AppIdInvalid, AppDataCorrupt,\
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
            app = int(app)
        except:
            app = read_app_id_from_config(app)

        if app is None:
            raise AppIdInvalid("Please check if application invoke name details are present in the file: app.yellowant")

        req = ctx.get(DEVELOPER_APPLICATION_ENDPOINT + str(app) + "/")

        save_data_from_request(req, ctx)
    except Exception as e:
        ctx.log(e)
