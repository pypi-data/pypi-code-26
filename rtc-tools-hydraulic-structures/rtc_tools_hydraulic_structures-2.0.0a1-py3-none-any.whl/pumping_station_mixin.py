import logging
import os
import pickle
import re
import sys
from abc import abstractmethod
from collections import OrderedDict
from itertools import starmap

from casadi import Function, MX, SX, det, hessian, jacobian, nlpsol, substitute, trace, vertcat

import numpy as np
from numpy import inf

from rtctools.optimization.goal_programming_mixin import Goal
from rtctools.optimization.optimization_problem import OptimizationProblem
from rtctools.optimization.timeseries import Timeseries

from .polygon_enclosure import enclosing_segments
from .util import _ObjectParameterWrapper

logger = logging.getLogger("rtctools")


class Pump(_ObjectParameterWrapper):
    """
    Python Pump object as an interface to the
    :cpp:class:`~Deltares::HydraulicStructures::PumpingStation::Pump` object
    in the model.
    """

    def __init__(self, optimization_problem, symbol):
        super().__init__(optimization_problem)

        self.optimization_problem = optimization_problem
        self.symbol = symbol

    def discharge(self):
        """
        Get the state corresponding to the pump discharge.

        :returns: `MX` expression of the pump discharge.
        """

        # TODO: We would rather use self.symbol + ".Q" as the control
        # variable, but only top level input variables are allowed. We
        # therefore use the convention that a symbol exists where all dots are
        # replaced with underscores.
        return self.optimization_problem.state(self.symbol.replace('.', '_') + '_Q')

    def head(self):
        """
        Get the state corresponding to the pump head. This depends on the
        ``head_option`` that was specified by the user.

        :returns: `MX` expression of the pump head.
        """
        return self.optimization_problem.state(self.symbol + '.dH')


class Resistance(_ObjectParameterWrapper):
    """
    Python Resistance object as an interface to the
    :cpp:class:`~Deltares::HydraulicStructures::PumpingStation::Resistance`
    object in the model.
    """

    def __init__(self, optimization_problem, symbol):
        super().__init__(optimization_problem)

        self.optimization_problem = optimization_problem
        self.symbol = symbol

    def discharge(self):
        """
        Get the state corresponding to the discharge through the resistance.

        :returns: `MX` expression of the discharge.
        """
        return self.optimization_problem.state(self.symbol + '.HQUp.Q')

    def head_loss(self):
        """
        Get the state corresponding to the head loss over the resistance.

        :returns: `MX` expression of the head loss.
        """

        # Can't we use the dot notation instead, as the two are equated in the
        # Modelica model anyway?
        return self.optimization_problem.state(self.symbol.replace('.', '_') + '_dH')


class PumpingStation(_ObjectParameterWrapper):
    """
    Python PumpingStation object as an interface to the
    :cpp:class:`~Deltares::HydraulicStructures::PumpingStation::PumpingStation` object in the model.
    """

    def __init__(self, optimization_problem, symbol, pump_symbols=None, **kwargs):
        """
        Initialize the pumping station object.

        :param optimization_problem:
               :py:class:`~rtctools.optimization.optimization_problem.OptimizationProblem` instance.
        :param symbol: Symbol name of the pumping station in the model.
        :param pump_symbols: Symbol names of the pumps in the pumping station.
        """
        super().__init__(optimization_problem)

        self.optimization_problem = optimization_problem
        self.symbol = symbol

        # NOTE: We use pump symbols to guarantee the order in which we process
        # the pumps. This is important for e.g. the pump switching matrix,
        # where we need to know what row represents what pump.
        self.pump_symbols = pump_symbols

        self._pumps = None
        self._resistances = None

    def pumps(self):
        """
        Get a list of :py:class:`Pump` objects that are part of this pumping station
        in the model.

        :returns: List of :py:class:`Pump` objects.
        """
        if self._pumps is None:
            if self.pump_symbols is None:
                # TODO: Until we are able to guarantee an order in Modelica, we can only come here
                # if the pump switching matrix is all zeros.
                matrix = self.pump_switching_matrix
                if not np.all(matrix == 0):
                    raise Exception("Automatic finding of pumps not allowed with non-zero switching matrix.")

                _pump_symbols = set()
                for x in self.optimization_problem.parameters(0).keys():
                    m = re.search(r'({}\..+?)\.working_area\['.format(self.symbol), x)
                    if m is None:
                        continue
                    else:
                        _pump_symbols.add(m.group(1))

                self.pump_symbols = sorted(_pump_symbols)

            self._pumps = [Pump(self.optimization_problem, x) for x in self.pump_symbols]

        return self._pumps

    def resistances(self):
        """
        Get a list of :py:class:`Resistance` objects that are part of this pumping station
        in the model.

        :returns: List of :py:class:`Resistance` objects.
        """

        if self._resistances is None:
            _resist_symbols = set()
            for x in self.optimization_problem.parameters(0).keys():
                # TODO: Isn't there a better way to find these components
                # instead of looking for some type of signature (which can
                # change).
                m = re.search(r'({}\..+?)\.C'.format(self.symbol), x)
                if m is None:
                    continue
                else:
                    _resist_symbols.add(m.group(1))

            _resist_symbols = sorted(_resist_symbols)

            self._resistances = [Resistance(self.optimization_problem, x) for x in _resist_symbols]

        return self._resistances

    @property
    def pump_switching_matrix(self):
        # TODO: Move default values to Modelica, and delete this property
        # method (i.e. let it be handled automatically by __getattr__)
        # TODO: For some reason using super() does not work. Why?
        matrix = _ObjectParameterWrapper.__getattr__(self, 'pump_switching_matrix')

        # FIXME: Detect placeholder array for JModelica workaround
        if np.all(matrix == -999):
            matrix = np.tril(np.ones(matrix.shape), -1)
            for i in range(matrix.shape[0]):
                matrix[i, i] = -1 * sum(matrix[i, :])

        # Only lower triangle matrices are allowed
        if not (np.tril(matrix) == matrix).all():
            raise Exception("Switching matrices may only contain a non-zeros in the lower triangle.")

        return matrix

    @property
    def pump_switching_constraints(self):
        # TODO: Move default values to Modelica, and delete this property
        # method (i.e. let it be handled automatically by __getattr__)
        constraints = _ObjectParameterWrapper.__getattr__(self, 'pump_switching_constraints')

        # FIXME: Detect placeholder array for JModelica workaround
        if np.all(constraints == -999):
            constraints = np.transpose([np.zeros(self.n_pumps), list(range(self.n_pumps))])

        return constraints

    @property
    def n_pumps(self):
        return int(_ObjectParameterWrapper.__getattr__(self, 'n_pumps'))


