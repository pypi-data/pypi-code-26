from ..interfaces.optimizer import Optimizer

from scipy.optimize import minimize

class SLSQP(Optimizer):
    def __init__(self):
        pass
    
    def run(self, x0: list, cost_func, constraints: dict):

        cons = self._convert_constraints(constraints)
        results = minimize(cost_func, x0, method="SLSQP", constraints=cons, options={'ftol':
                                                                                         10e-9,
                                                                                     'maxiter':
                                                                                         10e3,
                                                                                     'eps':
                                                                                         10-16,
                                                                                     'disp': True})
        print(results)
        return results

    def _convert_constraints(self, constraints: dict):
        cons = []
        for con_type, func_list in constraints.items():
            con_type = 'eq' if con_type is 'equality' else 'ineq'
            for func in func_list:
                cons.append({'type': con_type, 'fun': func})
        return tuple(cons)