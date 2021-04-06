#!/usr/bin/env python
from pybox.maths.time_series.volatility_process import VolatilityProcess


class ConstantVolatility(VolatilityProcess):

    def variance(self, residuals, estimates):
        return estimates['volatility_constant']**2
