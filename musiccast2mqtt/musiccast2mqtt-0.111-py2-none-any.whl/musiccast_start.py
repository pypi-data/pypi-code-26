'''Launcher for the MusicCast gateway.'''

import os.path
import traceback

_APP_NAME = 'musiccast2mqtt'

import mqttgateway.utils.app_properties as app
app.Properties.init(app_path=os.path.realpath(__file__), app_name=_APP_NAME)
_logger = app.Properties.get_logger(__name__)

# import the module that initiates and starts the gateway
import mqttgateway.gateway.start_gateway as start_g

# import the module representing the interface
import musiccast2mqtt.musiccast_interface as mci

def main():
    # launch the gateway
    try:
        start_g.startgateway(mci.musiccastInterface)
    except:
        _logger.error(''.join(('Fatal error: ', traceback.format_exc())))
        raise

if __name__ == '__main__':
    main()