import json
from yacli.common import AppDataCorrupt, FilePermissionError, save_application_yaml


def save_data_from_request(request, ctx):
    if str(request.status_code).startswith("2"):
        # application was created or updated
        try:
            try: # python 2.7 or >=3.6
                application_json = json.loads(request.content)
            except: # python 3.4 and 3.5
                application_json = json.loads(str(request.content, "utf-8"))
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
        ctx.log("APP ID: " + str(application_id))
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
        action = "created" if request.status_code == 201 else "updated"
        ctx.log("Successfully {} application {} with your YellowAnt developer account."
                .format(action, application_json["invoke_name"]))
    elif request.status_code == 400:
        # there was an error in the application data
        try:
            # try to parse JSON error data
            error = json.loads(request.text)
            msg = "\nError: Please check your app data JSON.\n"
            for key_name in error:
                msg += key_name + ": " + str(error[key_name][0]) + "\n"
            raise Exception(msg)
        except:
            # error is just in plain text
            raise Exception(request.text)
    else:
        # some other error
        try:
            error = json.loads(request.text)
            raise Exception(error["detail"])
        except:
            error = request.text
            raise Exception(error)