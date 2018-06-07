# inspired by https://gist.github.com/chaosmail/8372717


class PID:
    """
    PID controller implementation

    pid:
        p-gain: 75
        i-gain: 20
        d-gain: 0
        update-interval: 30  # in seconds (in fact not used anywhere)
        windup-guard: 20  # protect integral term from windup
    """
    _config = None  # config structure
    _logger = None  # logger instance

    _p_gain = None  # controller gain constant
    _i_gain = None  # controller integration constant
    _d_gain = None  # controller derivation constant

    _update_interval = -1  # update time in seconds
    _windup_guard = None  # window guard - i is limited to +/- this value.

    _set_point = None  # target output
    _i_prev = 0  # i value from the last iteration
    _err_prev = 0  # difference between desired and observed value in last iteration

    def __init__(self, config, logger):
        """
        Constructor.

        :param config: config yaml structure
        :param mqtt_client: instance of an mqtt client (optional)
        :param logger: instance of a logger (optional)
        """
        self._config = config
        self._logger = logger
        self._logger.info("PID.__ini__ - initializing instance ('{}').".format(self._config))

        self._p_gain = self._config["p-gain"]
        self._d_gain = self._config["d-gain"]
        self._i_gain = self._config["i-gain"]
        self._update_interval = self._config["update-interval"]
        self._windup_guard = self._config["windup-guard"]

    def reset(self, input_value, set_point):
        """
        Reset PID-controller during runtime.
        :param input_value: new input value
        :param set_point: new set point
        """
        self._set_point = set_point
        #self._err_prev = 0
        #self._i_prev = 0

    def update(self, input_value):
        """
        PID-controller algorithm update.

        :param input_value: measured value
        :return: controller output
        """

        # Error between the desired and actual output
        err = self._set_point - input_value

        # proportional input
        p_term = self._p_gain * err

        # Integration Input
        i_term = self._i_prev + err * self._update_interval
        if i_term > self._windup_guard:
            i_term = self._windup_guard
        elif i_term < -self._windup_guard:
            i_term = -self._windup_guard
        self._i_prev = i_term
        i_term = i_term * self._i_gain

        # Derivation Input
        d_term = self._d_gain * (err - self._err_prev) / self._update_interval

        self._err_prev = err

        # Calculate output
        output_value = p_term + i_term + d_term

        return output_value
