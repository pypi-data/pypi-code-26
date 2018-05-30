import os
from django.conf import settings

settings.WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'bundles/',
        'STATS_FILE': os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'webpack-stats.json'
        ),
    }
}
