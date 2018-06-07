from pelops import mylogger
from eurydike.eventdetectors.onband import OnBand
from eurydike.eventdetectors.onthreshold import OnThreshold


class EventDetectorFactory:
    """
    Create event detector instances based on the given yaml config structure.
    """

    @staticmethod
    def create_element(config_element, mqtt_client, parent_logger):
        """
        Create the corresponding eventdetection class instance.

        Note: new implementations of abstracteventdetector must be added to this method manually.

        :param config_element: config yaml structure for one eventdetector
        :param mqtt_client: mqtt client instance
        :param parent_logger: logger instance - a child will be spawned
        :return: a single eventdetection class instance
        """
        logger = mylogger.get_child(parent_logger, __name__)
        element = None
        if config_element["active"]:
            if config_element["type"].lower() == "onband":
                element = OnBand(config_element, mqtt_client, parent_logger)
            elif config_element["type"].lower() == "onthreshold":
                element = OnThreshold(config_element, mqtt_client, parent_logger)
            else:
                logger.error("EventDetectorFactory.create_element - unknown type '{}'".
                              format(config_element["type"].lower()))
                raise ValueError("Factory.create_element - unknown type '{}'".
                                 format(config_element["type"].lower()))
        else:
            logger.info("EventDetectorFactory.create_element - skipping inactive element '{}.{}'.".
                        format(config_element["type"].lower(), config_element["name"]))

        return element

    @staticmethod
    def create_elements(config_elements, mqtt_client, parent_logger):
        """
        Take a list of eventdetection config structures and create the corresponding class instances.

        :param config_elements: config yaml structure
        :param mqtt_client: mqtt client instance
        :param parent_logger: logger instance - a child will be spawned
        :return: a list with the eventdetector instances
        """
        logger = mylogger.get_child(parent_logger, __name__)
        element_list = []

        logger.info("EventDetectorFactory.create_elements - start")

        for config_element in config_elements:
            element = EventDetectorFactory.create_element(config_element, mqtt_client, parent_logger)
            if element is not None:
                element_list.append(element)

        logger.info("EventDetectorFactory.create_elements - finished")

        return element_list


