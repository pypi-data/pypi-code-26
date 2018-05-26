'''
Defines the function that starts the gateway and the 3 MQTT callbacks.
'''

import logging
import sys
import time

import mqtt_gateways.utils.app_properties as app
from mqtt_gateways.utils.load_config import loadconfig
from mqtt_gateways.utils.init_logger import initlogger

import mqtt_gateways.gateway.mqtt_map as mqtt_map

from mqtt_gateways.gateway.configuration import CONFIG

from mqtt_gateways.gateway.test_messages import _MESSAGES

#_THROTTLELAG = 600  #int: lag in seconds to throttle the error logs.
_IN = 0; _OUT = 1 # indices for the message lists

def startgateway(gateway_interface):
    '''
    Initialisation and main loop.
    '''

    # Load the configuration. Check the first command line argument for the filename.
    if len(sys.argv) >= 2: pathgiven = sys.argv[1].strip()
    else: pathgiven = '' # default location in case no file name or path is given
    conffilepath = app.Properties.get_path('.conf', pathgiven)
    cfg = loadconfig(CONFIG, conffilepath)

    # Initialise the root logger.TODO: testing new appHelper class
    logfilepath = app.Properties.get_path('.log', cfg.get('LOG', 'logfilename'))
    emailhost = (cfg.get('LOG', 'host'), cfg.get('LOG', 'port'))
    initlogger(app.Properties.root_logger, app.Properties.name, logfilepath, cfg.getboolean('LOG', 'debug'),
               emailhost, cfg.get('LOG', 'address'))
    logger = app.Properties.get_logger(__name__)
    print 'Logger object in start_gateway_test is ', logger
    
    # For TESTING purposes, add a console handler
    # create the console handler. It should always work.
    formatter = logging.Formatter('%(name)-40s %(funcName)-15s %(levelname)-8s: %(message)s')
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG) # set the level to INFO temporarily to log what happens in this module
    stream_handler.setFormatter(formatter)
    app.Properties.root_logger.addHandler(stream_handler)
    # =============================================================

    # Log the configuration used.
    logger.info('=== APPLICATION STARTED ===')
    logger.info('Configuration:')
    for section in cfg.sections():
        for option in cfg.options(section):
            logger.info(''.join(('   [', section, '].', option, ' : <',
                                 str(cfg.get(section, option)), '>.')))
    # Warn in case of error processing the configuration file.
    if cfg.has_section('CONFIG') and cfg.has_option('CONFIG', 'error'):
        raise OSError(''.join(('Error <', cfg.get('CONFIG', 'error'), '> while processing the configuration file.')))
    # Instantiate the gateway interface.
    interfaceparams = {} # the parameters for the interface from the configuration file
    for option in cfg.options('INTERFACE'): # read the configuration parameters in a dictionary
        interfaceparams[option] = str(cfg.get('INTERFACE', option))
    #msglists = [[], []] # pair of message lists
    gatewayinterface = gateway_interface(interfaceparams)

    # Main loop
    while True:
        try: par = _MESSAGES.pop(0) # par as in parameters...
        except IndexError: break # no more messages
        imsg = mqtt_map.internalMsg(par[0], par[1], par[2], par[3], par[4], par[5], par[6], par[7])
        mqtt_map.msglist_in.append(imsg)
        # Call the interface loop.
        gatewayinterface.loop()

        # Publish the messages returned, if any.
        while True:
            try: internal_msg = mqtt_map.msglist_out.pop(0) # send messages on a FIFO basis
            except IndexError: break
            logger.debug(internal_msg.str())

        time.sleep(1)