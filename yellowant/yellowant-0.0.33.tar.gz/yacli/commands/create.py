"""Create a YellowAnt application with a developer account"""
import json, yaml
import click

from yacli.cli import pass_context
from yacli.constants import APP_FILENAME, DEVELOPER_APPLICATION_ENDPOINT
from yacli.common import save_app_config, save_application_yaml, AppIdInvalid, AppDataCorrupt, FilePermissionError


@click.command()
@click.option("--filename", default=APP_FILENAME, type=click.File("rb"))
@pass_context
def cli(ctx, filename):
    """Create an application with your developer account."""
    ctx.is_auth_valid()
    try:
        data = yaml.safe_load(filename.read())
        data["invoke_name"] = click.prompt("Invoke Name", default=data.get("invoke_name"))
        data["website"] = click.prompt("Website", default=data.get("website"))
        data["api_url"] = click.prompt("API URL", default=data.get("api_url"))
        data["install_page_url"] = click.prompt("Installation URL", default=data.get("install_page_url"))
        data["privacy_policy_url"] = click.prompt("Privacy Policy URL", default=data.get("privacy_policy_url"))
        data["redirect_uris"] = click.prompt("Redirect URL", default=data.get("redirect_uris"))
        req = ctx.post(DEVELOPER_APPLICATION_ENDPOINT, data=json.dumps(data))
        if req.status_code == 201:
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
            except Exception as e:
                print(e)
                raise FilePermissionError("Could not save application data a local file. Please check permissions.")

            ctx.log("Successfully created application {} with your YellowAnt developer account."
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

