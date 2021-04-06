#!/usr/bin/env python
import numpy as np
from abc import ABC, abstractmethod


class MeanProcess(ABC):

    def __init__(self, settings):
        self.settings = settings
        self.parameters = dict(mean_constant=0)

    def initilize_starting_values(self, data):
        self.parameters['mean_constant'] = np.mean(data)

    @abstractmethod
    def residuals(self, data, estimates):
        pass
