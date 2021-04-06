#!/usr/bin/env python
import numpy as np
from abc import ABC, abstractmethod


class VolatilityProcess(ABC):

    def __init__(self, settings):
        self.settings = settings
        self.parameters = dict(volatility_constant=1.0)

    def initilize_starting_values(self, data):
        self.parameters['volatility_constant'] = np.std(data)

    @abstractmethod
    def variance(self, residuals, estimates):
        pass
