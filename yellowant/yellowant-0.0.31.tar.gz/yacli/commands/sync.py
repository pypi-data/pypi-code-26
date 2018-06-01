import click
import json, yaml

from yacli.cli import pass_context
from yacli.constants import APP_FILENAME, DEVELOPER_APPLICATION_SYNC_ENDPOINT
from yacli.common import save_app_config, save_application_yaml, AppDataCorrupt, FilePermissionError
from yacli.helpers.save_data_from_request import save_data_from_request


@click.command()
@click.option("--invoke_name", type=click.STRING, help="Unique name to invoke the app.")
@click.option("--website", type=click.STRING, help="Website of the app.")
@click.option("--api_url", type=click.STRING, help="API endpoint through which YellowAnt interacts with this app.")
@click.option("--install_page_url", type=click.STRING, help="Web URL through which users can integrate this app.")
@click.option("--privacy_policy_url", type=click.STRING, help="Web URL for the privacy policy of this app.")
@click.option("--redirect_uris", type=click.STRING, help="Redirect URI at which YellowAnt will provide OAuth tokens.")
@click.option("--quiet", "-q", is_flag=True, default=False, help="Do not prompt for inputs.")
@click.option("--filename", default=APP_FILENAME, type=click.File("rb"), help="App YAML file name.")
@pass_context
def cli(ctx, invoke_name, website, api_url, install_page_url, privacy_policy_url, redirect_uris, quiet, filename):
    """Create or update an application on YellowAnt"""
    # check permissions
    ctx.is_auth_valid()

    try:
        # load data from YAML file
        data = yaml.safe_load(filename.read())

        # check if no prompt is required from the user
        if quiet is True:
            data["invoke_name"] = invoke_name or data.get("invoke_name")
            data["website"] = website or data.get("website")
            data["api_url"] = api_url or data.get("api_url")
            data["install_page_url"] = install_page_url or data.get("install_page_url")
            data["privacy_policy_url"] = privacy_policy_url or data.get("privacy_policy_url")
            data["redirect_uris"] = redirect_uris or data.get("redirect_uris")
        else:
            data["invoke_name"] = invoke_name or click.prompt("Invoke Name", default=data.get("invoke_name"))
            data["website"] = website or click.prompt("Website", default=data.get("website"))
            data["api_url"] = api_url or click.prompt("API URL", default=data.get("api_url"))
            data["install_page_url"] = install_page_url or click.prompt("Installation URL", default=data.get("install_page_url"))
            data["privacy_policy_url"] = privacy_policy_url or click.prompt("Privacy Policy URL", default=data.get("privacy_policy_url"))
            data["redirect_uris"] = redirect_uris or click.prompt("Redirect URL", default=data.get("redirect_uris"))
        
        # send request to API
        req = ctx.post(DEVELOPER_APPLICATION_SYNC_ENDPOINT, data=json.dumps(data))

        save_data_from_request(req, ctx)
    except Exception as e:
        ctx.log(e)