class _MinimizePowerGoal(Goal):

    def __init__(self, optimization_problem, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ts = optimization_problem.get_timeseries('energy_price')
        energy_price = np.array([v for t, v in zip(ts.times, ts.values) if t in optimization_problem.times()])

        avg_energy_price = sum(energy_price) / len(energy_price)

        # For maximum power of each pump we use the (overestimated) big M
        avg_pump_powers = [float(max_power/2) for _, max_power in optimization_problem._pump_power_range_on.values()]
        total_avg_pump_power = sum(avg_pump_powers)

        nominal_instantaneous = total_avg_pump_power * avg_energy_price

        self.function_nominal = nominal_instantaneous * (
            optimization_problem.times()[-1] - optimization_problem.times()[0])

    def function(self, o, ensemble_member):
        costs = 0.0

        times = o.times()

        for ps in o.pumping_stations():
            for p in ps.pumps():
                for ts, tf in zip(times[:-1], times[1:]):
                    tstep = tf - ts

                    # TODO: Not pretty to use the same formatting again
                    # Pump power
                    costs += tstep * o.state_at('{}__power'.format(p.symbol), tf) * o.timeseries_at('energy_price', tf)

                    # Start-up energy
                    if p.start_up_energy > 0.0:
                        costs += tstep * o.state_at('{}__switched_on'.format(p.symbol), tf) \
                            * p.start_up_energy \
                            * o.timeseries_at('energy_price', tf)

                    # Fixed start-up costs (other than energy)
                    if p.start_up_cost > 0.0:
                        costs += tstep * o.state_at('{}__switched_on'.format(p.symbol), tf) \
                            * p.start_up_cost

                    # Shut-down energy
                    if p.shut_down_energy > 0.0:
                        costs += tstep * o.state_at('{}__switched_off'.format(p.symbol), tf) \
                            * p.shut_down_energy \
                            * o.timeseries_at('energy_price', tf)

                    # Fixed shut-down costs (other than energy)
                    if p.shut_down_cost > 0.0:
                        costs += tstep * o.state_at('{}__switched_off'.format(p.symbol), tf) \
                            * p.shut_down_cost

        return costs

    function_range = (0, 1)

    priority = 999

    order = 1


class _InvalidCacheError(Exception):
    pass


class PumpingStationMixin(OptimizationProblem):
    """
    Adds handling of PumpingStation objects in your model to your optimization
    problem.

    Relevant parameters and variables are read from the model, and from this
    data a set of constraints and objectives are automatically generated to
    minimize cost.
    """

    # TODO: Vijzels are different in that the pump head is just the upstream
    # head, and the discharge/working area is a non-smooth function that does
    # not fit a polynomial well. How to handle these?
    _pumping_station_mx_path_variables = []

    # In the post() routine we check if the non-linear equality constraints
    # (e.g. pump power and resistance head loss) minimized to their equality
    # constraint. A warning is raised if the relative error exceeds this value:
    _ineq_relative_error = 0.001

    # In the post() routine we check if the non-linear equality constraints
    # (e.g. pump power and resistance head loss) minimized to their equality
    # constraint. A warning is raised if the relative error exceeds this value:
    _ineq_absolute_error = 1e-8

    # Use pickle to cache the HQ subproblems that are solved. Using cached
    # data results in a different answer, see #54.
    pumpingstation_cache_hq_subproblem = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # We also want to output a bunch of variables that are calculated in
        # post(), which we return in the extract_results() call. We store them
        # in this dictionary.
        self.__additional_results = OrderedDict()

        assert 'model_folder' in kwargs
        self.__model_folder = kwargs['model_folder']

        self._hq_subproblem_cache = OrderedDict()
        self._hq_subproblem_cache_path = os.path.join(kwargs['model_folder'], '_hq_subproblem_cache.pickle')

    def pre(self):
        super().pre()

        # We cannot handle non-equidistant timesteps yet
        tsteps = np.diff(self.times())
        if not np.all(tsteps == tsteps[0]):
            raise Exception("Timesteps need to be equidistant.")

        # TODO: Is a reset necessary? It is a bit double with the statements above.
        self._pumping_station_mx_path_variables = []
        self._pump_discrete_symbols = []
        self._pump_status_bounds = OrderedDict()
        self._pump_power_bounds = OrderedDict()
        self._pump_discharge_bounds = OrderedDict()
        self._pump_status_pairs = OrderedDict()
        self._pump_power_range_on = OrderedDict()

        self._pump_working_area_head_range = OrderedDict()
        self._pump_extended_working_area_head_range = OrderedDict()

        self._head_range_up = OrderedDict()
        self._head_range_down = OrderedDict()
        self._head_range_diff = OrderedDict()

        # Uses the same mapping as Pump.head_option for easy access
        self._head_range = {-1: self._head_range_up,
                            0: self._head_range_diff,
                            1: self._head_range_down}

        # Check validity of HQ subproblem cache. We check if _any_ file other
        # than ourself in the model folder is newer.
        try:
            if not self.pumpingstation_cache_hq_subproblem:
                raise _InvalidCacheError("Caching disabled")

            # Calling getmtime() on a file that does not exist returns a vague
            # platform varying Exception. Try to prevent that from happening.
            if not os.path.exists(self._hq_subproblem_cache_path):
                raise _InvalidCacheError("Cache file does not exist")

            cache_mtime = os.path.getmtime(self._hq_subproblem_cache_path)
            cache_abspath = os.path.abspath(self._hq_subproblem_cache_path)
            for root, _dir, files in os.walk(self.__model_folder):
                for f in files:
                    f_abspath = os.path.abspath(os.path.join(root, f))
                    if cache_abspath != f_abspath and os.path.getmtime(f_abspath) > cache_mtime:
                        raise _InvalidCacheError("Cache no longer valid")

            with open(self._hq_subproblem_cache_path, 'rb') as f:
                self._hq_subproblem_cache = pickle.load(f)

        except _InvalidCacheError:
            self._hq_subproblem_cache = OrderedDict()

        # Automatic deriviation of maximum head over pumping station. Note
        # that it is possible that different pumps use different head
        # definitions (up, down, diff) for the maximum head of the enclosing
        # pumping station.
        for ps in self.pumping_stations():
            symbol_up = ps.symbol + ".HQUp.H"
            symbol_down = ps.symbol + ".HQDown.H"

            # Use bounds if specified, otherwise try deriving bounds from time series
            for hr, s in [(self._head_range_up, symbol_up),
                          (self._head_range_down, symbol_down)]:

                m, M = self.bounds().get(s, [None, None])

                try:
                    ts = self.get_timeseries(s)
                    canonical_state, sign = self.alias_relation.canonical_signed(s)

                    # Discard history values for head estimation.
                    ts_values = np.array([v for t, v in zip(ts.times, ts.values) if t in self.times()])

                    # Attempt to avoid using time series used as initial conditions only by checking for NaN
                    if m is None or not np.isfinite(m) and not any(np.isnan(ts_values)):
                        m = min(ts_values)
                        logger.info('Using {} value "{}" in time series "{}" as lower bound for "{}".'.format(
                            "minimum" if sign == 1 else "maximum", m, canonical_state, s))
                    if M is None or not np.isfinite(M) and not any(np.isnan(ts_values)):
                        M = max(ts_values)
                        logger.info('Using {} value "{}" in time series "{}" as upper bound for "{}".'.format(
                            "maximum" if sign == 1 else "minimum", M, canonical_state, s))
                except KeyError:
                    # Time series does not exist
                    pass

                if m is None or M is None or not np.isfinite(m) or not np.isfinite(M):
                    raise Exception(
                        "Specify (finite) bounds or time series for '{}', currently found {}".format(s, (m, M)))

                hr[ps.symbol] = (m, M)

            self._head_range_diff[ps.symbol] = [a - b for a, b in zip(self._head_range_down[ps.symbol],
                                                                      reversed(self._head_range_up[ps.symbol]))]

        # Automatic derivation of discharge and power if not specified by user
        for ps in self.pumping_stations():
            for p in ps.pumps():
                discharge_sym = p.symbol.replace('.', '_') + "_Q"
                head_sym = p.symbol + "_head"
                power_sym = '{}__power'.format(p.symbol)

                # Find the maximum discharge and head in the working area
                Q = MX.sym('Q')
                H = MX.sym('H')

                hr = self._head_range[p.head_option][ps.symbol]

                _, (_, q_max) = self._solve_working_area_subproblem(
                    p.working_area, p.working_area_direction, hr, H, Q, -1 * Q)
                self._pump_discharge_bounds[discharge_sym] = (0.0, q_max)

                _, (h_max, _) = self._solve_working_area_subproblem(
                    p.working_area, p.working_area_direction, hr, H, Q, -1 * H)
                self._pump_working_area_head_range[head_sym] = (0.0, h_max)
                # TODO: determine h_min, or do we count on it being 0.0?

                _, (h_max, _) = self._solve_working_area_subproblem(
                    p.working_area, p.working_area_direction, hr, H, Q, -1 * H, 0)
                _, (h_min, _) = self._solve_working_area_subproblem(
                    p.working_area, p.working_area_direction, hr, H, Q, H, 0)
                self._pump_extended_working_area_head_range[head_sym] = (h_min, h_max)

                # Recalculate the maximum discharge, but now for the
                # _extended_ working area, so that we can use it for the
                # maximum power calculation below.
                _, (_, q_max) = self._solve_working_area_subproblem(
                    p.working_area, p.working_area_direction, hr, H, Q, -1 * Q, 0)

                # Lower power bound (when on)
                power = 0.0

                coeffs = p.power_coefficients

                for i in range(coeffs.shape[0]):
                    for j in range(coeffs.shape[1]):
                        power += coeffs[i, j] * H**i * Q**j

                min_power, _ = self._solve_working_area_subproblem(
                    p.working_area, p.working_area_direction, hr, H, Q, power)

                # For a monotonically increasing convex function we can find
                # the maximum by checking all vertices of the polygon. We do
                # this not on the working area (which is not a polygon), but
                # on an enclosing square. Note that we do this on the H and Q
                # ranges of the _extended_ working area.
                max_power = 0.0

                for h, q in [(h_min, 0), (h_max, 0), (h_min, q_max), (h_max, q_max)]:
                    power = 0.0

                    for i in range(coeffs.shape[0]):
                        for j in range(coeffs.shape[1]):
                            power += coeffs[i, j] * h**i * q**j

                    max_power = max(power, max_power)

                self._pump_power_bounds[power_sym] = (0.0, max_power)
                self._pump_power_range_on[power_sym] = (min_power, max_power)

        # Convexity and increasing-with-H check of power coefficients
        Q = SX.sym('Q')
        H = SX.sym('H')
        X = vertcat(Q, H)

        for ps in self.pumping_stations():
            for p in ps.pumps():
                discharge_sym = p.symbol.replace('.', '_') + "_Q"
                head_sym = p.symbol + "_head"

                power = 0.0

                coeffs = p.power_coefficients
                for i in range(coeffs.shape[0]):
                    for j in range(coeffs.shape[1]):
                        power += coeffs[i, j] * H**i * Q**j

                # Check if power is increasing with H (only necessary if there are resistances)
                if ps.resistances():
                    sx_jac = jacobian(power, H)

                    sx_hess = hessian(sx_jac, X)[0]
                    sx_determinant = det(sx_hess)
                    sx_trace = trace(sx_hess)

                    # CasADi returns NaN if the expression is still a function of H and/or Q
                    determinant = float(sx_determinant)
                    trace_calculated = float(sx_trace)

                    if np.isnan(determinant):
                        logger.warning('Cannot determine monotonicity in H of power of pump "{}".'.format(p.symbol))
                    elif determinant < 0.0 or trace_calculated < 0.0:
                        # Concave function of which we are trying to find the minimum --> use enclosing rectangle
                        h_min, h_max = self._pump_working_area_head_range[head_sym]
                        q_min, q_max = self._pump_discharge_bounds[discharge_sym]

                        min_jac = np.inf

                        for h, q in [(h_min, q_min), (h_max, q_min), (h_min, q_max), (h_max, q_max)]:
                            cur_jac = float(substitute(substitute(sx_jac, H, h), Q, q))
                            min_jac = min(cur_jac, min_jac)

                        if min_jac < 0.0:
                            logger.warning(
                                'Power of pump "{}" likely not increasing with H in working area.'.format(p.symbol))
                    else:
                        hr = self._head_range[p.head_option][ps.symbol]
                        # We require convexity on the working area (i.e. when pump is on)
                        minimum_jac, _ = self._solve_working_area_subproblem(
                            p.working_area, p.working_area_direction, hr, H, Q, sx_jac)

                        if minimum_jac < 0.0:
                            logger.error(
                                'Power of pump "{}" is not increasing with H in working area.'.format(p.symbol))

                # Convexity check:
                sx_hess = hessian(power, X)[0]
                sx_determinant = det(sx_hess)
                sx_trace = trace(sx_hess)

                # CasADi returns NaN if the expression is still a function of H and/or Q
                determinant = float(sx_determinant)
                trace_calculated = float(sx_trace)

                if (not np.isnan(determinant) and determinant < 0.0) or (
                        not np.isnan(trace_calculated) and trace_calculated < 0.0):
                    logger.error('Non-convex power relationship specified for pump "{}".'.format(p.symbol))
                elif np.isnan(determinant):
                    # The determinant is an expression of H and Q. Check if it
                    # is a convex expression, and if so, find the minimum.
                    sx_det_hess = hessian(sx_determinant, X)[0]
                    sx_det_determinant = det(sx_det_hess)

                    det_determinant = float(sx_det_determinant)

                    if not np.isnan(det_determinant):
                        hr = self._head_range[p.head_option][ps.symbol]
                        # We require convexity on the expanded working area, i.e when pump is off
                        minimum_determinant, _ = self._solve_working_area_subproblem(
                            p.working_area, p.working_area_direction, hr, H, Q, sx_determinant, 0)
                        minimum_trace, _ = self._solve_working_area_subproblem(
                            p.working_area, p.working_area_direction, hr, H, Q, sx_trace, 0)

                        if minimum_determinant < 0.0 or minimum_trace < 0.0:
                            logger.error(
                                'Power for pump "{}" is not convex over extended working area'.format(p.symbol))

                        # For correct maximum power estimation, we also require
                        # convexity on the rectangular region:
                        # Q \in [0, max_q]
                        # H \in [0, max_h]
                        # where  max_q and max_h are the maximum discharge
                        # and pump head when the pump is _on_.
                        bnds = {Q.name(): self._pump_discharge_bounds[discharge_sym],
                                H.name(): self._pump_working_area_head_range[head_sym]}
                        minimum_determinant, _ = self._solve_hq_subproblem(H, Q, sx_determinant, bounds=bnds)
                        minimum_trace, _ = self._solve_hq_subproblem(H, Q, sx_trace, bounds=bnds)

                        if minimum_determinant < 0.0 or minimum_trace < 0.0:
                            logger.error(
                                'Power for pump "{}" is not convex over max. head/discharge range.'.format(p.symbol))
                    else:
                        logger.warning('Cannot detect convexity of power coefficients of pump "{}".'.format(p.symbol))
                else:
                    # Positive determinant --> convex
                    continue

        for ps in self.pumping_stations():
            # Add discharge symbols for each of the pumps in this pumping station
            # TODO: Add on/off + switched on/off symbols for each pump as well.
            #       Make sure that this is accompanied by also adding constraints on
            #       pump 2 only being able to switch on (or be on?) when pump 1 is on.
            for p in ps.pumps():
                # Define symbol names
                status_sym = '{}__status'.format(p.symbol)
                sw_on_sym = '{}__switched_on'.format(p.symbol)
                sw_off_sym = '{}__switched_off'.format(p.symbol)
                power_sym = '{}__power'.format(p.symbol)

                # Store variable names
                self._pump_discrete_symbols.append(status_sym)
                self._pump_discrete_symbols.append(sw_on_sym)
                self._pump_discrete_symbols.append(sw_off_sym)

                # Store bounds
                self._pump_status_bounds[status_sym] = (0, 1)
                self._pump_status_bounds[sw_off_sym] = (0, 1)
                self._pump_status_bounds[sw_off_sym] = (0, 1)

                # Generate and store MX variables
                status_mx = MX.sym(status_sym)
                sw_on_mx = MX.sym(sw_on_sym)
                sw_off_mx = MX.sym(sw_off_sym)
                power_mx = MX.sym(power_sym)

                self._pumping_station_mx_path_variables.append(status_mx)
                self._pumping_station_mx_path_variables.append(sw_on_mx)
                self._pumping_station_mx_path_variables.append(sw_off_mx)
                self._pumping_station_mx_path_variables.append(power_mx)

                # Store all symbols together
                self._pump_status_pairs[p.symbol] = (status_sym, sw_on_sym, sw_off_sym, power_sym)

        # Store cache to disk
        if self.pumpingstation_cache_hq_subproblem:
            with open(self._hq_subproblem_cache_path, 'wb') as f:
                pickle.dump(self._hq_subproblem_cache, f)

    @abstractmethod
    def pumping_stations(self):
        """
        User problem returns list of :class:`PumpingStation` objects.

        :returns: A list of pumping stations.
        """
        raise NotImplementedError()

    def constraints(self, ensemble_member):
        constraints = super().constraints(ensemble_member)

        for ps in self.pumping_stations():
            for p in ps.pumps():
                status_sym, sw_on_sym, sw_off_sym, _ = self._pump_status_pairs[p.symbol]

                for t_m1, t in zip(self.times()[:-1], self.times()[1:]):
                    d_t = self.state_at(status_sym, t)
                    d_tm1 = self.state_at(status_sym, t_m1)
                    d_diff = d_t - d_tm1
                    x = self.state_at(sw_on_sym, t)
                    y = self.state_at(sw_off_sym, t)

                    # x is 1 if and only if pump switched on (else 0)
                    constraints.append((d_t - x, 0, inf))
                    constraints.append((x - d_diff, 0, inf))
                    constraints.append((1 - d_tm1 - x, 0, inf))

                    # y is 1 if and only if pump switched off (else 0)
                    constraints.append((d_tm1 - y, 0, inf))
                    constraints.append((y + d_diff, 0, inf))
                    constraints.append((1 - d_t - y, 0, inf))

                # TODO: Minimum on and minimum off constraints currently
                # assume equidistant time steps, and the unit of
                # "minimum_on/off" is then the number of time steps. Allow for
                # non-equidistant time steps, and units of an hour.
                tstep = self.times()[1] - self.times()[0]
                num_tsteps = len(self.times())

                try:
                    hist_status = self.get_timeseries(p.symbol + '_status_hist').values[:1 - num_tsteps]
                    rev_hist_status = list(reversed(hist_status))

                    if not all((hist_status == 0) | (hist_status == 1)):
                        raise Exception("Invalid values in history of pump {}".format(p.symbol))

                    if len(rev_hist_status) < max(int(p.minimum_on / tstep), int(p.minimum_off / tstep)):
                        raise Exception(
                            "Length of history of pump {} is smaller than minimum_on/minimum_off".format(p.symbol))

                    # Force the initial state to match the history
                    constraints.append((self.state_at(status_sym, self.times()[0]),
                                        rev_hist_status[0], rev_hist_status[0]))

                    hist_on = next((i for i, s in enumerate(rev_hist_status) if s == 0), len(rev_hist_status))
                    hist_off = next((i for i, s in enumerate(rev_hist_status) if s == 1), len(rev_hist_status))
                except KeyError:
                    hist_on = 0
                    hist_off = 0

                if p.minimum_on > 0.0:
                    min_on = int(p.minimum_on / tstep)
                    if hist_on != 0 and min_on > hist_on:
                        sum_on = 0.0

                        num_tsteps_add = min(min_on - hist_on, num_tsteps)
                        for j in range(num_tsteps_add):
                            sum_on += self.state_at(status_sym, self.times()[j+1])

                        constraints.append((sum_on, num_tsteps_add, inf))
                    for i in range(1, num_tsteps):
                        sum_on = 0.0

                        num_tsteps_incl = min(num_tsteps - i, min_on)
                        for j in range(num_tsteps_incl):
                            sum_on += self.state_at(status_sym, self.times()[i+j])

                        constraints.append((sum_on - num_tsteps_incl * self.state_at(sw_on_sym, self.times()[i]),
                                            0, inf))

                if p.minimum_off > 0.0:
                    min_off = int(p.minimum_off / tstep)
                    if hist_off != 0 and min_off > hist_off:
                        sum_off = 0.0

                        num_tsteps_add = min(min_off - hist_off, num_tsteps)
                        for j in range(num_tsteps_add):
                            sum_off += self.state_at(status_sym, self.times()[j+1])

                        constraints.append((sum_off, -inf, 0))
                    for i in range(1, num_tsteps):
                        sum_off = 0.0

                        num_tsteps_incl = min(num_tsteps - i, min_off)
                        for j in range(num_tsteps_incl):
                            sum_off += (1 - self.state_at(status_sym, self.times()[i+j]))

                        constraints.append((sum_off - num_tsteps_incl * self.state_at(sw_off_sym, self.times()[i]),
                                            0, inf))

        return constraints

    def _solve_hq_subproblem(self, H, Q, f, constraints=None, bounds=None):
        # Caching of the results of this function. SWIG object cannot be
        # pickled directly, so isntead we just convert everything to a string.
        pickle_key = (str(H), str(Q), str(f), str(constraints), str(bounds))

        if self.pumpingstation_cache_hq_subproblem:
            try:
                return self._hq_subproblem_cache[pickle_key]
            except KeyError:
                pass

        # Discharge of pump is always positive
        if bounds is None:
            bounds = {Q.name(): (0.0, np.inf),
                      H.name(): (-np.inf, np.inf)}

        if constraints is None:
            g, lbg, ubg = list(starmap(vertcat, ([], [], [])))
        else:
            g, lbg, ubg = list(starmap(vertcat, list(zip(*constraints))))

        # State vector
        X = [H, Q]

        # Bounds
        lbx = vertcat(*(bounds[x.name()][0] for x in X))
        ubx = vertcat(*(bounds[x.name()][1] for x in X))

        X = vertcat(*X)

        nlp = {'f': f, 'g': g, 'x': X}

        options = {'print_time': False, 'ipopt': {'print_level': 0}}

        solver = nlpsol('nlp', 'ipopt', nlp, options)

        results = solver(x0=vertcat(0, 0), lbx=lbx, ubx=ubx, lbg=lbg, ubg=ubg)

        objective_value = float(results['f'])
        solver_output = np.array(results['x'])[:, 0]

        self._hq_subproblem_cache[pickle_key] = objective_value, solver_output

        return objective_value, solver_output

    def _solve_working_area_subproblem(self, working_area, working_area_direction, head_range, H, Q, f, pump_status=1):
        constraints = self._working_area_constraints(
            working_area, working_area_direction, head_range, H, Q, pump_status)

        return self._solve_hq_subproblem(H, Q, f, constraints)

    def _working_area_constraints(self, working_area, working_area_direction, head_range, head, discharge, status):
        constraints = []

        for poly, direction in zip(working_area, working_area_direction):
            # When the pump is off, we increasing the working area to
            # include all possible points on the H-axis. We calculate
            # the minimum needed offset to accomplish this.
            offset_min_h = 0.0
            offset_max_h = 0.0

            constr_f = 0.0

            for i in range(poly.shape[0]):
                offset_min_h += head_range[0]**i * poly[i, 0]
                offset_max_h += head_range[1]**i * poly[i, 0]

                for j in range(poly.shape[1]):
                    constr_f += poly[i, j] * head**i * discharge**j

            # TODO: Maybe compensate with more than exactly what is
            # needed, e.g. with 130% of the calculated offset. For
            # example, when we have a straight vertical line saying Q
            # > 0.2 m3/s, we might not want to shift the line to
            # exactly Q = 0 m3/s when the pump is off. To make it
            # easier for the mixed integer optimizer to find a good
            # solution, we probably want Q = 0 m3/s to already be an
            # acceptable solution for something like status = 0.2.

            # Apply the working area changes, but only if it increases
            # the working area size. We do not want to shrink it, even
            # if we hypothetically could, as we would rather keep the
            # constraints constant in that case.
            if np.sign(direction) != np.sign(offset_min_h) and \
               np.sign(direction) != np.sign(offset_max_h):
                # We are violating both the lowest H-value as well as
                # the highest H-value when the pump is off. We have to
                # compensate only for the largest difference.
                max_offset = np.sign(offset_min_h) * np.max(np.abs([offset_min_h, offset_max_h]))
                constr_f -= (1 - status) * max_offset
            elif np.sign(direction) != np.sign(offset_min_h):
                constr_f -= (1 - status) * offset_min_h
            elif np.sign(direction) != np.sign(offset_max_h):
                constr_f -= (1 - status) * offset_max_h

            if direction == -1:
                constraints.append((constr_f, -inf, 0.0))
            elif direction == 1:
                constraints.append((constr_f, 0.0, inf))
            else:
                raise Exception(
                    "Working area polynomial needs a direction of 1 or -1, but got {}".format(direction))

        return constraints

    def path_constraints(self, ensemble_member):
        constraints = super().path_constraints(ensemble_member)

        for ps in self.pumping_stations():
            for p in ps.pumps():
                status_sym, _, _, power_sym = self._pump_status_pairs[p.symbol]
                discharge_sym = p.symbol.replace('.', '_') + "_Q"

                status = self.state(status_sym)

                hr = self._head_range[p.head_option][ps.symbol]

                constraints.extend(self._working_area_constraints(
                    p.working_area, p.working_area_direction, hr, p.head(), p.discharge(), status))

                # Power calculation which we need for optimization/minimization and constraints.
                power = 0.0

                coeffs = p.power_coefficients
                for i in range(coeffs.shape[0]):
                    for j in range(coeffs.shape[1]):
                        # TODO: Is it better if we simplify here directly (e.g. x^0 = 1, x^1 = x)
                        power += coeffs[i, j] * p.head()**i * p.discharge()**j

                m, M = self._pump_power_range_on[power_sym]

                # NOTE: Inequality constraint for power, as an equality constraint would have to be affine
                constraints.append((self.state(power_sym) - m * status, 0.0, inf))
                constraints.append((self.state(power_sym) - M * status, -inf, 0.0))
                constraints.append((self.state(power_sym) - (power - M * (1 - status)), 0.0, inf))

                # Pump needs to always have a positive discharge
                constraints.append((p.discharge(), 0.0, inf))

                # Pump needs to have zero discharge when off
                _, q_max = self._pump_discharge_bounds[discharge_sym]

                constraints.append((p.discharge() - (status * q_max), -inf, 0.0))

            # To handle pump switching constraints easily, we make a vector of
            # the status symbols of all pumps.
            switch_matrix = ps.pump_switching_matrix
            switch_constraints = ps.pump_switching_constraints

            pump_status_vector = []
            for p in ps.pumps():
                pump_status_vector.append(self.state(self._pump_status_pairs[p.symbol][0]))

            for i in range(switch_matrix.shape[0]):
                if any(switch_matrix[i, :] != 0.0):
                    # A pump can only be on when it is allowed to be according to the pump switching matrix
                    # TODO: We can be multiplying by zero here. Is that worse than not multiplying at all?
                    constraints.append((sum(np.multiply(switch_matrix[i, :], pump_status_vector)),
                                        switch_constraints[i, 0],
                                        switch_constraints[i, 1]))

            for r in ps.resistances():
                C = r.C
                if C > 0.0:
                    constraints.append((r.head_loss() - C * r.discharge()**2, 0.0, inf))

                    # To force the head loss to go to zero, we need an upper bound as well.
                    _, max_head_loss = self._head_range[0][ps.symbol]
                    q_max_dh = (max_head_loss / C)**0.5
                    constraints.append((max_head_loss / q_max_dh * r.discharge() - r.head_loss(), 0.0, inf))
                elif C == 0.0:
                    # Force the head loss to zero in case of zero resistance
                    constraints.append((r.head_loss(), 0.0, 0.0))
                else:
                    # Resistance cannot have a negative value
                    raise Exception(
                        'Resistance has a negative value of "{}"'.format(r.C))

        return constraints

    @property
    def path_variables(self):
        variables = super().path_variables
        variables.extend(self._pumping_station_mx_path_variables)
        return variables

    def goals(self):
        goals = super().goals()
        goals.append(_MinimizePowerGoal(self))
        return goals

    def bounds(self):
        bounds = super().bounds()
        bounds.update(self._pump_status_bounds)
        bounds.update(self._pump_power_bounds)
        bounds.update(self._pump_discharge_bounds)
        return bounds

    def variable_is_discrete(self, variable):
        if variable in self._pump_discrete_symbols:
            return True
        else:
            return super().variable_is_discrete(variable)

    def post(self):

        results = self.extract_results()
        times = self.times()

        # TODO: If we put the calculated pump head and discharge in the
        # extract_results() dictionary, should we maybe move the calculation
        # of these time series to priority_completed() in case that exists (or
        # invalidate cached results with every optimize() call)? It might be
        # useful for debugging of intermediate results.

        # Extract the pump head and pump discharge from the results.
        path_expressions = []

        for ps in self.pumping_stations():
            for p in ps.pumps():
                path_expressions.append(p.head())
                path_expressions.append(p.discharge())

        expression = self.map_path_expression(vertcat(*path_expressions), 0)
        f = Function('f', [self.solver_input], [expression])
        evaluated_path_expressions = f(self.solver_output)
        evaluated_path_expressions = np.array(evaluated_path_expressions)

        # Append pump head and discharge to the results dictionary and
        # time series export.
        idx = 0
        for ps in self.pumping_stations():
            for p in ps.pumps():
                head_ts = Timeseries(times, evaluated_path_expressions[:, idx])
                head_key = "{}_{}".format(p.symbol, "head")

                self.set_timeseries(head_key, head_ts, output=True)
                self.__additional_results[head_key] = head_ts.values
                idx += 1

                discharge_ts = Timeseries(times, evaluated_path_expressions[:, idx])
                discharge_key = "{}_{}".format(p.symbol, "discharge")

                self.set_timeseries(discharge_key, discharge_ts, output=True)
                self.__additional_results[discharge_key] = discharge_ts.values
                idx += 1

        # Check if the inequality constraints of pump power and resistance
        # head loss have been succesfully minimized to equality.
        results = self.extract_results()

        for ps in self.pumping_stations():
            for p in ps.pumps():
                head_realised = results[p.symbol + "_head"][1:]
                discharge_realised = results[p.symbol + "_discharge"][1:]
                power_realised = results[p.symbol + "__power"][1:]
                status_realised = results[p.symbol + "__status"][1:]

                power_target = power_realised * 0.0

                coeffs = p.power_coefficients

                for i in range(coeffs.shape[0]):
                    for j in range(coeffs.shape[1]):
                        power_target += coeffs[i, j] * head_realised**i * discharge_realised**j * status_realised

                power_error = abs(sum(abs(power_target - power_realised))
                                  / max(sum(power_target), sys.float_info.min))

                if power_error > self._ineq_relative_error:
                    logger.error('Relative power error of {} in pump "{}"'.format(power_error, p.symbol))

            for r in ps.resistances():
                C = r.C
                head_loss_realised = results[r.symbol + ".dH"][1:]
                discharge_realised = results[r.symbol + ".HQUp.Q"][1:]

                head_loss_target = C * discharge_realised**2

                head_loss_abserror = sum(abs(head_loss_target - head_loss_realised))

                head_loss_error_chk = (self._ineq_absolute_error +
                                       self._ineq_relative_error * sum(abs(head_loss_target)))

                if head_loss_abserror > head_loss_error_chk:
                    logger.error('Absolute head loss error of {} exceeds tolerance in resistance "{}"'.format(
                        head_loss_abserror, r.symbol))

            # Append pump speed to results and output timeseries
            for ps in self.pumping_stations():
                for p in ps.pumps():
                    coeffs = p.speed_coefficients

                    # Only calculate and output pump speed if non-zero
                    # coefficients are specified
                    if np.all(coeffs == 0):
                        continue

                    head_realised = results[p.symbol + "_head"]
                    discharge_realised = results[p.symbol + "_discharge"]
                    status_realised = results[p.symbol + "__status"]

                    speed = discharge_realised * 0.0

                    for i in range(coeffs.shape[0]):
                        for j in range(coeffs.shape[1]):
                            speed += coeffs[i, j] * head_realised**i * discharge_realised**j * status_realised

                    speed_ts = Timeseries(times, speed)
                    speed_key = "{}_{}".format(p.symbol, "speed")

                    self.set_timeseries(speed_key, speed_ts, output=True)
                    self.__additional_results[speed_key] = speed_ts.values

            # Append pump power and status to output timeseries
            for ps in self.pumping_stations():
                for p in ps.pumps():
                    power_realised = results[p.symbol + "__power"]
                    status_realised = results[p.symbol + "__status"]

                    power_ts = Timeseries(times, power_realised)
                    power_key = "{}_{}".format(p.symbol, "power")
                    self.set_timeseries(power_key, power_ts, output=True)

                    status_ts = Timeseries(times, status_realised)
                    status_key = "{}_{}".format(p.symbol, "status")
                    self.set_timeseries(status_key, status_ts, output=True)

        # NOTE: If we call super() first, adding output time series with
        # set_time series has no effect, as e.g. PIMIxin/CSVMixin have already
        # written their export file. That is why we do it at the end instead.
        super().post()

    def extract_results(self, *args, **kwargs):
        results = super().extract_results(*args, **kwargs)
        results.update(self.__additional_results)
        return results


def plot_operating_points(optimization_problem, output_folder, plot_expanded_working_area=True):
    """
    Plot the working area of each pump with its operating points.
    """
    import matplotlib.pyplot as plt
    import matplotlib.lines as mlines

    for ps in optimization_problem.pumping_stations():
        for p in ps.pumps():
            plt.clf()

            # For the head range, we take the extremes of the head over the
            # pump encountered during optimization, and the maximum head
            # inside the working area.
            hrange = optimization_problem._head_range[p.head_option][ps.symbol]
            hrange = [float(x) for x in hrange]  # Convert DMatrix to float

            head_sym = p.symbol + "_head"
            if plot_expanded_working_area:
                hrange_wa = optimization_problem._pump_extended_working_area_head_range[head_sym]
            else:
                hrange_wa = optimization_problem._pump_working_area_head_range[head_sym]
            hrange_wa = [float(x) for x in hrange_wa]  # Convert DMatrix to float

            hrange = [min(hrange[0], hrange_wa[0]), max(hrange[1], hrange_wa[1])]

            discharge_sym = p.symbol.replace('.', '_') + "_Q"
            qrange = optimization_problem._pump_discharge_bounds[discharge_sym]
            qrange = [float(x) for x in qrange]  # Convert DMatrix to float

            # For the lines, use a little bit wider range for both H and Q
            extra_space = 0.25 * (qrange[1] - qrange[0])
            qs_range = (qrange[0] - extra_space, qrange[1] + extra_space)

            extra_space = 0.25 * (hrange[1] - hrange[0])
            hs_range = (hrange[0] - extra_space, hrange[1] + extra_space)

            qs = np.linspace(*qs_range)
            hs = np.linspace(*hs_range)[:, None]

            # For the x and y limits we use slightly less extra space. This is
            # to make sure that the contour lines go all the way to the edge
            # of our plots.
            extra_space = 0.1 * (qrange[1] - qrange[0])
            qplot_range = (qrange[0] - extra_space, qrange[1] + extra_space)

            extra_space = 0.1 * (hrange[1] - hrange[0])
            hplot_range = (hrange[0] - extra_space, hrange[1] + extra_space)

            plt.xlim(*qplot_range)
            plt.ylim(*hplot_range)

            # Plot lines for the horizontal and vertical axes
            plt.axhline(0, color='black', zorder=1)
            plt.axvline(0, color='black', zorder=1)

            wa = p.working_area
            wa_dir = p.working_area_direction

            wa_lines = []

            inner_points = qs * hs * 0.0

            # Plot the working area
            for w in range(len(wa)):
                constraints = optimization_problem._working_area_constraints(
                    wa[w:w+1], wa_dir[w:w+1], hrange, hs, qs, 1)

                C = plt.contour(qs, hs.ravel(), constraints[0][0], [0],
                                colors='b')

                inner_points += ((constraints[0][0] * wa_dir[w]) > 0).astype(int)
                wa_lines.append([tuple(x) for x in C.collections[0].get_paths()[0].vertices])

                if plot_expanded_working_area:
                    constraints = optimization_problem._working_area_constraints(
                        wa[w:w + 1], wa_dir[w:w+1], hrange, hs, qs, 0)

                    plt.contour(qs, hs.ravel(), constraints[0][0], [0],
                                colors='g', linestyles='dashed')

            plt.plot([0, 0], list(hrange), 'yo', ms=6, mec='k', label="Head range")

            results = optimization_problem.extract_results()

            plt.plot(results[discharge_sym][1:], results[head_sym][1:], 'r+',
                     markeredgewidth=2, label="Operating points")

            # Manually add legend entries for the working area(s), because
            # contour plots do not handle that automatically
            handles, _ = plt.gca().get_legend_handles_labels()
            handles.append(mlines.Line2D([], [], color='b', label='Working area'))
            if plot_expanded_working_area:
                handles.append(mlines.Line2D([], [], color='g', linestyle='--', label='Extended working area'))
            plt.legend(handles=handles)

            plt.xlabel(r'Discharge [$\mathdefault{m^3\!/s}$]')
            plt.ylabel(r'Head [$\mathdefault{m}$]')

            # Check if we found any point inside the working area, so that we
            # can color it. We typically will not have found such a point for
            # constant speed pumps (or close to constant speed pmps), in which
            # case we skip the filling.
            h_inds, q_inds = np.where(inner_points == len(wa))
            if h_inds.size > 0 and q_inds.size > 0:
                point = (qs[q_inds[0]], hs[h_inds[0]])
                wa_segments = enclosing_segments(point, wa_lines)
                x, y = list(zip(*(s[0] for s in wa_segments)))
                plt.fill(x, y, alpha=0.25, color='b')

            f = plt.gcf()
            f.set_size_inches(8, 6)
            f.tight_layout()

            plt.grid(True)

            fname = 'QHP_{}.png'.format(p.symbol.replace('.', '_'))
            fname = os.path.join(output_folder, fname)
            plt.savefig(fname, bbox_inches='tight', pad_inches=0.1)
