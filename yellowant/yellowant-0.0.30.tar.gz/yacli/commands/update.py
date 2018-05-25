"""Create a YellowAnt application with a developer account"""
import json, yaml
import click

from yacli.cli import pass_context
from yacli.constants import APP_FILENAME, DEVELOPER_APPLICATION_ENDPOINT
from yacli.common import read_app_id_from_config, save_app_config, save_application_yaml, \
AppIdInvalid, AppDataCorrupt, FilePermissionError


@click.command()
@click.argument('app')
@click.option("--filename", default=APP_FILENAME, type=click.File("rb"))
@pass_context
def cli(ctx, app, filename):
    """Update an application with your developer account."""
    try:
        ctx.is_auth_valid()

        try:
            app = int(app)
        except:
            app = read_app_id_from_config(app)
        
        if app is None:
            raise AppIdInvalid("Please check if application invoke name details are present in the file: app.yellowant")

        data = yaml.safe_load(filename.read())
        req = ctx.put(DEVELOPER_APPLICATION_ENDPOINT + str(app) + "/", data=json.dumps(data))
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
                save_app_config(application_json["id"], application_json["invoke_name"])
            except:
                raise FilePermissionError("Could not update application data a local file. Please check permissions.")

            ctx.log("Successfully updated application {} with your YellowAnt developer account."
                    .format(application_json["invoke_name"]))
        elif req.status_code == 400:
            error = json.loads(req.text)
            msg = "\nError: Please check your app data JSON.\n"
            print(error)
            for key_name in error:
                msg += key_name + ": " + str(error[key_name][0]) + "\n"
            raise Exception(msg)
        else:
            print(req.text)
            error = json.loads(req.text)
            raise Exception(error["detail"])
    except Exception as e:
        ctx.log(e)

