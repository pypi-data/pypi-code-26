from eurydike.eventdetectors.abstracteventdetector import AbstractEventDetector
from enum import Enum


class Comparator(Enum):
    """
    The Comparators are used for OnThreshold checks. Each enum is represented by a lambda function.
    """

    GREATERTHAN = (lambda x, y: x > y),
    LOWERTHAN = (lambda x, y: x < y),
    EQUALTO = (lambda x, y: x == y),

    @classmethod
    def get_enum(cls, text, logger):
        """
        Takes a string and returns the corresponding enum.

        :param text: string from config yaml structure.
        :param logger: logger instance
        :return: enum
        :raises: ValueError: raised if the text cannot be matched to one of the enum.
        """
        if text.lower()=="greaterthan" or text.lower()=="gt" or text.lower()==">":
            return cls.GREATERTHAN
        elif text.lower()=="lowerthan" or text.lower()=="lt" or text.lower()=="<":
            return cls.LOWERTHAN
        elif text.lower()=="equalto" or text.lower()=="==":
            return cls.EQUALTO
        else:
            logger.error("Comperator.get_enum - unkown value '{}'.".format(text))
            raise ValueError("Comperator.get_enum - unkown value '{}'.".format(text))

    def __call__(self, *args, **kwargs):
        """
        Execute the lambda function
        :return: result of the lambda function
        """
        return self.value[0](*args, **kwargs)


class OnThreshold(AbstractEventDetector):
    """
    Checks for simple threshold violations. Can be <, >, or ==.

        name: above  # unqiue name for event detector
        type: onthreshold  # detector type identifier
        comparator: gt  # GREATERTHAN/GT/>, LOWERTHAN/LT/<, EQUALTO/==
        threshold: 7  # threshold in combintation with comparator and value from topic-sub
        topic-sub: /test/value
        topic-pub: /test/above
        responses:  # leave value empty or remove line for no response
          on-violation: event_detected  # on detection of a threshold violation send this value to topic-pub
          on-restoration: event_ended  # on the event of returning to valid values send this value to topic-pub
        active: False  # entry ignored if set to False
    """
    _threshold = None  # threshold value
    _comparator = None  # enum representing the comparator type (<, >, or ==)

    def __init__(self, config, mqtt_client, parent_logger):
        """
        Constructor

        :param config: config yaml structure
        :param mqtt_client: mqtt client instance
        :param parent_logger: parent logger - a child logger will be spawned
        """
        AbstractEventDetector.__init__(self, config, mqtt_client, parent_logger)
        self._comparator = Comparator.get_enum(self._config["comparator"], self._logger)
        self._threshold = self._config["threshold"]

    def _is_violation(self, value):
        return self._comparator(value, self._threshold)


