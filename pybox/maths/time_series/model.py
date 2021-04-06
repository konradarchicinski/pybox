#!/usr/bin/env python
from pybox.helpers.text import camel_to_snake_case
from pybox.maths.optimizations import Optimizer
from pybox.maths.distributions import Distribution

import os
import inspect
import numpy as np
from importlib import import_module


class TimeSeriesModel:

    def __init__(self,
                 mean_process="ConstantMean",
                 volatility_process="ConstantVolatility",
                 disturbance_term="Normal",
                 mean_process_settings=dict(),
                 volatility_process_settings=dict(),
                 disturbance_term_settings=dict()):
        self.estimates = dict()

        self.mean_process = self._create_process(mean_process,
                                                 mean_process_settings)

        self.volatility_process = self._create_process(
            volatility_process, volatility_process_settings)

        disturbance_term_settings.update(name=disturbance_term)
        self.disturbance_term = Distribution.create(disturbance_term_settings)

    def log_likelihood(self, data):
        residuals = self.mean_process.residuals(data, self.estimates)
        variance = self.volatility_process.variance(residuals, self.estimates)

        standard_deviation = np.sqrt(variance)
        mean = np.mean(residuals)

        standardized_residuals = (residuals - mean) / standard_deviation
        distribution_parameters = {
            dp: self.estimates[dp] for dp in self.disturbance_term.parameters
        }

        likelihood = self.disturbance_terms.pdf(
            standardized_residuals, **
            distribution_parameters) / standard_deviation

        # removing the zeros so as not to put them into logarithms
        likelihood = likelihood[likelihood != 0.0]
        return np.sum(np.log(likelihood))

    def fit(self, data, model_selection='LL', settings=None):
        self._initilize_starting_values(data)

        if settings is None:
            settings = dict(algorithm='BasinHopping')
        if model_selection == 'LL':
            objective_function = self._log_likelihood
        else:
            objective_function = self._akaike_information_criterion

        initial_values = list(self.estimates.values())
        optimizer = Optimizer.create(settings['algorithm'])
        optimizer.minimize(objective_function,
                           initial_values,
                           objective_function_parameters=(data))

        self._update_estimates(optimizer.minimum_coordinates)
        self.fit_summary = optimizer.summary

    def simulate(self):
        pass

    def _log_likelihood(self, parameters, data):
        self._update_estimates(parameters)
        return -self.log_likelihood(data)

    def _akaike_information_criterion(self, parameters, data):
        self._update_estimates(parameters)
        return 2 * (len(self.estimates) - self.log_likelihood(data))

    def _update_estimates(self, parameters):
        for i, estimate in enumerate(self.estimates):
            self.estimates[estimate] = parameters[i]

    def _initilize_starting_values(self, data):
        self.mean_process.initilize_starting_values(data)
        self.volatility_process.initilize_starting_values(data)
        self.disturbance_term.initilize_starting_values(data)

        self.estimates.update(self.mean_process.parameters)
        self.estimates.update(self.volatility_process.parameters)
        self.estimates.update(self.disturbance_term.parameters)

    def _create_process(self, process_name, process_settings):
        for module in os.listdir(os.path.dirname(__file__)):
            if module in [
                    f"{process_name.lower()}.py",
                    f"{camel_to_snake_case(process_name)}.py"
            ]:
                imported_module = import_module(f".{module[:-3]}", __package__)
                models = inspect.getmembers(imported_module, inspect.isclass)
                for model_name, model in models:
                    if model_name == process_name:
                        time_series_process = model(process_settings)
                        return time_series_process
                raise ValueError(
                    (f"Module `{module}` has been inspected but no proper"
                     " implementation of time series process was found there."))
        raise ValueError(("No suitable `TimeSeriesModel` implementation"
                          f" was found for `{process_name}`."))
