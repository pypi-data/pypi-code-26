from werkzeug.utils import redirect
from flask import url_for, request

from myslx import config


def has_roles(user_roles, required_roles):
    # Falls die Liste der required_roles leer oder None ist True zurück geben
    if not required_roles:
        return True

    for required_role in required_roles:
        # Überprüft ob die Aktuelle rolle in den User Rollen vorhanden ist
        if required_role in user_roles:
            # Falls auch nur eine der Rollen vorhanden ist Return True
            return True

    # Falls keine der Rollen vorhanden ist Return false
    return False


def redirect_to_login():
    uri = url_for('myslx.callback', next=request.url, _external=True)
    return redirect(
        f"https://{config.PORTAL_DOMAIN}/auth/oauth/authorize?client_id={config.OAUTH_CLIENT_ID}&response_type=code&redirect_uri={uri}"
    )
