from pelops import mylogger


class AbstractEventDetector:
    """
    An event occurs when a value is outside the defined thresholds. Then the event detector changes its state
    to active and publishes the defined response. As soon as the value is back within the thresholds the state
    switches back to inactive and the defined response is published.
    """

    _config = None  # config yaml strucutre
    _logger = None  # logger instance
    _name = None  # name of event detector
    _mqtt_client = None  # mqtt client instance
    _event_active = None  # state of event detection - true if event has occured and still continues
    _topic_sub = None  # input for event detection
    _topic_pub = None  # publish results to this topic
    _responses = None  # stores the response messages that are published to _topic_pub

    def __init__(self, config, mqtt_client, parent_logger):
        """
        Constructor

        :param config: config yaml structure
        :param mqtt_client: mqtt client instance
        :param parent_logger: parent logger - a child logger will be spawned
        """
        self._config = config
        self._logger = mylogger.get_child(parent_logger, self.__class__.__name__, config)
        self._logger.info("{}.__init__ - initializing".format(self.__class__.__name__))
        self._logger.debug("{}.__init__ - configuration: {}".format(self.__class__.__name__, self._config))

        self._name = self._config["name"]

        self._mqtt_client = mqtt_client
        self._topic_pub = self._config["topic-pub"]
        self._topic_sub = self._config["topic-sub"]
        self._responses = {}
        for k, v in self._config["responses"].items():
            if v is None or v == "":
                continue
            self._responses[k] = v

        self._event_active = False

    def _message_handler(self, value):
        """
        The message handler is registered to process a message published to _topic_sub. Incoming values are
        checked if they are within the boundaries (_is_violation) and the corresponding response is published.

        :param value: incoming message from topic _topic_sub
        """
        try:
            value = int(value)
        except ValueError:
            value = float(value)

        if self._is_violation(value):
            # threshold is violated
            if not self._event_active:
                self._logger.info("{}._message_handler ({}) - threshold violation detected (value: {}).".
                                  format(self.__class__.__name__, self._name, value))
                try:
                    self._mqtt_client.publish(self._topic_pub, self._responses["on-violation"])
                except KeyError:
                    pass
            self._event_active = True
        else:
            if self._event_active:
                self._logger.info("{}._message_handler ({}) - threshold restored (value: {}).".
                                  format(self.__class__.__name__, self._name, value, ))
                try:
                    self._mqtt_client.publish(self._topic_pub, self._responses["on-restoration"])
                except KeyError:
                    pass
            self._event_active = False

    def _is_violation(self, value):
        """
        Checks if the value is within the boundaries/thresholds. Must be implemented by child classes.

        :param value: incoming value
        :return: True if the value violates the boundaries/thresholds. False if not.
        """
        raise NotImplementedError

    def start(self):
        """
        start event detection by subscribing to _topic_sub
        """
        self._mqtt_client.subscribe(self._topic_sub, self._message_handler)

    def stop(self):
        """
        stop event detection by unsubscribing from _topic_sub
        """
        self._mqtt_client.unsubscribe(self._topic_sub, self._message_handler)
