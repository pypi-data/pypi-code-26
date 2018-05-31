from urlobject import URLObject
import os


ROOT = URLObject(os.environ.get('HOST', 'https://shortesttrack.com'))

UAA_SERVICE_ENDPOINT = ROOT.add_path('api/uaa')
OAUTH_SERVICE_ENDPOINT = ROOT.add_path('oauth')
JWTKEY_ENDPOINT = ROOT.add_path('oauth_jwtkey')
METADATA_SERVICE_ENDPOINT = ROOT.add_path('api/metadata')
