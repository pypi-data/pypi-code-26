from pelops.abstractmicroservice import AbstractMicroservice
from epidaurus.pid import PID
import epidaurus.schema as schema
from epidaurus import version


class Controller(AbstractMicroservice):
    """
    Thermostat controller - wraps a PID-controller and produces the expected behavior. The heating system
    expects a minimum voltage by the controller (otherwise it goes into fail safe mode and starts heating
    immediately). Next to the minimum voltage there is a second threshold - above this the heater operates
    proportionally up to 100% with the maximum voltage.

    mqtt:
        mqtt-address: localhost
        mqtt-port: 1883
        mqtt-credentials: ~/credentials.yaml
        log-level: INFO

    logger:
        log-level: DEBUG
        log-file: epidaurus.log

    controller:
        value-idle: 4.5  # idle mode output - heating system does nothing
        value-min: 5  # minimum output for active (=heating) system
        value-max: 23  # maximum value for heater
        pid-max-output: 500  # for normalization purposes. this is the expected maximum output of the pid controller
        idle-mode-threshold: 0.75  # if temperature is this value above set-point, set output to volt-idle value.
        topics-sub:
            set-point: /test/thermostat/set-point  # receive new set point via this topic
            input:     /test/thermostat/input  # receive input (=temperature) updates via this topic
        topics-pub:
            output: /test/thermostat/output  # publish resulting output voltage to this topic
        pid:
            p-gain: 75
            i-gain: 20
            d-gain: 0
            update-interval: 30  # in seconds (in fact not used anywhere)
            windup-guard: 20  # protect integral term from windup
    """

    _version = version

    _topic_sub_set_point = None  # receive new set point via this topic
    _topic_sub_input = None  # receive input (=temperature) updates via this topic
    _topic_pub_output = None  # publish resulting output voltage to this topic

    _input = None  # last received input value
    _set_point = None  # last received set point
    _output = None  # last calculated output
    _output_raw = None  # unrefined output from pid controller
    _output_raw_max = -999999999  # maximum result from pid during runtime - for debugging purposes
    _output_raw_min = 999999999  # minimum result from pid during runtime - for debugging purposes

    _value_idle = None  # idle mode output - heating system does nothing
    _value_min = None  # minimum output for active (=heating) system
    _value_max = None  # maximum value for heater
    _idle_mode_threshold = None  # if temperature is this value above set-point, set output to volt-idle value.
    _pid_max_output = None  # for normalization purposes. this is the expected maximum output of the pid controller

    _pid = None  # instance from PID

    def __init__(self, config, mqtt_client=None, logger=None):
        """
        Constructor.

        :param config: config yaml structure
        :param mqtt_client: instance of an mqtt client (optional)
        :param logger: instance of a logger (optional)
        """
        AbstractMicroservice.__init__(self, config, "controller", mqtt_client, logger)

        self._pid = PID(self._config["pid"], self._logger)

        self._topic_pub_output = self._config["topics-pub"]["output"]
        self._topic_sub_input = self._config["topics-sub"]["input"]
        self._topic_sub_set_point = self._config["topics-sub"]["set-point"]
        self._mqtt_client.subscribe(self._topic_sub_set_point, self._sub_set_point_handler)
        self._mqtt_client.subscribe(self._topic_sub_input, self._sub_input_handler)

        self._idle_mode_threshold = float(self._config["idle-mode-threshold"])
        self._value_idle = float(self._config["value-idle"])
        self._value_min = float(self._config["value-min"])
        self._value_max = float(self._config["value-max"])
        self._pid_max_output = float(self._config["pid-max-output"])

        self._logger.info("{}.__init__ - done".format(self.__class__.__name__))

    def _sub_input_handler(self, value):
        """
        Message handler - to be registered to _topic_sub_input in mqtt_client. Stores the received input value
        in self._input

        :param value: Message content from incoming mqtt message.
        """
        self._logger.info("Controller._sub_input_handler - value:'{}'.".format(value))
        self._input = float(value)
        self._update()

    def _sub_set_point_handler(self, value):
        """
        Message handler - to be registered to _topic_sub_set_point in mqtt_client. Stores the received set point
        value in self._set_point

        :param value: Message content from incoming mqtt message.
        """
        self._logger.info("Controller._sub_set_point_handler - value:'{}'.".format(value))
        self._set_point = float(value)
        self._pid.reset(self._input, self._set_point)

    def _update(self):
        """
        Wrapper functionality for PID-controller - collect raw result from PID and convert it to the necessary
        voltage levels. the final result is published.
        """
        self._output_raw = self._pid.update(self._input)
        self._output_raw_max = max(self._output_raw, self._output_raw_max)
        self._output_raw_min = min(self._output_raw, self._output_raw_min)
        self._logger.info("Controller._update - pid output: {}, min: {}, max: {}.".
                          format(self._output_raw, self._output_raw_min, self._output_raw_max))
        if (self._input - self._idle_mode_threshold) > self._set_point:
            # measured value is much higher than target value -> overwriting pid output (but keep pid active)
            self._logger.info("Controller._update - hot enough. output:'{}' -> '{}'.".
                              format(self._output, self._value_idle))
            self._output = self._value_idle
        else:
            debug = []
            #  normalize pid output
            #  1. normalize pid output to (0,1)
            o = min(self._output_raw, self._pid_max_output)  # floor value
            debug.append(o)
            o = max(o, 0)  # ceil value
            debug.append(o)
            o = o / self._pid_max_output  # normalize to 1
            debug.append(o)
            #  1.5 desperate
            o = max(0.0, o - 0.5)  # remove lower
            debug.append(o)
            o = o / 0.5  # normalize to 1 (again)
            debug.append(o)
            #  2. inflate to valid output range
            valid_range = self._value_max - self._value_min
            debug.append(valid_range)
            o = o * valid_range
            debug.append(o)
            #  3. shift to operation range min-max
            o = o + self._value_min
            debug.append(o)
            self._output = o
            self._logger.info("Controller._update - pid postprocessing: {}.".format(debug))
        self._mqtt_client.publish(self._topic_pub_output, self._output)

    @classmethod
    def _get_schema(cls):
        """
        Get the sub schema to validate the yaml-config file against.

        :return: json-schema dict
        """
        return schema.get_schema()

    def _start(self):
        pass

    def _stop(self):
        pass

    @classmethod
    def _get_description(cls):
        return "PID controller for thermostat."


def standalone():
    Controller.standalone()


if __name__ == "__main__":
    Controller.standalone()

