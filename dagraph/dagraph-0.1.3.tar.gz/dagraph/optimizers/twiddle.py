from ..interfaces.optimizer import Optimizer

from math import isclose

class Twiddle(Optimizer):
    def __init__(self):
        pass
    
    def run(self, x0: list, cost_func, constraints: dict):
        x = x0
        dx = [1]*len(x)
        best_err = cost_func(x)
        self.constraints = constraints 

        threshold = 0.0000001

        while sum(dx) > threshold:
            print("theshold", sum(dx))
            for i in range(len(x)):
                start = x[i]
                x[i] += dx[i]
                err = cost_func(x)

                if (err < best_err) and (self._constraints(x) == False):  # There was some improvement
                    best_err = err
                    dx[i] *= 1.1   
                else:  # There was no improvement
                    x[i] -= 2*dx[i]  # Go into the other direction
                    err = cost_func(x)

                    if (err < best_err) and (self._constraints(x) == False):  # There was an improvement
                        best_err = err
                        dx[i] *= 1.05
                    else:  # There was no improvement
                        x[i] = start
                        # As there was no improvement, the step size in either
                        # direction, the step size might simply be too big.
                        dx[i] *= 0.95
        

        return x


    def _constraints(self, x):
        for con_type, func_list in self.constraints.items():
            if con_type == 'inequality':
                for func in func_list:
                    if func(x) < 0:
                        return True
        
        return False
