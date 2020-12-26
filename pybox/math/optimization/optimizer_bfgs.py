#!/usr/bin/env python
from pybox.math.optimization.optimizer import Optimizer
from scipy import optimize


class BFGS(Optimizer):

    def __init__(self):
        self.method = "BFGS"

    def minimize(self, objective_function, starting_values):
        self.objective_function = objective_function
        self.iteration = 1
        self.summary = optimize.minimize(
            self.objective_function, starting_values,
            method=self.method, jac=self.gradient(objective_function),
            callback=self._callback)

    def _callback(self, xs):
        self.print_info(self.iteration, xs, self.objective_function(xs))
        self.iteration += 1
