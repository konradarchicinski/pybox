#!/usr/bin/env python
from pybox.math.optimization.optimizer import Optimizer
from scipy.optimize import basinhopping


class BasinHopping(Optimizer):

    def __init__(self):
        self.method = "BasinHopping"

    def minimize(self, objective_function, starting_values, local_optimizer="BFGS"):
        if local_optimizer == "BFGS":
            local_optimizer_settings = dict(method=local_optimizer)
        elif local_optimizer == "LBFGSB":
            local_optimizer_settings = dict(method="L-BFGS-B",
                                            jac=self.gradient(objective_function))
        else:
            raise ValueError((
                f"Provided `{local_optimizer}` has not been implemented"
                " as a local optimizer in `Optimizer` class."))

        self.iteration = 1
        self.objective_function = objective_function
        self.summary = basinhopping(
            self.objective_function, starting_values,
            minimizer_kwargs=local_optimizer_settings,
            callback=self._callback)

    def _callback(self, xs, value, accepted):
        self.print_info(self.iteration, xs, value)
        self.iteration += 1
