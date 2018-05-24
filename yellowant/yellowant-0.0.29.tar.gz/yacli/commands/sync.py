import click
import json, yaml

from yacli.cli import pass_context
from yacli.constants import APP_FILENAME, DEVELOPER_APPLICATION_SYNC_ENDPOINT
from yacli.common import save_app_config, save_application_yaml, AppDataCorrupt, FilePermissionError


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

        if str(req.status_code).startswith("2"):
            # application was created or updated
            try:
                application_json = json.loads(req.content)
            except:
                raise AppDataCorrupt("Application data could not be parsed.")
            
            # log client ID and secret to console and save them in a json
            try:
                application_id = application_json.pop("id")
                client_id = application_json.pop("client_id")
                client_secret = application_json.pop("client_secret")
                verification_token = application_json.pop("verification_token")
                rtm_token = application_json.pop("rtm_token")
            except:
                raise AppDataCorrupt("Application data is incomplete.")
            # log values
            ctx.log("APP ID: " + application_id)
            ctx.log("CLIENT ID: " + client_id)
            ctx.log("CLIENT SECRET: " + client_secret)
            ctx.log("VERIFICATION TOKEN: " + verification_token)
            ctx.log("RTM TOKEN: " + rtm_token)
            # save credentials json
            credentials = {
                "application_id": application_id,
                "client_id": client_id,
                "invoke_name": application_json["invoke_name"],
                "client_secret": client_secret,
                "verification_token": verification_token,
                "rtm_token": rtm_token
            }
            try:
                with open("yellowant_app_credentials.json", "w") as credentials_json:
                    json.dump(credentials, credentials_json, indent=4, sort_keys=True)
            except:
                raise FilePermissionError("Could not save credentials information properly.")
            
            # save app YAML and config details
            try:
                save_application_yaml(application_json)
                # save_app_config(application_id, application_json["invoke_name"])
            except Exception as e:
                raise FilePermissionError("Could not save application data a local file. Please check permissions.")

            # log final message to user
            action = "created" if req.status_code == 201 else "updated"
            ctx.log("Successfully {} application {} with your YellowAnt developer account."
                    .format(action, application_json["invoke_name"]))

        elif req.status_code == 400:
            # there was an error in the application data
            error = json.loads(req.text)
            msg = "\nError: Please check your app data JSON.\n"
            for key_name in error:
                msg += key_name + ": " + str(error[key_name][0]) + "\n"
            raise Exception(msg)
        else:
            # some other error
            error = json.loads(req.text)
            raise Exception(error["detail"])
    except Exception as e:
        ctx.log(e)
