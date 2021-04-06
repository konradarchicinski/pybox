#!/usr/bin/env python
from pybox.maths.optimizations.optimizer import Optimizer

from scipy.optimize import differential_evolution


class DifferentialEvolution(Optimizer):

    def __init__(self):
        self.method = "DifferentialEvolution"
        self.settings = dict(popsize=100, polish=True, strategy="best1bin")

    def minimize(self, objective_function, bounds, settings=None):
        if settings is not None:
            self.settings.update(settings)
        self.iteration = 1
        self.objective_function = objective_function
        self.summary = differential_evolution(self.objective_function,
                                              bounds,
                                              callback=self._callback,
                                              **self.settings)

    def _callback(self, xs, convergence):
        self.print_info(self.iteration, xs, self.objective_function(xs))
        self.iteration += 1
