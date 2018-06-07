class TrivialFlat:
    _verbose = None

    temperature = None

    temp_decrease = 0.01  # cool off per interval

    heater_set_point = None
    heater_reaction = None
    heater_temp_increase = 0.1  # heat up per interval on full power
    heater_max_value = 22  # if setpoint is larger idle -> heater effect is set alequot value of temp_increase
    heater_idle_threshold = 5  # if volt is <=idle and >full -> heater is turned off
    heater_safety_threshold = 4  # if volt<=full -> heater is set to max capacity

    def __init__(self, temperature, verbose, temp_decrease=0.01, heater_temp_inc=0.1, heater_max=22, heater_idle=5,
                 heater_safety=4):
        self._verbose = verbose
        self.temperature = temperature
        self.temp_decrease = temp_decrease
        self.heater_temp_increase = heater_temp_inc
        self.heater_max_value = heater_max
        self.heater_idle_threshold = heater_idle
        self.heater_safety_threshold = heater_safety
        if self._verbose:
            print("TrivialFlat - initialized model with temperature {}.".format(self.temperature))

    def _get_temp_increase(self, heater_set_point):
        if heater_set_point > self.heater_max_value:
            raise ValueError("volt {} > max_value {}".format(heater_set_point, self.heater_max_value))
        if heater_set_point <= self.heater_safety_threshold:
            if self._verbose:
                print("TrivialFlat._get_temp_increase - heater_set_point to low ({}).".format(heater_set_point))
            #  if input value is below safety thershold assume a controller error and turn heater on as fail-safe
            #  behavior
            result = self.heater_temp_increase
        elif heater_set_point <= self.heater_idle_threshold:
            if self._verbose:
                print("TrivialFlat._get_temp_increase - heater_set_point in idle range ({}).".format(heater_set_point))
            #  if input value is between safety and idle assume that the heater should be turned off
            result = 0
        else:
            #  in every other case use proportional setting for heater between idle and max value.
            t_set_point = heater_set_point - self.heater_idle_threshold
            t_max_value = self.heater_max_value - self.heater_idle_threshold
            proportional_heater = t_set_point / t_max_value
            result = proportional_heater * self.heater_temp_increase
            if self._verbose:
                print("TrivialFlat._get_temp_increase - heater_set_point in proportional ({}->{}).".
                      format(heater_set_point, proportional_heater))
        return result

    def update_temperature(self, heater_set_point):
        self.heater_set_point = heater_set_point
        self.heater_reaction = self._get_temp_increase(self.heater_set_point)
        inc = self.heater_reaction
        prev = self.temperature
        self.temperature = self.temperature - self.temp_decrease + inc
        if self._verbose:
            print("TrivialFlat.update - old temp: {}, new temp: {}, heater-set-point: {}, inc-value: {}, dec-value: {},".
                  format(prev, self.temperature, heater_set_point, inc, self.temp_decrease))
        return self.temperature
