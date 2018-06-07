from eurydike.eventdetectors.abstracteventdetector import AbstractEventDetector


class OnBand(AbstractEventDetector):
    """
    Each incoming value is checked against an upper and a lower threshold. The threshold is violated if
    the following statement is fulfilled: lower_threshold <= value <= upper_threshold.

        name: outside  # unqiue name for event detector
        type: onband  # detector type identifier
        upper-threshold: 8  # upper threshold for on band detection
        lower-threshold: 7  # lower threshold for on band detection
        topic-sub: /test/value
        topic-pub: /test/band
        responses:  # leave value empty or remove line for no response
          on-violation: event_detected  # on detection of a threshold violation send this value to topic-pub
          on-restoration: event_ended  # on the event of returning to valid values send this value to topic-pub
        active: True  # entry ignored if set to False
    """

    _upper_threshold = None  # upper threshold value
    _lower_threshold = None  # lower threshold value

    def __init__(self, config, mqtt_client, parent_logger):
        """
        Constructor

        :param config: config yaml structure
        :param mqtt_client: mqtt client instance
        :param parent_logger: parent logger - a child logger will be spawned
        """
        AbstractEventDetector.__init__(self, config, mqtt_client, parent_logger)
        self._upper_threshold = self._config["upper-threshold"]
        self._lower_threshold = self._config["lower-threshold"]
        if self._lower_threshold >= self._upper_threshold:
            self._logger.error("OnBand.__init__ ({}) - lower limit ({}) must be smaller than upper limit({}).".
                               format(self._name, self._lower_threshold, self._upper_threshold))
            raise ValueError("OnBand.__init__ ({}) - lower limit ({}) must be smaller than upper limit({}).".
                               format(self._name, self._lower_threshold, self._upper_threshold))

    def _is_violation(self, value):
        return not (self._lower_threshold <= value <= self._upper_threshold)
