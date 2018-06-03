import google.auth
from google.auth.transport.requests import AuthorizedSession

credentials, project = google.auth.default(
    'https://www.googleapis.com/auth/rcsbusinessmessaging'
)

http = AuthorizedSession(credentials)  # OAuth wrapper for requests
