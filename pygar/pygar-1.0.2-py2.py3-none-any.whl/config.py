#
# pygaR
#
# Author: Brad Cable
# Email: brad@bcable.net
# License: MIT
#

import os

CACHE_TIMEOUT=600
CACHE_RETRIES=3
DEFAULT_ENCODING='iso8859-1'

CACHE_PATH=os.path.join(os.path.expanduser('~'), 'pygar_cache')

EDGAR_BASE='https://www.sec.gov/Archives'
START_PATH='edgar/full-index/master.gz'
