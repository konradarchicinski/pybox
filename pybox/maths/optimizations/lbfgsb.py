#!/usr/bin/env python
from pybox.maths.optimizations.optimizer import Optimizer

from scipy import optimize


class LBFGSB(Optimizer):

    def __init__(self):
        self.method = "L-BFGS-B"

    def minimize(self,
                 objective_function,
                 starting_values,
                 objective_function_parameters=None):
        self.objective_function = objective_function
        self.iteration = 1
        self.summary = optimize.minimize(self.objective_function,
                                         starting_values,
                                         args=objective_function_parameters,
                                         method=self.method,
                                         jac=self.gradient(objective_function),
                                         callback=self._callback)

    def _callback(self, xs):
        self.print_info(self.iteration, xs, self.objective_function(xs))
        self.iteration += 1
