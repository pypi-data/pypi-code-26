"""Pull a YellowAnt application's data into a file"""
import json, yaml
import click

from yacli.cli import pass_context
from yacli.constants import APP_FILENAME, DEVELOPER_APPLICATION_ENDPOINT
from yacli.common import save_app_config, read_app_id_from_config, save_application_yaml, AppIdInvalid, AppDataCorrupt,\
FilePermissionError





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
        if req.status_code == 200:
            try:
                application_json = json.loads(req.content)
            except:
                raise AppDataCorrupt("Application data could not be parsed.")

            # client_id = application_json.get("client_id", None)
            # client_secret = application_json.get("client_secret", None)
            # if client_id is None or client_secret is None:
            #     raise AppDataCorrupt("Application data is incomplete.")
            # ctx.log("\nCLIENT ID: " + client_id)
            # ctx.log("CLIENT SECRET: " + client_secret)
            
            try:
                save_application_yaml(application_json)
            except:
                raise FilePermissionError("Could not save application data a local file. Please check permissions.")
            
            ctx.log("Successfully saved application data to {}".format(filename))

            save_app_config(application_json["id"], application_json["invoke_name"])
        else:
            print(req.text)
            raise Exception("Either your auth credentials are incorrect, " +
                            "or the application could not be found.")
    except Exception as e:
        ctx.log(e)
